import json
import tempfile
import unittest
from pathlib import Path

from tools.collect_legal_documents import check_permission, load_manifest

ROOT = Path(__file__).resolve().parents[1]

class FirstOfficialBatchManifestTests(unittest.TestCase):
    def test_manifest_has_two_unique_official_document_entries(self):
        path = ROOT / "docs" / "collection_manifest.example.json"
        docs = load_manifest(path)
        self.assertEqual(len(docs), 4)
        self.assertEqual(len({d["document_id"] for d in docs}), 2)
        self.assertTrue(all(d["source_id"] for d in docs))

    def test_entries_have_permission_evidence_and_restricted_hosts(self):
        docs = load_manifest(ROOT / "docs" / "collection_manifest.example.json")
        for doc in docs:
            hosts = check_permission(doc)
            self.assertTrue(hosts)
            self.assertIn("Article 141", doc["permission_evidence"])
            self.assertEqual(doc["legal_status_assessment"], "unknown")
            self.assertIsNone(doc["effective_date"])
            self.assertTrue(all("/" not in host for host in hosts))

    def test_manifest_does_not_allow_unknown_permission(self):
        doc = {
            "document_id": "law-test",
            "source_id": "test",
            "direct_url": "https://example.gov/law.pdf",
            "allowed_hosts": ["example.gov"],
            "collection_permission": "unknown",
            "permission_evidence": "unverified",
            "terms_checked_on": "2026-10-23"
        }
        with self.assertRaises(ValueError):
            check_permission(doc)

if __name__ == "__main__":
    unittest.main()
