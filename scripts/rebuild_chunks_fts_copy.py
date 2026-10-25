"""Rebuild the chunks_fts index on a new copy, never on the source database.

Usage: PYTHONPATH=. python scripts/rebuild_chunks_fts_copy.py SOURCE.sqlite3 OUTPUT.sqlite3
The output path must not already exist. Review the JSON report and the rebuilt copy
before planning any operational replacement.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

from app import tokens
from scripts.chunks_fts_preflight import audit


def _readonly_connection(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.execute("PRAGMA query_only=ON")
    return connection


def _quick_check(connection: sqlite3.Connection) -> list[str]:
    return [str(row[0]) for row in connection.execute("PRAGMA quick_check")]


def _foreign_key_violations(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    return [
        {"table": str(row[0]), "rowid": row[1], "parent": str(row[2]), "fkid": int(row[3])}
        for row in connection.execute("PRAGMA foreign_key_check")
    ]


def rebuild_copy(source: str | Path, output: str | Path) -> dict[str, Any]:
    """Copy an existing DB and rebuild FTS in the new output file only."""
    source_path = Path(source).expanduser().resolve(strict=True)
    if not source_path.is_file():
        raise FileNotFoundError(source_path)

    requested_output = Path(output).expanduser()
    parent = requested_output.parent.resolve(strict=True)
    output_path = parent / requested_output.name
    if output_path.resolve(strict=False) == source_path:
        raise ValueError("Output path must differ from source database")
    if output_path.exists():
        raise FileExistsError(f"Output already exists; refusing to overwrite: {output_path}")

    # Exclusive creation prevents accidental overwrite if another process races
    # this check. Restrictive permissions are applied before SQLite opens it.
    fd = os.open(output_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    source_connection = None
    target_connection = None
    try:
        source_connection = _readonly_connection(source_path)
        source_check = _quick_check(source_connection)
        source_fk = _foreign_key_violations(source_connection)
        source_tables = {
            str(row[0]) for row in source_connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "chunks" not in source_tables:
            raise ValueError("Source database has no chunks table")
        chunk_columns = {
            str(row[1]) for row in source_connection.execute("PRAGMA table_info(chunks)")
        }
        if not {"id", "text"} <= chunk_columns:
            raise ValueError("Source chunks table must contain id and text columns")

        target_connection = sqlite3.connect(output_path, timeout=30)
        source_connection.backup(target_connection)
        target_connection.commit()

        # Rebuild only on the disposable copy. Dropping the virtual table also
        # removes its FTS5 shadow tables; any rebuild error aborts the copy.
        target_connection.execute("DROP TABLE IF EXISTS chunks_fts")
        target_connection.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(norm)")
        rows = target_connection.execute(
            "SELECT id, text FROM chunks ORDER BY id"
        ).fetchall()
        target_connection.executemany(
            "INSERT INTO chunks_fts(rowid, norm) VALUES(?, ?)",
            [(int(row[0]), " ".join(tokens(row[1] or ""))) for row in rows],
        )
        target_connection.commit()

        staged_check = _quick_check(target_connection)
        staged_fk = _foreign_key_violations(target_connection)
        fts_report = audit(target_connection)
        source_chunk_count = int(source_connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
        staged_chunk_count = int(target_connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
        checks_pass = (
            source_check == ["ok"]
            and staged_check == ["ok"]
            and not source_fk
            and not staged_fk
            and source_chunk_count == staged_chunk_count
            and fts_report["status"] == "no_detected_anomalies"
        )
        return {
            "mode": "rebuild_new_copy_only",
            "source_modified": False,
            "source_path": str(source_path),
            "output_path": str(output_path),
            "status": "passed" if checks_pass else "review_required",
            "source_quick_check": source_check,
            "staged_quick_check": staged_check,
            "source_foreign_key_violations": len(source_fk),
            "staged_foreign_key_violations": len(staged_fk),
            "source_chunks": source_chunk_count,
            "staged_chunks": staged_chunk_count,
            "fts_audit": fts_report,
            "limitations": [
                "The source is never modified; all FTS DDL and writes target the new output copy.",
                "A passing report does not establish that chunk text is legally accurate, complete, current, or correctly assigned to a firm.",
                "Do not replace an operational database until the output is reviewed, separately backed up, and a deployment/restore plan is approved.",
            ],
        }
    except Exception:
        if target_connection is not None:
            target_connection.close()
            target_connection = None
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass
        raise
    finally:
        if target_connection is not None:
            target_connection.close()
        if source_connection is not None:
            source_connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Existing source SQLite database (read-only)")
    parser.add_argument("output", type=Path, help="New output path; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        report = rebuild_copy(args.source, args.output)
    except (OSError, sqlite3.Error, RuntimeError, ValueError) as exc:
        print(json.dumps({"status": "error", "source_modified": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
