import copy
import json
import unittest
from pathlib import Path

from tools.validate_decision250_table23_candidates import DEFAULT_FILE, validate_data


class Decision250Table23CandidateValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DEFAULT_FILE.read_text(encoding="utf-8"))

    def test_repository_candidates_are_structurally_complete(self):
        self.assertEqual(validate_data(self.data), [])

    def test_missing_row_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["rows"].pop(5)
        errors = validate_data(data)
        self.assertTrue(any("expected 137 candidate rows" in error for error in errors))
        self.assertTrue(any("missing row numbers" in error for error in errors))

    def test_unit_pair_anomaly_is_rejected_not_corrected(self):
        data = copy.deepcopy(self.data)
        data["rows"][0]["quantity_lb"] = 1
        errors = validate_data(data)
        self.assertTrue(any("kg/lb candidate values differ" in error for error in errors))
        self.assertEqual(data["rows"][0]["quantity_lb"], 1)

    def test_official_hash_and_promotion_are_rejected(self):
        data = copy.deepcopy(self.data)
        data["official_pdf_downloaded_and_hashed"] = True
        data["rows"][0]["retrieval_eligible"] = True
        errors = validate_data(data)
        self.assertTrue(any("must not claim the official PDF" in error for error in errors))
        self.assertTrue(any("forbidden promotion/approval flag" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
