import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "labour_law_14_2025" / "related_instruments" / "public_text_crosswalk_2026-10-28.json"
INVENTORY = ROOT / "docs" / "phase_2_document_inventory.json"


class TestLabourDecisionPublicTextCrosswalk(unittest.TestCase):
    def test_working_time_decisions_keep_primary_and_secondary_evidence_separate(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in data["decisions"]}
        self.assertFalse(data["search_eligible"])
        d290 = records["EG-LABOUR-DECISION-290-2025"]
        d291 = records["EG-LABOUR-DECISION-291-2025"]
        for record in (d290, d291):
            self.assertEqual(record["primary_lead"]["url"], "https://dspace.id.com.eg/items/32fa3458-c4a5-4a6a-950c-23c6c74d41c1")
            self.assertIn("request-a-copy restricted", record["primary_lead"]["status"])
            self.assertEqual(record["gazette_date"], "2025-12-30 (official Amiri Press issue metadata; secondary EastLaws record independently states the same Gazette publication date)")
            self.assertEqual(record["effective_date"], "2025-12-31 (stated by EastLaws and derived from Article 4 in both secondary transcriptions; not primary-PDF verified)" if record is d290 else "2025-12-31 (stated by EastLaws and derived from Article 5 in both secondary transcriptions; not primary-PDF verified)")
            if record is d290:
                self.assertIn("Two public secondary full-text transcriptions", record["secondary_text"]["status"])
                self.assertIn("neither compared", record["secondary_text"]["status"])
            else:
                self.assertIn("cross-checked against third-party hosted Gazette page images", record["secondary_text"]["status"])
                self.assertIn("original DSpace PDF not compared", record["secondary_text"]["status"])
            self.assertIn("unknown", record["reuse_rights"])
            self.assertTrue(record["currentness"].startswith("not fully verified"))
            self.assertFalse(record.get("search_eligible", False))
        repository = d290["third_party_repository_metadata"]
        self.assertEqual(repository["url"], "https://dspace.id.com.eg/items/c2f1917d-0c72-4f51-b207-04d76e56a829/full")
        self.assertIn("not an official Gazette copy", repository["status"])
        self.assertIn("103.23 KB", " ".join(repository["listed_files"]))
        self.assertIn("105.2 KB", " ".join(repository["listed_files"]))
        self.assertIn("no hash", repository["status"])
        self.assertIn("intermittent work", d290["secondary_text"]["summary"])
        self.assertIn("35%", d291["secondary_text"]["summary"])
        self.assertIn("70%", d291["secondary_text"]["summary"])
        self.assertIn("annual overtime maximum", d291["secondary_text"]["summary"])
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        docs = {item["document_id"]: item for item in inventory["documents"]}
        for document_id, url in (("EG-LABOUR-DECISION-290-2025", "https://www.eastlaws.com/legislation-full-text/ar/egypt/labor/30-12-2025/no-290?id=5008505&type=1"), ("EG-LABOUR-DECISION-291-2025", "https://www.eastlaws.com/legislation-full-text/ar/egypt/labor/30-12-2025/no-291?id=5064176&type=1")):
            record = docs[document_id]
            self.assertEqual(record["legal_status"], "unknown")
            self.assertEqual(record["review_status"], "discovery_only")
            self.assertTrue(any(source["url"] == url and "secondary" in source["status"] for source in record["source_urls"]))



    def test_decision_290_meles_metadata_is_recorded_without_claiming_primary_text(self):
        register = json.loads((ROOT / "docs" / "phase_2_source_evidence_register.json").read_text(encoding="utf-8"))
        source = next(item for item in register["sources"] if item["source_id"] == "EG-MELES-DSpace-DECISION-290-2025")
        self.assertEqual(source["publication_date"], "2025-12-11")
        self.assertEqual(source["document_ids"], ["EG-LABOUR-DECISION-290-2025"])
        self.assertEqual(source["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertIn("103.23 KB", source["notes"])
        self.assertIn("105.2 KB", source["notes"])
        self.assertIn("no PDF or license bytes", source["notes"])
        currentness = (ROOT / "data" / "candidates" / "labour_law_14_2025" / "related_instruments" / "currentness_register_2026-10-28.md").read_text(encoding="utf-8")
        self.assertIn("Decision 290/2025 — exact identity and secondary-text corroboration", currentness)
        self.assertIn("G3 secondary corroboration plus third-party metadata; not G4", currentness)
        self.assertIn("search_eligible=false", currentness)

    def test_decisions_292_and_294_have_issue_metadata_and_secondary_text(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in data["decisions"]}
        for document_id in ("EG-LABOUR-DECISION-292-2025", "EG-LABOUR-DECISION-294-2025"):
            item = records[document_id]
            self.assertEqual(item["primary_lead"]["url"], "https://dspace.id.com.eg/items/37add437-802d-4848-8a24-8e064db22fcc/full")
            self.assertIn("request-a-copy restricted", item["primary_lead"]["status"])
            if document_id == "EG-LABOUR-DECISION-292-2025":
                self.assertIn("Two public secondary", item["secondary_text"]["status"])
                self.assertIn("neither compared", item["secondary_text"]["status"])
            else:
                self.assertIn("cross-checked against Ministry-hosted text copy", item["secondary_text"]["status"])
                self.assertIn("Gazette issue PDF not compared", item["secondary_text"]["status"])
            self.assertTrue(item["currentness"].startswith("not fully verified"))
            self.assertIn("unknown", item["reuse_rights"])
        self.assertIn("48 hours", records["EG-LABOUR-DECISION-292-2025"]["secondary_text"]["summary"])
        self.assertIn("12 paid holidays", records["EG-LABOUR-DECISION-294-2025"]["secondary_text"]["summary"])


    def test_decisions_288_and_289_have_secondary_crosswalks(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in data["decisions"]}
        for document_id in ("EG-LABOUR-DECISION-288-2025", "EG-LABOUR-DECISION-289-2025"):
            item = records[document_id]
            self.assertEqual(item["primary_lead"]["url"], "https://dspace.id.com.eg/items/32fa3458-c4a5-4a6a-950c-23c6c74d41c1")
            self.assertIn("request-a-copy restricted", item["primary_lead"]["status"])
            if document_id == "EG-LABOUR-DECISION-288-2025":
                self.assertIn("neither compared", item["secondary_text"]["status"])
            else:
                self.assertIn("cross-checked against Ministry-hosted text copy", item["secondary_text"]["status"])
                self.assertIn("Gazette issue PDF not compared", item["secondary_text"]["status"])
            self.assertTrue(item["currentness"].startswith("not fully verified"))
            self.assertIn("unknown", item["reuse_rights"])
        self.assertIn("five consecutive hours", records["EG-LABOUR-DECISION-288-2025"]["secondary_text"]["summary"])
        self.assertIn("48 hours per week", records["EG-LABOUR-DECISION-289-2025"]["secondary_text"]["summary"])


    def test_parent_law_primary_anchors_are_separate_from_decision_text(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in data["decisions"]}
        expected = {
            "EG-LABOUR-DECISION-288-2025": {118, 119},
            "EG-LABOUR-DECISION-289-2025": {117, 121},
            "EG-LABOUR-DECISION-290-2025": {119, 121},
            "EG-LABOUR-DECISION-291-2025": {121, 188},
            "EG-LABOUR-DECISION-292-2025": {121, 123},
            "EG-LABOUR-DECISION-294-2025": {129},
        }
        for document_id, articles in expected.items():
            anchor = records[document_id]["law_article_primary_anchor"]
            self.assertEqual(anchor["url"], "https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf")
            self.assertTrue(articles.issubset({item["law_article"] for item in anchor["articles"]}))
            self.assertIn("does not authenticate", anchor["caution"])
            self.assertTrue(all(item["printed_gazette_page"] > 0 for item in anchor["articles"]))


    def test_decision_291_page_image_reproduction_is_not_original_or_reuse_clearance(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        item = next(x for x in data["decisions"] if x["document_id"] == "EG-LABOUR-DECISION-291-2025")
        check = item["gazette_page_image_reproduction"]
        self.assertEqual(check["pages"][0]["printed_page"], 21)
        self.assertEqual(check["pages"][1]["printed_page"], 22)
        self.assertIn("original DSpace PDF remains request-a-copy restricted", check["caveat"])
        self.assertIn("35% daytime", " ".join(check["pages"][0]["observations"]))
        self.assertIn("three months", " ".join(check["pages"][1]["observations"]))
        self.assertEqual(item["annual_overtime_maximum_followup"]["deadline_candidate"], "2026-03-31")
        self.assertIn("No subsequent", item["annual_overtime_maximum_followup"]["followup_status"])
        self.assertIn("not proof", item["annual_overtime_maximum_followup"]["followup_status"])
        self.assertIn("reuse permissions are not established", check["caveat"])


    def test_decision_289_ministry_hosted_text_is_separate_from_gazette_verification(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        item = next(x for x in data["decisions"] if x["document_id"] == "EG-LABOUR-DECISION-289-2025")
        copy = item["ministry_hosted_text_copy"]
        self.assertIn("not the Gazette issue PDF", copy["caveat"])
        self.assertIn("eight hours", " ".join(copy["articles"][0]["observations"]))
        self.assertIn("Article 121", " ".join(copy["articles"][0]["observations"]))
        self.assertIn("Gazette issue PDF not compared", item["secondary_text"]["status"])


    def test_decision_288_meles_repository_lead_does_not_claim_gazette_verification(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        item = next(x for x in data["decisions"] if x["document_id"] == "EG-LABOUR-DECISION-288-2025")
        lead = item["additional_repository_lead"]
        self.assertIn("not the Official Gazette issue scan", lead["caveat"])
        self.assertIn("request-copy restricted", lead["status"])
        self.assertIn("license.txt", " ".join(lead["files"]))


    def test_decision_294_ministry_hosted_text_is_separate_from_gazette_verification(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        item = next(x for x in data["decisions"] if x["document_id"] == "EG-LABOUR-DECISION-294-2025")
        copy = item["ministry_hosted_text_copy"]
        self.assertIn("not the Gazette issue PDF", copy["caveat"])
        self.assertIn("Twelve paid holiday categories", " ".join(copy["articles"][0]["observations"]))
        self.assertIn("double pay", " ".join(copy["articles"][1]["observations"]))
        self.assertIn("Non-Muslim", " ".join(copy["articles"][2]["observations"]))
        self.assertIn("Gazette issue PDF not compared", item["secondary_text"]["status"])

if __name__ == "__main__":
    unittest.main()
