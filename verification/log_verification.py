#!/usr/bin/env python3
"""Validate human-entered Packet Tracer verification records.

This tool records no synthetic pings or resolution claims. A row is considered
resolved only when a human supplied before/after evidence and selected RESOLVED.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALID_STATUSES = {"RESOLVED", "NOT_RESOLVED", "NOT_VERIFIED"}
REQUIRED = ("case_id", "verification_command", "verification_status")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for number, row in enumerate(rows, start=2):
        missing = [field for field in REQUIRED if not row.get(field, "").strip()]
        if missing:
            errors.append(f"row {number}: missing {', '.join(missing)}")
        status = row.get("verification_status", "").strip().upper()
        if status and status not in VALID_STATUSES:
            errors.append(f"row {number}: invalid verification_status {status}")
        if status == "RESOLVED" and (not row.get("before_result", "").strip() or not row.get("after_result", "").strip()):
            errors.append(f"row {number}: RESOLVED requires human-entered before_result and after_result")
    return errors


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "verification" / "verification_results.csv"
    problems = validate(source)
    for problem in problems:
        print(f"ERROR: {problem}")
    print("Verification records are valid." if not problems else "Verification records are invalid.")
    raise SystemExit(1 if problems else 0)
