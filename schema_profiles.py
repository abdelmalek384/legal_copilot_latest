"""Profile-aware migration boundary for separate SQLite databases.

This is migration infrastructure, not the application's runtime tenant router.
Each database must be assigned exactly one approved profile (control_plane,
firm, or legal_corpus). Profile migration directories are supplied by the
trusted deployment, never by a request or a tenant catalog filename.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Literal

from db_migrations import MigrationError, apply_migrations

DatabaseProfile = Literal["control_plane", "firm", "legal_corpus"]
_ALLOWED_PROFILES = frozenset({"control_plane", "firm", "legal_corpus"})
_PROFILE_RE = re.compile(r"^[a-z_]+$")


class DatabaseProfileError(RuntimeError):
    """Raised when a database is assigned to the wrong schema profile."""


def apply_profile_migrations(
    connection: sqlite3.Connection,
    profile: DatabaseProfile,
    migrations_root: str | Path,
) -> list[int]:
    """Bind a database to one profile, then apply that profile's migrations.

    The profile marker is deliberately immutable. Reusing a database under a
    different profile fails closed; moving data between profiles requires an
    explicit migration/reconciliation process rather than changing this marker.
    The caller is responsible for selecting the database from trusted server
    configuration and quiescing concurrent writers during schema changes.
    """
    if not isinstance(profile, str) or profile not in _ALLOWED_PROFILES or not _PROFILE_RE.fullmatch(profile):
        raise DatabaseProfileError("Unsupported database profile")

    root = Path(migrations_root).resolve()
    directory = root / profile
    if not directory.is_dir() or directory.resolve().parent != root:
        raise MigrationError(f"Migration directory does not exist for profile: {profile}")

    # SQLite foreign-key enforcement is connection-local and must be enabled
    # before the migration runner opens its transaction.
    connection.execute("PRAGMA foreign_keys = ON")
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise DatabaseProfileError("SQLite foreign-key enforcement could not be enabled")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS database_profile (
            singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
            profile TEXT NOT NULL CHECK(profile IN ('control_plane','firm','legal_corpus')),
            bound_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    row = connection.execute(
        "SELECT profile FROM database_profile WHERE singleton=1"
    ).fetchone()
    if row is None:
        connection.execute(
            "INSERT INTO database_profile(singleton, profile) VALUES(1, ?)",
            (profile,),
        )
        connection.commit()
    elif row[0] != profile:
        raise DatabaseProfileError(
            f"Database is bound to profile {row[0]!r}; refusing profile {profile!r}"
        )

    return apply_migrations(connection, directory)
