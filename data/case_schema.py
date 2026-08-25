"""Canonical, backwards-compatible NetSage case-data helpers.

The project continues to accept the original eight-column ``cases.csv``.
New columns are optional and JSON-list fields are normalised when read.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

REQUIRED_CASE_FIELDS = (
    "case_id", "symptom", "topology_note", "show_output", "expected_fault",
    "osi_layer", "concept_tag", "severity",
)

EXTENDED_CASE_FIELDS = (
    "title", "category", "topology_image", "packet_tracer_file", "expected_fix",
    "verification_commands", "expected_verification_result",
)

LIST_FIELDS = {"expected_fix", "verification_commands"}


def parse_list(value: Any) -> list[str]:
    """Read a JSON array while safely supporting legacy blank/plain values."""
    if value is None or str(value).strip() == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return [str(value)]
    return [str(item) for item in parsed] if isinstance(parsed, list) else [str(value)]


def case_category(case: dict[str, Any]) -> str:
    """Use a supplied category or derive a stable legacy category from case ID."""
    if str(case.get("category", "")).strip():
        return str(case["category"]).strip().upper()
    prefix = str(case.get("case_id", "")).split("-", 1)[0].upper()
    return {"GW": "GATEWAY", "RT": "ROUTING", "WL": "WIRELESS"}.get(prefix, prefix)


def normalise_case(row: dict[str, Any]) -> dict[str, Any]:
    """Return one case with every optional field available to downstream code."""
    case = {key: ("" if value is None else value) for key, value in row.items()}
    for field in EXTENDED_CASE_FIELDS:
        case.setdefault(field, "")
    for field in LIST_FIELDS:
        case[field] = parse_list(case[field])
    case["category"] = case_category(case)
    if not case["title"]:
        case["title"] = case["expected_fault"].split(".", 1)[0]
    return case


def load_cases(path: str | Path, metadata_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load UTF-8 CSV case data and optionally merge additive metadata.

    ``case_metadata.csv`` is intentionally separate from the original dataset:
    existing tools that understand only the legacy file keep working unchanged.
    """
    source = Path(path)
    with source.open(encoding="utf-8", newline="") as handle:
        cases = list(csv.DictReader(handle))
    meta_source = Path(metadata_path) if metadata_path else source.with_name("case_metadata.csv")
    metadata: dict[str, dict[str, str]] = {}
    if meta_source.exists():
        with meta_source.open(encoding="utf-8", newline="") as handle:
            metadata = {row.get("case_id", ""): row for row in csv.DictReader(handle)}
    return [normalise_case({**row, **metadata.get(row.get("case_id", ""), {})}) for row in cases]


def missing_required_fields(case: dict[str, Any], fields: Iterable[str] = REQUIRED_CASE_FIELDS) -> list[str]:
    return [field for field in fields if not str(case.get(field, "")).strip()]
