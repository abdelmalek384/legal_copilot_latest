"""Read-only row-level evidence manifest for legacy mixed chunk ownership.

The report identifies provenance clues for human review. It never assigns ownership,
changes rows, or exports extracted text. Usage: python scripts/legacy_chunk_evidence_manifest.py DATABASE [--output manifest.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {str(row[0]) for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )}


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    quoted = '"' + table.replace('"', '""') + '"'
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({quoted})")]


def _value(row: sqlite3.Row, columns: set[str], name: str, default=None):
    return row[name] if name in columns else default


def _text_digest(value: Any) -> tuple[str | None, int | None]:
    if value is None:
        return None, None
    raw = value if isinstance(value, bytes) else str(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest(), len(raw)


def build_manifest(conn: sqlite3.Connection) -> dict[str, Any]:
    """Build a deterministic evidence manifest without exposing chunk text."""
    tables = _tables(conn)
    if "chunks" not in tables:
        return {
            "mode": "read_only_evidence_manifest",
            "source_modified": False,
            "status": "review_required",
            "schema_issue": "chunks table is missing",
            "summary": {},
            "records": [],
            "limitations": ["This report does not assign ownership or establish legal-corpus provenance."],
        }

    chunk_columns = set(_columns(conn, "chunks"))
    if "id" not in chunk_columns:
        return {
            "mode": "read_only_evidence_manifest",
            "source_modified": False,
            "status": "review_required",
            "schema_issue": "chunks.id is missing",
            "summary": {},
            "records": [],
            "limitations": ["This report does not assign ownership or establish legal-corpus provenance."],
        }

    cases_by_id: dict[Any, Any] = {}
    cases_schema_available = "cases" in tables and {"id", "firm_id"} <= set(_columns(conn, "cases"))
    if cases_schema_available:
        cases_by_id = {row["id"]: row["firm_id"] for row in conn.execute("SELECT id,firm_id FROM cases")}

    docs_by_id: dict[Any, dict[str, Any]] = {}
    if "docs" in tables and "id" in _columns(conn, "docs"):
        doc_columns = set(_columns(conn, "docs"))
        fields = ["id"] + [name for name in ("case_id", "firm_id", "uploader_user_id", "sha256") if name in doc_columns]
        select = ", ".join('"' + name + '"' for name in fields)
        for row in conn.execute(f"SELECT {select} FROM docs"):
            docs_by_id[row["id"]] = {name: row[name] for name in fields if name != "id"}

    versions_by_id: dict[Any, Any] = {}
    if "legal_document_versions" in tables and "version_id" in _columns(conn, "legal_document_versions"):
        version_columns = set(_columns(conn, "legal_document_versions"))
        fields = ["version_id"] + [name for name in ("document_id", "original_sha256", "legal_status", "review_status") if name in version_columns]
        select = ", ".join('"' + name + '"' for name in fields)
        for row in conn.execute(f"SELECT {select} FROM legal_document_versions"):
            versions_by_id[row["version_id"]] = {name: row[name] for name in fields if name != "version_id"}

    select_columns = [name for name in (
        "id", "case_id", "document_id", "document_version_id", "source", "ref",
        "article", "page", "text", "norm", "verified", "in_force", "as_of"
    ) if name in chunk_columns]
    quoted_columns = ", ".join('"' + name + '"' for name in select_columns)
    records = []
    for row in conn.execute(f"SELECT {quoted_columns} FROM chunks ORDER BY id"):
        case_id = _value(row, chunk_columns, "case_id")
        document_id = _value(row, chunk_columns, "document_id")
        version_id = _value(row, chunk_columns, "document_version_id")
        linked_doc = docs_by_id.get(document_id) if document_id is not None else None
        linked_version = versions_by_id.get(version_id) if version_id is not None else None
        case_firm_id = cases_by_id.get(case_id) if case_id is not None else None
        text_value = _value(row, chunk_columns, "text")
        if text_value is None:
            text_value = _value(row, chunk_columns, "norm")
        text_sha256, text_bytes = _text_digest(text_value)

        if case_id is not None and (not cases_schema_available or case_id not in cases_by_id):
            classification = "case_reference_unresolved"
        elif case_id is not None and cases_by_id.get(case_id) is None:
            classification = "matter_linked_missing_firm"
        elif linked_doc is not None and case_id is not None and linked_doc.get("case_id") is not None and linked_doc["case_id"] != case_id:
            classification = "document_case_mismatch"
        elif linked_doc is not None and case_id is None and linked_doc.get("case_id") is not None:
            classification = "chunk_missing_case_but_document_has_case"
        elif case_id is not None:
            classification = "matter_linked"
        elif document_id is not None and linked_doc is None:
            classification = "document_reference_unresolved"
        elif linked_doc is not None:
            classification = "document_linked_without_chunk_case"
        elif version_id is not None and linked_version is not None:
            classification = "legal_version_linked_candidate_not_auto_shared"
        elif version_id is not None:
            classification = "legal_version_reference_unresolved"
        else:
            classification = "unclassified_no_case_or_document_link"

        needs_review = classification != "matter_linked"
        record = {
            "chunk_id": _value(row, chunk_columns, "id"),
            "classification": classification,
            "requires_human_review": needs_review,
            "case_id": case_id,
            "case_firm_id": case_firm_id,
            "document_id": document_id,
            "linked_document": linked_doc,
            "document_version_id": version_id,
            "linked_legal_version": linked_version,
            "source": _value(row, chunk_columns, "source"),
            "ref": _value(row, chunk_columns, "ref"),
            "article": _value(row, chunk_columns, "article"),
            "page": _value(row, chunk_columns, "page"),
            "verified": _value(row, chunk_columns, "verified"),
            "in_force": _value(row, chunk_columns, "in_force"),
            "as_of": _value(row, chunk_columns, "as_of"),
            "text_sha256": text_sha256,
            "text_byte_length": text_bytes,
        }
        records.append(record)

    counts = Counter(record["classification"] for record in records)
    review_count = sum(1 for record in records if record["requires_human_review"])
    return {
        "mode": "read_only_evidence_manifest",
        "source_modified": False,
        "ownership_assigned": False,
        "status": "review_required" if review_count else "no_detected_anomalies",
        "summary": {
            "chunks_seen": len(records),
            "chunks_requiring_human_review": review_count,
            "classification_counts": dict(sorted(counts.items())),
        },
        "records": records,
        "limitations": [
            "No chunk text is included; SHA-256 and byte length are supplied for record matching.",
            "A legal-version link is only a provenance clue, not proof that a chunk belongs in the shared corpus.",
            "A null case_id is never automatically assigned to the legal corpus or to a firm.",
            "Review this report against trusted source files, upload records, and retention decisions before migration.",
            "This manifest does not audit FTS5 index integrity or prove application route isolation.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="SQLite database to inspect without modifying")
    parser.add_argument("--output", type=Path, help="optional JSON report path; no database writes occur")
    args = parser.parse_args(argv)
    if args.database.is_symlink():
        print(json.dumps({"status": "failed", "error": "database path must not be a symlink"}), file=sys.stderr)
        return 2
    if not args.database.is_file():
        print(json.dumps({"status": "failed", "error": "database file not found"}), file=sys.stderr)
        return 2
    if args.output is not None and args.output.is_symlink():
        print(json.dumps({"status": "failed", "error": "output path must not be a symlink"}), file=sys.stderr)
        return 2
    try:
        uri = args.database.resolve().as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA query_only=ON")
            report = build_manifest(conn)
        finally:
            conn.close()
        rendered = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output is not None:
            args.output.write_text(rendered + "\n", encoding="utf-8")
            print(json.dumps({
                "status": report["status"],
                "output": str(args.output),
                "source_modified": False,
                "summary": report.get("summary", {}),
            }, ensure_ascii=False))
        else:
            print(rendered)
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 1 if report["status"] == "review_required" else 0


if __name__ == "__main__":
    raise SystemExit(main())
