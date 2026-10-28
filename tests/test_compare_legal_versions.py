import hashlib
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.compare_legal_versions import (
    compare_registered_versions, compare_version_chunks, default_database_path,
)


class CompareLegalVersionsTests(unittest.TestCase):
    def test_default_registry_path_uses_corpus_profile_not_legacy_database(self):
        path = default_database_path({
            "COPILOT_CORPUS_DB": "/srv/legal/corpus.sqlite3",
            "COPILOT_DB": "/srv/legal/legacy.sqlite3",
        })
        self.assertEqual(path, Path("/srv/legal/corpus.sqlite3"))

    def test_default_registry_path_refuses_implicit_legacy_fallback(self):
        with self.assertRaisesRegex(ValueError, "COPILOT_DB is not a supported default"):
            default_database_path({"COPILOT_DB": "/srv/legal/legacy.sqlite3"})

    def test_compares_by_article_and_reports_changes_and_unmapped_passages(self):
        left = [
            {"id": 1, "article": "1", "page": "2", "text": "same text"},
            {"id": 2, "article": "2", "page": "3", "text": "old wording"},
            {"id": 3, "article": "3", "page": "4", "text": "removed wording"},
            {"id": 4, "article": None, "page": "5", "text": "unmapped old passage"},
        ]
        right = [
            {"id": 11, "article": "1", "page": "7", "text": " same   text "},
            {"id": 12, "article": "2", "page": "8", "text": "new wording"},
            {"id": 13, "article": "4", "page": "9", "text": "added wording"},
            {"id": 14, "article": "", "page": "10", "text": "unmapped new passage"},
        ]
        result = compare_version_chunks(left, right)
        self.assertEqual(result["summary"], {
            "added_in_right": 1,
            "removed_from_right": 1,
            "changed": 1,
            "unchanged": 1,
            "unmapped_left_passages": 1,
            "unmapped_right_passages": 1,
            "malformed_left_passages": 0,
            "malformed_right_passages": 0,
            "duplicate_left_chunk_ids": 0,
            "duplicate_right_chunk_ids": 0,
            "uncomparable_incomplete_text": 0,
        })
        changes = {item["article"]: item["change"] for item in result["provisions"]}
        self.assertEqual(changes, {
            "1": "unchanged", "2": "changed", "3": "removed_from_right", "4": "added_in_right"
        })
        changed = next(item for item in result["provisions"] if item["article"] == "2")
        self.assertIn("-old wording", changed["unified_diff"])
        self.assertIn("+new wording", changed["unified_diff"])
        self.assertIn("not a legal conclusion", " ".join(result["warnings"]))

    def test_aggregates_multiple_chunks_for_same_article_in_id_order(self):
        result = compare_version_chunks(
            [
                {"id": 1, "article": "12", "page": "1", "text": "first"},
                {"id": 2, "article": "12", "page": "2", "text": "second"},
            ],
            [
                {"id": 3, "article": "12", "page": "3", "text": "first"},
                {"id": 4, "article": "12", "page": "4", "text": "second"},
            ],
        )
        self.assertEqual(result["summary"]["unchanged"], 1)
        self.assertEqual(result["provisions"][0]["left_pages"], ["1", "2"])
        self.assertEqual(result["provisions"][0]["right_pages"], ["3", "4"])

    def test_missing_text_does_not_get_misclassified_as_added_or_removed(self):
        result = compare_version_chunks(
            [{"id": 1, "article": "5", "page": "2", "text": None}],
            [{"id": 2, "article": "5", "page": "3", "text": "valid extracted text"}],
        )
        self.assertEqual(result["summary"]["uncomparable_incomplete_text"], 1)
        self.assertEqual(result["summary"]["malformed_left_passages"], 1)
        self.assertEqual(result["provisions"][0]["change"], "uncomparable_incomplete_text")
        self.assertEqual(result["unmapped_passages"]["left"][0]["unmapped_reason"], "missing_or_invalid_text")
        self.assertTrue(any("Malformed or empty extracted passages" in warning for warning in result["warnings"]))

    def test_duplicate_chunk_ids_exclude_all_occurrences_and_make_article_uncomparable(self):
        result = compare_version_chunks(
            [
                {"id": 7, "article": "8", "page": "1", "text": "first copy"},
                {"id": 7, "article": "8", "page": "2", "text": "second copy"},
                {"id": 8, "article": "9", "page": "3", "text": "valid other article"},
            ],
            [{"id": 70, "article": "8", "page": "4", "text": "right text"}],
        )
        self.assertEqual(result["summary"]["duplicate_left_chunk_ids"], 1)
        self.assertEqual(result["summary"]["duplicate_right_chunk_ids"], 0)
        self.assertEqual(result["summary"]["unmapped_left_passages"], 2)
        self.assertEqual(
            [item["unmapped_reason"] for item in result["unmapped_passages"]["left"]],
            ["duplicate_chunk_id", "duplicate_chunk_id"],
        )
        changes = {item["article"]: item["change"] for item in result["provisions"]}
        self.assertEqual(changes["8"], "uncomparable_incomplete_text")
        self.assertEqual(changes["9"], "removed_from_right")

    def test_duplicate_chunk_id_across_article_labels_marks_both_uncomparable(self):
        result = compare_version_chunks(
            [
                {"id": 4, "article": "1", "page": "1", "text": "text one"},
                {"id": 4, "article": "2", "page": "2", "text": "text two"},
            ],
            [],
        )
        changes = {item["article"]: item["change"] for item in result["provisions"]}
        self.assertEqual(changes, {
            "1": "uncomparable_incomplete_text",
            "2": "uncomparable_incomplete_text",
        })
        self.assertEqual(result["summary"]["duplicate_left_chunk_ids"], 1)

    def test_non_object_chunk_record_is_reported_without_crashing(self):
        result = compare_version_chunks(
            [None, {"id": 2, "article": "6", "page": "2", "text": "left"}],
            [{"id": 3, "article": "6", "page": "3", "text": "right"}],
        )
        self.assertEqual(result["summary"]["malformed_left_passages"], 1)
        self.assertEqual(result["unmapped_passages"]["left"][0]["unmapped_reason"], "invalid_chunk_record")
        self.assertEqual(result["summary"]["changed"], 1)


    def _database(self, path):
        db = sqlite3.connect(path)
        db.executescript("""
            CREATE TABLE legal_documents(
                document_id TEXT PRIMARY KEY, official_title TEXT NOT NULL,
                law_number TEXT, law_year INTEGER
            );
            CREATE TABLE legal_document_versions(
                version_id INTEGER PRIMARY KEY, document_id TEXT NOT NULL,
                version_label TEXT NOT NULL, source_url TEXT NOT NULL,
                publication_date TEXT, effective_date TEXT, repeal_date TEXT,
                legal_status TEXT, review_status TEXT, authenticity_verified INTEGER,
                status_verified INTEGER, amendment_history_verified INTEGER,
                gazette_issue TEXT, gazette_pages TEXT
            );
            CREATE TABLE chunks(
                id INTEGER PRIMARY KEY, document_version_id INTEGER,
                article TEXT, page TEXT, text TEXT
            );
            INSERT INTO legal_documents VALUES('D1','Test law','12',2020);
            INSERT INTO legal_document_versions VALUES
                (1,'D1','original','https://example.gov/original.pdf','2020-01-01','2020-02-01',NULL,'in_force','verified',1,1,1,'10','2-5'),
                (2,'D1','amended','https://example.gov/amended.pdf','2024-01-01','2024-03-01',NULL,'in_force','verified',1,1,1,'20','4-8');
            INSERT INTO chunks VALUES
                (1,1,'1','2','old passage'),
                (2,2,'1','4','new passage');
        """)
        db.commit()
        db.close()

    def test_registered_comparison_reads_database_without_modifying_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.sqlite"
            self._database(path)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            result = compare_registered_versions(path, 1, 2)
            after = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(before, after)
        self.assertEqual(result["document"]["document_id"], "D1")
        self.assertEqual(result["left_version"]["version_label"], "original")
        self.assertEqual(result["right_version"]["version_label"], "amended")
        self.assertEqual(result["summary"]["changed"], 1)

    def test_rejects_same_version_and_cross_document_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.sqlite"
            self._database(path)
            with self.assertRaisesRegex(ValueError, "different version IDs"):
                compare_registered_versions(path, 1, 1)
            db = sqlite3.connect(path)
            db.execute("INSERT INTO legal_documents VALUES('D2','Other law','9',2022)")
            db.execute(
                "INSERT INTO legal_document_versions VALUES(3,'D2','other','https://example.gov/other.pdf',NULL,NULL,NULL,'unknown','pending_source_review',0,0,0,NULL,NULL)"
            )
            db.commit()
            db.close()
            with self.assertRaisesRegex(ValueError, "different legal documents"):
                compare_registered_versions(path, 1, 3)

    def test_missing_schema_and_missing_version_fail_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty.sqlite"
            sqlite3.connect(empty).close()
            with self.assertRaisesRegex(ValueError, "missing required tables"):
                compare_registered_versions(empty, 1, 2)
            db = Path(tmp) / "registry.sqlite"
            self._database(db)
            with self.assertRaisesRegex(ValueError, "version ID not found"):
                compare_registered_versions(db, 1, 99)


if __name__ == "__main__":
    unittest.main()
