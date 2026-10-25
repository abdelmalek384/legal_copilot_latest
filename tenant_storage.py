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

from tenant_catalog import resolve_tenant_database


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
        catalog = self._catalog_connection_factory()
        try:
            path = resolve_tenant_database(catalog, trusted_firm_id, self._storage_root)
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

        try:
            connection = sqlite3.connect(str(path), timeout=self._timeout)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
                connection.close()
                raise TenantConnectionError(
                    "Tenant database foreign-key enforcement could not be enabled"
                )
        except sqlite3.Error as exc:
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
