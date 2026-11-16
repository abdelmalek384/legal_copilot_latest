import contextlib
import io
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
        "status": "passed",
        "evidence": "TEST-TERMS-REVIEW-001",
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
            for index, raw in enumerate((b"Article 1\nOriginal text version one.", b"Article 1\nOriginal text version two.")):
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

    def test_jsonl_append_refuses_symlink_targets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "outside.jsonl"
            target.write_text("sentinel\\n", encoding="utf-8")
            link = root / "review_queue.jsonl"
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symbolic links"):
                collector.append_jsonl(link, {"private": "should not be written"})
            self.assertEqual(target.read_text(encoding="utf-8"), "sentinel\\n")

    def test_output_layout_rejects_symlinked_roots_directories_and_report_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outside = root / "outside"
            outside.mkdir()
            output = root / "output"
            output.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "output root"):
                collector.validate_output_layout(output)

            output.unlink()
            output.mkdir()
            (output / "metadata").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "metadata output directory"):
                collector.validate_output_layout(output)

            (output / "metadata").unlink()
            (output / "collection_report.jsonl").symlink_to(root / "sentinel.jsonl")
            with self.assertRaisesRegex(ValueError, "collection_report.jsonl"):
                collector.validate_output_layout(output)

    def test_collector_blocks_before_network_when_central_commercial_rights_are_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest_path = root / "manifest.json"
            register_path = root / "register.json"
            out = root / "corpus"
            manifest_path.write_text(json.dumps({"documents": [{
                "document_id": "LAW-1",
                "source_id": "SRC-1",
                "title": "Test law",
                "direct_url": "https://example.gov/law.pdf",
                "allowed_hosts": ["example.gov"],
                "collection_permission": "allowed",
                "permission_evidence": "Collection permission AUTH-1",
                "terms_checked_on": "2026-10-26",
                "permission_scope_review": approved_scope_review(),
            }]}), encoding="utf-8")
            base_source = {
                "source_id": "SRC-1",
                "authority": "Example authority",
                "source_page": "https://example.gov/",
                "material_types": ["law"],
                "access_status": "public",
                "collection_permission": "allowed",
                "permission_evidence": "Collection permission AUTH-1",
                "terms_checked_on": "2026-10-26",
                "required_next_action": "review",
            }
            for commercial in (
                {"commercial_reuse_permission": "unknown"},
                {"commercial_reuse_permission": "allowed"},
                {
                    "commercial_reuse_permission": "allowed",
                    "commercial_reuse_evidence": "Commercial license AUTH-COMM-1",
                    "commercial_terms_checked_on": "2099-01-01",
                },
            ):
                register_path.write_text(json.dumps({
                    "schema_version": "1.0",
                    "assessment_date": "2026-10-26",
                    "sources": [{**base_source, **commercial}],
                }), encoding="utf-8")
                args = [
                    "collect_legal_documents.py",
                    "--manifest", str(manifest_path),
                    "--register", str(register_path),
                    "--out", str(out),
                ]
                errors = io.StringIO()
                with patch.object(sys, "argv", args), patch.object(collector.httpx, "Client") as client, contextlib.redirect_stderr(errors):
                    code = collector.main()
                self.assertEqual(code, 2)
                client.assert_not_called()
                self.assertIn("no network requests were made", errors.getvalue())
                self.assertFalse(out.exists())

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

    def test_metadata_persistence_refuses_duplicate_keys_in_current_pointer(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            meta_dir = out / "metadata"
            meta_dir.mkdir()
            current = meta_dir / "TEST-LAW.json"
            current.write_text('{"document_id":"TEST-LAW","document_id":"OTHER"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unreadable or ambiguous"):
                collector.persist_metadata(out, "TEST-LAW", {"document_id": "TEST-LAW"})
            self.assertEqual(current.read_text(encoding="utf-8"), '{"document_id":"TEST-LAW","document_id":"OTHER"}')

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

    def test_source_url_rejects_empty_userinfo_as_well_as_credentials(self):
        public_answer = (2, 1, 6, "", ("8.8.8.8", 443))
        for url in (
            "https://@example.gov/law.pdf",
            "https://:@example.gov/law.pdf",
        ):
            with self.subTest(url=url), patch("tools.collect_legal_documents.socket.getaddrinfo", return_value=[public_answer]):
                with self.assertRaisesRegex(ValueError, "credentials"):
                    validate_public_https_url(url, {"example.gov"})

    def test_source_url_rejects_whitespace_and_invalid_ports(self):
        for url in (
            " https://example.gov/law.pdf",
            "https://example.gov/law file.pdf",
            "https://example.gov/law\\\\file.pdf",
            "https://example.gov:99999/law.pdf",
            "https://example.gov:0/law.pdf",
        ):
            with self.subTest(url=url), patch("tools.collect_legal_documents.socket.getaddrinfo") as resolver:
                with self.assertRaises(ValueError):
                    validate_public_https_url(url, {"example.gov"})
                resolver.assert_not_called()

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



    def test_source_url_rejects_del_empty_port_fragments_and_signed_queries(self):
        public_answer = (2, 1, 6, "", ("8.8.8.8", 443))
        for url in (
            "https://example.gov:",
            "https://example.gov/law\x7f.pdf",
            "https://example.gov/law.pdf#fragment",
            "https://example.gov/law.pdf?token=secret",
        ):
            with self.subTest(url=url), patch("tools.collect_legal_documents.socket.getaddrinfo", return_value=[public_answer]) as resolver:
                with self.assertRaises(ValueError):
                    validate_public_https_url(url, {"example.gov"})
                resolver.assert_not_called()

    def test_manifest_host_validation_rejects_del_empty_port_and_signed_queries(self):
        for url in (
            "https://example.gov:",
            "https://example.gov/law\x7f.pdf",
            "https://example.gov/law.pdf#fragment",
            "https://example.gov/law\\\\file.pdf",
            "https://example.gov/law.pdf?X-Amz-Signature=secret",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                collector.validate_manifest_hosts({"allowed_hosts": ["example.gov"], "direct_url": url})

    def test_existing_metadata_loader_rejects_duplicate_keys_at_every_depth(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "law-1.json"
            for raw in (
                '{"document_id":"law-1","document_id":"law-2"}',
                '{"document_id":"law-1","permission":{"status":"unknown","status":"allowed"}}',
            ):
                path.write_text(raw, encoding="utf-8")
                with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "unreadable, ambiguous, or unsafe"):
                    collector.load_existing_metadata(path)

    def test_existing_metadata_loader_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target.json"
            target.write_text('{"document_id":"law-1"}', encoding="utf-8")
            link = root / "linked.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {type(exc).__name__}")
            with self.assertRaisesRegex(ValueError, "unreadable, ambiguous, or unsafe"):
                collector.load_existing_metadata(link)

    def test_manifest_rejects_duplicate_json_keys_at_every_object_depth(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            for raw in (
                '{"documents": [], "documents": [{"document_id": "law-1", "source_id": "s1"}]}',
                '{"documents": [{"document_id": "law-1", "source_id": "s1", "source_id": "s2"}]}',
            ):
                with self.subTest(raw=raw):
                    path.write_text(raw, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate JSON key in collection manifest"):
                        load_manifest(path)

    def test_manifest_rejects_non_object_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON object"):
                load_manifest(path)

    def test_preserved_original_hash_rejects_symlink_swap_between_check_and_open(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "originals" / "DOC-1" / "original.pdf"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"approved original")
            outside = root / "outside.pdf"
            outside.write_bytes(b"replacement")
            real_open = collector.os.open
            swapped = False

            def replace_before_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if Path(path) == target and not swapped:
                    swapped = True
                    target.unlink()
                    target.symlink_to(outside)
                return real_open(path, flags, *args, **kwargs)

            with patch.object(collector.os, "open", side_effect=replace_before_open):
                with self.assertRaises(OSError):
                    collector.sha256_file(target)
            self.assertTrue(swapped)

    def test_preserved_original_hash_rejects_fifo_without_blocking(self):
        import os
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO files are unavailable on this platform")
        with tempfile.TemporaryDirectory() as temp:
            fifo = Path(temp) / "original.fifo"
            os.mkfifo(fifo)
            with self.assertRaises(OSError):
                collector.sha256_file(fifo)

    def test_manifest_reader_rejects_symlink_swap_between_check_and_open(self):
        target = self.root / "manifest-race.json"
        target.write_text(json.dumps({"documents": []}), encoding="utf-8")
        outside = self.root / "outside-manifest.json"
        outside.write_text(json.dumps({"documents": []}), encoding="utf-8")
        real_open = collector.os.open
        swapped = False

        def replace_before_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if Path(path) == target and not swapped:
                swapped = True
                target.unlink()
                target.symlink_to(outside)
            return real_open(path, flags, *args, **kwargs)

        with patch.object(collector.os, "open", side_effect=replace_before_open):
            with self.assertRaises((OSError, ValueError)):
                collector.load_manifest(target)
        self.assertTrue(swapped)

    def test_manifest_reader_rejects_fifo_and_oversized_inputs(self):
        import os
        if hasattr(os, "mkfifo"):
            fifo = self.root / "manifest.fifo"
            os.mkfifo(fifo)
            with self.assertRaises((OSError, ValueError)):
                collector.load_manifest(fifo)
        oversized = self.root / "oversized-manifest.json"
        oversized.write_bytes(b" " * (5 * 1024 * 1024 + 1))
        with self.assertRaises(ValueError):
            collector.load_manifest(oversized)


    def test_extract_text_reads_plain_text_from_stable_original_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            original = Path(td) / "original.txt"
            original.write_text("Article 1\nOriginal body", encoding="utf-8")
            text, error = collector.extract_text(original, "text/plain")
            self.assertIsNone(error)
            self.assertEqual(text, "Article 1\nOriginal body")

    def test_extract_text_rejects_original_symlink_swap_before_open(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = root / "original.txt"
            original.write_text("Article 1\nOriginal body", encoding="utf-8")
            outside = root / "outside.txt"
            outside.write_text("Article 9\nReplacement", encoding="utf-8")
            real_open = collector.os.open
            swapped = False

            def replace_before_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if Path(path) == original and not swapped:
                    swapped = True
                    original.unlink()
                    original.symlink_to(outside)
                return real_open(path, flags, *args, **kwargs)

            with patch.object(collector.os, "open", side_effect=replace_before_open):
                text, error = collector.extract_text(original, "text/plain")
            self.assertTrue(swapped)
            self.assertEqual(text, "")
            self.assertIn("could not be read safely", error)

if __name__ == "__main__":
    unittest.main()
