import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_legal_data_foundation.py"


class LegalDataFoundationMalformedInputTests(unittest.TestCase):
    def _run_with_inputs(self, manifest, question_line):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "tools").mkdir()
            (root / "docs").mkdir()
            shutil.copy2(SCRIPT, root / "tools" / SCRIPT.name)
            (root / "docs" / "source_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )
            (root / "docs" / "legal_coverage_matrix.csv").write_text(
                "practice_area,priority,core_materials,judgment_sources,temporal_checks,evaluation_owner,status\n"
                "civil,P0,law,judgments,dates,pending,pending\n",
                encoding="utf-8",
            )
            (root / "tests" / "legal_eval").mkdir(parents=True)
            (root / "tests" / "legal_eval" / "practice_questions.seed.jsonl").write_text(
                question_line + "\n", encoding="utf-8"
            )
            return subprocess.run(
                [sys.executable, str(root / "tools" / SCRIPT.name)],
                cwd=root, capture_output=True, text=True, check=False,
            )

    def _valid_source(self):
        return {
            "id": "SRC-1", "name": "Test source", "category": "official_primary",
            "url": "https://example.gov", "license_status": "unknown",
            "access_status": "candidate", "priority": "P0",
        }

    def _valid_question(self):
        return {
            "id": "Q1", "practice_area": "civil", "question_ar": "سؤال",
            "review_status": "needs_lawyer_review", "expected_answer": None,
            "expected_sources": [], "must_abstain_if_unverified": True,
        }

    def test_non_object_source_fails_with_controlled_validation_error(self):
        result = self._run_with_inputs({"sources": ["not-an-object"]}, json.dumps(self._valid_question(), ensure_ascii=False))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("VALIDATION FAILED: source #1 must be a JSON object", result.stderr)
        self.assertNotIn("AttributeError", result.stderr)

    def test_non_object_question_seed_fails_with_controlled_validation_error(self):
        result = self._run_with_inputs({"sources": [self._valid_source()]}, "[]")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("VALIDATION FAILED: question seed line 1 must be a JSON object", result.stderr)
        self.assertNotIn("AttributeError", result.stderr)

    def test_non_object_manifest_fails_with_controlled_validation_error(self):
        result = self._run_with_inputs([], json.dumps(self._valid_question(), ensure_ascii=False))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("VALIDATION FAILED: source manifest must be a JSON object", result.stderr)
        self.assertNotIn("AttributeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
