"""Versioned, checksum-verified SQLite migrations.

The runner deliberately accepts an existing connection. Callers must choose the
database explicitly and arrange application quiescence before running DDL.
Each migration is applied atomically and previously applied migration files are
immutable: checksum drift is an error, not an implicit re-run.
"""
from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import stat
from pathlib import Path
from typing import Iterable

_MIGRATION_NAME = re.compile(r"^(?P<version>[0-9]{4,})_(?P<name>[a-z0-9_]+)\.sql$")


class MigrationError(RuntimeError):
    """Raised when migration files or recorded migration history are unsafe."""


def read_migration_file(path: Path) -> str:
    """Read executable migration SQL without following links or blocking on special files."""
    if path.is_symlink():
        raise MigrationError(f"Migration file must not be a symlink: {path.name}")

    # O_NONBLOCK prevents a malicious or accidental FIFO from hanging startup;
    # O_NOFOLLOW closes the symlink race on platforms that support it. fstat
    # validates the opened object itself, not merely the path checked above.
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(path, flags)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise MigrationError(f"Migration file must be a regular file: {path.name}")
        if metadata.st_size > 5_000_000:
            raise MigrationError(f"Migration file exceeds the 5 MB safety limit: {path.name}")
        stream = os.fdopen(descriptor, "rb")
        descriptor = None  # ownership transferred to the stream
        with stream:
            data = stream.read(5_000_001)
        if len(data) > 5_000_000:
            raise MigrationError(f"Migration file exceeds the 5 MB safety limit: {path.name}")
        return data.decode("utf-8")
    except MigrationError:
        raise
    except (OSError, UnicodeError) as exc:
        raise MigrationError(f"Migration file could not be read safely: {path.name}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _migration_files(directory: Path) -> list[tuple[int, str, Path, str]]:
    found: list[tuple[int, str, Path, str]] = []
    versions: set[int] = set()
    for path in sorted(directory.glob("*.sql")):
        # Preserve the specific symlink rejection before resolving its target.
        if path.is_symlink():
            raise MigrationError(f"Migration file must not be a symlink: {path.name}")
        # Migration SQL is executable schema input; reject all other special files too.
        if path.resolve().parent != directory.resolve():
            raise MigrationError(f"Migration file escapes its directory: {path.name}")
        match = _MIGRATION_NAME.fullmatch(path.name)
        if not match:
            raise MigrationError(f"Invalid migration filename: {path.name}")
        version = int(match.group("version"))
        if version in versions:
            raise MigrationError(f"Duplicate migration version: {version}")
        versions.add(version)
        sql = read_migration_file(path)
        if not sql.strip():
            raise MigrationError(f"Empty migration: {path.name}")
        found.append((version, path.name, path, sql))
    return sorted(found)


def _statements(sql: str) -> Iterable[str]:
    """Split at complete statement terminators, including multiple per line.

    SQLite's completeness parser keeps semicolons inside trigger bodies from
    ending the statement early, while character-wise scanning supports compact
    migration files containing several ordinary statements on one line.
    """
    buffer = ""
    for char in sql:
        buffer += char
        if char == ";" and sqlite3.complete_statement(buffer):
            statement = buffer.strip()
            if statement:
                yield statement
            buffer = ""
    if buffer.strip():
        non_comments = [
            line for line in buffer.splitlines()
            if line.strip() and not line.lstrip().startswith("--")
        ]
        if non_comments:
            raise MigrationError("Migration ends with an incomplete SQL statement")


_CONDITIONAL_ADD_COLUMN = re.compile(
    r"^\s*--\s*@add-column-if-missing\s+([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*$",
    re.IGNORECASE,
)
_ADD_COLUMN_STATEMENT = re.compile(
    r"(?is)^\s*ALTER\s+TABLE\s+([A-Za-z_][A-Za-z0-9_]*)\s+ADD\s+COLUMN\s+([A-Za-z_][A-Za-z0-9_]*)\b"
)


def _migration_operations(sql: str):
    """Yield SQL statements and guarded ADD COLUMN operations in file order.

    A guarded operation is declared by a comment directive immediately before
    its ALTER TABLE statement. The raw file, including directives, remains
    checksum-protected by the migration ledger. Statement terminators are
    scanned character by character so multiple statements per line work while
    SQLite's parser keeps trigger bodies intact.
    """
    buffer = ""
    pending_column: tuple[str, str] | None = None
    for line in sql.splitlines(keepends=True):
        directive = _CONDITIONAL_ADD_COLUMN.fullmatch(line.rstrip("\r\n"))
        if directive:
            if pending_column is not None:
                raise MigrationError("Conditional column directive has no ALTER TABLE statement")
            if buffer.strip():
                non_comments = [
                    item for item in buffer.splitlines()
                    if item.strip() and not item.lstrip().startswith("--")
                ]
                if non_comments:
                    raise MigrationError("Conditional column directive must precede its ALTER TABLE statement")
                buffer = ""
            pending_column = (directive.group(1), directive.group(2))
            continue

        for char in line:
            buffer += char
            if char != ";" or not sqlite3.complete_statement(buffer):
                continue
            statement = buffer.strip()
            if statement:
                if pending_column is None:
                    yield ("sql", statement)
                else:
                    alter = _ADD_COLUMN_STATEMENT.match(statement)
                    if (
                        alter is None
                        or alter.group(1).lower() != pending_column[0].lower()
                        or alter.group(2).lower() != pending_column[1].lower()
                    ):
                        raise MigrationError(
                            "Conditional column directive must match the following ALTER TABLE statement"
                        )
                    yield ("add_column_if_missing", pending_column[0], pending_column[1], statement)
                    pending_column = None
            buffer = ""

    if buffer.strip():
        non_comments = [
            line for line in buffer.splitlines()
            if line.strip() and not line.lstrip().startswith("--")
        ]
        if non_comments:
            raise MigrationError("Migration ends with an incomplete SQL statement")
    if pending_column is not None:
        raise MigrationError("Conditional column directive has no ALTER TABLE statement")


def apply_migrations(connection: sqlite3.Connection, directory: str | Path) -> list[int]:
    """Apply pending migrations; return the versions applied in this invocation."""
    path = Path(directory)
    if path.is_symlink():
        raise MigrationError(f"Migration directory must not be a symlink: {path}")
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

    # Recorded history must be a prefix of the migrations available in this
    # checkout. Otherwise a newly added lower version could be applied after
    # a higher version was already recorded, violating migration order.
    available_versions = sorted(available)
    if recorded:
        latest_recorded = max(recorded)
        expected_prefix = [
            version for version in available_versions if version <= latest_recorded
        ]
        actual_recorded = sorted(recorded)
        if actual_recorded != expected_prefix:
            raise MigrationError(
                "Applied migration history is not an ordered prefix: "
                f"recorded {actual_recorded}, expected {expected_prefix}"
            )

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
            # Another process may have applied this version after the initial
            # ledger snapshot. Recheck under the write lock so concurrent app
            # startups do not execute the same migration twice.
            current = connection.execute(
                "SELECT name, checksum_sha256 FROM schema_migrations WHERE version=?",
                (version,),
            ).fetchone()
            if current is not None:
                current_name = current["name"] if isinstance(current, sqlite3.Row) else current[0]
                current_checksum = current["checksum_sha256"] if isinstance(current, sqlite3.Row) else current[1]
                if (current_name, current_checksum) != (name, checksum):
                    raise MigrationError(
                        f"Applied migration {version} differs from its recorded name/checksum"
                    )
                connection.commit()
                continue

            for operation in _migration_operations(sql):
                if operation[0] == "add_column_if_missing":
                    _kind, table, column, statement = operation
                    # SQLite identifiers are case-insensitive. Legacy schemas may
                    # use a different case than the migration directive, so compare
                    # normalized names to avoid duplicate-column ALTER failures.
                    columns = {
                        str(row[1]).casefold()
                        for row in connection.execute(f"PRAGMA table_info({table})")
                    }
                    if not columns:
                        raise MigrationError(
                            f"Conditional column migration references missing table {table}"
                        )
                    if column.casefold() not in columns:
                        connection.execute(statement)
                    continue

                statement = operation[1]
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
