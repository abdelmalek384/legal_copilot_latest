"""Fail-closed validation for explicit article/page pinpoints in cited answers."""
import unittest
from unittest.mock import patch
import app


class AnswerPinCitationBindingTests(unittest.TestCase):
    def test_matching_article_pin_passes(self):
        hits = [{"text": "تقرر المادة 12 القاعدة القانونية.", "article": "12"}]
        self.assertFalse(app._answer_has_mismatched_pincites("تقرر المادة 12 القاعدة القانونية [1].", hits))

    def test_mismatched_article_pin_fails(self):
        hits = [{"text": "تقرر المادة 12 القاعدة القانونية.", "article": "12"}]
        self.assertTrue(app._answer_has_mismatched_pincites("تقرر المادة 13 القاعدة القانونية [1].", hits))

    def test_matching_english_article_and_page_pins_pass(self):
        hits = [{"text": "The rule appears in article 12 on page 95.", "article": 12, "page": 95}]
        self.assertFalse(app._answer_has_mismatched_pincites("Article 12, page 95 [1].", hits))

    def test_page_within_recorded_range_passes_and_outside_range_fails(self):
        hits = [{"text": "The passage is on pages 94 to 95.", "page": "94–95"}]
        self.assertFalse(app._answer_has_mismatched_pincites("راجع ص 95 [1].", hits))
        self.assertTrue(app._answer_has_mismatched_pincites("راجع ص 96 [1].", hits))
        self.assertFalse(app._answer_has_mismatched_pincites("راجع الصفحة 95 [1].", hits))
        self.assertTrue(app._answer_has_mismatched_pincites("راجع الصفحة 96 [1].", hits))

    def test_arabic_indic_article_digits_are_normalized(self):
        hits = [{"text": "تقرر المادة 12 القاعدة القانونية.", "article": "12"}]
        self.assertFalse(app._answer_has_mismatched_pincites("تقرر المادة ١٢ [1].", hits))

    def test_complex_recorded_locator_is_left_for_manual_review(self):
        hits = [{"text": "تقرر المادة 12 مكرر القاعدة القانونية.", "article": "12 مكرر"}]
        self.assertFalse(app._answer_has_mismatched_pincites(
            "تقرر المادة 12 مكرر القاعدة القانونية [1].", hits
        ))
    def test_article_pin_without_recorded_locator_fails_closed(self):
        hits = [{"text": "تقرر القاعدة القانونية."}]
        self.assertTrue(app._answer_has_mismatched_pincites("المادة 12 تقرر القاعدة [1].", hits))

    def test_code_sample_does_not_supply_or_conflict_with_a_pin(self):
        hits = [{"text": "تقرر المادة 12 القاعدة القانونية.", "article": "12"}]
        answer = "المصدر يقرر القاعدة [1].\n```text\nالمادة 13 [1]\n```"
        self.assertFalse(app._answer_has_mismatched_pincites(answer, hits))

    def test_multi_source_sentence_is_left_for_manual_pin_assignment(self):
        hits = [
            {"text": "Article 12.", "article": "12"},
            {"text": "Article 13.", "article": "13"},
        ]
        self.assertFalse(app._answer_has_mismatched_pincites("Article 12 [1] [2].", hits))

    def test_ask_abstains_when_article_pin_conflicts_with_cited_chunk(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-PIN",
            "text": "تقرر المادة 12 القاعدة القانونية.", "article": "12", "page": "94",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="تقرر المادة 13 القاعدة القانونية [1]."
        ):
            result = app.ask(None, "ما رقم المادة؟", scope="verified_corpus")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertIn("لا يطابق محدد الموقع", result["message"])


if __name__ == "__main__":
    unittest.main()