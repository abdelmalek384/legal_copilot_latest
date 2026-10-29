import unittest

from tools.build_decision250_table24_review_queue import categories, render


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
