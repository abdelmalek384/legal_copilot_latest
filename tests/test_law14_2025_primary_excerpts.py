import importlib.util
import json
import shutil
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_law14_2025_primary_excerpts.py"
SPEC = importlib.util.spec_from_file_location("validate_law14_2025_primary_excerpts", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Law14OfficialPrimaryExcerptTests(unittest.TestCase):
    def test_repository_excerpts_are_structurally_valid_and_quarantined(self):
        self.assertEqual(MODULE.validate(), [])

    def _copy(self, target):
        shutil.copy2(MODULE.DEFAULT_FILE, target / MODULE.DEFAULT_FILE.name)
        return target / MODULE.DEFAULT_FILE.name

    def test_missing_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = MODULE.validate(Path(tmp) / "missing.jsonl")
        self.assertTrue(any("missing official excerpt JSONL" in error for error in errors))

    def test_cannot_claim_hash_or_retrieval_eligibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._copy(Path(tmp))
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            records[0]["original_pdf_sha256"] = "invented"
            records[0]["retrieval_eligible"] = True
            path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in records) + "\n", encoding="utf-8")
            errors = MODULE.validate(path)
        self.assertTrue(any("must not invent a PDF SHA-256" in error for error in errors))
        self.assertTrue(any("must remain retrieval-ineligible" in error for error in errors))

    def test_wrong_page_locator_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._copy(Path(tmp))
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            records[0]["printed_page"] = 999
            path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in records) + "\n", encoding="utf-8")
            errors = MODULE.validate(path)
        self.assertTrue(any("incorrect PDF/printed page locator" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
