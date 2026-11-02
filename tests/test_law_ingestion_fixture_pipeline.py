"""Fixture-only integration checks for the future law-ingestion workflow.

The source and article text used here are fictional and do not represent Egyptian law.
"""
import hashlib
import json
import re
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.audit_article_rows import main as audit_article_rows_main
from tools.compare_corpus_to_reference import build_report
from tools.record_manual_capture import record_capture
from tools.validate_manual_capture_record import validate_capture_record


FIXTURES = ROOT / "tests" / "fixtures" / "law_ingestion"


def _fixture_commencement_dates(text):
    """Parse only the two explicit month forms used in this fictional fixture."""
    months = {"سبتمبر": 9, "أكتوبر": 10}
    pattern = re.compile(r"اعتبارا من\s+(\d{1,2})\s+(سبتمبر|أكتوبر)\s+(\d{4})")
    return [
        date(int(year), months[month], int(day)).isoformat()
        for day, month, year in pattern.findall(text)
    ]


class LawIngestionFixturePipelineTests(unittest.TestCase):
    def test_manual_capture_integrity_and_article_comparison_fixture(self):
        reference = FIXTURES / "fictional_reference.txt"
        candidate = FIXTURES / "fictional_candidate.jsonl"
        raw = reference.read_bytes()

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = root / "original.txt"
            original.write_bytes(raw)
            record_path = root / "capture.json"
            record = {
                "document_id": "SYNTHETIC-LAW-ONLY",
                "official_title": "Fictional test text — not Egyptian law",
                "source_authority": "Synthetic fixture",
                "source_url": "https://example.test/fictional-source",
                "retrieved_at": "2026-11-01T00:00:00Z",
                "acquisition_method": "manual",
                "original_file": "original.txt",
                "original_sha256": hashlib.sha256(raw).hexdigest(),
                "collection_permission": "unknown",
                "commercial_reuse_permission": "unknown",
                "legal_status": "unknown",
                "review_status": "pending_source_review",
            }
            record_path.write_text(json.dumps(record), encoding="utf-8")
            provenance = validate_capture_record(record, record_path)
            self.assertTrue(provenance["valid"])
            self.assertTrue(provenance["provenance_valid"])
            self.assertFalse(provenance["retrieval_eligible"])

        comparison = build_report(candidate, reference)
        self.assertTrue(comparison["evidence_only"])
        self.assertTrue(comparison["all_identical"])
        self.assertEqual(comparison["candidate"]["rows_compared"], 2)
        self.assertEqual(comparison["reference"]["articles_detected"], 2)
        self.assertNotIn("numeric_difference", comparison["summary"])


    def test_full_fixture_workflow_manual_capture_audit_compare_and_commencement(self):
        reference = FIXTURES / "fictional_reference.txt"
        candidate = FIXTURES / "fictional_candidate.jsonl"

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            supplied = root / "fictional-gazette.txt"
            supplied.write_bytes(reference.read_bytes())
            corpus = root / "captured-corpus"

            capture = record_capture(SimpleNamespace(
                file=str(supplied),
                document_id="EG-LABOUR-14-2025",
                source_url="https://www.alamiria.com/law/14",
                captured_by="Fixture test operator",
                capture_method="manual_transcription",
                retrieved_on=date.today().isoformat(),
                publication_date=None,
                effective_date=None,
                gazette_issue="fictional fixture only",
                source_id=None,
                notes="SYNTHETIC FIXTURE ONLY — not Gazette text or legal evidence",
                out=str(corpus),
                max_mb=100,
                dry_run=False,
            ))
            self.assertFalse(capture["dry_run"])
            self.assertIsNone(capture["extraction_error"])
            metadata = json.loads(
                (corpus / "metadata" / "EG-LABOUR-14-2025.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["sha256"], hashlib.sha256(supplied.read_bytes()).hexdigest())
            self.assertEqual(metadata["review_status"], "pending_human_review")
            self.assertEqual(metadata["collection_permission"], "not_established_manual_capture")
            self.assertFalse(metadata["legal_authenticity_verified"])
            self.assertFalse(metadata["current_legal_status_verified"])
            self.assertFalse(metadata["commercial_reuse_permission_verified"])

            audit_input = root / "candidate_rows.jsonl"
            audit_rows = [
                {
                    "law": "Synthetic fixture only",
                    "article": "1",
                    "text": "مدة النص التجريبي خمس سنوات، ويبلغ المقابل 500 جنيه.",
                },
                {
                    "law": "Synthetic fixture only",
                    "article": "13",
                    "text": "يبدأ تطبيق النص التجريبي اعتبارا من 1 سبتمبر 2025. "
                            "وتبدأ الجهة التجريبية عملها اعتبارا من 1 أكتوبر 2025.",
                },
            ]
            audit_input.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in audit_rows),
                encoding="utf-8",
            )
            audit_dir = root / "article-audit"
            self.assertEqual(
                audit_article_rows_main(["--input", str(audit_input), "--out-dir", str(audit_dir)]),
                0,
            )
            audit_report = json.loads((audit_dir / "audit.json").read_text(encoding="utf-8"))
            self.assertEqual(audit_report["rows"], 2)
            self.assertEqual(audit_report["numbering"]["Synthetic fixture only"]["gaps"], list(range(2, 13)))
            checklist = (audit_dir / "quantity_checklist.csv").read_text(encoding="utf-8-sig")
            self.assertIn("خمس سنوات", checklist)
            self.assertIn("500 جنيه", checklist)

            comparison = build_report(candidate, reference)
            self.assertTrue(comparison["evidence_only"])
            self.assertTrue(comparison["all_identical"])
            self.assertEqual(comparison["candidate"]["rows_compared"], 2)
            self.assertEqual(comparison["reference"]["articles_detected"], 2)

            text = reference.read_text(encoding="utf-8")
            self.assertEqual(
                _fixture_commencement_dates(text),
                ["2025-09-01", "2025-10-01"],
            )

    def test_commencement_dates_are_read_from_fixture_text_not_capture_metadata(self):
        text = (FIXTURES / "fictional_reference.txt").read_text(encoding="utf-8")
        self.assertEqual(
            _fixture_commencement_dates(text),
            ["2025-09-01", "2025-10-01"],
        )

    def test_numeric_mismatch_is_visible_and_blocks_identical_result(self):
        reference = FIXTURES / "fictional_reference.txt"
        with tempfile.TemporaryDirectory() as td:
            candidate = Path(td) / "candidate.jsonl"
            rows = [
                {"article": "1", "text": "يحدد النص التجريبي نطاق العمل والالتزامات العامة."},
                {"article": "13", "text": "يبدأ تطبيق النص التجريبي اعتبارا من 2 سبتمبر 2025.\nوتبدأ الجهة التجريبية عملها اعتبارا من 1 أكتوبر 2025."},
            ]
            candidate.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8",
            )
            report = build_report(candidate, reference)
            self.assertFalse(report["all_identical"])
            self.assertGreater(report["summary"].get("numeric_difference", 0), 0)


if __name__ == "__main__":
    unittest.main()
