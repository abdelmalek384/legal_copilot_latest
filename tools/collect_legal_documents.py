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
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_acquisition_readiness import audit as audit_acquisition_readiness
from tools.validate_source_permission_register import validate as validate_source_permission_register

DEFAULT_REGISTER = ROOT / "docs" / "source_permission_register.json"
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
    if not isinstance(url, str) or not url or url != url.strip() or any(char.isspace() for char in url):
        raise ValueError("HTTPS URL must not contain whitespace")
    try:
        parsed = urlparse(url)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Only valid absolute HTTPS URLs are allowed") from exc
    if parsed.scheme != "https" or not parsed.hostname or (port is not None and not 1 <= port <= 65535):
        raise ValueError("Only absolute HTTPS URLs with a valid port are allowed")
    if parsed.username is not None or parsed.password is not None:
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


def validate_manifest_hosts(doc: dict) -> set[str]:
    """Validate host allowlisting without implying collection permission.

    This is safe to use for discovery-only / permission-pending manifest entries.
    Actual download paths must still call check_permission(), which fails closed.
    """
    hosts = doc.get("allowed_hosts")
    if not isinstance(hosts, list) or not hosts:
        raise ValueError("allowed_hosts must explicitly list the approved source host(s)")
    normalized = set()
    for item in hosts:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("allowed_hosts entries must be non-empty hostnames")
        host = item.strip().lower().rstrip(".")
        if ":" in host or "/" in host or "@" in host or host.startswith(".") or host.endswith("."):
            raise ValueError("allowed_hosts entries must be hostnames without schemes, paths, ports, or credentials")
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?", host):
            raise ValueError("allowed_hosts contains an invalid hostname")
        normalized.add(host)
    direct_url = doc.get("direct_url", "")
    if not isinstance(direct_url, str) or not direct_url or direct_url != direct_url.strip() or any(char.isspace() for char in direct_url):
        raise ValueError("direct_url must not contain whitespace")
    try:
        parsed = urlparse(direct_url)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("direct_url must be a valid absolute HTTPS URL") from exc
    if parsed.scheme != "https" or not parsed.hostname or (port is not None and not 1 <= port <= 65535):
        raise ValueError("direct_url must be an absolute HTTPS URL with a valid port")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("direct_url must not contain credentials")
    url_host = parsed.hostname.lower().rstrip(".")
    if not any(url_host == h or url_host.endswith("." + h) for h in normalized):
        raise ValueError("direct_url host must match an explicitly allowed host")
    return normalized


PERMISSION_SCOPE_FLAGS = (
    "storage",
    "text_extraction",
    "indexing",
    "commercial_product_use",
    "excerpt_display",
)


def validate_permission_scope_review(doc: dict) -> dict:
    """Require explicit, use-specific review before any collection can run.

    This checks recorded metadata only; it cannot prove the reviewer or evidence
    is genuine. Production release still requires independent legal review.
    """
    review = doc.get("permission_scope_review")
    if not isinstance(review, dict):
        raise ValueError("permission_scope_review must document the approved collection scope")
    if review.get("status") != "passed":
        raise ValueError("permission_scope_review.status must be 'passed'")
    evidence = review.get("evidence")
    if not isinstance(evidence, str) or len(evidence.strip()) < 3:
        raise ValueError("permission_scope_review.evidence must identify the reviewed authorization/terms")
    reviewer = review.get("reviewer_id")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("permission_scope_review.reviewer_id is required")
    evidence_ref = review.get("evidence_reference")
    if not isinstance(evidence_ref, str) or len(evidence_ref.strip()) < 3:
        raise ValueError("permission_scope_review.evidence_reference must identify the reviewed evidence")
    if review.get("access_method") != "direct_document_url":
        raise ValueError("permission_scope_review.access_method must explicitly authorize direct_document_url retrieval")
    if review.get("source_terms_reviewed") is not True:
        raise ValueError("permission_scope_review.source_terms_reviewed must be true")
    reviewed_on = parse_date(review.get("reviewed_on"), "permission_scope_review.reviewed_on")
    today = dt.datetime.now(dt.timezone.utc).date()
    if reviewed_on > today:
        raise ValueError("permission_scope_review.reviewed_on cannot be in the future")
    terms_checked_on = parse_date(doc.get("terms_checked_on"), "terms_checked_on")
    if terms_checked_on > today:
        raise ValueError("terms_checked_on cannot be in the future")
    if reviewed_on < terms_checked_on:
        raise ValueError("permission_scope_review.reviewed_on cannot precede terms_checked_on")
    evidence_url = review.get("evidence_url")
    if evidence_url is not None:
        parsed_evidence = urlparse(evidence_url) if isinstance(evidence_url, str) else None
        if (
            parsed_evidence is None
            or parsed_evidence.scheme != "https"
            or not parsed_evidence.hostname
            or parsed_evidence.username is not None
            or parsed_evidence.password is not None
        ):
            raise ValueError("permission_scope_review.evidence_url must be HTTPS without credentials or null")
    scope = review.get("scope")
    if not isinstance(scope, dict):
        raise ValueError("permission_scope_review.scope must be an object")
    for flag in PERMISSION_SCOPE_FLAGS:
        if scope.get(flag) is not True:
            raise ValueError(f"permission_scope_review.scope.{flag} must be explicitly true")
    return review


def check_permission(doc: dict) -> set[str]:
    if doc.get("collection_permission") != "allowed":
        raise ValueError("collection_permission must be explicitly set to 'allowed'")
    evidence = doc.get("permission_evidence")
    if not isinstance(evidence, str) or len(evidence.strip()) < 8:
        raise ValueError("permission_evidence must identify reviewed terms or written permission")
    validate_permission_scope_review(doc)
    return validate_manifest_hosts(doc)


def store_original(out: Path, document_id: str, extension: str, raw: bytes) -> Path:
    """Store a source file without overwriting prior bytes or following storage symlinks."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", document_id):
        raise ValueError("document_id is not a safe storage identifier")
    digest = sha256_bytes(raw)
    originals_root = out / "originals"
    if originals_root.is_symlink():
        raise ValueError("originals directory must not be a symbolic link")
    originals_root.mkdir(parents=True, exist_ok=True)
    original_dir = originals_root / document_id
    if original_dir.is_symlink():
        raise ValueError("document original directory must not be a symbolic link")
    original_dir.mkdir(parents=True, exist_ok=True)
    original_path = original_dir / ("original" + extension)

    def same_content(path: Path) -> bool:
        return path.is_file() and sha256_bytes(path.read_bytes()) == digest

    def create_exclusive(path: Path) -> bool:
        try:
            with path.open("xb") as stream:
                stream.write(raw)
            return True
        except FileExistsError:
            return False
        except Exception:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    if original_path.exists():
        if same_content(original_path):
            return original_path
    elif create_exclusive(original_path):
        return original_path
    elif same_content(original_path):
        return original_path

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    stem = f"original-{stamp}-{digest[:12]}"
    suffix = 0
    while True:
        filename = f"{stem}{'-' + str(suffix) if suffix else ''}{extension}"
        candidate = original_dir / filename
        if candidate.exists():
            if same_content(candidate):
                return candidate
            suffix += 1
            continue
        if create_exclusive(candidate):
            return candidate
        if same_content(candidate):
            return candidate
        suffix += 1


def _archive_metadata_version(meta_dir: Path, document_id: str, metadata: dict) -> Path:
    history_root = meta_dir / "history"
    if history_root.is_symlink():
        raise ValueError("metadata history root must not be a symbolic link")
    history_root.mkdir(parents=True, exist_ok=True)
    history_dir = history_root / document_id
    if history_dir.is_symlink():
        raise ValueError("metadata history directory must not be a symbolic link")
    history_dir.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    retrieved_at = metadata.get("retrieved_at", "")
    try:
        stamp = dt.datetime.fromisoformat(retrieved_at.replace("Z", "+00:00")).strftime("%Y%m%dT%H%M%S%fZ")
    except (TypeError, ValueError):
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    digest = metadata.get("sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
        digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    stem = f"{stamp}-{digest[:12]}"
    suffix = 0
    while True:
        name = f"{stem}{'-' + str(suffix) if suffix else ''}.json"
        candidate = history_dir / name
        try:
            with candidate.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
            return candidate
        except FileExistsError:
            if candidate.is_file() and candidate.read_text(encoding="utf-8") == rendered:
                return candidate
            suffix += 1


def persist_metadata(out: Path, document_id: str, metadata: dict) -> Path:
    """Keep immutable retrieval records and atomically update the current metadata pointer."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", document_id):
        raise ValueError("document_id is not a safe metadata identifier")
    meta_dir = out / "metadata"
    if meta_dir.is_symlink():
        raise ValueError("metadata directory must not be a symbolic link")
    meta_dir.mkdir(parents=True, exist_ok=True)
    current_path = meta_dir / f"{document_id}.json"
    if current_path.is_symlink():
        raise ValueError("current metadata file must not be a symbolic link")
    if current_path.exists():
        try:
            previous = json.loads(current_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("existing metadata is unreadable; refusing to overwrite it") from exc
        if previous != metadata:
            _archive_metadata_version(meta_dir, document_id, previous)
    _archive_metadata_version(meta_dir, document_id, metadata)

    rendered = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=meta_dir, prefix=f".{document_id}.", suffix=".tmp", delete=False
        ) as stream:
            temporary_path = Path(stream.name)
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, current_path)
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
    return current_path


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
    original_path = store_original(out, doc_id, ext, raw)
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
        "permission_scope_review": doc["permission_scope_review"],
        "collection_permission": "allowed",
        "legal_authenticity_verified": False,
        "current_legal_status_verified": False,
        "commercial_reuse_permission_verified": False,
        "review_status": "pending_human_review",
        "download_host": final_host,
    }
    persist_metadata(out, doc_id, metadata)
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


def _validated_original_path(out: Path, metadata: dict) -> Path:
    """Resolve only a regular original inside originals/<document_id>; never trust sidecar paths."""
    doc_id = metadata.get("document_id")
    if not isinstance(doc_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", doc_id):
        raise ValueError("metadata contains an unsafe document_id")
    relative = metadata.get("original_path")
    if not isinstance(relative, str):
        raise ValueError("metadata original_path must be a relative path")
    path = Path(relative)
    if path.is_absolute() or len(path.parts) != 3 or path.parts[0] != "originals" or path.parts[1] != doc_id:
        raise ValueError("metadata original_path must stay inside originals/<document_id>")
    if not path.parts[2].startswith("original"):
        raise ValueError("metadata original_path must name a preserved original")
    content_type = metadata.get("http_content_type")
    if content_type not in ALLOWED_TYPES:
        raise ValueError("metadata contains an unsupported original content type")
    if path.suffix.lower() != ALLOWED_TYPES[content_type]:
        raise ValueError("metadata original_path extension does not match its content type")

    originals_root = out / "originals"
    document_dir = originals_root / doc_id
    original = out / path
    if originals_root.is_symlink() or document_dir.is_symlink() or original.is_symlink():
        raise ValueError("original path must not traverse symbolic links")
    if not original.is_file():
        raise ValueError("metadata original_path does not identify a regular file")
    expected_hash = metadata.get("sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise ValueError("metadata sha256 must be a lowercase SHA-256 digest")
    if sha256_file(original) != expected_hash:
        raise ValueError("preserved original SHA-256 does not match metadata")
    return original


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_immutable(path: Path, payload: bytes, root: Path, document_id: str) -> Path:
    """Write content-addressed output without replacing existing artifacts or following symlinks."""
    root.mkdir(parents=True, exist_ok=True)
    if root.is_symlink():
        raise ValueError(f"{root.name} output root must not be a symbolic link")
    directory = root / document_id
    if directory.is_symlink():
        raise ValueError(f"{root.name} document directory must not be a symbolic link")
    directory.mkdir(parents=True, exist_ok=True)
    if path.parent != directory:
        raise ValueError("immutable output path escaped its document directory")
    if path.is_symlink():
        raise ValueError("immutable output file must not be a symbolic link")
    try:
        with path.open("xb") as stream:
            stream.write(payload)
        return path
    except FileExistsError:
        if path.is_file() and path.read_bytes() == payload:
            return path
        raise ValueError(f"refusing to overwrite different immutable artifact: {path.name}")


def process_document(out: Path, metadata: dict) -> dict:
    original = _validated_original_path(out, metadata)
    doc_id = metadata["document_id"]
    text, error = extract_text(original, metadata["http_content_type"])
    text_bytes = text.encode("utf-8")
    text_hash = sha256_bytes(text_bytes)
    original_hash = metadata["sha256"]
    text_path = out / "extracted" / doc_id / f"{original_hash}-{text_hash}.txt"
    _write_immutable(text_path, text_bytes, out / "extracted", doc_id)
    audit = article_audit(text)
    audit_record = {
        "document_id": doc_id,
        "source_id": metadata["source_id"],
        "original_path": metadata["original_path"],
        "original_sha256": original_hash,
        "extracted_text_path": str(text_path.relative_to(out)),
        "extracted_text_sha256": text_hash,
        "extraction_error": error,
        "audit": audit,
        "review_status": "pending_human_review",
        "legal_authenticity_verified": False,
        "current_legal_status_verified": False,
    }
    rendered_audit = (json.dumps(audit_record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    audit_hash = sha256_bytes(rendered_audit)
    audit_path = out / "audits" / doc_id / f"{original_hash}-{text_hash}-{audit_hash}.json"
    _write_immutable(audit_path, rendered_audit, out / "audits", doc_id)
    audit_record["audit_path"] = str(audit_path.relative_to(out))
    return audit_record

def append_jsonl(path: Path, record: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or path.is_symlink():
        raise ValueError("JSONL output path must not traverse symbolic links")
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as exc:
        raise ValueError(f"cannot safely open JSONL output: {exc}") from exc
    with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate_output_layout(out: Path) -> None:
    """Reject pre-existing symlink targets before the collector makes network requests."""
    if out.is_symlink():
        raise ValueError("output root must not be a symbolic link")
    for name in ("originals", "metadata", "extracted", "audits"):
        if (out / name).is_symlink():
            raise ValueError(f"{name} output directory must not be a symbolic link")
    for name in ("collection_report.jsonl", "review_queue.jsonl"):
        if (out / name).is_symlink():
            raise ValueError(f"{name} output file must not be a symbolic link")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "docs" / "collection_manifest.example.json")
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER,
                        help="Central source permission register; every document must pass collection and commercial-use gates.")
    parser.add_argument("--out", type=Path, default=Path("legal_corpus"))
    parser.add_argument("--max-mb", type=int, default=40)
    parser.add_argument("--delay", type=float, default=2.0, help="Minimum pause between requests (seconds)")
    parser.add_argument("--process-existing", action="store_true", help="Re-run extraction/audits for already downloaded files")
    args = parser.parse_args(argv)
    if args.max_mb < 1 or args.delay < 0:
        parser.error("--max-mb must be positive and --delay cannot be negative")
    try:
        docs = load_manifest(args.manifest)
    except Exception as exc:
        print(f"Manifest error: {exc}", file=sys.stderr)
        return 2
    try:
        register = json.loads(args.register.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Permission register error: {exc}", file=sys.stderr)
        return 2
    register_errors = validate_source_permission_register(register)
    if register_errors:
        print(
            "Permission register validation failed; no network requests were made.",
            file=sys.stderr,
        )
        for error in register_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    preflight = audit_acquisition_readiness({"documents": docs}, register)
    blocked = [
        item for item in preflight.get("documents", [])
        if not item.get("collection_ready") or not item.get("commercial_product_use_ready")
    ]
    if blocked:
        print(
            "Permission preflight blocked acquisition/indexing; no network requests were made. "
            "Every document must pass both collection and commercial product-use gates.",
            file=sys.stderr,
        )
        print(json.dumps({"blocked_documents": blocked}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    try:
        args.out.mkdir(parents=True, exist_ok=True)
        validate_output_layout(args.out)
    except (OSError, ValueError) as exc:
        print(f"Output path error: {exc}", file=sys.stderr)
        return 2
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
                    if metadata_path.is_symlink():
                        raise ValueError("existing metadata sidecar must not be a symbolic link")
                    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                else:
                    metadata = download_document(client, doc, args.out, args.max_mb * 1024 * 1024)
                audit = process_document(args.out, metadata)
                result = {
                    "document_id": doc_id,
                    "status": "downloaded_and_extracted" if not audit["extraction_error"] else "downloaded_extraction_needs_attention",
                    "sha256": metadata["sha256"],
                    "extracted_text_sha256": audit["extracted_text_sha256"],
                    "extracted_text_path": audit["extracted_text_path"],
                    "audit_path": audit["audit_path"],
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
                    "extracted_text_sha256": audit["extracted_text_sha256"],
                    "extracted_text_path": audit["extracted_text_path"],
                    "audit_path": audit["audit_path"],
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
