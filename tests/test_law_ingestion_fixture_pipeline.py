"""Fixture-only integration checks for the future law-ingestion workflow.

The source and article text used here are fictional and do not represent Egyptian law.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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

            capture_cli = subprocess.run(
                [
                    sys.executable, str(ROOT / "tools" / "record_manual_capture.py"),
                    "--file", str(supplied),
                    "--document-id", "SYNTHETIC-LAW-ONLY",
                    "--source-id", "EG-AMIRI-PRESS",
                    "--source-url", "https://www.alamiria.com/fixture-only",
                    "--captured-by", "Fixture test operator",
                    "--capture-method", "manual_transcription",
                    "--retrieved-on", date.today().isoformat(),
                    "--gazette-issue", "fictional fixture only",
                    "--notes", "SYNTHETIC FIXTURE ONLY — not Egyptian law or legal evidence",
                    "--out", str(corpus),
                    "--dry-run",
                ],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(capture_cli.returncode, 0, capture_cli.stderr)
            capture_cli_result = json.loads(capture_cli.stdout)
            self.assertTrue(capture_cli_result["dry_run"])
            self.assertEqual(capture_cli_result["metadata"]["document_id"], "SYNTHETIC-LAW-ONLY")
            self.assertFalse(capture_cli_result["metadata"]["legal_authenticity_verified"])

            capture = record_capture(SimpleNamespace(
                file=str(supplied),
                document_id="SYNTHETIC-LAW-ONLY",
                source_url="https://www.alamiria.com/fixture-only",
                captured_by="Fixture test operator",
                capture_method="manual_transcription",
                retrieved_on=date.today().isoformat(),
                publication_date=None,
                effective_date=None,
                gazette_issue="fictional fixture only",
                source_id="EG-AMIRI-PRESS",
                notes="SYNTHETIC FIXTURE ONLY — not Gazette text or legal evidence",
                out=str(corpus),
                max_mb=100,
                dry_run=False,
            ))
            self.assertFalse(capture["dry_run"])
            self.assertIsNone(capture["extraction_error"])
            metadata = json.loads(
                (corpus / "metadata" / "SYNTHETIC-LAW-ONLY.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["sha256"], hashlib.sha256(supplied.read_bytes()).hexdigest())
            self.assertEqual(metadata["review_status"], "pending_human_review")
            self.assertEqual(metadata["collection_permission"], "not_established_manual_capture")
            self.assertFalse(metadata["legal_authenticity_verified"])
            self.assertFalse(metadata["current_legal_status_verified"])
            self.assertFalse(metadata["commercial_reuse_permission_verified"])

            audit_dir = root / "article-audit"
            audit_process = subprocess.run(
                [
                    sys.executable, str(ROOT / "tools" / "audit_article_rows.py"),
                    "--input", str(candidate), "--out-dir", str(audit_dir),
                ],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(audit_process.returncode, 0, audit_process.stderr)
            audit_report = json.loads((audit_dir / "audit.json").read_text(encoding="utf-8"))
            self.assertEqual(audit_report["rows"], 2)
            self.assertEqual(audit_report["numbering"]["نص تجريبي خيالي"]["gaps"], list(range(2, 13)))
            checklist = (audit_dir / "quantity_checklist.csv").read_text(encoding="utf-8-sig")
            self.assertIn("خمس سنوات", checklist)
            self.assertIn("500 جنيه", checklist)

            comparison_dir = root / "comparison"
            comparison_process = subprocess.run(
                [
                    sys.executable, str(ROOT / "tools" / "compare_corpus_to_reference.py"),
                    "--candidate", str(candidate),
                    "--reference", str(reference),
                    "--out-dir", str(comparison_dir),
                ],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(comparison_process.returncode, 0, comparison_process.stderr)
            comparison = json.loads(
                (comparison_dir / "comparison_report.json").read_text(encoding="utf-8")
            )
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
