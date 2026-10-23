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
    def test_catalog_validates_and_every_document_has_known_source(self):
        data=MODULE.load_catalog()
        known={s["source_id"] for s in data["sources"]}
        self.assertGreaterEqual(len(data["documents"]),20)
        self.assertTrue(all(d["source_id"] in known for d in data["documents"]))
        self.assertTrue(all(d["candidate_status"]=="discovery_only" for d in data["documents"]))

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
