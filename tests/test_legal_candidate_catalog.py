import importlib.util
import os
import sqlite3
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_catalog_validates_and_every_document_has_known_source(self):
        data=MODULE.load_catalog()
        known={s["source_id"] for s in data["sources"]}
        self.assertGreaterEqual(len(data["documents"]),20)
        self.assertTrue(all(d["source_id"] in known for d in data["documents"]))
        self.assertTrue(all(d["candidate_status"]=="discovery_only" for d in data["documents"]))

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

    def test_configured_seed_writes_only_to_shared_corpus_profile(self):
        from database_runtime import DatabaseRuntime

        data = MODULE.load_catalog()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "control").mkdir()
            (root / "corpus").mkdir()
            env = {
                "COPILOT_CONTROL_DB": str(root / "control" / "control.sqlite3"),
                "COPILOT_TENANT_DB_ROOT": str(root / "tenants"),
                "COPILOT_CORPUS_DB": str(root / "corpus" / "corpus.sqlite3"),
            }
            with patch.dict(os.environ, env, clear=False):
                os.environ.pop("COPILOT_DB", None)
                inserted_sources, inserted_documents = MODULE.seed_configured_corpus(data)
                self.assertGreater(inserted_sources, 0)
                self.assertGreater(inserted_documents, 20)

                runtime = DatabaseRuntime.from_env()
                runtime.initialize()
                try:
                    corpus = runtime.legal_corpus_connection()
                    self.assertEqual(
                        corpus.execute("SELECT COUNT(*) FROM legal_sources").fetchone()[0],
                        len(data["sources"]),
                    )
                    self.assertEqual(
                        corpus.execute("SELECT COUNT(*) FROM legal_documents").fetchone()[0],
                        len(data["documents"]),
                    )
                    firm_id, _ = runtime.provision_firm("Candidate Seeder Isolation Firm")
                    user_id = runtime.create_initial_firm_owner(
                        firm_id, "Seeder Owner", "seeder-owner@example.test", "test-hash"
                    )
                    context = runtime.resolve_context(user_id, firm_id)
                    firm = runtime.firm_connection(context)
                    firm_tables = {
                        row[0] for row in firm.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                    }
                    self.assertNotIn("legal_sources", firm_tables)
                    control = runtime.control_connection()
                    control_tables = {
                        row[0] for row in control.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                    }
                    self.assertNotIn("legal_sources", control_tables)
                finally:
                    runtime.close_current_thread()

    def test_configured_seed_refuses_legacy_shared_database_mode(self):
        data = MODULE.load_catalog()
        with patch.dict(os.environ, {"COPILOT_DB": "legacy.sqlite3"}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "legacy shared database"):
                MODULE.seed_configured_corpus(data)

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
