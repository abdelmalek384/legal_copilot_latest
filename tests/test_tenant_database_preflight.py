"""Tests for the read-only tenant database catalog preflight."""
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path

from scripts.tenant_database_preflight import audit


class TenantDatabasePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "tenants"
        self.root.mkdir()
        self.catalog_path = self.base / "catalog.sqlite3"
        self.catalog = sqlite3.connect(self.catalog_path)
        self.catalog.execute("""
            CREATE TABLE tenant_database_catalog (
                firm_id INTEGER PRIMARY KEY,
                database_file TEXT UNIQUE,
                status TEXT NOT NULL
            )
        """)

    def tearDown(self):
        self.catalog.close()
        self.temp.cleanup()

    def add_tenant(self, firm_id, status="provisioned", filename=None):
        filename = filename or f"tenant-{firm_id}-{uuid.uuid4().hex}.sqlite3"
        self.catalog.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) VALUES(?,?,?)",
            (firm_id, filename, status),
        )
        self.catalog.commit()
        if status == "provisioned":
            db = sqlite3.connect(self.root / filename)
            db.execute("CREATE TABLE marker (value TEXT)")
            db.commit()
            db.close()
        return filename

    def test_clean_catalog_and_database_pass(self):
        self.add_tenant(1)
        before = self.catalog.execute("SELECT * FROM tenant_database_catalog").fetchall()
        report = audit(self.catalog_path, self.root)
        after = self.catalog.execute("SELECT * FROM tenant_database_catalog").fetchall()
        self.assertEqual(report["status"], "no_detected_problems")
        self.assertEqual(report["tenant_databases_inspected"], 1)
        self.assertEqual(before, after)

    def test_missing_database_is_reported(self):
        self.add_tenant(2, filename=f"tenant-2-{uuid.uuid4().hex}.sqlite3")
        (self.root / self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=2"
        ).fetchone()[0]).unlink()
        report = audit(self.catalog_path, self.root)
        self.assertIn("database_missing", {item["code"] for item in report["findings"]})

    def test_invalid_mapping_and_not_ready_tenant_are_reported(self):
        self.add_tenant(3, filename="../../outside.sqlite3")
        self.add_tenant(4, status="provisioning")
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("invalid_database_reference", codes)
        self.assertIn("tenant_not_ready", codes)

    def test_symlink_is_reported_without_following_it(self):
        target = self.add_tenant(5)
        row = self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=5"
        ).fetchone()[0]
        (self.root / row).unlink()
        (self.root / row).symlink_to(self.root / target)
        report = audit(self.catalog_path, self.root)
        self.assertIn("database_symlink", {item["code"] for item in report["findings"]})


if __name__ == "__main__":
    unittest.main()
