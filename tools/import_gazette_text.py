#!/usr/bin/env python3
"""Import lawyer-supplied UTF-8 Gazette text into quarantined article-level candidate rows.

This is an offline transcription importer. It does not fetch sources, verify authenticity,
grant reuse permission, determine current force, or approve legal content.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from tools.import_laws import pieces, split

MAX_TEXT_BYTES = 20 * 1024 * 1024
MAX_METADATA_BYTES = 1024 * 1024
SENSITIVE_QUERY_KEYS = {
    "token", "access_token", "auth", "authorization", "password", "secret",
    "signature", "sig", "api_key", "apikey", "session", "sessionid",
    "credential", "api-key", "auth_token", "session_token",
    "x-amz-signature", "x-amz-credential", "x-amz-security-token",
    "x-goog-signature", "x-goog-credential",
}


def _read_regular(path: Path, label: str, limit: int) -> bytes:
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"{label} must be a regular file, not a symlink")
        if before.st_size > limit:
            raise ValueError(f"{label} exceeds {limit} bytes")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
                raise ValueError(f"{label} changed identity while opening")
            data = handle.read(limit + 1)
            after = os.fstat(handle.fileno())
            if len(data) > limit or len(data) != after.st_size:
                raise ValueError(f"{label} changed or exceeded its size limit while reading")
            if (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError(f"{label} changed while being read")
            return data
    except OSError as exc:
        raise ValueError(f"cannot safely read {label}: {type(exc).__name__}") from exc


def _validate_metadata(meta: object, text_bytes: bytes) -> dict:
    if not isinstance(meta, dict):
        raise ValueError("metadata sidecar must be a JSON object")
    for field in ("document_id", "official_title", "language", "gazette_issue",
                  "publication_date", "retrieved_at", "captured_by", "capture_method",
                  "content_sha256"):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise ValueError(f"{field} is required and must be a non-empty string")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", meta["document_id"]):
        raise ValueError("document_id contains unsupported characters")
    if meta["language"].strip().lower() != "ar":
        raise ValueError("language must be ar for the Arabic-first Gazette text importer")
    if meta.get("supplier_role") not in {"egyptian_lawyer", "qualified_egyptian_counsel"}:
        raise ValueError("supplier_role must identify an Egyptian lawyer or qualified counsel")
    if meta["capture_method"] not in {"lawyer_supplied_text", "manual_transcription"}:
        raise ValueError("capture_method must be lawyer_supplied_text or manual_transcription")
    try:
        publication = dt.date.fromisoformat(meta["publication_date"])
        if publication.isoformat() != meta["publication_date"]:
            raise ValueError
    except ValueError as exc:
        raise ValueError("publication_date must be YYYY-MM-DD") from exc
    try:
        dt.datetime.fromisoformat(meta["retrieved_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        try:
            dt.date.fromisoformat(meta["retrieved_at"])
        except ValueError:
            raise ValueError("retrieved_at must be an ISO date or datetime") from exc
    expected = meta["content_sha256"].lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("content_sha256 must be a 64-character SHA-256")
    actual = hashlib.sha256(text_bytes).hexdigest()
    if actual != expected:
        raise ValueError("SHA-256 mismatch for supplied Gazette text")
    source_url = meta.get("source_url")
    if source_url:
        try:
            parsed = urlsplit(source_url)
            _ = parsed.port
        except (TypeError, ValueError) as exc:
            raise ValueError("source_url must be a valid HTTPS URL") from exc
        if (parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username
                or parsed.password or parsed.fragment):
            raise ValueError("source_url must be HTTPS without credentials or fragments")
        query_keys = {key.casefold() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
        if query_keys & SENSITIVE_QUERY_KEYS:
            raise ValueError("source_url must not contain signed or credential query parameters")
    elif not (isinstance(meta.get("source_reference"), str) and meta["source_reference"].strip()):
        raise ValueError("provide source_url or a non-empty source_reference")
    permission = meta.get("collection_permission", "unknown")
    if permission not in {"unknown", "allowed", "not_allowed"}:
        raise ValueError("collection_permission must be unknown, allowed, or not_allowed")
    if permission == "not_allowed":
        raise ValueError("collection permission is marked not_allowed; refusing to create candidate rows")
    return {**meta, "publication_date": publication.isoformat(), "actual_sha256": actual}


def import_text(text_path: Path, metadata_path: Path, output_dir: Path) -> dict:
    text_path, metadata_path, output_dir = Path(text_path), Path(metadata_path), Path(output_dir)
    if text_path.resolve() == metadata_path.resolve():
        raise ValueError("text and metadata paths must be different")
    if output_dir.is_symlink():
        raise ValueError("output directory must not be a symlink")
    source_parent = text_path.resolve().parent
    output_resolved = output_dir.resolve()
    if output_resolved == source_parent or source_parent in output_resolved.parents:
        raise ValueError("output directory must be outside the source directory")
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError("output path must be a directory")
    if output_dir.exists() and any((output_dir / name).exists() or (output_dir / name).is_symlink()
                                   for name in ("law_rows.jsonl", "import_report.md")):
        raise ValueError("output files already exist; use a new empty output directory")
    text_bytes = _read_regular(text_path, "Gazette text", MAX_TEXT_BYTES)
    meta_bytes = _read_regular(metadata_path, "metadata sidecar", MAX_METADATA_BYTES)
    try:
        text = text_bytes.decode("utf-8-sig")
        meta = json.loads(meta_bytes.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("text must be UTF-8 and metadata must be valid UTF-8 JSON") from exc
    if "\x00" in text:
        raise ValueError("Gazette text contains NUL characters")
    metadata = _validate_metadata(meta, text_bytes)
    article_parts = split(text)
    articles = [part for part in article_parts if part[0] != "preamble"]
    if not articles:
        raise ValueError("no recognized Arabic/English article headings were found")
    rows = []
    block_articles = {}
    empty_articles = []
    title = metadata["official_title"].strip()
    source = (
        f"{metadata.get('source_url') or metadata.get('source_reference')} | "
        f"{metadata['gazette_issue']} | published {metadata['publication_date']} | "
        f"retrieved {metadata['retrieved_at']} | sha256 {metadata['actual_sha256']} | "
        f"supplied by {metadata['captured_by']}"
    )
    for article, block, body in article_parts:
        label = title + ("" if block <= 1 else f" [block {block}]")
        chunks = list(pieces(body))
        if not chunks and article != "preamble":
            empty_articles.append(article)
        for chunk in chunks:
            rows.append({
                "law": label,
                "article": article,
                "text": chunk,
                "as_of": None,
                "in_force": 0,
                "verified": 0,
                "source": source,
                "document_id": metadata["document_id"],
                "gazette_issue": metadata["gazette_issue"],
                "publication_date": metadata["publication_date"],
                "content_sha256": metadata["actual_sha256"],
                "captured_by": metadata["captured_by"],
                "collection_permission": metadata.get("collection_permission", "unknown"),
            })
        block_articles.setdefault(block, []).append(article)
    if not rows:
        raise ValueError("recognized headings contained no importable text")
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
    report = [
        "# Gazette text import report", "",
        "**Status:** candidate transcription only; not verified, authoritative, current, or retrieval-eligible.", "",
        f"- Document: {title}",
        f"- Gazette issue: {metadata['gazette_issue']}",
        f"- Publication date: {metadata['publication_date']}",
        f"- Source reference: {metadata.get('source_url') or metadata.get('source_reference')}",
        f"- Supplied by: {metadata['captured_by']} ({metadata.get('supplier_role', 'role not recorded')})",
        f"- Exact text SHA-256: {metadata['actual_sha256']}",
        f"- Article headings recognized: {len(articles)}",
        f"- Output candidate chunks: {len(rows)}",
        f"- Empty article bodies requiring review: {len(empty_articles)}",
        f"- Collection permission: {metadata.get('collection_permission', 'unknown')}",
        "- Every row is emitted with verified=0, in_force=0, and as_of=null.",
        "- No legal currentness, source authenticity, or reuse rights are inferred.", "",
        "| numbering block | first label | last label | headings |",
        "|---|---|---|---:|",
    ]
    numbering_gaps = {}
    duplicate_numbers = {}
    for block, labels in sorted(block_articles.items()):
        numeric = []
        for label in labels:
            match = re.match(r"^\s*([0-9٠-٩]+)", str(label))
            if match:
                try:
                    numeric.append(int(match.group(1)))
                except ValueError:
                    pass
        missing = sorted(set(range(1, max(numeric, default=0) + 1)) - set(numeric))
        duplicates = sorted({number for number in numeric if numeric.count(number) > 1})
        if missing:
            numbering_gaps[str(block)] = missing
        if duplicates:
            duplicate_numbers[str(block)] = duplicates
        report.append(f"| {block} | {labels[0]} | {labels[-1]} | {len(labels)} |")
    report += ["", "## Numbering audit", "",
               f"- Blocks with missing article numbers: {len(numbering_gaps)}",
               f"- Blocks with duplicate article numbers: {len(duplicate_numbers)}"]
    for block, missing in numbering_gaps.items():
        report.append(f"- Block {block} missing: {', '.join(map(str, missing))}")
    for block, duplicates in duplicate_numbers.items():
        report.append(f"- Block {block} duplicates: {', '.join(map(str, duplicates))}")
    if empty_articles:
        report += ["", "## Empty article bodies", "", ", ".join(empty_articles)]
    report += ["", "## Human review", "",
               "- Compare each candidate article against the supplied Gazette image/text.",
               "- Resolve missing pages, numbering resets, schedules, tables, and OCR/transcription ambiguities.",
               "- Obtain separate source-rights, currentness, amendment/corrigendum, and Egyptian-lawyer review.",
               "- Do not change verification flags in this importer."]
    (output_dir / "law_rows.jsonl").write_text(jsonl, encoding="utf-8")
    (output_dir / "import_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"document_id": metadata["document_id"], "article_headings": len(articles),
            "candidate_chunks": len(rows), "empty_articles": empty_articles,
            "sha256": metadata["actual_sha256"], "output_dir": str(output_dir)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text_file", type=Path)
    parser.add_argument("metadata_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    try:
        result = import_text(args.text_file, args.metadata_json, args.output_dir)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
