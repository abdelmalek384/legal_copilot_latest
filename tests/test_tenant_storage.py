"""Tests for catalog-backed tenant connection routing (not request authorization)."""
import os
import sqlite3
import shutil
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path

from schema_profiles import apply_profile_migrations
from tenant_catalog import initialize_catalog, provision_tenant_database, resolve_tenant_database
from tenant_storage import TenantConnectionError, TenantSQLiteConnectionRouter

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


class TenantSQLiteConnectionRouterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "tenant-files"
        self.catalog_path = Path(self.temp.name) / "control-plane.sqlite3"
        self._init_catalog()

        def initialize_tenant(db):
            db.execute("PRAGMA journal_mode=WAL")
            apply_profile_migrations(db, "firm", MIGRATIONS)
            db.execute("CREATE TABLE marker (value TEXT NOT NULL)")
            db.execute("INSERT INTO marker(value) VALUES (?)", ("created",))

        with self._catalog() as catalog:
            provision_tenant_database(catalog, 101, self.root, initialize_tenant)
            provision_tenant_database(catalog, 202, self.root, initialize_tenant)

        tenant_paths = []
        for firm_id, value in ((101, "firm-a"), (202, "firm-b")):
            with self._catalog() as catalog:
                path = resolve_tenant_database(catalog, firm_id, self.root)
            tenant_paths.append(path)
            db = sqlite3.connect(path)
            try:
                db.execute("UPDATE marker SET value=?", (value,))
                db.commit()
                db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            finally:
                db.close()
            # Migration/provisioning writes can leave empty WAL sidecars after
            # the final connection closes. Remove those fixture artifacts so
            # the symlink/FIFO tests can create the exact sidecar they intend.
            for suffix in ("-wal", "-shm"):
                sidecar = Path(str(path) + suffix)
                if sidecar.exists() or sidecar.is_symlink():
                    sidecar.unlink()

        self.router = TenantSQLiteConnectionRouter(self._catalog, self.root)

    def tearDown(self):
        self.router.close_current_thread()
        self.temp.cleanup()

    def _init_catalog(self):
        with self._catalog() as db:
            apply_profile_migrations(db, "control_plane", MIGRATIONS)
            db.executemany(
                "INSERT INTO firms(id,name) VALUES(?,?)",
                [(101, "Firm A"), (202, "Firm B")],
            )
            db.commit()
            initialize_catalog(db)

    def _catalog(self):
        return sqlite3.connect(self.catalog_path)

    def test_rejects_tenant_database_without_wal_mode(self):
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        with sqlite3.connect(path) as db:
            self.assertEqual(db.execute("PRAGMA journal_mode=DELETE").fetchone()[0].lower(), "delete")

        with self.assertRaisesRegex(TenantConnectionError, "must use WAL journal mode"):
            self.router.connection_for_firm(101)

    def test_routes_to_distinct_catalog_selected_databases(self):
        a = self.router.connection_for_firm(101)
        b = self.router.connection_for_firm(202)
        self.assertEqual(a.execute("SELECT value FROM marker").fetchone()[0], "firm-a")
        self.assertEqual(b.execute("SELECT value FROM marker").fetchone()[0], "firm-b")
        self.assertIsNot(a, b)

    def test_same_path_database_replacement_revokes_cached_tenant_connection(self):
        connection = self.router.connection_for_firm(101)
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        replacement = self.root / "replacement-tenant.sqlite3"
        with sqlite3.connect(replacement) as db:
            db.execute("CREATE TABLE replacement_sentinel(value TEXT)")
            db.execute("INSERT INTO replacement_sentinel VALUES('not firm 101')")
        if os.name == "posix":
            os.chmod(replacement, 0o600)
        os.replace(replacement, path)

        with self.assertRaisesRegex(TenantConnectionError, "database file was replaced"):
            self.router.connection_for_firm(101)
        with self.assertRaisesRegex(sqlite3.ProgrammingError, "closed"):
            connection.execute("SELECT 1")

    @unittest.skipUnless(os.name == "posix", "POSIX file permission bits are required")
    def test_permissive_file_mode_revokes_cached_tenant_connection(self):
        connection = self.router.connection_for_firm(101)
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        os.chmod(path, 0o644)
        with self.assertRaisesRegex(TenantConnectionError, "permissions allow group/other access"):
            self.router.connection_for_firm(101)
        with self.assertRaisesRegex(sqlite3.ProgrammingError, "closed"):
            connection.execute("SELECT 1")

    @unittest.skipUnless(os.name == "posix", "POSIX file permission bits are required")
    def test_permissive_sqlite_sidecar_revokes_cached_tenant_connection(self):
        connection = self.router.connection_for_firm(101)
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        sidecar = Path(str(path) + "-wal")
        sidecar.write_text("synthetic WAL sidecar", encoding="utf-8")
        os.chmod(sidecar, 0o644)
        with self.assertRaisesRegex(TenantConnectionError, "sidecar permissions allow group/other access"):
            self.router.connection_for_firm(101)
        with self.assertRaisesRegex(sqlite3.ProgrammingError, "closed"):
            connection.execute("SELECT 1")

    @unittest.skipUnless(os.name == "posix", "POSIX symlinks are required")
    def test_symlinked_sqlite_sidecar_revokes_cached_tenant_connection(self):
        connection = self.router.connection_for_firm(101)
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        sidecar = Path(str(path) + "-wal")
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        sidecar.unlink(missing_ok=True)
        target = Path(self.temp.name) / "external-wal"
        target.write_text("synthetic WAL sidecar", encoding="utf-8")
        sidecar.symlink_to(target)
        with self.assertRaisesRegex(TenantConnectionError, "sidecar must not be a symbolic link"):
            self.router.connection_for_firm(101)
        with self.assertRaisesRegex(sqlite3.ProgrammingError, "closed"):
            connection.execute("SELECT 1")

    @unittest.skipUnless(os.name == "posix", "POSIX named pipes are required")
    def test_fifo_sqlite_sidecar_revokes_cached_tenant_connection(self):
        connection = self.router.connection_for_firm(101)
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        sidecar = Path(str(path) + "-wal")
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        sidecar.unlink(missing_ok=True)
        os.mkfifo(sidecar)
        with self.assertRaisesRegex(TenantConnectionError, "sidecar must be a regular file"):
            self.router.connection_for_firm(101)
        with self.assertRaisesRegex(sqlite3.ProgrammingError, "closed"):
            connection.execute("SELECT 1")

    def test_rejects_tenant_database_bound_to_non_firm_profile(self):
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        with sqlite3.connect(path) as db:
            # Simulate on-disk corruption by removing the immutable guard first;
            # ordinary application SQL must not be able to rebind this marker.
            db.execute("DROP TRIGGER database_profile_no_update")
            db.execute(
                "UPDATE database_profile SET profile='legal_corpus' WHERE singleton=1"
            )
        router = TenantSQLiteConnectionRouter(self._catalog, self.root)
        with self.assertRaisesRegex(TenantConnectionError, "not bound to the firm schema profile"):
            router.connection_for_firm(101)
        router.close_current_thread()

    def test_rejects_tenant_database_without_profile_binding(self):
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 202, self.root)
        with sqlite3.connect(path) as db:
            db.execute("DROP TABLE database_profile")
        router = TenantSQLiteConnectionRouter(self._catalog, self.root)
        with self.assertRaisesRegex(TenantConnectionError, "missing its required firm profile binding"):
            router.connection_for_firm(202)
        router.close_current_thread()

    def test_rejects_database_file_copied_from_another_firm(self):
        with self._catalog() as catalog:
            source = resolve_tenant_database(catalog, 101, self.root)
            target = resolve_tenant_database(catalog, 202, self.root)
        # Both database connections are closed here; replacing B's contents
        # with A's file must be detected by the immutable in-database binding.
        shutil.copyfile(source, target)
        router = TenantSQLiteConnectionRouter(self._catalog, self.root)
        with self.assertRaisesRegex(TenantConnectionError, "bound to a different firm"):
            router.connection_for_firm(202)
        router.close_current_thread()

    def test_router_rejects_missing_or_ineffective_profile_guards(self):
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        with sqlite3.connect(path) as db:
            db.execute("DROP TRIGGER database_profile_no_update")
            db.execute("DROP TRIGGER database_profile_no_delete")
            db.executescript("""
                CREATE TRIGGER database_profile_no_update
                BEFORE UPDATE ON database_profile
                BEGIN SELECT 1; END;
                CREATE TRIGGER database_profile_no_delete
                BEFORE DELETE ON database_profile
                BEGIN SELECT 1; END;
            """)
        router = TenantSQLiteConnectionRouter(self._catalog, self.root)
        with self.assertRaisesRegex(TenantConnectionError, "profile binding lacks effective immutable guards"):
            router.connection_for_firm(101)
        router.close_current_thread()

    def test_router_rejects_missing_or_ineffective_firm_binding_guards(self):
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        with sqlite3.connect(path) as db:
            db.execute("DROP TRIGGER tenant_database_binding_no_update")
            db.executescript("""
                CREATE TRIGGER tenant_database_binding_no_update
                BEFORE UPDATE ON tenant_database_binding
                BEGIN SELECT 1; END;
            """)
        router = TenantSQLiteConnectionRouter(self._catalog, self.root)
        with self.assertRaisesRegex(TenantConnectionError, "lacks effective immutable guards"):
            router.connection_for_firm(101)
        router.close_current_thread()

    def test_tenant_database_firm_binding_cannot_be_updated_or_deleted(self):
        with self._catalog() as catalog:
            path = resolve_tenant_database(catalog, 101, self.root)
        with sqlite3.connect(path) as db:
            with self.assertRaisesRegex(sqlite3.IntegrityError, "firm binding is immutable"):
                db.execute("UPDATE tenant_database_binding SET firm_id=202 WHERE singleton=1")
            with self.assertRaisesRegex(sqlite3.IntegrityError, "firm binding is immutable"):
                db.execute("DELETE FROM tenant_database_binding WHERE singleton=1")

    def test_reuses_connection_for_same_firm_on_current_thread(self):
        first = self.router.connection_for_firm(101)
        second = self.router.connection_for_firm(101)
        self.assertIs(first, second)

    def test_same_firm_uses_distinct_connections_across_threads(self):
        barrier = threading.Barrier(2)
        connections = []
        errors = []

        def worker():
            try:
                connection = self.router.connection_for_firm(101)
                connections.append(connection)
                barrier.wait(timeout=5)
                self.assertEqual(
                    connection.execute("SELECT value FROM marker").fetchone()[0],
                    "firm-a",
                )
                barrier.wait(timeout=5)
                self.router.close_current_thread()
                with self.assertRaises(sqlite3.ProgrammingError):
                    connection.execute("SELECT 1")
            except BaseException as exc:
                errors.append(exc)

        workers = [threading.Thread(target=worker) for _ in range(2)]
        for worker_thread in workers:
            worker_thread.start()
        for worker_thread in workers:
            worker_thread.join(timeout=10)

        self.assertTrue(all(not worker_thread.is_alive() for worker_thread in workers))
        self.assertEqual(errors, [])
        self.assertEqual(len(connections), 2)
        self.assertIsNot(connections[0], connections[1])

    def test_rejects_invalid_firm_id_shapes(self):
        for value in (0, -1, True, "101", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.router.connection_for_firm(value)

    def test_catalog_open_failure_revokes_cached_connection(self):
        unavailable = {"value": False}

        def catalog_factory():
            if unavailable["value"]:
                raise sqlite3.OperationalError("catalog unavailable")
            return self._catalog()

        router = TenantSQLiteConnectionRouter(catalog_factory, self.root)
        connection = router.connection_for_firm(101)
        unavailable["value"] = True

        with self.assertRaisesRegex(TenantConnectionError, "catalog is unavailable"):
            router.connection_for_firm(101)
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")

    def test_unknown_firm_fails_closed_without_shared_database_fallback(self):
        with self.assertRaises(TenantConnectionError):
            self.router.connection_for_firm(303)

    def test_disabled_tenant_is_rejected_and_cached_connection_is_closed(self):
        connection = self.router.connection_for_firm(101)
        with self._catalog() as catalog:
            catalog.execute("UPDATE tenant_database_catalog SET status='disabled' WHERE firm_id=101")
            catalog.commit()
        with self.assertRaises(TenantConnectionError):
            self.router.connection_for_firm(101)
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")

    def test_failed_connection_setup_closes_untracked_connection(self):
        original_connect = sqlite3.connect
        opened = []

        class FailingPragmaConnection(sqlite3.Connection):
            def execute(self, sql, parameters=()):
                if sql.strip().upper() == "PRAGMA FOREIGN_KEYS=ON":
                    raise sqlite3.OperationalError("foreign key pragma failed")
                return super().execute(sql, parameters)

        def connect_with_failure(database, *args, **kwargs):
            if str(database) == str(self.catalog_path):
                return original_connect(database, *args, **kwargs)
            kwargs["factory"] = FailingPragmaConnection
            connection = original_connect(database, *args, **kwargs)
            opened.append(connection)
            return connection

        router = TenantSQLiteConnectionRouter(
            lambda: original_connect(self.catalog_path), self.root
        )
        with patch("tenant_storage.sqlite3.connect", side_effect=connect_with_failure):
            with self.assertRaisesRegex(TenantConnectionError, "unavailable"):
                router.connection_for_firm(101)

        self.assertEqual(len(opened), 1)
        with self.assertRaises(sqlite3.ProgrammingError):
            opened[0].execute("SELECT 1")

    def test_each_tenant_connection_enables_foreign_keys(self):
        for firm_id in (101, 202):
            connection = self.router.connection_for_firm(firm_id)
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_close_current_thread_closes_and_clears_connections(self):
        connection = self.router.connection_for_firm(101)
        self.router.close_current_thread()
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")
        self.assertEqual(self.router.connection_for_firm(101).execute("SELECT 1").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
