"""End-to-end tests for the offline lawyer-supplied Gazette text importer."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.import_gazette_text import import_text


class GazetteTextImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.text_path = self.root / "gazette.txt"
        self.meta_path = self.root / "gazette.json"
        self.output = self.root / "output"
        self.text = (
            "المادة 1\nيصدر القانون المرافق بالنص الآتي.\n"
            "المادة 13\nيعمل بهذا القانون في التاريخ المحدد.\n"
            "المادة 1\nتسري أحكام القانون المرافق على المنشآت.\n"
            "المادة 2\nتكون السنة 365 يوما.\n"
        )
        self.text_path.write_text(self.text, encoding="utf-8")
        self.metadata = {
            "document_id": "EG-LABOUR-14-2025",
            "official_title": "قانون العمل رقم 14 لسنة 2025",
            "language": "ar",
            "gazette_issue": "الجريدة الرسمية العدد 18 (تابع)",
            "publication_date": "2025-05-03",
            "retrieved_at": "2026-11-06T00:00:00+02:00",
            "captured_by": "Qualified reviewer supplied text (test fixture)",
            "supplier_role": "egyptian_lawyer",
            "capture_method": "lawyer_supplied_text",
            "source_reference": "Test fixture; not a legal source",
            "content_sha256": hashlib.sha256(self.text.encode("utf-8")).hexdigest(),
            "collection_permission": "unknown",
        }
        self.write_metadata()

    def write_metadata(self):
        self.meta_path.write_text(json.dumps(self.metadata, ensure_ascii=False), encoding="utf-8")

    def test_imports_articles_across_numbering_reset_and_keeps_all_rows_unverified(self):
        result = import_text(self.text_path, self.meta_path, self.output)
        rows = [json.loads(line) for line in (self.output / "law_rows.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(result["article_headings"], 4)
        self.assertEqual([row["article"] for row in rows], ["1", "13", "1", "2"])
        self.assertEqual(rows[0]["law"], rows[1]["law"])
        self.assertIn("[block 2]", rows[2]["law"])
        self.assertTrue(all(row["verified"] == 0 for row in rows))
        self.assertTrue(all(row["in_force"] == 0 for row in rows))
        self.assertTrue(all(row["as_of"] is None for row in rows))
        self.assertTrue((self.output / "import_report.md").is_file())

    def test_non_lawyer_supplier_role_is_rejected(self):
        self.metadata["supplier_role"] = "unknown"
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, "supplier_role"):
            import_text(self.text_path, self.meta_path, self.output)
        self.assertFalse(self.output.exists())

    def test_hash_mismatch_is_rejected_before_output(self):
        self.metadata["content_sha256"] = "0" * 64
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            import_text(self.text_path, self.meta_path, self.output)
        self.assertFalse(self.output.exists())

    def test_source_url_credentials_and_signed_query_are_rejected(self):
        self.metadata["source_url"] = "https://user:pass@example.gov/item"
        self.metadata.pop("source_reference")
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, "source_url"):
            import_text(self.text_path, self.meta_path, self.output)

    def test_not_allowed_collection_permission_is_rejected(self):
        self.metadata["collection_permission"] = "not_allowed"
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, "not_allowed"):
            import_text(self.text_path, self.meta_path, self.output)
        self.assertFalse(self.output.exists())

    def test_output_inside_source_directory_is_rejected(self):
        nested = self.root / "nested-output"
        with self.assertRaisesRegex(ValueError, "outside the source directory"):
            import_text(self.text_path, self.meta_path, nested)
        self.assertFalse(nested.exists())

    def test_missing_article_headings_are_rejected(self):
        self.text_path.write_text("هذا نص بلا عناوين مواد.", encoding="utf-8")
        self.metadata["content_sha256"] = hashlib.sha256(self.text_path.read_bytes()).hexdigest()
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, "no recognized"):
            import_text(self.text_path, self.meta_path, self.output)

    def test_invalid_utf8_is_rejected(self):
        self.text_path.write_bytes(b"\xff\xfe\x00")
        self.metadata["content_sha256"] = hashlib.sha256(self.text_path.read_bytes()).hexdigest()
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            import_text(self.text_path, self.meta_path, self.output)

    def test_symlinked_text_is_rejected(self):
        link = self.root / "linked.txt"
        link.symlink_to(self.text_path)
        with self.assertRaisesRegex(ValueError, "symlink"):
            import_text(link, self.meta_path, self.output)

    def test_existing_output_is_not_overwritten(self):
        self.output.mkdir()
        (self.output / "law_rows.jsonl").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "already exist"):
            import_text(self.text_path, self.meta_path, self.output)
        self.assertEqual((self.output / "law_rows.jsonl").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
