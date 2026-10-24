"""Tests for safe tenant catalog and SQLite database provisioning."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tenant_catalog import (
    TenantCatalogError,
    initialize_catalog,
    provision_tenant_database,
    resolve_tenant_database,
)


class TenantCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "tenants"
        self.catalog = sqlite3.connect(":memory:")

    def tearDown(self):
        self.catalog.close()
        self.temp.cleanup()

    @staticmethod
    def initialize_tenant(db):
        db.execute("CREATE TABLE tenant_marker (value TEXT NOT NULL)")
        db.execute("INSERT INTO tenant_marker(value) VALUES('initialized')")

    def test_provision_and_resolve_uses_catalog_not_client_path(self):
        initialize_catalog(self.catalog)
        path = provision_tenant_database(self.catalog, 17, self.root, self.initialize_tenant)
        self.assertTrue(path.is_file())
        self.assertEqual(resolve_tenant_database(self.catalog, 17, self.root), path)
        tenant = sqlite3.connect(path)
        try:
            self.assertEqual(tenant.execute("SELECT value FROM tenant_marker").fetchone()[0], "initialized")
        finally:
            tenant.close()
        row = self.catalog.execute(
            "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=17"
        ).fetchone()
        self.assertEqual(row[0], "provisioned")
        self.assertEqual(Path(row[1]).name, row[1])

    def test_provision_is_idempotent_for_existing_tenant(self):
        first = provision_tenant_database(self.catalog, 3, self.root, self.initialize_tenant)
        second = provision_tenant_database(
            self.catalog, 3, self.root,
            lambda db: (_ for _ in ()).throw(AssertionError("must not reinitialize")),
        )
        self.assertEqual(first, second)

    def test_failed_initialization_cleans_file_and_records_failure(self):
        def fail(db):
            db.execute("CREATE TABLE partial (id INTEGER)")
            raise RuntimeError("initializer failed")

        with self.assertRaisesRegex(RuntimeError, "initializer failed"):
            provision_tenant_database(self.catalog, 4, self.root, fail)
        row = self.catalog.execute(
            "SELECT database_file,status,last_error_code FROM tenant_database_catalog WHERE firm_id=4"
        ).fetchone()
        self.assertEqual(row, (None, "failed", "provisioning_failed"))
        self.assertEqual(list(self.root.glob("tenant-4-*.sqlite3")), [])

    def test_unprovisioned_or_unknown_tenant_is_denied(self):
        with self.assertRaises(TenantCatalogError):
            resolve_tenant_database(self.catalog, 999, self.root)

    def test_invalid_firm_id_rejected(self):
        for value in (0, -1, True, "17"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                provision_tenant_database(self.catalog, value, self.root, self.initialize_tenant)

    def test_catalog_path_tampering_is_rejected(self):
        provision_tenant_database(self.catalog, 8, self.root, self.initialize_tenant)
        self.catalog.execute(
            "UPDATE tenant_database_catalog SET database_file=? WHERE firm_id=8",
            ("../../other.sqlite3",),
        )
        with self.assertRaises(TenantCatalogError):
            resolve_tenant_database(self.catalog, 8, self.root)

    def test_missing_provisioned_database_fails_closed(self):
        path = provision_tenant_database(self.catalog, 9, self.root, self.initialize_tenant)
        path.unlink()
        with self.assertRaisesRegex(TenantCatalogError, "missing"):
            resolve_tenant_database(self.catalog, 9, self.root)

    def test_disabled_tenant_cannot_be_resolved(self):
        provision_tenant_database(self.catalog, 10, self.root, self.initialize_tenant)
        self.catalog.execute(
            "UPDATE tenant_database_catalog SET status='disabled' WHERE firm_id=10"
        )
        with self.assertRaises(TenantCatalogError):
            resolve_tenant_database(self.catalog, 10, self.root)


if __name__ == "__main__":
    unittest.main()
