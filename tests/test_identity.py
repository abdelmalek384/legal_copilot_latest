"""Tests for global login email normalization."""
import unittest

from identity import normalize_email


class NormalizeEmailTests(unittest.TestCase):
    def test_trims_and_casefolds_email(self):
        self.assertEqual(normalize_email("  Lawyer@Example.COM  "), "lawyer@example.com")

    def test_applies_unicode_nfc_normalization(self):
        self.assertEqual(normalize_email("e\u0301@example.com"), normalize_email("\u00e9@example.com"))

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            normalize_email(None)


if __name__ == "__main__":
    unittest.main()
