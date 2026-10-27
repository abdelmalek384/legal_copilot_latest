import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools.reminder_schedule import main


class ReminderScheduleCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.input_path = self.root / "events.json"
        self.payload = {
            "events": [
                {"kind": "deadline", "event_id": "event-1",
                 "due_date": "2026-10-27", "is_complete": False}
            ],
            "already_sent": [],
        }
        self.input_path.write_text(json.dumps(self.payload), encoding="utf-8")
        self.args = [
            "--input", str(self.input_path),
            "--recipient-id", "user-test",
            "--scope-id", "firm-test",
            "--timezone", "Africa/Cairo",
            "--now", "2026-10-26T08:00:00+00:00",
        ]

    def tearDown(self):
        self.temp.cleanup()

    def test_stdout_output_is_valid_json_and_never_claims_delivery(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(self.args)
        report = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(report["dry_run_only"])
        self.assertFalse(report["delivery_performed"])
        self.assertEqual(report["planned_count"], 1)
        self.assertEqual(report["reminders"][0]["window"], "due_soon")

    def test_output_file_mode_writes_report_without_changing_input(self):
        original = self.input_path.read_text(encoding="utf-8")
        output_path = self.root / "reports" / "dry-run.json"
        code = main(self.args + ["--out", str(output_path)])
        report = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        self.assertFalse(report["delivery_performed"])
        self.assertEqual(self.input_path.read_text(encoding="utf-8"), original)

    def test_refuses_to_overwrite_input(self):
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code = main(self.args + ["--out", str(self.input_path)])
        self.assertEqual(code, 2)
        self.assertIn("must not overwrite", errors.getvalue())
        self.assertEqual(json.loads(self.input_path.read_text(encoding="utf-8")), self.payload)

    def test_malformed_json_and_missing_timezone_fail_cleanly(self):
        self.input_path.write_text("{", encoding="utf-8")
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code = main(self.args)
        self.assertEqual(code, 2)
        self.assertIn("not valid JSON", errors.getvalue())
        self.input_path.write_text(json.dumps(self.payload), encoding="utf-8")
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code = main(self.args[:-2] + ["--now", "2026-10-26T08:00:00"])
        self.assertEqual(code, 2)
        self.assertIn("timezone offset", errors.getvalue())


    def test_invalid_utf8_input_fails_cleanly(self):
        self.input_path.write_bytes(b"\xff")
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code = main(self.args)
        self.assertEqual(code, 2)
        self.assertIn("failed", errors.getvalue())

    def test_bad_events_and_already_sent_fail_closed(self):
        for payload in ({"events": "not-list"}, {"events": [], "already_sent": [7]}):
            self.input_path.write_text(json.dumps(payload), encoding="utf-8")
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = main(self.args)
            self.assertEqual(code, 2)
            self.assertIn("failed", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
