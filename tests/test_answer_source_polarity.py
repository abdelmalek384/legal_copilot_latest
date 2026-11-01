"""Conservative fail-closed checks for explicit Arabic source/answer polarity reversals."""
import unittest
from unittest.mock import patch

import app


class AnswerSourcePolarityTests(unittest.TestCase):
    def test_positive_answer_conflicts_with_explicit_negative_source(self):
        hits = [{"text": "لا يجوز لصاحب العمل إنهاء العقد دون إخطار."}]
        self.assertTrue(app._answer_has_source_polarity_conflict(
            "يجوز لصاحب العمل إنهاء العقد دون إخطار [1].", hits
        ))

    def test_negative_answer_conflicts_with_explicit_positive_source(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد في الحالة المحددة."}]
        self.assertTrue(app._answer_has_source_polarity_conflict(
            "لا يجوز لصاحب العمل إنهاء العقد في الحالة المحددة [1].", hits
        ))

    def test_attached_arabic_conjunction_does_not_hide_negative_polarity(self):
        hits = [{"text": "ولا يجوز لصاحب العمل إنهاء العقد دون إخطار."}]
        self.assertTrue(app._answer_has_source_polarity_conflict(
            "ويجوز لصاحب العمل إنهاء العقد دون إخطار [1].", hits
        ))

    def test_matching_negative_polarity_passes(self):
        hits = [{"text": "لا يجوز لصاحب العمل إنهاء العقد دون إخطار."}]
        self.assertFalse(app._answer_has_source_polarity_conflict(
            "لا يجوز لصاحب العمل إنهاء العقد دون إخطار [1].", hits
        ))

    def test_matching_positive_polarity_passes(self):
        hits = [{"text": "يحق للعامل طلب التعويض."}]
        self.assertFalse(app._answer_has_source_polarity_conflict(
            "يحق للعامل طلب التعويض [1].", hits
        ))

    def test_unrelated_predicates_do_not_create_a_conflict(self):
        hits = [{"text": "لا يجوز إنهاء العقد دون إخطار."}]
        self.assertFalse(app._answer_has_source_polarity_conflict(
            "يحق للعامل طلب التعويض [1].", hits
        ))

    def test_ambiguous_source_with_both_polarities_is_not_classified(self):
        hits = [{"text": "يجوز ذلك في الحالة الأولى ولا يجوز في الحالة الثانية."}]
        self.assertFalse(app._answer_has_source_polarity_conflict(
            "يجوز ذلك [1].", hits
        ))

    def test_code_sample_cannot_trigger_a_polarity_conflict(self):
        hits = [{"text": "لا يجوز إنهاء العقد دون إخطار."}]
        self.assertFalse(app._answer_has_source_polarity_conflict(
            "The rule is discussed in the source [1].\n~~~text\nيجوز إنهاء العقد دون إخطار [1].\n~~~",
            hits,
        ))

    def test_ask_abstains_on_explicit_source_polarity_reversal(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-POLARITY",
            "text": "لا يجوز لصاحب العمل إنهاء العقد دون إخطار.",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="يجوز لصاحب العمل إنهاء العقد دون إخطار [1]."
        ):
            result = app.ask(None, "هل يجوز إنهاء العقد دون إخطار؟", scope="verified_corpus")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertIn("تعكس صياغة صريحة", result["message"])


if __name__ == "__main__":
    unittest.main()
