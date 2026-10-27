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


def approved_scope_review(**overrides):
    review = {
        "reviewer_id": "test-reviewer-001",
        "reviewed_on": "2026-10-26",
        "evidence_reference": "TEST-TERMS-REVIEW-001",
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
    review.update(overrides)
    return review


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
            "permission_scope_review": approved_scope_review(),
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

    def test_extraction_artifacts_are_content_addressed_and_prior_versions_are_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            original_dir = out / "originals" / "TEST-LAW"
            original_dir.mkdir(parents=True)
            versions = []
            for index, raw in enumerate((b"Article 1\\nOriginal text version one.", b"Article 1\\nOriginal text version two.")):
                original = original_dir / ("original.txt" if index == 0 else f"original-version-{index}.txt")
                original.write_bytes(raw)
                metadata = {
                    "document_id": "TEST-LAW",
                    "source_id": "TEST-SOURCE",
                    "original_path": str(original.relative_to(out)),
                    "http_content_type": "text/plain",
                    "sha256": collector.sha256_bytes(raw),
                }
                result = collector.process_document(out, metadata)
                versions.append(result)
            self.assertNotEqual(versions[0]["extracted_text_path"], versions[1]["extracted_text_path"])
            self.assertNotEqual(versions[0]["audit_path"], versions[1]["audit_path"])
            for version in versions:
                self.assertTrue((out / version["extracted_text_path"]).is_file())
                self.assertTrue((out / version["audit_path"]).is_file())
                self.assertEqual(version["review_status"], "pending_human_review")
                self.assertFalse(version["legal_authenticity_verified"])

    def test_process_existing_rejects_traversal_and_original_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            original_dir = out / "originals" / "TEST-LAW"
            original_dir.mkdir(parents=True)
            original = original_dir / "original.txt"
            original.write_text("safe text", encoding="utf-8")
            base = {
                "document_id": "TEST-LAW",
                "source_id": "TEST-SOURCE",
                "original_path": "originals/TEST-LAW/original.txt",
                "http_content_type": "text/plain",
                "sha256": collector.sha256_bytes(b"safe text"),
            }
            with self.assertRaisesRegex(ValueError, "stay inside"):
                collector.process_document(out, {**base, "original_path": "../../outside.txt"})
            with self.assertRaisesRegex(ValueError, "does not match metadata"):
                collector.process_document(out, {**base, "sha256": "0" * 64})

    def test_process_existing_rejects_symlinked_original(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            original_dir = out / "originals" / "TEST-LAW"
            original_dir.mkdir(parents=True)
            outside = out / "outside.txt"
            outside.write_text("external text", encoding="utf-8")
            (original_dir / "original.txt").symlink_to(outside)
            metadata = {
                "document_id": "TEST-LAW",
                "source_id": "TEST-SOURCE",
                "original_path": "originals/TEST-LAW/original.txt",
                "http_content_type": "text/plain",
                "sha256": collector.sha256_bytes(b"external text"),
            }
            with self.assertRaisesRegex(ValueError, "symbolic links"):
                collector.process_document(out, metadata)

    def test_metadata_history_preserves_prior_retrievals_and_collision_records(self):
        first = {
            "document_id": "TEST-LAW",
            "retrieved_at": "2026-10-26T18:00:00.123456+00:00",
            "sha256": "a" * 64,
            "source_url": "https://example.gov/law.pdf",
            "etag": '"first"',
        }
        second = {**first, "retrieved_at": "2026-10-26T18:01:00.123456+00:00", "sha256": "b" * 64, "etag": '"second"'}
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            current = collector.persist_metadata(out, "TEST-LAW", first)
            collector.persist_metadata(out, "TEST-LAW", second)
            self.assertEqual(json.loads(current.read_text(encoding="utf-8")), second)
            history = sorted((out / "metadata" / "history" / "TEST-LAW").glob("*.json"))
            self.assertEqual(len(history), 2)
            self.assertEqual({json.loads(p.read_text(encoding="utf-8"))["sha256"] for p in history}, {"a" * 64, "b" * 64})

            same_time_different_metadata = {**second, "etag": '"third"'}
            collector.persist_metadata(out, "TEST-LAW", same_time_different_metadata)
            history = sorted((out / "metadata" / "history" / "TEST-LAW").glob("*.json"))
            self.assertEqual(len(history), 3)
            self.assertEqual(json.loads(current.read_text(encoding="utf-8")), same_time_different_metadata)
            self.assertEqual({json.loads(p.read_text(encoding="utf-8"))["etag"] for p in history}, {'"first"', '"second"', '"third"'})

    def test_metadata_persistence_refuses_symlinked_current_pointer(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            meta_dir = out / "metadata"
            meta_dir.mkdir()
            target = out / "outside.json"
            target.write_text('{"sentinel":"untouched"}', encoding="utf-8")
            (meta_dir / "TEST-LAW.json").symlink_to(target)
            with self.assertRaises(ValueError):
                collector.persist_metadata(out, "TEST-LAW", {"document_id": "TEST-LAW"})
            self.assertEqual(target.read_text(encoding="utf-8"), '{"sentinel":"untouched"}')

    def test_collector_refuses_symlinked_storage_roots(self):
        metadata = {"document_id": "TEST-LAW", "retrieved_at": "2026-10-26T18:00:00+00:00", "sha256": "a" * 64}
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            outside = out / "outside"
            outside.mkdir()
            meta_dir = out / "metadata"
            meta_dir.mkdir()
            (meta_dir / "history").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                collector.persist_metadata(out, "TEST-LAW", metadata)
            (out / "metadata" / "history").unlink()
            (out / "originals").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                collector.store_original(out, "TEST-LAW", ".pdf", b"%PDF-safe")
            self.assertEqual(list(outside.iterdir()), [])

    def test_storage_helpers_reject_unsafe_document_ids(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            for bad_id in ("../escape", ".hidden", "has/slash", "x" * 129):
                with self.subTest(document_id=bad_id):
                    with self.assertRaises(ValueError):
                        collector.store_original(out, bad_id, ".pdf", b"%PDF-safe")
                    with self.assertRaises(ValueError):
                        collector.persist_metadata(out, bad_id, {"document_id": bad_id})

    def test_source_hostname_rejects_any_non_public_dns_answer(self):
        public_answer = (2, 1, 6, "", ("8.8.8.8", 443))
        private_answer = (2, 1, 6, "", ("127.0.0.1", 443))
        with patch("tools.collect_legal_documents.socket.getaddrinfo", return_value=[public_answer]):
            self.assertEqual(validate_public_https_url("https://example.gov/law.pdf", {"example.gov"}), "example.gov")
        with patch("tools.collect_legal_documents.socket.getaddrinfo", return_value=[public_answer, private_answer]):
            with self.assertRaisesRegex(ValueError, "non-public address"):
                validate_public_https_url("https://example.gov/law.pdf", {"example.gov"})

    def test_source_hostname_resolution_failure_fails_closed(self):
        with patch("tools.collect_legal_documents.socket.getaddrinfo", side_effect=OSError("no resolver")):
            with self.assertRaisesRegex(ValueError, "Cannot resolve source host"):
                validate_public_https_url("https://example.gov/law.pdf", {"example.gov"})

    def test_permission_is_opt_in(self):
        with self.assertRaises(ValueError):
            check_permission({"collection_permission": "unknown"})

    def test_permission_requires_evidence_and_date(self):
        doc = {
            "collection_permission": "allowed",
            "permission_evidence": "",
            "terms_checked_on": "2026-10-23",
            "allowed_hosts": ["example.gov"],
            "direct_url": "https://example.gov/law.pdf",
            "permission_scope_review": approved_scope_review(),
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
            "permission_scope_review": approved_scope_review(),
        }
        with self.assertRaisesRegex(ValueError, "cannot be in the future"):
            check_permission(doc)

    def test_permission_scope_review_is_mandatory(self):
        doc = {
            "collection_permission": "allowed",
            "permission_evidence": "Reviewed source terms evidence",
            "terms_checked_on": "2026-10-26",
            "allowed_hosts": ["example.gov"],
            "direct_url": "https://example.gov/law.pdf",
        }
        with self.assertRaisesRegex(ValueError, "permission_scope_review"):
            check_permission(doc)

    def test_permission_scope_requires_each_intended_product_use(self):
        for flag in ("storage", "text_extraction", "indexing", "commercial_product_use", "excerpt_display"):
            scope = approved_scope_review()["scope"]
            scope[flag] = False
            doc = {
                "collection_permission": "allowed",
                "permission_evidence": "Reviewed source terms evidence",
                "terms_checked_on": "2026-10-26",
                "allowed_hosts": ["example.gov"],
                "direct_url": "https://example.gov/law.pdf",
                "permission_scope_review": approved_scope_review(scope=scope),
            }
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, flag):
                check_permission(doc)

    def test_permission_scope_rejects_unreviewed_terms_and_unsupported_access_method(self):
        for overrides, expected in (
            ({"source_terms_reviewed": False}, "source_terms_reviewed"),
            ({"access_method": "website_scraping"}, "access_method"),
            ({"reviewer_id": ""}, "reviewer_id"),
            ({"evidence_reference": ""}, "evidence_reference"),
        ):
            doc = {
                "collection_permission": "allowed",
                "permission_evidence": "Reviewed source terms evidence",
                "terms_checked_on": "2026-10-26",
                "allowed_hosts": ["example.gov"],
                "direct_url": "https://example.gov/law.pdf",
                "permission_scope_review": approved_scope_review(**overrides),
            }
            with self.subTest(expected=expected), self.assertRaisesRegex(ValueError, expected):
                check_permission(doc)

    def test_manifest_host_validation_rejects_credentials_in_direct_url(self):
        doc = {
            "allowed_hosts": ["example.gov"],
            "direct_url": "https://user:secret@example.gov/law.pdf",
        }
        with self.assertRaisesRegex(ValueError, "credentials"):
            collector.validate_manifest_hosts(doc)

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
