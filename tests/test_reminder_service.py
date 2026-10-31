import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from database_runtime import DatabaseRuntime
from tools.reminder_email import SMTPConfig
from tools.reminder_outbox import enqueue_plan
from tools.reminder_schedule import build_reminder_plan
from tools.reminder_service import (
    _ReadOnlyReminderRuntime, main, outbox_status, run_scheduler,
)


class ReminderServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = DatabaseRuntime(
            self.root / "control.sqlite3", self.root / "tenants", self.root / "corpus.sqlite3"
        )
        self.runtime.initialize()
        self.firm_id, _ = self.runtime.provision_firm("Reminder Firm")
        self.user_id = self.runtime.create_global_identity(
            "Reminder User", "reminder-user@example.test", "test-password-hash"
        )
        self.runtime.create_firm_membership(self.user_id, self.firm_id, "lawyer")
        self.control = self.runtime.control_connection()
        self.tenant = self.runtime._tenant_router.connection_for_firm(self.firm_id)
        self.case_id = self.tenant.execute(
            "INSERT INTO cases(title,firm_id,created_by) VALUES(?,?,?)",
            ("Private matter title", self.firm_id, self.user_id),
        ).lastrowid
        self.tenant.execute(
            "INSERT INTO members(case_id,user_id,role) VALUES(?,?,?)",
            (self.case_id, self.user_id, "lawyer"),
        )
        self.task_id = self.tenant.execute(
            "INSERT INTO tasks(case_id,title,assignee,due,status,created_by) VALUES(?,?,?,?,?,?)",
            (self.case_id, "Private task title", self.user_id, "2026-10-27", "open", self.user_id),
        ).lastrowid
        self.tenant.commit()
        self.now = datetime(2026, 10, 26, 8, 0, tzinfo=timezone.utc)
        self.smtp = SMTPConfig(
            "smtp.example.test", 587, "notices@example.test", "smtp-user", "test-password"
        )

    def tearDown(self):
        self.runtime.close_current_thread()
        self.temp.cleanup()

    def test_default_dry_run_does_not_write_outbox_or_send(self):
        report = run_scheduler(
            self.runtime, now=self.now, timezone_name="Africa/Cairo", send=False
        )
        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["reminders_planned"], 1)
        self.assertEqual(report["reminders_queued"], 0)
        self.assertEqual(
            self.tenant.execute("SELECT COUNT(*) FROM reminder_deliveries").fetchone()[0], 0
        )

    def test_read_only_dry_run_uses_query_only_connections(self):
        readonly = _ReadOnlyReminderRuntime(self.runtime)
        try:
            report = run_scheduler(
                readonly, now=self.now, timezone_name="Africa/Cairo", send=False
            )
            self.assertEqual(report["reminders_planned"], 1)
            control = readonly.control_connection()
            tenant = readonly._tenant_router.connection_for_firm(self.firm_id)
            self.assertEqual(control.execute("PRAGMA query_only").fetchone()[0], 1)
            self.assertEqual(tenant.execute("PRAGMA query_only").fetchone()[0], 1)
            with self.assertRaises(sqlite3.OperationalError):
                tenant.execute("UPDATE tasks SET status='done' WHERE id=?", (self.task_id,))
        finally:
            readonly.close_current_thread()

    def test_cli_dry_run_does_not_call_database_runtime_initialize(self):
        from contextlib import redirect_stdout
        import io

        with patch("tools.reminder_service.DatabaseRuntime.from_env", return_value=self.runtime), \
             patch.object(DatabaseRuntime, "initialize", side_effect=AssertionError("initialize must not run")), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(main([]), 0)

    def test_cli_status_does_not_call_database_runtime_initialize(self):
        from contextlib import redirect_stdout
        import io

        with patch("tools.reminder_service.DatabaseRuntime.from_env", return_value=self.runtime), \
             patch.object(DatabaseRuntime, "initialize", side_effect=AssertionError("initialize must not run")), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--status"]), 0)

    def test_status_report_is_read_only_and_contains_only_counts(self):
        plan = build_reminder_plan(
            [{"kind": "task", "event_id": str(self.task_id), "due_date": "2026-10-27", "is_complete": False}],
            str(self.user_id), self.now, "Africa/Cairo", str(self.firm_id),
        )
        enqueue_plan(self.tenant, plan, firm_id=self.firm_id, recipient_user_id=self.user_id)
        before = self.tenant.execute("SELECT status,COUNT(*) FROM reminder_deliveries GROUP BY status").fetchall()
        report = outbox_status(self.runtime)
        after = self.tenant.execute("SELECT status,COUNT(*) FROM reminder_deliveries GROUP BY status").fetchall()
        self.assertEqual(report["mode"], "status")
        self.assertEqual(report["totals"]["queued"], 1)
        self.assertEqual(before, after)
        self.assertNotIn("reminder-user@example.test", str(report))
        self.assertNotIn("Private matter title", str(report))

    def test_send_mode_queues_atomically_rechecks_authorization_and_records_acceptance(self):
        with patch(
            "tools.reminder_service.send_reminder_email",
            return_value={"status": "accepted_by_smtp", "attempts": 1, "error_code": None},
        ) as sender:
            report = run_scheduler(
                self.runtime, now=self.now, timezone_name="Africa/Cairo", send=True,
                smtp_config=self.smtp, app_url="https://app.example.test", max_send=10,
            )
        self.assertEqual(report["reminders_queued"], 1)
        self.assertEqual(report["smtp_accepted"], 1)
        self.assertEqual(report["failed"], 0)
        self.assertEqual(sender.call_count, 1)
        payload = sender.call_args.args[0]
        self.assertEqual(payload["event_type"], "task")
        self.assertNotIn("Private matter title", str(payload))
        row = self.tenant.execute("SELECT * FROM reminder_deliveries").fetchone()
        self.assertEqual(row["status"], "accepted_by_smtp")
        self.assertEqual(row["attempt_count"], 1)

    def test_nonmember_assignee_is_not_queued(self):
        other_id = self.runtime.create_global_identity(
            "Not a Case Member", "not-case-member@example.test", "test-password-hash"
        )
        self.runtime.create_firm_membership(other_id, self.firm_id, "lawyer")
        self.tenant.execute("UPDATE tasks SET assignee=? WHERE id=?", (other_id, self.task_id))
        self.tenant.commit()
        report = run_scheduler(
            self.runtime, now=self.now, timezone_name="Africa/Cairo", send=False
        )
        self.assertEqual(report["reminders_planned"], 0)
        self.assertEqual(
            self.tenant.execute("SELECT COUNT(*) FROM reminder_deliveries").fetchone()[0], 0
        )

    def test_queued_reminder_is_not_sent_after_firm_membership_revocation(self):
        plan = build_reminder_plan(
            [{"kind": "task", "event_id": str(self.task_id), "due_date": "2026-10-27", "is_complete": False}],
            str(self.user_id), self.now, "Africa/Cairo", str(self.firm_id),
        )
        enqueue_plan(self.tenant, plan, firm_id=self.firm_id, recipient_user_id=self.user_id)
        self.control.execute(
            "UPDATE firm_memberships SET status='revoked' WHERE user_id=? AND firm_id=?",
            (self.user_id, self.firm_id),
        )
        self.control.commit()
        with patch("tools.reminder_service.send_reminder_email") as sender:
            report = run_scheduler(
                self.runtime, now=self.now, timezone_name="Africa/Cairo", send=True,
                smtp_config=self.smtp, app_url="https://app.example.test",
            )
        self.assertEqual(sender.call_count, 0)
        self.assertEqual(report["skipped_unauthorized_or_stale"], 1)
        row = self.tenant.execute("SELECT status,last_error_code FROM reminder_deliveries").fetchone()
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["last_error_code"], "recipient_not_active")
        attempt = self.tenant.execute("SELECT * FROM reminder_delivery_attempts").fetchone()
        self.assertEqual(attempt["status"], "failed")
        self.assertEqual(attempt["smtp_attempts"], 0)
        self.assertEqual(attempt["error_code"], "recipient_not_active")

    def test_queued_reminder_is_not_sent_after_user_account_is_disabled(self):
        plan = build_reminder_plan(
            [{"kind": "task", "event_id": str(self.task_id), "due_date": "2026-10-27", "is_complete": False}],
            str(self.user_id), self.now, "Africa/Cairo", str(self.firm_id),
        )
        enqueue_plan(self.tenant, plan, firm_id=self.firm_id, recipient_user_id=self.user_id)
        self.control.execute("UPDATE users SET status='disabled' WHERE id=?", (self.user_id,))
        self.control.commit()
        with patch("tools.reminder_service.send_reminder_email") as sender:
            report = run_scheduler(
                self.runtime, now=self.now, timezone_name="Africa/Cairo", send=True,
                smtp_config=self.smtp, app_url="https://app.example.test",
            )
        self.assertEqual(sender.call_count, 0)
        self.assertEqual(report["skipped_unauthorized_or_stale"], 1)
        row = self.tenant.execute("SELECT status,last_error_code FROM reminder_deliveries").fetchone()
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["last_error_code"], "recipient_not_active")

    def test_queued_reminder_is_not_sent_after_firm_is_disabled(self):
        plan = build_reminder_plan(
            [{"kind": "task", "event_id": str(self.task_id), "due_date": "2026-10-27", "is_complete": False}],
            str(self.user_id), self.now, "Africa/Cairo", str(self.firm_id),
        )
        enqueue_plan(self.tenant, plan, firm_id=self.firm_id, recipient_user_id=self.user_id)
        self.control.execute("UPDATE firms SET status='disabled' WHERE id=?", (self.firm_id,))
        self.control.commit()
        with patch("tools.reminder_service.send_reminder_email") as sender:
            report = run_scheduler(
                self.runtime, now=self.now, timezone_name="Africa/Cairo", send=True,
                smtp_config=self.smtp, app_url="https://app.example.test",
            )
        self.assertEqual(sender.call_count, 0)
        # Disabled firms are not processed by the scheduler at all.
        self.assertEqual(report["firms_scanned"], 0)
        row = self.tenant.execute("SELECT status FROM reminder_deliveries").fetchone()
        self.assertEqual(row["status"], "queued")

    def test_queued_reminder_is_not_sent_after_case_membership_revocation(self):
        plan = build_reminder_plan(
            [{"kind": "task", "event_id": str(self.task_id), "due_date": "2026-10-27", "is_complete": False}],
            str(self.user_id), self.now, "Africa/Cairo", str(self.firm_id),
        )
        enqueue_plan(self.tenant, plan, firm_id=self.firm_id, recipient_user_id=self.user_id)
        self.tenant.execute(
            "DELETE FROM members WHERE case_id=? AND user_id=?",
            (self.case_id, self.user_id),
        )
        self.tenant.commit()
        with patch("tools.reminder_service.send_reminder_email") as sender:
            report = run_scheduler(
                self.runtime, now=self.now, timezone_name="Africa/Cairo", send=True,
                smtp_config=self.smtp, app_url="https://app.example.test",
            )
        self.assertEqual(sender.call_count, 0)
        self.assertEqual(report["skipped_unauthorized_or_stale"], 1)
        row = self.tenant.execute("SELECT status,last_error_code FROM reminder_deliveries").fetchone()
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["last_error_code"], "recipient_not_authorized")
        attempt = self.tenant.execute("SELECT * FROM reminder_delivery_attempts").fetchone()
        self.assertEqual(attempt["status"], "failed")
        self.assertEqual(attempt["smtp_attempts"], 0)
        self.assertEqual(attempt["error_code"], "recipient_not_authorized")

    def test_queued_reminder_is_not_sent_after_event_is_completed(self):
        plan = build_reminder_plan(
            [{"kind": "task", "event_id": str(self.task_id), "due_date": "2026-10-27", "is_complete": False}],
            str(self.user_id), self.now, "Africa/Cairo", str(self.firm_id),
        )
        enqueue_plan(self.tenant, plan, firm_id=self.firm_id, recipient_user_id=self.user_id)
        self.tenant.execute("UPDATE tasks SET status='done' WHERE id=?", (self.task_id,))
        self.tenant.commit()
        with patch("tools.reminder_service.send_reminder_email") as sender:
            report = run_scheduler(
                self.runtime, now=self.now, timezone_name="Africa/Cairo", send=True,
                smtp_config=self.smtp, app_url="https://app.example.test",
            )
        self.assertEqual(sender.call_count, 0)
        self.assertEqual(report["skipped_unauthorized_or_stale"], 1)
        row = self.tenant.execute("SELECT status,last_error_code FROM reminder_deliveries").fetchone()
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["last_error_code"], "event_no_longer_eligible")
        attempt = self.tenant.execute("SELECT * FROM reminder_delivery_attempts").fetchone()
        self.assertEqual(attempt["status"], "failed")
        self.assertEqual(attempt["smtp_attempts"], 0)
        self.assertEqual(attempt["error_code"], "event_no_longer_eligible")


if __name__ == "__main__":
    unittest.main()
