import unittest

from tools.legal_article_reference import extract_statute_reference, normalize_reference_digits, statute_title_matches


class LegalArticleReferenceTests(unittest.TestCase):
    def test_normalizes_arabic_and_persian_article_digits(self):
        self.assertEqual(normalize_reference_digits("المادة ٥"), "المادة 5")
        self.assertEqual(normalize_reference_digits("ماده ۵"), "ماده 5")

    def test_extracts_english_law_number_and_year(self):
        self.assertEqual(
            extract_statute_reference("Article 5 of Law No. 14 of 2025"),
            ("14", "2025"),
        )

    def test_extracts_arabic_law_number_and_year(self):
        self.assertEqual(
            extract_statute_reference("المادة ٥ من القانون رقم ١٤ لسنة ٢٠٢٥"),
            ("14", "2025"),
        )

    def test_extracts_arabic_descriptive_law_title_number_and_year(self):
        self.assertEqual(
            extract_statute_reference("المادة ٥ من قانون العمل رقم ١٤ لسنة ٢٠٢٥"),
            ("14", "2025"),
        )

    def test_rejects_article_number_without_explicit_statute(self):
        self.assertIsNone(extract_statute_reference("Article 5"))

    def test_rejects_incomplete_statute_reference(self):
        self.assertIsNone(extract_statute_reference("Article 5 of Law No. 14"))

    def test_title_must_contain_matching_law_number_and_year(self):
        reference = ("14", "2025")
        self.assertTrue(statute_title_matches("قانون رقم 14 لسنة 2025", reference))
        self.assertTrue(statute_title_matches("قانون العمل رقم 14 لسنة 2025", reference))
        self.assertTrue(statute_title_matches("Labour Law No. 14 of 2025", reference))
        self.assertFalse(statute_title_matches("قانون رقم 114 لسنة 2025", reference))
        self.assertFalse(statute_title_matches("قانون رقم 2025 لسنة 14", reference))
        self.assertFalse(statute_title_matches(
            "قانون رقم 20 لسنة 2025؛ تعديل رقم 14 لسنة 2024", reference
        ))
        self.assertFalse(statute_title_matches("قانون رقم 14 لسنة 2024", reference))
        self.assertFalse(statute_title_matches("قرار رقم 14 لسنة 2025", reference))
        self.assertFalse(statute_title_matches(None, reference))


if __name__ == "__main__":
    unittest.main()
