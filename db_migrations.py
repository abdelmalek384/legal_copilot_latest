"""Versioned, checksum-verified SQLite migrations.

The runner deliberately accepts an existing connection. Callers must choose the
database explicitly and arrange application quiescence before running DDL.
Each migration is applied atomically and previously applied migration files are
immutable: checksum drift is an error, not an implicit re-run.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
from pathlib import Path
from typing import Iterable

_MIGRATION_NAME = re.compile(r"^(?P<version>[0-9]{4,})_(?P<name>[a-z0-9_]+)\.sql$")


class MigrationError(RuntimeError):
    """Raised when migration files or recorded migration history are unsafe."""


def _migration_files(directory: Path) -> list[tuple[int, str, Path, str]]:
    found: list[tuple[int, str, Path, str]] = []
    versions: set[int] = set()
    for path in sorted(directory.glob("*.sql")):
        match = _MIGRATION_NAME.fullmatch(path.name)
        if not match:
            raise MigrationError(f"Invalid migration filename: {path.name}")
        version = int(match.group("version"))
        if version in versions:
            raise MigrationError(f"Duplicate migration version: {version}")
        versions.add(version)
        sql = path.read_text(encoding="utf-8")
        if not sql.strip():
            raise MigrationError(f"Empty migration: {path.name}")
        found.append((version, path.name, path, sql))
    return sorted(found)


def _statements(sql: str) -> Iterable[str]:
    """Split SQL using SQLite's own completeness parser, preserving trigger bodies."""
    buffer = ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            statement = buffer.strip()
            if statement:
                yield statement
            buffer = ""
    if buffer.strip():
        raise MigrationError("Migration ends with an incomplete SQL statement")


def apply_migrations(connection: sqlite3.Connection, directory: str | Path) -> list[int]:
    """Apply pending migrations; return the versions applied in this invocation."""
    path = Path(directory)
    if not path.is_dir():
        raise MigrationError(f"Migration directory does not exist: {path}")
    migrations = _migration_files(path)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            checksum_sha256 TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    connection.commit()

    recorded = {
        int(row["version"] if isinstance(row, sqlite3.Row) else row[0]):
        (row["name"] if isinstance(row, sqlite3.Row) else row[1],
         row["checksum_sha256"] if isinstance(row, sqlite3.Row) else row[2])
        for row in connection.execute(
            "SELECT version, name, checksum_sha256 FROM schema_migrations"
        )
    }
    available = {version: (name, hashlib.sha256(sql.encode("utf-8")).hexdigest(), sql)
                 for version, name, _file, sql in migrations}
    missing = sorted(set(recorded) - set(available))
    if missing:
        raise MigrationError(f"Applied migration files are missing: {missing}")

    for version, (name, checksum, _sql) in available.items():
        if version in recorded and recorded[version] != (name, checksum):
            raise MigrationError(
                f"Applied migration {version} differs from its recorded name/checksum"
            )

    applied: list[int] = []
    for version, (name, checksum, sql) in available.items():
        if version in recorded:
            continue
        try:
            connection.execute("BEGIN IMMEDIATE")
            for statement in _statements(sql):
                # Do not allow migration files to control transaction boundaries.
                if re.match(r"(?is)^\s*(BEGIN|COMMIT|END|ROLLBACK|SAVEPOINT|RELEASE)\b", statement):
                    raise MigrationError(f"Transaction control is not allowed in {name}")
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_migrations(version,name,checksum_sha256) VALUES(?,?,?)",
                (version, name, checksum),
            )
            connection.commit()
            applied.append(version)
        except Exception:
            connection.rollback()
            raise
    return applied
