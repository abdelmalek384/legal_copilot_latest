"""Safely rehearse SQLite migrations against a temporary copy of a database.

The source is opened read-only and copied using SQLite's backup API. All DDL
runs against a disposable staged copy; this tool never migrates the source.
"""
from __future__ import annotations

import argparse
import hashlib
from collections import Counter
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


def _table_row_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Count rows in existing tables using quoted names from sqlite_master."""
    names = [
        str(row[0]) for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    counts: dict[str, int] = {}
    for name in names:
        quoted = '"' + name.replace('"', '""') + '"'
        counts[name] = int(conn.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0])
    return counts



def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    quoted = '"' + table.replace('"', '""') + '"'
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({quoted})")]


def _stable_sqlite_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"blob_hex": value.hex()}
    if isinstance(value, float):
        return {"float_hex": value.hex()}
    return value


def _table_row_hashes(conn: sqlite3.Connection, table: str, columns: list[str]) -> list[str]:
    """Hash rows in shared columns independently of row order."""
    quoted_table = '"' + table.replace('"', '""') + '"'
    quoted_columns = ", ".join('"' + column.replace('"', '""') + '"' for column in columns)
    row_hashes = []
    for row in conn.execute(f"SELECT {quoted_columns} FROM {quoted_table}"):
        payload = json.dumps(
            [_stable_sqlite_value(value) for value in row],
            ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False,
        ).encode("utf-8")
        row_hashes.append(hashlib.sha256(payload).hexdigest())
    return sorted(row_hashes)


def _table_content_hash(conn: sqlite3.Connection, table: str, columns: list[str]) -> str:
    digest = hashlib.sha256()
    for row_hash in _table_row_hashes(conn, table, columns):
        digest.update(row_hash.encode("ascii"))
        digest.update(b"\\n")
    return digest.hexdigest()


def _common_table_content_changes(
    source: sqlite3.Connection, staged: sqlite3.Connection,
) -> list[dict[str, Any]]:
    """Report data changes across columns present before and after migration."""
    source_tables = {
        str(row[0]) for row in source.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    staged_tables = {
        str(row[0]) for row in staged.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    changes = []
    for table in sorted((source_tables & staged_tables) - {"schema_migrations"}):
        source_columns = _table_columns(source, table)
        staged_columns = set(_table_columns(staged, table))
        common_columns = [column for column in source_columns if column in staged_columns]
        if not common_columns:
            continue
        source_row_hashes = Counter(_table_row_hashes(source, table, common_columns))
        staged_row_hashes = Counter(_table_row_hashes(staged, table, common_columns))
        source_hash = _table_content_hash(source, table, common_columns)
        staged_hash = _table_content_hash(staged, table, common_columns)
        # New rows are not treated as rewrites if every pre-existing row survives.
        # A same-count edit or deletion/replacement removes an old row hash and is flagged.
        if any(count > staged_row_hashes[row_hash] for row_hash, count in source_row_hashes.items()):
            changes.append({
                "table": table,
                "columns_compared": common_columns,
                "source_sha256": source_hash,
                "staged_sha256": staged_hash,
            })
    return changes

def rehearse(database: str | Path, migrations_dir: str | Path) -> dict[str, Any]:
    """Apply pending migrations to a disposable copy and report integrity checks."""
    source_path = Path(database)
    if source_path.is_symlink():
        raise ValueError(f"Database path must not be a symlink: {source_path}")
    if not source_path.is_file():
        raise FileNotFoundError(f"Database file not found: {source_path}")
    source_check: list[str]
    source_fk_count: int
    source_row_counts: dict[str, int]
    staged_row_counts: dict[str, int]
    common_table_content_changes: list[dict[str, Any]]
    source = _connect_read_only(source_path)
    try:
        source_check = _quick_check(source)
        source_fk_count = _foreign_key_violation_count(source)
        source_row_counts = _table_row_counts(source)
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
                staged_row_counts = _table_row_counts(rehearsal_db)
                common_table_content_changes = _common_table_content_changes(source, rehearsal_db)
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

    row_count_decreases = [
        {
            "table": table,
            "source_rows": count,
            "staged_rows": staged_row_counts.get(table, 0),
        }
        for table, count in sorted(source_row_counts.items())
        if staged_row_counts.get(table, 0) < count
    ]
    checks_pass = source_check == ["ok"] and staged_check == ["ok"]
    status = (
        "passed"
        if checks_pass and source_fk_count == 0 and staged_fk_count == 0 and not row_count_decreases and not common_table_content_changes
        else "review_required"
    )
    return {
        "mode": "disposable_copy_only",
        "source_modified": False,
        "status": status,
        "source_quick_check": source_check,
        "source_foreign_key_violations": source_fk_count,
        "staged_quick_check": staged_check,
        "staged_foreign_key_violations": staged_fk_count,
        "source_table_row_counts": source_row_counts,
        "staged_table_row_counts": staged_row_counts,
        "row_count_decreases": row_count_decreases,
        "common_table_content_changes": common_table_content_changes,
        "migrations_applied": applied,
        "migration_ledger": ledger,
        "limitations": [
            "This rehearses SQLite migrations only; it does not validate application behavior or tenant isolation.",
            "Changes to data in columns shared by source and staged tables require explicit review; schema-added columns are not treated as data changes.",
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
