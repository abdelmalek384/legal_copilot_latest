"""Safely rehearse SQLite migrations against a temporary copy of a database.

The source is opened read-only and copied using SQLite's backup API. All DDL
runs against a disposable staged copy; this tool never migrates the source.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

from db_migrations import apply_migrations


def _connect_read_only(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _quick_check(conn: sqlite3.Connection) -> list[str]:
    return [str(row[0]) for row in conn.execute("PRAGMA quick_check")]


def _foreign_key_violation_count(conn: sqlite3.Connection) -> int:
    return sum(1 for _ in conn.execute("PRAGMA foreign_key_check"))


def rehearse(database: str | Path, migrations_dir: str | Path) -> dict[str, Any]:
    """Apply pending migrations to a disposable copy and report integrity checks."""
    source_path = Path(database)
    if not source_path.is_file():
        raise FileNotFoundError(f"Database file not found: {source_path}")
    source_check: list[str]
    source_fk_count: int
    source = _connect_read_only(source_path)
    try:
        source_check = _quick_check(source)
        source_fk_count = _foreign_key_violation_count(source)
        with tempfile.TemporaryDirectory(prefix="legal-db-migration-rehearsal-") as tmp:
            staged_path = Path(tmp) / "staged.sqlite3"
            staged = sqlite3.connect(staged_path)
            try:
                source.backup(staged)
                staged.commit()
            finally:
                staged.close()

            rehearsal_db = sqlite3.connect(staged_path)
            rehearsal_db.row_factory = sqlite3.Row
            try:
                applied = apply_migrations(rehearsal_db, migrations_dir)
                staged_check = _quick_check(rehearsal_db)
                staged_fk_count = _foreign_key_violation_count(rehearsal_db)
                ledger = [
                    {"version": int(row["version"]), "name": str(row["name"])}
                    for row in rehearsal_db.execute(
                        "SELECT version, name FROM schema_migrations ORDER BY version"
                    )
                ]
            finally:
                rehearsal_db.close()
    finally:
        source.close()

    checks_pass = source_check == ["ok"] and staged_check == ["ok"]
    status = "passed" if checks_pass and source_fk_count == 0 and staged_fk_count == 0 else "review_required"
    return {
        "mode": "disposable_copy_only",
        "source_modified": False,
        "status": status,
        "source_quick_check": source_check,
        "source_foreign_key_violations": source_fk_count,
        "staged_quick_check": staged_check,
        "staged_foreign_key_violations": staged_fk_count,
        "migrations_applied": applied,
        "migration_ledger": ledger,
        "limitations": [
            "This rehearses SQLite migrations only; it does not validate application behavior or tenant isolation.",
            "A clean rehearsal does not replace a verified backup, restore rehearsal, or deployment-specific rollback plan.",
            "Run against a representative, protected copy and review every reported foreign-key violation."
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="SQLite database to inspect without modifying")
    parser.add_argument(
        "--migrations-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "migrations",
        help="Directory containing versioned SQL migrations",
    )
    args = parser.parse_args(argv)
    try:
        report = rehearse(args.database, args.migrations_dir)
    except (OSError, sqlite3.Error, RuntimeError, ValueError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
