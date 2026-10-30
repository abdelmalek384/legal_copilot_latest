import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_decisions_251_252_candidates import DATA_DIR, validate, validate_record


class Decisions251252CandidateValidationTests(unittest.TestCase):
    def test_repository_candidate_files_are_valid(self):
        self.assertEqual(validate(), [])

    def test_decision_252_cannot_be_marked_retrieval_eligible(self):
        filename = "decision_252_numeric_candidate_assertions_2026-10-29.json"
        record = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        record["authoritative_retrieval_eligible"] = True
        errors = validate_record(record, "252", filename)
        self.assertTrue(any("eligibility must remain false" in error for error in errors))

    def test_candidate_row_cannot_be_promoted(self):
        filename = "decision_251_numeric_and_eligibility_candidates_2026-10-29.json"
        record = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        record["assertions"][0]["approved"] = True
        errors = validate_record(record, "251", filename)
        self.assertTrue(any("forbidden promotion flag" in error for error in errors))

    def test_summary_only_assertion_still_needs_source_locator(self):
        filename = "decision_252_numeric_candidate_assertions_2026-10-29.json"
        record = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        item = copy.deepcopy(record["assertions"][-1])
        item.pop("source_url", None)
        record["assertions"][-1] = item
        errors = validate_record(record, "252", filename)
        self.assertTrue(any("lacks a source locator" in error for error in errors))

    def test_missing_candidate_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = validate(Path(tmp))
        self.assertTrue(any("missing candidate file" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
