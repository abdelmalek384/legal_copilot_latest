"""Acceptance tests for isolated initial database profile schemas."""
import sqlite3
import unittest
from pathlib import Path
from schema_profiles import apply_profile_migrations

ROOT = Path(__file__).resolve().parents[1] / "migrations"

class ProfileInitialSchemaTests(unittest.TestCase):
    def build(self, profile):
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        expected_versions = [1, 2] if profile in ("control_plane", "firm") else [1]
        self.assertEqual(apply_profile_migrations(db, profile, ROOT), expected_versions)
        self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
        return db

    def test_profiles_have_disjoint_ownership_tables(self):
        control, firm, corpus = (self.build(p) for p in ("control_plane","firm","legal_corpus"))
        names = lambda db: {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn("tenant_database_catalog", names(control))
        self.assertNotIn("chunks", names(control))
        self.assertIn("cases", names(firm)); self.assertIn("chunks_fts", names(firm))
        self.assertNotIn("legal_sources", names(firm))
        self.assertIn("legal_sources", names(corpus)); self.assertIn("chunks_fts", names(corpus))
        self.assertNotIn("cases", names(corpus)); self.assertNotIn("tenant_database_catalog", names(corpus))
        control.close(); firm.close(); corpus.close()

    def test_firm_fts_insert_update_delete(self):
        db = self.build("firm")
        db.execute("INSERT INTO cases(id,title) VALUES(1,'matter')")
        db.execute("INSERT INTO chunks(id,text,norm,case_id) VALUES(1,'secret firm text','firmsecretterm',1)")
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'firmsecretterm'").fetchone()[0], 1)
        db.execute("UPDATE chunks SET norm='updatedsecretterm' WHERE id=1")
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'firmsecretterm'").fetchone()[0], 0)
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'updatedsecretterm'").fetchone()[0], 1)
        db.execute("DELETE FROM chunks WHERE id=1")
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'updatedsecretterm'").fetchone()[0], 0)
        db.close()

    def test_two_firm_databases_do_not_share_search_content(self):
        firm_a, firm_b = self.build("firm"), self.build("firm")
        firm_a.execute("INSERT INTO cases(id,title) VALUES(1,'A')")
        firm_b.execute("INSERT INTO cases(id,title) VALUES(1,'B')")
        firm_a.execute("INSERT INTO chunks(id,text,norm,case_id) VALUES(1,'alpha private sentinel','alphaprivatesentinel',1)")
        firm_b.execute("INSERT INTO chunks(id,text,norm,case_id) VALUES(1,'beta private sentinel','betaprivatesentinel',1)")
        self.assertEqual(firm_a.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'alphaprivatesentinel'").fetchone()[0], 1)
        self.assertEqual(firm_a.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'betaprivatesentinel'").fetchone()[0], 0)
        self.assertEqual(firm_b.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'betaprivatesentinel'").fetchone()[0], 1)
        self.assertEqual(firm_b.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'alphaprivatesentinel'").fetchone()[0], 0)
        firm_a.close(); firm_b.close()

    def test_firm_document_review_scope_guards(self):
        db = self.build("firm")
        db.execute("INSERT INTO cases(id,title,firm_id) VALUES(1,'Matter A',7)")
        db.execute("INSERT INTO cases(id,title,firm_id) VALUES(2,'Matter B',7)")
        db.execute("INSERT INTO docs(id,case_id,firm_id,name) VALUES(10,1,7,'doc-a')")
        db.execute("INSERT INTO docs(id,case_id,firm_id,name) VALUES(20,2,7,'doc-b')")
        db.execute("INSERT INTO chunks(id,text,norm,case_id,document_id) VALUES(100,'text a','texta',1,10)")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "chunk document/case scope mismatch"):
            db.execute("INSERT INTO chunks(id,text,norm,case_id,document_id) VALUES(101,'bad','bad',2,10)")
        db.execute("""INSERT INTO document_extraction_reviews
            (id,document_id,case_id,firm_id,chunk_id,reviewer_user_id,outcome,original_text,reviewed_text)
            VALUES(1,10,1,7,100,55,'accepted','raw','reviewed')""")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "document extraction review scope mismatch"):
            db.execute("""INSERT INTO document_extraction_reviews
                (id,document_id,case_id,firm_id,chunk_id,reviewer_user_id,outcome,original_text,reviewed_text)
                VALUES(2,10,2,7,100,55,'accepted','raw','reviewed')""")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "document extraction review scope mismatch"):
            db.execute("UPDATE document_extraction_reviews SET chunk_id=999 WHERE id=1")
        db.close()

    def test_firm_scope_migration_fails_closed_on_existing_mismatch(self):
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            firm = root / "firm"
            firm.mkdir()
            shutil.copy(ROOT / "firm" / "0001_firm_matter_foundation.sql", firm)
            db = sqlite3.connect(":memory:")
            try:
                self.assertEqual(apply_profile_migrations(db, "firm", root), [1])
                db.execute("INSERT INTO cases(id,title,firm_id) VALUES(1,'Matter A',7)")
                db.execute("INSERT INTO cases(id,title,firm_id) VALUES(2,'Matter B',7)")
                db.execute("INSERT INTO docs(id,case_id,firm_id,name) VALUES(10,1,7,'doc-a')")
                db.execute("INSERT INTO chunks(id,text,norm,case_id,document_id) VALUES(100,'bad','bad',2,10)")
                db.commit()
                shutil.copy(ROOT / "firm" / "0002_enforce_document_review_scope.sql", firm)
                with self.assertRaises(sqlite3.IntegrityError):
                    apply_profile_migrations(db, "firm", root)
                self.assertIsNotNone(db.execute("SELECT 1 FROM chunks WHERE id=100").fetchone())
                self.assertEqual(db.execute("SELECT COUNT(*) FROM schema_migrations WHERE version=2").fetchone()[0], 0)
            finally:
                db.close()

    def test_corpus_requires_version_provenance(self):
        db = self.build("legal_corpus")
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("INSERT INTO chunks(text,norm,document_version_id) VALUES('text','text',999)")
        db.execute("INSERT INTO legal_sources(source_id,authority,source_page) VALUES('src','Authority','https://example.invalid')")
        db.execute("INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES('doc','src','Title','law')")
        db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url) VALUES('doc','v1','https://example.invalid/law')")
        db.execute("INSERT INTO chunks(text,norm,document_version_id) VALUES('law passage','lawpassage',1)")
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'lawpassage'").fetchone()[0], 1)
        db.close()

    def test_case_children_cascade(self):
        db = self.build("firm")
        db.execute("INSERT INTO cases(id,title) VALUES(7,'test')")
        db.execute("INSERT INTO notes(case_id,text) VALUES(7,'note')")
        db.execute("DELETE FROM cases WHERE id=7")
        self.assertEqual(db.execute("SELECT count(*) FROM notes").fetchone()[0], 0)
        db.close()

if __name__ == "__main__":
    unittest.main()
