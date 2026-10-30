#!/usr/bin/env python3
"""Fail-closed metadata validator for official Law 14/2025 article excerpts.

This checks record structure and quarantine metadata only. It does not prove that
the browser-extracted text is byte-identical to the source PDF or that the law is
current, interpreted correctly, or approved for legal retrieval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "data" / "candidates" / "labour_law_14_2025" / "official_primary_text_articles11_12_13_255_259_260_261_262_2026-10-30.jsonl"
EXPECTED_URL = "https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf"
EXPECTED_ARTICLES = {11, 12, 13, 255, 259, 260, 261, 262}
EXPECTED_PAGES = {11: (3, 5), 12: (3, 5), 13: (3, 5), 255: (94, 96), 259: (96, 98), 260: (97, 99), 261: (97, 99), 262: (97, 99)}


def validate(path: Path = DEFAULT_FILE) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing official excerpt JSONL: {path}"]

    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"line {line_no}: record must be an object")
            continue
        records.append((line_no, record))

    observed: set[int] = set()
    for line_no, record in records:
        article = record.get("article")
        if not isinstance(article, int) or isinstance(article, bool):
            errors.append(f"line {line_no}: article must be an integer")
            continue
        if article in observed:
            errors.append(f"duplicate article excerpt: {article}")
        observed.add(article)
        if record.get("source_url") != EXPECTED_URL:
            errors.append(f"article {article}: unexpected or missing official PDF URL")
        if record.get("source_class") != "official_government_hosted_official_gazette_pdf":
            errors.append(f"article {article}: source must be classified as official government-hosted Gazette PDF")
        if record.get("gazette_issue") != "الجريدة الرسمية - العدد 18 (تابع)" or record.get("gazette_date") != "2025-05-03":
            errors.append(f"article {article}: Gazette issue/date mismatch")
        if EXPECTED_PAGES.get(article) != (record.get("pdf_page_index"), record.get("printed_page")):
            errors.append(f"article {article}: incorrect PDF/printed page locator")
        if not isinstance(record.get("source_text_ar"), str) or not record["source_text_ar"].strip():
            errors.append(f"article {article}: missing Arabic source text")
        if record.get("original_pdf_bytes_obtained") is not False:
            errors.append(f"article {article}: must not claim original PDF bytes were obtained")
        if record.get("original_pdf_sha256") is not None:
            errors.append(f"article {article}: must not invent a PDF SHA-256")
        if record.get("status") != "primary_source_observed_pending_byte_hash_and_counsel":
            errors.append(f"article {article}: excerpt must remain pending byte-hash/counsel review")
        if record.get("retrieval_eligible") is not False:
            errors.append(f"article {article}: must remain retrieval-ineligible")
        if record.get("currentness_review") != "not_started" or record.get("counsel_review") != "not_started":
            errors.append(f"article {article}: currentness/counsel review cannot be pre-approved")
        if record.get("source_use_status") != "provisional_official_document_exclusion_candidate_pending_counsel":
            errors.append(f"article {article}: source-use status must remain provisional pending counsel")

    if observed != EXPECTED_ARTICLES:
        errors.append(f"article coverage mismatch: expected {sorted(EXPECTED_ARTICLES)}, got {sorted(observed)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="Official article excerpt JSONL")
    args = parser.parse_args()
    errors = validate(args.file)
    if errors:
        print("FAIL: official Law 14/2025 excerpt metadata is invalid")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OK: Articles 11, 12, 13, 255, 259, 260, 261 and 262 have source/page metadata and remain quarantined.")
    print("LIMIT: no original PDF hash, currentness determination, counsel approval, or retrieval eligibility is claimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
