"""Numeric legal claims must be supported by the sources cited on that sentence."""
import unittest
import app


class CitationQuantityBindingTests(unittest.TestCase):
    def setUp(self):
        self.hits = [
            {"text": "The statutory deadline is 30 days."},
            {"text": "This passage discusses procedure but states no duration or fee."},
            {"text": "The filing fee is 500 pounds."},
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

    def test_non_numeric_claim_does_not_need_quantity_support(self):
        answer = "The source discusses the legal procedure [2]."
        self.assertFalse(app._answer_has_unsupported_quantities(answer, self.hits, {2}))


if __name__ == "__main__":
    unittest.main()
