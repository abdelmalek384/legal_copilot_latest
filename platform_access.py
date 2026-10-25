"""Explicit platform-role checks against the trusted control-plane database."""
from __future__ import annotations

import sqlite3

_PLATFORM_ROLES = frozenset({"platform_admin", "platform_reviewer"})


def has_platform_role(
    connection: sqlite3.Connection, user_id: int, role_name: str
) -> bool:
    """Return whether a global identity has an explicit platform-role assignment.

    Firm membership/role is intentionally not consulted. The connection must
    come from trusted server-side control-plane configuration; database errors
    propagate so callers can fail closed rather than granting access.
    """
    if not isinstance(connection, sqlite3.Connection):
        raise TypeError("trusted control-plane SQLite connection is required")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id must be a positive integer")
    if role_name not in _PLATFORM_ROLES:
        raise ValueError("unsupported platform role")
    return connection.execute(
        "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name=?",
        (user_id, role_name),
    ).fetchone() is not None
