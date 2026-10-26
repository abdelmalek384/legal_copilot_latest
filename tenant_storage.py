"""Tenant-aware SQLite connection routing foundation.

This module is not an authentication layer. Callers MUST pass a firm ID that
has already been resolved from the authenticated identity and an active,
server-validated membership. Never pass a request-supplied firm ID directly.

The application is not switched to this provider until the identity contract,
shared legal-corpus boundary, and route inventory are approved and migrated.
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Callable

from tenant_catalog import TenantCatalogError, resolve_tenant_database


class TenantConnectionError(RuntimeError):
    """Raised when a tenant database connection cannot be safely selected."""


CatalogConnectionFactory = Callable[[], sqlite3.Connection]


class TenantSQLiteConnectionRouter:
    """Resolve provisioned firm databases from the control-plane catalog.

    Connections are cached per thread and firm, but the catalog is revalidated
    on every call so disabled, missing, or unprovisioned tenants fail closed.
    The catalog connection is always closed by this router after resolution.
    """

    def __init__(
        self,
        catalog_connection_factory: CatalogConnectionFactory,
        storage_root: str | Path,
        *,
        timeout: float = 30.0,
    ) -> None:
        if not callable(catalog_connection_factory):
            raise TypeError("catalog_connection_factory must be callable")
        if str(storage_root).strip() == "":
            raise ValueError("storage_root must be a non-empty path")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._catalog_connection_factory = catalog_connection_factory
        self._storage_root = Path(storage_root)
        self._timeout = float(timeout)
        self._local = threading.local()

    @staticmethod
    def _validate_firm_id(firm_id: int) -> None:
        if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("trusted firm_id must be a positive integer")

    def connection_for_firm(self, trusted_firm_id: int) -> sqlite3.Connection:
        """Return a thread-local connection for a pre-authorized firm context.

        This method does not authenticate the caller or validate membership.
        The trusted argument is a security precondition, not a substitute for
        request authorization.
        """
        self._validate_firm_id(trusted_firm_id)
        try:
            catalog = self._catalog_connection_factory()
        except Exception as exc:
            # A catalog-open failure is also a failed revalidation. Do not leave
            # a previously cached connection available for later reuse.
            connections = getattr(self._local, "connections", None)
            cached = connections.pop(trusted_firm_id, None) if connections else None
            if cached is not None:
                try:
                    cached[1].close()
                except sqlite3.Error:
                    pass
            raise TenantConnectionError(
                "Tenant catalog is unavailable; refusing cached tenant storage"
            ) from exc

        try:
            try:
                path = resolve_tenant_database(catalog, trusted_firm_id, self._storage_root)
            except (TenantCatalogError, sqlite3.Error) as exc:
                # A disabled or invalid catalog entry must also revoke any
                # connection already cached for this firm on the current thread.
                connections = getattr(self._local, "connections", None)
                cached = connections.pop(trusted_firm_id, None) if connections else None
                if cached is not None:
                    try:
                        cached[1].close()
                    except sqlite3.Error:
                        pass
                raise TenantConnectionError(
                    "Tenant database is not available through the trusted catalog"
                ) from exc
        finally:
            catalog.close()

        connections = getattr(self._local, "connections", None)
        if connections is None:
            connections = {}
            self._local.connections = connections

        cached = connections.get(trusted_firm_id)
        if cached is not None:
            cached_path, connection = cached
            if cached_path == path:
                return connection
            connection.close()
            del connections[trusted_firm_id]

        connection = None
        try:
            connection = sqlite3.connect(str(path), timeout=self._timeout)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
                raise TenantConnectionError(
                    "Tenant database foreign-key enforcement could not be enabled"
                )
            try:
                profile = connection.execute(
                    "SELECT profile FROM database_profile WHERE singleton=1"
                ).fetchone()
            except sqlite3.Error as exc:
                raise TenantConnectionError(
                    "Tenant database is missing its required firm profile binding"
                ) from exc
            if profile is None or profile[0] != "firm":
                raise TenantConnectionError(
                    "Tenant database is not bound to the firm schema profile"
                )
            profile_triggers = {
                row[0]: row[1] for row in connection.execute(
                    "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
                    "AND name IN ('database_profile_no_update','database_profile_no_delete')"
                )
            }

            def has_immutable_profile_guard(sql: str | None, operation: str) -> bool:
                if not isinstance(sql, str):
                    return False
                normalized = " ".join(sql.lower().split())
                return (
                    f"before {operation} on database_profile" in normalized
                    and "raise(abort" in normalized
                    and "database profile binding is immutable" in normalized
                )

            if (
                not has_immutable_profile_guard(
                    profile_triggers.get("database_profile_no_update"), "update"
                )
                or not has_immutable_profile_guard(
                    profile_triggers.get("database_profile_no_delete"), "delete"
                )
            ):
                raise TenantConnectionError(
                    "Tenant database profile binding lacks effective immutable guards"
                )
            try:
                binding = connection.execute(
                    "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
                ).fetchone()
            except sqlite3.Error as exc:
                raise TenantConnectionError(
                    "Tenant database is missing its required firm ID binding"
                ) from exc
            if binding is None or binding[0] != trusted_firm_id:
                raise TenantConnectionError(
                    "Tenant database is bound to a different firm"
                )
            binding_triggers = {
                row[0]: row[1] for row in connection.execute(
                    "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
                    "AND name IN ('tenant_database_binding_no_update','tenant_database_binding_no_delete')"
                )
            }

            def has_immutable_binding_guard(sql: str | None, operation: str) -> bool:
                if not isinstance(sql, str):
                    return False
                normalized = " ".join(sql.lower().split())
                return (
                    f"before {operation} on tenant_database_binding" in normalized
                    and "raise(abort" in normalized
                    and "tenant database firm binding is immutable" in normalized
                )

            if (
                not has_immutable_binding_guard(
                    binding_triggers.get("tenant_database_binding_no_update"), "update"
                )
                or not has_immutable_binding_guard(
                    binding_triggers.get("tenant_database_binding_no_delete"), "delete"
                )
            ):
                raise TenantConnectionError(
                    "Tenant database firm binding lacks effective immutable guards"
                )
        except (sqlite3.Error, TenantConnectionError) as exc:
            if connection is not None:
                try:
                    connection.close()
                except sqlite3.Error:
                    pass
            if isinstance(exc, TenantConnectionError):
                raise
            raise TenantConnectionError(
                "Tenant database is unavailable; refusing fallback to shared storage"
            ) from exc

        connections[trusted_firm_id] = (path, connection)
        return connection

    def close_current_thread(self) -> None:
        """Close all tenant connections owned by the current thread."""
        connections = getattr(self._local, "connections", None)
        if connections is None:
            return
        errors = []
        for _, connection in connections.values():
            try:
                connection.close()
            except sqlite3.Error as exc:
                errors.append(exc)
        del self._local.connections
        if errors:
            raise TenantConnectionError(
                f"Failed to close {len(errors)} tenant database connection(s)"
            ) from errors[0]
