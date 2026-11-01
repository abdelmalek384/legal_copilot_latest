#!/usr/bin/env python3
"""Fail-closed, read-only release gate for metadata-only legal registry candidates.

This gate never downloads, imports, or modifies legal content. A pass means only that
the candidate's recorded evidence satisfies the configured structural gate; it is
not a legal opinion or an independent confirmation that evidence is truthful.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / "docs" / "source_permission_register.json"
DEFAULT_CANDIDATES = ROOT / "data" / "candidates"
DEFAULT_COVERAGE_MATRIX = ROOT / "docs" / "legal_coverage_matrix.csv"
ALLOWED = {"allowed", "allowed_limited"}
REQUIRED_REVIEWS = {
    "source_authenticity",
    "extraction_quality",
    "legal_status",
    "amendment_history",
    "licensing",
    "lawyer_approval",
}
REQUIRED_USES = {"collection", "storage", "text_extraction", "indexing", "commercial_product_use", "excerpt_display"}


def valid_calendar_date(value: object) -> bool:
    """Validate a real ISO calendar date without assuming it must be in the past."""
    if not isinstance(value, str):
        return False
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError:
        return False
    return parsed.isoformat() == value


def valid_date(value: object) -> bool:
    """Validate an ISO calendar date that must not be in the future."""
    return valid_calendar_date(value) and dt.date.fromisoformat(value) <= dt.date.today()


def valid_timestamp(value: object) -> bool:
    """Require an ISO-8601 timestamp with an explicit timezone, not a date-only placeholder."""
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        return False
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        return False
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return False
    return parsed <= dt.datetime.now(dt.timezone.utc).astimezone(parsed.tzinfo)


def https_host(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    if value != value.strip() or any(char.isspace() or ord(char) < 32 for char in value):
        return None
    try:
        parsed = urlparse(value)
        port = parsed.port
        if (
            parsed.scheme.lower() != "https" or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.netloc.endswith(":")
            or (port is not None and not 1 <= port <= 65535)
        ):
            return None
        host = parsed.hostname.lower().rstrip(".")
        return host[4:] if host.startswith("www.") else host
    except ValueError:
        return None

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_identifiers(value: object) -> list[str] | None:
    if not isinstance(value, list) or not value:
        return None
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return None
    return [item.strip() for item in value]


def add(blockers: list[dict], code: str, detail: str) -> None:
    blockers.append({"code": code, "detail": detail})


def resolve_corpus_artifact(root: Path, value: object, expected_directory: str) -> tuple[Path | None, str | None]:
    """Resolve a corpus artifact only from its expected relative directory, without symlinks."""
    if not isinstance(value, str) or not value or value.strip() != value or "\\" in value:
        return None, "invalid"
    relative = Path(value)
    if (
        relative.is_absolute()
        or not relative.parts
        or relative.parts[0] != expected_directory
        or ".." in relative.parts
        or relative.as_posix() != value
    ):
        return None, "invalid"
    root_resolved = root.resolve()
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return None, "symlink"
    resolved = cursor.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        return None, "escapes"
    return resolved, None


def audit_candidate(candidate: object, permission_register: object, root: Path = ROOT) -> dict:
    blockers: list[dict] = []
    if not isinstance(candidate, dict):
        add(blockers, "candidate_not_object", "Candidate root must be a JSON object.")
        return {"candidate_id": None, "ready": False, "blockers": blockers}
    document = candidate.get("document")
    version = candidate.get("version")
    sources = candidate.get("sources")
    reviews = candidate.get("reviews")
    if not isinstance(document, dict):
        add(blockers, "document_missing", "Candidate must contain a document object.")
        document = {}
    if not isinstance(version, dict):
        add(blockers, "version_missing", "Candidate must contain a version object.")
        version = {}
    if not isinstance(sources, list) or not sources or any(not isinstance(item, dict) for item in sources):
        add(blockers, "candidate_sources_invalid", "Candidate sources must be a non-empty list of objects.")
        sources = []
    if not isinstance(reviews, list) or any(not isinstance(item, dict) for item in reviews):
        add(blockers, "reviews_invalid", "Candidate reviews must be a list of objects.")
        reviews = []

    candidate_id = document.get("document_id") if isinstance(document.get("document_id"), str) else None
    if not isinstance(candidate_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", candidate_id):
        add(blockers, "document_id_invalid", "Document needs a stable ASCII document_id using letters, numbers, underscore, or hyphen.")
    if not isinstance(document.get("official_title"), str) or not document["official_title"].strip():
        add(blockers, "official_title_missing", "Document needs a non-empty official_title.")
    if not isinstance(document.get("document_type"), str) or not document["document_type"].strip():
        add(blockers, "document_type_missing", "Document needs a non-empty document_type.")
    release_priority = document.get("release_priority")
    if release_priority not in {"P0", "P1", "P2", "P3"}:
        add(blockers, "release_priority_missing", "Document needs an explicit release_priority of P0, P1, P2, or P3.")
    source_id = document.get("source_id")
    source_matches = [s for s in sources if s.get("source_id") == source_id]
    if not isinstance(source_id, str) or not source_id.strip() or len(source_matches) != 1:
        add(blockers, "document_source_link_invalid", "Document must link to exactly one candidate source by non-empty source_id.")
        source = {}
    else:
        source = source_matches[0]

    source_page_host = https_host(source.get("source_page"))
    version_url_host = https_host(version.get("source_url"))
    if source_page_host is None or version_url_host is None:
        add(blockers, "source_url_not_https", "Candidate source page and version URL must be valid HTTPS URLs without credentials.")
    elif source_page_host != version_url_host:
        add(blockers, "version_source_host_mismatch", "Version URL host does not match its linked candidate source.")

    if not isinstance(permission_register, dict) or not isinstance(permission_register.get("sources"), list):
        add(blockers, "permission_register_invalid", "Central source permission register must contain a sources list.")
        register_sources = []
    else:
        register_sources = [s for s in permission_register["sources"] if isinstance(s, dict)]

    register_matches = []
    if source_page_host and isinstance(source_id, str) and source_id.strip():
        register_matches = [
            item for item in register_sources
            if item.get("source_id") == source_id
            and https_host(item.get("source_page")) == source_page_host
        ]
    if not register_matches:
        same_host = [item for item in register_sources if source_page_host and https_host(item.get("source_page")) == source_page_host]
        if same_host:
            add(blockers, "central_source_id_mismatch",
                "A source shares this hostname but its permission-register source_id does not match the candidate; permission cannot transfer by hostname alone.")
        else:
            add(blockers, "central_source_record_missing",
                "No central permission-register source matches both the candidate source_id and source host.")
    elif len(register_matches) != 1:
        add(blockers, "central_source_record_ambiguous",
            "Exactly one central permission-register source must match both the candidate source_id and source host; duplicate matching records are ambiguous.")
    else:
        for registered in register_matches:
            for permission_field in ("collection_permission", "commercial_reuse_permission"):
                if source.get(permission_field) != registered.get(permission_field):
                    add(
                        blockers,
                        "candidate_register_permission_state_mismatch",
                        f"Candidate {permission_field} does not exactly match the canonical source-permission register.",
                    )
            if registered.get("collection_permission") not in ALLOWED:
                add(blockers, "central_collection_permission_not_allowed",
                    f"Central source {registered.get('source_id', '(unnamed)')} does not explicitly allow collection.")
            elif https_host(registered.get("permission_evidence_url")) is None:
                add(blockers, "central_permission_evidence_url_invalid",
                    f"Central source {registered.get('source_id', '(unnamed)')} needs a direct HTTPS URL to inspectable collection-rights evidence.")
            if registered.get("commercial_reuse_permission") not in ALLOWED:
                add(blockers, "central_commercial_permission_not_allowed",
                    f"Central source {registered.get('source_id', '(unnamed)')} does not explicitly allow commercial reuse.")
            else:
                if https_host(registered.get("commercial_reuse_evidence_url")) is None:
                    add(blockers, "central_commercial_permission_evidence_url_invalid",
                        f"Central source {registered.get('source_id', '(unnamed)')} needs a separate HTTPS URL to inspectable commercial-rights evidence.")
                if not isinstance(registered.get("commercial_reuse_evidence"), str) or not registered["commercial_reuse_evidence"].strip():
                    add(blockers, "central_commercial_permission_evidence_missing",
                        f"Central source {registered.get('source_id', '(unnamed)')} lacks separate commercial reuse evidence.")
                if not valid_date(registered.get("commercial_terms_checked_on")):
                    add(blockers, "central_commercial_terms_date_invalid",
                        f"Central source {registered.get('source_id', '(unnamed)')} lacks a valid commercial terms review date.")
            if not isinstance(registered.get("permission_evidence"), str) or not registered["permission_evidence"].strip():
                add(blockers, "central_permission_evidence_missing",
                    f"Central source {registered.get('source_id', '(unnamed)')} has no permission evidence.")
            if not valid_date(registered.get("terms_checked_on")):
                add(blockers, "central_terms_date_invalid",
                    f"Central source {registered.get('source_id', '(unnamed)')} needs a valid, non-future terms_checked_on date.")

    for field in ("collection_permission", "commercial_reuse_permission"):
        if source.get(field) not in ALLOWED:
            add(blockers, f"candidate_{field}_not_allowed", f"Candidate source {field} is not explicitly allowed.")
    if not isinstance(source.get("authority"), str) or not source["authority"].strip():
        add(blockers, "candidate_source_authority_missing", "Candidate source needs a named issuing authority or repository owner.")
    if not isinstance(source.get("source_class"), str) or not source["source_class"].strip():
        add(blockers, "candidate_source_class_missing", "Candidate source must be classified as primary, official copy, secondary, user-supplied, or another explicit provenance class.")
    if not isinstance(source.get("permission_evidence"), str) or not source["permission_evidence"].strip():
        add(blockers, "candidate_permission_evidence_missing", "Candidate source lacks collection permission evidence.")
    if source.get("collection_permission") in ALLOWED and https_host(source.get("permission_evidence_url")) is None:
        add(blockers, "candidate_permission_evidence_url_invalid", "Candidate source needs a direct HTTPS URL to inspectable collection-rights evidence.")
    if not valid_date(source.get("terms_checked_on")):
        add(blockers, "candidate_terms_date_invalid", "Candidate source needs a valid, non-future terms_checked_on date.")
    if source.get("commercial_reuse_permission") in ALLOWED:
        if https_host(source.get("commercial_reuse_evidence_url")) is None:
            add(blockers, "candidate_commercial_permission_evidence_url_invalid", "Candidate source needs a separate HTTPS URL to inspectable commercial-rights evidence.")
        if not isinstance(source.get("commercial_reuse_evidence"), str) or not source["commercial_reuse_evidence"].strip():
            add(blockers, "candidate_commercial_permission_evidence_missing",
                "Candidate source needs separate commercial_reuse_evidence; collection evidence is not sufficient.")
        if not valid_date(source.get("commercial_terms_checked_on")):
            add(blockers, "candidate_commercial_terms_date_invalid",
                "Candidate source needs a valid, non-future commercial_terms_checked_on date.")

    scope = document.get("permission_scope_review")
    if not isinstance(scope, dict) or scope.get("status") != "passed":
        add(blockers, "document_scope_review_not_passed", "Document-level permission scope review must be passed.")
    else:
        if not isinstance(scope.get("evidence"), str) or not scope["evidence"].strip():
            add(blockers, "document_scope_evidence_missing", "Document-level scope review needs evidence.")
        if not valid_date(scope.get("reviewed_on")):
            add(blockers, "document_scope_date_invalid", "Document-level scope review needs a valid, non-future reviewed_on date.")
        approved_uses = scope.get("approved_uses")
        if not isinstance(approved_uses, list) or not REQUIRED_USES.issubset(
            {item for item in approved_uses if isinstance(item, str)}
        ):
            add(blockers, "document_scope_uses_incomplete",
                "Document scope must explicitly approve collection, indexing, commercial_product_use, and excerpt_display.")

    if version.get("review_status") != "verified":
        add(blockers, "version_not_verified", "Version review_status must be verified.")
    if version.get("legal_status") not in {
        "in_force", "partially_repealed", "repealed", "historical", "not_yet_in_force"
    }:
        add(blockers, "legal_status_unverified",
            "Version needs a recognized, reviewed legal status; unknown/under_review cannot pass.")
    for field in ("authenticity_verified", "status_verified", "amendment_history_verified"):
        if version.get(field) not in (1, True):
            add(blockers, f"{field}_false", f"Version field {field} must be explicitly true.")
    for field in ("publication_date", "effective_date"):
        if not valid_date(version.get(field)):
            add(blockers, f"{field}_invalid", f"Version needs a valid, non-future {field} date.")
    if not valid_timestamp(version.get("retrieved_at")):
        add(blockers, "retrieved_at_invalid",
            "Version needs a timezone-aware ISO-8601 retrieval timestamp; a date-only value is insufficient.")
    if valid_date(version.get("publication_date")) and valid_date(version.get("effective_date")):
        if version["effective_date"] < version["publication_date"]:
            add(blockers, "effective_before_publication", "Effective date precedes publication date; review the legal basis.")
    repeal_date = version.get("repeal_date")
    if repeal_date is not None:
        if not valid_calendar_date(repeal_date):
            add(blockers, "repeal_date_invalid", "A recorded repeal_date must be a real YYYY-MM-DD calendar date.")
        elif valid_date(version.get("effective_date")) and repeal_date < version["effective_date"]:
            add(blockers, "repeal_before_effective", "Repeal date precedes the version's effective date; review the legal timeline.")
    if version.get("legal_status") in {"repealed", "historical"} and not valid_date(repeal_date):
        add(blockers, "repeal_date_required_for_historical_status",
            "A version marked repealed or historical needs a verified, valid repeal/end date; otherwise it could be treated as active indefinitely.")
    if (
        version.get("legal_status") == "in_force"
        and valid_calendar_date(repeal_date)
        and dt.date.fromisoformat(repeal_date) <= dt.date.today()
    ):
        add(blockers, "in_force_after_repeal_date",
            "A version marked in_force has an end/repeal date that has already arrived; reconcile the recorded legal status.")
    if not isinstance(version.get("gazette_issue"), str) or not version["gazette_issue"].strip():
        add(blockers, "gazette_issue_missing", "Official publication issue reference is required.")
    if not isinstance(version.get("gazette_pages"), str) or not version["gazette_pages"].strip():
        add(blockers, "gazette_pages_missing", "Official publication page range or decision pinpoint is required.")
    if https_host(version.get("publication_evidence_url")) is None:
        add(blockers, "publication_evidence_url_invalid",
            "Publication date and Gazette metadata need a traceable HTTPS evidence URL.")
    if not isinstance(version.get("permission_evidence"), str) or not version["permission_evidence"].strip():
        add(blockers, "version_permission_evidence_missing", "Version record needs permission evidence.")

    if version.get("text_review_status") not in {"text_checked", "lawyer_approved"}:
        add(blockers, "text_review_status_unchecked",
            "Extracted text must have an explicit text_checked or lawyer_approved status.")
    if https_host(version.get("text_review_evidence_url")) is None:
        add(blockers, "text_review_evidence_url_invalid",
            "Text-completeness review needs an HTTPS evidence URL.")
    text_hash = version.get("text_sha256")
    if not isinstance(text_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", text_hash):
        add(blockers, "text_hash_invalid", "Extracted-text SHA-256 must be a 64-character hexadecimal digest.")
    extracted_text_content = None
    text_path = version.get("extracted_text_path")
    if not isinstance(text_path, str) or not text_path.strip():
        add(blockers, "extracted_text_file_missing", "A relative path to the extracted text file is required.")
    else:
        extracted_path, path_error = resolve_corpus_artifact(root, text_path, "extracted")
        if path_error == "invalid":
            add(blockers, "extracted_text_path_invalid", "Extracted text path must be a normalized relative path inside extracted/.")
        elif path_error == "symlink":
            add(blockers, "extracted_text_path_symlinked", "Extracted text path must not traverse symbolic links.")
        elif path_error == "escapes":
            add(blockers, "extracted_text_path_escapes_root", "Extracted text path must remain within the repository/corpus root.")
        elif extracted_path is not None:
            if not extracted_path.is_file():
                add(blockers, "extracted_text_file_not_found", "Recorded extracted text file does not exist.")
            else:
                if isinstance(text_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", text_hash) and sha256_file(extracted_path).lower() != text_hash.lower():
                    add(blockers, "text_hash_mismatch", "Recorded text SHA-256 does not match extracted text bytes.")
                try:
                    extracted_text_content = extracted_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    add(blockers, "extracted_text_encoding_invalid", "Extracted text must be valid UTF-8.")
                else:
                    if not extracted_text_content.strip():
                        add(blockers, "extracted_text_empty", "Extracted text file is empty.")

    actual_articles = normalized_identifiers(version.get("article_identifiers"))
    expected_articles = normalized_identifiers(version.get("expected_article_identifiers"))
    if actual_articles is None:
        add(blockers, "article_identifiers_invalid", "Extracted text needs a non-empty list of article/decision pinpoint identifiers.")
    elif len(actual_articles) != len(set(actual_articles)):
        add(blockers, "article_identifiers_duplicated", "Extracted article/decision identifiers contain duplicates.")
    if expected_articles is None:
        add(blockers, "expected_article_identifiers_invalid",
            "A non-empty reviewed list of expected article/decision identifiers is required.")
    elif len(expected_articles) != len(set(expected_articles)):
        add(blockers, "expected_article_identifiers_duplicated",
            "Expected article/decision identifiers contain duplicates.")
    if actual_articles is not None and expected_articles is not None:
        missing_articles = sorted(set(expected_articles) - set(actual_articles))
        unexpected_articles = sorted(set(actual_articles) - set(expected_articles))
        if missing_articles:
            add(blockers, "article_identifiers_missing",
                "Extracted text is missing expected identifiers: " + ", ".join(missing_articles[:20]))
        if unexpected_articles:
            add(blockers, "article_identifiers_unexpected",
                "Extracted text has identifiers absent from the reviewed expected list: " + ", ".join(unexpected_articles[:20]))
    if extracted_text_content is not None and actual_articles is not None:
        absent_anchors = [identifier for identifier in actual_articles if identifier not in extracted_text_content]
        if absent_anchors:
            add(blockers, "article_identifiers_not_in_text",
                "Recorded article/decision anchors are absent from extracted text: " + ", ".join(absent_anchors[:20]))

    original_path = version.get("original_path")
    original_hash = version.get("original_sha256")
    if not isinstance(original_path, str) or not original_path.strip():
        add(blockers, "original_file_missing", "A relative path to the original source file is required.")
    elif not isinstance(original_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", original_hash):
        add(blockers, "original_hash_invalid", "Original file SHA-256 must be a 64-character hexadecimal digest.")
    else:
        candidate_path, path_error = resolve_corpus_artifact(root, original_path, "originals")
        if path_error == "invalid":
            add(blockers, "original_path_invalid", "Original path must be a normalized relative path inside originals/.")
        elif path_error == "symlink":
            add(blockers, "original_path_symlinked", "Original file path must not traverse symbolic links.")
        elif path_error == "escapes":
            add(blockers, "original_path_escapes_root", "Original file path must remain within the repository/corpus root.")
        elif candidate_path is not None:
            if not candidate_path.is_file():
                add(blockers, "original_file_not_found", "Recorded original file does not exist.")
            elif sha256_file(candidate_path).lower() != original_hash.lower():
                add(blockers, "original_hash_mismatch", "Recorded SHA-256 does not match the original file bytes.")

    review_by_type: dict[str, list[dict]] = {}
    for review in reviews:
        review_type = review.get("review_type")
        if isinstance(review_type, str):
            review_by_type.setdefault(review_type, []).append(review)
    for review_type in sorted(REQUIRED_REVIEWS):
        entries = review_by_type.get(review_type, [])
        if len(entries) != 1:
            add(blockers, "review_missing_or_duplicate", f"Exactly one {review_type} review record is required.")
            continue
        review = entries[0]
        if review.get("outcome") != "pass":
            add(blockers, "review_not_passed", f"{review_type} review outcome must be pass.")
        if not isinstance(review.get("notes"), str) or not review["notes"].strip():
            add(blockers, "review_notes_missing", f"{review_type} review needs notes.")
        reviewer_id = review.get("reviewer_id")
        if not isinstance(reviewer_id, str) or not reviewer_id.strip():
            add(blockers, "reviewer_identity_missing", f"{review_type} review needs a traceable reviewer_id.")
        reviewer_role = review.get("reviewer_role")
        if not isinstance(reviewer_role, str) or not reviewer_role.strip():
            add(blockers, "reviewer_role_missing", f"{review_type} review needs a reviewer_role.")
        elif review_type == "lawyer_approval":
            if reviewer_role not in {"egyptian_lawyer", "qualified_egyptian_counsel"}:
                add(blockers, "lawyer_qualification_not_established",
                    "lawyer_approval must identify a qualified Egyptian lawyer/counsel role.")
            notes = review.get("notes")
            marker = re.match(
                r"^\[qualified_egyptian_counsel_attested:user_id=([1-9][0-9]*)\](?:\s|$)",
                notes if isinstance(notes, str) else "",
            )
            marker_id = marker.group(1) if marker is not None else None
            marker_id_valid = (
                isinstance(marker_id, str)
                and len(marker_id) <= 19
                and int(marker_id) <= (2**63 - 1)
            )
            if not marker_id_valid or not isinstance(reviewer_id, str) or reviewer_id != marker_id:
                add(blockers, "counsel_attestation_missing_or_mismatched",
                    "lawyer_approval must carry a positive signed-64-bit runtime counsel-allowlist ID matching reviewer_id.")
        if not valid_date(review.get("reviewed_on")):
            add(blockers, "review_date_invalid", f"{review_type} review needs a valid, non-future reviewed_on date.")
        evidence_host = https_host(review.get("evidence_url"))
        if evidence_host is None:
            add(blockers, "review_evidence_url_invalid", f"{review_type} review needs a valid HTTPS evidence URL.")
    practice_areas = document.get("practice_areas", document.get("practice_area", []))
    if isinstance(practice_areas, str):
        practice_areas = [practice_areas]
    if not isinstance(practice_areas, list):
        practice_areas = []
    practice_areas = sorted({item.strip() for item in practice_areas if isinstance(item, str) and item.strip()})
    if not practice_areas:
        add(blockers, "practice_areas_missing", "Document needs at least one explicit practice-area classification.")
    return {
        "candidate_id": candidate_id,
        "title": document.get("official_title") if isinstance(document.get("official_title"), str) else None,
        "document_type": document.get("document_type") if isinstance(document.get("document_type"), str) else None,
        "release_priority": release_priority if release_priority in {"P0", "P1", "P2", "P3"} else "unspecified",
        "source_id": source.get("source_id") if isinstance(source.get("source_id"), str) else None,
        "source_authority": source.get("authority") if isinstance(source.get("authority"), str) else "unknown",
        "source_class": source.get("source_class") if isinstance(source.get("source_class"), str) else "unknown",
        "collection_permission": source.get("collection_permission") if isinstance(source.get("collection_permission"), str) else "unknown",
        "commercial_reuse_permission": source.get("commercial_reuse_permission") if isinstance(source.get("commercial_reuse_permission"), str) else "unknown",
        "retrieved_at": version.get("retrieved_at") if isinstance(version.get("retrieved_at"), str) else None,
        "gazette_issue": version.get("gazette_issue") if isinstance(version.get("gazette_issue"), str) else None,
        "gazette_pages": version.get("gazette_pages") if isinstance(version.get("gazette_pages"), str) else None,
        "practice_areas": practice_areas,
        "legal_status": version.get("legal_status") if isinstance(version.get("legal_status"), str) else "unknown",
        "review_status": version.get("review_status") if isinstance(version.get("review_status"), str) else "unknown",
        "ready": not blockers,
        "blockers": blockers,
    }


def summarize_coverage_matrix(path: Path) -> dict:
    """Summarize planning status separately from evidence-backed candidate readiness."""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"practice_area", "priority", "status"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                return {
                    "available": False,
                    "path": str(path),
                    "error": "Coverage matrix must include practice_area, priority, and status columns.",
                }
            rows = list(reader)
    except (OSError, csv.Error, UnicodeError) as exc:
        return {"available": False, "path": str(path), "error": f"Cannot read coverage matrix: {exc}"}

    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    areas_by_status: dict[str, list[str]] = {}
    malformed_rows = 0
    seen_areas: set[str] = set()
    for row in rows:
        area = (row.get("practice_area") or "").strip()
        priority = (row.get("priority") or "unspecified").strip() or "unspecified"
        status = (row.get("status") or "unknown").strip() or "unknown"
        if not area or area in seen_areas:
            malformed_rows += 1
            continue
        seen_areas.add(area)
        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        areas_by_status.setdefault(status, []).append(area)
    return {
        "available": True,
        "planning_only": True,
        "path": str(path),
        "practice_area_count": len(seen_areas),
        "status_counts": dict(sorted(status_counts.items())),
        "priority_counts": dict(sorted(priority_counts.items())),
        "practice_areas_by_status": {key: sorted(value) for key, value in sorted(areas_by_status.items())},
        "unstarted_practice_areas": sorted(areas_by_status.get("not_started", [])),
        "malformed_or_duplicate_rows": malformed_rows,
        "warning": "This matrix records planned coverage only; it does not prove that sources exist, are licensed, or have verified current text.",
    }


def build_report(candidate_paths: list[Path], permission_register_path: Path, root: Path = ROOT,
                 coverage_matrix_path: Path = DEFAULT_COVERAGE_MATRIX) -> dict:
    try:
        register = json.loads(permission_register_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"schema_version": 1, "error": f"Cannot read permission register: {exc}", "candidates": [], "ready_count": 0}
    reports = []
    for path in candidate_paths:
        try:
            candidate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            reports.append({"candidate_file": str(path), "candidate_id": None, "ready": False,
                            "blockers": [{"code": "candidate_unreadable", "detail": str(exc)}]})
            continue
        result = audit_candidate(candidate, register, root)
        result["candidate_file"] = str(path)
        reports.append(result)
    indices_by_candidate_id: dict[str, list[int]] = {}
    for index, item in enumerate(reports):
        candidate_id = item.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id:
            indices_by_candidate_id.setdefault(candidate_id, []).append(index)
    for candidate_id, indices in indices_by_candidate_id.items():
        if len(indices) < 2:
            continue
        for index in indices:
            item = reports[index]
            if not any(blocker.get("code") == "document_id_duplicate" for blocker in item.get("blockers", [])):
                item.setdefault("blockers", []).append({
                    "code": "document_id_duplicate",
                    "detail": f"Document ID {candidate_id!r} appears in multiple candidate files.",
                })
            item["ready"] = False

    blocker_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    review_counts: dict[str, int] = {}
    source_authority_counts: dict[str, int] = {}
    source_class_counts: dict[str, int] = {}
    release_priority_counts: dict[str, int] = {}
    collection_permission_counts: dict[str, int] = {}
    commercial_permission_counts: dict[str, int] = {}
    practice_area_counts: dict[str, dict[str, int]] = {}
    for item in reports:
        status = item.get("legal_status") or "unknown"
        review = item.get("review_status") or "unknown"
        authority = item.get("source_authority") or "unknown"
        source_class = item.get("source_class") or "unknown"
        release_priority = item.get("release_priority") or "unspecified"
        collection_permission = item.get("collection_permission") or "unknown"
        commercial_permission = item.get("commercial_reuse_permission") or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        review_counts[review] = review_counts.get(review, 0) + 1
        source_authority_counts[authority] = source_authority_counts.get(authority, 0) + 1
        source_class_counts[source_class] = source_class_counts.get(source_class, 0) + 1
        release_priority_counts[release_priority] = release_priority_counts.get(release_priority, 0) + 1
        collection_permission_counts[collection_permission] = collection_permission_counts.get(collection_permission, 0) + 1
        commercial_permission_counts[commercial_permission] = commercial_permission_counts.get(commercial_permission, 0) + 1
        for blocker in item.get("blockers", []):
            code = blocker.get("code", "unknown")
            blocker_counts[code] = blocker_counts.get(code, 0) + 1
        areas = item.get("practice_areas") or ["unspecified"]
        for area in areas:
            bucket = practice_area_counts.setdefault(area, {"candidate_count": 0, "ready_count": 0, "blocked_count": 0})
            bucket["candidate_count"] += 1
            bucket["ready_count"] += int(bool(item.get("ready")))
            bucket["blocked_count"] += int(not bool(item.get("ready")))
    ready_current = sum(1 for item in reports if item.get("ready") and item.get("legal_status") == "in_force")
    ready_historical = sum(1 for item in reports if item.get("ready") and item.get("legal_status") in {"historical", "repealed"})
    return {
        "schema_version": 1,
        "read_only": True,
        "candidate_count": len(reports),
        "ready_count": sum(1 for item in reports if item.get("ready")),
        "blocked_count": sum(1 for item in reports if not item.get("ready")),
        "release_ready_current_count": ready_current,
        "release_ready_historical_count": ready_historical,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "legal_status_counts": dict(sorted(status_counts.items())),
        "review_status_counts": dict(sorted(review_counts.items())),
        "source_authority_counts": dict(sorted(source_authority_counts.items())),
        "source_class_counts": dict(sorted(source_class_counts.items())),
        "release_priority_counts": dict(sorted(release_priority_counts.items())),
        "collection_permission_counts": dict(sorted(collection_permission_counts.items())),
        "commercial_reuse_permission_counts": dict(sorted(commercial_permission_counts.items())),
        "coverage_semantics": {
            "candidate_inventory_count": len(reports),
            "evidence_ready_current_text_count": ready_current,
            "evidence_ready_historical_text_count": ready_historical,
            "unresolved_candidate_count": sum(1 for item in reports if not item.get("ready")),
            "percentage_claims": False,
        },
        "practice_area_coverage": dict(sorted(practice_area_counts.items())),
        "coverage_matrix": summarize_coverage_matrix(coverage_matrix_path),
        "candidates": reports,
        "warning": "This checks recorded evidence and file integrity only; it cannot grant rights or independently certify legal correctness. Candidate counts are not complete Egyptian-law coverage; the coverage matrix is planning metadata, not proof of available, licensed, verified current text.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", help="Candidate JSON path; repeat for multiple candidates.")
    parser.add_argument("--candidates-dir", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--coverage-matrix", type=Path, default=DEFAULT_COVERAGE_MATRIX,
                        help="Planning-only coverage matrix CSV; kept separate from verified candidate counts.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Root used to resolve original_path values.")
    parser.add_argument("--out", type=Path, help="Optional JSON report path.")
    parser.add_argument("--require-ready", action="store_true", help="Exit nonzero unless every candidate passes.")
    args = parser.parse_args(argv)
    candidate_paths = [Path(item) for item in args.candidate] if args.candidate else sorted(args.candidates_dir.glob("**/registry_candidate.json"))
    if not candidate_paths:
        report = {"schema_version": 1, "error": "No candidate registry JSON files found.", "candidates": [], "ready_count": 0}
    else:
        report = build_report(candidate_paths, args.register, args.root, args.coverage_matrix)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        destination = args.out.resolve()
        protected_files = {path.resolve() for path in candidate_paths}
        protected_files.update({args.register.resolve(), args.coverage_matrix.resolve()})
        protected_directories = {
            args.candidates_dir.resolve(),
            (args.root.resolve() / "originals"),
            (args.root.resolve() / "extracted"),
        }
        if destination in protected_files or any(
            destination == directory or directory in destination.parents
            for directory in protected_directories
        ):
            error_report = {
                "schema_version": 1,
                "error": "Report output must not overwrite candidate/register/coverage inputs or original/extracted corpus artifacts.",
                "read_only": True,
            }
            print(json.dumps(error_report, ensure_ascii=False, indent=2))
            return 2
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if "error" in report:
        return 2
    if args.require_ready and report["blocked_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
