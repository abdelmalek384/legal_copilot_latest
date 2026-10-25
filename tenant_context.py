"""Trusted active-firm context resolution for tenant-aware request handlers.

The caller must supply the user object returned by verified server-side session
handling and a server-side membership lookup. Never pass raw request payloads,
headers, paths, or client-provided database references as identity.
This module is deliberately not wired into app routes until the membership
schema and legacy-user reconciliation plan are approved.
"""
from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Any, Callable, Mapping


class FirmContextError(PermissionError):
    """Raised when a trusted active firm context cannot be established."""


@dataclass(frozen=True)
class FirmContext:
    user_id: int
    firm_id: int
    role: str


MembershipLookup = Callable[[int, int], Mapping[str, Any] | None]



def sqlite_membership_lookup(connection: sqlite3.Connection) -> MembershipLookup:
    """Build a fail-closed lookup over the control-plane membership schema.

    The supplied connection must target the trusted control-plane database and
    be owned by the current request/thread. The function never accepts a
    database path or firm mapping from the client.
    """
    if not isinstance(connection, sqlite3.Connection):
        raise TypeError("trusted control-plane SQLite connection is required")

    # Prevent accidentally treating a firm database as the source of
    # authoritative memberships. The profile marker and its immutable guards
    # must identify this connection as the control-plane database.
    try:
        profile = connection.execute(
            "SELECT profile FROM database_profile WHERE singleton=1"
        ).fetchone()
        profile_triggers = {
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
        or profile_triggers != {"database_profile_no_update", "database_profile_no_delete"}
    ):
        raise ValueError("SQLite connection is not bound to the trusted control-plane profile")

    def lookup(user_id: int, firm_id: int) -> Mapping[str, Any] | None:
        row = connection.execute(
            """
            SELECT fm.status, fm.firm_role, u.status, f.status
            FROM firm_memberships fm
            JOIN firms f ON f.id=fm.firm_id
            JOIN users u ON u.id=fm.user_id
            WHERE fm.user_id=? AND fm.firm_id=?
            """,
            (user_id, firm_id),
        ).fetchone()
        if row is None:
            return None
        membership_status, role, user_status, firm_status = row
        # Access requires an active membership, enabled identity, and active
        # firm lifecycle state; any inactive prerequisite fails closed.
        status = membership_status
        if status == "active" and user_status != "active":
            status = user_status
        if status == "active" and firm_status != "active":
            status = firm_status
        return {"status": status, "role": role}

    return lookup


def resolve_firm_context(
    authenticated_user: Mapping[str, Any] | None,
    requested_firm_id: int | None,
    membership_lookup: MembershipLookup,
) -> FirmContext:
    """Validate a requested firm against an authenticated identity's membership.

    authenticated_user must come from verified server-side session handling.
    membership_lookup must query authoritative server-side membership state and
    return a row containing status and role. This primitive intentionally fails
    closed if identity or membership state is incomplete. It does not authenticate
    sessions or query the database itself.
    """
    if not isinstance(authenticated_user, Mapping):
        raise FirmContextError("authenticated identity is required")

    user_id = authenticated_user.get("id")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        raise FirmContextError("authenticated identity is invalid")

    if isinstance(requested_firm_id, bool) or not isinstance(requested_firm_id, int) or requested_firm_id <= 0:
        raise FirmContextError("a valid firm context is required")

    if not callable(membership_lookup):
        raise FirmContextError("trusted membership lookup is unavailable")

    try:
        membership = membership_lookup(user_id, requested_firm_id)
    except Exception as exc:
        raise FirmContextError("firm membership could not be verified") from exc

    if not isinstance(membership, Mapping):
        raise FirmContextError("active firm membership is required")
    if membership.get("status") != "active":
        raise FirmContextError("active firm membership is required")

    role = membership.get("role")
    if not isinstance(role, str) or role.strip() not in {"admin", "lawyer", "junior"}:
        raise FirmContextError("firm membership role is invalid")

    return FirmContext(user_id=user_id, firm_id=requested_firm_id, role=role.strip())
