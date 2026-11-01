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
from urllib.parse import urlparse

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


def load_catalog_documents(path: Path = CATALOG) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {d["document_id"]: d for d in data.get("documents", []) if isinstance(d, dict) and d.get("document_id")}


def validate_reference_url(url: str) -> str:
    """Light validation only: this URL is recorded, never fetched."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("source URL must be an absolute https:// URL")
    if parsed.username or parsed.password:
        raise ValueError("source URL must not contain credentials")
    if len(url) > 2048:
        raise ValueError("source URL is too long")
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

    catalog = load_catalog_documents()
    doc = catalog.get(args.document_id)
    if doc is None and not args.source_id:
        raise ValueError(f"document id {args.document_id!r} is not in docs/legal_document_candidates.json; "
                         "add it to the catalog first, or pass --source-id to record it anyway")
    source_id = args.source_id or doc["source_id"]

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

    original_dir.mkdir(parents=True, exist_ok=True)
    if not already:
        shutil.copyfile(path, original_path)
    meta_dir = out / "metadata"
    if meta_dir.is_symlink():
        raise ValueError("metadata directory must not be a symbolic link")
    meta_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = meta_dir / f"{args.document_id}.json"
    if metadata_path.is_symlink():
        raise ValueError("metadata file must not be a symbolic link")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    ap.add_argument("--source-id", help="only needed when the document id is not in the catalog")
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
