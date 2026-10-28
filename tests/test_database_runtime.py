import json
import os
import sqlite3
import stat
import shutil
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from database_runtime import DatabaseRuntime, DatabaseRuntimeError
from tenant_context import FirmContextError


class DatabaseRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = DatabaseRuntime(
            self.root / "control.sqlite3",
            self.root / "tenants",
            self.root / "corpus.sqlite3",
        )
        self.runtime.initialize()

    def test_production_runtime_refuses_to_create_missing_database_files(self):
        base = self.root / "production-missing"
        tenant_root = base / "tenants"
        tenant_root.mkdir(parents=True, mode=0o700)
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        control = base / "control.sqlite3"
        corpus = base / "corpus.sqlite3"
        runtime = DatabaseRuntime(control, tenant_root, corpus)
        with patch.dict(os.environ, {"COPILOT_ENV": "production"}):
            with self.assertRaisesRegex(DatabaseRuntimeError, "control-plane database file is missing"):
                runtime.initialize()
        self.assertFalse(control.exists())
        self.assertFalse(corpus.exists())

    def test_production_runtime_validates_all_profiles_before_migrating_any(self):
        base = self.root / "production-partial"
        tenant_root = base / "tenants"
        tenant_root.mkdir(parents=True, mode=0o700)
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        control = base / "control.sqlite3"
        corpus = base / "corpus.sqlite3"
        sqlite3.connect(control).close()
        if os.name == "posix":
            os.chmod(control, 0o600)
        runtime = DatabaseRuntime(control, tenant_root, corpus)
        with patch.dict(os.environ, {"COPILOT_ENV": "production"}):
            with self.assertRaisesRegex(DatabaseRuntimeError, "legal-corpus database file is missing"):
                runtime.initialize()
        self.assertFalse(corpus.exists())
        with sqlite3.connect(control) as db:
            self.assertIsNone(db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            ).fetchone())

    def test_production_runtime_refuses_existing_but_unprovisioned_files(self):
        base = self.root / "production-empty"
        tenant_root = base / "tenants"
        tenant_root.mkdir(parents=True, mode=0o700)
        control = base / "control.sqlite3"
        corpus = base / "corpus.sqlite3"
        sqlite3.connect(control).close()
        sqlite3.connect(corpus).close()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
            os.chmod(control, 0o600)
            os.chmod(corpus, 0o600)
        runtime = DatabaseRuntime(control, tenant_root, corpus)
        with patch.dict(os.environ, {"COPILOT_ENV": "production"}):
            with self.assertRaisesRegex(DatabaseRuntimeError, "not pre-provisioned"):
                runtime.initialize()
        with sqlite3.connect(control) as db:
            self.assertIsNone(db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            ).fetchone())

    def test_production_runtime_refuses_pending_migrations_instead_of_applying_them(self):
        base = self.root / "production-pending"
        migrations_root = base / "migrations"
        shutil.copytree(Path(__file__).resolve().parents[1] / "migrations", migrations_root)
        control = base / "control.sqlite3"
        tenant_root = base / "tenants"
        corpus = base / "corpus.sqlite3"
        development_runtime = DatabaseRuntime(
            control, tenant_root, corpus, migrations_root=migrations_root
        )
        with patch.dict(os.environ, {"COPILOT_ENV": "development"}):
            development_runtime.initialize()
        development_runtime.close_current_thread()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        pending = migrations_root / "control_plane" / "9999_pending_production_test.sql"
        pending.write_text(
            "CREATE TABLE pending_production_test(id INTEGER PRIMARY KEY);",
            encoding="utf-8",
        )
        runtime = DatabaseRuntime(
            control, tenant_root, corpus, migrations_root=migrations_root
        )
        with patch.dict(os.environ, {"COPILOT_ENV": "production"}):
            with self.assertRaisesRegex(DatabaseRuntimeError, "migration history is pending"):
                runtime.initialize()
        with sqlite3.connect(control) as db:
            self.assertIsNone(db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='pending_production_test'"
            ).fetchone())

    def test_production_runtime_refuses_pending_tenant_fleet_migrations(self):
        base = self.root / "production-pending-tenant"
        migrations_root = base / "migrations"
        shutil.copytree(Path(__file__).resolve().parents[1] / "migrations", migrations_root)
        control = base / "control.sqlite3"
        tenant_root = base / "tenants"
        corpus = base / "corpus.sqlite3"
        development_runtime = DatabaseRuntime(
            control, tenant_root, corpus, migrations_root=migrations_root
        )
        with patch.dict(os.environ, {"COPILOT_ENV": "development"}):
            development_runtime.initialize()
            firm_id, tenant_path = development_runtime.provision_firm(
                "Pending Migration Firm"
            )
        development_runtime.close_current_thread()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        pending = migrations_root / "firm" / "9999_pending_tenant_test.sql"
        pending.write_text(
            "CREATE TABLE pending_tenant_test(id INTEGER PRIMARY KEY);",
            encoding="utf-8",
        )
        runtime = DatabaseRuntime(
            control, tenant_root, corpus, migrations_root=migrations_root
        )
        with patch.dict(os.environ, {"COPILOT_ENV": "production"}):
            with self.assertRaisesRegex(DatabaseRuntimeError, "tenant database fleet has pending migrations"):
                runtime.initialize()
        with sqlite3.connect(tenant_path) as db:
            self.assertIsNone(db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='pending_tenant_test'"
            ).fetchone())

    def test_production_runtime_refuses_unreferenced_tenant_database_files(self):
        base = self.root / "production-orphan"
        migrations_root = base / "migrations"
        shutil.copytree(Path(__file__).resolve().parents[1] / "migrations", migrations_root)
        control = base / "control.sqlite3"
        tenant_root = base / "tenants"
        corpus = base / "corpus.sqlite3"
        development_runtime = DatabaseRuntime(
            control, tenant_root, corpus, migrations_root=migrations_root
        )
        with patch.dict(os.environ, {"COPILOT_ENV": "development"}):
            development_runtime.initialize()
            firm_id, _ = development_runtime.provision_firm("Cataloged Firm")
        development_runtime.close_current_thread()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        orphan = tenant_root / f"tenant-{firm_id + 100}-{'a' * 32}.sqlite3"
        orphan.write_bytes(b"unreferenced synthetic file")
        if os.name == "posix":
            os.chmod(orphan, 0o600)
        runtime = DatabaseRuntime(
            control, tenant_root, corpus, migrations_root=migrations_root
        )
        with patch.dict(os.environ, {"COPILOT_ENV": "production"}):
            with self.assertRaisesRegex(DatabaseRuntimeError, "unreferenced database files"):
                runtime.initialize()

    def test_production_runtime_requires_private_tenant_root(self):
        base = self.root / "production-open-root"
        tenant_root = base / "tenants"
        tenant_root.mkdir(parents=True, mode=0o755)
        control = base / "control.sqlite3"
        corpus = base / "corpus.sqlite3"
        sqlite3.connect(control).close()
        sqlite3.connect(corpus).close()
        if os.name == "posix":
            os.chmod(tenant_root, 0o755)
            os.chmod(control, 0o600)
            os.chmod(corpus, 0o600)
        runtime = DatabaseRuntime(control, tenant_root, corpus)
        if os.name == "posix":
            with patch.dict(os.environ, {"COPILOT_ENV": "production"}):
                with self.assertRaisesRegex(DatabaseRuntimeError, "tenant storage root permissions"):
                    runtime.initialize()
        else:
            self.skipTest("POSIX directory permission bits are not portable to this platform")

    def tearDown(self):
        self.runtime.close_current_thread()
        self.temp.cleanup()

    def _identity(self, email="lawyer@example.test"):
        return self.runtime.create_global_identity("Test Lawyer", email, "test-hash")

    def test_global_identity_email_uniqueness_uses_unicode_casefold_and_normalization(self):
        first_id = self.runtime.create_global_identity(
            "First Person", "  Straße@Example.test ", "test-hash"
        )
        row = self.runtime.control_connection().execute(
            "SELECT email_display,email_normalized FROM users WHERE id=?", (first_id,)
        ).fetchone()
        self.assertEqual(row["email_display"], "Straße@Example.test")
        self.assertEqual(row["email_normalized"], "strasse@example.test")
        with self.assertRaises(sqlite3.IntegrityError):
            self.runtime.create_global_identity(
                "Duplicate Person", "STRASSE@example.test", "other-hash"
            )
        self.runtime.create_global_identity("Composed Unicode", "é@example.test", "test-hash")
        with self.assertRaises(sqlite3.IntegrityError):
            self.runtime.create_global_identity(
                "Unicode Normalization Duplicate", "e\u0301@example.test", "other-hash"
            )

    def test_all_database_profiles_use_wal_for_concurrent_readers_and_writers(self):
        for path in (self.runtime.paths.control_plane, self.runtime.paths.legal_corpus):
            connection = sqlite3.connect(str(path))
            try:
                self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0].lower(), "wal")
            finally:
                connection.close()

        firm_id, _ = self.runtime.provision_firm("WAL Concurrency Firm")
        context = self.runtime.resolve_context(
            self.runtime.create_initial_firm_owner(firm_id, "WAL Owner", "wal-owner@example.test", "test-hash"),
            firm_id,
        )
        tenant = self.runtime.firm_connection(context)
        self.assertEqual(tenant.execute("PRAGMA journal_mode").fetchone()[0].lower(), "wal")

    def test_new_control_and_corpus_files_have_restrictive_permissions(self):
        if os.name != "posix":
            self.skipTest("POSIX mode bits are not portable to this platform")
        for path in (self.runtime.paths.control_plane, self.runtime.paths.legal_corpus):
            self.assertTrue(path.is_file())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_control_plane_creation_fails_closed_when_permissions_cannot_be_enforced(self):
        control = self.root / "permission-failure" / "control.sqlite3"
        corpus = self.root / "permission-failure" / "corpus.sqlite3"
        runtime = DatabaseRuntime(control, self.root / "permission-failure" / "tenants", corpus)
        with patch("database_runtime.os.chmod", side_effect=PermissionError("simulated chmod failure")):
            with self.assertRaisesRegex(DatabaseRuntimeError, "restrictive permissions"):
                runtime.initialize()
        self.assertFalse(control.exists())
        self.assertFalse(Path(str(control) + "-wal").exists())
        self.assertFalse(Path(str(control) + "-shm").exists())

    def test_control_connection_is_revoked_when_database_permissions_become_unsafe(self):
        if os.name != "posix":
            self.skipTest("POSIX mode bits are not portable to this platform")
        connection = self.runtime.control_connection()
        os.chmod(self.runtime.paths.control_plane, 0o644)
        try:
            with self.assertRaisesRegex(DatabaseRuntimeError, "group/other access"):
                self.runtime.control_connection()
            with self.assertRaises(sqlite3.ProgrammingError):
                connection.execute("SELECT 1")
        finally:
            os.chmod(self.runtime.paths.control_plane, 0o600)

    def test_control_connection_is_revoked_when_database_file_is_replaced(self):
        connection = self.runtime.control_connection()
        replacement = self.root / "replacement-control.sqlite3"
        with sqlite3.connect(replacement) as db:
            db.execute("CREATE TABLE replacement_sentinel(value TEXT)")
            db.execute("INSERT INTO replacement_sentinel VALUES('not the configured control plane')")
        if os.name == "posix":
            os.chmod(replacement, 0o600)
        os.replace(replacement, self.runtime.paths.control_plane)

        with self.assertRaisesRegex(DatabaseRuntimeError, "control-plane database file was replaced"):
            self.runtime.control_connection()
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")

    def test_corpus_connection_is_revoked_when_database_file_is_replaced(self):
        connection = self.runtime.legal_corpus_connection()
        replacement = self.root / "replacement-corpus.sqlite3"
        with sqlite3.connect(replacement) as db:
            db.execute("CREATE TABLE replacement_sentinel(value TEXT)")
            db.execute("INSERT INTO replacement_sentinel VALUES('not the configured legal corpus')")
        if os.name == "posix":
            os.chmod(replacement, 0o600)
        os.replace(replacement, self.runtime.paths.legal_corpus)

        with self.assertRaisesRegex(DatabaseRuntimeError, "legal-corpus database file was replaced"):
            self.runtime.legal_corpus_connection()
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")

    def test_corpus_connection_is_revoked_when_sidecar_becomes_a_symlink(self):
        if not hasattr(os, "symlink"):
            self.skipTest("Symbolic links are not supported")
        connection = self.runtime.legal_corpus_connection()
        sidecar = Path(str(self.runtime.paths.legal_corpus) + "-wal")
        target = self.root / "outside-wal"
        target.write_bytes(b"not a database sidecar")
        try:
            sidecar.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"Symbolic-link creation is unavailable: {exc}")
        try:
            with self.assertRaisesRegex(DatabaseRuntimeError, "sidecar must not be a symlink"):
                self.runtime.legal_corpus_connection()
            with self.assertRaises(sqlite3.ProgrammingError):
                connection.execute("SELECT 1")
        finally:
            sidecar.unlink(missing_ok=True)

    def test_firm_connection_attaches_control_and_corpus_read_only(self):
        user_id = self._identity("readonly-attachment@example.test")
        firm_id, _ = self.runtime.provision_firm("Read-only Attachments")
        self.runtime.create_firm_membership(user_id, firm_id, "admin")
        context = self.runtime.resolve_context(user_id, firm_id)
        tenant = self.runtime.firm_connection(context)

        control = self.runtime.control_connection()
        corpus = self.runtime.legal_corpus_connection()
        corpus.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("readonly-attachment-source", "Original Authority", "https://example.test/source"),
        )
        corpus.commit()

        with self.assertRaisesRegex(sqlite3.OperationalError, "readonly database"):
            tenant.execute("UPDATE control.users SET status='disabled' WHERE id=?", (user_id,))
        with self.assertRaisesRegex(sqlite3.OperationalError, "readonly database"):
            tenant.execute(
                "UPDATE corpus.legal_sources SET authority='Tampered' WHERE source_id=?",
                ("readonly-attachment-source",),
            )

        self.assertEqual(
            control.execute("SELECT status FROM users WHERE id=?", (user_id,)).fetchone()["status"],
            "active",
        )
        self.assertEqual(
            corpus.execute(
                "SELECT authority FROM legal_sources WHERE source_id=?",
                ("readonly-attachment-source",),
            ).fetchone()["authority"],
            "Original Authority",
        )

    def test_firm_connection_revalidates_attached_corpus_even_when_tenant_is_cached(self):
        if os.name != "posix":
            self.skipTest("POSIX mode bits are not portable to this platform")
        user_id = self._identity()
        firm_id, _ = self.runtime.provision_firm("Attached Corpus Validation")
        self.runtime.create_firm_membership(user_id, firm_id, "admin")
        context = self.runtime.resolve_context(user_id, firm_id)
        self.runtime.firm_connection(context)

        os.chmod(self.runtime.paths.legal_corpus, 0o644)
        try:
            with self.assertRaisesRegex(DatabaseRuntimeError, "legal-corpus database file permissions"):
                self.runtime.firm_connection(context)
        finally:
            os.chmod(self.runtime.paths.legal_corpus, 0o600)

    def test_separate_profile_fresh_install_and_restart_preserve_data(self):
        firm_id, _ = self.runtime.provision_firm("Restart Firm")
        user_id = self.runtime.create_initial_firm_owner(
            firm_id, "Restart Owner", "restart-owner@example.test", "test-hash"
        )
        context = self.runtime.resolve_context(user_id, firm_id)
        firm_db = self.runtime.firm_connection(context)
        case_id = firm_db.execute(
            "INSERT INTO cases(title,firm_id) VALUES(?,?)",
            ("Restart sentinel matter", firm_id),
        ).lastrowid
        firm_db.commit()
        corpus = self.runtime.legal_corpus_connection()
        corpus.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("restart-source", "Restart source", "https://example.test/source"),
        )
        corpus.commit()
        self.runtime.close_current_thread()

        restarted = DatabaseRuntime(
            self.root / "control.sqlite3",
            self.root / "tenants",
            self.root / "corpus.sqlite3",
        )
        try:
            restarted.initialize()
            restarted_context = restarted.resolve_context(user_id, firm_id)
            restarted_firm_db = restarted.firm_connection(restarted_context)
            self.assertEqual(
                restarted_firm_db.execute(
                    "SELECT title FROM cases WHERE id=?", (case_id,)
                ).fetchone()[0],
                "Restart sentinel matter",
            )
            self.assertEqual(
                restarted.legal_corpus_connection().execute(
                    "SELECT authority FROM legal_sources WHERE source_id='restart-source'"
                ).fetchone()[0],
                "Restart source",
            )
            self.assertEqual(
                restarted.control_connection().execute(
                    "SELECT status FROM firms WHERE id=?", (firm_id,)
                ).fetchone()[0],
                "active",
            )
        finally:
            restarted.close_current_thread()

    def test_missing_provisioned_tenant_database_fails_closed_without_recreating_file(self):
        user_id = self._identity("missing-tenant@example.test")
        firm_id, database_path = self.runtime.provision_firm("Missing Tenant Database")
        self.runtime.create_firm_membership(user_id, firm_id, "admin")
        context = self.runtime.resolve_context(user_id, firm_id)
        self.runtime.firm_connection(context)
        self.runtime.close_current_thread()

        database_path.unlink()
        self.assertFalse(database_path.exists())
        with self.assertRaisesRegex(DatabaseRuntimeError, "no shared fallback is permitted"):
            self.runtime.firm_connection(context)
        self.assertFalse(database_path.exists(), "runtime must not recreate a missing tenant database")
        catalog_row = self.runtime.control_connection().execute(
            "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
        ).fetchone()
        self.assertEqual(catalog_row["status"], "provisioned")

    def test_profiles_are_separate_and_firm_databases_are_distinct(self):
        user_id = self._identity()
        firm_a, path_a = self.runtime.provision_firm("Firm A")
        firm_b, path_b = self.runtime.provision_firm("Firm B")
        self.runtime.create_firm_membership(user_id, firm_a, "admin")
        self.runtime.create_firm_membership(user_id, firm_b, "lawyer")

        context_a = self.runtime.resolve_context(user_id, firm_a)
        context_b = self.runtime.resolve_context(user_id, firm_b)
        db_a = self.runtime.firm_connection(context_a)
        db_b = self.runtime.firm_connection(context_b)
        db_a.execute("INSERT INTO cases(title,firm_id) VALUES('Only A',?)", (firm_a,))
        db_a.commit()

        self.assertNotEqual(path_a, path_b)
        self.assertEqual(db_a.execute("SELECT title FROM cases").fetchall()[0][0], "Only A")
        self.assertEqual(db_b.execute("SELECT COUNT(*) FROM cases").fetchone()[0], 0)

        control = self.runtime.control_connection()
        corpus = self.runtime.legal_corpus_connection()
        self.assertEqual(
            control.execute("SELECT profile FROM database_profile").fetchone()[0],
            "control_plane",
        )
        self.assertEqual(
            corpus.execute("SELECT profile FROM database_profile").fetchone()[0],
            "legal_corpus",
        )
        self.assertEqual(
            db_a.execute("SELECT profile FROM database_profile").fetchone()[0],
            "firm",
        )
        firm_tables = {
            row[0] for row in db_a.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        corpus_tables = {
            row[0] for row in corpus.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        self.assertNotIn("firm_memberships", firm_tables)
        self.assertNotIn("cases", corpus_tables)
        self.assertEqual(
            db_a.execute("SELECT name FROM users WHERE id=? AND firm_id=?", (user_id, firm_a)).fetchone()[0],
            "Test Lawyer",
        )
        self.assertEqual(
            db_a.execute("SELECT COUNT(*) FROM users WHERE id=?", (user_id,)).fetchone()[0],
            1,
        )

    def test_firm_row_ids_must_match_immutable_database_binding(self):
        user_id = self._identity("scope-owner@example.test")
        firm_a, _ = self.runtime.provision_firm("Scope Firm A")
        firm_b, _ = self.runtime.provision_firm("Scope Firm B")
        self.runtime.create_firm_membership(user_id, firm_a, "admin")
        context_a = self.runtime.resolve_context(user_id, firm_a)
        db = self.runtime.firm_connection(context_a)
        case_id = db.execute(
            "INSERT INTO cases(title,firm_id) VALUES('Scoped matter',?)", (firm_a,)
        ).lastrowid
        db.commit()

        with self.assertRaisesRegex(sqlite3.IntegrityError, "case firm scope"):
            db.execute(
                "INSERT INTO cases(title,firm_id) VALUES('Wrong tenant',?)", (firm_b,)
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "document (case/firm scope|firm scope)"):
            db.execute(
                "INSERT INTO docs(case_id,name,firm_id) VALUES(?,?,?)",
                (case_id, "wrong-tenant.pdf", firm_b),
            )
        conversation_id = db.execute(
            "INSERT INTO research_conversations(user_id,firm_id,title) VALUES(?,?,?)",
            (user_id, firm_a, "valid tenant"),
        ).lastrowid
        with self.assertRaisesRegex(sqlite3.IntegrityError, "research conversation firm scope"):
            db.execute(
                "INSERT INTO research_conversations(user_id,firm_id,title) VALUES(?,?,?)",
                (user_id, firm_b, "wrong tenant"),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "research conversation firm scope"):
            db.execute(
                "UPDATE research_conversations SET firm_id=? WHERE id=?",
                (firm_b, conversation_id),
            )
        audit_id = db.execute(
            "INSERT INTO case_deletion_audit(firm_id,case_id,actor_user_id,actor_name,"
            "case_snapshot_json,events_snapshot_json,related_counts_json) "
            "VALUES(?,?,?,?,?,?,?)",
            (firm_a, case_id, user_id, "actor", "{}", "[]", "{}"),
        ).lastrowid
        with self.assertRaisesRegex(sqlite3.IntegrityError, "case deletion audit firm scope"):
            db.execute(
                "INSERT INTO case_deletion_audit(firm_id,case_id,actor_user_id,actor_name,"
                "case_snapshot_json,events_snapshot_json,related_counts_json) "
                "VALUES(?,?,?,?,?,?,?)",
                (firm_b, case_id, user_id, "actor", "{}", "[]", "{}"),
            )
        with self.assertRaisesRegex(sqlite3.IntegrityError, "case deletion audit firm scope does not match tenant database"):
            db.execute(
                "UPDATE case_deletion_audit SET firm_id=? WHERE id=?",
                (firm_b, audit_id),
            )
        db.rollback()
        self.assertEqual(
            db.execute("SELECT firm_id FROM cases WHERE id=?", (case_id,)).fetchone()[0],
            firm_a,
        )

    def test_catalog_connection_failure_does_not_strand_firm_in_provisioning(self):
        with patch.object(
            self.runtime,
            "_new_catalog_connection",
            side_effect=sqlite3.OperationalError("simulated catalog connection failure"),
        ):
            with self.assertRaisesRegex(sqlite3.OperationalError, "simulated catalog connection failure"):
                self.runtime.provision_firm("Catalog Connection Failure")

        control = self.runtime.control_connection()
        firm = control.execute(
            "SELECT id,status FROM firms WHERE name='Catalog Connection Failure'"
        ).fetchone()
        self.assertIsNotNone(firm)
        self.assertEqual(firm["status"], "disabled")
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM tenant_database_catalog WHERE firm_id=?", (firm["id"],)
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            list(self.runtime.paths.tenant_root.glob("tenant-*.sqlite3")), []
        )

    def test_provisioning_audit_failure_disables_firm_and_catalog_without_activating_tenant(self):
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_firm_provision_audit
            BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='firm_provisioned'
            BEGIN SELECT RAISE(ABORT, 'simulated provisioning audit failure'); END
        """)
        control.commit()

        with self.assertRaisesRegex(sqlite3.IntegrityError, "simulated provisioning audit failure"):
            self.runtime.provision_firm("Audit Failure Firm")

        firm = control.execute(
            "SELECT id,status FROM firms WHERE name='Audit Failure Firm'"
        ).fetchone()
        self.assertIsNotNone(firm)
        self.assertEqual(firm["status"], "disabled")
        catalog = control.execute(
            "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
            (firm["id"],),
        ).fetchone()
        self.assertIsNotNone(catalog)
        self.assertEqual(catalog["status"], "disabled")
        tenant_path = self.runtime.paths.tenant_root / catalog["database_file"]
        self.assertTrue(tenant_path.is_file(), "failed provisioning data must remain for explicit review")
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events WHERE firm_id=? AND event_type='firm_provisioned'",
                (firm["id"],),
            ).fetchone()[0],
            0,
        )

    def test_reconcile_interrupted_fileless_provisioning_to_retryable_failure(self):
        control = self.runtime.control_connection()
        firm_id = int(control.execute(
            "INSERT INTO firms(name,status) VALUES('Interrupted Provisioning','provisioning')"
        ).lastrowid)
        control.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) "
            "VALUES(?,NULL,'provisioning')",
            (firm_id,),
        )
        control.commit()

        self.runtime.reconcile_interrupted_firm_provisioning(
            firm_id,
            reason="deployment host restarted during tenant initialization",
            operator_reference="incident-123",
            change_reference="change-456",
        )

        firm = control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()
        catalog = control.execute(
            "SELECT status,database_file,last_error_code FROM tenant_database_catalog WHERE firm_id=?",
            (firm_id,),
        ).fetchone()
        self.assertEqual(firm["status"], "disabled")
        self.assertEqual(catalog["status"], "failed")
        self.assertIsNone(catalog["database_file"])
        self.assertEqual(catalog["last_error_code"], "interrupted_provisioning_reconciled")
        event = control.execute(
            "SELECT detail_json FROM platform_security_events "
            "WHERE firm_id=? AND event_type='firm_provisioning_reconciled_failed'",
            (firm_id,),
        ).fetchone()
        self.assertIsNotNone(event)
        detail = json.loads(event["detail_json"])
        self.assertEqual(detail["operator_reference"], "incident-123")
        self.assertEqual(detail["change_reference"], "change-456")
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events "
                "WHERE firm_id=? AND event_type='firm_provisioning_reconciled_failed'",
                (firm_id,),
            ).fetchone()[0],
            1,
        )
        tenant_path = self.runtime.retry_failed_firm_provisioning(
            firm_id,
            reason="retry after file-less interrupted provisioning was reconciled",
            operator_reference="operator-retry-after-reconcile",
            change_reference="change-retry-after-reconcile",
        )
        self.assertTrue(tenant_path.is_file())
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "active",
        )
        self.assertEqual(
            control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
            ).fetchone()[0],
            "provisioned",
        )

    def test_reconcile_interrupted_provisioning_refuses_any_existing_database_file(self):
        control = self.runtime.control_connection()
        firm_id = int(control.execute(
            "INSERT INTO firms(name,status) VALUES('Interrupted With File','provisioning')"
        ).lastrowid)
        filename = f"tenant-{firm_id}-{'a' * 32}.sqlite3"
        control.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) "
            "VALUES(?,?,'provisioning')",
            (firm_id, filename),
        )
        control.commit()
        path = self.runtime.paths.tenant_root / filename
        path.write_bytes(b"ambiguous partial database")
        with self.assertRaisesRegex(DatabaseRuntimeError, "database or sidecar exists"):
            self.runtime.reconcile_interrupted_firm_provisioning(
                firm_id,
                reason="operator is checking a crash recovery",
                operator_reference="incident-789",
                change_reference="change-012",
            )
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "provisioning",
        )
        self.assertEqual(
            control.execute(
                "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
                (firm_id,),
            ).fetchone()["status"],
            "provisioning",
        )
        self.assertTrue(path.is_file())

    def test_reconcile_interrupted_provisioning_rejects_mismatched_states_and_invalid_mapping(self):
        control = self.runtime.control_connection()
        cases = [
            ("Active firm", "active", "provisioning", None),
            ("Failed catalog", "provisioning", "failed", None),
            ("Invalid mapping", "provisioning", "provisioning", "../another-tenant.sqlite3"),
        ]
        firm_ids = []
        for name, firm_status, catalog_status, filename in cases:
            firm_id = int(control.execute(
                "INSERT INTO firms(name,status) VALUES(?,?)", (name, firm_status)
            ).lastrowid)
            control.execute(
                "INSERT INTO tenant_database_catalog(firm_id,database_file,status) VALUES(?,?,?)",
                (firm_id, filename, catalog_status),
            )
            firm_ids.append(firm_id)
        control.commit()

        for firm_id in firm_ids:
            with self.subTest(firm_id=firm_id):
                with self.assertRaises(DatabaseRuntimeError):
                    self.runtime.reconcile_interrupted_firm_provisioning(
                        firm_id,
                        reason="reject inconsistent state during lifecycle review",
                        operator_reference="incident-state-matrix",
                        change_reference="change-state-matrix",
                    )
                self.assertEqual(
                    control.execute(
                        "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
                    ).fetchone()[0],
                    cases[firm_ids.index(firm_id)][2],
                )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events "
                "WHERE event_type='firm_provisioning_reconciled_failed'"
            ).fetchone()[0],
            0,
        )

    def test_reconcile_interrupted_provisioning_refuses_existing_memberships_or_invitations(self):
        control = self.runtime.control_connection()
        user_id = self.runtime.create_global_identity(
            "Provisioning History User", "provisioning-history-user@example.test", "test-hash"
        )
        firm_with_membership = int(control.execute(
            "INSERT INTO firms(name,status) VALUES('Interrupted With Membership','provisioning')"
        ).lastrowid)
        control.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) "
            "VALUES(?,NULL,'provisioning')",
            (firm_with_membership,),
        )
        control.execute(
            "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status) "
            "VALUES(?,?,'lawyer','suspended')",
            (user_id, firm_with_membership),
        )
        firm_with_invitation = int(control.execute(
            "INSERT INTO firms(name,status) VALUES('Interrupted With Invitation','provisioning')"
        ).lastrowid)
        control.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) "
            "VALUES(?,NULL,'provisioning')",
            (firm_with_invitation,),
        )
        control.execute(
            "INSERT INTO identity_invitations("
            "firm_id,email_normalized,email_display,invited_role,token_hash,invited_by_user_id,"
            "created_at,expires_at,status,updated_at"
            ") VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                firm_with_invitation,
                "interrupted-invite@example.test",
                "interrupted-invite@example.test",
                "lawyer",
                "b" * 64,
                user_id,
                100,
                200,
                "sent",
                100,
            ),
        )
        control.commit()

        for firm_id in (firm_with_membership, firm_with_invitation):
            with self.subTest(firm_id=firm_id):
                with self.assertRaisesRegex(DatabaseRuntimeError, "existing memberships or invitations"):
                    self.runtime.reconcile_interrupted_firm_provisioning(
                        firm_id,
                        reason="state with identity history requires manual review",
                        operator_reference="incident-identity-history",
                        change_reference="change-identity-history",
                    )
                self.assertEqual(
                    control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
                    "provisioning",
                )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events "
                "WHERE event_type='firm_provisioning_reconciled_failed'"
            ).fetchone()[0],
            0,
        )

    def test_reconcile_interrupted_provisioning_audit_failure_rolls_back_lifecycle_changes(self):
        control = self.runtime.control_connection()
        firm_id = int(control.execute(
            "INSERT INTO firms(name,status) VALUES('Interrupted Audit Failure','provisioning')"
        ).lastrowid)
        control.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) "
            "VALUES(?,NULL,'provisioning')",
            (firm_id,),
        )
        control.execute(
            "CREATE TRIGGER reject_interrupted_reconcile_audit "
            "BEFORE INSERT ON platform_security_events "
            "WHEN NEW.event_type='firm_provisioning_reconciled_failed' "
            "BEGIN SELECT RAISE(ABORT, 'injected reconcile audit failure'); END"
        )
        control.commit()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected reconcile audit failure"):
            self.runtime.reconcile_interrupted_firm_provisioning(
                firm_id,
                reason="verify lifecycle changes require an audit record",
                operator_reference="incident-audit",
                change_reference="change-audit",
            )
        control.execute("DROP TRIGGER reject_interrupted_reconcile_audit")
        control.commit()
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "provisioning",
        )
        self.assertEqual(
            control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
            ).fetchone()[0],
            "provisioning",
        )

    def test_failed_firm_provisioning_can_be_retried_with_audited_operator_references(self):
        with patch.object(
            self.runtime,
            "_initialize_firm_database",
            side_effect=RuntimeError("simulated tenant schema initialization failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "simulated tenant schema initialization failure"):
                self.runtime.provision_firm("Retryable Failed Firm")

        control = self.runtime.control_connection()
        firm = control.execute(
            "SELECT id,status FROM firms WHERE name='Retryable Failed Firm'"
        ).fetchone()
        self.assertIsNotNone(firm)
        firm_id = int(firm["id"])
        self.assertEqual(firm["status"], "disabled")
        catalog = control.execute(
            "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
            (firm_id,),
        ).fetchone()
        self.assertEqual(catalog["status"], "failed")
        self.assertIsNone(catalog["database_file"])
        self.assertEqual(
            list(self.runtime.paths.tenant_root.glob(f"tenant-{firm_id}-*.sqlite3")), []
        )

        path = self.runtime.retry_failed_firm_provisioning(
            firm_id,
            reason="recover after transient schema initializer failure",
            operator_reference="operator-ticket-123",
            change_reference="change-window-456",
        )
        self.assertTrue(path.is_file())
        firm = control.execute(
            "SELECT status FROM firms WHERE id=?", (firm_id,)
        ).fetchone()
        self.assertEqual(firm["status"], "active")
        catalog = control.execute(
            "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
            (firm_id,),
        ).fetchone()
        self.assertEqual(catalog["status"], "provisioned")
        self.assertEqual(catalog["database_file"], path.name)
        event = control.execute(
            "SELECT detail_json FROM platform_security_events "
            "WHERE firm_id=? AND event_type='firm_provisioning_retried'",
            (firm_id,),
        ).fetchone()
        self.assertIsNotNone(event)
        detail = json.loads(event["detail_json"])
        self.assertEqual(detail["operator_reference"], "operator-ticket-123")
        self.assertEqual(detail["change_reference"], "change-window-456")
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events "
                "WHERE firm_id=? AND event_type='firm_provisioned'",
                (firm_id,),
            ).fetchone()[0],
            0,
        )

    def test_failed_recovery_keeps_catalog_retryable_for_another_operator_attempt(self):
        with patch.object(
            self.runtime,
            "_initialize_firm_database",
            side_effect=RuntimeError("initial schema initialization failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "initial schema initialization failure"):
                self.runtime.provision_firm("Repeatable Recovery Failure")
        control = self.runtime.control_connection()
        firm_id = int(control.execute(
            "SELECT id FROM firms WHERE name='Repeatable Recovery Failure'"
        ).fetchone()[0])

        with patch.object(
            self.runtime,
            "_initialize_firm_database",
            side_effect=RuntimeError("recovery schema initialization failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "recovery schema initialization failure"):
                self.runtime.retry_failed_firm_provisioning(
                    firm_id,
                    reason="first recovery attempt failed during schema initialization",
                    operator_reference="operator-ticket-retry-1",
                    change_reference="change-retry-1",
                )

        firm = control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()
        catalog = control.execute(
            "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
            (firm_id,),
        ).fetchone()
        self.assertEqual(firm["status"], "disabled")
        self.assertEqual(catalog["status"], "failed")
        self.assertIsNone(catalog["database_file"])
        self.assertEqual(list(self.runtime.paths.tenant_root.glob(f"tenant-{firm_id}-*.sqlite3")), [])

        path = self.runtime.retry_failed_firm_provisioning(
            firm_id,
            reason="retry after the second schema initialization failure was diagnosed",
            operator_reference="operator-ticket-retry-2",
            change_reference="change-retry-2",
        )
        self.assertTrue(path.is_file())
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "active",
        )
        self.assertEqual(
            control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
            ).fetchone()[0],
            "provisioned",
        )

    def test_recovery_audit_failure_disables_but_retains_successfully_provisioned_database(self):
        with patch.object(
            self.runtime,
            "_initialize_firm_database",
            side_effect=RuntimeError("initial schema initialization failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "initial schema initialization failure"):
                self.runtime.provision_firm("Recovery Audit Failure")
        control = self.runtime.control_connection()
        firm_id = int(control.execute(
            "SELECT id FROM firms WHERE name='Recovery Audit Failure'"
        ).fetchone()[0])
        control.execute(
            "CREATE TRIGGER test_fail_provisioning_retry_audit "
            "BEFORE INSERT ON platform_security_events "
            "WHEN NEW.event_type='firm_provisioning_retried' "
            "BEGIN SELECT RAISE(ABORT, 'injected recovery audit failure'); END"
        )
        control.commit()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected recovery audit failure"):
            self.runtime.retry_failed_firm_provisioning(
                firm_id,
                reason="test that audit failure prevents activation",
                operator_reference="operator-ticket-audit",
                change_reference="change-audit",
            )
        control.execute("DROP TRIGGER test_fail_provisioning_retry_audit")
        control.commit()
        firm = control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()
        catalog = control.execute(
            "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
            (firm_id,),
        ).fetchone()
        self.assertEqual(firm["status"], "disabled")
        self.assertEqual(catalog["status"], "disabled")
        self.assertTrue(catalog["database_file"])
        retained_path = self.runtime.paths.tenant_root / catalog["database_file"]
        self.assertTrue(retained_path.is_file())
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events "
                "WHERE firm_id=? AND event_type='firm_provisioning_retried'",
                (firm_id,),
            ).fetchone()[0],
            0,
        )

    def test_failed_firm_provisioning_retry_refuses_existing_membership_history(self):
        control = self.runtime.control_connection()
        firm_id = int(control.execute(
            "INSERT INTO firms(name,status) VALUES('Failed Firm With Membership','disabled')"
        ).lastrowid)
        control.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) VALUES(?,NULL,'failed')",
            (firm_id,),
        )
        user_id = self.runtime.create_global_identity(
            "Preexisting Member", "preexisting-member@example.test", "test-hash"
        )
        control.execute(
            "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status) "
            "VALUES(?,?,'lawyer','suspended')",
            (user_id, firm_id),
        )
        control.commit()
        with self.assertRaisesRegex(DatabaseRuntimeError, "no existing memberships or invitations"):
            self.runtime.retry_failed_firm_provisioning(
                firm_id,
                reason="must not reactivate a firm with prior identity links",
                operator_reference="operator-ticket-111",
                change_reference="change-222",
            )
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "disabled",
        )
        self.assertEqual(
            control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
            ).fetchone()[0],
            "failed",
        )

    def test_failed_firm_provisioning_retry_rejects_nonfailed_lifecycle_states(self):
        firm_id, _ = self.runtime.provision_firm("Already Provisioned Firm")
        with self.assertRaisesRegex(DatabaseRuntimeError, "Only a disabled firm"):
            self.runtime.retry_failed_firm_provisioning(
                firm_id,
                reason="must not retry",
                operator_reference="operator-ticket-789",
                change_reference="change-window-999",
            )

    def test_disabled_firm_invitation_offboarding_revokes_and_audits_active_tokens(self):
        firm_id, _ = self.runtime.provision_firm("Invitation Offboarding Firm")
        user_id = self.runtime.create_global_identity(
            "Invitation Offboarding Owner", "invitation-offboarding-owner@example.test", "test-hash"
        )
        control = self.runtime.control_connection()
        invitation_ids = []
        for index, status in enumerate(("pending", "sent")):
            cursor = control.execute(
                "INSERT INTO identity_invitations("
                "firm_id,email_normalized,email_display,invited_role,token_hash,invited_by_user_id,"
                "created_at,expires_at,status,updated_at"
                ") VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    firm_id,
                    f"offboarding-{index}@example.test",
                    f"offboarding-{index}@example.test",
                    "lawyer",
                    str(index + 1) * 64,
                    user_id,
                    100,
                    200,
                    status,
                    100,
                ),
            )
            invitation_ids.append(int(cursor.lastrowid))
        control.commit()
        self.runtime.disable_firm(firm_id)

        revoked = self.runtime.revoke_disabled_firm_invitations(
            firm_id,
            reason="close all outstanding invitations before approved offboarding",
            operator_reference="offboarding-ticket-123",
            change_reference="change-offboarding-456",
        )
        self.assertEqual(revoked, 2)
        for invitation_id in invitation_ids:
            row = control.execute(
                "SELECT status FROM identity_invitations WHERE id=?", (invitation_id,)
            ).fetchone()
            self.assertEqual(row["status"], "revoked")
            event = control.execute(
                "SELECT detail_json FROM identity_lifecycle_events "
                "WHERE invitation_id=? AND event_type='invitation_revoked'",
                (invitation_id,),
            ).fetchone()
            self.assertIsNotNone(event)
            detail = json.loads(event["detail_json"])
            self.assertEqual(detail["operator_reference"], "offboarding-ticket-123")
            self.assertEqual(detail["change_reference"], "change-offboarding-456")
            self.assertEqual(detail["source"], "firm_offboarding_cli")
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM identity_invitations "
                "WHERE firm_id=? AND status IN ('pending','sent')",
                (firm_id,),
            ).fetchone()[0],
            0,
        )

    def test_disabled_firm_invitation_offboarding_audit_failure_rolls_back_all_changes(self):
        firm_id, _ = self.runtime.provision_firm("Invitation Offboarding Audit Failure")
        user_id = self.runtime.create_global_identity(
            "Invitation Audit Owner", "invitation-audit-owner@example.test", "test-hash"
        )
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO identity_invitations("
            "firm_id,email_normalized,email_display,invited_role,token_hash,invited_by_user_id,"
            "created_at,expires_at,status,updated_at"
            ") VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                firm_id, "rollback-invite@example.test", "rollback-invite@example.test",
                "lawyer", "c" * 64, user_id, 100, 200, "sent", 100,
            ),
        )
        control.execute(
            "CREATE TRIGGER reject_offboarding_invitation_audit "
            "BEFORE INSERT ON identity_lifecycle_events "
            "WHEN NEW.event_type='invitation_revoked' "
            "BEGIN SELECT RAISE(ABORT, 'injected invitation audit failure'); END"
        )
        control.commit()
        self.runtime.disable_firm(firm_id)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected invitation audit failure"):
            self.runtime.revoke_disabled_firm_invitations(
                firm_id,
                reason="test audit rollback",
                operator_reference="offboarding-ticket-audit",
                change_reference="change-offboarding-audit",
            )
        control.execute("DROP TRIGGER reject_offboarding_invitation_audit")
        control.commit()
        self.assertEqual(
            control.execute(
                "SELECT status FROM identity_invitations WHERE firm_id=?", (firm_id,)
            ).fetchone()[0],
            "sent",
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM identity_lifecycle_events "
                "WHERE firm_id=? AND event_type='invitation_revoked'",
                (firm_id,),
            ).fetchone()[0],
            0,
        )

    def test_revoked_membership_closes_cached_firm_connection(self):
        user_id = self._identity()
        firm_id, _ = self.runtime.provision_firm("Revocation Test")
        self.runtime.create_firm_membership(user_id, firm_id, "admin")
        old_context = self.runtime.resolve_context(user_id, firm_id)
        cached = self.runtime.firm_connection(old_context)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='revoked' WHERE user_id=? AND firm_id=?",
            (user_id, firm_id),
        )
        control.commit()
        with self.assertRaises(FirmContextError):
            self.runtime.firm_connection(old_context)
        with self.assertRaises(sqlite3.ProgrammingError):
            cached.execute("SELECT 1")

    def test_disabling_global_identity_closes_cached_firm_connection(self):
        user_id = self._identity("disabled-global-identity@example.test")
        firm_id, database_path = self.runtime.provision_firm("Disabled Global Identity")
        self.runtime.create_firm_membership(user_id, firm_id, "admin")
        context = self.runtime.resolve_context(user_id, firm_id)
        cached = self.runtime.firm_connection(context)
        control = self.runtime.control_connection()
        control.execute("UPDATE users SET status='disabled' WHERE id=?", (user_id,))
        control.commit()

        with self.assertRaises(FirmContextError):
            self.runtime.firm_connection(context)
        with self.assertRaises(sqlite3.ProgrammingError):
            cached.execute("SELECT 1")
        self.assertTrue(database_path.is_file(), "disabling an identity must not delete firm data")
        self.assertEqual(
            control.execute(
                "SELECT status FROM firm_memberships WHERE user_id=? AND firm_id=?",
                (user_id, firm_id),
            ).fetchone()[0],
            "active",
        )

    def test_disabling_firm_closes_cached_firm_connection(self):
        user_id = self._identity()
        firm_id, database_path = self.runtime.provision_firm("Disable Cached Connection")
        self.runtime.create_firm_membership(user_id, firm_id, "admin")
        context = self.runtime.resolve_context(user_id, firm_id)
        cached = self.runtime.firm_connection(context)
        self.assertTrue(database_path.is_file())

        self.assertTrue(self.runtime.disable_firm(firm_id))
        with self.assertRaises(FirmContextError):
            self.runtime.firm_connection(context)
        with self.assertRaises(sqlite3.ProgrammingError):
            cached.execute("SELECT 1")
        self.assertTrue(database_path.is_file())

    def test_role_change_requires_context_refresh(self):
        user_id = self._identity()
        firm_id, _ = self.runtime.provision_firm("Role Test")
        self.runtime.create_firm_membership(user_id, firm_id, "lawyer")
        old_context = self.runtime.resolve_context(user_id, firm_id)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET firm_role='admin' WHERE user_id=? AND firm_id=?",
            (user_id, firm_id),
        )
        control.commit()
        with self.assertRaises(FirmContextError):
            self.runtime.firm_connection(old_context)

    def test_firm_role_change_closes_cached_tenant_connection(self):
        user_id = self._identity("role-change-cache@example.test")
        firm_id, database_path = self.runtime.provision_firm("Role Change Cache")
        self.runtime.create_firm_membership(user_id, firm_id, "lawyer")
        old_context = self.runtime.resolve_context(user_id, firm_id)
        cached = self.runtime.firm_connection(old_context)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET firm_role='admin' WHERE user_id=? AND firm_id=?",
            (user_id, firm_id),
        )
        control.commit()

        with self.assertRaises(FirmContextError):
            self.runtime.firm_connection(old_context)
        with self.assertRaises(sqlite3.ProgrammingError):
            cached.execute("SELECT 1")
        self.assertTrue(database_path.is_file())
        refreshed = self.runtime.resolve_context(user_id, firm_id)
        self.assertEqual(refreshed.role, "admin")
        self.assertEqual(self.runtime.firm_connection(refreshed).execute("SELECT 1").fetchone()[0], 1)

    def test_initial_owner_bootstrap_never_grants_platform_role(self):
        firm_id, _ = self.runtime.provision_firm("Owner Bootstrap")
        user_id = self.runtime.create_initial_firm_owner(
            firm_id, "First Owner", "owner@example.test", "test-hash"
        )
        control = self.runtime.control_connection()
        self.assertEqual(
            control.execute(
                "SELECT firm_role FROM firm_memberships WHERE user_id=? AND firm_id=?",
                (user_id, firm_id),
            ).fetchone()[0],
            "admin",
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM user_platform_roles WHERE user_id=?", (user_id,)
            ).fetchone()[0],
            0,
        )
        with self.assertRaises(DatabaseRuntimeError):
            self.runtime.create_initial_firm_owner(
                firm_id, "Second Owner", "second@example.test", "test-hash"
            )

    def test_runtime_refuses_ambiguous_or_overlapping_paths(self):
        with self.assertRaises(DatabaseRuntimeError):
            DatabaseRuntime(
                self.root / "same.sqlite3",
                self.root / "tenants",
                self.root / "same.sqlite3",
            )
        with self.assertRaises(DatabaseRuntimeError):
            DatabaseRuntime(
                self.root / "tenants" / "control.sqlite3",
                self.root / "tenants",
                self.root / "corpus.sqlite3",
            )

    def test_from_env_requires_three_explicit_database_paths(self):
        names = (
            "COPILOT_CONTROL_DB",
            "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB",
        )
        previous = {name: os.environ.get(name) for name in names}
        try:
            for name in names:
                os.environ.pop(name, None)
            with self.assertRaises(DatabaseRuntimeError):
                DatabaseRuntime.from_env()
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value


    def test_fresh_firm_schema_has_no_scope_defaults_and_rejects_unscoped_case(self):
        user_id = self._identity("explicit-scope@example.test")
        firm_id, _ = self.runtime.provision_firm("Explicit Scope Firm")
        self.runtime.create_firm_membership(user_id, firm_id, "admin")
        context = self.runtime.resolve_context(user_id, firm_id)
        db = self.runtime.firm_connection(context)

        for table in ("cases", "docs", "document_extraction_reviews",
                      "research_conversations", "case_deletion_audit"):
            with self.subTest(table=table):
                columns = {
                    row["name"]: row
                    for row in db.execute(f'PRAGMA table_info("{table}")')
                }
                self.assertIn("firm_id", columns)
                self.assertEqual(
                    columns["firm_id"]["dflt_value"], None,
                    f"{table}.firm_id must not default to an arbitrary firm",
                )

        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("INSERT INTO cases(title) VALUES('missing firm scope')")
        db.rollback()
        self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
