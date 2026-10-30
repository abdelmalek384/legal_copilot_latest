#!/usr/bin/env python3
"""Create a blank, fail-closed primary-source match register for Table 24.

The register is a workflow template, not a claim that any source has been
verified. It never assigns an official page, hash, currentness result, legal
conclusion, counsel approval, or retrieval eligibility.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from validate_decision250_table24_candidates import BATCHES, DATA_DIR, flatten_rows, validate
except ImportError:
    from tools.validate_decision250_table24_candidates import BATCHES, DATA_DIR, flatten_rows, validate


def build_register(root: Path = DATA_DIR) -> list[dict[str, Any]]:
    errors = validate(root)
    if errors:
        raise ValueError("candidate batches failed validation: " + "; ".join(errors[:10]))
    records: list[dict[str, Any]] = []
    for filename in BATCHES:
        path = root / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        source = data["source"]
        for row in flatten_rows(data["rows"]):
            label = str(row.get("name_en") or "")
            name_ar = str(row.get("name_ar") or "")
            record_kind = "unresolved_placeholder" if "placeholder" in str(row.get("anomaly", "")).lower() else "candidate"
            records.append({
                "instrument": "Minister of Labour Decision 250/2026",
                "table": 24,
                "candidate_row": row["row"],
                "candidate_record_kind": record_kind,
                "candidate_name_en": label,
                "candidate_name_ar": name_ar,
                "candidate_cas": row.get("raw_cas_token") or row.get("cas"),
                "candidate_source_class": source.get("class"),
                "candidate_source_url": source.get("url"),
                "candidate_source_line": row.get("source_line"),
                "candidate_batch_file": filename,
                "official_source_url": None,
                "official_pdf_sha256": None,
                "official_printed_page": None,
                "official_page_image_review": "not_started",
                "candidate_to_official_text_match": "not_started",
                "currentness_review": "not_started",
                "source_use_review": "not_started",
                "counsel_review": "not_started",
                "retrieval_eligible": False,
                "review_notes": None,
            })
    records.sort(key=lambda item: item["candidate_row"])
    numbers = [item["candidate_row"] for item in records]
    if len(numbers) != len(set(numbers)):
        raise ValueError("duplicate candidate_row values in register input")
    expected = list(range(1, 782))
    if numbers != expected:
        raise ValueError(f"expected candidate rows 1–781, got {len(numbers)} records; gaps/ordering must be fixed first")
    if any(item["retrieval_eligible"] for item in records):
        raise ValueError("register must initialize every row as retrieval-ineligible")
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DATA_DIR,
                        help="Directory containing the validated candidate JSON batches")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output JSONL path (default: stdout)")
    args = parser.parse_args()
    records = build_register(args.root)
    result = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in records)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
        print(f"Wrote {len(records)} fail-closed row records to {args.output}")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
