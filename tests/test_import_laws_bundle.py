"""Regression tests for legal PDF/metadata bundle validation (no PDF parser needed)."""
import hashlib
import json
import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from tools.import_laws import validate_inputs


class LegalImportBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-import-bundle-")
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.output = self.root / "output"
        self.source.mkdir()
        self.pdf_bytes = b"%PDF-1.7\n% test fixture bytes; not a real legal document\n"
        self._write_pair("sample_law", "DOC-001", self.pdf_bytes)

    def tearDown(self):
        self.temp.cleanup()

    def _write_pair(self, stem, document_id, pdf_bytes, **overrides):
        pdf = self.source / f"{stem}.pdf"
        pdf.write_bytes(pdf_bytes)
        metadata = {
            "document_id": document_id,
            "source_url": "https://example.gov.eg/gazette/item?id=123",
            "retrieved_at": "2026-10-30T10:30:00+02:00",
            "content_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
            "review_status": "pending_human_review",
        }
        metadata.update(overrides)
        (self.source / f"{stem}.json").write_text(json.dumps(metadata), encoding="utf-8")
        return pdf

    def test_valid_pair_returns_actual_hash_and_metadata(self):
        prepared = validate_inputs(self.source, self.output)
        self.assertEqual(len(prepared), 1)
        _, metadata, pdf, actual_hash = prepared[0]
        self.assertEqual(metadata["document_id"], "DOC-001")
        self.assertEqual(pdf.name, "sample_law.pdf")
        self.assertEqual(actual_hash, hashlib.sha256(self.pdf_bytes).hexdigest())
        self.assertFalse(self.output.exists())

    def test_extracted_rows_remain_unverified_and_report_full_hash(self):
        from tools import import_laws

        with mock.patch.object(import_laws, "page_texts", return_value=(["Article 1\\nCandidate article text"], False)):
            import_laws.main(self.source, self.output)
        rows = [json.loads(line) for line in (self.output / "law_rows.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["verified"], 0)
        self.assertEqual(rows[0]["in_force"], 0)
        self.assertIsNone(rows[0]["as_of"])
        self.assertIn(hashlib.sha256(self.pdf_bytes).hexdigest(), rows[0]["source"])
        report = (self.output / "import_report.md").read_text(encoding="utf-8")
        self.assertIn("verified PDF SHA-256", report)

    def test_hash_mismatch_is_rejected_before_output_creation(self):
        sidecar = self.source / "sample_law.json"
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        metadata["content_sha256"] = "0" * 64
        sidecar.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "SHA-256 mismatch"):
            validate_inputs(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_http_or_credential_bearing_source_urls_are_rejected(self):
        for source_url in ("http://example.gov.eg/item", "https://user:pass@example.gov.eg/item"):
            with self.subTest(source_url=source_url):
                sidecar = self.source / "sample_law.json"
                metadata = json.loads(sidecar.read_text(encoding="utf-8"))
                metadata["source_url"] = source_url
                sidecar.write_text(json.dumps(metadata), encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "source_url"):
                    validate_inputs(self.source, self.output)
                metadata["source_url"] = "https://example.gov.eg/gazette/item?id=123"
                sidecar.write_text(json.dumps(metadata), encoding="utf-8")

    def test_invalid_retrieval_date_or_hash_shape_is_rejected(self):
        sidecar = self.source / "sample_law.json"
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        metadata["retrieved_at"] = "yesterday"
        sidecar.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "retrieved_at"):
            validate_inputs(self.source, self.output)
        metadata["retrieved_at"] = "2026-10-30"
        metadata["content_sha256"] = "abc123"
        sidecar.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "64-character SHA-256"):
            validate_inputs(self.source, self.output)

    def test_non_pdf_signature_is_rejected(self):
        pdf = self.source / "sample_law.pdf"
        pdf.write_bytes(b"not a PDF file")
        sidecar = self.source / "sample_law.json"
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        metadata["content_sha256"] = hashlib.sha256(pdf.read_bytes()).hexdigest()
        sidecar.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "PDF signature"):
            validate_inputs(self.source, self.output)

    def test_missing_or_unpaired_pdf_sidecar_is_rejected(self):
        (self.source / "sample_law.pdf").unlink()
        with self.assertRaisesRegex(SystemExit, "missing PDFs"):
            validate_inputs(self.source, self.output)
        self._write_pair("orphan", "DOC-002", self.pdf_bytes)
        (self.source / "orphan.json").unlink()
        with self.assertRaisesRegex(SystemExit, "missing sidecars"):
            validate_inputs(self.source, self.output)

    def test_duplicate_document_ids_are_rejected(self):
        self._write_pair("second_law", "DOC-001", self.pdf_bytes)
        with self.assertRaisesRegex(SystemExit, "duplicate document_id"):
            validate_inputs(self.source, self.output)

    def test_non_object_json_and_missing_sidecars_are_rejected(self):
        (self.source / "sample_law.json").write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "JSON object"):
            validate_inputs(self.source, self.output)
        (self.source / "sample_law.json").unlink()
        with self.assertRaisesRegex(SystemExit, "no JSON metadata"):
            validate_inputs(self.source, self.output)

    def test_symlinked_pdf_and_sidecar_are_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks are unavailable")
        pdf = self.source / "sample_law.pdf"
        real_pdf = self.root / "real.pdf"
        real_pdf.write_bytes(pdf.read_bytes())
        pdf.unlink()
        pdf.symlink_to(real_pdf)
        with self.assertRaisesRegex(SystemExit, "symbolic link"):
            validate_inputs(self.source, self.output)
        pdf.unlink()
        pdf.write_bytes(self.pdf_bytes)
        sidecar = self.source / "sample_law.json"
        real_sidecar = self.root / "real.json"
        real_sidecar.write_bytes(sidecar.read_bytes())
        sidecar.unlink()
        sidecar.symlink_to(real_sidecar)
        with self.assertRaisesRegex(SystemExit, "symbolic link"):
            validate_inputs(self.source, self.output)

    def test_source_and_output_paths_must_be_separate_regular_directories(self):
        with self.assertRaisesRegex(SystemExit, "separate"):
            validate_inputs(self.source, self.source / "out")
        source_link = self.root / "source-link"
        source_link.symlink_to(self.source, target_is_directory=True)
        with self.assertRaisesRegex(SystemExit, "regular directory"):
            validate_inputs(source_link, self.output)
        output_link = self.root / "output-link"
        output_link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(SystemExit, "output directory"):
            validate_inputs(self.source, output_link)


if __name__ == "__main__":
    unittest.main()
