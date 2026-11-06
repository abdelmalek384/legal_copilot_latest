import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "report_legal_corpus_inventory", ROOT / "tools" / "report_legal_corpus_inventory.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LegalCorpusInventoryTests(unittest.TestCase):
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
            "https://[malformed/law",
        ):
            with self.subTest(value=value):
                self.assertIsNone(MODULE.hostname(value))

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


if __name__ == "__main__":
    unittest.main()
