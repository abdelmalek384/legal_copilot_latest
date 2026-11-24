"""Regression tests for firm-scoped, source-anchored passage annotations."""
from __future__ import annotations

import hashlib
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "firm" / "0025_document_passage_annotations.sql"


class PassageAnnotationMigrationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER NOT NULL);
            CREATE TABLE docs(id INTEGER PRIMARY KEY, case_id INTEGER NOT NULL REFERENCES cases(id), firm_id INTEGER NOT NULL);
            CREATE TABLE chunks(id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES docs(id),
                                case_id INTEGER NOT NULL REFERENCES cases(id), text TEXT NOT NULL);
            INSERT INTO cases(id,firm_id) VALUES(10,7),(20,8);
            INSERT INTO docs(id,case_id,firm_id) VALUES(100,10,7),(200,20,8);
            INSERT INTO chunks(id,document_id,case_id,text) VALUES
                (1000,100,10,'Original evidence passage'),(2000,200,20,'Other firm passage');
        """)
        self.db.executescript(MIGRATION.read_text(encoding="utf-8"))

    def tearDown(self):
        self.db.close()

    def insert_annotation(self):
        source = "Original evidence passage"
        return self.db.execute(
            """INSERT INTO document_passage_annotations(
                document_id,case_id,firm_id,chunk_id,created_by_user_id,start_offset,end_offset,
                selected_text,source_text_sha256,note,color
            ) VALUES(100,10,7,1000,55,0,8,'Original',?,'Check this clause','yellow')""",
            (hashlib.sha256(source.encode("utf-8")).hexdigest(),),
        ).lastrowid

    def test_annotation_is_bound_to_matching_firm_case_document_and_chunk(self):
        self.insert_annotation()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "scope mismatch"):
            self.db.execute(
                """INSERT INTO document_passage_annotations(
                    document_id,case_id,firm_id,chunk_id,created_by_user_id,start_offset,end_offset,
                    selected_text,source_text_sha256,note
                ) VALUES(100,10,8,1000,55,0,8,'Original',?,'wrong firm')""",
                ("a" * 64,),
            )

    def test_document_firm_id_must_match_case_and_annotation_firm(self):
        self.db.execute("UPDATE docs SET firm_id=8 WHERE id=100")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "scope mismatch"):
            self.insert_annotation()

    def test_annotation_content_is_immutable_but_soft_delete_is_allowed_once(self):
        annotation_id = self.insert_annotation()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
            self.db.execute(
                "UPDATE document_passage_annotations SET note='tampered' WHERE id=?",
                (annotation_id,),
            )
        self.db.execute(
            "UPDATE document_passage_annotations SET deleted_at=datetime('now'),deleted_by_user_id=55 WHERE id=?",
            (annotation_id,),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
            self.db.execute(
                "UPDATE document_passage_annotations SET deleted_at=datetime('now','+1 second') WHERE id=?",
                (annotation_id,),
            )

    def test_parent_document_retention_cascade_removes_annotations(self):
        annotation_id = self.insert_annotation()
        self.db.execute("DELETE FROM docs WHERE id=100")
        remaining = self.db.execute(
            "SELECT COUNT(*) FROM document_passage_annotations WHERE id=?", (annotation_id,)
        ).fetchone()[0]
        self.assertEqual(remaining, 0)

    def test_parent_case_retention_cascade_removes_annotations(self):
        annotation_id = self.insert_annotation()
        self.db.execute("DELETE FROM cases WHERE id=10")
        remaining = self.db.execute(
            "SELECT COUNT(*) FROM document_passage_annotations WHERE id=?", (annotation_id,)
        ).fetchone()[0]
        self.assertEqual(remaining, 0)

    def test_active_annotations_cannot_overlap_but_soft_deleted_ranges_can_be_reused(self):
        first = self.insert_annotation()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "overlaps an active"):
            self.db.execute(
                """INSERT INTO document_passage_annotations(
                    document_id,case_id,firm_id,chunk_id,created_by_user_id,start_offset,end_offset,
                    selected_text,source_text_sha256,note,color
                ) VALUES(100,10,7,1000,55,4,12,'ginal evi',?,'overlap','blue')""",
                (hashlib.sha256(b"Original evidence passage").hexdigest(),),
            )
        self.db.execute(
            "UPDATE document_passage_annotations SET deleted_at=datetime('now'),deleted_by_user_id=55 WHERE id=?",
            (first,),
        )
        reused = self.db.execute(
            """INSERT INTO document_passage_annotations(
                document_id,case_id,firm_id,chunk_id,created_by_user_id,start_offset,end_offset,
                selected_text,source_text_sha256,note,color
            ) VALUES(100,10,7,1000,55,4,12,'ginal evi',?,'replacement','blue')""",
            (hashlib.sha256(b"Original evidence passage").hexdigest(),),
        )
        self.assertGreater(reused.lastrowid, first)

    def test_original_chunk_text_is_not_mutated_by_annotation_storage(self):
        self.insert_annotation()
        original = self.db.execute("SELECT text FROM chunks WHERE id=1000").fetchone()[0]
        self.assertEqual(original, "Original evidence passage")


class PassageAnnotationApiContractTests(unittest.TestCase):
    def test_create_route_checks_matter_access_digest_and_exact_offsets(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        start = app.index("def create_document_passage_annotation(")
        end = app.index('@app.delete("/cases/{cid}/docs/{document_id}/annotations/{annotation_id}")', start)
        route = app[start:end]
        for required in (
            "need(c, u, cid)",
            "d.firm_id=?",
            "hashlib.sha256(source_text.encode(\"utf-8\")).hexdigest()",
            "b.source_text_sha256 != actual_digest",
            "source_text[b.start_offset:b.end_offset] != b.selected_text",
            "start_offset < ? AND end_offset > ?",
            "overlaps an active passage annotation",
            "document_passage_annotation_created",
        ):
            self.assertIn(required, route)

    def test_document_chunk_response_includes_only_active_scoped_annotations(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        start = app.index("def list_document_chunks(")
        end = app.index('@app.get("/cases/{cid}/docs/{document_id}/reviews")', start)
        route = app[start:end]
        self.assertIn("WHERE firm_id=? AND case_id=? AND document_id=? AND deleted_at IS NULL", route)
        self.assertIn('item["annotations"] = annotations_by_chunk.get(int(item["id"]), [])', route)

    def test_frontend_anchors_offsets_to_original_chunk_and_marks_stale_text(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        start = html.index("const renderChunkReviewCards=()=>{")
        end = html.index("const renderAnalysis=()=>{", start)
        review = html[start:end]
        for required in (
            "window.getSelection()",
            "Array.from(prefix.toString()).length",
            "source_text_sha256:chunk.text_sha256",
            "passage-annotation-highlight",
            "The passage changed after this annotation",
            "Passage text for review and highlighting",
            "Latest recorded correction (working copy)",
        ):
            self.assertIn(required, review)

    def test_list_and_delete_routes_are_matter_and_firm_scoped(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        start = app.index('@app.get("/cases/{cid}/docs/{document_id}/chunks/{chunk_id}/annotations")')
        end = app.index('@app.get("/cases/{cid}/docs/{document_id}/reviews")', start)
        routes = app[start:end]
        self.assertIn("need(c, u, cid)", routes)
        self.assertIn("firm_id=? AND case_id=? AND document_id=? AND chunk_id=?", routes)
        self.assertIn("deleted_at IS NULL", routes)
        self.assertIn("created_by_user_id", routes)
        self.assertIn("is_lead(c, u, cid)", routes)


if __name__ == "__main__":
    unittest.main()
