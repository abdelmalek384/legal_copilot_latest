import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from database_runtime import DatabaseRuntime
from tools.reminder_healthcheck import inspect_health


class ReminderHealthcheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="reminder-health-")
        self.root = Path(self.temp.name)
        self.runtime = DatabaseRuntime(
            self.root / "control.sqlite3",
            self.root / "tenants",
            self.root / "corpus.sqlite3",
        )
        self.runtime.initialize()
        self.firm_id, self.tenant_path = self.runtime.provision_firm("Healthcheck Firm")
        self.now = datetime(2026, 10, 30, 14, 0, tzinfo=timezone.utc)
        self.tenant = self.runtime._tenant_router.connection_for_firm(self.firm_id)

    def tearDown(self):
        self.runtime.close_current_thread()
        self.temp.cleanup()

    def _insert(self, key, status, *, created="2026-10-30 13:50:00",
                updated="2026-10-30 13:50:00", lease=None, next_attempt=None):
        return self.tenant.execute(
            "INSERT INTO reminder_deliveries "
            "(idempotency_key,recipient_user_id,event_type,event_id,due_date,reminder_window,"
            "status,created_at,updated_at,lease_until,next_attempt_at) "
            "VALUES(?,1,'task',?,'2026-10-31','due_soon',?,?,?,?,?)",
            (key * 64, key, status, created, updated, lease, next_attempt),
        ).lastrowid

    def _report(self, threshold=30):
        return inspect_health(
            self.runtime.paths.control_plane,
            self.runtime.paths.tenant_root,
            now=self.now,
            stale_queued_minutes=threshold,
        )

    def test_empty_outbox_is_healthy_and_read_only(self):
        before = self.tenant.execute("SELECT COUNT(*) FROM reminder_deliveries").fetchone()[0]
        report = self._report()
        after = self.tenant.execute("SELECT COUNT(*) FROM reminder_deliveries").fetchone()[0]
        self.assertTrue(report["healthy"])
        self.assertEqual(report["firms_scanned"], 1)
        self.assertEqual(before, after)
        self.assertEqual(report["totals"]["queued"], 0)

    def test_accepted_by_smtp_is_not_a_health_failure(self):
        self._insert("a", "accepted_by_smtp")
        self.tenant.commit()
        report = self._report()
        self.assertTrue(report["healthy"])
        self.assertEqual(report["totals"]["accepted_by_smtp"], 1)
        self.assertEqual(report["findings"], [])

    def test_stale_queued_row_is_reported_but_future_retry_is_not_stale(self):
        self._insert("b", "queued", created="2026-10-30 12:00:00", updated="2026-10-30 12:00:00")
        self._insert(
            "c", "queued", created="2026-10-30 12:00:00", updated="2026-10-30 12:00:00",
            next_attempt="2026-10-30T14:30:00+00:00",
        )
        self.tenant.commit()
        report = self._report()
        self.assertFalse(report["healthy"])
        self.assertEqual(report["totals"]["queued"], 2)
        self.assertEqual(report["totals"]["stale_queued"], 1)
        self.assertIn("stale_queued_reminders", [item["code"] for item in report["findings"]])

    def test_expired_or_missing_sender_lease_is_critical(self):
        self._insert("d", "sending", lease="2026-10-30T13:59:00+00:00")
        self._insert("e", "sending", lease=None)
        self.tenant.commit()
        report = self._report()
        self.assertFalse(report["healthy"])
        self.assertEqual(report["totals"]["sending"], 2)
        self.assertEqual(report["totals"]["expired_sending"], 2)
        finding = next(item for item in report["findings"] if item["code"] == "expired_or_missing_sender_lease")
        self.assertEqual(finding["severity"], "critical")

    def test_malformed_queue_and_lease_timestamps_are_not_silently_healthy(self):
        self._insert("h", "queued", created="not-a-time", updated="not-a-time")
        self._insert("i", "sending", lease="not-a-time")
        self.tenant.commit()
        report = self._report()
        self.assertFalse(report["healthy"])
        self.assertEqual(report["totals"]["stale_queued"], 1)
        self.assertEqual(report["totals"]["expired_sending"], 1)

    def test_failed_and_ambiguous_rows_require_operator_attention(self):
        self._insert("f", "failed")
        self._insert("g", "ambiguous")
        self.tenant.commit()
        report = self._report()
        self.assertFalse(report["healthy"])
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("failed_reminders_present", codes)
        self.assertIn("ambiguous_reminders_require_reconciliation", codes)

    def test_scans_multiple_firms_and_aggregates_without_cross_firm_data(self):
        second_id, second_path = self.runtime.provision_firm("Second Healthcheck Firm")
        second = self.runtime._tenant_router.connection_for_firm(second_id)
        self._insert("j", "queued")
        second.execute(
            "INSERT INTO reminder_deliveries "
            "(idempotency_key,recipient_user_id,event_type,event_id,due_date,reminder_window,status,created_at,updated_at) "
            "VALUES(?,1,'task','second','2026-10-31','due_soon','queued','2026-10-30 12:00:00','2026-10-30 12:00:00')",
            ("j" * 64,),
        )
        self.tenant.commit()
        second.commit()
        report = self._report()
        self.assertFalse(report["healthy"])
        self.assertEqual(report["firms_scanned"], 2)
        self.assertEqual(report["totals"]["queued"], 2)
        self.assertEqual(
            [item["firm_id"] for item in report["firms"]],
            sorted([self.firm_id, second_id]),
        )
        self.assertTrue(all("recipient" not in str(item).lower() for item in report["firms"]))

    def test_missing_tenant_database_is_a_critical_finding(self):
        second_id, second_path = self.runtime.provision_firm("Missing Outbox Firm")
        self.runtime.close_current_thread()
        second_path.unlink()
        report = self._report()
        self.assertFalse(report["healthy"])
        self.assertEqual(report["firms_scanned"], 1)
        finding = next(item for item in report["findings"] if item["firm_id"] == second_id)
        self.assertEqual(finding["code"], "tenant_outbox_unavailable")
        self.assertEqual(finding["severity"], "critical")

    def test_invalid_threshold_and_naive_time_are_rejected(self):
        with self.assertRaises(ValueError):
            inspect_health(self.runtime.paths.control_plane, self.runtime.paths.tenant_root, stale_queued_minutes=0)
        with self.assertRaises(ValueError):
            inspect_health(
                self.runtime.paths.control_plane, self.runtime.paths.tenant_root,
                now=datetime(2026, 10, 30, 14, 0),
            )


if __name__ == "__main__":
    unittest.main()
