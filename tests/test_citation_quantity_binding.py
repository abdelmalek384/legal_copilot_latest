"""Numeric legal claims must be supported by the sources cited on that sentence."""
import unittest
import app


class CitationQuantityBindingTests(unittest.TestCase):
    def setUp(self):
        self.hits = [
            {"text": "The statutory deadline is 30 days."},
            {"text": "This passage discusses procedure but states no duration or fee."},
            {"text": "The filing fee is 500 pounds."},
            {"text": "The applicable tax rate is 14%."},
        ]

    def test_quantity_is_supported_by_its_own_inline_citation(self):
        answer = "The deadline is 30 days [1]. The fee is 500 pounds [3]."
        self.assertFalse(app._answer_has_unsupported_quantities(answer, self.hits, {1, 3}))

    def test_unrelated_citation_elsewhere_cannot_support_numeric_claim(self):
        # Source 1 contains the duration, but the sentence cites only source 2.
        answer = "The deadline is 30 days [2]. Another point is supported by source [1]."
        self.assertTrue(app._answer_has_unsupported_quantities(answer, self.hits, {1, 2}))

    def test_multiple_citations_on_same_sentence_can_support_claim(self):
        answer = "The deadline is 30 days [2][1]."
        self.assertFalse(app._answer_has_unsupported_quantities(answer, self.hits, {1, 2}))

    def test_quantity_without_inline_citation_fails_closed(self):
        answer = "The deadline is 30 days. A separate source is cited [1]."
        self.assertTrue(app._answer_has_unsupported_quantities(answer, self.hits, {1}))

    def test_out_of_range_citation_cannot_support_quantity(self):
        answer = "The deadline is 30 days [99]."
        self.assertTrue(app._answer_has_unsupported_quantities(answer, self.hits, {99}))

    def test_arabic_and_english_number_words_cover_common_legal_quantities(self):
        self.assertEqual(app._legal_quantities("thirty days"), {(30, "day")})
        self.assertEqual(app._legal_quantities("three hundred days"), {(300, "day")})
        self.assertEqual(app._legal_quantities("ثلاثين يوما"), {(30, "day")})
        self.assertEqual(app._legal_quantities("خمسة عشر يوما"), {(15, "day")})
        self.assertEqual(app._legal_quantities("مائة جنيه"), {(100, "currency")})

    def test_arabic_worded_quantity_is_bound_to_its_inline_source(self):
        hits = self.hits + [{"text": "The statutory deadline is ثلاثين يوما."}]
        self.assertFalse(app._answer_has_unsupported_quantities(
            "The deadline is 30 days [5].", hits, {5}
        ))
        self.assertTrue(app._answer_has_unsupported_quantities(
            "The deadline is 30 days [2]. Another source says ثلاثين يوما [5].",
            hits, {2, 5}
        ))

    def test_adjacent_and_arabic_percent_symbols_are_checked(self):
        self.assertFalse(app._answer_has_unsupported_quantities(
            "The tax rate is 14% [4].", self.hits, {4}
        ))
        self.assertFalse(app._answer_has_unsupported_quantities(
            "The tax rate is ١٤٪ [4].", self.hits, {4}
        ))
        self.assertTrue(app._answer_has_unsupported_quantities(
            "The tax rate is 14% [2]. Another point cites the rate [4].",
            self.hits, {2, 4}
        ))
        self.assertTrue(app._answer_has_unsupported_quantities(
            "The tax rate is 14٪ [2].", self.hits, {2}
        ))

    def test_ask_accepts_supported_arabic_compound_quantity(self):
        from unittest.mock import patch
        hit = {
            "cos": 1.0, "score": 1, "ref": "LAW-25", "text": "The statutory deadline is 25 days.",
            "verified": True, "in_force": True, "applies_as_of": True, "case_id": None,
            "source_status": "verified_operative_text", "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="المدة خمسة وعشرون يوما [1]."
        ):
            result = app.ask(None, "ما المدة القانونية؟", scope="verified_corpus")
        self.assertEqual(result["answer"], "المدة خمسة وعشرون يوما [1].")
        self.assertFalse(result["abstained"])

    def test_ask_abstains_on_unsupported_arabic_compound_quantity(self):
        from unittest.mock import patch
        hit = {
            "cos": 1.0, "score": 1, "ref": "LAW-30", "text": "The statutory deadline is 30 days.",
            "verified": True, "in_force": True, "applies_as_of": True, "case_id": None,
            "source_status": "verified_operative_text", "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="المدة خمسة وعشرون يوما [1]."
        ):
            result = app.ask(None, "ما المدة القانونية؟", scope="verified_corpus")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertIn("الأرقام", result["message"])

    def test_non_numeric_claim_does_not_need_quantity_support(self):
        answer = "The source discusses the legal procedure [2]."
        self.assertFalse(app._answer_has_unsupported_quantities(answer, self.hits, {2}))


    def test_arabic_conjunction_compound_numbers_are_normalized(self):
        self.assertEqual(app._legal_quantities("خمسة وعشرون يوما"), {(25, "day")})
        self.assertEqual(app._legal_quantities("خمسة وعشرين يوما"), {(25, "day")})
        self.assertEqual(app._legal_quantities("مائة وخمسون جنيها"), {(150, "currency")})
        self.assertEqual(app._legal_quantities("مائة وخمسين جنيها"), {(150, "currency")})
        self.assertEqual(app._legal_quantities("ثلاثمائة وخمسة وعشرون يوما"), {(325, "day")})
        self.assertEqual(app._legal_quantities("ثلاثمائة وخمسة وعشرين يوما"), {(325, "day")})
        self.assertEqual(app._legal_quantities("ألف ومائتان وخمسون جنيها"), {(1250, "currency")})
        self.assertEqual(app._legal_quantities("ألف ومائتين وخمسين جنيها"), {(1250, "currency")})
        self.assertEqual(app._legal_quantities("خمسة و عشرون يوما"), {(25, "day")})

    def test_arabic_compound_quantity_is_bound_to_its_inline_source(self):
        hits = [
            {"text": "The statutory deadline is 25 days."},
            {"text": "This passage states no deadline."},
        ]
        self.assertFalse(app._answer_has_unsupported_quantities(
            "المدة خمسة وعشرون يوما [1].", hits, {1}
        ))
        self.assertTrue(app._answer_has_unsupported_quantities(
            "المدة خمسة وعشرون يوما [2].", hits, {2}
        ))

if __name__ == "__main__":
    unittest.main()
