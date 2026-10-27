#!/usr/bin/env python3
"""Operator-run, tenant-isolated deadline reminder scheduler.

Dry-run is the default and performs no database writes or email delivery.
Use --send only after SMTP, public-origin, recipient, and delivery policies are
configured and reviewed. SMTP acceptance is not proof of inbox delivery.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from database_runtime import DatabaseRuntime, DatabaseRuntimeError
from tools.reminder_email import ReminderEmailError, SMTPConfig, send_reminder_email
from tools.reminder_outbox import (
    ReminderOutboxError, claim_next, enqueue_plan, finish_attempt, retry_failed,
)
from tools.reminder_schedule import ReminderScheduleError, build_reminder_plan


def _parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    try:
        result = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ReminderScheduleError("--now must be an ISO timestamp with a timezone offset") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ReminderScheduleError("--now must include a timezone offset")
    return result


def _date_only(value: object) -> str | None:
    if not isinstance(value, str) or len(value) < 10:
        return None
    candidate = value[:10]
    try:
        if datetime.strptime(candidate, "%Y-%m-%d").date().isoformat() != candidate:
            return None
    except ValueError:
        return None
    return candidate


def _active_recipients(control: sqlite3.Connection, firm_id: int) -> dict[int, dict]:
    rows = control.execute(
        "SELECT u.id,u.email_display,fm.firm_role FROM users u "
        "JOIN firm_memberships fm ON fm.user_id=u.id "
        "WHERE fm.firm_id=? AND fm.status='active' AND u.status='active' "
        "ORDER BY u.id",
        (firm_id,),
    ).fetchall()
    return {int(row["id"]): {"email": row["email_display"], "role": row["firm_role"]}
            for row in rows}


def _case_member(tenant: sqlite3.Connection, case_id: int, user_id: int) -> bool:
    return tenant.execute(
        "SELECT 1 FROM members WHERE case_id=? AND user_id=?", (case_id, user_id)
    ).fetchone() is not None


def _events_for_recipients(
    tenant: sqlite3.Connection, recipients: Mapping[int, Mapping[str, object]]
) -> dict[int, list[dict]]:
    result: dict[int, list[dict]] = {user_id: [] for user_id in recipients}

    for row in tenant.execute(
        "SELECT id,case_id,assignee,due,status FROM tasks "
        "WHERE due IS NOT NULL AND COALESCE(status,'open')<>'done' ORDER BY id"
    ).fetchall():
        user_id = row["assignee"]
        due = _date_only(row["due"])
        if user_id is None or user_id not in recipients or due is None:
            continue
        if recipients[user_id]["role"] != "admin" and not _case_member(tenant, row["case_id"], user_id):
            continue
        result[user_id].append({
            "kind": "task", "event_id": str(row["id"]), "due_date": due,
            "is_complete": False,
        })

    for row in tenant.execute(
        "SELECT id,case_id,created_by,due,status FROM deadlines "
        "WHERE due IS NOT NULL AND COALESCE(status,'open')<>'done' ORDER BY id"
    ).fetchall():
        user_id = row["created_by"]
        due = _date_only(row["due"])
        if user_id is None or user_id not in recipients or due is None:
            continue
        if recipients[user_id]["role"] != "admin" and not _case_member(tenant, row["case_id"], user_id):
            continue
        result[user_id].append({
            "kind": "deadline", "event_id": str(row["id"]), "due_date": due,
            "is_complete": False,
        })

    for row in tenant.execute(
        "SELECT id,case_id,date,done FROM sessions WHERE date IS NOT NULL AND COALESCE(done,0)=0 ORDER BY id"
    ).fetchall():
        due = _date_only(row["date"])
        if due is None:
            continue
        for user_id in recipients:
            # Court-session reminders go only to explicit case members; firm-admin
            # visibility alone does not subscribe an administrator to every session.
            if _case_member(tenant, row["case_id"], user_id):
                result[user_id].append({
                    "kind": "session", "event_id": str(row["id"]), "due_date": due,
                    "is_complete": False,
                })

    return {user_id: events for user_id, events in result.items() if events}


def _still_authorized(
    tenant: sqlite3.Connection,
    control: sqlite3.Connection,
    firm_id: int,
    delivery: Mapping[str, object],
) -> tuple[str | None, str | None]:
    user_id = int(delivery["recipient_user_id"])
    membership = control.execute(
        "SELECT u.email_display,u.status,fm.status AS membership_status,fm.firm_role "
        "FROM users u JOIN firm_memberships fm ON fm.user_id=u.id "
        "JOIN firms f ON f.id=fm.firm_id "
        "WHERE u.id=? AND fm.firm_id=? AND f.status='active'",
        (user_id, firm_id),
    ).fetchone()
    if membership is None or membership["status"] != "active" or membership["membership_status"] != "active":
        return None, "recipient_not_active"

    kind = str(delivery["event_type"])
    event_id = int(delivery["event_id"])
    due = str(delivery["due_date"])
    if kind == "task":
        event = tenant.execute(
            "SELECT case_id,assignee,due,status FROM tasks WHERE id=?", (event_id,)
        ).fetchone()
        if event is None or event["assignee"] != user_id or (event["status"] or "open") == "done" or _date_only(event["due"]) != due:
            return None, "event_no_longer_eligible"
    elif kind == "deadline":
        event = tenant.execute(
            "SELECT case_id,created_by,due,status FROM deadlines WHERE id=?", (event_id,)
        ).fetchone()
        if event is None or event["created_by"] != user_id or (event["status"] or "open") == "done" or _date_only(event["due"]) != due:
            return None, "event_no_longer_eligible"
    elif kind == "session":
        event = tenant.execute(
            "SELECT case_id,date,done FROM sessions WHERE id=?", (event_id,)
        ).fetchone()
        if event is None or bool(event["done"]) or _date_only(event["date"]) != due:
            return None, "event_no_longer_eligible"
        if not _case_member(tenant, event["case_id"], user_id):
            return None, "recipient_not_authorized"
        return membership["email_display"], None
    else:
        return None, "unsupported_event_type"

    if membership["firm_role"] != "admin" and not _case_member(tenant, event["case_id"], user_id):
        return None, "recipient_not_authorized"
    return membership["email_display"], None


def run_scheduler(
    runtime: DatabaseRuntime,
    *,
    now: datetime,
    timezone_name: str,
    lead_days: int = 1,
    send: bool = False,
    smtp_config: SMTPConfig | None = None,
    app_url: str | None = None,
    max_send: int = 100,
) -> dict:
    control = runtime.control_connection()
    summary = {
        "mode": "send" if send else "dry_run",
        "evaluated_at": now.isoformat(),
        "timezone": timezone_name,
        "firms_scanned": 0,
        "plans_built": 0,
        "reminders_planned": 0,
        "reminders_queued": 0,
        "smtp_accepted": 0,
        "failed": 0,
        "ambiguous": 0,
        "skipped_unauthorized_or_stale": 0,
        "warnings": [
            "A planned reminder is not a delivery.",
            "SMTP acceptance is not confirmation of inbox delivery.",
            "Notifications omit matter names and facts; date reminders are not legal-deadline calculations.",
        ],
    }
    firms = control.execute(
        "SELECT id FROM firms WHERE status='active' ORDER BY id"
    ).fetchall()
    for firm_row in firms:
        firm_id = int(firm_row["id"])
        try:
            tenant = runtime._tenant_router.connection_for_firm(firm_id)
        except Exception:
            # An unavailable or unprovisioned tenant must not stop other firms.
            summary["warnings"].append(f"firm_{firm_id}: tenant database unavailable; skipped")
            continue
        summary["firms_scanned"] += 1
        recipients = _active_recipients(control, firm_id)
        events_by_user = _events_for_recipients(tenant, recipients)
        if not send:
            for user_id, events in events_by_user.items():
                plan = build_reminder_plan(
                    events, str(user_id), now, timezone_name, str(firm_id), lead_days=lead_days
                )
                summary["plans_built"] += 1
                summary["reminders_planned"] += plan["planned_count"]
            continue

        for user_id, events in events_by_user.items():
            plan = build_reminder_plan(
                events, str(user_id), now, timezone_name, str(firm_id), lead_days=lead_days
            )
            summary["plans_built"] += 1
            summary["reminders_planned"] += plan["planned_count"]
            summary["reminders_queued"] += enqueue_plan(
                tenant, plan, firm_id=firm_id, recipient_user_id=user_id
            )

        sent_this_firm = 0
        while sent_this_firm < max_send:
            delivery = claim_next(tenant, now=now)
            if delivery is None:
                break
            sent_this_firm += 1
            recipient, denial = _still_authorized(tenant, control, firm_id, delivery)
            if denial:
                finish_attempt(
                    tenant, int(delivery["id"]), result_status="failed",
                    error_code=denial, now=now,
                )
                summary["skipped_unauthorized_or_stale"] += 1
                summary["failed"] += 1
                continue
            payload = {
                "event_type": delivery["event_type"],
                "due_date": delivery["due_date"],
                "window": delivery["reminder_window"],
            }
            outcome = send_reminder_email(
                payload, recipient, app_url or "", smtp_config, enabled=True,
            )
            if outcome["status"] == "accepted_by_smtp":
                finish_attempt(tenant, int(delivery["id"]), result_status="accepted_by_smtp", now=now)
                summary["smtp_accepted"] += 1
            else:
                status = "ambiguous" if outcome.get("error_code") == "smtp_connection_failure" else "failed"
                finish_attempt(
                    tenant, int(delivery["id"]), result_status=status,
                    error_code=outcome.get("error_code") or "smtp_delivery_failure", now=now,
                )
                if status == "ambiguous":
                    summary["ambiguous"] += 1
                else:
                    summary["failed"] += 1
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send", action="store_true",
                        help="explicitly enable SMTP delivery; otherwise this is a read-only dry run")
    parser.add_argument("--timezone", default="Africa/Cairo", help="IANA timezone (default: Africa/Cairo)")
    parser.add_argument("--now", help="optional ISO timestamp with timezone offset")
    parser.add_argument("--lead-days", type=int, default=1)
    parser.add_argument("--max-send", type=int, default=100, help="maximum queued messages to claim per firm")
    parser.add_argument("--retry-failed-key", help="explicitly requeue one failed idempotency key in each firm")
    parser.add_argument("--out", type=Path, help="write sanitized JSON summary to this path")
    args = parser.parse_args(argv)
    runtime = None
    try:
        now = _parse_now(args.now)
        if type(args.lead_days) is not int or not 1 <= args.lead_days <= 30:
            raise ReminderScheduleError("--lead-days must be between 1 and 30")
        if type(args.max_send) is not int or not 1 <= args.max_send <= 1000:
            raise ReminderOutboxError("--max-send must be between 1 and 1000")
        if args.send:
            smtp_config = SMTPConfig.from_env()
            app_url = __import__("os").environ.get("COPILOT_PUBLIC_ORIGIN", "").strip()
            if not app_url:
                raise ReminderEmailError("COPILOT_PUBLIC_ORIGIN must be configured before sending reminders")
        else:
            smtp_config, app_url = None, None

        runtime = DatabaseRuntime.from_env()
        runtime.initialize()
        if args.retry_failed_key:
            if not args.send:
                raise ReminderOutboxError("--retry-failed-key requires --send and explicit delivery configuration")
            control = runtime.control_connection()
            requeued = 0
            for row in control.execute("SELECT id FROM firms WHERE status='active' ORDER BY id").fetchall():
                try:
                    tenant = runtime._tenant_router.connection_for_firm(int(row["id"]))
                    requeued += int(retry_failed(tenant, args.retry_failed_key, now=now))
                except ReminderOutboxError:
                    continue
            result = {"mode": "retry_failed", "requeued": requeued,
                      "warning": "Only failed rows are requeued; ambiguous rows require reconciliation."}
        else:
            result = run_scheduler(
                runtime, now=now, timezone_name=args.timezone, lead_days=args.lead_days,
                send=args.send, smtp_config=smtp_config, app_url=app_url, max_send=args.max_send,
            )
        output = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)
        if args.out:
            args.out.write_text(output + "\n", encoding="utf-8")
        else:
            print(output)
        return 0
    except (DatabaseRuntimeError, ReminderOutboxError, ReminderEmailError, ReminderScheduleError,
            sqlite3.Error, OSError, ValueError) as exc:
        print("Reminder scheduler failed: " + str(exc), file=sys.stderr)
        return 2
    finally:
        if runtime is not None:
            runtime.close_current_thread()


if __name__ == "__main__":
    raise SystemExit(main())
