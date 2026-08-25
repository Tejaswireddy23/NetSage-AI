#!/usr/bin/env python3
"""Create documentation-only Packet Tracer lab specifications.

This script never creates a .pkt file. It turns the source case evidence into a
per-case README and expected.json so a Cisco Packet Tracer author has an honest,
traceable build checklist.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data.case_schema import load_cases  # noqa: E402


def document(case: dict) -> str:
    commands = case.get("verification_commands") or ["REQUIRES HUMAN INPUT: choose commands after building the topology"]
    return f"""# {case['case_id']} — {case['title']}

## Lab status

**REQUIRES PACKET TRACER.** Create and save `{case['packet_tracer_file']}` in Cisco
Packet Tracer. This repository does not provide or fabricate a `.pkt` binary.

## Scenario from the source case

- Category: {case['category']}
- Severity: {case['severity']}
- OSI layer: {case['osi_layer']}
- Concept: {case['concept_tag']}
- Symptom: {case['symptom']}
- Topology note: {case['topology_note']}

## Build procedure

1. Build the working topology described above in Cisco Packet Tracer.
2. Document the device list, interfaces, IP addressing, VLANs, and routing in
   the Packet Tracer file notes or an attached screenshot.
3. Verify the working baseline before introducing one fault only.
4. Introduce the expected fault below and save the broken lab at the `.pkt` path.
5. Run the supplied show commands, capture actual output, and compare it with
   the source evidence below.

## Intentional fault and expected outcome

- Root cause: {case['expected_fault']}
- Expected symptom: {case['symptom']}
- Expected fix: {case.get('expected_fix') or 'REQUIRES HUMAN INPUT — derive from actual Packet Tracer configuration.'}
- Verification commands: {commands}
- Expected verification result: {case['expected_verification_result']}

## Source pre-fix evidence

```text
{case['show_output']}
```

## Verification record

Do not claim this lab is resolved until a human records the real before/after
results in `verification/verification_results.csv`.
"""


def main() -> None:
    labs = ROOT / "labs"
    for case in load_cases(ROOT / "data" / "cases.csv"):
        target = labs / case["category"] / case["case_id"]
        target.mkdir(parents=True, exist_ok=True)
        expected = {
            "case_id": case["case_id"], "status": "REQUIRES PACKET TRACER",
            "packet_tracer_file": case["packet_tracer_file"],
            "topology_note": case["topology_note"], "expected_fault": case["expected_fault"],
            "expected_fix": case["expected_fix"],
            "verification_commands": case["verification_commands"],
            "expected_verification_result": case["expected_verification_result"],
            "source_evidence": case["show_output"],
        }
        (target / "expected.json").write_text(json.dumps(expected, indent=2), encoding="utf-8")
        (target / "README.md").write_text(document(case), encoding="utf-8")
    print("Created documentation-only specifications; no .pkt files were created.")


if __name__ == "__main__":
    main()
