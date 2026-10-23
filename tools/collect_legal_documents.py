#!/usr/bin/env python3
"""Lawful, provenance-preserving Egyptian legal document collection pipeline.

This tool downloads only explicitly listed direct-document URLs whose manifest entry
records permission as "allowed", a permission evidence reference, and a terms-check
date. It never crawls a website, guesses document URLs, bypasses login, or treats
downloaded material as legally verified/current.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import ipaddress
import json
import mimetypes
import os
import re
import socket
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

MAX_BYTES_DEFAULT = 40 * 1024 * 1024
ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "text/plain": ".txt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
ARTICLE_RE = re.compile(
    r"(?im)^\s*(?:المادة|مادة)\s*\(?\s*([0-9٠-٩۰-۹]+)"
    r"(?:\s*(مكرر(?:ة)?|مكررا|bis))?\s*\)?\s*[:：\-]?\s*$"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class VisibleHTML(HTMLParser):
    SKIP = {"script", "style", "nav", "footer", "noscript", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
        if tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "section"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip_depth = max(0, self.skip_depth - 1)
        if tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "section"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)

    def text(self):
        return re.sub(r"[ \t\u00a0]+", " ", "".join(self.parts)).strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_date(value: str, field: str) -> dt.date:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        raise ValueError(f"{field} must be an ISO date YYYY-MM-DD")
    return dt.date.fromisoformat(value)


def validate_public_https_url(url: str, allowed_hosts: set[str]) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Only absolute HTTPS URLs are allowed")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed")
    host = parsed.hostname.lower().rstrip(".")
    if not any(host == h or host.endswith("." + h) for h in allowed_hosts):
        raise ValueError(f"Host {host!r} is not in the source's allowed_hosts")
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            raise ValueError("Non-public IP URLs are not allowed")
    except ValueError as exc:
        if "not allowed" in str(exc):
            raise
        # A non-IP hostname is expected. Resolve and reject private/local targets.
        try:
            answers = socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
        except OSError:
            raise ValueError(f"Cannot resolve source host {host!r}")
        for answer in answers:
            address = ipaddress.ip_address(answer[4][0])
            if not address.is_global:
                raise ValueError(f"Source host resolves to non-public address {address}")
    return host


def load_manifest(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    docs = data.get("documents")
    if not isinstance(docs, list):
        raise ValueError("Manifest must contain a 'documents' list")
    if any(not isinstance(doc, dict) for doc in docs):
        raise ValueError("Every document entry must be a JSON object")
    ids = [d.get("document_id") for d in docs]
    # IDs become directory and filename components; restrict them to a safe alphabet.
    if any(not isinstance(i, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", i) for i in ids):
        raise ValueError("document_id must start with a letter/digit and contain only letters, digits, '_' or '-' (max 128 characters)")
    if len(ids) != len(set(ids)):
        raise ValueError("document_id values must be unique")
    for index, doc in enumerate(docs, start=1):
        if not isinstance(doc.get("source_id"), str) or not doc["source_id"].strip():
            raise ValueError(f"Document entry #{index} needs a non-empty source_id")
    return docs


def check_permission(doc: dict) -> set[str]:
    if doc.get("collection_permission") != "allowed":
        raise ValueError("collection_permission must be explicitly set to 'allowed'")
    evidence = doc.get("permission_evidence")
    if not isinstance(evidence, str) or len(evidence.strip()) < 8:
        raise ValueError("permission_evidence must identify reviewed terms or written permission")
    parse_date(doc.get("terms_checked_on"), "terms_checked_on")
    hosts = doc.get("allowed_hosts")
    if not isinstance(hosts, list) or not hosts:
        raise ValueError("allowed_hosts must explicitly list the approved source host(s)")
    return {str(h).lower().rstrip(".") for h in hosts}


def download_document(client: httpx.Client, doc: dict, out: Path, max_bytes: int) -> dict:
    hosts = check_permission(doc)
    url = doc.get("direct_url", "")
    current = url
    raw = bytearray()
    content_type = ""
    final_url = ""
    response_headers = {}
    for _ in range(6):
        validate_public_https_url(current, hosts)
        # Stream instead of response.content: enforce the byte limit while reading,
        # so a server cannot force an unbounded body into memory before the check.
        with client.stream("GET", current, follow_redirects=False) as response:
            if response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("location")
                if not location:
                    raise ValueError("Redirect response has no Location header")
                current = urljoin(current, location)
                continue
            response.raise_for_status()
            final_url = str(response.url)
            final_host = validate_public_https_url(final_url, hosts)
            content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            response_headers = dict(response.headers)
            content_length = response.headers.get("content-length")
            if content_length:
                try:
                    declared_size = int(content_length)
                except ValueError:
                    raise ValueError("Invalid Content-Length header")
                if declared_size < 0 or declared_size > max_bytes:
                    raise ValueError(f"File exceeds maximum size of {max_bytes} bytes")
            for chunk in response.iter_bytes():
                if len(raw) + len(chunk) > max_bytes:
                    raise ValueError(f"File exceeds maximum size of {max_bytes} bytes")
                raw.extend(chunk)
        break
    else:
        raise ValueError("Too many redirects")
    raw = bytes(raw)
    if not raw:
        raise ValueError("Downloaded file is empty")
    if content_type not in ALLOWED_TYPES:
        # Some servers label PDFs as octet-stream; only accept when signature confirms PDF.
        if content_type != "application/octet-stream" or not raw.startswith(b"%PDF-"):
            raise ValueError(f"Unsupported content type: {content_type or '(missing)'}")
        content_type = "application/pdf"
    if content_type == "application/pdf" and not raw.startswith(b"%PDF-"):
        raise ValueError("PDF content type but file signature is not PDF")
    if content_type in {"text/html", "application/xhtml+xml"}:
        sample = raw[:4096].lstrip().lower()
        if not (b"<html" in sample or b"<!doctype html" in sample or b"<body" in sample):
            raise ValueError("HTML content type but no recognizable HTML document")
    ext = ALLOWED_TYPES[content_type]
    doc_id = doc["document_id"]
    original_dir = out / "originals" / doc_id
    original_dir.mkdir(parents=True, exist_ok=True)
    original_path = original_dir / ("original" + ext)
    if original_path.exists():
        existing_hash = sha256_bytes(original_path.read_bytes())
        new_hash = sha256_bytes(raw)
        if existing_hash != new_hash:
            version = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            original_path = original_dir / f"original-{version}{ext}"
    original_path.write_bytes(raw)
    retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
    metadata = {
        "document_id": doc_id,
        "source_id": doc["source_id"],
        "title": doc.get("title", doc_id),
        "document_type": doc.get("document_type", "legislation"),
        "jurisdiction": "Egypt",
        "source_url": final_url,
        "requested_url": url,
        "retrieved_at": retrieved_at,
        "http_content_type": content_type,
        "http_last_modified": response_headers.get("last-modified"),
        "http_etag": response_headers.get("etag"),
        "original_path": str(original_path.relative_to(out)),
        "original_filename": original_path.name,
        "original_size_bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "publication_date": doc.get("publication_date"),
        "effective_date": doc.get("effective_date"),
        "repeal_date": doc.get("repeal_date"),
        "legal_status_assessment": doc.get("legal_status_assessment", "unknown"),
        "amends_document_ids": doc.get("amends_document_ids", []),
        "amended_by_document_ids": doc.get("amended_by_document_ids", []),
        "consolidates_document_ids": doc.get("consolidates_document_ids", []),
        "consolidated_version_as_of": doc.get("consolidated_version_as_of"),
        "law_number": doc.get("law_number"),
        "gazette_issue": doc.get("gazette_issue"),
        "permission_evidence": doc["permission_evidence"],
        "terms_checked_on": doc["terms_checked_on"],
        "collection_permission": "allowed",
        "legal_authenticity_verified": False,
        "current_legal_status_verified": False,
        "commercial_reuse_permission_verified": False,
        "review_status": "pending_human_review",
        "download_host": final_host,
    }
    meta_dir = out / "metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / f"{doc_id}.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def extract_text(original_path: Path, content_type: str) -> tuple[str, str | None]:
    if content_type == "application/pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(original_path))
            pages = [(p.extract_text() or "") for p in reader.pages]
            text = "\n\n".join(f"[PAGE {i + 1}]\n{p}" for i, p in enumerate(pages))
            if not text.strip():
                return "", "PDF has no extractable text; OCR/manual transcription required"
            return text, None
        except Exception as exc:
            return "", f"PDF extraction failed: {type(exc).__name__}: {exc}"
    if content_type in {"text/html", "application/xhtml+xml"}:
        parser = VisibleHTML()
        parser.feed(original_path.read_text(encoding="utf-8", errors="replace"))
        return parser.text(), None
    if content_type == "text/plain":
        return original_path.read_text(encoding="utf-8", errors="replace"), None
    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            from docx import Document
            d = Document(str(original_path))
            return "\n".join(p.text for p in d.paragraphs), None
        except Exception as exc:
            return "", f"DOCX extraction failed: {type(exc).__name__}: {exc}"
    return "", f"No extractor for content type {content_type}"


def article_audit(text: str) -> dict:
    normalized = text.translate(ARABIC_DIGITS)
    matches = list(ARTICLE_RE.finditer(normalized))
    articles = []
    for match in matches:
        suffix = (match.group(2) or "").strip()
        key = match.group(1) + (f" {suffix}" if suffix else "")
        articles.append(key)
    numeric = []
    for key in articles:
        first = key.split()[0]
        if first.isdigit():
            numeric.append(int(first))
    duplicates = sorted({x for x in articles if articles.count(x) > 1})
    gaps = []
    if numeric:
        seen = set(numeric)
        gaps = sorted(set(range(min(seen), max(seen) + 1)) - seen)
    warnings = []
    if not articles:
        warnings.append("No article headings detected; document may be a scan, a different format, or use an unrecognized heading style.")
    if duplicates:
        warnings.append("Repeated article labels detected; check duplicate extraction or legitimate inserted/numbered provisions.")
    if gaps:
        warnings.append("Numbering gaps detected; check against the original. Gaps may be legitimate or caused by split/extraction errors.")
    if len(text.strip()) < 300:
        warnings.append("Extracted text is very short; check for a failed text layer or an incomplete download.")
    return {
        "article_headings_detected": len(articles),
        "article_labels": articles,
        "duplicate_article_labels": duplicates,
        "numeric_article_gaps": gaps,
        "character_count": len(text),
        "warnings": warnings,
    }


def process_document(out: Path, metadata: dict) -> dict:
    original = out / metadata["original_path"]
    text, error = extract_text(original, metadata["http_content_type"])
    doc_id = metadata["document_id"]
    extracted_dir = out / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    text_path = extracted_dir / f"{doc_id}.txt"
    text_path.write_text(text, encoding="utf-8")
    audit = article_audit(text)
    audit_record = {
        "document_id": doc_id,
        "source_id": metadata["source_id"],
        "original_sha256": metadata["sha256"],
        "extracted_text_path": str(text_path.relative_to(out)),
        "extracted_text_sha256": sha256_bytes(text.encode("utf-8")),
        "extraction_error": error,
        "audit": audit,
        "review_status": "pending_human_review",
        "legal_authenticity_verified": False,
        "current_legal_status_verified": False,
    }
    audit_dir = out / "audits"
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / f"{doc_id}.json").write_text(json.dumps(audit_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return audit_record


def append_jsonl(path: Path, record: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("docs/collection_manifest.example.json"))
    parser.add_argument("--out", type=Path, default=Path("legal_corpus"))
    parser.add_argument("--max-mb", type=int, default=40)
    parser.add_argument("--delay", type=float, default=2.0, help="Minimum pause between requests (seconds)")
    parser.add_argument("--process-existing", action="store_true", help="Re-run extraction/audits for already downloaded files")
    args = parser.parse_args()
    if args.max_mb < 1 or args.delay < 0:
        parser.error("--max-mb must be positive and --delay cannot be negative")
    try:
        docs = load_manifest(args.manifest)
    except Exception as exc:
        print(f"Manifest error: {exc}", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    report_path = args.out / "collection_report.jsonl"
    review_path = args.out / "review_queue.jsonl"
    results = []
    timeout = httpx.Timeout(30.0, connect=10.0)
    with httpx.Client(timeout=timeout, headers={"User-Agent": "LegalCopilotResearch/0.1 (document retrieval; contact details should be added before production)"}) as client:
        for index, doc in enumerate(docs):
            doc_id = doc["document_id"]
            metadata_path = args.out / "metadata" / f"{doc_id}.json"
            try:
                if args.process_existing and metadata_path.exists():
                    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                else:
                    metadata = download_document(client, doc, args.out, args.max_mb * 1024 * 1024)
                audit = process_document(args.out, metadata)
                result = {
                    "document_id": doc_id,
                    "status": "downloaded_and_extracted" if not audit["extraction_error"] else "downloaded_extraction_needs_attention",
                    "sha256": metadata["sha256"],
                    "article_headings_detected": audit["audit"]["article_headings_detected"],
                    "numeric_article_gaps": audit["audit"]["numeric_article_gaps"],
                    "warnings": audit["audit"]["warnings"],
                    "extraction_error": audit["extraction_error"],
                }
                append_jsonl(review_path, {
                    "document_id": doc_id,
                    "source_id": metadata["source_id"],
                    "source_url": metadata["source_url"],
                    "original_sha256": metadata["sha256"],
                    "review_status": "pending_human_review",
                    "legal_authenticity_verified": False,
                    "current_legal_status_verified": False,
                    "commercial_reuse_permission_verified": False,
                    "review_reasons": (audit["audit"]["warnings"] + ([audit["extraction_error"]] if audit["extraction_error"] else [])),
                })
                print(f"[{index + 1}/{len(docs)}] {doc_id}: {result['status']} ({metadata['sha256'][:12]})")
            except Exception as exc:
                result = {"document_id": doc_id, "status": "skipped_or_failed", "error": f"{type(exc).__name__}: {exc}"}
                append_jsonl(review_path, {
                    "document_id": doc_id,
                    "source_id": doc.get("source_id"),
                    "source_url": doc.get("direct_url"),
                    "review_status": "collection_permission_or_download_error",
                    "legal_authenticity_verified": False,
                    "current_legal_status_verified": False,
                    "error": result["error"],
                })
                print(f"[{index + 1}/{len(docs)}] {doc_id}: SKIPPED — {result['error']}", file=sys.stderr)
            append_jsonl(report_path, result)
            results.append(result)
            if index + 1 < len(docs) and args.delay:
                time.sleep(args.delay)
    successful = sum(r["status"] in {"downloaded_and_extracted", "downloaded_extraction_needs_attention"} for r in results)
    print(f"Finished: {successful}/{len(docs)} documents processed.")
    print(f"Originals: {args.out / 'originals'}")
    print(f"Review queue: {review_path}")
    print("No document is automatically marked as legally authentic, current, or verified.")
    return 0 if successful == len(docs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
