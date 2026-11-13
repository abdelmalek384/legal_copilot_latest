#!/usr/bin/env python3
"""Validate Legal Copilot answer-rating CSV exports against docs/answer_rating_contract.md.

Accepts UTF-8 (with or without BOM), enforces the exact column order, required
fields, enum values and timezone-aware ISO-8601 timestamps. It never changes
trust tiers or treats ratings as legal verification.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

EXPECTED_HEADER = [
    "answer_id",
    "answer_rating",
    "cited_article_rating",
    "notes",
    "rater",
    "timestamp",
    "trust_tier",
]
ANSWER_RATINGS = {"correct", "partial", "wrong"}
CITED_ARTICLE_RATINGS = {"right", "wrong"}
TRUST_TIERS = {"verified", "source_matched", "unverified"}


def validate_rows(rows):
    errors = []
    valid = 0
    for line_number, row in enumerate(rows, start=2):
        row_errors = []
        for field in ("answer_id", "rater", "timestamp", "answer_rating",
                      "cited_article_rating", "trust_tier"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                row_errors.append(f"{field} is required")
        if row.get("answer_rating") not in ANSWER_RATINGS:
            row_errors.append("answer_rating must be correct, partial, or wrong")
        if row.get("cited_article_rating") not in CITED_ARTICLE_RATINGS:
            row_errors.append("cited_article_rating must be right or wrong")
        if row.get("trust_tier") not in TRUST_TIERS:
            row_errors.append("trust_tier must be verified, source_matched, or unverified")
        timestamp = row.get("timestamp")
        if isinstance(timestamp, str) and timestamp.strip():
            try:
                parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if parsed.tzinfo is None or parsed.utcoffset() is None:
                    row_errors.append("timestamp must include an explicit timezone")
            except ValueError:
                row_errors.append("timestamp must be a valid ISO-8601 datetime")
        if row_errors:
            errors.append({"line": line_number, "answer_id": row.get("answer_id", ""), "errors": row_errors})
        else:
            valid += 1
    return {"valid_rows": valid, "invalid_rows": len(errors), "errors": errors}


def validate_file(path):
    try:
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, strict=True)
            if reader.fieldnames != EXPECTED_HEADER:
                return {
                    "valid": False,
                    "error": "CSV header does not match the exact answer rating contract",
                    "expected_header": EXPECTED_HEADER,
                    "actual_header": reader.fieldnames,
                }
            rows = []
            for row in reader:
                if None in row:
                    return {"valid": False, "error": "row contains more fields than the header"}
                if any(value is None for value in row.values()):
                    return {"valid": False, "error": "row contains fewer fields than the header"}
                rows.append(row)
            result = validate_rows(rows)
            result["valid"] = result["invalid_rows"] == 0
            result["header"] = EXPECTED_HEADER
            return result
    except (OSError, UnicodeError, csv.Error) as exc:
        return {"valid": False, "error": str(exc)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", help="UTF-8 answer-rating export to validate")
    args = parser.parse_args(argv)
    result = validate_file(args.csv_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
