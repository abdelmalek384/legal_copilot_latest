#!/usr/bin/env python3
"""Validate Decision 251's secondary Gazette-image candidate map only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "data" / "candidates" / "labour_law_14_2025" / "decision_251_secondary_article_candidate_map_2026-10-30.json"
EXPECTED_ARTICLES = set(range(1, 12))
BASE = "https://www.almasdar.com/WebP/libfiles/46/4/"


def validate(path: Path = DEFAULT_FILE) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing Decision 251 candidate map: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot parse Decision 251 candidate map: {exc}"]

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
    by_article = {}
    for record in records:
        article = record.get("article")
        if not isinstance(article, int) or isinstance(article, bool):
            errors.append(f"invalid article ID: {article!r}")
            continue
        if article in observed:
            errors.append(f"duplicate article {article}")
        observed.add(article)
        by_article[article] = record
        if record.get("source_class") != "secondary_scan_image_reproduction":
            errors.append(f"article {article}: wrong source class")
        if record.get("official_gazette_match") != "not_performed":
            errors.append(f"article {article}: official match must remain not_performed")
        if record.get("official_pdf_sha256") is not None:
            errors.append(f"article {article}: must not claim official PDF hash")
        if record.get("retrieval_eligible") is not False:
            errors.append(f"article {article}: must remain retrieval-ineligible")
        if record.get("status") != "candidate_only_pending_official_match":
            errors.append(f"article {article}: must remain pending official match")
        if not record.get("printed_gazette_pages") or not record.get("source_image_urls"):
            errors.append(f"article {article}: missing page/image locator")
        for url in record.get("source_image_urls", []):
            if not isinstance(url, str) or not url.startswith(BASE) or not url.endswith(".webp"):
                errors.append(f"article {article}: invalid image URL {url!r}")

    if observed != EXPECTED_ARTICLES:
        errors.append(f"article coverage mismatch: expected 1–11, got {sorted(observed)}")
    if 7 in by_article:
        periods = by_article[7].get("candidate_procedure_periods", {})
        if periods.get("initial_review_days") != 15 or periods.get("notice_of_result_business_days") != 3:
            errors.append("article 7 candidate procedure periods missing or changed")
        if periods.get("completion_of_missing_documents_days") != 30 or periods.get("decision_after_complete_application_days") != 30:
            errors.append("article 7 completion/decision periods missing or changed")
    if 8 in by_article:
        fees = by_article[8].get("candidate_fee_table_egp", {})
        if fees.get("consultant_A") != {"initial_license": 3000, "renewal": 2500}:
            errors.append("article 8 Consultant A candidate fees mismatch")
        if fees.get("consultant_B") != {"initial_license": 2500, "renewal": 2000}:
            errors.append("article 8 Consultant B candidate fees mismatch")
        if any(v > 50000 for tier in fees.values() if isinstance(tier, dict) for v in tier.values() if isinstance(v, int)):
            errors.append("candidate fee exceeds the parent-law Article 262 ceiling; investigate")
    if 9 in by_article and by_article[9].get("candidate_license_validity_years") != 3:
        errors.append("article 9 candidate licence validity missing or changed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    args = parser.parse_args()
    errors = validate(args.file)
    if errors:
        print("FAIL: Decision 251 candidate map invalid")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: Decision 251 Articles 1–11 and candidate fee/procedure fields are present and quarantined.")
    print("LIMIT: secondary scan reproductions only; no official match, currentness, counsel approval or retrieval eligibility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
