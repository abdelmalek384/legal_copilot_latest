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
        self.catalog.execute("CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        for firm_id in (3, 4, 8, 9, 10, 11, 12, 17, 21, 22, 23, 24, 30, 31):
            self.catalog.execute(
                "INSERT INTO firms(id,name) VALUES(?,?)", (firm_id, f"Firm {firm_id}")
            )
        self.catalog.commit()
        initialize_catalog(self.catalog)

    def tearDown(self):
        self.catalog.close()
        self.temp.cleanup()

    @staticmethod
    def initialize_tenant(db):
        db.execute("CREATE TABLE tenant_marker (value TEXT NOT NULL)")
        db.execute("INSERT INTO tenant_marker(value) VALUES('initialized')")
        db.execute("""
            CREATE TABLE database_profile (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                profile TEXT NOT NULL
            )
        """)
        db.execute("INSERT INTO database_profile(singleton,profile) VALUES(1,'firm')")
        db.commit()

    def test_catalog_initialization_requires_migration_managed_firms_table(self):
        db = sqlite3.connect(":memory:")
        try:
            with self.assertRaisesRegex(TenantCatalogError, "firms table must be created by migrations"):
                initialize_catalog(db)
            self.assertIsNone(db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tenant_database_catalog'"
            ).fetchone())
        finally:
            db.close()

    def test_existing_catalog_without_firm_foreign_key_is_rejected(self):
        db = sqlite3.connect(":memory:")
        try:
            db.execute("CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
            db.execute("""
                CREATE TABLE tenant_database_catalog (
                    firm_id INTEGER PRIMARY KEY,
                    database_file TEXT UNIQUE,
                    status TEXT NOT NULL CHECK(status IN ('provisioning','provisioned','failed','disabled')),
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    last_error_code TEXT
                )
            """)
            db.commit()
            with self.assertRaisesRegex(TenantCatalogError, "missing its firm ownership constraint"):
                initialize_catalog(db)
        finally:
            db.close()

    def test_catalog_with_existing_orphan_firm_reference_is_rejected(self):
        db = sqlite3.connect(":memory:")
        try:
            db.execute("CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
            db.execute("""
                CREATE TABLE tenant_database_catalog (
                    firm_id INTEGER PRIMARY KEY CHECK(firm_id > 0)
                        REFERENCES firms(id) ON DELETE RESTRICT,
                    database_file TEXT UNIQUE,
                    status TEXT NOT NULL CHECK(status IN ('provisioning','provisioned','failed','disabled')),
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    last_error_code TEXT
                )
            """)
            db.execute("PRAGMA foreign_keys=OFF")
            db.execute("""
                INSERT INTO tenant_database_catalog(firm_id,database_file,status)
                VALUES(404,NULL,'failed')
            """)
            db.commit()
            with self.assertRaisesRegex(TenantCatalogError, "invalid firm ownership references"):
                initialize_catalog(db)
        finally:
            db.close()

    def test_provision_requires_an_existing_firm(self):
        with self.assertRaisesRegex(sqlite3.IntegrityError, "FOREIGN KEY"):
            provision_tenant_database(self.catalog, 404, self.root, self.initialize_tenant)
        self.assertIsNone(self.catalog.execute(
            "SELECT 1 FROM tenant_database_catalog WHERE firm_id=404"
        ).fetchone())

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

    def test_provision_enables_foreign_key_enforcement_for_initializer(self):
        def initialize_with_invalid_reference(db):
            self.initialize_tenant(db)
            db.execute("CREATE TABLE parent (id INTEGER PRIMARY KEY)")
            db.execute("CREATE TABLE child (parent_id INTEGER REFERENCES parent(id))")
            db.execute("INSERT INTO child(parent_id) VALUES(404)")

        with self.assertRaises(sqlite3.IntegrityError):
            provision_tenant_database(
                self.catalog, 24, self.root, initialize_with_invalid_reference
            )

        row = self.catalog.execute(
            "SELECT database_file,status,last_error_code FROM tenant_database_catalog WHERE firm_id=24"
        ).fetchone()
        self.assertEqual(row, (None, "failed", "provisioning_failed"))
        self.assertEqual(list(self.root.glob("tenant-24-*.sqlite3")), [])

    def test_provision_rejects_foreign_key_violations_and_cleans_partial_file(self):
        def initialize_with_broken_reference(db):
            self.initialize_tenant(db)
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("CREATE TABLE parent (id INTEGER PRIMARY KEY)")
            db.execute("CREATE TABLE child (parent_id INTEGER REFERENCES parent(id))")
            # Deliberately disable enforcement to simulate a malformed schema/data
            # initializer; foreign_key_check must catch what integrity_check misses.
            db.execute("PRAGMA foreign_keys=OFF")
            db.execute("INSERT INTO child(parent_id) VALUES(404)")

        with self.assertRaisesRegex(TenantCatalogError, "foreign-key validation"):
            provision_tenant_database(
                self.catalog, 23, self.root, initialize_with_broken_reference
            )

        row = self.catalog.execute(
            "SELECT database_file,status,last_error_code FROM tenant_database_catalog WHERE firm_id=23"
        ).fetchone()
        self.assertEqual(row, (None, "failed", "provisioning_failed"))
        self.assertEqual(list(self.root.glob("tenant-23-*.sqlite3")), [])


    def test_provision_rejects_missing_or_wrong_firm_profile(self):
        def without_profile(db):
            db.execute("CREATE TABLE marker (value TEXT)")

        def wrong_profile(db):
            self.initialize_tenant(db)
            db.execute("UPDATE database_profile SET profile='legal_corpus' WHERE singleton=1")

        for firm_id, initializer, message in (
            (30, without_profile, "missing its required firm schema profile binding"),
            (31, wrong_profile, "not bound to the firm schema profile"),
        ):
            with self.subTest(firm_id=firm_id), self.assertRaisesRegex(TenantCatalogError, message):
                provision_tenant_database(self.catalog, firm_id, self.root, initializer)
            row = self.catalog.execute(
                "SELECT database_file,status,last_error_code FROM tenant_database_catalog WHERE firm_id=?",
                (firm_id,),
            ).fetchone()
            self.assertEqual(row, (None, "failed", "provisioning_failed"))
            self.assertEqual(list(self.root.glob(f"tenant-{firm_id}-*.sqlite3")), [])


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

    def test_symlink_to_another_tenant_database_is_rejected(self):
        first = provision_tenant_database(self.catalog, 11, self.root, self.initialize_tenant)
        second = provision_tenant_database(self.catalog, 12, self.root, self.initialize_tenant)
        # Catalog filenames are validated; use the exact catalog filename for
        # firm 11 and replace its directory entry with a symlink to firm 12.
        row = self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=11"
        ).fetchone()
        first.unlink()
        (self.root / row[0]).symlink_to(second)
        with self.assertRaisesRegex(TenantCatalogError, "symlink"):
            resolve_tenant_database(self.catalog, 11, self.root)

    def test_disabled_tenant_cannot_be_resolved(self):
        provision_tenant_database(self.catalog, 10, self.root, self.initialize_tenant)
        self.catalog.execute(
            "UPDATE tenant_database_catalog SET status='disabled' WHERE firm_id=10"
        )
        with self.assertRaises(TenantCatalogError):
            resolve_tenant_database(self.catalog, 10, self.root)


    def test_symlinked_storage_root_is_rejected_before_provisioning(self):
        real_root = Path(self.temp.name) / "real-tenants"
        real_root.mkdir()
        link_root = Path(self.temp.name) / "tenants-link"
        link_root.symlink_to(real_root, target_is_directory=True)
        with self.assertRaisesRegex(TenantCatalogError, "storage root.*symlink"):
            provision_tenant_database(self.catalog, 21, link_root, self.initialize_tenant)
        self.assertEqual(list(real_root.iterdir()), [])

    def test_symlinked_storage_root_is_rejected_during_resolution(self):
        real_root = Path(self.temp.name) / "real-tenants"
        real_root.mkdir()
        link_root = Path(self.temp.name) / "tenants-link"
        link_root.symlink_to(real_root, target_is_directory=True)
        with self.assertRaisesRegex(TenantCatalogError, "storage root.*symlink"):
            resolve_tenant_database(self.catalog, 22, link_root)


if __name__ == "__main__":
    unittest.main()
