"""Read-only consistency audit for the chunks table and FTS5 search index.

Usage: python scripts/chunks_fts_preflight.py path/to/copilot.db
Exit codes: 0 = no detected FTS anomalies; 1 = review findings; 2 = usage/database error.
The input database is opened read-only by the CLI and this module never writes.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Reuse the application's canonical tokenization so the audit does not drift
# from the values written by add_chunks(). Importing app does not open a DB.
from app import tokens


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {
        row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}


def audit(conn: sqlite3.Connection) -> dict[str, Any]:
    """Return deterministic counts/findings without modifying the connection."""
    tables = _tables(conn)
    findings: list[dict[str, Any]] = []

    def add(code: str, count: int, detail: str) -> None:
        if count:
            findings.append({
                "code": code,
                "severity": "high",
                "count": int(count),
                "detail": detail,
            })

    if "chunks" not in tables:
        add("chunks_table_missing", 1, "The database has no chunks table to reconcile.")
        return {
            "mode": "read_only",
            "chunks_row_count": 0,
            "fts_row_count": 0,
            "finding_count": len(findings),
            "findings": findings,
            "status": "review_required",
        }

    chunk_columns = _columns(conn, "chunks")
    missing_chunk_columns = {"id", "text"} - chunk_columns
    if missing_chunk_columns:
        add(
            "chunks_columns_missing",
            len(missing_chunk_columns),
            f"Required chunks columns are missing: {sorted(missing_chunk_columns)}",
        )
        return {
            "mode": "read_only",
            "chunks_row_count": 0,
            "fts_row_count": 0,
            "finding_count": len(findings),
            "findings": findings,
            "status": "review_required",
        }

    chunk_count = int(conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
    if "chunks_fts" not in tables:
        add(
            "fts_table_missing",
            1,
            "The chunks_fts virtual table is absent; run a reviewed rebuild on a protected copy.",
        )
        return {
            "mode": "read_only",
            "chunks_row_count": chunk_count,
            "fts_row_count": 0,
            "finding_count": len(findings),
            "findings": findings,
            "status": "review_required",
        }

    fts_columns = _columns(conn, "chunks_fts")
    if "norm" not in fts_columns:
        add(
            "fts_norm_column_missing",
            1,
            "The chunks_fts table does not expose the expected norm column.",
        )
        return {
            "mode": "read_only",
            "chunks_row_count": chunk_count,
            "fts_row_count": 0,
            "finding_count": len(findings),
            "findings": findings,
            "status": "review_required",
        }

    fts_count = int(conn.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0])
    missing_rows = 0
    mismatched_rows = 0
    for row in conn.execute(
        "SELECT c.id, c.text, f.rowid, f.norm "
        "FROM chunks AS c LEFT JOIN chunks_fts AS f ON f.rowid=c.id"
    ):
        if row[2] is None:
            missing_rows += 1
            continue
        expected = " ".join(tokens(row[1] or ""))
        if row[3] != expected:
            mismatched_rows += 1

    extra_rows = int(conn.execute(
        "SELECT COUNT(*) FROM chunks_fts AS f "
        "LEFT JOIN chunks AS c ON c.id=f.rowid WHERE c.id IS NULL"
    ).fetchone()[0])

    add(
        "fts_rows_missing",
        missing_rows,
        "Chunks without matching FTS rowids will not be found by full-text search.",
    )
    add(
        "fts_content_mismatch",
        mismatched_rows,
        "FTS text differs from the application's current canonical tokenization.",
    )
    add(
        "fts_rows_orphaned",
        extra_rows,
        "FTS rowids without a matching chunks row may return stale search results.",
    )

    return {
        "mode": "read_only",
        "chunks_row_count": chunk_count,
        "fts_row_count": fts_count,
        "finding_count": len(findings),
        "findings": findings,
        "status": "no_detected_anomalies" if not findings else "review_required",
    }


def audit_path(database: str | Path) -> dict[str, Any]:
    """Open an existing database read-only, run the audit, and close it."""
    path = Path(database).expanduser().resolve(strict=True)
    if not path.is_file():
        raise FileNotFoundError(path)
    uri = path.as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=30)
    try:
        connection.execute("PRAGMA query_only=ON")
        return audit(connection)
    finally:
        connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="Existing SQLite database (read-only)")
    args = parser.parse_args(argv)
    try:
        report = audit_path(args.database)
    except (OSError, sqlite3.Error) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "no_detected_anomalies" else 1


if __name__ == "__main__":
    raise SystemExit(main())
