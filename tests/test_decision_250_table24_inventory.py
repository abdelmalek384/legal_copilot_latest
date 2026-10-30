"""Structural regression checks for Decision 250/2026 Table 24 candidates.

These checks prove only inventory consistency, never legal accuracy or provenance.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DIR = ROOT / "data" / "candidates" / "labour_law_14_2025"


def walk_rows(rows):
    """Yield top-level and recursively nested chemical/group subentries."""
    for row in rows:
        yield row
        children = row.get("children", [])
        if not isinstance(children, list):
            raise AssertionError(f"children must be a list for row {row.get('row')}")
        yield from walk_rows(children)


class Decision250Table24InventoryTests(unittest.TestCase):
    def test_technical_index_has_one_table_24_and_no_table_25(self):
        index = json.loads(
            (CANDIDATE_DIR / "decision_250_technical_table_index_2026-10-29.json").read_text(encoding="utf-8")
        )
        table_numbers = [int(item["table"]) for item in index["tables"]]
        self.assertEqual(len(table_numbers), 24)
        self.assertEqual(table_numbers.count(24), 1)
        self.assertNotIn(25, table_numbers)
        table24 = next(item for item in index["tables"] if int(item["table"]) == 24)
        self.assertEqual(table24["printed_pages"], "249-360")
        self.assertIn("primary_match_pending", table24["status"])
        self.assertFalse(index["official_pdf_bytes_downloaded_and_hashed"])
        self.assertFalse(index["authoritative_retrieval_eligible"])

    def test_lawyer_acceptance_plan_covers_decisions_249_251_252(self):
        plan = (
            CANDIDATE_DIR / "lawyer_in_app_acceptance_plan_2026-10-29.md"
        ).read_text(encoding="utf-8")
        for test_id in ("OSH-17", "OSH-18", "OSH-19", "OSH-20", "OSH-21", "OSH-22"):
            self.assertIn(f"| {test_id} |", plan)

    def test_acceptance_plan_covers_2026_remote_work_and_wages_currentness(self):
        plan = (
            CANDIDATE_DIR / "lawyer_in_app_acceptance_plan_2026-10-29.md"
        ).read_text(encoding="utf-8")
        for test_id in ("OSH-23", "OSH-24", "OSH-25", "OSH-26", "OSH-27"):
            self.assertIn(f"| {test_id} |", plan)
        self.assertIn("خلال شهر أكتوبر 2026", plan)
        self.assertIn("3165 لسنة 2026", plan)
        self.assertIn("Do not invent a decree number or effective date.", plan)
        self.assertIn("Do not assume continuation or expiry.", plan)

    def test_decisions_249_251_252_candidate_maps_remain_quarantined(self):
        expected = {
            "decision_249_secondary_article_table_map_2026-10-30.json": {"article": 22, "table": 3, "appendix": 1},
            "decision_251_secondary_article_candidate_map_2026-10-30.json": {"article": 11},
            "decision_252_secondary_article_candidate_map_2026-10-30.json": {"article": 36, "table": 1},
        }
        for filename, expected_types in expected.items():
            payload = json.loads((CANDIDATE_DIR / filename).read_text(encoding="utf-8"))
            records = payload["records"]
            actual_types = {}
            for record in records:
                kind = record["record_type"]
                actual_types[kind] = actual_types.get(kind, 0) + 1
                self.assertEqual(record["source_class"], "secondary_scan_image_reproduction")
                self.assertEqual(record["official_gazette_match"], "not_performed")
                self.assertIsNone(record["official_pdf_sha256"])
                self.assertEqual(record["currentness_review"], "not_started")
                self.assertEqual(record["source_use_review"], "not_started")
                self.assertEqual(record["counsel_review"], "not_started")
                self.assertEqual(record["status"], "candidate_only_pending_official_match")
                self.assertFalse(record["retrieval_eligible"])
            self.assertEqual(actual_types, expected_types)

    def test_official_gazette_manifest_preserves_restricted_access_and_rights_status(self):
        manifest = json.loads((ROOT / "docs" / "source_manifest.json").read_text(encoding="utf-8"))
        source = next(item for item in manifest["sources"] if item["id"] == "EG-OFFICIAL-GAZETTE")
        repository = next(item for item in manifest["sources"] if item["id"] == "EG-DSPACE-OFFICIAL-GAZETTE-CATALOGUE")
        self.assertIn("Amiri Press portal located", source["access_status"])
        self.assertEqual(source["commercial_reuse"], "not_confirmed")
        self.assertEqual(source["bulk_export"], "not_confirmed")
        self.assertIn("dspace.id.com.eg", repository["url"])
        self.assertIn("request-copy restricted", repository["access_status"])
        self.assertEqual(repository["license_status"], "unknown")
        requirements = " ".join(repository["verification_requirements"])
        self.assertIn("dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full", requirements)
        self.assertIn("Do not bypass login or request-copy controls", requirements)

    def test_article296_penalty_excerpt_remains_quarantined(self):
        path = CANDIDATE_DIR / "official_primary_text_article296_2026-10-30.jsonl"
        records = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["article"], 296)
        self.assertEqual(record["pdf_page_index"], 108)
        self.assertEqual(record["printed_page"], 111)
        self.assertFalse(record["original_pdf_bytes_obtained"])
        self.assertIsNone(record["original_pdf_sha256"])
        self.assertEqual(record["currentness_review"], "not_started")
        self.assertEqual(record["counsel_review"], "not_started")
        self.assertEqual(record["source_use_status"], "provisional_official_document_exclusion_candidate_pending_counsel")
        self.assertFalse(record["retrieval_eligible"])
        self.assertIn("مادة (٢٩٦)", record["source_text_ar"])
        self.assertIn("٢٧٢، ٢٧١، ٢٧٠", record["source_text_ar"])
        self.assertIn("٢٦٧، ٢٦٨، ٢٦٩", record["source_text_ar"])
        self.assertIn("٢٦٠", record["source_text_ar"])
        self.assertIn("٢٦١", record["source_text_ar"])
        self.assertIn("خمسة آلاف جنيه", record["source_text_ar"])
        self.assertIn("مائة ألف جنيه", record["source_text_ar"])
        self.assertIn("تضاعف الغرامة في حالة العود", record["source_text_ar"])

    def test_secondary_candidate_inventory_is_contiguous_and_quarantined(self):
        batches = sorted(CANDIDATE_DIR.glob("decision_250_table24_candidate_batch*_2026-*.json"))
        self.assertEqual(len(batches), 38)
        row_numbers = []
        for path in batches:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["table"], "24")
            self.assertEqual(payload["source"]["class"], "secondary_transcription")
            self.assertEqual(payload["source"]["official_gazette_match"], "not_performed")
            self.assertIsNone(payload["source"]["official_pdf_sha256"])
            self.assertEqual(payload["status"], "candidate_only_not_for_authoritative_retrieval")
            row_numbers.extend(int(row["row"]) for row in walk_rows(payload["rows"]))
        self.assertEqual(len(row_numbers), 781)
        self.assertEqual(sorted(row_numbers), list(range(1, 782)))
        self.assertEqual(len(set(row_numbers)), 781)


if __name__ == "__main__":
    unittest.main()
