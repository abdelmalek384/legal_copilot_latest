import json
import tempfile
import unittest
from unittest.mock import patch
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tools.collect_legal_documents as collector
from tools.collect_legal_documents import article_audit, check_permission, download_document, load_manifest, validate_public_https_url


class CollectionPipelineTests(unittest.TestCase):
    def test_download_never_overwrites_existing_original_or_version_collision(self):
        class FakeResponse:
            status_code = 200

            def __init__(self, url, payload):
                self.url = url
                self.payload = payload
                self.headers = {
                    "content-type": "application/pdf",
                    "content-length": str(len(payload)),
                    "etag": '"fixture"',
                }

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def raise_for_status(self):
                return None

            def iter_bytes(self):
                yield self.payload

        class FakeClient:
            def __init__(self, payload):
                self.payload = payload

            def stream(self, method, url, follow_redirects=False):
                self.assertions = (method, url, follow_redirects)
                return FakeResponse(url, self.payload)

        payload = b"%PDF-new-original"
        digest = collector.sha256_bytes(payload)
        fixed = dt.datetime(2026, 10, 26, 17, 0, 0, tzinfo=dt.timezone.utc)
        doc = {
            "document_id": "TEST-LAW",
            "source_id": "TEST-SOURCE",
            "title": "Test law",
            "direct_url": "https://example.gov/law.pdf",
            "allowed_hosts": ["example.gov"],
            "collection_permission": "allowed",
            "permission_evidence": "Reviewed source terms evidence",
            "terms_checked_on": "2026-10-26",
        }
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            original_dir = out / "originals" / "TEST-LAW"
            original_dir.mkdir(parents=True)
            original = original_dir / "original.pdf"
            original.write_bytes(b"%PDF-older-original")
            collision = original_dir / f"original-20261026T170000000000Z-{digest[:12]}.pdf"
            collision.write_bytes(b"%PDF-different-existing-version")

            with patch("tools.collect_legal_documents.validate_public_https_url", return_value="example.gov"), \
                 patch("tools.collect_legal_documents.dt.datetime") as clock:
                clock.now.return_value = fixed
                result = download_document(FakeClient(payload), doc, out, 1024)
                self.assertEqual(original.read_bytes(), b"%PDF-older-original")
                self.assertEqual(collision.read_bytes(), b"%PDF-different-existing-version")
                created = out / result["original_path"]
                self.assertEqual(created.read_bytes(), payload)
                self.assertEqual(result["sha256"], digest)
                self.assertTrue(created.name.endswith(f"-{digest[:12]}-1.pdf"))

                repeated = download_document(FakeClient(payload), doc, out, 1024)
                self.assertEqual(repeated["original_path"], result["original_path"])
                self.assertEqual(created.read_bytes(), payload)

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

    def test_permission_rejects_future_terms_review_date(self):
        doc = {
            "collection_permission": "allowed",
            "permission_evidence": "Reviewed source terms evidence",
            "terms_checked_on": "9999-12-31",
            "allowed_hosts": ["example.gov"],
            "direct_url": "https://example.gov/law.pdf",
        }
        with self.assertRaisesRegex(ValueError, "cannot be in the future"):
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

    def test_manifest_rejects_non_object_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "manifest.json"
            p.write_text(json.dumps({"documents": ["not-an-object"]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_manifest(p)

    def test_manifest_rejects_path_traversal_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "manifest.json"
            p.write_text(json.dumps({"documents": [
                {"document_id": "../escape", "source_id": "test"}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_manifest(p)

    def test_manifest_requires_source_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "manifest.json"
            p.write_text(json.dumps({"documents": [
                {"document_id": "law-001"}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_manifest(p)


if __name__ == "__main__":
    unittest.main()
