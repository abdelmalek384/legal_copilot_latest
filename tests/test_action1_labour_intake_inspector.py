import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.inspect_action1_labour_intake import build_report, inspect_jsonl, inspect_pdf


class Action1IntakeInspectorTests(unittest.TestCase):
    def test_pdf_receipt_records_hash_and_signature_without_extracting_content(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "gazette.pdf"
            payload = b"%PDF-1.7\n% fixture source bytes\n%%EOF\n"
            path.write_bytes(payload)
            report = build_report(path)
            pdf = report["gazette_pdf"]
            self.assertEqual(pdf["size_bytes"], len(payload))
            self.assertEqual(len(pdf["sha256"]), 64)
            self.assertTrue(pdf["pdf_signature_valid"])
            self.assertTrue(pdf["eof_marker_seen_near_file_end"])
            self.assertFalse(report["safety_boundary"]["source_contents_embedded"])
            self.assertFalse(report["safety_boundary"]["retrieval_eligible"])
            self.assertNotIn("fixture source bytes", json.dumps(report))

    def test_jsonl_receipt_counts_records_fields_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "law_rows_ar.jsonl"
            path.write_text(
                '{"id":"A1","article":1,"text":"first"}\n'
                '{"id":"A1","article":2,"text":"second"}\n'
                '{"id":"A3","article":3}\n',
                encoding="utf-8",
            )
            result = inspect_jsonl(path)
            self.assertEqual(result["jsonl_records"], 3)
            self.assertEqual(result["stable_key_field_candidate"], "id")
            self.assertEqual(result["duplicate_stable_key_count"], 1)
            self.assertEqual(result["top_level_field_counts"]["article"], 3)
            self.assertEqual(result["top_level_field_counts"]["text"], 2)
            self.assertNotIn("first", json.dumps(result))

    def test_jsonl_rejects_invalid_json_and_non_object_records(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.jsonl"
            path.write_text('{"id":"ok"}\nnot-json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2 is invalid JSON"):
                inspect_jsonl(path)
            path.write_text('{"id":"ok"}\n[]\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2 must contain a JSON object"):
                inspect_jsonl(path)

    def test_pdf_rejects_non_pdf_and_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bad = root / "bad.pdf"
            bad.write_bytes(b"not a pdf")
            with self.assertRaisesRegex(ValueError, "PDF signature"):
                inspect_pdf(bad)
            target = root / "target.pdf"
            target.write_bytes(b"%PDF-1.4\n%%EOF")
            link = root / "link.pdf"
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symbolic link"):
                inspect_pdf(link)

    def test_report_does_not_claim_legal_or_reuse_verification(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pdf = root / "gazette.pdf"
            pdf.write_bytes(b"%PDF-1.4\n%%EOF")
            rows = root / "law_rows_ar.jsonl"
            rows.write_text('{"id":"x","article":1}\n', encoding="utf-8")
            report = build_report(pdf, rows)
            self.assertFalse(report["safety_boundary"]["legal_authenticity_verified"])
            self.assertFalse(report["safety_boundary"]["currentness_verified"])
            self.assertFalse(report["safety_boundary"]["reuse_permission_confirmed"])
            self.assertFalse(report["safety_boundary"]["retrieval_eligible"])


if __name__ == "__main__":
    unittest.main()
