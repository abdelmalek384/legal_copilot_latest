"""Contract tests for the firm-local lawyer answer-rating migration."""
import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "firm" / "0021_answer_ratings.sql"


class AnswerRatingMigrationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute(
            "CREATE TABLE research_messages ("
            "id INTEGER PRIMARY KEY, conversation_id INTEGER NOT NULL, "
            "role TEXT NOT NULL, content TEXT NOT NULL)"
        )
        self.db.execute(
            "INSERT INTO research_messages(id,conversation_id,role,content) "
            "VALUES (1,10,'assistant','A generated answer')"
        )
        self.db.executescript(MIGRATION.read_text(encoding="utf-8"))

    def tearDown(self):
        self.db.close()

    def insert_rating(self, **overrides):
        values = {
            "answer_message_id": 1,
            "answer_id": "ans_123456789",
            "rating": "partially_correct",
            "cited_article_accuracy": "wrong",
            "expected_article_ids_json": '["LABOUR::article:12"]',
            "answerable": 1,
            "notes": "Wrong article cited.",
            "rated_by": 7,
        }
        values.update(overrides)
        columns = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)
        return self.db.execute(
            f"INSERT INTO answer_ratings ({columns}) VALUES ({placeholders})",
            tuple(values.values()),
        )

    def test_accepts_complete_rating_and_expected_article_label(self):
        self.insert_rating()
        row = self.db.execute(
            "SELECT rating,cited_article_accuracy,expected_article_ids_json,answerable "
            "FROM answer_ratings"
        ).fetchone()
        self.assertEqual(row, (
            "partially_correct", "wrong", '["LABOUR::article:12"]', 1
        ))

    def test_one_current_rating_per_reviewer_per_answer(self):
        self.insert_rating()
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_rating(rating="correct", cited_article_accuracy="right")

    def test_rating_enums_and_answerability_are_constrained(self):
        for changes in (
            {"rating": "maybe"},
            {"cited_article_accuracy": "unknown"},
            {"answerable": 2},
            {"expected_article_ids_json": '{"article":"12"}'},
        ):
            with self.subTest(changes=changes), self.assertRaises(sqlite3.IntegrityError):
                self.insert_rating(**changes)

    def test_notes_are_bounded(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_rating(notes="x" * 2001)

    def test_rating_cannot_be_detached_from_its_answer_message(self):
        self.insert_rating()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("DELETE FROM research_messages WHERE id=1")

    def test_rating_event_ledger_is_append_only(self):
        rating_id = self.insert_rating().lastrowid
        self.db.execute(
            "INSERT INTO answer_rating_events(rating_id,actor_user_id,event_type) "
            "VALUES (?,7,'created')",
            (rating_id,),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE answer_rating_events SET event_type='updated' WHERE rating_id=?",
                (rating_id,),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "DELETE FROM answer_rating_events WHERE rating_id=?",
                (rating_id,),
            )


if __name__ == "__main__":
    unittest.main()
