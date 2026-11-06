import unittest

from fastapi import HTTPException

import app


class ReviewEvidenceUrlValidationTests(unittest.TestCase):
    def test_accepts_well_formed_https_evidence_url(self):
        self.assertEqual(
            app.validate_review_evidence_url("https://example.gov/legal/permission"),
            "https://example.gov/legal/permission",
        )

    def test_rejects_non_https_and_embedded_credentials(self):
        for value in (
            "http://example.gov/evidence",
            "https://reviewer:secret@example.gov/evidence",
            "https://@example.gov/evidence",
        ):
            with self.subTest(value=value), self.assertRaises(HTTPException):
                app.validate_review_evidence_url(value)

    def test_rejects_whitespace_and_control_characters(self):
        for value in (
            " https://example.gov/evidence",
            "https://example.gov/evidence ",
            "https://example.gov/path with spaces",
            "https://example.gov/path\nnext",
        ):
            with self.subTest(value=value), self.assertRaises(HTTPException):
                app.validate_review_evidence_url(value)

    def test_rejects_invalid_or_empty_ports(self):
        for value in (
            "https://example.gov:not-a-port/evidence",
            "https://example.gov:99999/evidence",
            "https://example.gov:0/evidence",
            "https://example.gov:/evidence",
        ):
            with self.subTest(value=value), self.assertRaises(HTTPException):
                app.validate_review_evidence_url(value)

    def test_none_or_empty_is_optional_for_non_passing_events(self):
        self.assertIsNone(app.validate_review_evidence_url(None))
        self.assertIsNone(app.validate_review_evidence_url(""))


if __name__ == "__main__":
    unittest.main()
