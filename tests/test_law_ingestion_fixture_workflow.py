import contextlib
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.record_manual_capture import main as capture_main  # noqa: E402
from tools.audit_article_rows import main as audit_main  # noqa: E402
from tools.compare_corpus_to_reference import main as compare_main  # noqa: E402
from tools.answer_trust_tier import TIER_UNREVIEWED, classify_answer_trust_tier  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "law_ingestion"


class LawIngestionFixtureWorkflowTests(unittest.TestCase):
    def test_capture_audit_compare_and_fail_closed_tier(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            capture_out = root / "capture"
            capture_stdout = io.StringIO()
            with contextlib.redirect_stdout(capture_stdout):
                code = capture_main([
                    "--file", str(FIXTURE / "fictional_reference.txt"),
                    "--document-id", "EG-INGESTION-FIXTURE",
                    "--source-id", "EG-AMIRI-PRESS",
                    "--source-url", "https://www.alamiria.com/fixture-only-not-a-source",
                    "--captured-by", "Local fixture dry-run",
                    "--capture-method", "manual_transcription",
                    "--retrieved-on", "2026-10-20",
                    "--notes", "Synthetic fixture only; placeholder URL; do not persist.",
                    "--out", str(capture_out),
                    "--dry-run",
                ])
            self.assertEqual(code, 0)
            capture = json.loads(capture_stdout.getvalue())
            self.assertTrue(capture["dry_run"])
            self.assertFalse(capture["metadata"]["legal_authenticity_verified"])
            self.assertFalse(capture["metadata"]["current_legal_status_verified"])
            self.assertFalse(capture["metadata"]["commercial_reuse_permission_verified"])
            self.assertIsNone(capture["metadata"]["effective_date"])
            self.assertFalse(capture_out.exists())

            audit_out = root / "audit"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit_main([
                    "--input", str(FIXTURE / "fictional_candidate.jsonl"),
                    "--out-dir", str(audit_out),
                ]), 0)
            with (audit_out / "quantity_checklist.csv").open(encoding="utf-8") as handle:
                quantities = list(csv.DictReader(handle))
            self.assertTrue(any("ثلاثين يوما" in row["numbers_periods_amounts_found"] for row in quantities))

            compare_out = root / "comparison"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(compare_main([
                    "--candidate", str(FIXTURE / "fictional_candidate.jsonl"),
                    "--reference", str(FIXTURE / "fictional_reference.txt"),
                    "--out-dir", str(compare_out),
                ]), 0)
            report = json.loads((compare_out / "comparison_report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["evidence_only"])
            self.assertTrue(report["all_identical"])
            self.assertEqual(report["summary"], {"identical_after_normalization": 2})

            reference = (FIXTURE / "fictional_reference.txt").read_text(encoding="utf-8")
            self.assertIn("1 سبتمبر 2025", reference)
            self.assertIn("1 أكتوبر 2025", reference)

            tier = classify_answer_trust_tier(
                [{"source_id": "FIXTURE", "source_status": "source_matched_unreviewed"}],
                claims_supported=True,
                citations_complete=True,
                contradictory_sources=False,
            )
            self.assertEqual(tier["trust_tier"], TIER_UNREVIEWED)
            self.assertEqual(tier["reason_codes"], ["source_matched_policy_not_approved"])


if __name__ == "__main__":
    unittest.main()
