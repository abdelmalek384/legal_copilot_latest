#!/usr/bin/env python3
"""Validate Decision 252's secondary Gazette-image candidate map only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "data" / "candidates" / "labour_law_14_2025" / "decision_252_secondary_article_candidate_map_2026-10-30.json"
EXPECTED_ARTICLES = set(range(1, 37))
BASE = "https://www.almasdar.com/WebP/libfiles/46/4/"


def validate(path: Path = DEFAULT_FILE) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing Decision 252 candidate map: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot parse Decision 252 candidate map: {exc}"]
    source = data.get("source", {})
    if source.get("class") != "secondary_scan_image_reproduction":
        errors.append("source must remain secondary_scan_image_reproduction")
    if source.get("original_gazette_pdf_obtained") is not False or source.get("official_pdf_sha256") is not None:
        errors.append("must not claim original Gazette PDF bytes/hash")
    if data.get("status") != "candidate_only_not_for_authoritative_retrieval":
        errors.append("top-level map must remain candidate-only")
    records = data.get("records")
    if not isinstance(records, list):
        return errors + ["records must be a list"]
    observed: set[int] = set()
    tables: set[int] = set()
    for record in records:
        rtype = record.get("record_type")
        rid = record.get("article") if rtype == "article" else record.get("table_number")
        if rtype == "article":
            if not isinstance(rid, int) or isinstance(rid, bool):
                errors.append(f"invalid article ID: {rid!r}")
            elif rid in observed:
                errors.append(f"duplicate article {rid}")
            else:
                observed.add(rid)
        elif rtype == "table":
            if not isinstance(rid, int) or isinstance(rid, bool):
                errors.append(f"invalid table ID: {rid!r}")
            elif rid in tables:
                errors.append(f"duplicate table {rid}")
            else:
                tables.add(rid)
        else:
            errors.append(f"unknown record_type: {rtype!r}")
        key = f"{rtype}:{rid}"
        if record.get("source_class") != "secondary_scan_image_reproduction":
            errors.append(f"{key}: wrong source class")
        if record.get("official_gazette_match") != "not_performed":
            errors.append(f"{key}: official match must remain not_performed")
        if record.get("official_pdf_sha256") is not None:
            errors.append(f"{key}: must not claim official PDF hash")
        if record.get("retrieval_eligible") is not False:
            errors.append(f"{key}: must remain retrieval-ineligible")
        if record.get("status") != "candidate_only_pending_official_match":
            errors.append(f"{key}: must remain pending official match")
        if not record.get("printed_gazette_pages") or not record.get("source_image_urls"):
            errors.append(f"{key}: missing page/image locator")
        for url in record.get("source_image_urls", []):
            if not isinstance(url, str) or not url.startswith(BASE) or not url.endswith(".webp"):
                errors.append(f"{key}: invalid image URL {url!r}")
    if observed != EXPECTED_ARTICLES:
        errors.append(f"article coverage mismatch: expected 1–36, got {sorted(observed)}")
    if tables != {29}:
        errors.append(f"table coverage mismatch: expected Table 29, got {sorted(tables)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    args = parser.parse_args()
    errors = validate(args.file)
    if errors:
        print("FAIL: Decision 252 candidate map invalid")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: Decision 252 Articles 1–36 and Table 29 locator map are complete and quarantined.")
    print("LIMIT: secondary scan reproductions only; no official match, currentness, counsel approval or retrieval eligibility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
