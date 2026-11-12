#!/usr/bin/env python3
"""Record a legal document that a person saved BY HAND from a source, with full provenance.

Use this when automated collection is not allowed or not possible: a person opens the
official source in a browser, saves the file, and then records it here. The tool never
contacts the network.

IMPORTANT: recording a capture is evidence of what was saved, from where, when and by whom.
It is NOT permission to store, index, embed, display or commercially reuse the content, and
it does not verify authenticity or current legal status.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.collect_legal_documents import (  # noqa: E402
    ALLOWED_TYPES,
    append_jsonl,
    process_document,
    sha256_bytes,
    validate_output_layout,
)

CATALOG = ROOT / "docs" / "legal_document_candidates.json"
CAPTURE_METHODS = {"browser_download", "browser_save_page", "print_to_pdf", "manual_transcription", "official_copy_by_request"}
DEFAULT_MAX_MB = 100
SIGNATURES = {
    "application/pdf": lambda b: b.startswith(b"%PDF-"),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": lambda b: b.startswith(b"PK\x03\x04"),
}
EXT_TO_TYPE = {
    ".pdf": "application/pdf",
    ".html": "text/html",
    ".htm": "text/html",
    ".txt": "text/plain",
    ".md": "text/plain",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_catalog(path: Path = CATALOG) -> tuple[dict, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("document catalog must be a JSON object")

    def index_rows(field: str, id_field: str) -> dict:
        rows = data.get(field, [])
        if not isinstance(rows, list):
            raise ValueError(f"document catalog {field} must be a list")
        indexed = {}
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                raise ValueError(f"document catalog {field} row {index} must be an object")
            identifier = row.get(id_field)
            if not isinstance(identifier, str) or not identifier.strip():
                raise ValueError(f"document catalog {field} row {index} needs a non-empty {id_field}")
            if identifier in indexed:
                raise ValueError(f"document catalog contains duplicate {id_field}: {identifier}")
            indexed[identifier] = row
        return indexed

    return index_rows("documents", "document_id"), index_rows("sources", "source_id")


def validate_reference_url(url: str) -> str:
    """Validate a public HTTPS reference URL; this tool records it but never fetches it."""
    if not isinstance(url, str) or not url:
        raise ValueError("source URL must be an absolute https:// URL")
    if len(url) > 2048:
        raise ValueError("source URL is too long")
    if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in url):
        raise ValueError("source URL must not contain whitespace or control characters")
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except (TypeError, ValueError) as exc:
        raise ValueError("source URL must have a valid HTTPS authority and port") from exc
    if (parsed.scheme.lower() != "https" or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.fragment or parsed.netloc.endswith(":")
            or (port is not None and not 1 <= port <= 65535)):
        raise ValueError("source URL must be HTTPS without credentials or fragments and with a valid authority")
    sensitive_query_keys = {
        "token", "access_token", "auth", "authorization", "password", "secret",
        "signature", "sig", "api_key", "apikey", "session", "sessionid",
        "credential", "api-key", "auth_token", "session_token",
        "x-amz-signature", "x-amz-credential", "x-amz-security-token",
        "x-goog-signature", "x-goog-credential",
    }
    query_keys = {key.casefold() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & sensitive_query_keys:
        raise ValueError("source URL must not contain signed or credential query parameters")
    return parsed.hostname.lower().rstrip(".")


def detect_content_type(path: Path, data: bytes) -> str:
    ctype = EXT_TO_TYPE.get(path.suffix.lower())
    if ctype is None:
        raise ValueError(f"unsupported file extension {path.suffix!r}; use PDF, HTML, TXT or DOCX")
    check = SIGNATURES.get(ctype)
    if check and not check(data):
        raise ValueError(f"file does not look like a real {ctype} document (signature mismatch)")
    if ctype == "text/html":
        sample = data[:4096].lstrip().lower()
        if not (b"<html" in sample or b"<!doctype html" in sample or b"<body" in sample):
            raise ValueError("HTML file has no recognizable HTML document structure")
    if ctype == "text/plain":
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("text file must be UTF-8 encoded") from exc
    return ctype


def record_capture(args) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", args.document_id):
        raise ValueError("--document-id must start with a letter/digit and contain only letters, digits, '_' or '-' (max 128 characters)")
    path = Path(args.file).expanduser()
    if not path.is_file():
        raise ValueError(f"file not found: {path}")
    size = path.stat().st_size
    if size == 0:
        raise ValueError("file is empty")
    if size > args.max_mb * 1024 * 1024:
        raise ValueError(f"file exceeds {args.max_mb} MB")
    data = path.read_bytes()
    content_type = detect_content_type(path, data)
    host = validate_reference_url(args.source_url)
    if not args.captured_by.strip():
        raise ValueError("--captured-by must name the person who saved the file")
    for label, value in (("--retrieved-on", args.retrieved_on), ("--publication-date", args.publication_date),
                         ("--effective-date", args.effective_date)):
        if value and not DATE_RE.match(value):
            raise ValueError(f"{label} must be YYYY-MM-DD")
    try:
        retrieved = dt.date.fromisoformat(args.retrieved_on)
    except ValueError as exc:
        raise ValueError("--retrieved-on is not a valid date") from exc
    if retrieved > dt.date.today():
        raise ValueError("--retrieved-on cannot be in the future")

    documents, sources = load_catalog()
    doc = documents.get(args.document_id)
    if doc is None and not args.source_id:
        raise ValueError(f"document id {args.document_id!r} is not in docs/legal_document_candidates.json; "
                         "add it to the catalog first, or pass a registered --source-id")
    source_id = args.source_id or (doc or {}).get("source_id")
    source = sources.get(source_id)
    if source is None:
        raise ValueError(f"source id {source_id!r} is not registered in docs/legal_document_candidates.json")
    registered_host = validate_reference_url(source.get("source_page", ""))
    if host != registered_host:
        raise ValueError(f"source URL host {host!r} does not match registered source {source_id!r} host {registered_host!r}; "
                         "select the correct registered --source-id")

    sha = sha256_bytes(data)
    ext = ALLOWED_TYPES.get(content_type) or path.suffix.lower()
    out = Path(args.out)
    validate_output_layout(out)
    original_dir = out / "originals" / args.document_id
    if original_dir.is_symlink():
        raise ValueError("original document directory must not be a symbolic link")
    original_path = original_dir / f"original-manual-{sha[:16]}{ext}"
    if original_path.is_symlink():
        raise ValueError("original capture target must not be a symbolic link")
    already = original_path.exists()
    metadata = {
        "document_id": args.document_id,
        "source_id": source_id,
        "title": (doc or {}).get("official_title", args.document_id),
        "document_type": (doc or {}).get("document_type", "legislation"),
        "jurisdiction": "Egypt",
        "collection_mode": "manual_capture",
        "source_url": args.source_url,
        "source_host": host,
        "retrieved_on": args.retrieved_on,
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "captured_by": args.captured_by.strip(),
        "capture_method": args.capture_method,
        "capture_notes": args.notes or None,
        "http_content_type": content_type,
        "original_path": str(original_path.relative_to(out)),
        "original_filename": original_path.name,
        "original_supplied_filename": path.name,
        "original_size_bytes": len(data),
        "sha256": sha,
        "publication_date": args.publication_date,
        "effective_date": args.effective_date,
        "gazette_issue": args.gazette_issue,
        "law_number": (doc or {}).get("law_number"),
        "legal_status_assessment": "unknown",
        "permission_evidence": None,
        "collection_permission": "not_established_manual_capture",
        "legal_authenticity_verified": False,
        "current_legal_status_verified": False,
        "commercial_reuse_permission_verified": False,
        "review_status": "pending_human_review",
        "permission_note": ("Manual capture is evidence of what was saved, from where, when and by whom. "
                            "It is not permission to store, index, display or commercially reuse the content."),
    }
    if args.dry_run:
        return {"dry_run": True, "would_write": str(original_path), "metadata": metadata}

    meta_dir = out / "metadata"
    if meta_dir.is_symlink():
        raise ValueError("metadata directory must not be a symbolic link")
    meta_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = meta_dir / f"{args.document_id}.json"
    if metadata_path.is_symlink():
        raise ValueError("metadata file must not be a symbolic link")
    metadata_exists = metadata_path.exists()
    if metadata_exists:
        if not metadata_path.is_file():
            raise ValueError("existing metadata path must be a regular file")
        try:
            existing_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("existing metadata sidecar is unreadable; refusing to overwrite it") from exc
        if not isinstance(existing_metadata, dict):
            raise ValueError("existing metadata sidecar must be a JSON object; refusing to overwrite it")
        identity_fields = ("document_id", "source_id", "source_url", "original_path", "sha256", "http_content_type")
        if any(existing_metadata.get(field) != metadata.get(field) for field in identity_fields):
            raise ValueError("existing metadata sidecar belongs to a different capture; refusing to overwrite it")
        # Preserve reviewer annotations and any other existing provenance fields on reruns.
        metadata = existing_metadata

    original_dir.mkdir(parents=True, exist_ok=True)
    if not already:
        shutil.copyfile(path, original_path)
    if not metadata_exists:
        try:
            with metadata_path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
        except FileExistsError as exc:
            raise ValueError("metadata sidecar appeared during capture; refusing to overwrite it") from exc
    audit = process_document(out, metadata)
    reasons = list(audit["audit"]["warnings"])
    if audit["extraction_error"]:
        reasons.append(audit["extraction_error"])
    reasons.append("Manual capture: storage, indexing and commercial-reuse permission are separate and not established.")
    reasons.append("Compare against the official Gazette text and obtain lawyer review before any approval.")
    append_jsonl(out / "review_queue.jsonl", {
        "document_id": args.document_id,
        "source_id": source_id,
        "source_url": args.source_url,
        "original_sha256": sha,
        "collection_mode": "manual_capture",
        "captured_by": metadata["captured_by"],
        "retrieved_on": args.retrieved_on,
        "review_status": "pending_human_review",
        "legal_authenticity_verified": False,
        "current_legal_status_verified": False,
        "commercial_reuse_permission_verified": False,
        "review_reasons": reasons,
    })
    append_jsonl(out / "collection_report.jsonl", {
        "document_id": args.document_id,
        "status": "manual_capture_recorded" if not audit["extraction_error"] else "manual_capture_extraction_needs_attention",
        "sha256": sha,
        "article_headings_detected": audit["audit"]["article_headings_detected"],
        "numeric_article_gaps": audit["audit"]["numeric_article_gaps"],
        "warnings": audit["audit"]["warnings"],
        "extraction_error": audit["extraction_error"],
    })
    return {"dry_run": False, "original": str(original_path), "sha256": sha, "audit": audit["audit"],
            "extraction_error": audit["extraction_error"], "already_recorded_file": already}


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", required=True, help="the file you saved by hand (PDF, HTML, TXT or DOCX)")
    ap.add_argument("--document-id", required=True, help="catalog document id, for example EG-LABOUR-14-2025")
    ap.add_argument("--source-url", required=True, help="the exact https page or file URL you saved it from (recorded, never fetched)")
    ap.add_argument("--captured-by", required=True, help="name of the person who saved the file")
    ap.add_argument("--capture-method", choices=sorted(CAPTURE_METHODS), default="browser_download")
    ap.add_argument("--retrieved-on", default=dt.date.today().isoformat(), help="date you saved it (YYYY-MM-DD)")
    ap.add_argument("--publication-date", help="publication date shown by the source (YYYY-MM-DD), if known")
    ap.add_argument("--effective-date", help="effective date shown by the source (YYYY-MM-DD); unverified until reviewed")
    ap.add_argument("--gazette-issue", help="Official Gazette issue as printed, for example '18 (تابع)'")
    ap.add_argument("--source-id", help="registered source id for this capture; must match the source URL host (defaults to the document catalog source)")
    ap.add_argument("--notes", help="free-text notes about how the file was obtained")
    ap.add_argument("--out", default="legal_corpus", help="corpus folder (same layout as the collector)")
    ap.add_argument("--max-mb", type=int, default=DEFAULT_MAX_MB)
    ap.add_argument("--dry-run", action="store_true", help="validate and show the record without writing anything")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = record_capture(args)
    except ValueError as exc:
        print(f"Cannot record capture: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    if not result["dry_run"]:
        print("\nRecorded as pending human review. Nothing is marked authentic, current, permitted for reuse, or verified.")
        print(f"Next: compare with the official text (tools/compare_corpus_to_reference.py), then lawyer review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
