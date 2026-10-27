#!/usr/bin/env python3
"""Validate provenance metadata for a manually acquired legal-source file.

This tool is local-only and read-only: it performs no network requests, database
writes, source extraction, legal verification, or retrieval release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit


PERMISSION_STATES = {
    "unknown", "permission_pending", "allowed", "allowed_limited", "prohibited",
    "not_allowed_without_explicit_exception_or_license",
}
COMMERCIAL_STATES = {
    "unknown", "allowed", "allowed_limited", "prohibited", "restricted",
    "not_allowed_without_explicit_exception_or_license",
    "prior_written_permission_required_per_published_terms",
}


def _https_url(value: object) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if any(ch.isspace() or ord(ch) < 32 for ch in value):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
        return (
            parsed.scheme.lower() == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not parsed.netloc.endswith(":")
            and (port is None or 1 <= port <= 65535)
        )
    except (ValueError, TypeError):
        return False


def _iso_date(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _iso_datetime_with_timezone(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except (ValueError, OverflowError):
        return False


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_capture_record(record: object, record_path: Path) -> dict:
    """Validate record structure and local original-file integrity without mutation."""
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return {
            "valid": False,
            "provenance_valid": False,
            "collection_ready": False,
            "commercial_product_use_ready": False,
            "retrieval_eligible": False,
            "errors": ["record must be a JSON object"],
            "warnings": [],
        }

    required = (
        "document_id", "official_title", "source_authority", "source_url",
        "retrieved_at", "acquisition_method", "original_file", "original_sha256",
        "collection_permission", "commercial_reuse_permission",
    )
    for field in required:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")

    for field in ("source_url", "terms_url", "collection_permission_evidence_url",
                  "commercial_reuse_evidence_url"):
        value = record.get(field)
        if value is not None and value != "" and not _https_url(value):
            errors.append(f"{field} must be a valid HTTPS URL without credentials or whitespace")
    if not _https_url(record.get("source_url")):
        if not any(error.startswith("source_url ") for error in errors):
            errors.append("source_url must be a valid HTTPS URL without credentials or whitespace")

    if not _iso_datetime_with_timezone(record.get("retrieved_at")):
        errors.append("retrieved_at must be an ISO-8601 datetime with an explicit timezone")
    for field in ("publication_date", "effective_date", "repeal_date", "terms_checked_on"):
        value = record.get(field)
        if value not in (None, "") and not _iso_date(value):
            errors.append(f"{field} must be an ISO date (YYYY-MM-DD) when supplied")

    collection = record.get("collection_permission")
    if not isinstance(collection, str) or collection not in PERMISSION_STATES:
        errors.append("collection_permission must be one of: " + ", ".join(sorted(PERMISSION_STATES)))
    commercial = record.get("commercial_reuse_permission")
    if not isinstance(commercial, str) or commercial not in COMMERCIAL_STATES:
        errors.append("commercial_reuse_permission must be one of: " + ", ".join(sorted(COMMERCIAL_STATES)))

    expected_hash = record.get("original_sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
        errors.append("original_sha256 must contain exactly 64 hexadecimal characters")

    original = record.get("original_file")
    actual_hash = None
    if isinstance(original, str) and original.strip():
        relative = Path(original)
        if relative.is_absolute() or any(part in {"..", ""} for part in relative.parts):
            errors.append("original_file must be a safe relative path inside the capture-record directory")
        else:
            base = record_path.resolve().parent
            candidate = base / relative
            # Refuse symlinks at every existing component; do not follow a caller-controlled link.
            current = base
            symlink_found = base.is_symlink()
            for part in relative.parts:
                current = current / part
                if current.is_symlink():
                    symlink_found = True
                    break
            if symlink_found:
                errors.append("original_file path must not traverse symbolic links")
            else:
                try:
                    resolved = candidate.resolve(strict=True)
                    resolved.relative_to(base)
                    if not resolved.is_file():
                        errors.append("original_file must resolve to a regular file")
                    elif resolved.stat().st_size == 0:
                        errors.append("original_file must not be empty")
                    else:
                        actual_hash = _sha256_file(resolved)
                        if isinstance(expected_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
                            if actual_hash.lower() != expected_hash.lower():
                                errors.append("original_sha256 does not match the original file bytes")
                except (OSError, ValueError):
                    errors.append("original_file is missing or resolves outside the capture-record directory")

    collection_evidence = _https_url(record.get("collection_permission_evidence_url"))
    commercial_evidence = _https_url(record.get("commercial_reuse_evidence_url"))
    terms_recorded = _https_url(record.get("terms_url")) and _iso_date(record.get("terms_checked_on"))
    collection_ready = collection == "allowed" and collection_evidence and terms_recorded
    commercial_ready = commercial == "allowed" and commercial_evidence and terms_recorded
    if not terms_recorded:
        warnings.append("source terms URL and checked date are not both recorded")
    if not collection_ready:
        warnings.append("collection permission is not supported by recorded terms and evidence")
    if not commercial_ready:
        warnings.append("commercial reuse permission is not supported by recorded terms and evidence")
    warnings.append("this tool never verifies legal authenticity, currentness, amendment history, or lawyer approval")
    warnings.append("retrieval eligibility must be decided by the separate source-to-release gate")

    provenance_valid = not errors and actual_hash is not None
    return {
        "valid": not errors,
        "provenance_valid": provenance_valid,
        "actual_sha256": actual_hash,
        "collection_ready": bool(collection_ready),
        "commercial_product_use_ready": bool(commercial_ready),
        "retrieval_eligible": False,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True, help="JSON sidecar record")
    args = parser.parse_args(argv)
    if args.record.is_symlink():
        print(json.dumps({"valid": False, "errors": ["capture record must not be a symbolic link"]}, ensure_ascii=False, indent=2))
        return 2
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [f"cannot read capture record: {exc}"]}, ensure_ascii=False, indent=2))
        return 2
    result = validate_capture_record(record, args.record)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
