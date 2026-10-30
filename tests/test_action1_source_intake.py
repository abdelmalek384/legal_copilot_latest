"""Tests for metadata-only Action 1 source intake hashing."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.hash_action1_sources import build_manifest, inspect_file


class Action1SourceIntakeTests(unittest.TestCase):
    def test_pdf_hash_and_signature_are_recorded_without_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gazette.pdf"
            payload = b"%PDF-1.7\nexample-pdf-bytes"
            path.write_bytes(payload)
            result = inspect_file(path)
            self.assertEqual(result["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(result["size_bytes"], len(payload))
            self.assertTrue(result["pdf_signature_valid"])
            self.assertFalse(result["content_extracted"])

    def test_jsonl_counts_valid_malformed_and_blank_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "law_rows_ar.jsonl"
            path.write_text('{"id":1}\nnot-json\n\n{"id":2}\n', encoding="utf-8")
            result = inspect_file(path)
            self.assertEqual(result["nonblank_records"], 3)
            self.assertEqual(result["valid_json_records"], 2)
            self.assertEqual(result["malformed_json_records"], 1)
            self.assertEqual(result["blank_lines"], 1)
            self.assertFalse(result["content_extracted"])

    def test_manifest_contains_metadata_only_and_no_source_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "gazette.pdf"
            data = root / "law_rows_ar.jsonl"
            pdf.write_bytes(b"%PDF-1.4\nprivate bytes")
            data.write_text('{"article":1}\n', encoding="utf-8")
            manifest = build_manifest([pdf, data])
            self.assertFalse(manifest["source_bytes_copied"])
            self.assertFalse(manifest["source_contents_extracted"])
            self.assertEqual(len(manifest["records"]), 2)
            serialized = json.dumps(manifest)
            self.assertNotIn("private bytes", serialized)
            self.assertNotIn('{"article":1}', serialized)

    def test_symbolic_link_inputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "original.pdf"
            target.write_bytes(b"%PDF-1.4\\n%%EOF")
            link = root / "linked.pdf"
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symbolic link"):
                inspect_file(link)

    def test_empty_inputs_and_duplicate_basenames_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "a" / "same.jsonl"
            second = root / "b" / "same.jsonl"
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_text('{"x":1}\n', encoding="utf-8")
            second.write_text('{"x":2}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                build_manifest([])
            with self.assertRaises(ValueError):
                build_manifest([first, second])


if __name__ == "__main__":
    unittest.main()
