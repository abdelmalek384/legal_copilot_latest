"""Fail-closed checks for inline citation coverage in generated legal answers."""
import unittest
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


if __name__ == "__main__":
    unittest.main()
