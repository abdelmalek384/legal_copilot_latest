import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Running "python tests/test_..." sets sys.path[0] to tests/, not the repo root.
sys.path.insert(0, str(ROOT))

from tools.collect_legal_documents import check_permission, load_manifest, validate_manifest_hosts


class FirstOfficialBatchManifestTests(unittest.TestCase):
    def test_manifest_has_four_unique_official_document_entries(self):
        docs = load_manifest(ROOT / "docs" / "collection_manifest.example.json")
        self.assertEqual(len(docs), 4)
        self.assertEqual(len({d["document_id"] for d in docs}), 4)
        self.assertTrue(all(d["source_id"] for d in docs))

    def test_pending_entries_have_valid_hosts_but_are_not_authorized_for_collection(self):
        docs = load_manifest(ROOT / "docs" / "collection_manifest.example.json")
        for doc in docs:
            hosts = validate_manifest_hosts(doc)
            self.assertTrue(hosts)
            self.assertIn("Article 141", doc["permission_evidence"])
            self.assertEqual(doc["collection_permission"], "permission_pending")
            self.assertEqual(doc["legal_status_assessment"], "unknown")
            with self.assertRaises(ValueError):
                check_permission(doc)
            # Effective dates may be supplied for an individual instrument; when
            # present they must be ISO dates. Their presence does not verify status.
            effective_date = doc["effective_date"]
            if effective_date is not None:
                self.assertEqual(date.fromisoformat(effective_date).isoformat(), effective_date)
            self.assertTrue(all("/" not in host for host in hosts))

    def test_manifest_does_not_allow_unknown_permission(self):
        doc = {
            "document_id": "law-test",
            "source_id": "test",
            "direct_url": "https://example.gov/law.pdf",
            "allowed_hosts": ["example.gov"],
            "collection_permission": "unknown",
            "permission_evidence": "unverified",
            "terms_checked_on": "2026-10-23",
        }
        with self.assertRaises(ValueError):
            check_permission(doc)


    def test_criminal_procedure_commencement_stays_unverified_until_counsel_review(self):
        candidates_path = ROOT / "docs" / "first_batch_candidates.json"
        candidates = json.loads(candidates_path.read_text(encoding="utf-8"))["documents"]
        by_id = {item["document_id"]: item for item in candidates}
        law_174 = by_id["eg_criminal_procedure_law_174_2025_moj_pdf"]
        law_160 = by_id["eg_criminal_procedure_law_160_2026_amiri_press"]

        self.assertIsNone(law_174["effective_date"])
        self.assertFalse(law_174["legal_authenticity_verified"])
        self.assertFalse(law_174["current_legal_status_verified"])
        self.assertFalse(law_174["amendment_history_verified"])
        self.assertIn("commencement", law_174["reason_not_approved"].lower())
        self.assertEqual(law_160["amends_document_id"], law_174["document_id"])
        self.assertFalse(law_160["legal_authenticity_verified"])
        self.assertFalse(law_160["current_legal_status_verified"])


if __name__ == "__main__":
    unittest.main()
