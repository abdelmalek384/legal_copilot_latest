"""Contract tests for the Arabic-first product feedback workflow UI."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")


class ProductFeedbackFrontendContractTests(unittest.TestCase):
    def test_feedback_navigation_and_submission_are_exposed(self):
        self.assertIn("Product feedback", HTML)
        self.assertIn("ملاحظات المنتج", HTML)
        self.assertIn("function feedbackPage()", HTML)
        self.assertIn("api('/feedback','POST'", HTML)
        self.assertIn("api('/feedback/mine')", HTML)
        self.assertIn("api('/admin/feedback')", HTML)
        self.assertIn("api('/admin/feedback/'+item.id+'/review'", HTML)

    def test_ui_explains_firm_privacy_and_no_training_default(self):
        self.assertIn("private to your firm", HTML)
        self.assertIn("not used for model training", HTML)
        self.assertIn("لا تُستخدم لتدريب النماذج", HTML)
        self.assertIn("Do not include client names", HTML)


if __name__ == "__main__":
    unittest.main()
