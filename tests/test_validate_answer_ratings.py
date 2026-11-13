import csv
import tempfile
import unittest
from pathlib import Path

from tools.validate_answer_ratings import EXPECTED_HEADER, validate_file, validate_rows


def row(**overrides):
    value = {
        "answer_id": "ans-1",
        "answer_rating": "correct",
        "cited_article_rating": "right",
        "notes": "",
        "rater": "reviewer-1",
        "timestamp": "2026-11-14T10:30:00Z",
        "trust_tier": "source_matched",
    }
    value.update(overrides)
    return value


class AnswerRatingValidationTests(unittest.TestCase):
    def test_accepts_valid_contract_row(self):
        result = validate_rows([row()])
        self.assertEqual(result["valid_rows"], 1)
        self.assertEqual(result["invalid_rows"], 0)

    def test_rejects_unknown_rating_or_trust_tier(self):
        result = validate_rows([row(answer_rating="excellent", trust_tier="verified_by_ai")])
        self.assertEqual(result["invalid_rows"], 1)
        self.assertEqual(len(result["errors"][0]["errors"]), 2)

    def test_rejects_non_string_notes_and_non_object_rows(self):
        result = validate_rows([row(notes=None), None])
        self.assertEqual(result["invalid_rows"], 2)
        self.assertIn("notes must be a string (empty is allowed)", result["errors"][0]["errors"])
        self.assertIn("row must be an object", result["errors"][1]["errors"])

    def test_rejects_timestamp_without_timezone(self):
        result = validate_rows([row(timestamp="2026-11-14T10:30:00")])
        self.assertIn("timestamp must include an explicit timezone", result["errors"][0]["errors"])

    def test_accepts_utf8_bom_and_exact_header(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ratings.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=EXPECTED_HEADER)
                writer.writeheader()
                writer.writerow(row(notes="إجابة صحيحة، مع تحفظ"))
            result = validate_file(path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["valid_rows"], 1)

    def test_rejects_wrong_header_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ratings.csv"
            path.write_text("answer_rating,answer_id\\ncorrect,ans-1\\n", encoding="utf-8")
            result = validate_file(path)
        self.assertFalse(result["valid"])
        self.assertIn("exact answer rating contract", result["error"])


if __name__ == "__main__":
    unittest.main()
