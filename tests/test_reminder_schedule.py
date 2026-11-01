import unittest
from datetime import datetime, timezone

from tools.reminder_schedule import ReminderScheduleError, build_reminder_plan


class ReminderScheduleTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 26, 8, 0, tzinfo=timezone.utc)
        self.events = [
            {"kind": "task", "event_id": "11", "due_date": "2026-10-27", "is_complete": False},
            {"kind": "deadline", "event_id": "22", "due_date": "2026-10-26", "is_complete": False},
            {"kind": "deadline", "event_id": "33", "due_date": "2026-10-25", "is_complete": False},
            {"kind": "task", "event_id": "44", "due_date": "2026-10-26", "is_complete": True},
            {"kind": "deadline", "event_id": "55", "due_date": "2026-10-29", "is_complete": False},
        ]

    def plan(self, **kwargs):
        return build_reminder_plan(self.events, "user-7", self.now, "Africa/Cairo", "firm-1", **kwargs)

    def test_plans_due_soon_today_and_overdue_without_delivery(self):
        report = self.plan()
        self.assertTrue(report["dry_run_only"])
        self.assertFalse(report["delivery_performed"])
        self.assertEqual(report["planned_count"], 3)
        self.assertEqual({item["window"] for item in report["reminders"]},
                         {"due_soon", "due_today", "overdue"})
        self.assertNotIn("title", report["reminders"][0])
        self.assertTrue(all(len(item["idempotency_key"]) == 64 for item in report["reminders"]))

    def test_sent_keys_suppress_duplicates_across_repeated_runs(self):
        first = self.plan()
        keys = {item["idempotency_key"] for item in first["reminders"]}
        second = self.plan(already_sent=keys)
        self.assertEqual(second["planned_count"], 0)

    def test_overdue_window_is_stable_across_days_but_due_date_change_changes_key(self):
        overdue = self.events[2]
        first = build_reminder_plan([overdue], "user-7", self.now, "Africa/Cairo", "firm-1")
        later = build_reminder_plan(
            [overdue], "user-7", datetime(2026, 10, 30, 8, 0, tzinfo=timezone.utc), "Africa/Cairo", "firm-1"
        )
        self.assertEqual(first["reminders"][0]["idempotency_key"], later["reminders"][0]["idempotency_key"])
        changed = dict(overdue, due_date="2026-10-24")
        third = build_reminder_plan([changed], "user-7", self.now, "Africa/Cairo", "firm-1")
        self.assertNotEqual(first["reminders"][0]["idempotency_key"], third["reminders"][0]["idempotency_key"])

    def test_timezone_conversion_controls_local_date_across_midnight(self):
        event = [{"kind": "deadline", "event_id": "1", "due_date": "2026-10-27", "is_complete": False}]
        report = build_reminder_plan(
            event, "user-7", datetime(2026, 10, 26, 23, 30, tzinfo=timezone.utc), "Africa/Cairo", "firm-1"
        )
        self.assertEqual(report["planned_count"], 1)
        self.assertEqual(report["reminders"][0]["window"], "due_today")

    def test_dst_boundary_uses_the_requested_local_timezone(self):
        event = [{"kind": "session", "event_id": "9", "due_date": "2026-03-29", "is_complete": False}]
        report = build_reminder_plan(
            event, "user-7", datetime(2026, 3, 29, 1, 30, tzinfo=timezone.utc), "Europe/Paris", "firm-1"
        )
        self.assertEqual(report["evaluated_at_local"][:10], "2026-03-29")
        self.assertEqual(report["reminders"][0]["window"], "due_today")

    def test_rejects_naive_time_invalid_timezone_bad_status_and_duplicate_events(self):
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan(self.events, "user-7", datetime(2026, 10, 26), "Africa/Cairo", "firm-1")
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan(self.events, "user-7", self.now, "Not/A_Timezone", "firm-1")
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan([dict(self.events[0], is_complete="false")], "user-7", self.now, "Africa/Cairo", "firm-1")
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan([dict(self.events[0], kind=[])], "user-7", self.now, "Africa/Cairo", "firm-1")
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan([self.events[0], self.events[0]], "user-7", self.now, "Africa/Cairo", "firm-1")

    def test_firm_scope_is_part_of_idempotency_key(self):
        event = [self.events[0]]
        first = build_reminder_plan(event, "shared-user", self.now, "Africa/Cairo", "firm-1")
        second = build_reminder_plan(event, "shared-user", self.now, "Africa/Cairo", "firm-2")
        self.assertNotEqual(first["reminders"][0]["idempotency_key"], second["reminders"][0]["idempotency_key"])

    def test_rejects_missing_scope_and_wrong_sent_key_container(self):
        event = [self.events[0]]
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan(event, "user-7", self.now, "Africa/Cairo", "")
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan(event, "user-7", self.now, "Africa/Cairo", "firm-1", already_sent=[])


    def test_multiple_deadline_lead_windows_and_session_day_of_only(self):
        events = [
            {"kind": "deadline", "event_id": "7", "due_date": "2026-11-02", "is_complete": False},
            {"kind": "deadline", "event_id": "3", "due_date": "2026-10-29", "is_complete": False},
            {"kind": "deadline", "event_id": "1", "due_date": "2026-10-27", "is_complete": False},
            {"kind": "session", "event_id": "today", "due_date": "2026-10-26", "is_complete": False},
            {"kind": "session", "event_id": "tomorrow", "due_date": "2026-10-27", "is_complete": False},
        ]
        report = build_reminder_plan(
            events, "user-7", self.now, "Africa/Cairo", "firm-1", lead_days=(7, 3, 1)
        )
        self.assertEqual(report["planned_count"], 4)
        by_id = {item["event_id"]: item for item in report["reminders"]}
        self.assertEqual(by_id["7"]["lead_days"], 7)
        self.assertEqual(by_id["3"]["lead_days"], 3)
        self.assertEqual(by_id["1"]["lead_days"], 1)
        self.assertEqual(by_id["today"]["window"], "due_today")
        self.assertNotIn("tomorrow", by_id)

    def test_same_deadline_can_have_distinct_idempotency_keys_for_each_lead_window(self):
        event = [{"kind": "deadline", "event_id": "22", "due_date": "2026-11-02", "is_complete": False}]
        seven = build_reminder_plan(event, "user-7", self.now, "Africa/Cairo", "firm-1", lead_days=7)
        three = build_reminder_plan(
            event, "user-7", datetime(2026, 10, 30, 8, 0, tzinfo=timezone.utc),
            "Africa/Cairo", "firm-1", lead_days=3,
        )
        self.assertNotEqual(seven["reminders"][0]["idempotency_key"], three["reminders"][0]["idempotency_key"])


    def test_rejects_noncanonical_dates_and_bad_lead_windows(self):
        event = [{"kind": "task", "event_id": "1", "due_date": "2026-1-2", "is_complete": False}]
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan(event, "user-7", self.now, "Africa/Cairo", "firm-1")
        with self.assertRaises(ReminderScheduleError):
            build_reminder_plan(self.events, "user-7", self.now, "Africa/Cairo", "firm-1", lead_days=-1)


if __name__ == "__main__":
    unittest.main()
