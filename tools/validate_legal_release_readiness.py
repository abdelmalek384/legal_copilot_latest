#!/usr/bin/env python3
"""Fail-closed, read-only release gate for metadata-only legal registry candidates.

This gate never downloads, imports, or modifies legal content. A pass means only that
the candidate's recorded evidence satisfies the configured structural gate; it is
not a legal opinion or an independent confirmation that evidence is truthful.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / "docs" / "source_permission_register.json"
DEFAULT_CANDIDATES = ROOT / "data" / "candidates"
ALLOWED = {"allowed", "allowed_limited"}
REQUIRED_REVIEWS = {
    "source_authenticity",
    "extraction_quality",
    "legal_status",
    "amendment_history",
    "licensing",
    "lawyer_approval",
}
REQUIRED_USES = {"collection", "indexing", "commercial_product_use", "excerpt_display"}


def valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError:
        return False
    return parsed.isoformat() == value and parsed <= dt.date.today()


def https_host(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
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
    source_id = document.get("source_id")
    source_matches = [s for s in sources if s.get("source_id") == source_id]
    if not source_id or len(source_matches) != 1:
        add(blockers, "document_source_link_invalid", "Document must link to exactly one candidate source.")
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
    if source_page_host:
        register_matches = [s for s in register_sources if https_host(s.get("source_page")) == source_page_host]
    if not register_matches:
        add(blockers, "central_source_record_missing", "No central permission-register source matches the candidate source host.")
    else:
        for registered in register_matches:
            if registered.get("collection_permission") not in ALLOWED:
                add(blockers, "central_collection_permission_not_allowed",
                    f"Central source {registered.get('source_id', '(unnamed)')} does not explicitly allow collection.")
            if registered.get("commercial_reuse_permission") not in ALLOWED:
                add(blockers, "central_commercial_permission_not_allowed",
                    f"Central source {registered.get('source_id', '(unnamed)')} does not explicitly allow commercial reuse.")
            if not isinstance(registered.get("permission_evidence"), str) or not registered["permission_evidence"].strip():
                add(blockers, "central_permission_evidence_missing",
                    f"Central source {registered.get('source_id', '(unnamed)')} has no permission evidence.")
            if not valid_date(registered.get("terms_checked_on")):
                add(blockers, "central_terms_date_invalid",
                    f"Central source {registered.get('source_id', '(unnamed)')} needs a valid, non-future terms_checked_on date.")

    for field in ("collection_permission", "commercial_reuse_permission"):
        if source.get(field) not in ALLOWED:
            add(blockers, f"candidate_{field}_not_allowed", f"Candidate source {field} is not explicitly allowed.")
    if not isinstance(source.get("permission_evidence"), str) or not source["permission_evidence"].strip():
        add(blockers, "candidate_permission_evidence_missing", "Candidate source lacks permission evidence.")
    if not valid_date(source.get("terms_checked_on")):
        add(blockers, "candidate_terms_date_invalid", "Candidate source needs a valid, non-future terms_checked_on date.")

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
    for field in ("publication_date", "effective_date", "retrieved_at"):
        if not valid_date(version.get(field)):
            add(blockers, f"{field}_invalid", f"Version needs a valid, non-future {field} date.")
    if valid_date(version.get("publication_date")) and valid_date(version.get("effective_date")):
        if version["effective_date"] < version["publication_date"]:
            add(blockers, "effective_before_publication", "Effective date precedes publication date; review the legal basis.")
    if not isinstance(version.get("gazette_issue"), str) or not version["gazette_issue"].strip():
        add(blockers, "gazette_issue_missing", "Official publication issue reference is required.")
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
    text_path = version.get("extracted_text_path")
    if not isinstance(text_path, str) or not text_path.strip() or Path(text_path).is_absolute():
        add(blockers, "extracted_text_file_missing", "A relative path to the extracted text file is required.")
    else:
        extracted_path = (root / text_path).resolve()
        try:
            extracted_path.relative_to(root.resolve())
        except ValueError:
            add(blockers, "extracted_text_path_escapes_root", "Extracted text path must remain within the repository/corpus root.")
        else:
            if not extracted_path.is_file():
                add(blockers, "extracted_text_file_not_found", "Recorded extracted text file does not exist.")
            elif isinstance(text_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", text_hash) and sha256_file(extracted_path).lower() != text_hash.lower():
                add(blockers, "text_hash_mismatch", "Recorded text SHA-256 does not match extracted text bytes.")

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

    original_path = version.get("original_path")
    original_hash = version.get("original_sha256")
    if not isinstance(original_path, str) or not original_path.strip() or Path(original_path).is_absolute():
        add(blockers, "original_file_missing", "A relative path to the original source file is required.")
    elif not isinstance(original_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", original_hash):
        add(blockers, "original_hash_invalid", "Original file SHA-256 must be a 64-character hexadecimal digest.")
    else:
        candidate_path = (root / original_path).resolve()
        try:
            candidate_path.relative_to(root.resolve())
        except ValueError:
            add(blockers, "original_path_escapes_root", "Original file path must remain within the repository/corpus root.")
        else:
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
        elif review_type == "lawyer_approval" and reviewer_role not in {
            "egyptian_lawyer", "qualified_egyptian_counsel"
        }:
            add(blockers, "lawyer_qualification_not_established",
                "lawyer_approval must identify a qualified Egyptian lawyer/counsel role.")
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
    return {
        "candidate_id": candidate_id,
        "title": document.get("official_title") if isinstance(document.get("official_title"), str) else None,
        "document_type": document.get("document_type") if isinstance(document.get("document_type"), str) else None,
        "practice_areas": practice_areas,
        "legal_status": version.get("legal_status") if isinstance(version.get("legal_status"), str) else "unknown",
        "review_status": version.get("review_status") if isinstance(version.get("review_status"), str) else "unknown",
        "ready": not blockers,
        "blockers": blockers,
    }


def build_report(candidate_paths: list[Path], permission_register_path: Path, root: Path = ROOT) -> dict:
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
    blocker_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    review_counts: dict[str, int] = {}
    practice_area_counts: dict[str, dict[str, int]] = {}
    for item in reports:
        status = item.get("legal_status") or "unknown"
        review = item.get("review_status") or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        review_counts[review] = review_counts.get(review, 0) + 1
        for blocker in item.get("blockers", []):
            code = blocker.get("code", "unknown")
            blocker_counts[code] = blocker_counts.get(code, 0) + 1
        areas = item.get("practice_areas") or ["unspecified"]
        for area in areas:
            bucket = practice_area_counts.setdefault(area, {"candidate_count": 0, "ready_count": 0, "blocked_count": 0})
            bucket["candidate_count"] += 1
            bucket["ready_count"] += int(bool(item.get("ready")))
            bucket["blocked_count"] += int(not bool(item.get("ready")))
    return {
        "schema_version": 1,
        "read_only": True,
        "candidate_count": len(reports),
        "ready_count": sum(1 for item in reports if item.get("ready")),
        "blocked_count": sum(1 for item in reports if not item.get("ready")),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "legal_status_counts": dict(sorted(status_counts.items())),
        "review_status_counts": dict(sorted(review_counts.items())),
        "practice_area_coverage": dict(sorted(practice_area_counts.items())),
        "candidates": reports,
        "warning": "This checks recorded evidence and file integrity only; it cannot grant rights or independently certify legal correctness. Counts describe candidate records, not complete Egyptian-law coverage.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", help="Candidate JSON path; repeat for multiple candidates.")
    parser.add_argument("--candidates-dir", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--root", type=Path, default=ROOT, help="Root used to resolve original_path values.")
    parser.add_argument("--out", type=Path, help="Optional JSON report path.")
    parser.add_argument("--require-ready", action="store_true", help="Exit nonzero unless every candidate passes.")
    args = parser.parse_args(argv)
    candidate_paths = [Path(item) for item in args.candidate] if args.candidate else sorted(args.candidates_dir.glob("**/registry_candidate.json"))
    if not candidate_paths:
        report = {"schema_version": 1, "error": "No candidate registry JSON files found.", "candidates": [], "ready_count": 0}
    else:
        report = build_report(candidate_paths, args.register, args.root)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
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
