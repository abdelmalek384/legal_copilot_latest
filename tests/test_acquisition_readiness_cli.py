import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_acquisition_readiness",
    ROOT / "tools" / "validate_acquisition_readiness.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def passed_scope_review():
    return {
        "status": "passed",
        "evidence": "AUTH-1 section 2",
        "reviewer_id": "test-reviewer-001",
        "reviewed_on": "2026-10-23",
        "evidence_reference": "AUTH-1",
        "evidence_url": "https://laws.example.gov/rights/authorization",
        "access_method": "direct_document_url",
        "source_terms_reviewed": True,
        "scope": {
            "storage": True,
            "text_extraction": True,
            "indexing": True,
            "commercial_product_use": True,
            "excerpt_display": True,
        },
    }


class AcquisitionReadinessCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest = self.root / "manifest.json"
        self.register = self.root / "register.json"
        self.payload = {
            "documents": [{
                "document_id": "LAW-1",
                "source_id": "SRC-1",
                "direct_url": "https://laws.example.gov/law.pdf",
                "allowed_hosts": ["example.gov"],
                "collection_permission": "allowed",
                "permission_evidence": "written authorization ref AUTH-1",
                "permission_evidence_url": "https://laws.example.gov/rights/collection",
                "terms_checked_on": "2026-10-23",
                "terms_url": "https://laws.example.gov/terms",
                "permission_scope_review": passed_scope_review(),
            }]
        }
        self.register_payload = {
            "sources": [{
                "source_id": "SRC-1",
                "collection_permission": "allowed",
                "commercial_reuse_permission": "unknown",
                "permission_evidence": "written authorization ref AUTH-1",
                "permission_evidence_url": "https://laws.example.gov/rights/collection",
                "terms_checked_on": "2026-10-23",
                "terms_url": "https://laws.example.gov/terms",
            }]
        }
        self.manifest.write_text(json.dumps(self.payload), encoding="utf-8")
        self.register.write_text(json.dumps(self.register_payload), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *extra):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = MODULE.main([
                "--manifest", str(self.manifest),
                "--register", str(self.register),
                *extra,
            ])
        return code, json.loads(output.getvalue())

    def test_production_gate_fails_when_commercial_reuse_is_unknown(self):
        code, report = self.run_cli("--require-ready")
        self.assertEqual(report["collection_ready_count"], 1)
        self.assertEqual(report["commercial_product_use_ready_count"], 0)
        self.assertEqual(code, 1)

    def test_collection_only_gate_is_explicitly_distinct(self):
        code, report = self.run_cli("--require-collection-ready")
        self.assertEqual(report["collection_ready_count"], 1)
        self.assertEqual(report["commercial_product_use_ready_count"], 0)
        self.assertEqual(code, 0)

    def test_production_gate_blocks_allowed_label_without_separate_commercial_evidence(self):
        self.register_payload["sources"][0]["commercial_reuse_permission"] = "allowed"
        self.register.write_text(json.dumps(self.register_payload), encoding="utf-8")
        code, report = self.run_cli("--require-ready")
        self.assertEqual(report["collection_ready_count"], 1)
        self.assertEqual(report["commercial_product_use_ready_count"], 0)
        self.assertEqual(code, 1)
        self.assertIn(
            "commercial_permission_evidence_or_date_missing",
            report["documents"][0]["warnings"],
        )
        self.assertIn(
            "source_commercial_reuse_evidence_url_missing_or_invalid",
            report["documents"][0]["warnings"],
        )

    def test_production_gate_passes_only_when_both_permissions_and_evidence_are_allowed(self):
        source = self.register_payload["sources"][0]
        source["commercial_reuse_permission"] = "allowed"
        source["commercial_reuse_evidence"] = "Written commercial license AUTH-COMM-1"
        source["commercial_reuse_evidence_url"] = "https://laws.example.gov/rights/commercial"
        source["commercial_terms_checked_on"] = "2026-10-23"
        self.register.write_text(json.dumps(self.register_payload), encoding="utf-8")
        code, report = self.run_cli("--require-ready")
        self.assertEqual(report["collection_ready_count"], 1)
        self.assertEqual(report["commercial_product_use_ready_count"], 1)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
