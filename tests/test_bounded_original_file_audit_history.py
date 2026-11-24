"""Regression contracts for bounded original-file audit history endpoints."""
import pathlib
import sqlite3
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")


class BoundedOriginalFileAuditHistoryTests(unittest.TestCase):
    def test_legal_hold_history_is_paginated_and_reports_truncation(self):
        start = APP_SOURCE.index("def list_original_document_legal_hold_events(")
        end = APP_SOURCE.index("class OriginalFileDeletionRequestIn", start)
        endpoint = APP_SOURCE[start:end]
        self.assertIn("limit: int = Query(default=100, ge=1, le=200)", endpoint)
        self.assertIn("offset: int = Query(default=0, ge=0, le=100000)", endpoint)
        self.assertIn("ORDER BY id DESC LIMIT ? OFFSET ?", endpoint)
        self.assertIn('"total": total', endpoint)
        self.assertIn('"truncated": offset + len(events) < total', endpoint)
        self.assertIn("WHERE object_id=? AND document_id=? AND firm_id=?", endpoint)

    def test_deletion_requests_and_nested_events_are_bounded(self):
        start = APP_SOURCE.index("def list_original_document_deletion_requests(")
        end = APP_SOURCE.index("class DocumentClassificationIn", start)
        endpoint = APP_SOURCE[start:end]
        self.assertIn("limit: int = Query(default=50, ge=1, le=200)", endpoint)
        self.assertIn("offset: int = Query(default=0, ge=0, le=100000)", endpoint)
        self.assertIn("ORDER BY id DESC LIMIT ? OFFSET ?", endpoint)
        self.assertIn("ORDER BY id DESC LIMIT 100", endpoint)
        self.assertIn('"events_truncated": len(events) < event_total', endpoint)
        self.assertIn('"truncated": offset + len(requests) < total', endpoint)
        self.assertIn("WHERE request_id=? AND firm_id=?", endpoint)

    def test_hold_history_pagination_is_firm_and_document_scoped(self):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, object_id TEXT, document_id INTEGER, firm_id INTEGER, action TEXT)")
        db.executemany("INSERT INTO events VALUES(?,?,?,?,?)", [
            (1, "obj-a", 10, 2, "set"),
            (2, "obj-a", 10, 2, "release"),
            (3, "obj-b", 11, 2, "set"),
            (4, "obj-c", 10, 3, "set"),
        ])
        rows = db.execute(
            "SELECT action FROM events WHERE object_id=? AND document_id=? AND firm_id=? ORDER BY id DESC LIMIT ? OFFSET ?",
            ("obj-a", 10, 2, 1, 0),
        ).fetchall()
        self.assertEqual(rows, [("release",)])
        db.close()

    def test_nested_deletion_event_page_does_not_cross_request_or_firm(self):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, request_id INTEGER, firm_id INTEGER, action TEXT)")
        db.executemany("INSERT INTO events VALUES(?,?,?,?)", [
            (1, 20, 2, "requested"),
            (2, 20, 2, "approved"),
            (3, 21, 2, "requested"),
            (4, 20, 3, "requested"),
        ])
        rows = db.execute(
            "SELECT action FROM events WHERE request_id=? AND firm_id=? ORDER BY id DESC LIMIT 100",
            (20, 2),
        ).fetchall()
        self.assertEqual(rows, [("approved",), ("requested",)])
        db.close()


if __name__ == "__main__":
    unittest.main()
