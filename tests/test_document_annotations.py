"""Regression tests for persistent matter-scoped document annotations."""
import hashlib
import sqlite3
import unittest
from pathlib import Path

from schema_profiles import apply_profile_migrations
from tests.invoice_test_support import InvoiceTestSupport

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

    def test_schema_rejects_malformed_digest_and_blank_note(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.create_annotation(text_sha256="z" * 64)
        with self.assertRaises(sqlite3.IntegrityError):
            self.create_annotation(annotation_type="note", body="")

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
        self.assertIn("@rollback_tenant_transaction_on_error", app[app.index('@app.get("/cases/{cid}/docs/{document_id}/annotations")'):app.index("def list_document_annotations(")])
        self.assertIn("SELECT id FROM docs WHERE id=? AND case_id=? AND firm_id=?", endpoint)
        self.assertIn("WHERE ch.id=? AND ch.document_id=? AND ch.case_id=?", endpoint)
        self.assertIn("AND d.firm_id=? AND cs.firm_id=?", endpoint)
        self.assertIn("hmac.compare_digest(current_digest, b.text_sha256)", endpoint)
        self.assertIn("source_text[b.start_offset:b.end_offset] != b.quoted_text", endpoint)
        self.assertIn("INSERT INTO document_annotations(", endpoint)
        self.assertIn("AND ch.text=?", endpoint)
        self.assertIn("cursor.rowcount != 1", endpoint)
        self.assertIn("requested_page_reference != page_reference", endpoint)
        self.assertIn("document_annotation_events", endpoint)
        self.assertIn("document_annotation_created", endpoint)
        self.assertIn("WHERE a.firm_id=? AND c.firm_id=?", app)
        self.assertIn("WHERE e.firm_id=? AND c.firm_id=?", app)
        self.assertIn('bucket = "document_annotations"', app)
        self.assertIn("limit = (30, 60)", app)

    def test_list_api_joins_firm_parents_and_marks_stale_source_anchors(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        endpoint = app[app.index("def list_document_annotations("):app.index('@app.post("/cases/{cid}/docs/{document_id}/annotations"')]
        self.assertIn("need(c, u, cid)", endpoint)
        self.assertIn("JOIN docs d ON d.id=a.document_id", endpoint)
        self.assertIn("JOIN cases c ON c.id=a.case_id", endpoint)
        self.assertIn("JOIN chunks ch ON ch.id=a.chunk_id", endpoint)
        self.assertIn("a.firm_id=? AND c.firm_id=?", endpoint)
        self.assertIn('item["stale_anchor"]', endpoint)
        self.assertIn("current_page", endpoint)
        self.assertIn("str(current_page) != str(item[\"page_reference\"])", endpoint)
        self.assertIn('item["author_name"]', endpoint)

    def test_quote_is_preserved_exactly_for_unicode_source_offsets(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        model = app[app.index("class DocumentAnnotationIn"):app.index('@app.get("/cases/{cid}/docs/{document_id}/annotations")')]
        self.assertIn('Field(pattern=r"^(highlight|note)$")', model)
        quote_validator = model[model.index('@field_validator("quoted_text")'):]
        self.assertIn("return value", quote_validator)
        self.assertNotIn('return value.strip()', quote_validator)

    def test_matter_deletion_audit_counts_annotation_rows_before_cascade(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        delete_case = app[app.index("def delete_case(c, u, cid):"):app.index("def _qualified_egyptian_counsel_user_ids")]
        self.assertIn('"document_annotations", "document_annotation_events"', delete_case)
        self.assertIn("related_counts[table]", delete_case)
        self.assertIn("sqlite_master", delete_case)

    def test_bilingual_ui_captures_and_saves_selected_passage_annotations(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("التقاط التحديد", html)
        self.assertIn("Capture selection", html)
        self.assertIn("حفظ التظليل", html)
        self.assertIn("Save highlight", html)
        self.assertIn("حفظ الملاحظة", html)
        self.assertIn("Save note", html)
        self.assertIn("Array.from(fullText.slice(0,range.startOffset)).length", html)
        self.assertIn("pendingSelectionRange", html)
        self.assertIn("getRangeAt(0).cloneRange()", html)
        self.assertIn("text_sha256:chunk.text_sha256", html)
        self.assertIn("stale_anchor", html)
        self.assertIn("annotationError", html)
        self.assertIn("Could not load saved annotations", html)
        self.assertIn("#main .document-annotation-controls .row button{flex:1 1 140px}", html)
        self.assertIn("item.annotations=Array.isArray(annotationData.annotations)?annotationData.annotations:[]", html)




class DocumentAnnotationAPIRuntimeTests(InvoiceTestSupport, unittest.TestCase):
    def test_annotation_persists_across_case_switch_and_stales_after_source_correction(self):
        source = "Alpha 🧑‍⚖️ source passage for a synthetic annotation acceptance test."
        uploaded = self.mutate(
            self.client_a, "post", f"/cases/{self.case_id}/docs",
            json={"name": "annotation-source.txt", "text": source},
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        matter = self.mutate(self.client_a, "get", f"/cases/{self.case_id}")
        self.assertEqual(matter.status_code, 200, matter.text)
        document_id = next(
            item["document_id"] for item in matter.json()["docs"]
            if item["name"] == "annotation-source.txt"
        )
        chunk_response = self.mutate(
            self.client_a, "get",
            f"/cases/{self.case_id}/docs/{document_id}/chunks",
        )
        self.assertEqual(chunk_response.status_code, 200, chunk_response.text)
        chunk = chunk_response.json()["chunks"][0]
        page_reference = str(chunk.get("page") or "")
        quote = "source passage"
        start = chunk["text"].index(quote)
        payload = {
            "chunk_id": chunk["id"],
            "annotation_type": "note",
            "start_offset": start,
            "end_offset": start + len(quote),
            "quoted_text": quote,
            "body": "Verify this passage against the uploaded original.",
            "page_reference": page_reference,
            "text_sha256": chunk["text_sha256"],
        }
        created = self.mutate(
            self.client_a, "post",
            f"/cases/{self.case_id}/docs/{document_id}/annotations",
            json=payload,
        )
        self.assertEqual(created.status_code, 201, created.text)
        highlight_quote = "synthetic annotation"
        highlight_start = chunk["text"].index(highlight_quote)
        highlight_payload = {
            **payload,
            "annotation_type": "highlight",
            "start_offset": highlight_start,
            "end_offset": highlight_start + len(highlight_quote),
            "quoted_text": highlight_quote,
            "body": "",
        }
        highlighted = self.mutate(
            self.client_a, "post",
            f"/cases/{self.case_id}/docs/{document_id}/annotations",
            json=highlight_payload,
        )
        self.assertEqual(highlighted.status_code, 201, highlighted.text)

        listed = self.mutate(
            self.client_a, "get",
            f"/cases/{self.case_id}/docs/{document_id}/annotations",
        )
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual(len(listed.json()["annotations"]), 2)
        self.assertEqual(
            {item["annotation_type"] for item in listed.json()["annotations"]},
            {"note", "highlight"},
        )
        self.assertTrue(all(not item["stale_anchor"] for item in listed.json()["annotations"]))
        self.assertIn("Invoice Owner A", {item["author_name"] for item in listed.json()["annotations"]})

        second_case = self.mutate(
            self.client_a, "post", "/cases",
            json={"title": "Second matter, same client", "client": "Client Snapshot"},
        )
        self.assertEqual(second_case.status_code, 200, second_case.text)
        second_case_id = second_case.json()["id"]
        self.assertEqual(
            self.mutate(self.client_a, "get", f"/cases/{second_case_id}").status_code,
            200,
        )
        self.assertEqual(
            self.mutate(
                self.client_a, "get",
                f"/cases/{self.case_id}/docs/{document_id}/annotations",
            ).status_code,
            200,
        )
        self.assertEqual(
            self.mutate(
                self.client_a, "get",
                f"/cases/{second_case_id}/docs/{document_id}/annotations",
            ).status_code,
            404,
        )
        self.assertEqual(
            self.mutate(
                self.client_b, "get",
                f"/cases/{self.case_id}/docs/{document_id}/annotations",
            ).status_code,
            404,
        )

        corrected_text = chunk["text"].replace("source passage", "revised source passage")
        reviewed = self.mutate(
            self.client_a, "post",
            f"/cases/{self.case_id}/docs/{document_id}/chunks/{chunk['id']}/review",
            json={
                "outcome": "corrected",
                "corrected_text": corrected_text,
                "expected_text_sha256": chunk["text_sha256"],
                "page_reference": page_reference,
                "note": "Synthetic correction to test stale annotation handling.",
            },
        )
        self.assertEqual(reviewed.status_code, 201, reviewed.text)
        stale = self.mutate(
            self.client_a, "get",
            f"/cases/{self.case_id}/docs/{document_id}/annotations",
        )
        self.assertEqual(stale.status_code, 200, stale.text)
        self.assertTrue(all(item["stale_anchor"] for item in stale.json()["annotations"]))

        old_anchor_write = self.mutate(
            self.client_a, "post",
            f"/cases/{self.case_id}/docs/{document_id}/annotations",
            json=payload,
        )
        self.assertEqual(old_anchor_write.status_code, 409, old_anchor_write.text)


if __name__ == "__main__":
    unittest.main()
