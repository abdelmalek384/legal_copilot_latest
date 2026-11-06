"""Conservative regressions for overgeneralizing conditional cited legal sources."""
import unittest
from unittest.mock import patch
import app


class ConditionalScopeBindingTests(unittest.TestCase):
    def test_arabic_universal_answer_conflicts_with_conditional_source(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد إذا ارتكب العامل مخالفة جسيمة."}]
        self.assertTrue(app._answer_has_unqualified_claim_against_conditional_source(
            "يجوز لصاحب العمل إنهاء العقد في جميع الحالات [1].", hits
        ))

    def test_english_universal_answer_conflicts_with_only_if_source(self):
        hits = [{"text": "The employer may terminate the contract only if the employee commits serious misconduct."}]
        self.assertTrue(app._answer_has_unqualified_claim_against_conditional_source(
            "The employer may always terminate the contract [1].", hits
        ))

    def test_bishart_an_condition_is_recognized(self):
        hits = [{"text": "يحق للدائن طلب التنفيذ بشرط أن يحل الأجل."}]
        self.assertTrue(app._answer_has_unqualified_claim_against_conditional_source(
            "يحق للدائن طلب التنفيذ في جميع الحالات [1].", hits
        ))

    def test_ma_lam_exception_is_recognized_as_a_condition(self):
        hits = [{"text": "يجوز للمؤجر إنهاء العقد ما لم يسدد المستأجر الأجرة."}]
        self.assertTrue(app._answer_has_unqualified_claim_against_conditional_source(
            "يجوز للمؤجر إنهاء العقد في جميع الحالات [1].", hits
        ))
    def test_answer_that_preserves_the_condition_passes(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد إذا ارتكب العامل مخالفة جسيمة."}]
        self.assertFalse(app._answer_has_unqualified_claim_against_conditional_source(
            "يجوز لصاحب العمل إنهاء العقد إذا ارتكب العامل مخالفة جسيمة [1].", hits
        ))

    def test_unconditional_source_does_not_trigger(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد."}]
        self.assertFalse(app._answer_has_unqualified_claim_against_conditional_source(
            "يجوز لصاحب العمل إنهاء العقد في جميع الحالات [1].", hits
        ))

    def test_source_with_its_own_universal_qualification_is_not_rejected(self):
        hits = [{"text": "إذا تحقق الشرط جاز الإنهاء، وفي جميع الحالات الأخرى لا يجوز."}]
        self.assertFalse(app._answer_has_unqualified_claim_against_conditional_source(
            "يجوز الإنهاء في جميع الحالات [1].", hits
        ))

    def test_unrelated_conditional_clause_does_not_trigger_without_action_overlap(self):
        hits = [{"text": "إذا قدم المدعي مستنداته، تنظر المحكمة الدعوى. ويجوز لصاحب العمل إنهاء العقد."}]
        self.assertFalse(app._answer_has_unqualified_claim_against_conditional_source(
            "يجوز لصاحب العمل إنهاء العقد في جميع الحالات [1].", hits
        ))

    def test_code_sample_cannot_trigger_scope_conflict(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد إذا ارتكب العامل مخالفة جسيمة."}]
        self.assertFalse(app._answer_has_unqualified_claim_against_conditional_source(
            "المصدر يبين القاعدة [1].\n```text\nيجوز لصاحب العمل إنهاء العقد في جميع الحالات [1].\n```", hits
        ))

    def test_invalid_citation_index_fails_closed(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد إذا ارتكب العامل مخالفة جسيمة."}]
        self.assertTrue(app._answer_has_unqualified_claim_against_conditional_source(
            "يجوز لصاحب العمل إنهاء العقد في جميع الحالات [2].", hits
        ))

    def test_ask_abstains_on_universal_claim_against_conditional_source(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-CONDITION",
            "text": "يجوز لصاحب العمل إنهاء العقد إذا ارتكب العامل مخالفة جسيمة.",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="يجوز لصاحب العمل إنهاء العقد في جميع الحالات [1]."
        ):
            result = app.ask(None, "متى يجوز إنهاء العقد؟", scope="verified_corpus")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertIn("تعمم إحدى العبارات", result["message"])


if __name__ == "__main__":
    unittest.main()