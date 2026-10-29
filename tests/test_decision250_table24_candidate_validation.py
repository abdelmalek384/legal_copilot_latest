import importlib.util
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


if __name__ == "__main__":
    unittest.main()
