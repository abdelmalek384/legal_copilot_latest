#!/usr/bin/env python3
"""Operator-run, tenant-isolated deadline reminder scheduler.

Dry-run is the default and performs no database writes or email delivery.
Use --send only after SMTP, public-origin, recipient, and delivery policies are
configured and reviewed. SMTP acceptance is not proof of inbox delivery.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from database_runtime import DatabaseRuntime, DatabaseRuntimeError
from tenant_storage import TenantSQLiteConnectionRouter
from tools.reminder_email import ReminderEmailError, SMTPConfig, send_reminder_email
from tools.reminder_outbox import (
    ReminderOutboxError, claim_next, enqueue_plan, finish_attempt, retry_failed,
)
from tools.reminder_schedule import ReminderScheduleError, build_reminder_plan

class _ReadOnlyReminderRuntime:
    """Read-only view of an existing database runtime for dry-run and status.

    It deliberately skips DatabaseRuntime.initialize(), which is a provisioning
    and migration entry point. SQL writes are disabled on every returned
    connection; tenant routing still uses the trusted firm catalog and router
    validation before a connection is exposed.
    """

    def __init__(self, runtime: DatabaseRuntime) -> None:
        self.paths = runtime.paths
        self.timeout = runtime.timeout
        self._local = threading.local()
        self._router = TenantSQLiteConnectionRouter(
            self._new_catalog_connection, self.paths.tenant_root,
            timeout=self.timeout,
        )
        self._tenant_router = self

    def _new_catalog_connection(self) -> sqlite3.Connection:
        path = self.paths.control_plane
        DatabaseRuntime._validate_profile_storage(path, "control-plane")
        connection = sqlite3.connect(
            path.resolve().as_uri() + "?mode=ro", uri=True, timeout=self.timeout
        )
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA query_only=ON")
            if connection.execute("PRAGMA query_only").fetchone()[0] != 1:
                raise DatabaseRuntimeError("Read-only control-plane mode could not be enforced")
            return connection
        except Exception:
            connection.close()
            raise

    def control_connection(self) -> sqlite3.Connection:
        connection = getattr(self._local, "control", None)
        if connection is None:
            connection = self._new_catalog_connection()
            self._local.control = connection
        return connection

    def connection_for_firm(self, firm_id: int) -> sqlite3.Connection:
        connection = self._router.connection_for_firm(firm_id)
        connection.execute("PRAGMA query_only=ON")
        if connection.execute("PRAGMA query_only").fetchone()[0] != 1:
            self._router.revoke_firm_connection(firm_id)
            raise DatabaseRuntimeError("Read-only tenant mode could not be enforced")
        return connection

    def close_current_thread(self) -> None:
        connection = getattr(self._local, "control", None)
        if connection is not None:
            connection.close()
            del self._local.control
        self._router.close_current_thread()




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


_DEFAULT_REMINDER_PREFERENCES = {
    "email_enabled": 1, "deadline_7_days": 1, "deadline_3_days": 1,
    "deadline_1_day": 1, "deadline_day_of": 1, "deadline_overdue": 1,
    "session_day_of": 1, "task_reminders": 1,
}


def _reminder_preferences(tenant: sqlite3.Connection, user_id: int) -> dict[str, int]:
    try:
        row = tenant.execute(
            "SELECT email_enabled,deadline_7_days,deadline_3_days,deadline_1_day,"
            "deadline_day_of,deadline_overdue,session_day_of,task_reminders "
            "FROM reminder_preferences WHERE user_id=?", (user_id,)
        ).fetchone()
    except sqlite3.Error:
        return dict(_DEFAULT_REMINDER_PREFERENCES)
    if row is None:
        return dict(_DEFAULT_REMINDER_PREFERENCES)
    return {key: int(row[key]) for key in _DEFAULT_REMINDER_PREFERENCES}


def _preference_allows_event(event: Mapping[str, object], preferences: Mapping[str, int],
                             local_today, lead_windows: set[int]) -> bool:
    if not preferences.get("email_enabled", 0):
        return False
    due = _date_only(event.get("due_date"))
    if due is None:
        return False
    days = (datetime.strptime(due, "%Y-%m-%d").date() - local_today).days
    kind = event.get("kind")
    if kind == "session":
        return days == 0 and bool(preferences.get("session_day_of", 0))
    if kind == "task":
        return bool(preferences.get("task_reminders", 0)) and (
            days in lead_windows or days <= 0
        )
    if kind == "deadline":
        if days == 7:
            return bool(preferences.get("deadline_7_days", 0))
        if days == 3:
            return bool(preferences.get("deadline_3_days", 0))
        if days == 1:
            return bool(preferences.get("deadline_1_day", 0))
        if days == 0:
            return bool(preferences.get("deadline_day_of", 0))
        if days < 0:
            return bool(preferences.get("deadline_overdue", 0))
    return False


def _filter_events_by_preferences(events, preferences, now, timezone_name, lead_days):
    if isinstance(lead_days, int):
        lead_windows = {lead_days}
    else:
        lead_windows = set(lead_days)
    local_today = now.astimezone(ZoneInfo(timezone_name)).date()
    return [
        event for event in events
        if _preference_allows_event(event, preferences, local_today, lead_windows)
    ]


def _preference_allows_delivery(delivery: Mapping[str, object], preferences: Mapping[str, int]) -> bool:
    if not preferences.get("email_enabled", 0):
        return False
    kind = delivery.get("event_type")
    window = delivery.get("reminder_window")
    lead = delivery.get("lead_days", 1)
    if kind == "session":
        return window == "due_today" and bool(preferences.get("session_day_of", 0))
    if kind == "task":
        return bool(preferences.get("task_reminders", 0))
    if kind == "deadline":
        if window == "due_today":
            return bool(preferences.get("deadline_day_of", 0))
        if window == "overdue":
            return bool(preferences.get("deadline_overdue", 0))
        return bool(preferences.get({7: "deadline_7_days", 3: "deadline_3_days", 1: "deadline_1_day"}.get(lead, ""), 0))
    return False


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
    if not _preference_allows_delivery(delivery, _reminder_preferences(tenant, user_id)):
        return None, "reminder_preference_changed"

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
    lead_days: int | tuple[int, ...] = (7, 3, 1),
    send: bool = False,
    smtp_config: SMTPConfig | None = None,
    app_url: str | None = None,
    max_send: int = 100,
) -> dict:
    if send:
        if smtp_config is None:
            raise ReminderEmailError("SMTP configuration is required when delivery is enabled")
        if not isinstance(app_url, str):
            raise ReminderEmailError("COPILOT_PUBLIC_ORIGIN must be a clean HTTPS URL")
        try:
            parsed_url = urlsplit(app_url)
            valid_url = (
                parsed_url.scheme == "https" and bool(parsed_url.netloc)
                and not parsed_url.username and not parsed_url.password
                and parsed_url.path in {"", "/"} and not parsed_url.query and not parsed_url.fragment
            )
        except ValueError:
            valid_url = False
        if not valid_url:
            raise ReminderEmailError("COPILOT_PUBLIC_ORIGIN must be an HTTPS origin without credentials, path, query, or fragment")

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
        events_by_user = {
            user_id: _filter_events_by_preferences(
                events, _reminder_preferences(tenant, user_id), now, timezone_name, lead_days
            )
            for user_id, events in events_by_user.items()
        }
        events_by_user = {user_id: events for user_id, events in events_by_user.items() if events}
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
                    error_code=denial, smtp_attempts=0, now=now,
                )
                summary["skipped_unauthorized_or_stale"] += 1
                summary["failed"] += 1
                continue
            payload = {
                "event_type": delivery["event_type"],
                "due_date": delivery["due_date"],
                "window": delivery["reminder_window"],
                "lead_days": delivery["lead_days"],
            }
            outcome = send_reminder_email(
                payload, recipient, app_url or "", smtp_config, enabled=True,
            )
            if outcome["status"] == "accepted_by_smtp":
                finish_attempt(
                    tenant, int(delivery["id"]), result_status="accepted_by_smtp",
                    smtp_attempts=int(outcome.get("attempts", 1)), now=now,
                )
                summary["smtp_accepted"] += 1
            else:
                status = (
                    "ambiguous"
                    if outcome.get("error_code") in {"smtp_connection_failure", "smtp_submission_ambiguous"}
                    else "failed"
                )
                finish_attempt(
                    tenant, int(delivery["id"]), result_status=status,
                    error_code=outcome.get("error_code") or "smtp_delivery_failure",
                    smtp_attempts=int(outcome.get("attempts", 1)), now=now,
                )
                if status == "ambiguous":
                    summary["ambiguous"] += 1
                else:
                    summary["failed"] += 1
    return summary


def outbox_status(runtime: DatabaseRuntime) -> dict:
    """Read-only operational counts for each active firm's reminder outbox."""
    control = runtime.control_connection()
    report = {"mode": "status", "firms_scanned": 0, "firms": [],
              "totals": {"queued": 0, "sending": 0, "accepted_by_smtp": 0,
                         "failed": 0, "ambiguous": 0},
              "warnings": ["SMTP acceptance is not inbox delivery.",
                           "Ambiguous records require operator reconciliation; they are not auto-retried."]}
    for row in control.execute("SELECT id FROM firms WHERE status='active' ORDER BY id").fetchall():
        firm_id = int(row["id"])
        try:
            tenant = runtime._tenant_router.connection_for_firm(firm_id)
            counts = {status: 0 for status in report["totals"]}
            for item in tenant.execute(
                "SELECT status,COUNT(*) AS total FROM reminder_deliveries GROUP BY status"
            ).fetchall():
                if item["status"] in counts:
                    counts[item["status"]] = int(item["total"])
        except ReminderOutboxError:
            report["warnings"].append(f"firm_{firm_id}: reminder outbox schema unavailable; apply the firm migration")
            continue
        except sqlite3.Error:
            report["warnings"].append(f"firm_{firm_id}: outbox status unavailable")
            continue
        except Exception:
            report["warnings"].append(f"firm_{firm_id}: tenant database unavailable; skipped")
            continue
        report["firms_scanned"] += 1
        report["firms"].append({"firm_id": firm_id, "counts": counts})
        for status, count in counts.items():
            report["totals"][status] += count
    return report


def _parse_lead_days(value: str) -> tuple[int, ...]:
    try:
        parsed = tuple(sorted({int(item.strip()) for item in value.split(",") if item.strip()}, reverse=True))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("lead days must be comma-separated integers") from exc
    if not parsed or any(not 1 <= day <= 30 for day in parsed):
        raise argparse.ArgumentTypeError("lead days must be between 1 and 30")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--send", action="store_true",
                      help="explicitly enable SMTP delivery; otherwise this is a read-only dry run")
    mode.add_argument("--status", action="store_true",
                      help="show read-only per-firm outbox counts without scheduling or delivery")
    parser.add_argument("--timezone", default="Africa/Cairo", help="IANA timezone (default: Africa/Cairo)")
    parser.add_argument("--now", help="optional ISO timestamp with timezone offset")
    parser.add_argument("--lead-days", type=_parse_lead_days, default=(7, 3, 1), help="comma-separated deadline lead windows (default: 7,3,1)")
    parser.add_argument("--max-send", type=int, default=100, help="maximum queued messages to claim per firm")
    parser.add_argument("--retry-failed-key", help="explicitly requeue one failed idempotency key in each firm")
    parser.add_argument("--out", type=Path, help="write sanitized JSON summary to this path")
    args = parser.parse_args(argv)
    runtime = None
    try:
        now = _parse_now(args.now)
        if args.retry_failed_key and (not args.send or args.status):
            raise ReminderOutboxError("--retry-failed-key requires --send")
        if not isinstance(args.lead_days, tuple) or not args.lead_days:
            raise ReminderScheduleError("--lead-days must contain one or more windows from 1 through 30")
        if type(args.max_send) is not int or not 1 <= args.max_send <= 1000:
            raise ReminderOutboxError("--max-send must be between 1 and 1000")
        if args.send:
            smtp_config = SMTPConfig.from_env()
            app_url = os.environ.get("COPILOT_PUBLIC_ORIGIN", "").strip()
            if not app_url:
                raise ReminderEmailError("COPILOT_PUBLIC_ORIGIN must be configured before sending reminders")
        else:
            smtp_config, app_url = None, None

        base_runtime = DatabaseRuntime.from_env()
        # Dry-run and status must not initialize schemas or apply migrations.
        # Only the explicit --send path opens the normal writable runtime.
        if args.send:
            base_runtime.initialize()
            runtime = base_runtime
        else:
            runtime = _ReadOnlyReminderRuntime(base_runtime)
        if args.status:
            result = outbox_status(runtime)
            output = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)
            if args.out:
                destination = args.out.resolve()
                tenant_root = runtime.paths.tenant_root.resolve()
                protected_files = {runtime.paths.control_plane.resolve(), runtime.paths.legal_corpus.resolve()}
                if destination in protected_files or destination == tenant_root or tenant_root in destination.parents:
                    raise ReminderOutboxError("report output must not overwrite or reside inside database storage")
                args.out.write_text(output + "\\n", encoding="utf-8")
            else:
                print(output)
            return 0
        retry_summary = None
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
            retry_summary = {"requested_retry_requeued": requeued}

        result = run_scheduler(
            runtime, now=now, timezone_name=args.timezone, lead_days=args.lead_days,
            send=args.send, smtp_config=smtp_config, app_url=app_url, max_send=args.max_send,
        )
        if retry_summary:
            result.update(retry_summary)
        output = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)
        if args.out:
            destination = args.out.resolve()
            tenant_root = runtime.paths.tenant_root.resolve()
            protected_files = {
                runtime.paths.control_plane.resolve(),
                runtime.paths.legal_corpus.resolve(),
            }
            if destination in protected_files or destination == tenant_root or tenant_root in destination.parents:
                raise ReminderOutboxError("report output must not overwrite or reside inside database storage")
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
