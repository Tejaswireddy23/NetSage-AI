#!/usr/bin/env python3
"""
review/log_reviews.py
=====================
Human-in-the-loop review workflow for NetSage AI diagnoses.

Sub-commands
------------
    python review/log_reviews.py generate-template
        Create / refresh ``review_template.csv`` from the latest
        diagnosis results (or ``data/cases.csv`` as fallback).

    python review/log_reviews.py generate-log
        Read the **completed** ``review_template.csv`` (after a human
        has filled in decisions) and produce ``responsible_ai_log.md``.
        Requires ≥ 5 Edited / Rejected rows.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import List

import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CASES_CSV = _PROJECT_ROOT / "data" / "cases.csv"
_DIAG_CSV = _PROJECT_ROOT / "runner" / "diagnosis_results.csv"
_REVIEW_DIR = Path(__file__).resolve().parent
_TEMPLATE_CSV = _REVIEW_DIR / "review_template.csv"
_LOG_MD = _REVIEW_DIR / "responsible_ai_log.md"

_MIN_CORRECTIONS = 5

# Red-herring case IDs (from Module 1) — suggested for closer review
_RED_HERRING_CASES = [
    "VLAN-005", "GW-005", "DHCP-004", "DNS-002", "DNS-004", "RT-004", "NAT-004",
]

# ── Stop words for keyword analysis ──────────────────────────────────────────
_STOP = {
    "the", "a", "an", "is", "are", "was", "were", "not", "no", "on", "in",
    "to", "of", "for", "and", "or", "but", "has", "have", "had", "that",
    "this", "it", "its", "be", "been", "being", "with", "from", "by", "at",
    "as", "so", "if", "do", "does", "did", "should", "would", "could", "can",
}


# ═══════════════════════════════════════════════════════════════════════════════
#  generate-template
# ═══════════════════════════════════════════════════════════════════════════════

def generate_template() -> None:
    """Create ``review_template.csv`` pre-populated with one row per case.

    Pulls ``ai_root_cause`` from ``runner/diagnosis_results.csv`` if it
    exists, otherwise uses a placeholder.  Decision columns are always
    left blank for the human reviewer.
    """
    cases = pd.read_csv(_CASES_CSV)

    if _DIAG_CSV.exists():
        diag = pd.read_csv(_DIAG_CSV)
        merged = cases[["case_id", "expected_fault"]].merge(
            diag[["case_id", "ai_root_cause"]],
            on="case_id",
            how="left",
        )
        source = str(_DIAG_CSV)
    else:
        merged = cases[["case_id", "expected_fault"]].copy()
        merged["ai_root_cause"] = "(pending — run runner/run_diagnosis.py first)"
        source = f"{_CASES_CSV} (diagnosis_results.csv not yet available)"

    # Blank columns the reviewer fills in
    merged["reviewer_decision"] = ""
    merged["corrected_diagnosis"] = ""
    merged["reviewer_notes"] = ""
    merged["reviewer_name"] = ""
    merged["review_date"] = ""

    # Ensure correct column order
    col_order = [
        "case_id",
        "ai_root_cause",
        "expected_fault",
        "reviewer_decision",
        "corrected_diagnosis",
        "reviewer_notes",
        "reviewer_name",
        "review_date",
    ]
    merged = merged[col_order]
    merged.to_csv(_TEMPLATE_CSV, index=False)

    print(f"\n  ✓ Template written to {_TEMPLATE_CSV}")
    print(f"    Source: {source}")
    print(f"    Rows:   {len(merged)}")
    print()
    print("  Next steps:")
    print("    1. Open review_template.csv in a spreadsheet editor")
    print("    2. For each row, set reviewer_decision to one of:")
    print("         Accepted  — AI diagnosis is correct")
    print("         Edited    — AI was partially right; fill corrected_diagnosis")
    print("         Rejected  — AI was wrong; fill corrected_diagnosis")
    print("    3. Optionally add reviewer_notes, reviewer_name, review_date")
    print(f"    4. Run:  python {Path(__file__).name} generate-log")
    print()
    print(f"  Tip: Pay extra attention to these red-herring cases:")
    print(f"    {', '.join(_RED_HERRING_CASES)}")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
#  generate-log
# ═══════════════════════════════════════════════════════════════════════════════

def _tokenise(text: str) -> set[str]:
    """Lowercase, strip punctuation, remove stop words."""
    return set(re.findall(r"[a-z0-9]+", str(text).lower())) - _STOP


def _infer_error_reason(
    ai_said: str,
    correct: str,
    reviewer_notes: str,
    concept_tag: str,
) -> str:
    """Best-effort inference of WHY the AI produced a wrong diagnosis.

    Priority:
      1. Reviewer's own notes (if substantive)
      2. Pattern matching on concept-tag vs. AI keywords
      3. Generic token-overlap analysis
    """
    notes = str(reviewer_notes).strip()
    if notes and notes.lower() not in ("", "nan", "none"):
        return notes

    ai_low = str(ai_said).lower()
    correct_low = str(correct).lower()
    tag_low = str(concept_tag).lower()

    # ── Known confusion patterns ──────────────────────────────────────────
    patterns = [
        # (ai_keyword, correct_keyword, explanation)
        ("dhcp", "dns",
         "Conflated DHCP scope issues with DNS failures because both "
         "produce similar user-facing symptoms (no name resolution / "
         "no connectivity)."),
        ("dns", "dhcp",
         "Misidentified a DHCP failure as a DNS issue because the "
         "user-visible symptom (can't browse) is common to both."),
        ("vlan", "rout",
         "Mistook a VLAN misconfiguration for a routing problem "
         "because both cause inter-network unreachability."),
        ("rout", "vlan",
         "Identified a routing fault when the real issue was VLAN "
         "assignment — the show output's routing table was a red "
         "herring that appeared incomplete."),
        ("acl", "vlan",
         "Focused on ACL rules when the underlying fault was a VLAN "
         "misconfiguration; the ACL in the output was a plausible but "
         "incorrect suspect."),
        ("acl", "nat",
         "Blamed an ACL for blocking traffic when the actual issue was "
         "a NAT misconfiguration; both can produce 'destination "
         "unreachable' symptoms."),
        ("nat", "rout",
         "Confused a NAT misconfiguration with a missing route — both "
         "prevent external connectivity, but the root cause was in the "
         "routing table."),
        ("gateway", "dhcp",
         "Identified the gateway as the problem when the root cause "
         "was in the DHCP pool configuration distributing wrong "
         "parameters."),
        ("mask", "vlan",
         "Focused on a subnet mask mismatch when the actual fault was "
         "VLAN assignment — the mask looked suspicious but was "
         "consistent with the intended design."),
        ("down", "vlan",
         "Flagged an interface-down condition as the primary fault "
         "when the real issue was a VLAN configuration error."),
        ("trunk", "rout",
         "Identified a trunk issue when the actual problem was in "
         "routing configuration — both affect inter-VLAN traffic."),
        ("exclus", "exhaust",
         "Confused DHCP address exclusion with pool exhaustion because "
         "the pool summary showed total addresses that obscured the "
         "effective exclusion."),
    ]

    for ai_kw, correct_kw, explanation in patterns:
        if ai_kw in ai_low and correct_kw in correct_low:
            return explanation

    # ── Red-herring detection ─────────────────────────────────────────────
    if "red herring" in tag_low or "herring" in correct_low:
        return (
            "The AI was misled by a red herring in the show output — "
            "plausible but irrelevant evidence drew attention away "
            "from the actual root cause."
        )

    # ── Token-overlap fallback ────────────────────────────────────────────
    ai_tokens = _tokenise(ai_said)
    correct_tokens = _tokenise(correct)
    if correct_tokens:
        overlap = len(ai_tokens & correct_tokens) / len(correct_tokens)
        if overlap < 0.2:
            return (
                "AI diagnosis diverged significantly from the actual fault — "
                "likely misread the show-command evidence or fixated on a "
                "secondary detail instead of the primary root cause."
            )

    return (
        "AI identified a related but incorrect root cause — the evidence "
        "in the show output pointed to a different underlying issue than "
        "what the AI concluded."
    )


def generate_log() -> None:
    """Read completed ``review_template.csv`` and produce
    ``responsible_ai_log.md`` + print agreement rate.
    """
    if not _TEMPLATE_CSV.exists():
        print(
            f"\n  ERROR: {_TEMPLATE_CSV} not found.\n"
            f"  Run 'python {Path(__file__).name} generate-template' first.\n"
        )
        sys.exit(1)

    df = pd.read_csv(_TEMPLATE_CSV)

    # Normalise decision column
    df["reviewer_decision"] = df["reviewer_decision"].astype(str).str.strip()

    valid_decisions = {"Accepted", "Edited", "Rejected"}
    reviewed = df[df["reviewer_decision"].isin(valid_decisions)].copy()
    not_reviewed = len(df) - len(reviewed)

    if reviewed.empty:
        print(
            "\n  ERROR: No rows have a reviewer_decision.\n"
            "  Open review_template.csv and fill in the "
            "'reviewer_decision' column first.\n"
        )
        sys.exit(1)

    corrections = reviewed[
        reviewed["reviewer_decision"].isin({"Edited", "Rejected"})
    ]

    if len(corrections) < _MIN_CORRECTIONS:
        print(
            f"\n  ERROR: Only {len(corrections)} Edited/Rejected row(s) found "
            f"(minimum {_MIN_CORRECTIONS} required).\n"
            f"  Please review more cases in review_template.csv.\n"
            f"  Tip: These red-herring cases are good candidates for "
            f"Edited/Rejected:\n"
            f"    {', '.join(_RED_HERRING_CASES)}\n"
        )
        sys.exit(1)

    # ── Load concept_tags from cases.csv for richer error analysis ────────
    concept_map: dict[str, str] = {}
    if _CASES_CSV.exists():
        cases = pd.read_csv(_CASES_CSV)
        concept_map = dict(zip(cases["case_id"], cases["concept_tag"]))

    # ── Agreement rate ────────────────────────────────────────────────────
    accepted = len(reviewed[reviewed["reviewer_decision"] == "Accepted"])
    edited = len(reviewed[reviewed["reviewer_decision"] == "Edited"])
    rejected = len(reviewed[reviewed["reviewer_decision"] == "Rejected"])
    total_reviewed = accepted + edited + rejected
    agreement_rate = accepted / total_reviewed * 100 if total_reviewed else 0

    # ── Build markdown ────────────────────────────────────────────────────
    lines: List[str] = []

    lines.append("# Responsible AI Review Log — NetSage")
    lines.append("")
    lines.append(f"> Generated on **{date.today().isoformat()}** by "
                 f"`review/log_reviews.py`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Total cases reviewed | {total_reviewed} |")
    lines.append(f"| Accepted (AI correct) | {accepted} |")
    lines.append(f"| Edited (partially correct) | {edited} |")
    lines.append(f"| Rejected (AI wrong) | {rejected} |")
    lines.append(f"| Not yet reviewed | {not_reviewed} |")
    lines.append(
        f"| **Agreement rate** | "
        f"**{accepted}/{total_reviewed} ({agreement_rate:.1f}%)** |"
    )
    lines.append("")

    if agreement_rate >= 80:
        lines.append("> [!NOTE]")
        lines.append(f"> Agreement rate of {agreement_rate:.1f}% indicates "
                     f"strong AI performance on this dataset.")
    elif agreement_rate >= 60:
        lines.append("> [!WARNING]")
        lines.append(f"> Agreement rate of {agreement_rate:.1f}% — AI "
                     f"diagnoses need human verification before action.")
    else:
        lines.append("> [!CAUTION]")
        lines.append(f"> Agreement rate of {agreement_rate:.1f}% is below "
                     f"acceptable threshold — review AI prompt and training "
                     f"examples.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Cases Requiring Correction")
    lines.append("")
    lines.append(
        "Each entry below documents a case where the AI diagnosis was "
        "**Edited** or **Rejected** by a human reviewer, along with an "
        "analysis of *why* the AI likely produced an incorrect result."
    )
    lines.append("")

    for _, row in corrections.iterrows():
        cid = row["case_id"]
        decision = row["reviewer_decision"]
        ai_said = str(row.get("ai_root_cause", "")).strip()
        expected = str(row.get("expected_fault", "")).strip()

        corrected = str(row.get("corrected_diagnosis", "")).strip()
        if not corrected or corrected.lower() in ("", "nan", "none"):
            corrected = expected  # fall back to ground truth

        notes = str(row.get("reviewer_notes", "")).strip()
        reviewer = str(row.get("reviewer_name", "")).strip()
        rev_date = str(row.get("review_date", "")).strip()
        concept = concept_map.get(cid, "")

        why = _infer_error_reason(ai_said, corrected, notes, concept)

        badge = "🔴 Rejected" if decision == "Rejected" else "🟡 Edited"
        lines.append(f"### {cid} — {badge}")
        lines.append("")
        lines.append(f"| Field | Detail |")
        lines.append(f"|---|---|")
        lines.append(f"| **AI said** | {ai_said} |")
        lines.append(f"| **Correct diagnosis** | {corrected} |")
        lines.append(f"| **Decision** | {decision} |")
        if concept:
            lines.append(f"| **Concept area** | {concept} |")
        if reviewer and reviewer.lower() not in ("nan", "none"):
            lines.append(f"| **Reviewer** | {reviewer} |")
        if rev_date and rev_date.lower() not in ("nan", "none"):
            lines.append(f"| **Review date** | {rev_date} |")
        lines.append("")

        lines.append(f"**Why the AI likely got it wrong:**")
        lines.append(f"{why}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # ── Patterns & recommendations ────────────────────────────────────────
    lines.append("## Observed Error Patterns")
    lines.append("")

    # Tally concept_tags of failed cases
    tag_counts: dict[str, int] = {}
    for _, row in corrections.iterrows():
        tag = concept_map.get(row["case_id"], "Unknown")
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if tag_counts:
        lines.append("| Concept Area | Correction Count |")
        lines.append("|---|---|")
        for tag, cnt in sorted(tag_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {tag} | {cnt} |")
        lines.append("")
        top_tag = max(tag_counts, key=tag_counts.get)  # type: ignore[arg-type]
        lines.append(
            f"> [!IMPORTANT]\n"
            f"> The AI struggled most with **{top_tag}** cases "
            f"({tag_counts[top_tag]} correction(s)). Consider adding more "
            f"few-shot examples for this category in "
            f"`prompts/diagnose_prompt.md`."
        )
    lines.append("")

    _LOG_MD.write_text("\n".join(lines), encoding="utf-8")

    # ── Console output ────────────────────────────────────────────────────
    print(f"\n{'═' * 60}")
    print(f"  Responsible AI Log generated")
    print(f"{'═' * 60}")
    print(f"  Output:          {_LOG_MD}")
    print(f"  Cases reviewed:  {total_reviewed}")
    print(f"  Accepted:        {accepted}")
    print(f"  Edited:          {edited}")
    print(f"  Rejected:        {rejected}")
    print(f"  ─────────────────────────────")
    print(f"  Agreement rate:  {accepted}/{total_reviewed} "
          f"({agreement_rate:.1f}%)")
    print(f"{'═' * 60}\n")


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════════

_USAGE = f"""\
Usage:
  python {Path(__file__).name} generate-template
      Create review_template.csv pre-populated from diagnosis results.

  python {Path(__file__).name} generate-log
      Read completed review_template.csv and produce responsible_ai_log.md.
"""


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(_USAGE)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "generate-template":
        generate_template()
    elif cmd == "generate-log":
        generate_log()
    else:
        print(f"Unknown command: {cmd}\n")
        print(_USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
