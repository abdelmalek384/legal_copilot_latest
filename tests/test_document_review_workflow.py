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
        self.assertIn("expected_text_sha256:chunk.text_sha256", html)
        self.assertIn("PDF أو Word حتى 15 ميجابايت", html)
        self.assertIn("لا تحفظه إلا بعد مقارنته بالملف الأصلي", html)


    def test_document_review_summary_discloses_its_100_passage_cap(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        start = html.index("const renderChunkReviewCards=()=>{")
        end = html.index("const renderAnalysis=()=>{", start)
        review = html[start:end]
        self.assertIn("let remaining=100,hasMore=false", review)
        self.assertIn("if(remaining<=0){hasMore=true;break}", review)
        self.assertIn("if(hasMore)cards.unshift", review)
        self.assertIn("This summary shows the first 100 passages only. Open the document review panel to access the remaining passages.", review)


if __name__ == "__main__":
    unittest.main()
