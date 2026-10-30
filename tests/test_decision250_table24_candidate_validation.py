import importlib.util
import json
import shutil
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_decision250_table24_candidates.py"
SPEC = importlib.util.spec_from_file_location("validate_decision250_table24_candidates", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Decision250Table24CandidateValidationTests(unittest.TestCase):
    def test_repository_candidate_batches_are_structurally_complete(self):
        errors = MODULE.validate()
        self.assertEqual(errors, [], "\n".join(errors))

    def test_flatten_rows_includes_nested_variants(self):
        rows = [
            {
                "row": 28,
                "children": [
                    {"row": 29},
                    {"row": 30, "children": [{"row": 31}]},
                ],
            }
        ]
        self.assertEqual(
            [item["row"] for item in MODULE.flatten_rows(rows)],
            [28, 29, 30, 31],
        )

    def test_missing_batch_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = MODULE.validate(Path(tmp))
        self.assertTrue(any("missing batch file" in error for error in errors))
        self.assertTrue(any("missing Table 24 row numbers" in error for error in errors))

    def _copy_batches(self, target):
        for filename in MODULE.BATCHES:
            shutil.copy2(MODULE.DATA_DIR / filename, target / filename)

    def test_candidate_cannot_claim_retrieval_eligibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_batches(root)
            path = root / MODULE.BATCHES[0]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["rows"][0]["retrieval_eligible"] = True
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(root)
        self.assertTrue(any("forbidden promotion/approval flag" in error for error in errors))

    def test_rows_1_to_327_require_secondary_scan_page_locator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_batches(root)
            path = root / MODULE.BATCHES[0]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["rows"][0].pop("secondary_scan_image_url", None)
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(root)
        self.assertTrue(any("missing/wrong secondary scan image URL" in error for error in errors))

    def test_partial_secondary_image_spot_check_requires_field_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_batches(root)
            path = root / MODULE.BATCHES[0]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["rows"][0]["secondary_scan_match_status"] = "secondary_image_spot_check_partial_fields"
            data["rows"][0]["secondary_scan_fields_checked"] = ["chemical_name"]
            data["rows"][0]["secondary_scan_checked_on"] = "2026-10-30"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(root)
        self.assertTrue(any("incomplete secondary image spot-check fields" in error for error in errors))

    def test_secondary_image_discrepancy_requires_evidence_and_pending_original_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_batches(root)
            path = root / MODULE.BATCHES[3]
            data = json.loads(path.read_text(encoding="utf-8"))
            row = next(x for x in data["rows"] if x["row"] == 61)
            row["secondary_scan_match_status"] = "secondary_image_discrepancy_found"
            row["secondary_scan_fields_checked"] = ["chemical_name", "cas_identifier", "primary_exposure_limit_token", "unit"]
            row["secondary_scan_checked_on"] = "2026-10-30"
            row["secondary_scan_discrepancy"] = {"field": "cas_identifier", "candidate_transcription": "x", "secondary_image_observed_tentative": "y", "status": "approved"}
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(root)
        self.assertTrue(any("pending original Gazette confirmation" in error for error in errors))

    def test_candidate_cannot_claim_official_pdf_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_batches(root)
            path = root / MODULE.BATCHES[0]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["source"]["official_pdf_sha256"] = "fake-hash"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(root)
        self.assertTrue(any("must not claim an official PDF hash" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
