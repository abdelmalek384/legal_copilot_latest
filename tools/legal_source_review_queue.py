#!/usr/bin/env python3
"""Read-only reviewer queue for legal-source provenance and version checks.

This tool prioritizes records for human review. It does not change review statuses,
approve legal effect, or determine whether a source is legally authoritative.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def tables(db):
    return {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def cols(db, table):
    return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}


def review_queue(db_path: Path) -> dict:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    db = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        present = tables(db)
        report = {
            "report_type": "legal_source_review_queue",
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "read_only": True,
            "records": [],
            "source_permissions": [],
            "issues": [],
            "limitations": [
                "Queue is a prioritization aid, not legal advice or a certification of authenticity.",
                "No missing field or absent review event is treated as proof that a law is invalid.",
                "No records, statuses, or reviewer decisions are modified.",
            ],
        }
        required_tables = {"legal_sources", "legal_documents", "legal_document_versions", "legal_review_events"}
        missing_tables = sorted(required_tables - present)
        if missing_tables:
            report["issues"].append({
                "severity": "high", "code": "review_schema_tables_missing",
                "detail": missing_tables,
            })
            return report

        source_cols = cols(db, "legal_sources")
        doc_cols = cols(db, "legal_documents")
        version_cols = cols(db, "legal_document_versions")
        event_cols = cols(db, "legal_review_events")
        required = {
            "legal_sources": {"source_id", "authority", "source_page", "collection_permission", "commercial_reuse_permission", "permission_evidence", "terms_url"},
            "legal_documents": {"document_id", "source_id", "official_title", "document_type"},
            "legal_document_versions": {"version_id", "document_id", "version_label", "source_url", "original_sha256", "publication_date", "effective_date", "repeal_date", "legal_status", "review_status", "authenticity_verified", "status_verified", "amendment_history_verified", "permission_evidence"},
            "legal_review_events": {"version_id", "review_type", "outcome", "evidence_url", "reviewer", "reviewed_at"},
        }
        actual = {
            "legal_sources": source_cols, "legal_documents": doc_cols,
            "legal_document_versions": version_cols, "legal_review_events": event_cols,
        }
        schema_errors = {
            table: sorted(fields - actual[table]) for table, fields in required.items()
            if fields - actual[table]
        }
        if schema_errors:
            report["issues"].append({
                "severity": "high", "code": "review_schema_columns_missing",
                "detail": schema_errors,
            })
            return report

        source_rows = db.execute(
            "SELECT source_id,authority,source_page,collection_permission,commercial_reuse_permission,"
            "terms_url,permission_evidence FROM legal_sources ORDER BY source_id"
        ).fetchall()
        for source in source_rows:
            row = dict(source)
            reasons = []
            if row["collection_permission"] in (None, "", "unknown"):
                reasons.append("collection_permission_unknown")
            if row["commercial_reuse_permission"] in (None, "", "unknown"):
                reasons.append("commercial_reuse_permission_unknown")
            if not row["terms_url"]:
                reasons.append("terms_url_missing")
            if not row["permission_evidence"]:
                reasons.append("permission_evidence_missing")
            if reasons:
                report["source_permissions"].append({
                    **row, "review_reasons": reasons,
                    "next_action": "Review applicable terms and record scoped permission evidence; do not infer permission from public accessibility.",
                })

        versions = db.execute(
            "SELECT v.version_id,v.document_id,v.version_label,v.source_url,v.original_sha256,"
            "v.publication_date,v.effective_date,v.repeal_date,v.legal_status,v.review_status,"
            "v.authenticity_verified,v.status_verified,v.amendment_history_verified,v.permission_evidence,"
            "d.official_title,d.document_type,d.source_id,s.authority,s.source_page,"
            "s.collection_permission,s.commercial_reuse_permission "
            "FROM legal_document_versions v "
            "JOIN legal_documents d ON d.document_id=v.document_id "
            "JOIN legal_sources s ON s.source_id=d.source_id "
            "ORDER BY v.version_id"
        ).fetchall()
        review_types = (
            "source_authenticity", "extraction_quality", "legal_status",
            "amendment_history", "licensing", "lawyer_approval",
        )
        for version in versions:
            row = dict(version)
            events = [dict(e) for e in db.execute(
                "SELECT review_type,outcome,evidence_url,reviewer,reviewed_at "
                "FROM legal_review_events WHERE version_id=? ORDER BY reviewed_at DESC,review_event_id DESC",
                (row["version_id"],)
            ).fetchall()]
            reasons = []
            if not row["original_sha256"]:
                reasons.append("original_content_hash_missing")
            if not row["publication_date"]:
                reasons.append("publication_date_unknown")
            if not row["effective_date"]:
                reasons.append("effective_date_unknown")
            if row["legal_status"] in (None, "", "unknown", "under_review"):
                reasons.append("legal_status_unresolved")
            if row["review_status"] != "verified":
                reasons.append("version_not_marked_verified")
            if not row["authenticity_verified"]:
                reasons.append("source_authenticity_not_verified")
            if not row["status_verified"]:
                reasons.append("legal_status_not_verified")
            if not row["amendment_history_verified"]:
                reasons.append("amendment_history_not_verified")
            if not row["permission_evidence"]:
                reasons.append("version_permission_evidence_missing")
            for review_type in review_types:
                passing = any(
                    e["review_type"] == review_type and e["outcome"] == "pass" and e["evidence_url"]
                    for e in events
                )
                if not passing:
                    reasons.append("review_evidence_missing:" + review_type)
            if row["collection_permission"] not in ("allowed", "allowed_limited"):
                reasons.append("source_collection_permission_not_confirmed")
            if row["commercial_reuse_permission"] in (None, "", "unknown"):
                reasons.append("source_commercial_reuse_permission_unknown")
            if reasons:
                report["records"].append({
                    **row, "review_reasons": reasons,
                    "review_events": events,
                    "next_action": "Reviewer: inspect the original official instrument and evidence, record scoped review events, and leave unresolved items explicitly unresolved.",
                })

        report["summary"] = {
            "versions_in_queue": len(report["records"]),
            "sources_with_permission_follow_up": len(report["source_permissions"]),
            "versions_scanned": len(versions),
            "sources_scanned": len(source_rows),
        }
        return report
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, type=Path, help="Path to the Legal Copilot SQLite database")
    parser.add_argument("--out", type=Path, help="Write JSON report to this path (default: stdout)")
    args = parser.parse_args()
    try:
        report = review_queue(args.db)
    except (FileNotFoundError, sqlite3.Error) as exc:
        parser.error(str(exc))
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if any(issue["severity"] == "high" for issue in report["issues"]):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
