#!/usr/bin/env python3
"""Audit acquisition-manifest readiness against the source permission register.

This tool is read-only: it never changes permission, downloads documents, or certifies
legal authenticity/current status. Collection and commercial product-use readiness
require an explicit, evidence-backed, document-level permission-scope review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs" / "collection_manifest.example.json"
DEFAULT_REGISTER = ROOT / "docs" / "source_permission_register.json"
COLLECTION_ALLOWED = {"allowed", "allowed_limited"}
COMMERCIAL_ALLOWED = {"allowed", "allowed_limited"}


def _valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = dt.date.fromisoformat(value)
        return parsed.isoformat() == value and parsed <= dt.date.today()
    except ValueError:
        return False


def _hostname(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username is not None or parsed.password is not None:
            return None
        return parsed.hostname.lower().rstrip(".")
    except ValueError:
        return None


def _host_matches(host: str | None, allowed_hosts: object) -> bool:
    if host is None or not isinstance(allowed_hosts, list) or not allowed_hosts:
        return False
    normalized = {
        item.strip().lower().rstrip(".")
        for item in allowed_hosts
        if isinstance(item, str) and item.strip()
    }
    return any(host == item or host.endswith("." + item) for item in normalized)


SCOPE_FLAGS = (
    "storage",
    "text_extraction",
    "indexing",
    "commercial_product_use",
    "excerpt_display",
)


def _scope_review_valid(document: dict) -> bool:
    """Match the acquisition pipeline's exact fail-closed permission review contract."""
    review = document.get("permission_scope_review")
    if not isinstance(review, dict) or review.get("status") != "passed":
        return False
    if not isinstance(review.get("evidence"), str) or len(review["evidence"].strip()) < 3:
        return False
    if not isinstance(review.get("reviewer_id"), str) or not review["reviewer_id"].strip():
        return False
    if not isinstance(review.get("evidence_reference"), str) or len(review["evidence_reference"].strip()) < 3:
        return False
    if review.get("access_method") != "direct_document_url" or review.get("source_terms_reviewed") is not True:
        return False
    if not _valid_date(review.get("reviewed_on")) or not _valid_date(document.get("terms_checked_on")):
        return False
    if review["reviewed_on"] < document["terms_checked_on"]:
        return False
    evidence_url = review.get("evidence_url")
    if evidence_url is not None:
        try:
            parsed = urlparse(evidence_url) if isinstance(evidence_url, str) else None
            if (
                parsed is None or parsed.scheme != "https" or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
            ):
                return False
        except ValueError:
            return False
    scope = review.get("scope")
    return isinstance(scope, dict) and all(scope.get(flag) is True for flag in SCOPE_FLAGS)


def audit(manifest: dict, register: dict) -> dict:
    """Return per-document readiness findings without changing either input."""
    findings: list[dict] = []
    sources = register.get("sources") if isinstance(register, dict) else None
    documents = manifest.get("documents") if isinstance(manifest, dict) else None
    if not isinstance(sources, list):
        return {"schema_error": "source permission register must contain a sources list", "documents": [], "findings": []}
    if not isinstance(documents, list):
        return {"schema_error": "manifest must contain a documents list", "documents": [], "findings": []}

    source_by_id: dict[str, dict] = {}
    duplicate_source_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            continue
        if source_id in source_by_id:
            duplicate_source_ids.add(source_id)
        source_by_id[source_id] = source

    results = []
    seen_document_ids: set[str] = set()
    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            findings.append({"severity": "blocker", "code": "invalid_document_entry", "index": index})
            continue
        document_id = document.get("document_id")
        source_id = document.get("source_id")
        blockers: list[str] = []
        warnings: list[str] = []

        if not isinstance(document_id, str) or not document_id.strip():
            blockers.append("missing_document_id")
        elif document_id in seen_document_ids:
            blockers.append("duplicate_document_id")
        else:
            seen_document_ids.add(document_id)

        if not isinstance(source_id, str) or source_id not in source_by_id:
            source = None
            blockers.append("source_id_not_in_permission_register")
        else:
            source = source_by_id[source_id]
            if source_id in duplicate_source_ids:
                blockers.append("duplicate_source_id_in_permission_register")

        if document.get("collection_permission") != "allowed":
            blockers.append("manifest_collection_permission_not_allowed")

        if source is not None:
            if source.get("collection_permission") not in COLLECTION_ALLOWED:
                blockers.append("source_register_does_not_allow_collection")
            if not source.get("permission_evidence") or not _valid_date(source.get("terms_checked_on")):
                blockers.append("source_permission_evidence_or_terms_date_missing")
            if source.get("commercial_reuse_permission") not in COMMERCIAL_ALLOWED:
                warnings.append("commercial_product_reuse_not_established")
        else:
            warnings.append("source_permission_record_unavailable")

        if not document.get("permission_evidence"):
            blockers.append("manifest_permission_evidence_missing")
        if not _valid_date(document.get("terms_checked_on")):
            blockers.append("manifest_terms_checked_on_missing_or_invalid")

        host = _hostname(document.get("direct_url"))
        if host is None:
            blockers.append("direct_url_not_valid_https_url")
        if not _host_matches(host, document.get("allowed_hosts")):
            blockers.append("direct_url_host_not_in_allowlist")

        scope_review_valid = _scope_review_valid(document)
        if not scope_review_valid:
            blockers.append("document_level_collection_scope_review_missing")

        collection_ready = not blockers
        commercial_evidence_valid = (
            source is not None
            and isinstance(source.get("commercial_reuse_evidence"), str)
            and bool(source["commercial_reuse_evidence"].strip())
            and _valid_date(source.get("commercial_terms_checked_on"))
        )
        commercial_source_ready = (
            source is not None
            and source.get("commercial_reuse_permission") in COMMERCIAL_ALLOWED
            and commercial_evidence_valid
        )
        product_use_ready = collection_ready and scope_review_valid and commercial_source_ready
        if source is not None and source.get("commercial_reuse_permission") not in COMMERCIAL_ALLOWED:
            warnings.append("commercial_product_reuse_not_established")
        elif source is not None and not commercial_evidence_valid:
            warnings.append("commercial_permission_evidence_or_date_missing")
        results.append({
            "document_id": document_id,
            "source_id": source_id,
            "collection_ready": collection_ready,
            "commercial_product_use_ready": product_use_ready,
            "blockers": sorted(set(blockers)),
            "warnings": sorted(set(warnings)),
        })
        for code in sorted(set(blockers)):
            findings.append({"severity": "blocker", "code": code, "document_id": document_id})
        for code in sorted(set(warnings)):
            findings.append({"severity": "warning", "code": code, "document_id": document_id})

    return {
        "schema_version": "1.0",
        "audit_type": "read_only_acquisition_readiness",
        "documents_checked": len(results),
        "collection_ready_count": sum(item["collection_ready"] for item in results),
        "commercial_product_use_ready_count": sum(item["commercial_product_use_ready"] for item in results),
        "documents": results,
        "findings": findings,
        "limitations": [
            "This report does not grant permission or initiate acquisition.",
            "A document-level scope review must cite evidence that covers the exact document and intended method/use; a status flag alone is not legal advice.",
            "This report does not verify authenticity, completeness, commencement, amendment history, current legal status, or lawyer approval.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--out", type=Path, help="Optional path for a JSON report")
    parser.add_argument(
        "--require-ready", action="store_true",
        help="Production gate: exit non-zero unless every document is collection-ready and commercially cleared",
    )
    parser.add_argument(
        "--require-collection-ready", action="store_true",
        help="Check collection readiness only; this does not authorize commercial product use",
    )
    args = parser.parse_args(argv)

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        register = json.loads(args.register.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    report = audit(manifest, register)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if report.get("schema_error"):
        return 2
    if args.require_collection_ready and report["collection_ready_count"] != report["documents_checked"]:
        return 1
    if args.require_ready and (
        report["collection_ready_count"] != report["documents_checked"]
        or report["commercial_product_use_ready_count"] != report["documents_checked"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
