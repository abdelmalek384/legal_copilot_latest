import importlib.util
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
SPEC=importlib.util.spec_from_file_location("seed_legal_candidates",ROOT/"tools"/"seed_legal_candidates.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class CandidateCatalogTests(unittest.TestCase):
    def test_every_candidate_source_has_a_permission_register_record(self):
        import json
        catalog = MODULE.load_catalog()
        register_path = ROOT / "docs" / "source_permission_register.json"
        register = json.loads(register_path.read_text(encoding="utf-8"))
        registered_ids = {item["source_id"] for item in register["sources"]}
        candidate_ids = {item["source_id"] for item in catalog["sources"]}
        self.assertEqual(candidate_ids - registered_ids, set())

    def test_candidate_permission_states_match_canonical_register(self):
        data = MODULE.load_catalog()
        self.assertTrue(MODULE.validate_permission_parity(data))

    def test_candidate_permission_mismatch_fails_closed_before_seeding(self):
        import json
        import tempfile
        data = {
            "sources": [{
                "source_id": "SRC-1",
                "source_page": "https://example.gov/candidate",
                "collection_permission": "allowed",
                "commercial_reuse_permission": "unknown",
            }],
            "documents": [],
        }
        register = {
            "sources": [{
                "source_id": "SRC-1",
                "source_page": "https://example.gov/register",
                "collection_permission": "unknown",
                "commercial_reuse_permission": "unknown",
            }]
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "permission-register.json"
            path.write_text(json.dumps(register), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "collection_permission differs"):
                MODULE.validate_permission_parity(data, path)

    def test_candidate_permission_register_host_mismatch_fails_closed(self):
        import json
        import tempfile
        data = {
            "sources": [{
                "source_id": "SRC-1",
                "source_page": "https://candidate.example.gov",
                "collection_permission": "unknown",
                "commercial_reuse_permission": "unknown",
            }],
            "documents": [],
        }
        register = {
            "sources": [{
                "source_id": "SRC-1",
                "source_page": "https://other.example.gov",
                "collection_permission": "unknown",
                "commercial_reuse_permission": "unknown",
            }]
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "permission-register.json"
            path.write_text(json.dumps(register), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source_page host differs"):
                MODULE.validate_permission_parity(data, path)

    def test_catalog_validates_and_every_document_has_known_source(self):
        data=MODULE.load_catalog()
        known={s["source_id"] for s in data["sources"]}
        self.assertGreaterEqual(len(data["documents"]),20)
        self.assertTrue(all(d["source_id"] in known for d in data["documents"]))
        self.assertTrue(all(d["candidate_status"]=="discovery_only" for d in data["documents"]))

    def test_labour_law_candidate_records_public_gazette_pdf_locators_without_upgrading_status(self):
        data = MODULE.load_catalog()
        labour = next(item for item in data["documents"] if item["document_id"] == "EG-LABOUR-14-2025")
        self.assertEqual(labour["candidate_status"], "discovery_only")
        self.assertIn("portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf", labour["notes"])
        self.assertIn("sis.gov.eg/media/760267/", labour["notes"])
        self.assertIn("Public accessibility does not establish reuse permission", labour["notes"])
        self.assertIn("not been fully compared article-by-article", labour["notes"])

    def test_malformed_catalog_entries_fail_with_clear_validation_errors(self):
        cases = [
            ({"sources": [None], "documents": []}, "sources[0] must be an object"),
            ({"sources": [{"source_id": []}], "documents": []}, "source_id must be a non-empty string"),
            ({"sources": [{"source_id": "SRC-1", "authority": "Authority", "source_page": "https://example.gov", "collection_permission": []}], "documents": []}, "invalid collection_permission"),
            ({"sources": [{"source_id": "SRC-1", "authority": "Authority", "source_page": "https://example.gov"}], "documents": [None]}, "documents[0] must be an object"),
            ([], "catalog root must be an object"),
        ]
        import json
        import tempfile
        for catalog, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as td:
                path = Path(td) / "catalog.json"
                path.write_text(json.dumps(catalog), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, expected.replace("[", r"\[").replace("]", r"\]")):
                    MODULE.load_catalog(path)

    def test_seed_is_idempotent_and_does_not_create_versions(self):
        data=MODULE.load_catalog()
        db=sqlite3.connect(":memory:")
        db.executescript("""
        CREATE TABLE legal_sources(source_id TEXT PRIMARY KEY, authority TEXT NOT NULL, source_page TEXT NOT NULL, access_status TEXT NOT NULL DEFAULT 'unknown', collection_permission TEXT NOT NULL DEFAULT 'unknown', commercial_reuse_permission TEXT NOT NULL DEFAULT 'unknown', terms_url TEXT, terms_checked_on TEXT, permission_evidence TEXT);
        CREATE TABLE legal_documents(document_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, official_title TEXT NOT NULL, document_type TEXT NOT NULL, law_number TEXT, law_year INTEGER, language TEXT NOT NULL DEFAULT 'ar');
        CREATE TABLE legal_document_versions(version_id INTEGER PRIMARY KEY, document_id TEXT, source_url TEXT);
        """)
        first=MODULE.seed(data,db)
        second=MODULE.seed(data,db)
        self.assertGreater(first[0],0); self.assertGreater(first[1],20)
        self.assertEqual(second,(0,0))
        self.assertEqual(db.execute("SELECT COUNT(*) FROM legal_document_versions").fetchone()[0],0)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM legal_sources WHERE collection_permission='allowed'").fetchone()[0],0)
        db.close()

if __name__=="__main__": unittest.main()
