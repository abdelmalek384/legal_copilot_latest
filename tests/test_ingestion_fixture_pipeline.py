"""Disposable end-to-end fixture for the manual legal-ingestion evidence path.

All fixture text and metadata are fictional. The test writes only inside a temporary
directory and never imports anything into an application database.
"""
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tools.record_manual_capture import main as record_capture_main
from tools.audit_article_rows import audit, load_rows, quantity_checklist
from tools.compare_corpus_to_reference import build_report
from tools.answer_trust_tier import classify_answer_trust_tier


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "legal_ingestion"
GAZETTE = FIXTURE / "fictional_gazette.txt"
CANDIDATE = FIXTURE / "fictional_law_rows.jsonl"


class FixtureIngestionPipelineTests(unittest.TestCase):
    def test_capture_audit_comparison_dates_and_source_matched_tier(self):
        with tempfile.TemporaryDirectory(prefix="legal-copilot-ingestion-") as tmp:
            root = Path(tmp)
            capture_out = root / "capture"
            stdout = io.StringIO()
            args = [
                "--file", str(GAZETTE),
                "--document-id", "EG-TEST-FICTIONAL-001",
                "--source-id", "EG-AMIRI-PRESS",
                "--source-url", "https://www.alamiria.com/fictional-fixture",
                "--captured-by", "Automated fixture test",
                "--capture-method", "manual_transcription",
                "--retrieved-on", date.today().isoformat(),
                "--publication-date", "2025-05-03",
                "--effective-date", "2025-09-01",
                "--gazette-issue", "FICTIONAL-TEST-ISSUE",
                "--notes", "Fixture only; Article 3 separately states 2025-10-01.",
                "--out", str(capture_out),
            ]
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(record_capture_main(args), 0)
            captured = json.loads(stdout.getvalue())
            metadata = json.loads(
                (capture_out / "metadata" / "EG-TEST-FICTIONAL-001.json").read_text(encoding="utf-8")
            )
            extracted = capture_out / metadata["original_path"]
            self.assertTrue(extracted.is_file())
            audit_record_path = next((capture_out / "audits" / "EG-TEST-FICTIONAL-001").glob("*.json"))
            audit_record = json.loads(audit_record_path.read_text(encoding="utf-8"))
            extracted_text_path = capture_out / audit_record["extracted_text_path"]
            extracted_text = extracted_text_path.read_text(encoding="utf-8")
            self.assertIn("2025-09-01", extracted_text)
            self.assertIn("2025-10-01", extracted_text)
            self.assertEqual(metadata["publication_date"], "2025-05-03")
            self.assertEqual(metadata["effective_date"], "2025-09-01")
            self.assertFalse(metadata["legal_authenticity_verified"])
            self.assertFalse(metadata["current_legal_status_verified"])
            self.assertFalse(metadata["commercial_reuse_permission_verified"])
            self.assertEqual(metadata["review_status"], "pending_human_review")

            rows, malformed = load_rows(CANDIDATE)
            self.assertEqual(malformed, 0)
            structural = audit(rows)
            self.assertEqual(structural["rows"], 3)
            self.assertEqual(structural["numbering"]["قانون تجريبي للاختبار فقط"]["gaps"], [])
            checklist = quantity_checklist(rows)
            self.assertEqual([item["article"] for item in checklist], ["2"])

            comparison = build_report(CANDIDATE, GAZETTE)
            self.assertTrue(comparison["all_identical"])
            self.assertEqual(comparison["summary"], {"identical_after_normalization": 3})
            self.assertEqual(comparison["candidate"]["sha256"], hashlib.sha256(CANDIDATE.read_bytes()).hexdigest())
            self.assertEqual(comparison["reference"]["sha256"], hashlib.sha256(GAZETTE.read_bytes()).hexdigest())

            independent_copy = root / "independent-copy.txt"
            independent_copy.write_bytes(GAZETTE.read_bytes())
            source = {
                "source_id": "SYNTHETIC-FIXTURE-CAPTURE",
                "source_status": "source_matched_unreviewed",
                "source_match_evidence": {
                    "validator_passed": True,
                    "original_capture_sha256": metadata["sha256"],
                    "independent_copy_sha256": hashlib.sha256(independent_copy.read_bytes()).hexdigest(),
                    "independent_copy_source_id": "SYNTHETIC-FIXTURE-INDEPENDENT-COPY",
                    "publication_date": "2025-05-03",
                    "effective_date": "2025-09-01",
                    "reuse_rights_evidence": "Repository-authored fictional fixture; test-only evidence, not a real legal source.",
                    "reuse_rights_evidence_url": "https://example.test/fixture-rights",
                    "approved_uses": [
                        "collection", "storage", "text_extraction", "indexing",
                        "commercial_product_use", "excerpt_display",
                    ],
                    "article_inventory_complete": len(rows) == comparison["candidate"]["rows_compared"],
                    "differences_resolved_against_primary": comparison["all_identical"],
                    "publication_and_effective_dates_verified": (
                        "2025-05-03" in extracted_text and "2025-09-01" in extracted_text
                    ),
                    "reuse_rights_allowed": True,
                },
            }
            tier = classify_answer_trust_tier(
                [source],
                claims_supported=True,
                citations_complete=True,
                contradictory_sources=False,
                source_matched_policy_approved=True,
                source_matched_feature_enabled=True,
            )
            self.assertEqual(tier["trust_tier"], "source_matched")
            self.assertEqual(tier["reason_codes"], ["not_lawyer_reviewed"])
            self.assertEqual(captured["audit"]["article_headings_detected"], 3)


if __name__ == "__main__":
    unittest.main()
