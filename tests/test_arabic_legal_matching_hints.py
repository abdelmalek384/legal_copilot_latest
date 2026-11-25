"""Focused regressions for Arabic legal retrieval-only hint expansion.

No legal meaning is asserted: aliases are lexical retrieval hints only.
"""
import re
import unittest

from tools.arabic_legal_matching import expand_lexicon_hints, orthographic_variants


def _tokens(value):
    return re.findall(r"\w+", value)


def _norm(value):
    return value


class ArabicLegalMatchingHintTests(unittest.TestCase):
    def _expand(self, query, phrases=None, tokens=None):
        original = _tokens(query)
        return expand_lexicon_hints(
            query, original, _tokens, _norm, limit=48,
            phrase_aliases=phrases or {}, token_aliases=tokens or {},
        )

    def test_positive_phrase_alias_adds_retrieval_hints(self):
        hints = self._expand(
            "فصلني من الشغل",
            phrases={"فصلني من الشغل": ["إنهاء عقد العمل"]},
        )
        self.assertIn("إنهاء", hints)
        self.assertIn("عقد", hints)
        self.assertIn("العمل", hints)

    def test_negated_phrase_does_not_add_aliases(self):
        hints = self._expand(
            "مش فصلني من الشغل",
            phrases={"فصلني من الشغل": ["إنهاء عقد العمل"]},
        )
        self.assertNotIn("إنهاء", hints)
        self.assertNotIn("عقد", hints)

    def test_positive_occurrence_survives_negated_duplicate(self):
        hints = self._expand(
            "مش فصلني من الشغل لكن فصلني",
            phrases={"فصلني": ["إنهاء عقد العمل"]},
        )
        self.assertIn("إنهاء", hints)

    def test_original_query_terms_are_preserved_before_hint_limit(self):
        query = " ".join(f"مصطلح{i}" for i in range(80))
        hints = expand_lexicon_hints(query, _tokens(query), _tokens, _norm, limit=1,
                                     phrase_aliases={}, token_aliases={})
        self.assertEqual(hints[:80], _tokens(query))

    def test_orthographic_variants_are_narrow_and_deduplicated(self):
        self.assertEqual(orthographic_variants("مسؤول"), ("مسؤول", "مسئول"))
        self.assertEqual(orthographic_variants("مسئول"), ("مسئول", "مسؤول"))
        self.assertEqual(orthographic_variants("الإجازة"), ("الإجازة", "الإجازه"))
        self.assertEqual(orthographic_variants("قصير"), ("قصير",))


if __name__ == "__main__":
    unittest.main()
