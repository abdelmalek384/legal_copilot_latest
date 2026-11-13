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

    def test_every_registered_predicate_pair_detects_opposite_polarity(self):
        for positive, _negative_pattern in app._ARABIC_POLARITY_PREDICATES:
            with self.subTest(predicate=positive):
                negative_source = {"text": "ولا " + positive + " ذلك."}
                positive_answer = "و" + positive + " ذلك [1]."
                self.assertTrue(app._answer_has_source_polarity_conflict(
                    positive_answer, [negative_source]
                ))
                positive_source = {"text": "و" + positive + " ذلك."}
                negative_answer = "ولا " + positive + " ذلك [1]."
                self.assertTrue(app._answer_has_source_polarity_conflict(
                    negative_answer, [positive_source]
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



    def test_ask_abstains_when_english_must_not_is_rewritten_as_must(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-ENGLISH-OBLIGATION",
            "text": "The employer must not deduct wages.",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.dict("os.environ", {"LEGAL_CLAIM_SUPPORT_CHECK": ""}):
            with patch.object(app, "search", return_value=[hit]), patch.object(
                app, "LLM", return_value="The employer must deduct wages [1]."
            ):
                result = app.ask(None, "Must the employer deduct wages?", scope="verified_corpus")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertIn("التزاماً أو حظراً صريحاً", result["message"])

    def test_ask_preserves_faithful_english_must_not_answer(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-ENGLISH-OBLIGATION",
            "text": "The employer must not deduct wages.",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.dict("os.environ", {"LEGAL_CLAIM_SUPPORT_CHECK": ""}):
            with patch.object(app, "search", return_value=[hit]), patch.object(
                app, "LLM", return_value="The employer must not deduct wages [1]."
            ):
                result = app.ask(None, "Must the employer deduct wages?", scope="verified_corpus")
        self.assertEqual(result["answer"], "The employer must not deduct wages [1].")
        self.assertFalse(result["abstained"])


    def test_ask_abstains_on_arabic_negated_obligation_reversal(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-ARABIC-OBLIGATION",
            "text": "لا يلتزم صاحب العمل بتقديم الإخطار.",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.dict("os.environ", {"LEGAL_CLAIM_SUPPORT_CHECK": ""}):
            with patch.object(app, "search", return_value=[hit]), patch.object(
                app, "LLM", return_value="يلتزم صاحب العمل بتقديم الإخطار [1]."
            ), patch.object(app, "_answer_has_source_polarity_conflict", return_value=False):
                result = app.ask(None, "هل يلتزم صاحب العمل بتقديم الإخطار؟", scope="verified_corpus")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertIn("التزاماً أو حظراً صريحاً", result["message"])

    def test_ask_preserves_faithful_arabic_negated_obligation(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-ARABIC-OBLIGATION",
            "text": "لا يلتزم صاحب العمل بتقديم الإخطار.",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.dict("os.environ", {"LEGAL_CLAIM_SUPPORT_CHECK": ""}):
            with patch.object(app, "search", return_value=[hit]), patch.object(
                app, "LLM", return_value="لا يلتزم صاحب العمل بتقديم الإخطار [1]."
            ), patch.object(app, "_answer_has_source_polarity_conflict", return_value=False):
                result = app.ask(None, "ما الالتزام بشأن الإخطار؟", scope="verified_corpus")
        self.assertEqual(result["answer"], "لا يلتزم صاحب العمل بتقديم الإخطار [1].")
        self.assertFalse(result["abstained"])

    def test_ask_does_not_mix_unrelated_arabic_obligation_clauses(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-UNRELATED-OBLIGATIONS",
            "text": "لا يلتزم صاحب العمل بتقديم الإخطار. ويجب على العامل تقديم الطلب.",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.dict("os.environ", {"LEGAL_CLAIM_SUPPORT_CHECK": ""}):
            with patch.object(app, "search", return_value=[hit]), patch.object(
                app, "LLM", return_value="يجب على العامل تقديم الطلب [1]."
            ), patch.object(app, "_answer_has_source_polarity_conflict", return_value=False):
                result = app.ask(None, "ما الذي يجب على العامل فعله؟", scope="verified_corpus")
        self.assertEqual(result["answer"], "يجب على العامل تقديم الطلب [1].")
        self.assertFalse(result["abstained"])


    def test_ask_abstains_on_the_three_original_negated_obligation_regressions(self):
        cases = (
            (
                "The employer is not required to provide notice.",
                "The employer must provide notice [1].",
                "Must the employer provide notice?",
            ),
            (
                "لا يجب على صاحب العمل تقديم الإخطار.",
                "يجب على صاحب العمل تقديم الإخطار [1].",
                "هل يجب على صاحب العمل تقديم الإخطار؟",
            ),
            (
                "لا يلتزم صاحب العمل بتقديم الإخطار.",
                "يلتزم صاحب العمل بتقديم الإخطار [1].",
                "هل يلتزم صاحب العمل بتقديم الإخطار؟",
            ),
        )
        for evidence, generated_answer, question in cases:
            with self.subTest(evidence=evidence):
                hit = {
                    "cos": 1.0, "score": 1, "ref": "SYNTHETIC-NEGATION-REGRESSION",
                    "text": evidence, "verified": True, "in_force": True,
                    "applies_as_of": True, "case_id": None,
                    "source_status": app.STATUS_VERIFIED, "provenance": {},
                }
                with patch.dict("os.environ", {"LEGAL_CLAIM_SUPPORT_CHECK": ""}):
                    with patch.object(app, "search", return_value=[hit]), patch.object(
                        app, "LLM", return_value=generated_answer
                    ), patch.object(app, "_answer_has_source_polarity_conflict", return_value=False):
                        result = app.ask(None, question, scope="verified_corpus")
                self.assertIsNone(result["answer"])
                self.assertTrue(result["abstained"])
                self.assertIn("التزاماً أو حظراً صريحاً", result["message"])


if __name__ == "__main__":
    unittest.main()
