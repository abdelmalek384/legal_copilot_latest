import tempfile
import unittest
from pathlib import Path

from tools.build_decision250_table24_review_queue import categories, load_rows, render


class Decision250Table24ReviewQueueTests(unittest.TestCase):
    def test_flags_anomalies_high_risk_currentness_and_missing_cas(self):
        row = {
            "row": 537,
            "name_en": "Oil mist",
            "source_line": 5377,
            "cas": None,
            "anomaly": "Secondary text says removed as a standalone item",
            "currentness_candidate": "Primary confirmation required",
            "risk_note": "Needs specialist review",
            "raw_limit_and_note_text": "surface value 1 mg/100 cm2 (SL)",
            "status": "pending_official_match",
        }
        tags = categories(row)
        self.assertIn("TEXT/IDENTIFIER ANOMALY", tags)
        self.assertIn("HIGH-RISK REVIEW", tags)
        self.assertIn("CURRENTNESS CHECK", tags)
        self.assertIn("NO CAS / GROUP ENTRY", tags)
        self.assertIn("POSSIBLE SURFACE/AIR UNIT REVIEW", tags)

    def test_flags_secondary_image_discrepancy_and_shows_locator(self):
        row = {
            "row": 34,
            "name_en": "Aluminum oxide",
            "source_line": 4541,
            "cas": "1344-281",
            "status": "pending_official_match",
            "secondary_scan_match_status": "secondary_image_discrepancy_found",
            "secondary_scan_printed_page": 254,
            "secondary_scan_image_url": "https://example.invalid/page-254.webp",
            "secondary_scan_discrepancy": {
                "field": "cas_identifier",
                "candidate_transcription": "1344-281",
                "secondary_image_observed_tentative": "1344-28-1",
                "status": "pending_original_gazette_confirmation",
                "note": "Do not correct pending original Gazette confirmation.",
            },
        }
        tags = categories(row)
        self.assertIn("SECONDARY IMAGE DISCREPANCY — ORIGINAL GAZETTE REQUIRED", tags)
        rendered = render([row])
        self.assertIn("p. 254: https://example.invalid/page-254.webp", rendered)
        self.assertIn("Do not correct pending original Gazette confirmation.", rendered)
        self.assertIn("cas_identifier: 1344-281 vs 1344-28-1", rendered)

    def test_loader_refuses_partial_queue_when_batches_are_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "refusing to build a partial review queue"):
                load_rows(Path(tmp))

    def test_render_keeps_queue_as_unverified_triage(self):
        result = render([{
            "row": 1,
            "name_en": "Example chemical",
            "name_ar": "مادة اختبار",
            "source_line": 100,
            "cas": "123-45-6",
            "anomaly": "Test anomaly",
            "raw_limit_and_note_text": "1 mg/m3",
            "status": "pending_official_match",
        }])
        self.assertIn("no legal row is approved", result)
        self.assertIn("TEXT/IDENTIFIER ANOMALY", result)
        self.assertIn("does not resolve a single anomaly automatically", result)


if __name__ == "__main__":
    unittest.main()
