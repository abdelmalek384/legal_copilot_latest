#!/usr/bin/env python3
"""Pure, side-effect-free planner for privacy-safe case reminders.

This module does not read/write a database, send email, or claim delivery.
Callers must supply events already authorized for the intended recipient.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SUPPORTED_KINDS = {"task", "deadline", "session"}


class ReminderScheduleError(ValueError):
    """Raised when normalized reminder input is invalid."""


def _parse_due_date(value: object, event_id: str) -> date:
    if not isinstance(value, str):
        raise ReminderScheduleError(f"{event_id}: due_date must be an ISO YYYY-MM-DD string")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ReminderScheduleError(f"{event_id}: due_date must be a real date in YYYY-MM-DD form") from exc
    if parsed.isoformat() != value:
        raise ReminderScheduleError(f"{event_id}: due_date must use canonical YYYY-MM-DD form")
    return parsed


def _idempotency_key(scope_id: str, recipient_id: str, kind: str, event_id: str, due_date: str, window: str, lead_days: int = 1) -> str:
    identity = ["case-reminder-v1", scope_id, recipient_id, kind, event_id, due_date, window]
    if window == "due_soon" and lead_days != 1:
        identity.append(lead_days)
    material = json.dumps(
        identity,
        ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def build_reminder_plan(
    events: Iterable[Mapping[str, object]],
    recipient_id: str,
    now: datetime,
    timezone_name: str,
    scope_id: str,
    already_sent: set[str] | None = None,
    lead_days: int | Iterable[int] = 1,
) -> dict:
    """Return a deterministic dry-run plan for configured lead windows and due-day events.

    Required normalized event fields: kind (task/deadline/session), event_id,
    due_date (YYYY-MM-DD), and is_complete (bool). now must be timezone-aware.
    Overdue events share one idempotency window, so daily reruns do not create a
    new key every day. A changed due date creates a new key.
    """
    if not isinstance(recipient_id, str) or not recipient_id.strip():
        raise ReminderScheduleError("recipient_id must be a non-empty string")
    if not isinstance(scope_id, str) or not scope_id.strip():
        raise ReminderScheduleError("scope_id must be a non-empty firm/scope identifier")
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ReminderScheduleError("now must be a timezone-aware datetime")
    if type(lead_days) is int:
        lead_windows = {lead_days}
    else:
        try:
            raw_windows = list(lead_days)
        except TypeError as exc:
            raise ReminderScheduleError("lead_days must be an integer or a collection of integers") from exc
        if not raw_windows:
            raise ReminderScheduleError("lead_days must contain at least one lead window")
        if any(type(value) is not int or not 1 <= value <= 30 for value in raw_windows):
            raise ReminderScheduleError("lead_days values must be integers from 1 through 30")
        lead_windows = set(raw_windows)
    if any(type(value) is not int or not 1 <= value <= 30 for value in lead_windows):
        raise ReminderScheduleError("lead_days values must be integers from 1 through 30")
    try:
        local_zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, TypeError) as exc:
        raise ReminderScheduleError("timezone_name must be a valid IANA timezone") from exc

    sent = set() if already_sent is None else already_sent
    if not isinstance(sent, set) or any(not isinstance(key, str) for key in sent):
        raise ReminderScheduleError("already_sent must be a set of idempotency-key strings")

    local_now = now.astimezone(local_zone)
    local_today = local_now.date()
    prepared = []
    seen = set()
    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            raise ReminderScheduleError(f"event {index}: expected an object")
        kind = event.get("kind")
        if not isinstance(kind, str) or kind not in SUPPORTED_KINDS:
            raise ReminderScheduleError(f"event {index}: kind must be task, deadline, or session")
        raw_id = event.get("event_id")
        if isinstance(raw_id, bool) or not isinstance(raw_id, (str, int)) or not str(raw_id).strip():
            raise ReminderScheduleError(f"event {index}: event_id must be a non-empty string or integer")
        event_id = str(raw_id).strip()
        identity = (kind, event_id)
        if identity in seen:
            raise ReminderScheduleError(f"duplicate event identity: {kind}/{event_id}")
        seen.add(identity)
        is_complete = event.get("is_complete")
        if not isinstance(is_complete, bool):
            raise ReminderScheduleError(f"{kind}/{event_id}: is_complete must be true or false")
        due = _parse_due_date(event.get("due_date"), f"{kind}/{event_id}")
        if is_complete:
            continue

        days_until_due = (due - local_today).days
        if kind == "session":
            if days_until_due != 0:
                continue
            window, lead_value = "due_today", 0
        elif days_until_due in lead_windows:
            window, lead_value = "due_soon", days_until_due
        elif days_until_due == 0:
            window, lead_value = "due_today", 0
        elif days_until_due < 0:
            window, lead_value = "overdue", 0
        else:
            continue

        due_text = due.isoformat()
        key = _idempotency_key(
            scope_id.strip(), recipient_id.strip(), str(kind), event_id, due_text, window, lead_value
        )
        if key in sent:
            continue
        prepared.append({
            "scope_id": scope_id.strip(),
            "recipient_id": recipient_id.strip(),
            "event_type": str(kind),
            "event_id": event_id,
            "due_date": due_text,
            "days_until_due": days_until_due,
            "lead_days": lead_value,
            "window": window,
            "idempotency_key": key,
        })

    prepared.sort(key=lambda item: (item["due_date"], item["event_type"], item["event_id"]))
    return {
        "schema_version": 1,
        "dry_run_only": True,
        "delivery_performed": False,
        "scope_id": scope_id.strip(),
        "recipient_id": recipient_id.strip(),
        "timezone": timezone_name,
        "evaluated_at_local": local_now.isoformat(),
        "planned_count": len(prepared),
        "reminders": prepared,
        "warning": "A planned reminder is not a queued or delivered notification. Delivery, durable deduplication, retries, and audit persistence are not implemented by this module.",
    }



def main(argv: list[str] | None = None) -> int:
    """Run a local JSON-in/JSON-out dry-run; never reads a database or sends messages."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="JSON file with events and optional already_sent idempotency keys")
    parser.add_argument("--recipient-id", required=True)
    parser.add_argument("--scope-id", required=True, help="Firm/scope identifier")
    parser.add_argument("--timezone", required=True, help="IANA timezone, e.g. Africa/Cairo")
    parser.add_argument("--now", help="Optional ISO-8601 timestamp with timezone offset")
    parser.add_argument("--lead-days", type=int, default=1)
    parser.add_argument("--out", type=Path, help="Optional report path; defaults to stdout")
    args = parser.parse_args(argv)

    try:
        if args.out is not None and args.out.resolve() == args.input.resolve():
            raise ReminderScheduleError("--out must not overwrite the input file")
        try:
            data = json.loads(args.input.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ReminderScheduleError("input file is not valid JSON") from exc
        if not isinstance(data, dict):
            raise ReminderScheduleError("input root must be a JSON object")
        events = data.get("events")
        if not isinstance(events, list):
            raise ReminderScheduleError("input must contain an events array")
        already_sent = data.get("already_sent", [])
        if not isinstance(already_sent, list) or any(not isinstance(key, str) for key in already_sent):
            raise ReminderScheduleError("already_sent must be an array of idempotency-key strings")
        if args.now is None:
            now = datetime.now(timezone.utc)
        else:
            raw_now = args.now[:-1] + "+00:00" if args.now.endswith("Z") else args.now
            try:
                now = datetime.fromisoformat(raw_now)
            except ValueError as exc:
                raise ReminderScheduleError("--now must be an ISO-8601 timestamp") from exc
            if now.tzinfo is None or now.utcoffset() is None:
                raise ReminderScheduleError("--now must include a timezone offset")
        report = build_reminder_plan(
            events, args.recipient_id, now, args.timezone, args.scope_id,
            already_sent=set(already_sent), lead_days=args.lead_days,
        )
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.out is None:
            print(rendered, end="")
        else:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(rendered, encoding="utf-8")
        return 0
    except (OSError, UnicodeError, ReminderScheduleError) as exc:
        print(f"Reminder dry-run failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
