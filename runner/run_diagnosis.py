#!/usr/bin/env python3
"""
runner/run_diagnosis.py
=======================
Orchestrates AI diagnosis + deterministic rule-checking for every case in
``data/cases.csv``.

For each case the script:
  1. Sends the case to the Groq API using the prompt defined in
     ``prompts/diagnose_prompt.md`` (loaded at runtime, never hardcoded).
  2. Parses the JSON response (gracefully skips malformed replies).
  3. Runs ``checker.rule_checker.run_all_checks()`` on the same case.
  4. Compares the AI's diagnosis against the ground-truth ``expected_fault``
     and ``osi_layer``, recording ``matches_expected`` + notes.
  5. Writes ``runner/diagnosis_results.csv`` and prints a summary.

Usage
-----
    python runner/run_diagnosis.py               # defaults to data/cases.csv
    python runner/run_diagnosis.py path/to.csv    # explicit path
"""

from __future__ import annotations

import csv
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Make project root importable regardless of invocation dir
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from checker.rule_checker import Finding, run_all_checks  # noqa: E402

# Load environment variables from .env if present
load_dotenv(_PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("run_diagnosis")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_PROMPT_PATH = _PROJECT_ROOT / "prompts" / "diagnose_prompt_v2.md"
_DATA_DEFAULT = _PROJECT_ROOT / "data" / "cases.csv"
_OUTPUT_DIR = Path(__file__).resolve().parent
_OUTPUT_CSV = _OUTPUT_DIR / "diagnosis_results.csv"
_MODEL = "claude-3-5-sonnet-20240620"
_PROMPT_VERSION = "v2"
_MAX_TOKENS = 2048
_RETRY_LIMIT = 5
_RETRY_DELAY = 10  # seconds


# ---------------------------------------------------------------------------
# Prompt loader
# ---------------------------------------------------------------------------

def _load_prompts(path: Path) -> Tuple[str, str]:
    """Parse ``diagnose_prompt.md`` and return (system_prompt, user_template).

    The system prompt is everything from ``## System Prompt`` up to (but not
    including) ``## User Prompt Template``.  The user template is the code
    block inside ``## User Prompt Template``.
    """
    text = path.read_text(encoding="utf-8")

    # ── System prompt: from "## System Prompt" to "## User Prompt Template"
    sys_match = re.search(
        r"## System Prompt\s*\n(.*?)(?=\n## User Prompt Template)",
        text,
        re.DOTALL,
    )
    if not sys_match:
        raise ValueError(
            f"Could not find '## System Prompt' … '## User Prompt Template' "
            f"sections in {path}"
        )
    system_prompt = sys_match.group(1).strip()

    # ── User template: the fenced code block after "## User Prompt Template"
    user_section = text[text.index("## User Prompt Template"):]
    tpl_match = re.search(r"```\n?(.*?)```", user_section, re.DOTALL)
    if not tpl_match:
        raise ValueError(
            f"Could not find a code-fenced user template in {path}"
        )
    user_template = tpl_match.group(1).strip()

    return system_prompt, user_template


# ---------------------------------------------------------------------------
# JSON parsing (resilient)
# ---------------------------------------------------------------------------

def _parse_ai_json(raw: str) -> Optional[Dict[str, Any]]:
    """Try to extract valid JSON from the AI response.

    Handles: bare JSON, markdown-fenced JSON, trailing text after the object.
    Returns None on failure.
    """
    # Strip markdown fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)

    # Attempt 1: direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Attempt 2: find the first { … } blob
    brace = cleaned.find("{")
    if brace == -1:
        return None
    depth = 0
    end = brace
    for i, ch in enumerate(cleaned[brace:], start=brace):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    try:
        return json.loads(cleaned[brace : end + 1])
    except json.JSONDecodeError:
        return None


def _validate_ai_diagnosis(payload: Optional[Dict[str, Any]]) -> tuple[Optional[Dict[str, Any]], str]:
    """Enforce the public response contract and retain failure provenance."""
    required = {"root_cause", "osi_layer", "confidence", "evidence", "next_command", "fix_steps", "verification_steps", "requires_human_review"}
    if payload is None or not required.issubset(payload):
        return None, "MALFORMED_RESPONSE"
    if payload["confidence"] not in {"low", "medium", "high"}:
        return None, "MALFORMED_RESPONSE"
    if not all(isinstance(payload[field], list) for field in ("evidence", "fix_steps", "verification_steps")):
        return None, "MALFORMED_RESPONSE"
    if payload["requires_human_review"] is not True:
        return None, "POLICY_VIOLATION"
    return payload, "SUCCESS"


# ---------------------------------------------------------------------------
# Keyword / semantic match
# ---------------------------------------------------------------------------

def _normalise(text: str) -> set[str]:
    """Lower-case, strip punctuation, return set of tokens."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _compare_diagnosis(
    ai_root_cause: str,
    ai_osi: str,
    expected_fault: str,
    expected_osi: str,
) -> Tuple[bool, str]:
    """Return (matches_expected, note).

    Matching strategy:
      • OSI layer must match (extracted layer number).
      • Root-cause keywords: ≥40 % of significant expected-fault tokens
        must appear in the AI root_cause (simple recall metric).
    """
    notes: list[str] = []

    # ── OSI comparison (by layer number) ──────────────────────────────────
    def _layer_num(s: str) -> Optional[str]:
        m = re.search(r"layer\s*(\d)", s, re.IGNORECASE)
        return m.group(1) if m else None

    ai_layer = _layer_num(ai_osi)
    exp_layer = _layer_num(expected_osi)
    osi_match = ai_layer is not None and ai_layer == exp_layer
    if not osi_match:
        notes.append(f"OSI mismatch: AI='{ai_osi}' vs expected='{expected_osi}'")

    # ── Keyword recall ────────────────────────────────────────────────────
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "not", "no", "on",
        "in", "to", "of", "for", "and", "or", "but", "has", "have", "that",
        "this", "it", "its", "be", "been", "being", "with", "from", "by",
        "at", "as", "so", "if", "do", "does", "did"
    }
    exp_tokens = _normalise(expected_fault) - stop
    ai_tokens = _normalise(ai_root_cause)

    if exp_tokens:
        overlap = exp_tokens & ai_tokens
        recall = len(overlap) / len(exp_tokens)
    else:
        recall = 0.0

    keyword_match = recall >= 0.40
    if not keyword_match:
        notes.append(
            f"Low keyword recall ({recall:.0%}): "
            f"missing {sorted(exp_tokens - ai_tokens)[:8]}"
        )
    else:
        notes.append(f"Keyword recall {recall:.0%}")

    matches = osi_match and keyword_match
    return matches, "; ".join(notes)


# ---------------------------------------------------------------------------
# Anthropic API call
# ---------------------------------------------------------------------------

def _call_anthropic(
    client: Any,
    system_prompt: str,
    user_message: str,
) -> Optional[str]:
    """Send one request to the Anthropic API with retry."""
    for attempt in range(1, _RETRY_LIMIT + 1):
        try:
            resp = client.messages.create(
                model=_MODEL,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                max_tokens=_MAX_TOKENS,
                temperature=0.0,
            )
            return resp.content[0].text
        except Exception as exc:
            delay = _RETRY_DELAY
            msg = str(exc).lower()
            m = re.search(r"retry after ([\d\.]+)s", msg)
            if m:
                delay = max(delay, float(m.group(1)) + 2.0)
                
            log.warning(
                "Anthropic API attempt %d/%d failed: %s (sleeping %.1fs)",
                attempt, _RETRY_LIMIT, exc, delay
            )
            if attempt < _RETRY_LIMIT:
                time.sleep(delay)
    return None


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(csv_path: Path) -> None:
    """Process every case and write results."""
    # ── Validate env ──────────────────────────────────────────────────────
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error(
            "ANTHROPIC_API_KEY environment variable is not set.  "
            "Ensure it is set in .env or exported in your shell."
        )
        sys.exit(1)

    # ── Lazy-import the SDK (avoids ImportError at module level if
    #    the user is only running tests or rule_checker) ────────────────────
    try:
        from anthropic import Anthropic
    except ImportError:
        log.error(
            "The 'anthropic' package is not installed.  Run:\n"
            "  pip install -r requirements.txt"
        )
        sys.exit(1)

    client = Anthropic(
        api_key=api_key
    )

    # ── Load prompts ──────────────────────────────────────────────────────
    system_prompt, user_template = _load_prompts(_PROMPT_PATH)
    log.info("Loaded prompt from %s", _PROMPT_PATH)

    # ── Load cases ────────────────────────────────────────────────────────
    df = pd.read_csv(csv_path)
    cases = df.to_dict(orient="records")
    log.info("Loaded %d case(s) from %s", len(cases), csv_path)

    # ── Process ───────────────────────────────────────────────────────────
    results: List[Dict[str, Any]] = []
    total = len(cases)

    for idx, case in enumerate(cases, 1):
        cid = case.get("case_id", f"row-{idx}")
        log.info("[%d/%d] Processing %s …", idx, total, cid)

        # ── Build user message ────────────────────────────────────────────
        user_msg = user_template.format(
            symptom=case.get("symptom", ""),
            topology_note=case.get("topology_note", ""),
            show_output=case.get("show_output", ""),
        )

        # ── Call AI ───────────────────────────────────────────────────────
        raw_response = _call_anthropic(client, system_prompt, user_msg)
        parsed: Optional[Dict[str, Any]] = None
        response_status = "API_FAILURE"
        api_error = "No response after retries"
        if raw_response is not None:
            parsed, response_status = _validate_ai_diagnosis(_parse_ai_json(raw_response))
            if parsed is None:
                log.warning(
                    "  %s: malformed JSON — skipping AI fields.  "
                    "Raw (first 300 chars): %s",
                    cid, raw_response[:300],
                )
                api_error = "Response did not match the required JSON contract"
            else:
                api_error = ""
        else:
            log.warning("  %s: no API response after retries", cid)

        # ── Rule checker ──────────────────────────────────────────────────
        rule_findings: List[Finding] = run_all_checks(case)
        rule_str = "; ".join(
            f"[{f.check_name}|{f.severity}] {f.description}"
            for f in rule_findings
        ) or "(none)"

        # ── Compare with expected ─────────────────────────────────────────
        ai_root = parsed.get("root_cause", "") if parsed else ""
        ai_osi = parsed.get("osi_layer", "") if parsed else ""
        ai_conf = parsed.get("confidence", "") if parsed else ""
        ai_evidence = json.dumps(parsed.get("evidence", [])) if parsed else "[]"
        ai_next = parsed.get("next_command", "") if parsed else ""
        ai_fix = (
            json.dumps(parsed.get("fix_steps", []))
            if parsed else "[]"
        )
        ai_verify = json.dumps(parsed.get("verification_steps", [])) if parsed else "[]"

        matches, notes = _compare_diagnosis(
            ai_root, ai_osi,
            case.get("expected_fault", ""),
            case.get("osi_layer", ""),
        )

        # Check AI vs rule-checker disagreement
        if rule_findings and parsed:
            rule_checks = {f.check_name for f in rule_findings}
            # If rule checker found something but AI doesn't mention
            # any of those check keywords → likely disagreement
            ai_combined = (ai_root + " " + ai_evidence).lower()
            rule_keywords = {
                "duplicate_ip": ["duplicate", "same ip"],
                "wrong_mask": ["mask", "subnet"],
                "gateway_mismatch": ["gateway", "default-router"],
                "interface_down": ["down", "shutdown", "administratively"],
                "missing_vlan": ["vlan", "missing vlan"],
                "missing_route": ["route", "missing route"],
            }
            for ck in rule_checks:
                kws = rule_keywords.get(ck, [])
                if not any(kw in ai_combined for kw in kws):
                    notes += f"; DISAGREE: rule_checker flagged '{ck}' but AI may not address it"

        results.append({
            "case_id": cid,
            "ai_root_cause": ai_root,
            "ai_confidence": ai_conf,
            "ai_evidence": ai_evidence,
            "ai_next_command": ai_next,
            "ai_fix_steps": ai_fix,
            "ai_verification_steps": ai_verify,
            "requires_human_review": True,
            "original_ai_answer": json.dumps(parsed) if parsed else "",
            "response_status": response_status,
            "api_error": api_error,
            "model_used": _MODEL,
            "model_version": _MODEL,
            "prompt_version": _PROMPT_VERSION,
            "rule_checker_findings": rule_str,
            "matches_expected": matches,
            "notes": notes,
        })

        status = "✓ match" if matches else "✗ mismatch"
        log.info("  %s  confidence=%s  %s", status, ai_conf, cid)
        
        # Rate limit protection: 1.5 seconds delay between calls
        time.sleep(1.5)

    # ── Write CSV ─────────────────────────────────────────────────────────
    out_df = pd.DataFrame(results)
    out_df.to_csv(_OUTPUT_CSV, index=False)
    log.info("Results written to %s", _OUTPUT_CSV)

    # ── Summary ───────────────────────────────────────────────────────────
    _print_summary(results)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def _print_summary(results: List[Dict[str, Any]]) -> None:
    """Print a concise summary table to stdout."""
    total = len(results)
    if total == 0:
        print("\n  No cases processed.\n")
        return

    agreed = sum(1 for r in results if r["matches_expected"])
    low_conf = sum(
        1 for r in results if r["ai_confidence"].lower() == "low"
    )
    no_response = sum(
        1 for r in results if not r["ai_root_cause"]
    )
    disagree = sum(
        1 for r in results if "DISAGREE" in r.get("notes", "")
    )

    rate = agreed / total * 100 if total else 0

    print(f"\n{'═' * 62}")
    print(f"  NetSage Diagnosis Run — Summary")
    print(f"{'═' * 62}")
    print(f"  Total cases processed:           {total}")
    print(f"  AI vs expected agreement:        {agreed}/{total} ({rate:.1f}%)")
    print(f"  Low-confidence AI responses:     {low_conf}")
    print(f"  No / malformed AI responses:     {no_response}")
    print(f"  Rule-checker ↔ AI disagreements: {disagree}")
    print(f"{'═' * 62}")

    # Per-case one-liner
    print(f"\n  {'case_id':<14} {'match':<9} {'confidence':<12} "
          f"{'rule_checks':<30}")
    print(f"  {'─' * 14} {'─' * 9} {'─' * 12} {'─' * 30}")
    for r in results:
        match_str = "✓" if r["matches_expected"] else "✗"
        conf = r["ai_confidence"] or "N/A"
        rules = (
            r["rule_checker_findings"][:28]
            if r["rule_checker_findings"] != "(none)"
            else "—"
        )
        print(f"  {r['case_id']:<14} {match_str:<9} {conf:<12} {rules:<30}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    csv_file = Path(sys.argv[1]) if len(sys.argv) > 1 else _DATA_DEFAULT
    if not csv_file.exists():
        log.error("CSV file not found: %s", csv_file)
        sys.exit(1)
    run(csv_file)
