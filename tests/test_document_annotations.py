"""Regression contracts for persisted document passage annotations."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DocumentPassageAnnotationTests(unittest.TestCase):
    def test_firm_migration_binds_annotations_to_document_case_and_chunk(self):
        migration = (ROOT / "migrations" / "firm" / "0025_document_passage_annotations.sql").read_text(encoding="utf-8")
        self.assertIn("document_passage_annotations_scope_insert", migration)
        self.assertIn("document_passage_annotations_scope_update", migration)
        self.assertIn("document_passage_annotations_immutable", migration)
        self.assertIn("source_text_sha256", migration)
        self.assertIn("deleted_by_user_id", migration)

    def test_api_checks_digest_and_exact_selected_text(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        create = app[
            app.index("def create_document_passage_annotation("):
            app.index('@app.delete("/cases/{cid}/docs/{document_id}/annotations/{annotation_id}")')
        ]
        self.assertIn("need(c, u, cid)", create)
        self.assertIn("b.source_text_sha256 != actual_digest", create)
        self.assertIn("source_text[b.start_offset:b.end_offset] != b.selected_text", create)
        self.assertIn("document_passage_annotations", create)

    def test_review_ui_highlights_selected_text_and_marks_stale_offsets(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        page = html[html.index("const renderChunkReviewCards="):html.index("const renderAnalysis=()=>{")]
        self.assertIn("window.getSelection()", page)
        self.assertIn("Array.from(prefix.toString()).length", page)
        self.assertIn("source_text_sha256:chunk.text_sha256", page)
        self.assertIn("passage-annotation-highlight", page)
        self.assertIn("Remove highlight", page)
        self.assertIn("The passage changed after this annotation", page)
