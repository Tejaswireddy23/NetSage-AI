#!/usr/bin/env python3
"""Validate NetSage cross-file data consistency without making changes.

Usage: python scripts/validate_project.py [project-root]
Exit status is non-zero only for errors; missing optional workflow artefacts are
reported as warnings so the project remains usable before a live AI/PT run.
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data.case_schema import load_cases, missing_required_fields  # noqa: E402

VALID_DECISIONS = {"ACCEPTED", "EDITED", "REJECTED", ""}


def rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    cases_path = ROOT / "data" / "cases.csv"
    try:
        cases = load_cases(cases_path)
    except (OSError, csv.Error) as exc:
        print(f"ERROR: cannot load {cases_path}: {exc}")
        return 1

    ids = [str(case.get("case_id", "")).strip() for case in cases]
    duplicates = sorted(key for key, count in Counter(ids).items() if key and count > 1)
    if not ids:
        errors.append("cases.csv contains no cases")
    if "" in ids:
        errors.append("cases.csv contains a missing case_id")
    if duplicates:
        errors.append(f"duplicate case IDs: {', '.join(duplicates)}")
    for case in cases:
        missing = missing_required_fields(case)
        if missing:
            errors.append(f"{case.get('case_id', '<missing>')}: missing {', '.join(missing)}")

    case_ids = set(ids)
    for label, relative in (
        ("diagnosis", "runner/diagnosis_results.csv"),
        ("review", "review/review_template.csv"),
        ("verification", "verification/verification_results.csv"),
    ):
        artifact = ROOT / relative
        artifact_rows = rows(artifact)
        if not artifact_rows:
            warnings.append(f"{label} data is not available: {relative}")
            continue
        artifact_ids = {str(row.get("case_id", "")).strip() for row in artifact_rows}
        unknown = sorted(artifact_ids - case_ids - {""})
        if unknown:
            errors.append(f"{label} contains unknown case IDs: {', '.join(unknown)}")
        missing = sorted(case_ids - artifact_ids)
        if missing:
            warnings.append(f"{label} has no row for {len(missing)} case(s)")
        if label == "review":
            invalid = sorted({str(row.get("reviewer_decision", "")).upper().strip() for row in artifact_rows} - VALID_DECISIONS)
            if invalid:
                errors.append(f"invalid reviewer decisions: {', '.join(invalid)}")

    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")
    print(f"Validated {len(cases)} case(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
