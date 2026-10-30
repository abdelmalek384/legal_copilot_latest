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
            self.assertIn(provision["confidence"], {"provisional_source_text_observed", "provisional_official_text_observed"})
            if provision["confidence"] == "provisional_official_text_observed":
                self.assertTrue(any(
                    "Official General Authority for Amiri Press" in source["basis"]
                    for source in provision["source_refs"]
                ))
            self.assertNotIn(provision["provision_id"], seen)
            seen.add(provision["provision_id"])
            self.assertGreaterEqual(len(provision["source_refs"]), 1)
            for source in provision["source_refs"]:
                parsed = urlparse(source["url"])
                self.assertEqual(parsed.scheme, "https")
                self.assertTrue(parsed.netloc)
                self.assertTrue(source["basis"])

    def test_official_document_copyright_note_does_not_override_source_terms(self):
        note = self.seed["source_assessment"]
        # This seed may discuss a legal copyright basis, but must never imply that
        # it grants source-site access or commercial reuse permission.
        manifest_path = ROOT / "data/candidates/labour_law_14_2025/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        copyright_note = manifest["official_primary_source_evidence"]["egyptian_official_document_copyright_basis"]
        self.assertIn("Article 141", copyright_note["statute"])
        self.assertEqual(copyright_note["permission_status_unchanged"], "unknown")
        self.assertEqual(copyright_note["review_status"], "pending_qualified_legal_review")
        self.assertIn("systematic retrieval restrictions", copyright_note["does_not_resolve"])
        self.assertEqual(note["permission_status"], "unknown")

    def test_targeted_pdf_page_pinpoints_are_explicit_without_claiming_full_review(self):
        evidence = self.seed["source_assessment"]
        self.assertTrue(evidence["targeted_pdf_text_page_review"])
        self.assertFalse(evidence["official_pdf_downloaded"])
        self.assertFalse(evidence["page_level_review"])
        pages = {item["printed_page_label"]: item for item in evidence["targeted_pdf_pages_reviewed"]}
        self.assertIn("2", pages)
        self.assertIn("5", pages)
        self.assertIn("12", pages)
        self.assertIn("43", pages)
        self.assertIn("52", pages)
        self.assertIn("53", pages)
        self.assertIn("54", pages)
        self.assertIn("55", pages)
        self.assertIn("68", pages)
        self.assertIn("69", pages)
        self.assertIn("70", pages)
        self.assertIn("71", pages)
        self.assertIn("72", pages)
        self.assertIn("73", pages)
        self.assertIn("74", pages)
        self.assertIn("61", pages)
        self.assertIn("62", pages)
        self.assertIn("63", pages)
        self.assertIn("64", pages)
        for provision in self.seed["provisions"]:
            pinpoint = provision["page_pinpoint"]
            if pinpoint.get("source_type") == "official_text_page":
                self.assertTrue(pinpoint["pinpoint"].startswith("مادة"))
                self.assertIsNone(pinpoint["printed_page"])
                self.assertIsNone(pinpoint["pdf_page_index_zero_based"])
                self.assertEqual(pinpoint["source_url"], "https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D")
                continue
            self.assertEqual(pinpoint["gazette_issue"], "18 (تابع)")
            if "printed_pages" in pinpoint:
                self.assertEqual(len(pinpoint["printed_pages"]), len(pinpoint["pdf_page_indices_zero_based"]))
                for page in pinpoint["printed_pages"]:
                    self.assertIn(page, pages)
            else:
                self.assertIn(pinpoint["printed_page"], pages)
            self.assertEqual(pinpoint["source_url"], "https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf")

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
