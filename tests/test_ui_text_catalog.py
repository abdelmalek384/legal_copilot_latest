"""Tests for the read-only Arabic/English UI text catalog extractor."""
import unittest
from pathlib import Path

from tools.extract_ui_text_catalog import (
    DEFAULT_OUTPUT,
    DEFAULT_SOURCE,
    decode_js_string,
    extract_pairs,
    render_catalog,
)


class UiTextCatalogTests(unittest.TestCase):
    def test_checked_in_catalog_matches_literal_ui_text_pairs(self):
        pairs, literal_calls, dynamic_calls = extract_pairs(
            DEFAULT_SOURCE.read_text(encoding="utf-8")
        )
        self.assertGreater(len(pairs), 350)
        self.assertGreater(literal_calls, len(pairs))
        self.assertGreater(dynamic_calls, 0)
        self.assertEqual(DEFAULT_OUTPUT.read_text(encoding="utf-8"), render_catalog(pairs))

    def test_pairs_are_nonempty_and_deduplicated_with_occurrence_counts(self):
        pairs, _, _ = extract_pairs(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(len({(ar, en) for ar, en, _ in pairs}), len(pairs))
        self.assertTrue(all(ar.strip() and en.strip() and count >= 1 for ar, en, count in pairs))

    def test_javascript_escaped_quotes_and_unicode_are_decoded(self):
        self.assertEqual(decode_js_string("'O\\'Brien'"), "O'Brien")
        self.assertEqual(decode_js_string("'\\u0645\\u0631\\u062d\\u0628\\u0627'"), "مرحبا")
        self.assertEqual(decode_js_string('"line\\nnext"'), "line\nnext")


if __name__ == "__main__":
    unittest.main()
