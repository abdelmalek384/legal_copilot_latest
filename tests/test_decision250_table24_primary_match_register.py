import tempfile
import unittest
from pathlib import Path

from tools.build_decision250_table24_primary_match_register import build_register


class Decision250Table24PrimaryMatchRegisterTests(unittest.TestCase):
    def test_register_covers_candidate_rows_and_starts_fail_closed(self):
        records = build_register()
        self.assertEqual(len(records), 781)
        self.assertEqual([record["candidate_row"] for record in records], list(range(1, 782)))
        self.assertTrue(all(record["retrieval_eligible"] is False for record in records))
        self.assertTrue(all(record["official_pdf_sha256"] is None for record in records))
        self.assertTrue(all(record["official_printed_page"] is None for record in records))
        self.assertTrue(all(record["counsel_review"] == "not_started" for record in records))
        placeholder = next(record for record in records if record["candidate_row"] == 599)
        self.assertEqual(placeholder["candidate_record_kind"], "unresolved_placeholder")
        self.assertFalse(placeholder["retrieval_eligible"])

    def test_missing_batches_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                build_register(Path(tmp))


if __name__ == "__main__":
    unittest.main()
