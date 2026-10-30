#!/usr/bin/env python3
"""Validate Decision 249's secondary Gazette-image locator map only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "data" / "candidates" / "labour_law_14_2025" / "decision_249_secondary_article_table_map_2026-10-30.json"
EXPECTED_ARTICLES = set(range(1, 23))
EXPECTED_OTHER = {("table", 1), ("table", 2), ("table", 3), ("appendix", "high_risk_criteria")}
BASE = "https://www.almasdar.com/WebP/libfiles/46/3/"


def validate(path: Path = DEFAULT_FILE) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing Decision 249 candidate map: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot parse Decision 249 candidate map: {exc}"]

    source = data.get("source", {})
    if source.get("class") != "secondary_scan_image_reproduction":
        errors.append("source must remain classified as secondary_scan_image_reproduction")
    if source.get("original_gazette_pdf_obtained") is not False or source.get("official_pdf_sha256") is not None:
        errors.append("must not claim original Gazette PDF bytes/hash")
    if data.get("status") != "candidate_only_not_for_authoritative_retrieval":
        errors.append("top-level map must remain candidate-only")
    records = data.get("records")
    if not isinstance(records, list):
        return errors + ["records must be a list"]

    articles: set[int] = set()
    other: set[tuple] = set()
    for index, record in enumerate(records):
        rtype, rid = record.get("record_type"), record.get("record_id")
        key = (rtype, rid)
        if rtype == "article":
            if not isinstance(rid, int) or isinstance(rid, bool):
                errors.append(f"record {index}: article ID must be an integer")
            elif rid in articles:
                errors.append(f"duplicate article {rid}")
            else:
                articles.add(rid)
        else:
            if key in other:
                errors.append(f"duplicate non-article record {key}")
            other.add(key)
        if record.get("source_class") != "secondary_scan_image_reproduction":
            errors.append(f"record {key}: wrong source class")
        if record.get("official_gazette_match") != "not_performed":
            errors.append(f"record {key}: must state official Gazette match not performed")
        if record.get("official_pdf_sha256") is not None:
            errors.append(f"record {key}: must not claim official PDF hash")
        if record.get("retrieval_eligible") is not False:
            errors.append(f"record {key}: must remain retrieval-ineligible")
        if record.get("status") != "candidate_only_pending_official_match":
            errors.append(f"record {key}: must remain pending official match")
        if not record.get("printed_gazette_pages") or not record.get("source_image_urls"):
            errors.append(f"record {key}: missing printed page or image locator")
        for url in record.get("source_image_urls", []):
            if not isinstance(url, str) or not url.startswith(BASE) or not url.endswith(".webp"):
                errors.append(f"record {key}: unexpected image locator {url!r}")
    if articles != EXPECTED_ARTICLES:
        errors.append(f"article coverage mismatch: expected 1–22, got {sorted(articles)}")
    if other != EXPECTED_OTHER:
        errors.append(f"table/appendix coverage mismatch: expected {EXPECTED_OTHER}, got {other}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    args = parser.parse_args()
    errors = validate(args.file)
    if errors:
        print("FAIL: Decision 249 candidate map invalid")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: Decision 249 Articles 1–22, Tables 1–3 and high-risk criteria locator map are complete and quarantined.")
    print("LIMIT: secondary scan reproductions only; no official Gazette match, currentness, counsel approval or retrieval eligibility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
