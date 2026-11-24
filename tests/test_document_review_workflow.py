"""Contract tests for the document extraction review API and UI workflow."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentReviewWorkflowTests(unittest.TestCase):
    def test_api_exposes_case_scoped_chunk_review(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('@app.get("/cases/{cid}/docs/{document_id}/chunks")', app)
        self.assertIn("document_extraction_reviews", app)
        self.assertIn('item["text_sha256"] = hashlib.sha256', app)
        self.assertIn('need(c, u, cid)', app)

    def test_ui_can_accept_correct_and_flag_extraction(self):
        html = (ROOT / "static/index.html").read_text(encoding="utf-8")
        self.assertIn("مراجعة النص المستخرج", html)
        self.assertIn("اعتماد النص المستخرج", html)
        self.assertIn("حفظ التصحيح", html)
        self.assertIn("يحتاج إعادة فحص", html)
        self.assertIn("chunk.latest_review&&chunk.latest_review.page_reference?chunk.latest_review.page_reference:''", html)
        self.assertIn("page_reference:chunk.latest_review&&chunk.latest_review.page_reference?String(chunk.latest_review.page_reference):''", html)
        self.assertIn("const extractedPage=chunk.page", html)
        self.assertIn("expected_text_sha256:chunk.text_sha256", html)
        self.assertIn("PDF أو Word حتى 15 ميجابايت", html)
        self.assertIn("لا تحفظه إلا بعد مقارنته بالملف الأصلي", html)

    def test_reviewer_page_reference_does_not_overwrite_extraction_page(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        endpoint = app[
            app.index("def review_document_chunk("):
            app.index("@app.delete(\"/cases/{cid}\")")
        ]
        self.assertIn('"UPDATE chunks SET text=?,norm=? "', endpoint)
        self.assertIn('"UPDATE chunks SET text=text "', endpoint)
        self.assertNotIn("SET page=", endpoint)
        self.assertIn("b.note.strip(), b.page_reference.strip()", endpoint)
        self.assertIn('"page_reference": b.page_reference.strip() or None', endpoint)

    def test_compact_review_queue_submits_the_current_reviewer_page_reference(self):
        html = (ROOT / "static/index.html").read_text(encoding="utf-8")
        self.assertIn("const submitChunkReview=async(item,chunk,outcome,correctedText,note,pageReference,controls)=>", html)
        self.assertIn("page_reference:String(pageReference||'').trim()", html)
        self.assertIn("value:latest&&latest.page_reference?String(latest.page_reference):''", html)
        self.assertIn("note,pageReference,correction,h('div'", html)
        self.assertIn("correction.value,note.value,pageReference.value", html)
        self.assertIn("note.value,pageReference.value,[accepted,recheck,edit]", html)
        self.assertIn("submitChunkReview(item,chunk,'accepted','',note.value,pageReference.value,[accepted,recheck,edit])", html)
        self.assertIn("submitChunkReview(item,chunk,'needs_recheck','',note.value,pageReference.value,[accepted,recheck,edit])", html)
        self.assertIn("submitChunkReview(item,chunk,'corrected',correction.value,note.value,pageReference.value,[accepted,recheck,edit,save])", html)

    def test_compact_review_queue_discloses_its_100_passage_cap(self):
        html = (ROOT / "static/index.html").read_text(encoding="utf-8")
        self.assertIn("let remaining=100,hasMore=false", html)
        self.assertIn("if(remaining<=0){hasMore=true;break}", html)
        self.assertIn("if(hasMore)cards.unshift", html)
        self.assertIn("This summary shows the first 100 passages only. Open the document review panel to access the remaining passages.", html)


if __name__ == "__main__":
    unittest.main()
