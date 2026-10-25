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

    def lookup(user_id: int, firm_id: int) -> Mapping[str, Any] | None:
        row = connection.execute(
            "SELECT status, firm_role FROM firm_memberships WHERE user_id=? AND firm_id=?",
            (user_id, firm_id),
        ).fetchone()
        if row is None:
            return None
        return {"status": row[0], "role": row[1]}

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
