"""Tests for the optional claim-support screen using fictional passages only."""
import os
import unittest
from unittest import mock

from app import norm, tokens, _mask_markdown_code
from tools.claim_support import claim_support_enabled, has_unsupported_claims


class ClaimSupportTests(unittest.TestCase):
    def test_never_expires_is_blocked_against_a_five_year_limitation_source(self):
        hits = [{"text": "The limitation period is five years."}]
        self.assertTrue(has_unsupported_claims(
            "The claim never expires [1].", hits, tokens, norm, _mask_markdown_code
        ))

    def test_faithful_five_year_paraphrase_passes(self):
        hits = [{"text": "The limitation period is five years."}]
        self.assertFalse(has_unsupported_claims(
            "The limitation period lasts five years [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_invalid_citation_fails_closed(self):
        self.assertTrue(has_unsupported_claims(
            "The limitation period is five years [2].",
            [{"text": "The limitation period is five years."}],
            tokens, norm, _mask_markdown_code
        ))

    def test_feature_flag_is_off_by_default_and_requires_explicit_opt_in(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(claim_support_enabled())
        with mock.patch.dict(os.environ, {"LEGAL_CLAIM_SUPPORT_CHECK": "1"}):
            self.assertTrue(claim_support_enabled())


if __name__ == "__main__":
    unittest.main()
