import importlib.util
import json
import shutil
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_decision252_candidate_map.py"
SPEC = importlib.util.spec_from_file_location("validate_decision252_candidate_map", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Decision252CandidateMapTests(unittest.TestCase):
    def test_map_is_complete_and_quarantined(self):
        self.assertEqual(MODULE.validate(), [])

    def _copy(self, target):
        shutil.copy2(MODULE.DEFAULT_FILE, target / MODULE.DEFAULT_FILE.name)
        return target / MODULE.DEFAULT_FILE.name

    def test_fake_official_match_and_retrieval_flag_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._copy(Path(tmp))
            data = json.loads(path.read_text(encoding="utf-8"))
            data["records"][0]["official_gazette_match"] = "matched"
            data["records"][0]["retrieval_eligible"] = True
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(path)
        self.assertTrue(any("official match must remain not_performed" in e for e in errors))
        self.assertTrue(any("must remain retrieval-ineligible" in e for e in errors))

    def test_missing_article_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._copy(Path(tmp))
            data = json.loads(path.read_text(encoding="utf-8"))
            data["records"] = [r for r in data["records"] if not (r["record_type"] == "article" and r["article"] == 2)]
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            errors = MODULE.validate(path)
        self.assertTrue(any("article coverage mismatch" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
