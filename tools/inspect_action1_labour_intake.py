#!/usr/bin/env python3
"""Create a metadata-only intake receipt for user-supplied Action 1 files.

This tool never extracts, modifies, uploads, or commits source contents. It records
SHA-256 and structural JSONL diagnostics so the original Gazette PDF and optional
law_rows_ar.jsonl can be compared reproducibly after they are supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def require_regular_file(path_value: str | Path, label: str) -> Path:
    path = Path(path_value).expanduser()
    if path.is_symlink():
        raise ValueError(f"{label} must not be a symbolic link")
    if not path.exists() or not path.is_file():
        raise ValueError(f"{label} must be an existing regular file")
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_pdf(path_value: str | Path) -> dict[str, Any]:
    path = require_regular_file(path_value, "Gazette PDF")
    size = path.stat().st_size
    with path.open("rb") as handle:
        header = handle.read(8)
        if size:
            handle.seek(max(0, size - 4096))
            tail = handle.read(4096)
        else:
            tail = b""
    signature_ok = header.startswith(b"%PDF-")
    if not signature_ok:
        raise ValueError("Gazette input does not begin with a PDF signature")
    return {
        "filename": path.name,
        "size_bytes": size,
        "sha256": sha256_file(path),
        "pdf_signature_valid": True,
        "eof_marker_seen_near_file_end": b"%%EOF" in tail,
    }


def inspect_jsonl(path_value: str | Path) -> dict[str, Any]:
    path = require_regular_file(path_value, "law_rows_ar.jsonl")
    field_counts: Counter[str] = Counter()
    rows = 0
    candidate_key_fields = ("row_id", "record_id", "id")
    key_values: dict[str, set[str]] = {key: set() for key in candidate_key_fields}
    key_counts: Counter[str] = Counter()

    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"law_rows_ar.jsonl line {line_number} is invalid JSON: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"law_rows_ar.jsonl line {line_number} must contain a JSON object"
                )
            rows += 1
            field_counts.update(record.keys())
            for key in candidate_key_fields:
                value = record.get(key)
                if value is not None and str(value).strip():
                    key_values[key].add(str(value))
                    key_counts[key] += 1

    stable_key_field = next(
        (
            key
            for key in candidate_key_fields
            if key_counts[key] == rows and rows > 0
        ),
        None,
    )
    duplicate_key_count = None
    if stable_key_field:
        # Re-read only to detect duplicates; no source content is emitted.
        seen: set[str] = set()
        duplicate_key_count = 0
        with path.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                value = str(record[stable_key_field])
                if value in seen:
                    duplicate_key_count += 1
                seen.add(value)

    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "jsonl_records": rows,
        "top_level_field_counts": dict(sorted(field_counts.items())),
        "stable_key_field_candidate": stable_key_field,
        "duplicate_stable_key_count": duplicate_key_count,
    }


def build_report(gazette_pdf: str | Path, law_rows_jsonl: str | Path | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "metadata_only_action1_intake_receipt",
        "gazette_pdf": inspect_pdf(gazette_pdf),
        "law_rows_jsonl": inspect_jsonl(law_rows_jsonl) if law_rows_jsonl else None,
        "safety_boundary": {
            "source_contents_embedded": False,
            "files_modified": False,
            "files_uploaded": False,
            "legal_authenticity_verified": False,
            "currentness_verified": False,
            "reuse_permission_confirmed": False,
            "retrieval_eligible": False,
        },
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gazette-pdf", required=True, help="Path to the original Official Gazette PDF supplied for Action 1")
    parser.add_argument("--law-rows-jsonl", help="Optional path to law_rows_ar.jsonl")
    args = parser.parse_args(argv)
    try:
        report = build_report(args.gazette_pdf, args.law_rows_jsonl)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Action 1 intake inspection failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
