import os
import sqlite3
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from database_runtime import DatabaseRuntime
from tools.reminder_outbox import (
    ReminderOutboxError, claim_next, enqueue_plan, finish_attempt, retry_failed,
)
from tools.reminder_schedule import build_reminder_plan


class ReminderOutboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = DatabaseRuntime(
            self.root / "control.sqlite3", self.root / "tenants", self.root / "corpus.sqlite3"
        )
        self.runtime.initialize()
        self.firm_id, self.path = self.runtime.provision_firm("Reminder Firm")
        self.db = sqlite3.connect(self.path, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.now = datetime(2026, 10, 26, 8, 0, tzinfo=timezone.utc)
        self.plan = build_reminder_plan(
            [{"kind": "deadline", "event_id": "22", "due_date": "2026-10-27", "is_complete": False}],
            str(7), self.now, "Africa/Cairo", str(self.firm_id),
        )

    def tearDown(self):
        self.db.close()
        self.runtime.close_current_thread()
        self.temp.cleanup()

    def test_plan_is_bound_to_firm_and_recipient_and_duplicate_runs_are_idempotent(self):
        self.assertEqual(self.plan["scope_id"], str(self.firm_id))
        self.assertEqual(self.plan["recipient_id"], "7")
        self.assertEqual(enqueue_plan(self.db, self.plan, firm_id=self.firm_id, recipient_user_id=7), 1)
        self.assertEqual(enqueue_plan(self.db, self.plan, firm_id=self.firm_id, recipient_user_id=7), 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM reminder_deliveries").fetchone()[0], 1)

    def test_same_deadline_can_queue_separate_lead_windows(self):
        event = [{"kind": "deadline", "event_id": "22", "due_date": "2026-11-02", "is_complete": False}]
        seven = build_reminder_plan(
            event, str(7), self.now, "Africa/Cairo", str(self.firm_id), lead_days=7
        )
        three = build_reminder_plan(
            event, str(7), datetime(2026, 10, 30, 8, 0, tzinfo=timezone.utc),
            "Africa/Cairo", str(self.firm_id), lead_days=3,
        )
        self.assertEqual(enqueue_plan(self.db, seven, firm_id=self.firm_id, recipient_user_id=7), 1)
        self.assertEqual(enqueue_plan(self.db, three, firm_id=self.firm_id, recipient_user_id=7), 1)
        rows = self.db.execute(
            "SELECT lead_days,reminder_window FROM reminder_deliveries ORDER BY lead_days DESC"
        ).fetchall()
        self.assertEqual([(row["lead_days"], row["reminder_window"]) for row in rows],
                         [(7, "due_soon"), (3, "due_soon")])

    def test_scope_and_recipient_mismatch_are_rejected_before_writes(self):
        with self.assertRaisesRegex(ReminderOutboxError, "scope or recipient"):
            enqueue_plan(self.db, self.plan, firm_id=self.firm_id + 1, recipient_user_id=7)
        with self.assertRaisesRegex(ReminderOutboxError, "scope or recipient"):
            enqueue_plan(self.db, self.plan, firm_id=self.firm_id, recipient_user_id=8)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM reminder_deliveries").fetchone()[0], 0)

    def test_tampered_plan_row_scope_or_idempotency_key_is_rejected(self):
        wrong_scope = dict(self.plan)
        wrong_scope["reminders"] = [dict(self.plan["reminders"][0], scope_id="999")]
        with self.assertRaisesRegex(ReminderOutboxError, "scope or recipient"):
            enqueue_plan(self.db, wrong_scope, firm_id=self.firm_id, recipient_user_id=7)

        wrong_key = dict(self.plan)
        wrong_key["reminders"] = [dict(self.plan["reminders"][0], idempotency_key="0" * 64)]
        with self.assertRaisesRegex(ReminderOutboxError, "idempotency key does not match"):
            enqueue_plan(self.db, wrong_key, firm_id=self.firm_id, recipient_user_id=7)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM reminder_deliveries").fetchone()[0], 0)

    def test_accepted_smtp_result_is_durable_and_not_claimed_again(self):
        enqueue_plan(self.db, self.plan, firm_id=self.firm_id, recipient_user_id=7)
        claimed = claim_next(self.db, now=self.now)
        self.assertEqual(claimed["status"], "sending")
        self.assertEqual(claimed["attempt_count"], 1)
        finish_attempt(
            self.db, claimed["id"], result_status="accepted_by_smtp",
            provider_message_id="smtp-accepted-123", now=self.now,
        )
        row = self.db.execute("SELECT * FROM reminder_deliveries").fetchone()
        self.assertEqual(row["status"], "accepted_by_smtp")
        self.assertEqual(row["provider_message_id"], "smtp-accepted-123")
        self.assertIsNotNone(row["accepted_at"])
        self.assertIsNone(row["lease_until"])
        attempt = self.db.execute("SELECT * FROM reminder_delivery_attempts").fetchone()
        self.assertEqual(attempt["status"], "accepted_by_smtp")
        self.assertEqual(attempt["smtp_attempts"], 1)
        self.assertEqual(attempt["provider_message_id"], "smtp-accepted-123")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only"):
            self.db.execute(
                "UPDATE reminder_delivery_attempts SET status='failed' WHERE id=?", (attempt["id"],)
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only"):
            self.db.execute("DELETE FROM reminder_delivery_attempts WHERE id=?", (attempt["id"],))
        self.db.rollback()
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM reminder_delivery_attempts").fetchone()[0], 1)
        self.assertIsNone(claim_next(self.db, now=self.now + timedelta(minutes=5)))

    def test_expired_sender_lease_becomes_ambiguous_never_automatically_requeued(self):
        enqueue_plan(self.db, self.plan, firm_id=self.firm_id, recipient_user_id=7)
        claimed = claim_next(self.db, now=self.now, lease_seconds=15)
        self.assertIsNotNone(claimed)
        self.assertIsNone(claim_next(self.db, now=self.now + timedelta(seconds=16), lease_seconds=15))
        row = self.db.execute("SELECT status,last_error_code,lease_until FROM reminder_deliveries").fetchone()
        self.assertEqual(row["status"], "ambiguous")
        self.assertEqual(row["last_error_code"], "sender_lease_expired")
        self.assertIsNone(row["lease_until"])

    def test_failed_delivery_requires_explicit_retry_and_preserves_attempt_history(self):
        enqueue_plan(self.db, self.plan, firm_id=self.firm_id, recipient_user_id=7)
        claimed = claim_next(self.db, now=self.now)
        finish_attempt(self.db, claimed["id"], result_status="failed",
                       error_code="smtp_connection_failure", now=self.now)
        self.assertTrue(retry_failed(self.db, claimed["idempotency_key"], now=self.now + timedelta(minutes=1)))
        self.assertFalse(retry_failed(self.db, claimed["idempotency_key"], now=self.now + timedelta(minutes=1)))
        second = claim_next(self.db, now=self.now + timedelta(minutes=1))
        self.assertEqual(second["id"], claimed["id"])
        self.assertEqual(second["attempt_count"], 2)
        finish_attempt(self.db, second["id"], result_status="failed", error_code="smtp_permanent_failure")
        attempts = self.db.execute(
            "SELECT attempt_number,status FROM reminder_delivery_attempts ORDER BY attempt_number"
        ).fetchall()
        self.assertEqual([(row["attempt_number"], row["status"]) for row in attempts],
                         [(1, "failed"), (2, "failed")])
        with self.assertRaisesRegex(ReminderOutboxError, "in-flight"):
            finish_attempt(self.db, second["id"], result_status="accepted_by_smtp")

    def test_concurrent_workers_cannot_claim_the_same_queued_row(self):
        enqueue_plan(self.db, self.plan, firm_id=self.firm_id, recipient_user_id=7)
        barrier = threading.Barrier(2)
        results = []
        errors = []

        def worker():
            connection = sqlite3.connect(self.path, timeout=5)
            connection.row_factory = sqlite3.Row
            try:
                barrier.wait()
                results.append(claim_next(connection, now=self.now))
            except Exception as exc:
                errors.append(exc)
            finally:
                connection.close()

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertFalse(errors, errors)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(sum(result is not None for result in results), 1)

    def test_invalid_error_codes_and_provider_identifiers_are_rejected(self):
        enqueue_plan(self.db, self.plan, firm_id=self.firm_id, recipient_user_id=7)
        claimed = claim_next(self.db, now=self.now)
        with self.assertRaises(ReminderOutboxError):
            finish_attempt(self.db, claimed["id"], result_status="failed", error_code="private provider response")
        with self.assertRaises(ReminderOutboxError):
            finish_attempt(self.db, claimed["id"], result_status="accepted_by_smtp", provider_message_id="x\nBcc: bad")


if __name__ == "__main__":
    unittest.main()
