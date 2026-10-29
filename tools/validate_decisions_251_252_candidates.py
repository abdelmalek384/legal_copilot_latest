#!/usr/bin/env python3
"""Validate Decisions 251/252 numeric/eligibility assertions remain quarantined candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "candidates" / "labour_law_14_2025"
FILES = {
    "251": ("decision_251_numeric_and_eligibility_candidates_2026-10-29.json", 17, "251-A"),
    "252": ("decision_252_numeric_candidate_assertions_2026-10-29.json", 40, "252-N"),
}
FORBIDDEN_APPROVAL_STATUSES = {"approved", "verified", "authoritative", "retrieval_eligible"}


def _has_locator(item: dict[str, Any]) -> bool:
    if item.get("source_image") or item.get("source_url"):
        return True
    if isinstance(item.get("source_images"), list) and item["source_images"]:
        return True
    return bool(item.get("source_page") or item.get("source_pages") or item.get("printed_page"))


def validate_record(record: Any, decision: str, filename: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{filename}: root must be a JSON object"]
    expected_count, prefix = FILES[decision][1], FILES[decision][2]
    if record.get("official_pdf_downloaded_and_hashed") is not False:
        errors.append(f"{filename}: official PDF must remain not downloaded/hashed")
    if record.get("official_file_match") != "pending":
        errors.append(f"{filename}: official-file match must remain pending")
    if record.get("currentness") != "not_checked":
        errors.append(f"{filename}: currentness must remain not_checked")
    if record.get("counsel_review") != "not_reviewed":
        errors.append(f"{filename}: counsel review must remain not_reviewed")
    if record.get("authoritative_retrieval_eligible") is not False:
        errors.append(f"{filename}: authoritative retrieval eligibility must remain false")
    assertions = record.get("assertions")
    if not isinstance(assertions, list):
        return errors + [f"{filename}: assertions must be a list"]
    if len(assertions) != expected_count or record.get("count") != expected_count:
        errors.append(f"{filename}: expected {expected_count} assertions and matching count field")
    ids: list[str] = []
    for index, item in enumerate(assertions):
        if not isinstance(item, dict):
            errors.append(f"{filename}: assertion index {index} must be an object")
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"{filename}: assertion index {index} has no ID")
        else:
            ids.append(identifier)
        if not isinstance(item.get("topic"), str) or not item["topic"].strip():
            errors.append(f"{filename}: assertion {identifier!r} missing topic")
        if "value" not in item:
            errors.append(f"{filename}: assertion {identifier!r} missing candidate value")
        status = item.get("status")
        if not isinstance(status, str) or not status.strip():
            errors.append(f"{filename}: assertion {identifier!r} missing status")
        elif status.strip().lower() in FORBIDDEN_APPROVAL_STATUSES:
            errors.append(f"{filename}: assertion {identifier!r} has a forbidden approval status")
        if not _has_locator(item):
            errors.append(f"{filename}: assertion {identifier!r} lacks a source locator")
        for field in ("source_image", "source_url"):
            url = item.get(field)
            if url is not None and (not isinstance(url, str) or not url.startswith("https://")):
                errors.append(f"{filename}: assertion {identifier!r} has invalid {field}")
        for field in ("source_images",):
            urls = item.get(field)
            if urls is not None and (
                not isinstance(urls, list) or any(not isinstance(url, str) or not url.startswith("https://") for url in urls)
            ):
                errors.append(f"{filename}: assertion {identifier!r} has invalid {field}")
        if item.get("verified") is True or item.get("approved") is True or item.get("retrieval_eligible") is True:
            errors.append(f"{filename}: assertion {identifier!r} has a forbidden promotion flag")
    if len(ids) != len(set(ids)):
        errors.append(f"{filename}: duplicate assertion IDs")
    expected_ids = (
        [f"251-A{i:02d}" for i in range(1, 18)]
        if decision == "251"
        else [f"252-N{i:03d}" for i in range(1, 41)]
    )
    if ids != expected_ids:
        errors.append(f"{filename}: assertion IDs must be complete and ordered from {expected_ids[0]} to {expected_ids[-1]}")
    return errors


def validate(root: Path = DATA_DIR) -> list[str]:
    errors: list[str] = []
    for decision, (filename, _, _) in FILES.items():
        path = root / filename
        if not path.is_file():
            errors.append(f"missing candidate file: {filename}")
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{filename}: cannot parse JSON: {exc}")
            continue
        errors.extend(validate_record(record, decision, filename))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DATA_DIR, help="Directory containing Decisions 251/252 candidate JSON")
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        print("FAIL: Decisions 251/252 candidate assertions are incomplete or not safely quarantined")
        for error in errors:
            print("- " + error)
        return 1
    print("OK: 17 Decision 251 and 40 Decision 252 assertions are structurally complete and remain unapproved.")
    print("LIMIT: secondary candidate evidence only; official matching, currentness, source-use and counsel review remain required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
