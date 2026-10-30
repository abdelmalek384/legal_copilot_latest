#!/usr/bin/env python3
"""Fail-closed structural/arithmetic validator for Decision 250 Table 23 candidates.

This tool does not verify the Official Gazette, authenticate CAS identifiers, or
approve thresholds for legal or workplace-safety use.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "data" / "candidates" / "labour_law_14_2025" / "decision_250_table23_first_page_candidate_rows_2026-10-29.json"
EXPECTED_SOURCE_QUALITY = "secondary_hosted_reproduction_of_gazette_page_image"
ALLOWED_ROW_STATUSES = {
    "scan_candidate_pending_match",
    "secondary_text_value_added_pending_official_match",
    "secondary_text_transcription_added_pending_official_match",
}
LB_PER_KG = 2.2046226218
MAX_RELATIVE_UNIT_DIFFERENCE = 0.015


def validate_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["candidate file must be a JSON object"]
    if data.get("record_type") != "hazardous_substance_threshold_quantity_candidates":
        errors.append("wrong record_type")
    if data.get("instrument") != "Egyptian Labour Ministry Decision 250/2026":
        errors.append("wrong instrument")
    if data.get("table") != 23:
        errors.append("table must be 23")
    if data.get("source_quality") != EXPECTED_SOURCE_QUALITY:
        errors.append("source_quality must remain a secondary hosted reproduction")
    if data.get("official_pdf_downloaded_and_hashed") is not False:
        errors.append("must not claim the official PDF was downloaded and hashed")
    if data.get("official_file_match") != "pending":
        errors.append("official_file_match must remain pending")
    if data.get("counsel_review") != "not_reviewed":
        errors.append("counsel_review must remain not_reviewed")
    if data.get("authoritative_retrieval_eligible") is not False:
        errors.append("Table 23 candidates must remain ineligible for authoritative retrieval")

    rows = data.get("rows")
    if not isinstance(rows, list):
        return errors + ["rows must be a list"]
    observed: dict[int, int] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"row index {index}: row must be an object")
            continue
        number = row.get("row")
        if not isinstance(number, int) or isinstance(number, bool):
            errors.append(f"row index {index}: row number must be an integer")
            continue
        if number in observed:
            errors.append(f"duplicate row number {number}")
        else:
            observed[number] = index
        for field in ("name_en", "name_ar"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f"row {number}: missing {field}")
        cas = row.get("cas")
        if cas is not None and (not isinstance(cas, str) or not cas.strip()):
            errors.append(f"row {number}: cas must be null or a non-empty string")
        for field in ("quantity_kg", "quantity_lb"):
            value = row.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                errors.append(f"row {number}: {field} must be a positive finite number")
        if row.get("status") not in ALLOWED_ROW_STATUSES:
            errors.append(f"row {number}: candidate status is not an allowed pending status")
        if row.get("verified") is True or row.get("approved") is True or row.get("retrieval_eligible") is True:
            errors.append(f"row {number}: forbidden promotion/approval flag in candidate-only data")
        if isinstance(row.get("quantity_kg"), (int, float)) and not isinstance(row.get("quantity_kg"), bool) and isinstance(row.get("quantity_lb"), (int, float)) and not isinstance(row.get("quantity_lb"), bool) and row["quantity_kg"] > 0:
            expected_lb = row["quantity_kg"] * LB_PER_KG
            relative_difference = abs(row["quantity_lb"] - expected_lb) / expected_lb
            if relative_difference > MAX_RELATIVE_UNIT_DIFFERENCE:
                errors.append(
                    f"row {number}: kg/lb candidate values differ by more than "
                    f"{MAX_RELATIVE_UNIT_DIFFERENCE:.1%}; inspect source, do not auto-correct"
                )

    expected = set(range(1, 138))
    actual = set(observed)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if len(rows) != 137:
        errors.append(f"expected 137 candidate rows, got {len(rows)}")
    if missing:
        errors.append(f"missing row numbers: {missing}")
    if unexpected:
        errors.append(f"unexpected row numbers: {unexpected}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="Table 23 candidate JSON file")
    args = parser.parse_args()
    try:
        data = json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read candidate JSON: {exc}")
    errors = validate_data(data)
    if errors:
        print("FAIL: Table 23 candidate structure/arithmetic validation failed")
        for error in errors:
            print("- " + error)
        return 1
    print("OK: 137 unique candidate rows; row numbers 1–137; kg/lb pairs are arithmetically consistent within 1.5%.")
    print("LIMIT: secondary transcription only; official match, currentness, source-use and counsel review remain pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
