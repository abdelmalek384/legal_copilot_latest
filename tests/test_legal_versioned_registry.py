import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

class LegalVersionedRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["COPILOT_DB"] = str(Path(self.tmp.name) / "registry.db")
        import importlib
        import app
        self.app = importlib.reload(app)
        self.db = self.app.conn()

    def tearDown(self):
        try:
            self.db.close()
        finally:
            import app
            app._t.c = None
            app._schema_ready = False
            self.tmp.cleanup()
            os.environ.pop("COPILOT_DB", None)

    def test_registry_tables_exist_and_legacy_chunks_are_linkable(self):
        tables = {r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for name in ("legal_sources", "legal_documents", "legal_document_versions", "legal_version_relations", "legal_review_events"):
            self.assertIn(name, tables)
        cols = {r[1] for r in self.db.execute("PRAGMA table_info(chunks)")}
        self.assertIn("document_version_id", cols)

    def test_unknown_is_default_and_verified_requires_explicit_update(self):
        self.db.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("S1", "Example Authority", "https://example.gov")
        )
        self.db.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
            ("D1", "S1", "عنوان تجريبي", "legislation")
        )
        cur = self.db.execute(
            "INSERT INTO legal_document_versions(document_id,version_label,source_url) VALUES(?,?,?)",
            ("D1", "original", "https://example.gov/law.pdf")
        )
        row = self.db.execute("SELECT legal_status,review_status,authenticity_verified,status_verified FROM legal_document_versions WHERE version_id=?", (cur.lastrowid,)).fetchone()
        self.assertEqual(tuple(row), ("unknown", "pending_source_review", 0, 0))

    def test_invalid_status_and_relation_types_are_rejected(self):
        self.db.execute("INSERT INTO legal_sources(source_id,authority,source_page) VALUES('S1','Example','https://example.gov')")
        self.db.execute("INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES('D1','S1','Test','law')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url,legal_status) VALUES('D1','v1','https://example.gov/a.pdf','probably_current')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url,legal_status) VALUES('D1','v1','https://example.gov/a.pdf','in_force')")
            self.db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url,legal_status) VALUES('D1','v2','https://example.gov/b.pdf','in_force')")
            ids = [x[0] for x in self.db.execute("SELECT version_id FROM legal_document_versions")]
            self.db.execute("INSERT INTO legal_version_relations(from_version_id,to_version_id,relation_type) VALUES(?,?,?)", (ids[0],ids[1],"magic"))

if __name__ == "__main__":
    unittest.main()
