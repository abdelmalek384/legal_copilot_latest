"""Tests for catalog-backed tenant connection routing (not request authorization)."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tenant_catalog import initialize_catalog, provision_tenant_database, resolve_tenant_database
from tenant_storage import TenantConnectionError, TenantSQLiteConnectionRouter


class TenantSQLiteConnectionRouterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "tenant-files"
        self.catalog_path = Path(self.temp.name) / "control-plane.sqlite3"
        self._init_catalog()

        def initialize_tenant(db):
            db.execute("CREATE TABLE marker (value TEXT NOT NULL)")
            db.execute("INSERT INTO marker(value) VALUES (?)", ("created",))

        with self._catalog() as catalog:
            provision_tenant_database(catalog, 101, self.root, initialize_tenant)
            provision_tenant_database(catalog, 202, self.root, initialize_tenant)

        for firm_id, value in ((101, "firm-a"), (202, "firm-b")):
            with self._catalog() as catalog:
                path = resolve_tenant_database(catalog, firm_id, self.root)
            db = sqlite3.connect(path)
            try:
                db.execute("UPDATE marker SET value=?", (value,))
                db.commit()
            finally:
                db.close()

        self.router = TenantSQLiteConnectionRouter(self._catalog, self.root)

    def tearDown(self):
        self.router.close_current_thread()
        self.temp.cleanup()

    def _init_catalog(self):
        with self._catalog() as db:
            db.execute("CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
            db.executemany("INSERT INTO firms(id,name) VALUES(?,?)",
                           [(101, "Firm A"), (202, "Firm B")])
            db.commit()
            initialize_catalog(db)

    def _catalog(self):
        return sqlite3.connect(self.catalog_path)

    def test_routes_to_distinct_catalog_selected_databases(self):
        a = self.router.connection_for_firm(101)
        b = self.router.connection_for_firm(202)
        self.assertEqual(a.execute("SELECT value FROM marker").fetchone()[0], "firm-a")
        self.assertEqual(b.execute("SELECT value FROM marker").fetchone()[0], "firm-b")
        self.assertIsNot(a, b)

    def test_reuses_connection_for_same_firm_on_current_thread(self):
        first = self.router.connection_for_firm(101)
        second = self.router.connection_for_firm(101)
        self.assertIs(first, second)

    def test_rejects_invalid_firm_id_shapes(self):
        for value in (0, -1, True, "101", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.router.connection_for_firm(value)

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
