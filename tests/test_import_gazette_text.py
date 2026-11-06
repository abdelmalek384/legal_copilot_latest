"""End-to-end tests for the offline lawyer-supplied Gazette text importer."""
import hashlib
import json
from pathlib import Path
import sys
import subprocess
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
        self.assertTrue(all(row["supplier_role"] == "egyptian_lawyer" for row in rows))
        self.assertTrue(all(row["capture_method"] == "lawyer_supplied_text" for row in rows))
        self.assertTrue(all(row["retrieved_at"] == self.metadata["retrieved_at"] for row in rows))
        self.assertTrue(all(row["source_reference"] == self.metadata["source_reference"] for row in rows))
        self.assertTrue(all("document_id EG-LABOUR-14-2025" in row["source"] for row in rows))
        self.assertTrue(all("source_reference Test fixture; not a legal source" in row["source"] for row in rows))
        self.assertTrue(all("source_url not_supplied" in row["source"] for row in rows))
        self.assertTrue(all("supplier_role egyptian_lawyer" in row["source"] for row in rows))
        self.assertTrue(all("capture_method lawyer_supplied_text" in row["source"] for row in rows))
        self.assertTrue(all("collection_permission unknown" in row["source"] for row in rows))
        self.assertTrue((self.output / "import_report.md").is_file())
        report = (self.output / "import_report.md").read_text(encoding="utf-8")
        self.assertIn("Block 1 missing: 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12", report)
        self.assertIn("Blocks with duplicate article numbers: 0", report)

    def test_imports_ordinal_promulgation_and_attached_law_separately(self):
        ordinals = [
            "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة",
            "السادسة", "السابعة", "الثامنة", "التاسعة", "العاشرة",
            "الحادية عشرة", "الثانية عشرة", "الثالثة عشرة",
        ]
        parts = ["عنوان القانون"]
        for number, ordinal in enumerate(ordinals, 1):
            parts.extend([f"(المادة {ordinal})", f"نص إصدار {number}."])
        for number in range(1, 299):
            parts.extend([
                f"مادة ({number})",
                f"نص المادة {number} من القانون المرافق.",
            ])
        source_text = "\n".join(parts)
        self.text_path.write_text(source_text, encoding="utf-8")
        self.metadata["content_sha256"] = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        self.write_metadata()

        result = import_text(self.text_path, self.meta_path, self.output)
        rows = [
            json.loads(line)
            for line in (self.output / "law_rows.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(result["article_headings"], 311)
        self.assertEqual(result["promulgation_provisions"], 13)
        self.assertEqual(result["attached_law_articles"], 298)
        self.assertEqual(result["candidate_chunks"], 311)
        self.assertEqual(len(rows), 311)
        self.assertGreater(result["unparsed_preamble_characters"], 0)
        self.assertEqual(
            [row["article"] for row in rows],
            [f"issuance_{n}" for n in range(1, 14)] + [str(n) for n in range(1, 299)],
        )
        self.assertEqual(
            [row["provision_type"] for row in rows],
            ["promulgation"] * 13 + ["attached_law"] * 298,
        )
        self.assertIn("[promulgation]", rows[0]["law"])
        self.assertIn("[attached law]", rows[13]["law"])
        self.assertNotEqual(rows[0]["law"], rows[13]["law"])
        self.assertTrue(all(row["verified"] == 0 for row in rows))
        self.assertTrue(all(row["in_force"] == 0 for row in rows))
        self.assertTrue(all(row["as_of"] is None for row in rows))
        report = (self.output / "import_report.md").read_text(encoding="utf-8")
        self.assertIn("Promulgation provisions recognized: 13", report)
        self.assertIn("Attached-law article headings recognized: 298", report)
        self.assertIn("Unparsed preamble excluded from candidate rows", report)
        self.assertNotIn('"article": "preamble"', (self.output / "law_rows.jsonl").read_text(encoding="utf-8"))

    def test_numeric_only_import_does_not_index_unparsed_preamble(self):
        source_text = "Official Gazette issue title\nالمادة 1\nنص المادة الأولى.\n"
        self.text_path.write_text(source_text, encoding="utf-8")
        self.metadata["content_sha256"] = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        self.write_metadata()
        result = import_text(self.text_path, self.meta_path, self.output)
        rows = [
            json.loads(line)
            for line in (self.output / "law_rows.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual([row["article"] for row in rows], ["1"])
        self.assertGreater(result["unparsed_preamble_characters"], 0)
        self.assertEqual(result["attached_law_articles"], 1)
        self.assertEqual(result["promulgation_provisions"], 0)

    def test_command_line_import_completes_one_sitting_run(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "import_gazette_text.py"),
                str(self.text_path),
                str(self.meta_path),
                str(self.output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["document_id"], "EG-LABOUR-14-2025")
        self.assertEqual(result["article_headings"], 4)
        self.assertGreater(result["candidate_chunks"], 0)
        self.assertTrue((self.output / "law_rows.jsonl").is_file())
        self.assertTrue((self.output / "import_report.md").is_file())
        rows = [json.loads(line) for line in (self.output / "law_rows.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all(row["verified"] == 0 and row["in_force"] == 0 and row["as_of"] is None for row in rows))

    def test_candidate_rows_match_separate_importlaws_staging_contract(self):
        result = import_text(self.text_path, self.meta_path, self.output)
        rows = [json.loads(line) for line in (self.output / "law_rows.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertGreater(result["candidate_chunks"], 0)
        for row in rows:
            # manage.py importlaws consumes these required fields into the
            # quarantined legal_import_staging table; extra provenance fields are retained.
            for key in ("law", "article", "text", "source"):
                self.assertIn(key, row)
                self.assertIsInstance(row[key], str)
                self.assertTrue(row[key].strip())
            self.assertEqual(row["verified"], 0)
            self.assertEqual(row["in_force"], 0)
            self.assertIsNone(row["as_of"])
            self.assertIn("content_sha256", row)
            self.assertIn("permission_evidence_reference", row)

    def test_allowed_permission_evidence_is_retained_in_staged_source(self):
        self.metadata["collection_permission"] = "allowed"
        self.metadata["permission_evidence_reference"] = "lawyer-provided written permission record #TEST-1"
        self.write_metadata()
        import_text(self.text_path, self.meta_path, self.output)
        rows = [json.loads(line) for line in (self.output / "law_rows.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all(row["collection_permission"] == "allowed" for row in rows))
        self.assertTrue(all("permission_evidence_reference lawyer-provided written permission record #TEST-1" in row["source"] for row in rows))

    def test_inline_article_body_after_heading_separator_is_preserved(self):
        inline_text = "المادة 1: يبدأ النص في السطر نفسه.\nالمادة 2 - ويبدأ النص الثاني هنا."
        self.text_path.write_text(inline_text, encoding="utf-8")
        self.metadata["content_sha256"] = hashlib.sha256(inline_text.encode("utf-8")).hexdigest()
        self.write_metadata()
        import_text(self.text_path, self.meta_path, self.output)
        rows = [json.loads(line) for line in (self.output / "law_rows.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([row["article"] for row in rows], ["1", "2"])
        self.assertIn("يبدأ النص في السطر نفسه", rows[0]["text"])
        self.assertIn("ويبدأ النص الثاني هنا", rows[1]["text"])

    def test_duplicate_article_number_is_reported_without_auto_repair(self):
        duplicate_text = "المادة 1\nنص أول.\nالمادة 2\nنص ثان.\nالمادة 2\nنص مكرر."
        self.text_path.write_text(duplicate_text, encoding="utf-8")
        self.metadata["content_sha256"] = hashlib.sha256(duplicate_text.encode("utf-8")).hexdigest()
        self.write_metadata()
        import_text(self.text_path, self.meta_path, self.output)
        report = (self.output / "import_report.md").read_text(encoding="utf-8")
        self.assertIn("Block 1 duplicates: 2", report)

    def test_malformed_metadata_types_fail_with_clear_validation_errors(self):
        for field, value, message in (
            ("language", [], "language must be ar"),
            ("supplier_role", [], "supplier_role must identify"),
            ("capture_method", [], "capture_method must be"),
            ("collection_permission", [], "collection_permission must be"),
        ):
            with self.subTest(field=field):
                self.metadata[field] = value
                self.write_metadata()
                with self.assertRaisesRegex(ValueError, message):
                    import_text(self.text_path, self.meta_path, self.output)
                self.assertFalse(self.output.exists())
                self.metadata[field] = {
                    "language": "ar",
                    "supplier_role": "egyptian_lawyer",
                    "capture_method": "lawyer_supplied_text",
                    "collection_permission": "unknown",
                }[field]
                self.write_metadata()

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

    def test_allowed_collection_permission_requires_evidence_reference(self):
        self.metadata["collection_permission"] = "allowed"
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, "permission_evidence_reference is required"):
            import_text(self.text_path, self.meta_path, self.output)
        self.assertFalse(self.output.exists())

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
