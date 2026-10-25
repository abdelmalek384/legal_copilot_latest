"""Trusted server-side catalog for database-per-firm routing.

This module is infrastructure only. It must not be called with a tenant ID or
database path taken directly from an HTTP request. Authentication and active
membership must resolve the trusted firm_id before database resolution is used.
"""
from __future__ import annotations

import os
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Callable

_FILENAME = re.compile(r"^tenant-(?P<firm_id>[1-9][0-9]*)-(?P<nonce>[0-9a-f]{32})\.sqlite3$")


class TenantCatalogError(RuntimeError):
    """Raised when tenant catalog state or storage mapping is unsafe."""


def initialize_catalog(connection: sqlite3.Connection) -> None:
    """Validate and initialize the migration-managed control-plane catalog.

    The firms table and tenant catalog migrations are the schema authority.
    This helper must not silently create a weaker catalog without a firm FK.
    """
    if connection.in_transaction:
        raise TenantCatalogError("Initialize the tenant catalog outside an active transaction")
    connection.execute("PRAGMA foreign_keys = ON")
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise TenantCatalogError("Control-plane foreign-key enforcement could not be enabled")
    tables = {
        row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    if "firms" not in tables:
        raise TenantCatalogError(
            "Control-plane firms table must be created by migrations before catalog initialization"
        )
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tenant_database_catalog (
            firm_id INTEGER PRIMARY KEY CHECK(firm_id > 0)
                REFERENCES firms(id) ON DELETE RESTRICT,
            database_file TEXT UNIQUE,
            status TEXT NOT NULL CHECK(status IN ('provisioning','provisioned','failed','disabled')),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_error_code TEXT
        )
    """)
    foreign_keys = connection.execute(
        "PRAGMA foreign_key_list(tenant_database_catalog)"
    ).fetchall()
    if not any(row[2] == "firms" and row[3] == "firm_id" and row[4] == "id" for row in foreign_keys):
        raise TenantCatalogError(
            "Tenant catalog is missing its firm ownership constraint; apply control-plane migrations"
        )
    # A declared FK does not prove that existing rows satisfy it: SQLite can
    # contain violations from a prior connection that had foreign_keys OFF.
    # Refuse to resolve any tenant until catalog ownership is reconciled.
    violations = connection.execute(
        "PRAGMA foreign_key_check(tenant_database_catalog)"
    ).fetchall()
    if violations:
        raise TenantCatalogError(
            "Tenant catalog contains invalid firm ownership references; reconcile before use"
        )
    connection.commit()


def _storage_root_path(storage_root: str | Path, *, create: bool = False) -> Path:
    """Validate the configured storage root before resolving it.

    Calling resolve() first would erase evidence that the configured root itself
    is a symlink. Reject that mapping for both provisioning and resolution.
    """
    raw_root = Path(storage_root).expanduser()
    if raw_root.is_symlink():
        raise TenantCatalogError("Tenant storage root must not be a symlink")
    if create:
        raw_root.mkdir(parents=True, exist_ok=True)
    if raw_root.is_symlink() or not raw_root.is_dir():
        raise TenantCatalogError("Tenant storage root must be a real directory")
    return raw_root.resolve()


def _safe_database_path(root: Path, firm_id: int, filename: str) -> Path:
    match = _FILENAME.fullmatch(filename)
    if not match or int(match.group("firm_id")) != firm_id:
        raise TenantCatalogError("Tenant catalog contains an invalid database reference")
    if root.is_symlink():
        raise TenantCatalogError("Tenant storage root must not be a symlink")
    resolved_root = root.resolve()
    if not resolved_root.is_dir():
        raise TenantCatalogError("Tenant storage root must be a real directory")
    raw_candidate = resolved_root / filename
    # Check the directory entry before resolve(): resolving first would erase
    # evidence that the catalog filename itself is a symlink to another tenant.
    if raw_candidate.is_symlink():
        raise TenantCatalogError("Tenant database reference must not be a symlink")
    candidate = raw_candidate.resolve()
    if candidate.parent != resolved_root:
        raise TenantCatalogError("Tenant database path escapes its configured storage root")
    return candidate


def provision_tenant_database(
    catalog: sqlite3.Connection,
    firm_id: int,
    storage_root: str | Path,
    initialize_database: Callable[[sqlite3.Connection], None],
) -> Path:
    """Provision one firm database with exclusive file creation and safe retries.

    The caller must supply a trusted firm ID and an initializer that builds a
    complete tenant schema. This function does not migrate application tables
    or create a firm identity itself.
    """
    if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
        raise ValueError("firm_id must be a positive integer")
    if not callable(initialize_database):
        raise TypeError("initialize_database must be callable")

    initialize_catalog(catalog)
    root = _storage_root_path(storage_root, create=True)

    catalog.execute("BEGIN IMMEDIATE")
    try:
        existing = catalog.execute(
            "SELECT database_file, status FROM tenant_database_catalog WHERE firm_id=?",
            (firm_id,),
        ).fetchone()
        if existing and existing[1] == "provisioned":
            filename = existing[0]
            if not filename:
                raise TenantCatalogError("Provisioned tenant has no database reference")
            path = _safe_database_path(root, firm_id, filename)
            if not path.is_file():
                raise TenantCatalogError("Provisioned tenant database is missing")
            catalog.commit()
            return path
        if existing and existing[1] in ("provisioning", "disabled"):
            raise TenantCatalogError(f"Tenant cannot be provisioned while status is {existing[1]}")

        filename = f"tenant-{firm_id}-{uuid.uuid4().hex}.sqlite3"
        path = _safe_database_path(root, firm_id, filename)
        if existing:
            catalog.execute(
                "UPDATE tenant_database_catalog SET database_file=?, status='provisioning', "
                "updated_at=datetime('now'), last_error_code=NULL WHERE firm_id=?",
                (filename, firm_id),
            )
        else:
            catalog.execute(
                "INSERT INTO tenant_database_catalog(firm_id,database_file,status) "
                "VALUES(?,?,'provisioning')",
                (firm_id, filename),
            )
        catalog.commit()
    except Exception:
        catalog.rollback()
        raise

    created = False
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
        created = True
        try:
            os.chmod(path, 0o600)
        except OSError:
            # Some platforms do not support POSIX file modes; deployment must
            # enforce equivalent filesystem ACLs there.
            pass

        tenant = sqlite3.connect(str(path), timeout=30)
        try:
            # SQLite disables FK enforcement by default on each connection.
            # Enable it before running tenant schema/data initialization.
            tenant.execute("PRAGMA foreign_keys=ON")
            initialize_database(tenant)
            tenant.commit()
            integrity = tenant.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise TenantCatalogError("New tenant database failed integrity check")
            foreign_key_violations = tenant.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_key_violations:
                raise TenantCatalogError(
                    "New tenant database failed foreign-key validation "
                    f"({len(foreign_key_violations)} violation(s))"
                )
        finally:
            tenant.close()

        catalog.execute("BEGIN IMMEDIATE")
        catalog.execute(
            "UPDATE tenant_database_catalog SET status='provisioned', "
            "updated_at=datetime('now'), last_error_code=NULL WHERE firm_id=? AND status='provisioning'",
            (firm_id,),
        )
        if catalog.execute("SELECT changes()").fetchone()[0] != 1:
            raise TenantCatalogError("Tenant catalog state changed during provisioning")
        catalog.commit()
        return path
    except Exception:
        if catalog.in_transaction:
            catalog.rollback()
        if created:
            for suffix in ("", "-wal", "-shm", "-journal"):
                try:
                    Path(str(path) + suffix).unlink(missing_ok=True)
                except OSError:
                    pass
        catalog.execute(
            "UPDATE tenant_database_catalog SET database_file=NULL, status='failed', "
            "updated_at=datetime('now'), last_error_code='provisioning_failed' WHERE firm_id=?",
            (firm_id,),
        )
        catalog.commit()
        raise


def resolve_tenant_database(
    catalog: sqlite3.Connection, firm_id: int, storage_root: str | Path
) -> Path:
    """Resolve only an active, provisioned catalog entry; never accept a raw path."""
    if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
        raise ValueError("firm_id must be a positive integer")
    root = _storage_root_path(storage_root)
    initialize_catalog(catalog)
    row = catalog.execute(
        "SELECT database_file, status FROM tenant_database_catalog WHERE firm_id=?",
        (firm_id,),
    ).fetchone()
    if row is None or row[1] != "provisioned" or not row[0]:
        raise TenantCatalogError("Tenant database is not provisioned")
    path = _safe_database_path(root, firm_id, row[0])
    if not path.is_file():
        raise TenantCatalogError("Provisioned tenant database is missing")
    return path
