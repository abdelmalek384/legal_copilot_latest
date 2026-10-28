import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data/candidates/labour_law_14_2025/provisional_provisions_seed.json"


class LabourLawPrimaryEvidenceSeedTests(unittest.TestCase):
    def setUp(self):
        self.seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    def test_seed_is_explicitly_not_search_eligible_or_verified(self):
        evidence = self.seed["source_assessment"]
        self.assertFalse(evidence["search_eligible"])
        self.assertFalse(evidence["official_pdf_downloaded"])
        self.assertFalse(evidence["page_level_review"])
        self.assertFalse(evidence["full_article_by_article_comparison"])
        self.assertFalse(evidence["amendment_history_verified"])
        self.assertFalse(evidence["current_status_verified"])
        self.assertEqual(evidence["permission_status"], "unknown")
        self.assertEqual(evidence["lawyer_review_status"], "pending")

    def test_each_provision_has_article_pinpoint_and_https_evidence(self):
        provisions = self.seed["provisions"]
        self.assertGreaterEqual(len(provisions), 5)
        seen = set()
        for provision in provisions:
            self.assertTrue(provision["provision_id"])
            self.assertTrue(provision["provision_ref"])
            self.assertTrue(provision["summary_ar"])
            self.assertEqual(provision["human_review"], "pending")
            self.assertEqual(provision["confidence"], "provisional_source_text_observed")
            self.assertNotIn(provision["provision_id"], seen)
            seen.add(provision["provision_id"])
            self.assertGreaterEqual(len(provision["source_refs"]), 1)
            for source in provision["source_refs"]:
                parsed = urlparse(source["url"])
                self.assertEqual(parsed.scheme, "https")
                self.assertTrue(parsed.netloc)
                self.assertTrue(source["basis"])

    def test_publication_metadata_and_commencement_candidates_are_explicit(self):
        evidence = self.seed["source_assessment"]
        self.assertEqual(evidence["official_gazette_issue"], "18 (تابع)")
        self.assertEqual(evidence["publication_date"], "2025-05-03")
        commencement = next(
            item for item in self.seed["provisions"]
            if item["topic"] == "commencement"
        )
        self.assertEqual(commencement["derived_dates"]["general_commencement_candidate"], "2025-09-01")
        self.assertEqual(commencement["derived_dates"]["specialized_labour_courts_candidate"], "2025-10-01")


if __name__ == "__main__":
    unittest.main()
