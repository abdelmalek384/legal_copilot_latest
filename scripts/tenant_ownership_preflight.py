"""Read-only preflight audit for legacy SQLite tenant ownership.

Usage: python scripts/tenant_ownership_preflight.py path/to/copilot.db
Exit codes: 0 = no detected ownership anomalies; 1 = anomalies found; 2 = usage/database error.
This tool never changes the input database.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
    )}


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    # Table names originate only from sqlite_master, not user input.
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}


def _count(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> int:
    return int(conn.execute(sql, params).fetchone()[0])


def audit(conn: sqlite3.Connection) -> dict[str, Any]:
    """Return deterministic counts/findings without writing to the database."""
    tables = _tables(conn)
    findings: list[dict[str, Any]] = []

    def add(code: str, severity: str, count: int, detail: str) -> None:
        if count:
            findings.append({"code": code, "severity": severity, "count": count, "detail": detail})

    # Do not report "clean" for an empty or structurally incomplete database:
    # ownership checks are meaningful only when core tables and key columns exist.
    required_core_columns = {
        "firms": {"id"},
        "users": {"id", "firm_id"},
        "cases": {"id", "firm_id"},
    }
    schema_issues = False
    for table, required_columns in required_core_columns.items():
        if table not in tables:
            add(
                "core_schema_table_missing", "critical", 1,
                f"Required ownership table {table!r} is missing; this database cannot be certified by the ownership preflight.",
            )
            schema_issues = True
            continue
        missing_columns = required_columns - _columns(conn, table)
        if missing_columns:
            add(
                "core_schema_columns_missing", "critical", len(missing_columns),
                f"Required columns are missing from {table!r}: {sorted(missing_columns)}.",
            )
            schema_issues = True
    if schema_issues:
        findings.sort(key=lambda item: (item["severity"], item["code"]))
        return {
            "mode": "read_only",
            "database_tables_seen": sorted(tables),
            "findings": findings,
            "finding_count": len(findings),
            "status": "review_required",
            "limitations": [
                "Core schema is incomplete, so ownership checks could not be fully evaluated.",
                "No records are assigned, repaired, deleted, or migrated by this tool.",
            ],
        }

    firms = "firms" in tables
    if "users" in tables and "firm_id" in _columns(conn, "users"):
        add("users_missing_firm", "critical",
            _count(conn, "SELECT COUNT(*) FROM users WHERE firm_id IS NULL"),
            "Users without an explicit firm assignment must be quarantined, not assigned a default.")
        if firms:
            add("users_unknown_firm", "critical",
                _count(conn, "SELECT COUNT(*) FROM users u LEFT JOIN firms f ON f.id=u.firm_id WHERE u.firm_id IS NOT NULL AND f.id IS NULL"),
                "User firm_id does not resolve to a firms row.")
    if "cases" in tables and "firm_id" in _columns(conn, "cases"):
        add("cases_missing_firm", "critical",
            _count(conn, "SELECT COUNT(*) FROM cases WHERE firm_id IS NULL"),
            "Cases without explicit ownership must be quarantined, not assigned a default.")
        if firms:
            add("cases_unknown_firm", "critical",
                _count(conn, "SELECT COUNT(*) FROM cases c LEFT JOIN firms f ON f.id=c.firm_id WHERE c.firm_id IS NOT NULL AND f.id IS NULL"),
                "Case firm_id does not resolve to a firms row.")
    if {"users", "cases", "members"} <= tables:
        if {"firm_id"} <= _columns(conn, "users") and {"firm_id"} <= _columns(conn, "cases"):
            add("cross_firm_membership", "critical",
                _count(conn, "SELECT COUNT(*) FROM members m JOIN users u ON u.id=m.user_id JOIN cases c ON c.id=m.case_id WHERE u.firm_id IS NOT c.firm_id"),
                "A member user and their case belong to different firms.")
            add("orphan_membership_user", "high",
                _count(conn, "SELECT COUNT(*) FROM members m LEFT JOIN users u ON u.id=m.user_id WHERE u.id IS NULL"),
                "Membership points to a missing user.")
            add("orphan_membership_case", "high",
                _count(conn, "SELECT COUNT(*) FROM members m LEFT JOIN cases c ON c.id=m.case_id WHERE c.id IS NULL"),
                "Membership points to a missing case.")
    if {"docs", "cases"} <= tables and {"case_id", "firm_id"} <= _columns(conn, "docs") and "firm_id" in _columns(conn, "cases"):
        add("docs_missing_firm", "critical",
            _count(conn, "SELECT COUNT(*) FROM docs WHERE firm_id IS NULL"),
            "Document ownership is missing.")
        add("docs_case_missing", "high",
            _count(conn, "SELECT COUNT(*) FROM docs d LEFT JOIN cases c ON c.id=d.case_id WHERE d.case_id IS NOT NULL AND c.id IS NULL"),
            "Document references a missing case.")
        add("docs_case_unlinked", "high",
            _count(conn, "SELECT COUNT(*) FROM docs WHERE case_id IS NULL"),
            "Document metadata has no parent case; establish whether it is valid shared material or an incomplete matter upload.")
        add("docs_case_firm_mismatch", "critical",
            _count(conn, "SELECT COUNT(*) FROM docs d JOIN cases c ON c.id=d.case_id WHERE d.firm_id IS NOT NULL AND c.firm_id IS NOT NULL AND d.firm_id IS NOT c.firm_id"),
            "Document firm_id differs from its parent case.")
    if "docs" in tables and "users" in tables:
        doc_cols = _columns(conn, "docs")
        user_cols = _columns(conn, "users")
        if {"uploader_user_id", "firm_id"} <= doc_cols and "firm_id" in user_cols:
            add("docs_uploader_missing_user", "high",
                _count(conn, "SELECT COUNT(*) FROM docs d LEFT JOIN users u ON u.id=d.uploader_user_id WHERE d.uploader_user_id IS NOT NULL AND u.id IS NULL"),
                "Document uploader_user_id points to a missing user.")
            add("docs_uploader_firm_mismatch", "critical",
                _count(conn, "SELECT COUNT(*) FROM docs d JOIN users u ON u.id=d.uploader_user_id WHERE d.uploader_user_id IS NOT NULL AND d.firm_id IS NOT NULL AND u.firm_id IS NOT NULL AND d.firm_id IS NOT u.firm_id"),
                "Document firm differs from the uploader's firm; verify uploader identity and document ownership before migration.")

    if "document_extraction_reviews" in tables:
        review_cols = _columns(conn, "document_extraction_reviews")
        if "document_id" in review_cols and "docs" in tables:
            add("document_review_document_missing", "high",
                _count(conn, "SELECT COUNT(*) FROM document_extraction_reviews r LEFT JOIN docs d ON d.id=r.document_id WHERE d.id IS NULL"),
                "Extraction review references a missing document.")
            if {"firm_id"} <= review_cols and "firm_id" in _columns(conn, "docs"):
                add("document_review_document_firm_mismatch", "critical",
                    _count(conn, "SELECT COUNT(*) FROM document_extraction_reviews r JOIN docs d ON d.id=r.document_id WHERE r.firm_id IS NOT d.firm_id"),
                    "Extraction review firm differs from its document firm.")
        if "case_id" in review_cols and "cases" in tables:
            add("document_review_case_missing", "high",
                _count(conn, "SELECT COUNT(*) FROM document_extraction_reviews r LEFT JOIN cases c ON c.id=r.case_id WHERE c.id IS NULL"),
                "Extraction review references a missing matter.")
            if "firm_id" in review_cols and "firm_id" in _columns(conn, "cases"):
                add("document_review_case_firm_mismatch", "critical",
                    _count(conn, "SELECT COUNT(*) FROM document_extraction_reviews r JOIN cases c ON c.id=r.case_id WHERE r.firm_id IS NOT c.firm_id"),
                    "Extraction review firm differs from its matter firm.")
        if "reviewer_user_id" in review_cols and "users" in tables:
            add("document_review_reviewer_missing", "high",
                _count(conn, "SELECT COUNT(*) FROM document_extraction_reviews r LEFT JOIN users u ON u.id=r.reviewer_user_id WHERE u.id IS NULL"),
                "Extraction review references a missing reviewer.")
            if "firm_id" in review_cols and "firm_id" in _columns(conn, "users"):
                add("document_review_reviewer_firm_mismatch", "critical",
                    _count(conn, "SELECT COUNT(*) FROM document_extraction_reviews r JOIN users u ON u.id=r.reviewer_user_id WHERE r.firm_id IS NOT u.firm_id"),
                    "Extraction review firm differs from the reviewer's firm.")
        if "chunk_id" in review_cols and "chunks" in tables:
            add("document_review_chunk_missing", "high",
                _count(conn, "SELECT COUNT(*) FROM document_extraction_reviews r LEFT JOIN chunks ch ON ch.id=r.chunk_id WHERE ch.id IS NULL"),
                "Extraction review references a missing extracted chunk.")
            if {"case_id", "document_id"} <= review_cols and {"case_id", "document_id"} <= _columns(conn, "chunks"):
                add("document_review_chunk_scope_mismatch", "critical",
                    _count(conn, "SELECT COUNT(*) FROM document_extraction_reviews r JOIN chunks ch ON ch.id=r.chunk_id WHERE r.case_id IS NOT ch.case_id OR r.document_id IS NOT ch.document_id"),
                    "Extraction review matter/document scope differs from its chunk.")

    if "case_deletion_audit" in tables and "users" in tables:
        audit_cols = _columns(conn, "case_deletion_audit")
        user_cols = _columns(conn, "users")
        if {"firm_id", "actor_user_id"} <= audit_cols and "firm_id" in user_cols:
            add("deletion_audit_actor_missing", "high",
                _count(conn, "SELECT COUNT(*) FROM case_deletion_audit a LEFT JOIN users u ON u.id=a.actor_user_id WHERE a.actor_user_id IS NOT NULL AND u.id IS NULL"),
                "Case deletion audit references a missing actor.")
            add("deletion_audit_actor_firm_mismatch", "critical",
                _count(conn, "SELECT COUNT(*) FROM case_deletion_audit a JOIN users u ON u.id=a.actor_user_id WHERE a.firm_id IS NOT u.firm_id"),
                "Case deletion audit firm differs from the actor's firm.")

    if "chunks" in tables:
        cols = _columns(conn, "chunks")
        if "case_id" in cols:
            add("chunks_case_missing", "high",
                _count(conn, "SELECT COUNT(*) FROM chunks ch LEFT JOIN cases c ON c.id=ch.case_id WHERE ch.case_id IS NOT NULL AND c.id IS NULL"),
                "Matter chunk references a missing case.")
            if "document_id" in cols and "docs" in tables:
                add("chunks_document_missing", "high",
                    _count(conn, "SELECT COUNT(*) FROM chunks ch LEFT JOIN docs d ON d.id=ch.document_id WHERE ch.document_id IS NOT NULL AND d.id IS NULL"),
                    "Chunk references a missing document.")
                if "case_id" in _columns(conn, "docs"):
                    add("chunks_document_case_mismatch", "critical",
                        _count(conn, "SELECT COUNT(*) FROM chunks ch JOIN docs d ON d.id=ch.document_id WHERE ch.document_id IS NOT NULL AND ch.case_id IS NOT d.case_id"),
                        "Chunk and document have different case ownership.")
            add("chunks_unclassified_shared", "review",
                _count(conn, "SELECT COUNT(*) FROM chunks WHERE case_id IS NULL"),
                "NULL case_id may mean shared legal corpus, but must be verified against corpus provenance before migration.")
    if "research_conversations" in tables:
        research_cols = _columns(conn, "research_conversations")
        if "user_id" in research_cols and "users" in tables:
            add("research_owner_missing_user", "high",
                _count(conn, "SELECT COUNT(*) FROM research_conversations rc LEFT JOIN users u ON u.id=rc.user_id WHERE rc.user_id IS NOT NULL AND u.id IS NULL"),
                "Research conversation owner points to a missing user.")
            add("research_owner_unassigned", "high",
                _count(conn, "SELECT COUNT(*) FROM research_conversations WHERE user_id IS NULL"),
                "Research conversation has no explicit owner; establish ownership from trusted evidence.")
            if "firm_id" in research_cols and "firm_id" in _columns(conn, "users"):
                add("research_owner_firm_mismatch", "critical",
                    _count(conn, "SELECT COUNT(*) FROM research_conversations rc JOIN users u ON u.id=rc.user_id WHERE rc.firm_id IS NOT u.firm_id"),
                    "Research conversation firm differs from its owner's current firm.")
        if "firm_id" in research_cols:
            add("research_missing_firm", "critical",
                _count(conn, "SELECT COUNT(*) FROM research_conversations WHERE firm_id IS NULL"),
                "Research conversation has no explicit firm ownership.")
            if "firms" in tables and "id" in _columns(conn, "firms"):
                add("research_unknown_firm", "critical",
                    _count(conn, "SELECT COUNT(*) FROM research_conversations rc LEFT JOIN firms f ON f.id=rc.firm_id WHERE rc.firm_id IS NOT NULL AND f.id IS NULL"),
                    "Research conversation firm_id does not resolve to a firms row.")
    if "case_deletion_audit" in tables and "firm_id" in _columns(conn, "case_deletion_audit"):
        add("deletion_audit_missing_firm", "critical",
            _count(conn, "SELECT COUNT(*) FROM case_deletion_audit WHERE firm_id IS NULL"),
            "Deletion audit snapshots need explicit firm ownership.")

    # Matter child tables do not currently carry firm_id consistently. Their
    # parent case must exist, and application access must always authorize that
    # parent before reading or mutating a child record.
    for table in ("notes", "deadlines", "fees", "tasks", "events", "sessions"):
        if table in tables and "case_id" in _columns(conn, table) and "cases" in tables:
            add(f"orphan_{table}_case", "high",
                _count(conn, f"SELECT COUNT(*) FROM {table} child LEFT JOIN cases c ON c.id=child.case_id WHERE child.case_id IS NOT NULL AND c.id IS NULL"),
                f"{table} contains rows whose parent case does not exist.")
            add(f"unlinked_{table}_case", "high",
                _count(conn, f"SELECT COUNT(*) FROM {table} WHERE case_id IS NULL"),
                f"{table} contains rows with no parent case; do not assign ownership without trusted evidence.")

    findings.sort(key=lambda item: (item["severity"], item["code"]))
    return {
        "mode": "read_only",
        "database_tables_seen": sorted(tables),
        "findings": findings,
        "finding_count": len(findings),
        "status": "review_required" if findings else "no_detected_anomalies",
        "limitations": [
            "A clean report is not proof of tenant isolation or authorization correctness.",
            "Rows with chunks.case_id IS NULL require provenance review; they are not automatically trusted as shared corpus.",
            "This checks the supplied SQLite file only, not external jobs, files, backups, object storage, or deployment configuration.",
            "No records are assigned, repaired, deleted, or migrated by this tool."
        ]
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="SQLite database file to inspect (read-only)")
    args = parser.parse_args(argv)
    # Do not silently follow a caller-supplied symlink to another database.
    # This preflight is often used against sensitive legacy files; the path
    # being inspected must be an explicitly selected regular file.
    if args.database.is_symlink():
        print(json.dumps({"error": "database path must not be a symlink", "path": str(args.database)}), file=sys.stderr)
        return 2
    if not args.database.is_file():
        print(json.dumps({"error": "database file not found", "path": str(args.database)}), file=sys.stderr)
        return 2
    try:
        uri = args.database.resolve().as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA query_only=ON")
            report = audit(conn)
        finally:
            conn.close()
    except sqlite3.Error as exc:
        print(json.dumps({"error": "could not inspect database", "detail": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["finding_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
