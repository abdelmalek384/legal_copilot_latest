#!/usr/bin/env python3
"""Create a metadata-only intake manifest for user-supplied Action 1 files.

The script never copies, uploads, extracts, or prints source contents. It records
only each input's basename, byte length, SHA-256, basic format check, and (for
JSONL) line/JSON validity counts. Keep original files in the user's controlled
workspace and do not commit them to the public repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def inspect_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    digest = hashlib.sha256()
    size = 0
    prefix = b""
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            if not prefix:
                prefix = chunk[:8]
            digest.update(chunk)
            size += len(chunk)

    result: dict[str, Any] = {
        "filename": path.name,
        "size_bytes": size,
        "sha256": digest.hexdigest(),
    }
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        result.update({
            "kind": "pdf",
            "pdf_signature_valid": prefix.startswith(b"%PDF-"),
            "content_extracted": False,
        })
    elif suffix in {".jsonl", ".ndjson"}:
        total = valid = malformed = blank = 0
        with path.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    blank += 1
                    continue
                total += 1
                try:
                    json.loads(line)
                    valid += 1
                except json.JSONDecodeError:
                    malformed += 1
        result.update({
            "kind": "jsonl",
            "nonblank_records": total,
            "valid_json_records": valid,
            "malformed_json_records": malformed,
            "blank_lines": blank,
            "content_extracted": False,
        })
    else:
        result.update({"kind": "other", "content_extracted": False})
    return result


def build_manifest(inputs: list[Path]) -> dict[str, Any]:
    if not inputs:
        raise ValueError("At least one input file is required")
    records = [inspect_file(path) for path in inputs]
    names = [record["filename"] for record in records]
    if len(names) != len(set(names)):
        raise ValueError("Input filenames must be unique in the manifest")
    return {
        "manifest_version": 1,
        "purpose": "Action 1 user-supplied source intake",
        "source_bytes_copied": False,
        "source_contents_extracted": False,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Path for metadata-only JSON manifest")
    parser.add_argument("inputs", nargs="+", type=Path, help="Original user-supplied source files")
    args = parser.parse_args()

    manifest = build_manifest(args.inputs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote metadata-only manifest for {len(manifest['records'])} file(s): {args.output}")
    for record in manifest["records"]:
        print(f"{record['filename']}: {record['size_bytes']} bytes; SHA-256 {record['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
