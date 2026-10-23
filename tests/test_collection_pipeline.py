import json
import tempfile
import unittest
from pathlib import Path

from tools.collect_legal_documents import article_audit, check_permission, load_manifest, validate_public_https_url


class CollectionPipelineTests(unittest.TestCase):
    def test_permission_is_opt_in(self):
        with self.assertRaises(ValueError):
            check_permission({"collection_permission": "unknown"})

    def test_permission_requires_evidence_and_date(self):
        doc = {
            "collection_permission": "allowed",
            "permission_evidence": "",
            "terms_checked_on": "2026-10-23",
            "allowed_hosts": ["example.gov"],
        }
        with self.assertRaises(ValueError):
            check_permission(doc)

    def test_rejects_http_and_unapproved_host(self):
        with self.assertRaises(ValueError):
            validate_public_https_url("http://example.gov/law.pdf", {"example.gov"})
        with self.assertRaises(ValueError):
            validate_public_https_url("https://other.example/law.pdf", {"example.gov"})

    def test_article_audit_normalizes_arabic_digits_and_finds_gaps(self):
        result = article_audit("المادة ١\nنص\n\nالمادة ٣\nنص")
        self.assertEqual(result["article_headings_detected"], 2)
        self.assertEqual(result["numeric_article_gaps"], [2])

    def test_article_audit_warns_when_no_headings(self):
        result = article_audit("A short plain text document without legal article headings.")
        self.assertEqual(result["article_headings_detected"], 0)
        self.assertTrue(result["warnings"])

    def test_manifest_requires_document_list_and_unique_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "manifest.json"
            p.write_text(json.dumps({"documents": [
                {"document_id": "same"}, {"document_id": "same"}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_manifest(p)


if __name__ == "__main__":
    unittest.main()
