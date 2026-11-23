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

    def test_client_wide_search_is_client_and_membership_scoped(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        search = app[
            app.index('def search_client_document_text('):
            app.index('@app.get("/documents/search")')
        ]
        self.assertIn("cs.client_id=?", search)
        self.assertIn("cs.firm_id=?", search)
        self.assertIn("m.case_id=cs.id AND m.user_id=?", search)
        self.assertIn("chunks_fts MATCH ?", search)
        self.assertIn("ORDER BY rank,chunks.id LIMIT ? OFFSET ?", search)
        self.assertIn("limit: int = Query(default=40, ge=1, le=100)", search)
        self.assertIn("client_document_text_search", search)

    def test_client_profile_ui_exposes_cross_matter_document_search(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("const clientSearchPanel=client=>", html)
        self.assertIn("/documents/search-text?q=", html)
        self.assertIn("Client-wide document search", html)
        self.assertIn("&limit=40&offset='+offset", html)
        self.assertIn("Open passage in matter", html)
        self.assertIn("chunkId:String(item.chunk_id)", html)


    def test_annotation_controls_expose_passage_help_and_list_semantics(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        page = html[html.index("const renderChunkReviewCards="):html.index("const renderAnalysis=()=>{")]
        self.assertIn("tabIndex:0,'aria-label':uiText('النص المستخرج للمقطع '", page)
        self.assertIn("setAttribute('aria-describedby',passageHelpId)", page)
        self.assertIn("role:'list','aria-label':uiText('قائمة التظليلات والملاحظات'", page)
        self.assertIn("role:'listitem'", page)
        self.assertIn("role:'group','aria-label':uiText('إعدادات التظليل والملاحظة'", page)

    def test_review_history_disclosure_tracks_expanded_state(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        page = html[html.index("const renderChunkReviewCards="):html.index("const renderAnalysis=()=>{")]
        self.assertIn("role:'region','aria-label':uiText('سجل مراجعة النص المستخرج'", page)
        self.assertIn("historyButton.setAttribute('aria-controls',historyResults.id)", page)
        self.assertIn("historyButton.setAttribute('aria-expanded','false')", page)
        self.assertIn("historyButton.setAttribute('aria-expanded','true')", page)
        self.assertIn("uiText('إخفاء سجل المراجعة','Hide review history')", page)

    def test_review_ui_highlights_selected_text_and_marks_stale_offsets(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        page = html[html.index("const renderChunkReviewCards="):html.index("const renderAnalysis=()=>{")]
        self.assertIn("window.getSelection()", page)
        self.assertIn("Array.from(prefix.toString()).length", page)
        self.assertIn("source_text_sha256:chunk.text_sha256", page)
        self.assertIn("passage-annotation-highlight", page)
        self.assertIn("Remove highlight", page)
        self.assertIn("The passage changed after this annotation", page)

    def test_annotations_remain_anchored_to_original_extracted_text_after_correction(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        page = html[html.index("const renderChunkReviewCards="):html.index("const renderAnalysis=()=>{")]
        self.assertIn("const currentText=String(chunk.text||'')", page)
        self.assertIn("Original extracted passage for highlighting", page)
        self.assertIn("Latest recorded correction (working copy)", page)
