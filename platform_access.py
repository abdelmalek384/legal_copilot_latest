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
    if not isinstance(role_name, str) or role_name not in _PLATFORM_ROLES:
        raise ValueError("unsupported platform role")
    # A wrong-profile connection must never become the authority for platform
    # privileges. Require the immutable control-plane marker before querying.
    try:
        profile = connection.execute(
            "SELECT profile FROM database_profile WHERE singleton=1"
        ).fetchone()
        triggers = {
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger' "
                "AND name IN ('database_profile_no_update','database_profile_no_delete')"
            )
        }
    except sqlite3.Error as exc:
        raise ValueError("SQLite connection is not bound to the trusted control-plane profile") from exc
    if (
        profile is None
        or profile[0] != "control_plane"
        or triggers != {"database_profile_no_update", "database_profile_no_delete"}
    ):
        raise ValueError("SQLite connection is not bound to the trusted control-plane profile")

    # A disabled global identity must not retain platform privileges through a
    # stale role assignment. Role checks are evaluated against current state.
    return connection.execute(
        """
        SELECT 1
        FROM user_platform_roles AS r
        JOIN users AS u ON u.id = r.user_id
        WHERE r.user_id=? AND r.role_name=? AND u.status='active'
        """,
        (user_id, role_name),
    ).fetchone() is not None
