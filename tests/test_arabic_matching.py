"""Regression tests for Arabic query expansion and preliminary conflict-name matching."""
import unittest

from app import conflict_name_matches, expanded_tokens, tokens


class ArabicMatchingTests(unittest.TestCase):
    def test_article_prefix_and_accusative_alif_variant_are_query_expanded(self):
        query = expanded_tokens("الشيك")
        self.assertIn("شيك", query)
        self.assertIn("شيكا", query)

    def test_delay_derivation_variants_are_query_expanded(self):
        query = expanded_tokens("التأخير")
        self.assertIn("تأخير", query)
        self.assertIn("تأخر", query)

    def test_arabic_case_search_keeps_the_surface_text_unchanged(self):
        self.assertEqual(tokens("الشيك"), ["شيك"])
        # Expansion is for retrieval only; it does not rewrite document evidence.
        self.assertIn("شيكا", expanded_tokens("الشيك"))

    def test_conflict_name_match_ignores_repeated_whitespace_and_word_order(self):
        self.assertTrue(conflict_name_matches("عمر فتحي", "فتحي  عمر"))

    def test_conflict_name_match_ignores_common_company_descriptor(self):
        self.assertTrue(conflict_name_matches("شركة النيل", "النيل"))
        self.assertTrue(conflict_name_matches("النيل", "شركة النيل للتوريدات"))

    def test_generic_descriptor_alone_does_not_match_every_company(self):
        self.assertFalse(conflict_name_matches("شركة", "شركة النيل"))
        self.assertFalse(conflict_name_matches("شركة", "شركة أخرى"))

    def test_empty_names_never_match(self):
        self.assertFalse(conflict_name_matches("", "عمر فتحي"))
        self.assertFalse(conflict_name_matches("عمر فتحي", ""))


if __name__ == "__main__":
    unittest.main()
