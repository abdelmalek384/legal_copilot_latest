import tempfile
import unittest
from pathlib import Path

from tools.output_path_safety import ensure_output_paths_safe


class OutputPathSafetyTests(unittest.TestCase):
    def test_rejects_direct_and_resolved_input_aliases(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            protected = root / "evidence.json"
            protected.write_text("preserve", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "protected input"):
                ensure_output_paths_safe([protected], [protected])

            alias = root / "nested" / ".." / "evidence.json"
            with self.assertRaisesRegex(ValueError, "protected input"):
                ensure_output_paths_safe([alias], [protected])

    def test_rejects_symlink_alias_to_protected_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            protected = root / "source.json"
            protected.write_text("preserve", encoding="utf-8")
            alias = root / "report.json"
            try:
                alias.symlink_to(protected)
            except (NotImplementedError, OSError):
                self.skipTest("symlinks are unavailable in this environment")

            with self.assertRaisesRegex(ValueError, "protected input"):
                ensure_output_paths_safe([alias], [protected])

    def test_rejects_hardlink_alias_to_protected_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            protected = root / "source.json"
            protected.write_text("preserve", encoding="utf-8")
            alias = root / "report.json"
            try:
                alias.hardlink_to(protected)
            except (NotImplementedError, OSError):
                self.skipTest("hard links are unavailable in this environment")

            with self.assertRaisesRegex(ValueError, "protected input"):
                ensure_output_paths_safe([alias], [protected])

    def test_rejects_two_report_outputs_that_alias(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = root / "report.json"
            with self.assertRaisesRegex(ValueError, "must be distinct"):
                ensure_output_paths_safe([report, report], [])

    def test_allows_distinct_outputs_and_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            protected = root / "source.json"
            protected.write_text("preserve", encoding="utf-8")
            ensure_output_paths_safe(
                [root / "report.json", root / "report.md"],
                [protected],
            )


if __name__ == "__main__":
    unittest.main()
