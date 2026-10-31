"""Fail-closed checks for inline citation coverage in generated legal answers."""
import unittest
from unittest.mock import patch
import app


class CitationCoverageTests(unittest.TestCase):
    def test_cited_arabic_and_english_sentences_pass(self):
        self.assertFalse(app._answer_has_uncited_claims(
            "يحدد النص المدة بثلاثين يوماً [1]. ويطبق الاستثناء الوارد في المادة [2]."
        ))
        self.assertFalse(app._answer_has_uncited_claims(
            "The statute sets the period at thirty days [1]. The exception is in section 4 [2]."
        ))

    def test_uncited_claim_after_cited_sentence_fails(self):
        self.assertTrue(app._answer_has_uncited_claims(
            "يحدد النص المدة بثلاثين يوماً [1]. ويجوز إنهاء العقد فوراً."
        ))

    def test_uncited_bullet_fails_even_when_another_bullet_is_cited(self):
        self.assertTrue(app._answer_has_uncited_claims(
            "- يحدد النص المدة بثلاثين يوماً [1].\n- ويجوز الإنهاء في جميع الحالات."
        ))

    def test_headings_and_blank_lines_do_not_count_as_claims(self):
        self.assertFalse(app._answer_has_uncited_claims(
            "## القاعدة\n\nيحدد النص المدة بثلاثين يوماً [1].\n\n**الاستثناء:**\nينطبق الاستثناء المذكور في النص [2]."
        ))

    def test_empty_or_non_string_answer_fails_closed(self):
        self.assertTrue(app._answer_has_uncited_claims(""))
        self.assertTrue(app._answer_has_uncited_claims(None))

    def test_citation_index_parser_ignores_code_and_keeps_prose_markers(self):
        self.assertEqual(app._answer_citation_indices("Rule [2]. `[3]`"), {2})
        self.assertEqual(app._answer_citation_indices("Rule [1].\n```text\n[4]\n```"), {1})
        self.assertEqual(app._answer_citation_indices("```text\n[1]"), set())

    def test_citation_inside_hidden_html_comment_does_not_support_a_claim(self):
        self.assertTrue(app._answer_has_uncited_claims(
            "The deadline is 30 days. <!-- [1] -->"
        ))
        self.assertEqual(app._answer_citation_indices("Rule [2]. <!-- [1] -->"), {2})

    def test_citation_inside_fenced_code_does_not_support_a_claim(self):
        answer = "The deadline is 30 days.\n\n```text\n[1]\n```"
        self.assertTrue(app._answer_has_uncited_claims(answer))

    def test_uncited_code_sample_does_not_invalidate_cited_prose(self):
        answer = "The rule is stated in the source [1].\n\n```python\nprint('example')\n```"
        self.assertFalse(app._answer_has_uncited_claims(answer))

    def test_inline_code_citation_does_not_support_adjacent_claim(self):
        self.assertTrue(app._answer_has_uncited_claims(
            "The court may dismiss the claim. `[1]`"
        ))

    def test_unclosed_fenced_code_cannot_supply_citation(self):
        self.assertTrue(app._answer_has_uncited_claims(
            "The deadline is 30 days.\n```text\n[1]"
        ))

    def test_ask_abstains_when_corpus_source_permission_evidence_is_unresolved(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "LAW-UNLICENSED", "text": "A source passage.",
            "verified": True, "in_force": True, "applies_as_of": True, "case_id": None,
            "source_status": app.STATUS_REVIEW, "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="The rule is stated in the source [1]."
        ) as llm:
            result = app.ask(None, "What is the rule?", scope="verified_corpus")
        self.assertTrue(result["found"])
        self.assertTrue(result["abstained"])
        self.assertIsNone(result["answer"])
        self.assertIn("المصادر فقط", result["message"])
        llm.assert_not_called()

    def test_ask_rejects_answer_citing_only_a_code_block(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "LAW-1", "text": "A source passage.",
            "verified": True, "in_force": True, "applies_as_of": True, "case_id": None,
            "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="The deadline is 30 days.\n```text\n[1]\n```"
        ):
            result = app.ask(None, "What is the deadline?", scope="verified_corpus")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertIn("استشهادات", result["message"])

    def test_ask_accepts_prose_citation_but_ignores_invalid_code_citation(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "LAW-1", "text": "A source passage.",
            "verified": True, "in_force": True, "applies_as_of": True, "case_id": None,
            "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="The rule is stated in the source [1].\n```text\n[99]\n```"
        ):
            result = app.ask(None, "What is the rule?", scope="verified_corpus")
        self.assertEqual(result["answer"], "The rule is stated in the source [1].\n```text\n[99]\n```")
        self.assertFalse(result["abstained"])

    def test_numeric_claim_inside_code_is_not_treated_as_a_legal_claim(self):
        hits = [{"text": "This source does not mention any deadline."}]
        answer = "The applicable rule is in source [1].\n```text\nDeadline: 30 days [1].\n```"
        self.assertFalse(app._answer_has_unsupported_quantities(answer, hits, {1}))


if __name__ == "__main__":
    unittest.main()
