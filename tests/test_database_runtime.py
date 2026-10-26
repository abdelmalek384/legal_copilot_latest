import os
import sqlite3
import stat
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

    def tearDown(self):
        self.runtime.close_current_thread()
        self.temp.cleanup()

    def _identity(self, email="lawyer@example.test"):
        return self.runtime.create_global_identity("Test Lawyer", email, "test-hash")

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
        with self.assertRaisesRegex(sqlite3.IntegrityError, "case deletion audit firm scope"):
            db.execute(
                "INSERT INTO case_deletion_audit(firm_id,case_id,actor_user_id,actor_name,"
                "case_snapshot_json,events_snapshot_json,related_counts_json) "
                "VALUES(?,?,?,?,?,?,?)",
                (firm_b, case_id, user_id, "actor", "{}", "[]", "{}"),
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


if __name__ == "__main__":
    unittest.main()
