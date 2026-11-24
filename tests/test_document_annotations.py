"""Regression tests for persistent matter-scoped document annotations."""
import hashlib
import sqlite3
import unittest
from pathlib import Path

from schema_profiles import apply_profile_migrations

ROOT = Path(__file__).resolve().parents[1]


class DocumentAnnotationSchemaTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        apply_profile_migrations(self.db, "firm", ROOT / "migrations")
        self.db.execute(
            "INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,7)"
        )
        self.db.execute(
            "INSERT INTO cases(id,title,firm_id) VALUES(1,'Matter A',7)"
        )
        self.db.execute(
            "INSERT INTO docs(id,case_id,name,firm_id) VALUES(2,1,'source.pdf',7)"
        )
        self.db.execute(
            "INSERT INTO chunks(id,ref,page,text,norm,case_id,document_id) "
            "VALUES(3,'p1','1','alpha beta','alpha beta',1,2)"
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def create_annotation(self, **overrides):
        values = {
            "document_id": 2, "case_id": 1, "firm_id": 7, "chunk_id": 3,
            "author_user_id": 9, "annotation_type": "highlight",
            "start_offset": 6, "end_offset": 10, "quoted_text": "beta",
            "body": "", "page_reference": "1",
            "text_sha256": hashlib.sha256(b"alpha beta").hexdigest(),
        }
        values.update(overrides)
        columns = ",".join(values)
        placeholders = ",".join("?" for _ in values)
        return self.db.execute(
            f"INSERT INTO document_annotations({columns}) VALUES({placeholders})",
            tuple(values.values()),
        )

    def test_firm_migration_installs_annotation_tables_and_scope_guards(self):
        tables = {
            row["name"] for row in self.db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        self.assertTrue({
            "document_annotations", "document_annotation_events"
        } <= tables)
        self.create_annotation()
        self.db.commit()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only"):
            self.db.execute(
                "UPDATE document_annotations SET body='changed' WHERE id=1"
            )

    def test_annotation_rejects_cross_document_or_case_chunk(self):
        with self.assertRaisesRegex(sqlite3.IntegrityError, "scope mismatch"):
            self.create_annotation(document_id=999)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "scope mismatch"):
            self.create_annotation(firm_id=8)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "scope mismatch"):
            self.create_annotation(chunk_id=999)

    def test_parent_document_deletion_cascades_annotations_and_events(self):
        cursor = self.create_annotation()
        annotation_id = cursor.lastrowid
        self.db.execute(
            "INSERT INTO document_annotation_events("
            "annotation_id,firm_id,case_id,document_id,actor_user_id,action"
            ") VALUES(?,7,1,2,9,'created')",
            (annotation_id,),
        )
        self.db.commit()
        self.db.execute("DELETE FROM docs WHERE id=2")
        self.db.commit()
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM document_annotations").fetchone()[0],
            0,
        )
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM document_annotation_events").fetchone()[0],
            0,
        )


class DocumentAnnotationAPITests(unittest.TestCase):
    def test_api_binds_annotations_to_authorized_matter_and_text_version(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('@app.get("/cases/{cid}/docs/{document_id}/annotations")', app)
        self.assertIn('@app.post("/cases/{cid}/docs/{document_id}/annotations", status_code=201)', app)
        endpoint = app[app.index("def create_document_annotation("):app.index('@app.get("/cases/{cid}/documents/timeline")')]
        self.assertIn("need(c, u, cid)", endpoint)
        self.assertIn("SELECT id FROM docs WHERE id=? AND case_id=? AND firm_id=?", endpoint)
        self.assertIn("WHERE id=? AND document_id=? AND case_id=?", endpoint)
        self.assertIn("hmac.compare_digest(current_digest, b.text_sha256)", endpoint)
        self.assertIn("source_text[b.start_offset:b.end_offset] != b.quoted_text", endpoint)
        self.assertIn("document_annotation_events", endpoint)
        self.assertIn("document_annotation_created", endpoint)

    def test_quote_is_preserved_exactly_for_unicode_source_offsets(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        model = app[app.index("class DocumentAnnotationIn"):app.index('@app.get("/cases/{cid}/docs/{document_id}/annotations")')]
        self.assertIn('Field(pattern=r"^(highlight|note)$")', model)
        quote_validator = model[model.index('@field_validator("quoted_text")'):]
        self.assertIn("return value", quote_validator)
        self.assertNotIn('return value.strip()', quote_validator)

    def test_bilingual_ui_captures_and_saves_selected_passage_annotations(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("التقاط التحديد", html)
        self.assertIn("Capture selection", html)
        self.assertIn("حفظ التظليل", html)
        self.assertIn("Save highlight", html)
        self.assertIn("حفظ الملاحظة", html)
        self.assertIn("Save note", html)
        self.assertIn("Array.from(fullText.slice(0,range.startOffset)).length", html)
        self.assertIn("text_sha256:chunk.text_sha256", html)
        self.assertIn("stale_anchor", html)
        self.assertIn("item.annotations=Array.isArray(annotationData.annotations)?annotationData.annotations:[]", html)


if __name__ == "__main__":
    unittest.main()
