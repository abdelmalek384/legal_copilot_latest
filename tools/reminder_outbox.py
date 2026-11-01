#!/usr/bin/env python3
"""Transactional, tenant-local persistence for privacy-safe reminder plans.

This module never discovers recipients, sends email, or establishes authorization.
Callers must supply a plan produced for an authorized user in the selected firm DB.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Mapping


class ReminderOutboxError(ValueError):
    """Raised when a reminder plan or outbox transition is invalid."""


_EVENT_TYPES = {"task", "deadline", "session"}
_WINDOWS = {"due_soon", "due_today", "overdue"}
_KEY_RE = re.compile(r"^[0-9a-f]{64}$")
_ERROR_RE = re.compile(r"^[a-z0-9_]{1,80}$")


def _utc_now(value: datetime | None = None) -> datetime:
    result = datetime.now(timezone.utc) if value is None else value
    if not isinstance(result, datetime) or result.tzinfo is None or result.utcoffset() is None:
        raise ReminderOutboxError("timestamp must be timezone-aware")
    return result.astimezone(timezone.utc)


def _timestamp(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def _require_outbox(connection: sqlite3.Connection) -> None:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='reminder_deliveries'"
    ).fetchone()
    if row is None:
        raise ReminderOutboxError("durable reminder outbox migration is not installed")


def enqueue_plan(
    connection: sqlite3.Connection,
    plan: Mapping[str, object],
    *,
    firm_id: int,
    recipient_user_id: int,
) -> int:
    """Atomically insert plan rows; repeated scheduler runs are idempotent."""
    if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
        raise ReminderOutboxError("firm_id must be a positive integer")
    if isinstance(recipient_user_id, bool) or not isinstance(recipient_user_id, int) or recipient_user_id <= 0:
        raise ReminderOutboxError("recipient_user_id must be a positive integer")
    if not isinstance(plan, Mapping) or plan.get("dry_run_only") is not True:
        raise ReminderOutboxError("a validated reminder planner result is required")
    if plan.get("delivery_performed") is not False:
        raise ReminderOutboxError("planner result must not claim delivery")
    if plan.get("scope_id") != str(firm_id) or plan.get("recipient_id") != str(recipient_user_id):
        raise ReminderOutboxError("plan scope or recipient does not match the trusted firm/user")
    reminders = plan.get("reminders")
    if not isinstance(reminders, list):
        raise ReminderOutboxError("plan reminders must be a list")

    prepared = []
    seen = set()
    for index, item in enumerate(reminders):
        if not isinstance(item, Mapping):
            raise ReminderOutboxError(f"reminder {index} must be an object")
        key = item.get("idempotency_key")
        kind = item.get("event_type")
        event_id = item.get("event_id")
        due_date = item.get("due_date")
        window = item.get("window")
        lead_days = item.get("lead_days", 1)
        if type(lead_days) is not int or not 0 <= lead_days <= 30:
            raise ReminderOutboxError(f"reminder {index} has an invalid lead_days value")
        if not isinstance(key, str) or not _KEY_RE.fullmatch(key):
            raise ReminderOutboxError(f"reminder {index} has an invalid idempotency key")
        if not isinstance(kind, str) or kind not in _EVENT_TYPES:
            raise ReminderOutboxError(f"reminder {index} has an unsupported event type")
        if isinstance(event_id, bool) or not isinstance(event_id, str) or not event_id.strip():
            raise ReminderOutboxError(f"reminder {index} has an invalid event ID")
        if not isinstance(due_date, str):
            raise ReminderOutboxError(f"reminder {index} has an invalid due date")
        try:
            if datetime.strptime(due_date, "%Y-%m-%d").date().isoformat() != due_date:
                raise ValueError
        except ValueError as exc:
            raise ReminderOutboxError(f"reminder {index} has an invalid due date") from exc
        if not isinstance(window, str) or window not in _WINDOWS:
            raise ReminderOutboxError(f"reminder {index} has an unsupported window")
        if item.get("scope_id") != str(firm_id) or item.get("recipient_id") != str(recipient_user_id):
            raise ReminderOutboxError(f"reminder {index} scope or recipient does not match the trusted firm/user")
        identity = ["case-reminder-v1", str(firm_id), str(recipient_user_id), kind,
                    event_id.strip(), due_date, window]
        if window == "due_soon" and lead_days != 1:
            identity.append(lead_days)
        key_material = json.dumps(
            identity, ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")
        if key != hashlib.sha256(key_material).hexdigest():
            raise ReminderOutboxError(f"reminder {index} idempotency key does not match its event identity")
        if key in seen:
            raise ReminderOutboxError("plan contains duplicate idempotency keys")
        seen.add(key)
        prepared.append((key, recipient_user_id, kind, event_id.strip(), due_date, window, lead_days))

    _require_outbox(connection)
    inserted = 0
    connection.execute("BEGIN IMMEDIATE")
    try:
        for row in prepared:
            before = connection.total_changes
            connection.execute(
                "INSERT OR IGNORE INTO reminder_deliveries "
                "(idempotency_key,recipient_user_id,event_type,event_id,due_date,reminder_window,lead_days) "
                "VALUES(?,?,?,?,?,?,?)",
                row,
            )
            inserted += connection.total_changes - before
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return inserted


def claim_next(
    connection: sqlite3.Connection,
    *,
    now: datetime | None = None,
    lease_seconds: int = 120,
) -> dict | None:
    """Atomically claim one queued row; expired in-flight sends become ambiguous.

    A crashed sender may have submitted to SMTP before dying. Such rows are never
    silently requeued, because doing so could duplicate an already accepted email.
    """
    current = _utc_now(now)
    if type(lease_seconds) is not int or not 15 <= lease_seconds <= 900:
        raise ReminderOutboxError("lease_seconds must be an integer from 15 through 900")
    _require_outbox(connection)
    now_text = _timestamp(current)
    lease_text = _timestamp(current + timedelta(seconds=lease_seconds))
    connection.execute("BEGIN IMMEDIATE")
    try:
        connection.execute(
            "UPDATE reminder_deliveries SET status='ambiguous',lease_until=NULL,"
            "last_error_code='sender_lease_expired',updated_at=? "
            "WHERE status='sending' AND lease_until IS NOT NULL AND lease_until<=?",
            (now_text, now_text),
        )
        row = connection.execute(
            "SELECT * FROM reminder_deliveries WHERE status='queued' "
            "AND (next_attempt_at IS NULL OR next_attempt_at<=?) "
            "ORDER BY created_at,id LIMIT 1",
            (now_text,),
        ).fetchone()
        if row is None:
            connection.commit()
            return None
        updated = connection.execute(
            "UPDATE reminder_deliveries SET status='sending',attempt_count=attempt_count+1,"
            "last_attempt_at=?,lease_until=?,updated_at=? WHERE id=? AND status='queued'",
            (now_text, lease_text, now_text, row["id"]),
        )
        if updated.rowcount != 1:
            connection.rollback()
            return None
        claimed = connection.execute(
            "SELECT * FROM reminder_deliveries WHERE id=?", (row["id"],)
        ).fetchone()
        connection.commit()
        return dict(claimed)
    except Exception:
        connection.rollback()
        raise


def finish_attempt(
    connection: sqlite3.Connection,
    delivery_id: int,
    *,
    result_status: str,
    error_code: str | None = None,
    provider_message_id: str | None = None,
    smtp_attempts: int = 1,
    now: datetime | None = None,
) -> None:
    """Persist the adapter outcome without storing message bodies or provider text."""
    if isinstance(delivery_id, bool) or not isinstance(delivery_id, int) or delivery_id <= 0:
        raise ReminderOutboxError("delivery_id must be a positive integer")
    if result_status not in {"accepted_by_smtp", "failed", "ambiguous"}:
        raise ReminderOutboxError("result_status is invalid")
    if type(smtp_attempts) is not int or not 0 <= smtp_attempts <= 5:
        raise ReminderOutboxError("smtp_attempts must be an integer from 0 through 5")
    if error_code is not None and (not isinstance(error_code, str) or not _ERROR_RE.fullmatch(error_code)):
        raise ReminderOutboxError("error_code must be a sanitized lowercase code")
    if provider_message_id is not None and (
        not isinstance(provider_message_id, str) or len(provider_message_id) > 200
        or any(ord(ch) < 32 or ord(ch) == 127 for ch in provider_message_id)
    ):
        raise ReminderOutboxError("provider_message_id is invalid")
    current = _timestamp(_utc_now(now))
    _require_outbox(connection)
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute(
            "SELECT status,attempt_count,last_attempt_at FROM reminder_deliveries WHERE id=?",
            (delivery_id,),
        ).fetchone()
        if row is None or row["status"] != "sending":
            raise ReminderOutboxError("only an in-flight reminder can be completed")
        changed = connection.execute(
            "UPDATE reminder_deliveries SET status=?,last_error_code=?,provider_message_id=?,"
            "accepted_at=CASE WHEN ?='accepted_by_smtp' THEN ? ELSE accepted_at END,"
            "lease_until=NULL,next_attempt_at=NULL,updated_at=? WHERE id=? AND status='sending'",
            (result_status, error_code, provider_message_id, result_status, current, current, delivery_id),
        )
        if changed.rowcount != 1:
            raise ReminderOutboxError("in-flight reminder changed during completion")
        connection.execute(
            "INSERT INTO reminder_delivery_attempts "
            "(delivery_id,attempt_number,smtp_attempts,status,error_code,provider_message_id,attempted_at,finished_at) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (delivery_id, row["attempt_count"], smtp_attempts, result_status, error_code,
             provider_message_id, row["last_attempt_at"] or current, current),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def retry_failed(
    connection: sqlite3.Connection,
    idempotency_key: str,
    *,
    now: datetime | None = None,
) -> bool:
    """Explicitly requeue a failed row; ambiguous rows require separate reconciliation."""
    if not isinstance(idempotency_key, str) or not _KEY_RE.fullmatch(idempotency_key):
        raise ReminderOutboxError("idempotency_key is invalid")
    current = _timestamp(_utc_now(now))
    _require_outbox(connection)
    connection.execute("BEGIN IMMEDIATE")
    try:
        cursor = connection.execute(
            "UPDATE reminder_deliveries SET status='queued',next_attempt_at=NULL,lease_until=NULL,"
            "last_error_code=NULL,updated_at=? WHERE idempotency_key=? AND status='failed'",
            (current, idempotency_key),
        )
        connection.commit()
        return cursor.rowcount == 1
    except Exception:
        connection.rollback()
        raise
