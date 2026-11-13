import csv
import tempfile
import unittest
from pathlib import Path

from tools.adapt_answer_rating_export import adapt_file, adapt_rows
from tools.validate_answer_ratings import EXPECTED_HEADER


def firm_row(**overrides):
    row = {
        "answer_id": "ans-0001",
        "rating": "partially_correct",
        "cited_article_accuracy": "right",
        "notes": "يحتاج إلى ذكر الاستثناء",
        "rated_by": "firm-user-17",
        "updated_at": "2026-11-14T12:30:00+02:00",
        "trust_tier": "source_matched",
        "expected_article_ids": "[]",
        "answerable": "true",
        "benchmark_ready": "true",
    }
    row.update(overrides)
    return row


class AnswerRatingExportAdapterTests(unittest.TestCase):
    def test_maps_enums_and_preserves_message_time_trust_tier(self):
        rows, skipped = adapt_rows([firm_row()])
        self.assertEqual(skipped, [])
        self.assertEqual(rows[0]["answer_rating"], "partial")
        self.assertEqual(rows[0]["cited_article_rating"], "right")
        self.assertEqual(rows[0]["trust_tier"], "source_matched")
        self.assertEqual(rows[0]["rater"], "firm-user-17")
        self.assertEqual(rows[0]["timestamp"], "2026-11-14T12:30:00+02:00")

    def test_not_applicable_is_reported_and_never_coerced(self):
        rows, skipped = adapt_rows([
            firm_row(),
            firm_row(answer_id="ans-0002", cited_article_accuracy="not_applicable"),
        ])
        self.assertEqual(len(rows), 1)
        self.assertEqual(skipped, ["ans-0002"])

    def test_unknown_or_unreviewed_tier_fails_safe_to_unverified(self):
        rows, _ = adapt_rows([firm_row(trust_tier="unreviewed")])
        self.assertEqual(rows[0]["trust_tier"], "unverified")
        rows, _ = adapt_rows([firm_row(trust_tier="unexpected")])
        self.assertEqual(rows[0]["trust_tier"], "unverified")

    def test_malformed_enum_types_are_rejected_without_crashing(self):
        with self.assertRaisesRegex(ValueError, "rating must be"):
            adapt_rows([firm_row(rating=["correct"])])
        with self.assertRaisesRegex(ValueError, "cited_article_accuracy must be"):
            adapt_rows([firm_row(cited_article_accuracy=["right"])])
        with self.assertRaisesRegex(ValueError, "notes must be a string"):
            adapt_rows([firm_row(notes=None)])

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "explicit timezone"):
            adapt_rows([firm_row(updated_at="2026-11-14T12:30:00")])

    def test_missing_message_time_trust_tier_column_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "firm.csv"
            output = Path(directory) / "canonical.csv"
            headers = [name for name in firm_row() if name != "trust_tier"]
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=headers)
                writer.writeheader()
                writer.writerow({key: value for key, value in firm_row().items() if key != "trust_tier"})
            with self.assertRaisesRegex(ValueError, "trust_tier"):
                adapt_file(source, output)
            self.assertFalse(output.exists())

    def test_writes_utf8_bom_canonical_header_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "firm.csv"
            output = Path(directory) / "canonical.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(firm_row()))
                writer.writeheader()
                writer.writerow(firm_row())
            report = adapt_file(source, output)
            self.assertEqual(report["exported_rows"], 1)
            self.assertTrue(output.read_bytes().startswith(b"\\xef\\xbb\\xbf"))
            with output.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, EXPECTED_HEADER)
                self.assertEqual(next(reader)["answer_rating"], "partial")
            with self.assertRaises(FileExistsError):
                adapt_file(source, output)


if __name__ == "__main__":
    unittest.main()
