#!/usr/bin/env python3
"""Validate the structure of the quarantined Decision 250 Table 24 candidate batches.

This validator checks metadata/row bookkeeping only. It does not authenticate the
secondary transcription, compare the Official Gazette, interpret limit columns,
review currentness/rights, or approve content for retrieval.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "candidates" / "labour_law_14_2025"
EXPECTED_SOURCE = "https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html"
BATCHES = [
    "decision_250_table24_candidate_batch1_rows001_020_2026-10-29.json",
    "decision_250_table24_candidate_batch2_rows021_040_2026-10-29.json",
    "decision_250_table24_candidate_batch3_rows041_060_2026-10-29.json",
    "decision_250_table24_candidate_batch4_rows061_080_2026-10-29.json",
    "decision_250_table24_candidate_batch5_rows081_100_2026-10-29.json",
    "decision_250_table24_candidate_batch6_rows100_120_2026-10-29.json",
    "decision_250_table24_candidate_batch7_rows121_140_2026-10-29.json",
    "decision_250_table24_candidate_batch8_rows141_160_2026-10-29.json",
    "decision_250_table24_candidate_batch9_rows161_180_2026-10-29.json",
    "decision_250_table24_candidate_batch10_rows181_200_2026-10-29.json",
    "decision_250_table24_candidate_batch11_rows201_220_2026-10-29.json",
    "decision_250_table24_candidate_batch12_rows221_240_2026-10-29.json",
    "decision_250_table24_candidate_batch13_rows241_260_2026-10-29.json",
    "decision_250_table24_candidate_batch14_rows261_280_2026-10-29.json",
    "decision_250_table24_candidate_batch15_rows281_300_2026-10-29.json",
    "decision_250_table24_candidate_batch16_rows301_320_2026-10-29.json",
    "decision_250_table24_candidate_batch17_rows321_340_2026-10-29.json",
    "decision_250_table24_candidate_batch18_rows341_360_2026-10-29.json",
    "decision_250_table24_candidate_batch19_rows361_380_2026-10-29.json",
    "decision_250_table24_candidate_batch20_rows381_403_2026-10-29.json",
    "decision_250_table24_candidate_batch21_rows404_423_2026-10-29.json",
    "decision_250_table24_candidate_batch22_rows424_443_2026-10-29.json",
    "decision_250_table24_candidate_batch23_rows444_463_2026-10-29.json",
    "decision_250_table24_candidate_batch24_rows464_483_2026-10-29.json",
    "decision_250_table24_candidate_batch25_rows484_503_2026-10-29.json",
    "decision_250_table24_candidate_batch26_rows504_523_2026-10-29.json",
    "decision_250_table24_candidate_batch27_rows524_543_2026-10-29.json",
    "decision_250_table24_candidate_batch28_rows544_563_2026-10-29.json",
    "decision_250_table24_candidate_batch29_rows564_583_2026-10-29.json",
    "decision_250_table24_candidate_batch30_rows584_603_2026-10-29.json",
    "decision_250_table24_candidate_batch31_rows604_617_2026-10-29.json",
    "decision_250_table24_candidate_batch32_rows618_642_2026-10-30.json",
    "decision_250_table24_candidate_batch33_rows643_668_2026-10-30.json",
    "decision_250_table24_candidate_batch34_rows669_694_2026-10-30.json",
    "decision_250_table24_candidate_batch35_rows695_720_2026-10-30.json",
    "decision_250_table24_candidate_batch36_rows721_746_2026-10-30.json",
    "decision_250_table24_candidate_batch37_rows747_772_2026-10-30.json",
    "decision_250_table24_candidate_batch38_rows773_781_2026-10-30.json",
]


def flatten_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for row in rows:
        flattened.append(row)
        children = row.get("children", [])
        if not isinstance(children, list):
            raise ValueError(f"row {row.get('row')} children must be a list")
        if any(not isinstance(child, dict) for child in children):
            raise ValueError(f"row {row.get('row')} contains a non-object child")
        flattened.extend(flatten_rows(children))
    return flattened


def validate(root: Path = DATA_DIR) -> list[str]:
    errors: list[str] = []
    observed: dict[int, str] = {}
    for filename in BATCHES:
        path = root / filename
        if not path.is_file():
            errors.append(f"missing batch file: {filename}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{filename}: cannot parse JSON: {exc}")
            continue

        if data.get("record_type") != "secondary_source_candidate_extraction":
            errors.append(f"{filename}: wrong record_type")
        source = data.get("source")
        if not isinstance(source, dict) or source.get("url") != EXPECTED_SOURCE:
            errors.append(f"{filename}: missing expected secondary source URL")
        if not isinstance(source, dict) or source.get("class") != "secondary_transcription":
            errors.append(f"{filename}: source must be classified as secondary_transcription")
        if isinstance(source, dict) and source.get("official_pdf_sha256") is not None:
            errors.append(f"{filename}: must not claim an official PDF hash before obtaining the original bytes")
        if not isinstance(source, dict) or source.get("official_gazette_match") != "not_performed":
            errors.append(f"{filename}: must explicitly state official Gazette match was not performed")
        if data.get("status") != "candidate_only_not_for_authoritative_retrieval":
            errors.append(f"{filename}: candidate must remain ineligible for authoritative retrieval")

        rows = data.get("rows")
        if not isinstance(rows, list):
            errors.append(f"{filename}: rows must be a list")
            continue
        try:
            flattened = flatten_rows(rows)
        except ValueError as exc:
            errors.append(f"{filename}: {exc}")
            continue

        for row in flattened:
            number = row.get("row")
            if not isinstance(number, int) or isinstance(number, bool) or number < 1:
                errors.append(f"{filename}: invalid row number {number!r}")
                continue
            if number in observed:
                errors.append(f"duplicate Table 24 row {number} in {observed[number]} and {filename}")
            else:
                observed[number] = filename
            if not isinstance(row.get("source_line"), int):
                errors.append(f"{filename}: row {number} missing integer source_line")
            if not isinstance(row.get("name_en"), str) or not row["name_en"].strip():
                errors.append(f"{filename}: row {number} missing English name/label")
            if not isinstance(row.get("name_ar"), str) or not row["name_ar"].strip():
                errors.append(f"{filename}: row {number} missing Arabic name/label")
            if row.get("status") != "pending_official_match":
                errors.append(f"{filename}: row {number} must remain pending_official_match")
            if row.get("retrieval_eligible") is True or row.get("verified") is True or row.get("approved") is True:
                errors.append(f"{filename}: row {number} contains a forbidden promotion/approval flag in candidate-only data")

    expected = set(range(1, 782))
    actual = set(observed)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        errors.append(f"missing Table 24 row numbers: {missing}")
    if unexpected:
        errors.append(f"unexpected Table 24 row numbers: {unexpected}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DATA_DIR,
                        help="Directory containing the five candidate JSON files")
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        print("FAIL: Decision 250 Table 24 candidate structure is incomplete/invalid")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: rows 1–781 are structurally present exactly once; every row remains pending official match.")
    print("LIMIT: this does not establish authenticity, legal status, reuse permission, or retrieval eligibility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
