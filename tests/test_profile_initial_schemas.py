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
        expected_versions = sorted(int(path.name.split("_", 1)[0]) for path in (ROOT / profile).glob("*.sql"))
        self.assertEqual(apply_profile_migrations(db, profile, ROOT), expected_versions)
        # Runtime provisioning supplies the firm ID only; table and immutable
        # guards are owned by the versioned firm-profile migration.
        if profile == "firm":
            db.execute("INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,7)")
        self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
        return db

    def test_firm_binding_schema_is_migration_managed_and_immutable(self):
        db = self.build("firm")
        self.assertIn(
            "tenant_database_binding",
            {row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )},
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "binding is immutable"):
            db.execute("UPDATE tenant_database_binding SET firm_id=8 WHERE singleton=1")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "binding is immutable"):
            db.execute("DELETE FROM tenant_database_binding WHERE singleton=1")
        self.assertEqual(
            db.execute("SELECT firm_id FROM tenant_database_binding WHERE singleton=1").fetchone()[0],
            7,
        )
        db.close()

    def test_profiles_have_disjoint_ownership_tables(self):
        control, firm, corpus = (self.build(p) for p in ("control_plane","firm","legal_corpus"))
        names = lambda db: {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn("tenant_database_catalog", names(control))
        self.assertIn("users", names(control))
        self.assertIn("firm_memberships", names(control))
        self.assertIn("user_platform_roles", names(control))
        self.assertIn("platform_security_events", names(control))
        event_triggers = {r[0] for r in control.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
        self.assertTrue({"platform_security_events_no_update", "platform_security_events_no_delete"} <= event_triggers)
        self.assertNotIn("users", names(firm))
        self.assertNotIn("firm_memberships", names(firm))
        self.assertNotIn("user_platform_roles", names(firm))
        self.assertNotIn("users", names(corpus))
        self.assertNotIn("firm_memberships", names(corpus))
        self.assertNotIn("user_platform_roles", names(corpus))
        self.assertNotIn("chunks", names(control))
        self.assertIn("cases", names(firm)); self.assertIn("chunks_fts", names(firm))
        self.assertNotIn("legal_sources", names(firm))
        self.assertIn("legal_sources", names(corpus)); self.assertIn("chunks_fts", names(corpus))
        self.assertNotIn("cases", names(corpus)); self.assertNotIn("tenant_database_catalog", names(corpus))
        source_columns = {row["name"] for row in corpus.execute("PRAGMA table_info(legal_sources)")}
        version_columns = {row["name"] for row in corpus.execute("PRAGMA table_info(legal_document_versions)")}
        self.assertIn("source_class", source_columns)
        self.assertIn("text_sha256", version_columns)
        self.assertIn("publication_evidence_url", version_columns)
        control.close(); firm.close(); corpus.close()

    def test_each_profile_excludes_all_foreign_boundary_tables(self):
        control, firm, corpus = (self.build(p) for p in ("control_plane", "firm", "legal_corpus"))
        names = lambda db: {
            row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        control_names, firm_names, corpus_names = names(control), names(firm), names(corpus)

        # These sets are deliberate architecture boundaries, not merely a
        # sample of tables. New profile migrations must extend the appropriate
        # set when adding a table that belongs to another security domain.
        identity_and_control = {
            "firms", "users", "firm_memberships", "user_platform_roles",
            "platform_security_events", "tenant_database_catalog",
            "auth_sessions", "login_attempts", "api_rate_limit_windows",
        }
        matter_owned = {
            "cases", "members", "tasks", "events", "notes", "deadlines", "fees",
            "sessions", "docs", "document_extraction_reviews", "research_conversations",
            "research_messages", "case_deletion_audit", "security_audit_events",
            "tenant_database_binding",
        }
        corpus_owned = {
            "legal_sources", "legal_documents", "legal_document_versions",
            "legal_version_relations", "legal_review_events",
        }

        self.assertFalse(identity_and_control & firm_names, sorted(identity_and_control & firm_names))
        self.assertFalse(identity_and_control & corpus_names, sorted(identity_and_control & corpus_names))
        self.assertFalse(matter_owned & control_names, sorted(matter_owned & control_names))
        self.assertFalse(matter_owned & corpus_names, sorted(matter_owned & corpus_names))
        self.assertFalse(corpus_owned & control_names, sorted(corpus_owned & control_names))
        self.assertFalse(corpus_owned & firm_names, sorted(corpus_owned & firm_names))
        control.close()
        firm.close()
        corpus.close()

    def test_firm_profile_installs_insert_and_update_scope_guards_for_every_owned_table(self):
        db = self.build("firm")
        expected = {
            "cases": {"cases_tenant_firm_insert", "cases_tenant_firm_update"},
            "docs": {"docs_tenant_firm_insert", "docs_tenant_firm_update"},
            "document_extraction_reviews": {"reviews_tenant_firm_insert", "reviews_tenant_firm_update"},
            "research_conversations": {
                "research_conversations_tenant_firm_insert",
                "research_conversations_tenant_firm_update",
            },
            "case_deletion_audit": {
                "case_deletion_audit_tenant_firm_insert",
                "case_deletion_audit_tenant_firm_update",
            },
            "original_file_objects": {
                "original_file_objects_tenant_insert",
                "original_file_objects_tenant_update",
            },
        }
        installed = {
            row["name"]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        for table, trigger_names in expected.items():
            with self.subTest(table=table):
                self.assertTrue(
                    trigger_names <= installed,
                    f"{table} is missing tenant-binding guards: {sorted(trigger_names - installed)}",
                )
        db.close()

    def test_wrong_firm_scope_is_rejected_on_every_firm_owned_table(self):
        db = self.build("firm")
        for table in (
            "cases",
            "docs",
            "document_extraction_reviews",
            "research_conversations",
            "case_deletion_audit",
        ):
            with self.subTest(table=table):
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute(f'INSERT INTO "{table}"(firm_id) VALUES(999)')
                self.assertEqual(
                    db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0],
                    0,
                    f"{table} accepted or retained a row for the wrong firm",
                )
        db.close()

    def test_wrong_firm_updates_are_rejected_on_every_firm_owned_table(self):
        db = self.build("firm")
        db.execute("INSERT INTO cases(id,title,firm_id) VALUES(1,'Matter',7)")
        db.execute("INSERT INTO docs(id,case_id,firm_id,name) VALUES(2,1,7,'matter.docx')")
        db.execute(
            "INSERT INTO chunks(id,case_id,document_id,text,norm) "
            "VALUES(3,1,2,'source text','source text')"
        )
        db.execute(
            "INSERT INTO document_extraction_reviews"
            "(id,document_id,case_id,firm_id,chunk_id,reviewer_user_id,outcome,original_text,reviewed_text) "
            "VALUES(4,2,1,7,3,1,'accepted','source text','source text')"
        )
        db.execute(
            "INSERT INTO research_conversations(id,user_id,firm_id,title) "
            "VALUES(5,1,7,'private conversation')"
        )
        db.execute(
            "INSERT INTO case_deletion_audit"
            "(id,firm_id,case_id,actor_user_id,actor_name,case_snapshot_json,events_snapshot_json,related_counts_json) "
            "VALUES(6,7,1,1,'reviewer','{}','[]','{}')"
        )
        db.commit()

        targets = (
            ("cases", 1),
            ("docs", 2),
            ("document_extraction_reviews", 4),
            ("research_conversations", 5),
            ("case_deletion_audit", 6),
        )
        for table, row_id in targets:
            with self.subTest(table=table):
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute(
                        f'UPDATE "{table}" SET firm_id=999 WHERE id=?',
                        (row_id,),
                    )
                self.assertEqual(
                    db.execute(
                        f'SELECT firm_id FROM "{table}" WHERE id=?', (row_id,)
                    ).fetchone()[0],
                    7,
                    f"{table} retained an update that escaped the tenant binding",
                )
        db.close()

    def test_original_file_metadata_is_firm_scoped_and_legal_hold_blocks_delete(self):
        db = self.build("firm")
        db.execute("INSERT INTO cases(id,title,firm_id) VALUES(1,'Matter',7)")
        db.execute("INSERT INTO docs(id,case_id,firm_id,name) VALUES(2,1,7,'original.pdf')")
        db.execute(
            "INSERT INTO original_file_objects"
            "(object_id,document_id,firm_id,storage_backend,sha256,byte_size,content_type,state) "
            "VALUES(?,?,?,?,?,?,?,'ready')",
            ("a" * 32, 2, 7, "local", "b" * 64, 123, "application/pdf"),
        )
        db.commit()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "different firm"):
            db.execute("UPDATE original_file_objects SET firm_id=8 WHERE object_id=?", ("a" * 32,))
        db.execute(
            "UPDATE original_file_objects SET legal_hold=1,hold_reason='active litigation',"
            "hold_set_by=42,hold_set_at=datetime('now') WHERE object_id=?",
            ("a" * 32,),
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "legal hold"):
            db.execute("DELETE FROM original_file_objects WHERE object_id=?", ("a" * 32,))
        self.assertEqual(
            tuple(db.execute(
                "SELECT state,legal_hold FROM original_file_objects WHERE object_id=?", ("a" * 32,)
            ).fetchone()),
            ("ready", 1),
        )
        db.close()

    def test_control_plane_catalog_requires_existing_firm_and_blocks_firm_delete(self):
        db = self.build("control_plane")
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO tenant_database_catalog(firm_id,status) VALUES(404,'provisioning')"
            )
        db.execute("INSERT INTO firms(id,name) VALUES(10,'Firm A')")
        db.execute(
            "INSERT INTO tenant_database_catalog(firm_id,status) VALUES(10,'provisioned')"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("DELETE FROM firms WHERE id=10")
        db.close()

    def test_catalog_firm_integrity_migration_fails_closed_on_legacy_orphan(self):
        import shutil
        import tempfile
        from schema_profiles import apply_profile_migrations

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            control = root / "control_plane"
            control.mkdir()
            shutil.copy(ROOT / "control_plane" / "0001_control_plane_catalog.sql", control)
            db = sqlite3.connect(":memory:")
            try:
                apply_profile_migrations(db, "control_plane", root)
                db.execute(
                    "INSERT INTO tenant_database_catalog(firm_id,status) VALUES(404,'failed')"
                )
                db.commit()
                shutil.copy(ROOT / "control_plane" / "0002_catalog_firm_integrity.sql", control)
                with self.assertRaises(sqlite3.IntegrityError):
                    apply_profile_migrations(db, "control_plane", root)
                self.assertIsNotNone(db.execute(
                    "SELECT 1 FROM tenant_database_catalog WHERE firm_id=404"
                ).fetchone())
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM schema_migrations WHERE version=2").fetchone()[0],
                    0,
                )
            finally:
                db.close()

    def test_firm_fts_insert_update_delete(self):
        db = self.build("firm")
        db.execute("INSERT INTO cases(id,title,firm_id) VALUES(1,'matter',7)")
        db.execute("INSERT INTO chunks(id,text,norm,case_id) VALUES(1,'secret firm text','firmsecretterm',1)")
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'firmsecretterm'").fetchone()[0], 1)
        db.execute("UPDATE chunks SET norm='updatedsecretterm' WHERE id=1")
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'firmsecretterm'").fetchone()[0], 0)
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'updatedsecretterm'").fetchone()[0], 1)
        db.execute("DELETE FROM chunks WHERE id=1")
        self.assertEqual(db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'updatedsecretterm'").fetchone()[0], 0)
        db.close()

    def test_corpus_fts_insert_update_delete_and_external_content_integrity(self):
        db = self.build("legal_corpus")
        db.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("fts-source", "Test authority", "https://example.test/source"),
        )
        db.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type) "
            "VALUES(?,?,?,?)",
            ("fts-doc", "fts-source", "Test legal document", "statute"),
        )
        db.execute(
            "INSERT INTO legal_document_versions(version_id,document_id,version_label,source_url) "
            "VALUES(?,?,?,?)",
            (1, "fts-doc", "initial", "https://example.test/source/version-1"),
        )
        db.execute(
            "INSERT INTO chunks(id,text,norm,document_version_id) VALUES(?,?,?,?)",
            (1, "corpus private term", "corpusinitialterm", 1),
        )
        self.assertEqual(
            db.execute("SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'corpusinitialterm'").fetchone()[0],
            1,
        )
        db.execute("INSERT INTO chunks_fts(chunks_fts,rank) VALUES('integrity-check',1)")

        db.execute("UPDATE chunks SET norm='corpusupdatedterm' WHERE id=1")
        self.assertEqual(
            db.execute("SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'corpusinitialterm'").fetchone()[0],
            0,
        )
        self.assertEqual(
            db.execute("SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'corpusupdatedterm'").fetchone()[0],
            1,
        )
        db.execute("INSERT INTO chunks_fts(chunks_fts,rank) VALUES('integrity-check',1)")

        db.execute("DELETE FROM chunks WHERE id=1")
        self.assertEqual(
            db.execute("SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'corpusupdatedterm'").fetchone()[0],
            0,
        )
        db.execute("INSERT INTO chunks_fts(chunks_fts,rank) VALUES('integrity-check',1)")
        db.close()

    def test_two_firm_databases_do_not_share_search_content(self):
        firm_a, firm_b = self.build("firm"), self.build("firm")
        firm_a.execute("INSERT INTO cases(id,title,firm_id) VALUES(1,'A',7)")
        firm_b.execute("INSERT INTO cases(id,title,firm_id) VALUES(1,'B',7)")
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
        with self.assertRaisesRegex(sqlite3.IntegrityError, "review firm scope does not match tenant database"):
            db.execute("UPDATE document_extraction_reviews SET firm_id=8 WHERE id=1")
        # Parent mutations must not invalidate already-valid child relationships.
        with self.assertRaisesRegex(sqlite3.IntegrityError, "document child scope mismatch"):
            db.execute("UPDATE docs SET case_id=2 WHERE id=10")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "document (child scope|case/firm scope mismatch|firm scope does not match tenant database)"):
            db.execute("UPDATE docs SET firm_id=8 WHERE id=10")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "case firm scope (mismatch|does not match tenant database)"):
            db.execute("UPDATE cases SET firm_id=8 WHERE id=1")
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

    def test_parent_scope_migration_fails_closed_on_existing_firm_mismatch(self):
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            firm = root / "firm"
            firm.mkdir()
            shutil.copy(ROOT / "firm" / "0001_firm_matter_foundation.sql", firm)
            shutil.copy(ROOT / "firm" / "0002_enforce_document_review_scope.sql", firm)
            db = sqlite3.connect(":memory:")
            try:
                self.assertEqual(apply_profile_migrations(db, "firm", root), [1, 2])
                db.execute("INSERT INTO cases(id,title,firm_id) VALUES(1,'Matter A',7)")
                db.execute("INSERT INTO docs(id,case_id,firm_id,name) VALUES(10,1,8,'wrong-firm-doc')")
                db.commit()
                shutil.copy(ROOT / "firm" / "0003_preserve_parent_scope.sql", firm)
                with self.assertRaises(sqlite3.IntegrityError):
                    apply_profile_migrations(db, "firm", root)
                self.assertIsNotNone(db.execute("SELECT 1 FROM docs WHERE id=10").fetchone())
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM schema_migrations WHERE version=3").fetchone()[0],
                    0,
                )
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
        db.execute("INSERT INTO cases(id,title,firm_id) VALUES(7,'test',7)")
        db.execute("INSERT INTO notes(case_id,text) VALUES(7,'note')")
        db.execute("DELETE FROM cases WHERE id=7")
        self.assertEqual(db.execute("SELECT count(*) FROM notes").fetchone()[0], 0)
        db.close()

    def test_control_plane_global_identity_and_membership_constraints(self):
        db = self.build("control_plane")
        db.execute("INSERT INTO firms(id,name) VALUES(10,'Firm A')")
        db.execute("INSERT INTO firms(id,name) VALUES(20,'Firm B')")
        db.execute("""INSERT INTO users
            (id,name,email_display,email_normalized,password_hash)
            VALUES(1,'Lawyer','Lawyer@Example.com','lawyer@example.com','test-hash')""")
        # A global identity can have separate memberships in multiple firms.
        db.execute("""INSERT INTO firm_memberships(user_id,firm_id,firm_role,status)
            VALUES(1,10,'lawyer','active')""")
        db.execute("""INSERT INTO firm_memberships(user_id,firm_id,firm_role,status)
            VALUES(1,20,'admin','active')""")
        self.assertEqual(
            db.execute("SELECT COUNT(*) FROM firm_memberships WHERE user_id=1").fetchone()[0],
            2,
        )
        # The canonical normalized email is globally unique, not per firm.
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("""INSERT INTO users
                (id,name,email_display,email_normalized,password_hash)
                VALUES(2,'Another','LAWYER@example.com','LAWYER@example.com','test-hash')""")
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("""INSERT INTO firm_memberships(user_id,firm_id,firm_role,status)
                VALUES(1,10,'lawyer','active')""")
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("""INSERT INTO firm_memberships(user_id,firm_id,firm_role,status)
                VALUES(1,999,'lawyer','active')""")
        db.close()

    def test_platform_roles_are_separate_from_firm_memberships(self):
        db = self.build("control_plane")
        db.execute("""INSERT INTO users
            (id,name,email_display,email_normalized,password_hash)
            VALUES(1,'Reviewer','reviewer@example.com','reviewer@example.com','test-hash')""")
        db.execute("""INSERT INTO user_platform_roles(user_id,role_name)
            VALUES(1,'platform_reviewer')""")
        self.assertEqual(
            db.execute("SELECT role_name FROM user_platform_roles WHERE user_id=1").fetchone()[0],
            "platform_reviewer",
        )
        self.assertEqual(db.execute("SELECT COUNT(*) FROM firm_memberships").fetchone()[0], 0)
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("""INSERT INTO user_platform_roles(user_id,role_name)
                VALUES(1,'firm_admin')""")
        db.close()

    def test_normalized_email_key_uses_shared_unicode_normalizer(self):
        from identity import normalize_email

        first = normalize_email("  Straße@EXAMPLE.COM ")
        second = normalize_email("STRASSE@example.com")
        self.assertEqual(first, second)
        self.assertEqual(
            normalize_email("E\u0301@example.com"),
            normalize_email("É@EXAMPLE.COM"),
        )

        db = self.build("control_plane")
        db.execute("""INSERT INTO users
            (id,name,email_display,email_normalized,password_hash)
            VALUES(1,'First','Straße@EXAMPLE.COM',?,'test-hash')""", (first,))
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("""INSERT INTO users
                (id,name,email_display,email_normalized,password_hash)
                VALUES(2,'Second','STRASSE@example.com',?,'test-hash')""", (second,))
        db.close()

    def test_platform_security_ledger_accepts_identity_creation_event_and_remains_append_only(self):
        db = self.build("control_plane")
        db.execute(
            "INSERT INTO platform_security_events(event_type,detail_json) "
            "VALUES('identity_created_cli','{}')"
        )
        db.commit()
        self.assertEqual(
            db.execute(
                "SELECT event_type FROM platform_security_events"
            ).fetchone()[0],
            "identity_created_cli",
        )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only"):
            db.execute("UPDATE platform_security_events SET detail_json='{}' WHERE id=1")
        db.rollback()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only"):
            db.execute("DELETE FROM platform_security_events WHERE id=1")
        db.rollback()
        db.close()



    def test_identity_event_migration_preserves_existing_platform_audit_rows(self):
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "migrations"
            control_dir = root / "control_plane"
            control_dir.mkdir(parents=True)
            # Build a pre-0006 database. Later migrations must not be marked
            # applied before the identity-event migration they depend on.
            for migration in (ROOT / "control_plane").glob("*.sql"):
                if int(migration.name.split("_", 1)[0]) <= 5:
                    shutil.copyfile(migration, control_dir / migration.name)

            db = sqlite3.connect(":memory:")
            db.row_factory = sqlite3.Row
            apply_profile_migrations(db, "control_plane", root)
            db.execute(
                "INSERT INTO platform_security_events(event_type,detail_json) "
                "VALUES('password_reset_cli','{\"sessions_revoked\":true}')"
            )
            db.commit()

            applied = apply_profile_migrations(db, "control_plane", ROOT)
            self.assertEqual(applied, [6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
            previous = db.execute(
                "SELECT event_type,detail_json FROM platform_security_events"
            ).fetchone()
            self.assertEqual(previous["event_type"], "password_reset_cli")
            self.assertEqual(previous["detail_json"], '{"sessions_revoked":true}')
            self.assertIsNotNone(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='firm_subscriptions'").fetchone())
            self.assertIsNotNone(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='subscription_payment_requests'").fetchone())
            db.execute(
                "INSERT INTO platform_security_events(event_type,detail_json) "
                "VALUES('identity_created_cli','{}')"
            )
            db.commit()
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM platform_security_events").fetchone()[0],
                2,
            )
            db.close()



if __name__ == "__main__":
    unittest.main()
