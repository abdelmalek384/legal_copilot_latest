import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import validate_decisions_251_252_fee_ceiling_candidates as MODULE


class Decisions251252FeeCeilingCandidateTests(unittest.TestCase):
    def _copy_inputs(self, root: Path) -> None:
        for filename in MODULE.EXPECTED:
            shutil.copy2(MODULE.DATA / filename, root / filename)

    def test_current_candidate_fee_crosscheck_passes_without_promotion(self):
        self.assertEqual(MODULE.validate(), [])

    def test_rejects_candidate_licence_fee_above_parent_statute_ceiling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_inputs(root)
            path = root / "decision_251_numeric_and_eligibility_candidates_2026-10-29.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            item = next(x for x in record["assertions"] if x["id"] == "251-A11")
            item["value"] = 50_001
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(root)
        self.assertTrue(any("differs from the recorded cross-check" in error or "exceeds the EGP 50000" in error for error in errors))

    def test_rejects_non_licence_charge_being_relabelled_as_licence_fee(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_inputs(root)
            path = root / "decision_252_numeric_candidate_assertions_2026-10-29.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            item = next(x for x in record["assertions"] if x["id"] == "252-N022")
            item["topic"] = "provider_licensing_fee"
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(root)
        self.assertTrue(any("must remain separately classified" in error for error in errors))

    def test_rejects_fee_candidate_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_inputs(root)
            path = root / "decision_252_numeric_candidate_assertions_2026-10-29.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            item = next(x for x in record["assertions"] if x["id"] == "252-N019")
            item["retrieval_eligible"] = True
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(root)
        self.assertTrue(any("forbidden promotion flag" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
