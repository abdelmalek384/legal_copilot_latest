"""Focused tests for firm-scoped lawyer answer-rating routes."""
import csv
import io
import json
import sqlite3
import unittest
from unittest.mock import patch

import app


class AnswerRatingRouteTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE research_conversations(
                id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,firm_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE research_messages(
                id INTEGER PRIMARY KEY,conversation_id INTEGER NOT NULL REFERENCES research_conversations(id),
                role TEXT NOT NULL,content TEXT NOT NULL,sources_json TEXT NOT NULL DEFAULT '[]',
                message_json TEXT NOT NULL DEFAULT '{}',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE security_audit_events(
                id INTEGER PRIMARY KEY,firm_id INTEGER NOT NULL,user_id INTEGER NOT NULL,event TEXT NOT NULL
            );
            INSERT INTO research_conversations(id,user_id,firm_id,title) VALUES
                (10,7,1,'Firm A'),(20,8,2,'Firm B');
            INSERT INTO research_messages(id,conversation_id,role,content,message_json) VALUES
                (1,10,'user','=SUM(1,1)','{}'),
                (2,10,'assistant','Firm A answer','{"answer_id":"ans_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA","sources":[{"article_id":"LABOUR::article:12"}]}'),
                (3,20,'user','Private Firm B question','{}'),
                (4,20,'assistant','Private Firm B answer','{"answer_id":"ans_BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"}');
        """)
        migration = app.Path(__file__).resolve().parents[1] / "migrations" / "firm" / "0021_answer_ratings.sql"
        self.db.executescript(migration.read_text(encoding="utf-8"))
        self.user = {"id": 7, "firm_id": 1, "role": "admin", "name": "Reviewer"}
        self.answer_id = "ans_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        self.connection_patch = patch.object(app, "conn", return_value=self.db)
        self.connection_patch.start()

    def tearDown(self):
        self.connection_patch.stop()
        self.db.close()

    def rating(self, **changes):
        values = {
            "rating": "partially_correct",
            "cited_article_accuracy": "wrong",
            "expected_article_ids": ["LABOUR::article:12"],
            "answerable": True,
            "notes": "Wrong article cited.",
        }
        values.update(changes)
        return app.AnswerRatingIn(**values)

    def test_create_then_update_keeps_one_current_rating_and_appends_events(self):
        first = app.save_answer_rating(self.answer_id, self.rating(), self.user)
        second = app.save_answer_rating(
            self.answer_id,
            self.rating(rating="correct", cited_article_accuracy="right"),
            self.user,
        )
        self.assertEqual(first["rating_id"], second["rating_id"])
        self.assertEqual(second["rating"], "correct")
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM answer_ratings").fetchone()[0], 1
        )
        events = self.db.execute(
            "SELECT event_type FROM answer_rating_events ORDER BY id"
        ).fetchall()
        self.assertEqual([row["event_type"] for row in events], ["created", "updated"])
        self.assertTrue(second["benchmark_ready"])

    def test_authenticated_reviewer_identity_is_server_derived(self):
        lawyer = {"id": 19, "firm_id": 1, "role": "lawyer", "name": "Lawyer"}
        forged = app.AnswerRatingIn(**{
            "rating": "correct",
            "cited_article_accuracy": "right",
            "expected_article_ids": ["LABOUR::article:12"],
            "answerable": True,
            "notes": "",
            "rated_by": 999,
        })
        saved = app.save_answer_rating(self.answer_id, forged, lawyer)
        self.assertEqual(saved["rated_by"], 19)
        self.assertEqual(
            self.db.execute("SELECT rated_by FROM answer_ratings").fetchone()[0], 19
        )

    def test_rating_list_is_admin_only(self):
        lawyer = {"id": 19, "firm_id": 1, "role": "lawyer", "name": "Lawyer"}
        with self.assertRaises(app.HTTPException) as caught:
            app.list_firm_answer_ratings(100, 0, lawyer)
        self.assertEqual(caught.exception.status_code, 403)

    def test_cross_firm_answer_id_is_not_disclosed_or_rated(self):
        with self.assertRaises(app.HTTPException) as caught:
            app.save_answer_rating(
                "ans_BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", self.rating(), self.user
            )
        self.assertEqual(caught.exception.status_code, 404)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM answer_ratings").fetchone()[0], 0)

    def test_rating_schema_rejects_invalid_enum_and_overlong_notes(self):
        with self.assertRaises(Exception):
            self.rating(rating="maybe")
        with self.assertRaises(Exception):
            self.rating(notes="x" * 2001)

    def test_firm_rating_list_and_csv_export_are_scoped_and_formula_safe(self):
        app.save_answer_rating(self.answer_id, self.rating(notes="=HYPERLINK(\"x\")"), self.user)
        listed = app.list_firm_answer_ratings(100, 0, self.user)
        self.assertEqual(listed["total"], 1)
        self.assertEqual(len(listed["items"]), 1)
        response = app.export_firm_answer_ratings_csv(self.user)
        self.assertTrue(response.body.startswith(b"\xef\xbb\xbf"))
        text = response.body.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["question"], "'=SUM(1,1)")
        self.assertEqual(rows[0]["notes"], "'=HYPERLINK(\"x\")")
        self.assertEqual(rows[0]["benchmark_ready"], "true")
        self.assertEqual(rows[0]["cited_article_ids"], '["LABOUR::article:12"]')
        self.assertNotIn("Firm B", text)
        audit = self.db.execute("SELECT event FROM security_audit_events").fetchone()[0]
        self.assertEqual(audit, "answer_rating_export:count=1")


if __name__ == "__main__":
    unittest.main()
