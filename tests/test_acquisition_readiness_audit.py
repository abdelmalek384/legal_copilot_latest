import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_acquisition_readiness", ROOT / "tools" / "validate_acquisition_readiness.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AcquisitionReadinessAuditTests(unittest.TestCase):
    def test_committed_manifest_is_not_collection_ready(self):
        manifest = json.loads((ROOT / "docs" / "collection_manifest.example.json").read_text(encoding="utf-8"))
        register = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        report = MODULE.audit(manifest, register)
        self.assertEqual(report["documents_checked"], len(manifest["documents"]))
        self.assertEqual(report["collection_ready_count"], 0)
        self.assertTrue(all(not item["collection_ready"] for item in report["documents"]))
        self.assertTrue(any(item["code"] == "manifest_collection_permission_not_allowed" for item in report["findings"]))

    def test_ready_collection_still_does_not_imply_commercial_product_use(self):
        manifest = {"documents": [{
            "document_id": "LAW-1",
            "source_id": "SRC-1",
            "direct_url": "https://laws.example.gov/law.pdf",
            "allowed_hosts": ["example.gov"],
            "collection_permission": "allowed",
            "permission_evidence": "written authorization ref AUTH-1",
            "terms_checked_on": "2026-10-23",
        }]}
        register = {"sources": [{
            "source_id": "SRC-1",
            "collection_permission": "allowed",
            "commercial_reuse_permission": "unknown",
            "permission_evidence": "written authorization ref AUTH-1",
            "terms_checked_on": "2026-10-23",
        }]}
        report = MODULE.audit(manifest, register)
        self.assertTrue(report["documents"][0]["collection_ready"])
        self.assertFalse(report["documents"][0]["commercial_product_use_ready"])
        self.assertIn("commercial_product_reuse_not_established", report["documents"][0]["warnings"])

    def test_manifest_permission_cannot_override_source_register(self):
        manifest = {"documents": [{
            "document_id": "LAW-2",
            "source_id": "SRC-2",
            "direct_url": "https://laws.example.gov/law.pdf",
            "allowed_hosts": ["laws.example.gov"],
            "collection_permission": "allowed",
            "permission_evidence": "claim",
            "terms_checked_on": "2026-10-23",
        }]}
        register = {"sources": [{
            "source_id": "SRC-2",
            "collection_permission": "unknown",
            "commercial_reuse_permission": "unknown",
            "permission_evidence": None,
            "terms_checked_on": None,
        }]}
        report = MODULE.audit(manifest, register)
        self.assertFalse(report["documents"][0]["collection_ready"])
        self.assertIn("source_register_does_not_allow_collection", report["documents"][0]["blockers"])

    def test_direct_url_host_must_match_allowlist(self):
        manifest = {"documents": [{
            "document_id": "LAW-3",
            "source_id": "SRC-3",
            "direct_url": "https://other.example.net/law.pdf",
            "allowed_hosts": ["example.gov"],
            "collection_permission": "allowed",
            "permission_evidence": "written authorization",
            "terms_checked_on": "2026-10-23",
        }]}
        register = {"sources": [{
            "source_id": "SRC-3",
            "collection_permission": "allowed",
            "commercial_reuse_permission": "allowed",
            "permission_evidence": "written authorization",
            "terms_checked_on": "2026-10-23",
        }]}
        report = MODULE.audit(manifest, register)
        self.assertIn("direct_url_host_not_in_allowlist", report["documents"][0]["blockers"])
        self.assertFalse(report["documents"][0]["collection_ready"])


if __name__ == "__main__":
    unittest.main()
