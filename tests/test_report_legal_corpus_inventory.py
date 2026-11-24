import importlib.util
import json
import tempfile
import os
from unittest.mock import patch
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "report_legal_corpus_inventory", ROOT / "tools" / "report_legal_corpus_inventory.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LegalCorpusInventoryTests(unittest.TestCase):
    def test_read_json_rejects_duplicate_keys_at_all_object_depths(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "registry.json"
            for raw in ('{"sources":[],"sources":[]}', '{"sources":[{"source_id":"A","metadata":{"status":"unknown","status":"allowed"}}]}'):
                path.write_text(raw, encoding="utf-8")
                with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                    MODULE.read_json(path)

    def test_hostname_ignores_malformed_https_urls(self):
        self.assertEqual(MODULE.hostname("https://www.example.gov/law"), "www.example.gov")
        for value in (
            " https://example.gov/law",
            "https://example.gov/path with spaces",
            "https://user:secret@example.gov/law",
            "https://@example.gov/law",
            "https://example.gov:not-a-port/law",
            "https://example.gov:99999/law",
            "https://example.gov:0/law",
            "https://example.gov:/law",
            "https://example.gov/law\x7f",
            "https://example.gov\\law",
            "https://[malformed/law",
        ):
            with self.subTest(value=value):
                self.assertIsNone(MODULE.hostname(value))

    def test_coverage_matrix_rejects_duplicate_headers_ragged_rows_and_duplicate_areas(self):
        headers = "practice_area,priority,core_materials,judgment_sources,temporal_checks,evaluation_owner,status"
        valid = "Civil law,P0,Civil Code,Cassation,amendments,lawyer,not_started"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "coverage.csv"
            cases = (
                (headers + ",status\\n" + valid + ",not_started\\n", "duplicate column headers"),
                (headers + "\\n" + valid + ",extra\\n", "has 8 fields; expected 7"),
                (headers + "\\n" + valid + "\\n" + valid + "\\n", "duplicate practice_area"),
            )
            for raw, message in cases:
                path.write_text(raw, encoding="utf-8")
                with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                    MODULE.read_coverage_matrix(path)

    def test_coverage_matrix_rejects_symlinks_and_accepts_current_register(self):
        self.assertEqual(len(MODULE.read_coverage_matrix(MODULE.DEFAULTS["coverage"])), 21)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "real.csv"
            target.write_text(
                "practice_area,priority,core_materials,judgment_sources,temporal_checks,evaluation_owner,status\\n"
                "Civil law,P0,Civil Code,Cassation,amendments,lawyer,not_started\\n",
                encoding="utf-8",
            )
            link = root / "link.csv"
            link.symlink_to(target)
            with self.assertRaises(OSError):
                MODULE.read_coverage_matrix(link)

    def test_repository_inventory_does_not_claim_corpus_verification(self):
        report = MODULE.build_report(MODULE.DEFAULTS)
        self.assertTrue(report["read_only"])
        self.assertFalse(report["corpus_claims"]["candidate_catalogue_is_legal_corpus"])
        self.assertFalse(report["corpus_claims"]["authenticity_or_currentness_certified"])
        self.assertFalse(report["corpus_claims"]["lawyer_review_inferred"])
        self.assertGreater(report["counts"]["candidate_documents"], 0)
        self.assertIn("collection_permission", report["statuses"])

    def test_cross_register_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = {}
            for name, original in MODULE.DEFAULTS.items():
                target = root / original.name
                target.write_bytes(original.read_bytes())
                paths[name] = target
            permissions = json.loads(paths["permissions"].read_text(encoding="utf-8"))
            permissions["sources"] = [
                source for source in permissions["sources"]
                if source.get("source_id") != "EG-AMIRI-PRESS"
            ]
            paths["permissions"].write_text(
                json.dumps(permissions, ensure_ascii=False), encoding="utf-8"
            )
            report = MODULE.build_report(paths)
            issue_codes = {issue["code"] for issue in report["cross_registry_issues"]}
            self.assertIn("candidate_sources_missing_permission_register", issue_codes)

    def test_markdown_is_explicit_about_scope(self):
        report = MODULE.build_report(MODULE.DEFAULTS)
        output = MODULE.markdown(report)
        self.assertIn("not a verified legal corpus", output.lower())
        self.assertIn("no database or legal-text files were scanned", output.lower())

    def test_documented_cli_runs_without_pythonpath_from_outside_repo(self):
        import subprocess
        import sys

        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "report_legal_corpus_inventory.py")],
                cwd=temp,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["report_type"], "legal_corpus_artifact_inventory")
        self.assertTrue(report["read_only"])


    def test_read_json_rejects_symlink_swap_and_fifo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "register.json"
            target.write_text('{"sources":[]}', encoding="utf-8")
            outside = root / "outside.json"
            outside.write_text('{"sources":[]}', encoding="utf-8")
            real_open = MODULE.os.open
            swapped = False

            def replace_before_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if Path(path) == target and not swapped:
                    swapped = True
                    target.unlink()
                    target.symlink_to(outside)
                return real_open(path, flags, *args, **kwargs)

            with patch("tools.validate_source_permission_register.os.open", side_effect=replace_before_open):
                with self.assertRaises(OSError):
                    MODULE.read_json(target)
            self.assertTrue(swapped)
            if hasattr(os, "mkfifo"):
                fifo = root / "register.fifo"
                os.mkfifo(fifo)
                with self.assertRaises(OSError):
                    MODULE.read_json(fifo)

if __name__ == "__main__":
    unittest.main()
