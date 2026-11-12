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
        self.assertIn('@app.post("/cases/{cid}/docs/{document_id}/classification"', app)
        self.assertIn('@app.get("/cases/{cid}/docs/{document_id}/classification-history")', app)
        self.assertIn('expected_version', app)
        self.assertIn('document_classification_events', app)
        self.assertIn('document_classification_events.csv', app)

    def test_ui_can_accept_correct_and_flag_extraction(self):
        html = (ROOT / "static/index.html").read_text(encoding="utf-8")
        self.assertIn("مراجعة النص المستخرج", html)
        self.assertIn("اعتماد النص المستخرج", html)
        self.assertIn("حفظ التصحيح", html)
        self.assertIn("يحتاج إعادة فحص", html)
        self.assertIn("expected_text_sha256:chunk.text_sha256", html)
        self.assertIn("PDF أو Word حتى 15 ميجابايت", html)
        self.assertIn("لا تحفظه إلا بعد مقارنته بالملف الأصلي", html)
        self.assertIn("Save classification and review history", html)
        self.assertIn("classification-history", html)
        self.assertIn("Reviewer-selected classification", html)


if __name__ == "__main__":
    unittest.main()
