#!/usr/bin/env python3
"""Check candidate fee amounts against the parent-law ceilings without promoting them."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "labour_law_14_2025"
CAP_EGP = 50_000
EXPECTED = {
    "decision_251_numeric_and_eligibility_candidates_2026-10-29.json": {
        "251-A11": ("consultant_A_initial_fee", 30_000),
        "251-A12": ("consultant_A_renewal_fee", 25_000),
        "251-A13": ("consultant_B_initial_fee", 25_000),
        "251-A14": ("consultant_B_renewal_fee", 20_000),
    },
    "decision_252_numeric_candidate_assertions_2026-10-29.json": {
        "252-N019": ("provider_licensing_fee", 3_000),
        "252-N020": ("provider_licensing_fee", 1_500),
        "252-N024": ("trainer_licensing_fee", 5_000),
    },
}
NON_LICENSE_FEES = {
    "252-N021": "training_programme_material_review_fee",
    "252-N022": "inspection_fee",
    "252-N023": "reinspection_fee",
}


def _assertion_map(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = record.get("assertions")
    if not isinstance(items, list):
        return {}
    return {item["id"]: item for item in items if isinstance(item, dict) and isinstance(item.get("id"), str)}


def validate(root: Path = DATA) -> list[str]:
    errors: list[str] = []
    records: dict[str, dict[str, dict[str, Any]]] = {}
    for filename in EXPECTED:
        path = root / filename
        if not path.is_file():
            errors.append(f"missing candidate file: {filename}")
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{filename}: cannot parse candidate JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{filename}: root must be an object")
            continue
        if record.get("official_file_match") != "pending":
            errors.append(f"{filename}: official file match must remain pending")
        if record.get("currentness") != "not_checked":
            errors.append(f"{filename}: currentness must remain not_checked")
        if record.get("counsel_review") != "not_reviewed":
            errors.append(f"{filename}: counsel review must remain not_reviewed")
        if record.get("authoritative_retrieval_eligible") is not False:
            errors.append(f"{filename}: authoritative retrieval must remain false")
        records[filename] = _assertion_map(record)

    for filename, expected in EXPECTED.items():
        items = records.get(filename, {})
        for identifier, (topic, amount) in expected.items():
            item = items.get(identifier)
            if item is None:
                errors.append(f"{filename}: missing expected fee assertion {identifier}")
                continue
            if item.get("topic") != topic:
                errors.append(f"{filename}: {identifier} topic must remain {topic}")
            if item.get("value") != amount or item.get("unit") != "EGP":
                errors.append(f"{filename}: {identifier} candidate amount/unit differs from the recorded cross-check")
            if isinstance(item.get("value"), (int, float)) and item["value"] > CAP_EGP:
                errors.append(f"{filename}: {identifier} exceeds the EGP {CAP_EGP} parent-law ceiling")
            if item.get("verified") is True or item.get("approved") is True or item.get("retrieval_eligible") is True:
                errors.append(f"{filename}: {identifier} has a forbidden promotion flag")

    decision252 = records.get("decision_252_numeric_candidate_assertions_2026-10-29.json", {})
    for identifier, expected_topic in NON_LICENSE_FEES.items():
        item = decision252.get(identifier)
        if item is None:
            errors.append(f"Decision 252: missing non-licence fee classification candidate {identifier}")
            continue
        if item.get("topic") != expected_topic:
            errors.append(f"Decision 252: {identifier} must remain separately classified as {expected_topic}")
        if item.get("verified") is True or item.get("approved") is True or item.get("retrieval_eligible") is True:
            errors.append(f"Decision 252: {identifier} has a forbidden promotion flag")

    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("FAIL: candidate fee ceiling cross-check failed")
        for problem in problems:
            print("- " + problem)
        raise SystemExit(1)
    print("OK: candidate licence fees are below the EGP 50,000 parent-law ceilings; non-licence charges remain separately classified.")
    print("LIMIT: secondary candidates only; no fee clause is officially matched, currentness-complete, counsel-approved or retrieval-eligible.")
