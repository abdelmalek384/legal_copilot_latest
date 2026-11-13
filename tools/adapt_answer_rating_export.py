#!/usr/bin/env python3
"""Adapt the richer firm answer-rating export to the canonical AI-1 CSV contract.

Requires message-time trust_tier in the source export. Rows whose cited article
accuracy is not_applicable are reported and excluded, never coerced to right/wrong.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from tools.output_path_safety import ensure_output_paths_safe
    from tools.validate_answer_ratings import EXPECTED_HEADER, validate_rows
except ModuleNotFoundError:  # direct execution from tools/
    from output_path_safety import ensure_output_paths_safe
    from validate_answer_ratings import EXPECTED_HEADER, validate_rows

SOURCE_REQUIRED = {
    "answer_id",
    "rating",
    "cited_article_accuracy",
    "notes",
    "rated_by",
    "updated_at",
    "trust_tier",
}
RATING_MAP = {
    "correct": "correct",
    "partially_correct": "partial",
    "wrong": "wrong",
}


def _timestamp(value: object, line_number: int) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"row {line_number}: updated_at must be a trimmed ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"row {line_number}: updated_at is not a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"row {line_number}: updated_at must include an explicit timezone")
    return parsed.isoformat().replace("+00:00", "Z")


def adapt_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[str]]:
    adapted: list[dict[str, str]] = []
    skipped_not_applicable: list[str] = []
    for line_number, row in enumerate(rows, start=2):
        answer_id = row.get("answer_id")
        if not isinstance(answer_id, str) or not answer_id.strip():
            raise ValueError(f"row {line_number}: answer_id is required")
        rating = row.get("rating")
        if not isinstance(rating, str) or rating not in RATING_MAP:
            raise ValueError(f"row {line_number}: rating must be correct, partially_correct, or wrong")
        cited = row.get("cited_article_accuracy")
        if not isinstance(cited, str) or cited not in {"right", "wrong", "not_applicable"}:
            raise ValueError(f"row {line_number}: cited_article_accuracy must be right, wrong, or not_applicable")
        notes = row.get("notes")
        if not isinstance(notes, str):
            raise ValueError(f"row {line_number}: notes must be a string (empty is allowed)")
        rater = row.get("rated_by")
        if not isinstance(rater, str) or not rater.strip():
            raise ValueError(f"row {line_number}: rated_by is required")
        timestamp = _timestamp(row.get("updated_at"), line_number)
        raw_tier = row.get("trust_tier")
        trust_tier = raw_tier.strip().lower() if isinstance(raw_tier, str) else ""
        canonical_tier = trust_tier if trust_tier in {"verified", "source_matched"} else "unverified"

        if cited == "not_applicable":
            skipped_not_applicable.append(answer_id)
            continue

        adapted.append({
            "answer_id": answer_id.strip(),
            "answer_rating": RATING_MAP[rating],
            "cited_article_rating": cited,
            "notes": notes,
            "rater": rater.strip(),
            "timestamp": timestamp,
            "trust_tier": canonical_tier,
        })

    validation = validate_rows(adapted)
    if not validation["valid_rows"] == len(adapted) or validation["invalid_rows"]:
        raise ValueError("adapted rows failed the canonical answer-rating contract: " +
                         json.dumps(validation["errors"], ensure_ascii=False))
    return adapted, skipped_not_applicable


def adapt_file(input_path: Path, output_path: Path) -> dict[str, Any]:
    input_path, output_path = Path(input_path), Path(output_path)
    ensure_output_paths_safe([output_path], [input_path])
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        fieldnames = reader.fieldnames or []
        if len(fieldnames) != len(set(fieldnames)):
            raise ValueError("firm export contains duplicate column names")
        missing = SOURCE_REQUIRED - set(fieldnames)
        if missing:
            raise ValueError("firm export is missing required columns: " + ", ".join(sorted(missing)))
        rows = list(reader)
        if any(None in row for row in rows):
            raise ValueError("firm export contains a row with more fields than its header")
        if any(any(value is None for value in row.values()) for row in rows):
            raise ValueError("firm export contains a row with fewer fields than its header")

    adapted, skipped = adapt_rows(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_HEADER, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(adapted)

    return {
        "valid": True,
        "input_rows": len(rows),
        "exported_rows": len(adapted),
        "skipped_not_applicable_rows": len(skipped),
        "skipped_answer_ids": skipped,
        "output": str(output_path),
        "encoding": "UTF-8 with BOM",
        "canonical_header": EXPECTED_HEADER,
        "trust_tier_rule": "message-time verified/source_matched preserved; all other values become unverified",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firm_export", type=Path)
    parser.add_argument("canonical_output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = adapt_file(args.firm_export, args.canonical_output)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
