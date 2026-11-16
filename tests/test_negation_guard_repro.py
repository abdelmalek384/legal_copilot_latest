"""Small, focused reproducer for the three original English/Arabic negation failures.

Run with:
    PYTHONPATH=. python -m unittest tests.test_negation_guard_repro -v

All passages are synthetic and contain no Egyptian legal text.
"""
import unittest

import app
from tools.claim_support import has_negated_obligation_conflicts


class NegationGuardReproTests(unittest.TestCase):
    def assert_reversal_is_blocked(self, evidence, answer):
        self.assertTrue(
            has_negated_obligation_conflicts(
                answer + " [1].",
                [{"text": evidence}],
                app.tokens,
                app.norm,
                app._mask_markdown_code,
            )
        )

    def test_english_not_required_cannot_be_rewritten_as_must(self):
        self.assert_reversal_is_blocked(
            "The employer is not required to provide notice.",
            "The employer must provide notice",
        )

    def test_arabic_la_yajib_cannot_be_rewritten_as_yajib(self):
        self.assert_reversal_is_blocked(
            "لا يجب على صاحب العمل تقديم الإخطار.",
            "يجب على صاحب العمل تقديم الإخطار",
        )

    def test_arabic_la_yaltazim_cannot_be_rewritten_as_yaltazim(self):
        self.assert_reversal_is_blocked(
            "لا يلتزم صاحب العمل بتقديم الإخطار.",
            "يلتزم صاحب العمل بتقديم الإخطار",
        )


    def test_egyptian_circumfix_negated_obligation_cannot_be_rewritten_as_positive(self):
        cases = (
            ("ما يلزمش صاحب العمل تقديم الإخطار.", "يلزم صاحب العمل تقديم الإخطار"),
            ("ما يجبش على صاحب العمل تقديم الإخطار.", "يجب على صاحب العمل تقديم الإخطار"),
        )
        for evidence, answer in cases:
            with self.subTest(evidence=evidence):
                self.assert_reversal_is_blocked(evidence, answer)


if __name__ == "__main__":
    unittest.main()
