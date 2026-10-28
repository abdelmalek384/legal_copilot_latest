"""Tests for the read-only tenant database catalog preflight."""
import os
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path

from scripts.tenant_database_preflight import audit
from schema_profiles import apply_profile_migrations

MIGRATIONS_ROOT = Path(__file__).resolve().parents[1] / "migrations"


class TenantDatabasePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "tenants"
        self.root.mkdir()
        self.catalog_path = self.base / "catalog.sqlite3"
        self.catalog = sqlite3.connect(self.catalog_path)
        self.catalog.execute("PRAGMA foreign_keys=ON")
        apply_profile_migrations(self.catalog, "control_plane", MIGRATIONS_ROOT)
        if os.name == "posix":
            os.chmod(self.catalog_path, 0o600)

    def tearDown(self):
        self.catalog.close()
        self.temp.cleanup()

    def add_tenant(self, firm_id, status="provisioned", filename=None):
        filename = filename or f"tenant-{firm_id}-{uuid.uuid4().hex}.sqlite3"
        self.catalog.execute(
            "INSERT INTO firms(id,name) VALUES(?,?)",
            (firm_id, f"Firm {firm_id}"),
        )
        self.catalog.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) VALUES(?,?,?)",
            (firm_id, filename, status),
        )
        self.catalog.commit()
        if status == "provisioned":
            db = sqlite3.connect(self.root / filename)
            db.execute("PRAGMA foreign_keys=ON")
            apply_profile_migrations(db, "firm", MIGRATIONS_ROOT)
            db.execute("INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,?)", (firm_id,))
            db.commit()
            db.close()
            if os.name == "posix":
                os.chmod(self.root / filename, 0o600)
        return filename

    def test_profile_migration_fifo_is_rejected_without_blocking(self):
        import os
        from unittest.mock import patch
        from scripts import tenant_database_preflight as preflight_module

        if not hasattr(os, "mkfifo") or os.name != "posix":
            self.skipTest("FIFO behavior is POSIX-specific")
        fake_root = self.base / "tool-root"
        scripts = fake_root / "scripts"
        migrations = fake_root / "migrations"
        scripts.mkdir(parents=True)
        (migrations / "firm").mkdir(parents=True)
        (migrations / "control_plane").mkdir(parents=True)
        script_file = scripts / "tenant_database_preflight.py"
        script_file.write_text("# test fixture", encoding="utf-8")
        (migrations / "firm" / "0001_fixture.sql").write_text(
            "CREATE TABLE fixture(id INTEGER);", encoding="utf-8"
        )
        os.mkfifo(migrations / "firm" / "0002_wait_forever.sql")
        with patch.object(preflight_module, "__file__", str(script_file)):
            with self.assertRaisesRegex(ValueError, "unsafe firm migration input"):
                preflight_module._expected_profile_migrations("firm")

    def test_clean_catalog_and_database_pass(self):
        self.add_tenant(1)
        before = self.catalog.execute("SELECT * FROM tenant_database_catalog").fetchall()
        report = audit(self.catalog_path, self.root)
        after = self.catalog.execute("SELECT * FROM tenant_database_catalog").fetchall()
        self.assertEqual(report["status"], "no_detected_problems")
        self.assertEqual(report["tenant_databases_inspected"], 1)
        self.assertEqual(before, after)

    def test_missing_migration_history_is_reported(self):
        self.add_tenant(9)
        filename = self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=9"
        ).fetchone()[0]
        with sqlite3.connect(self.root / filename) as db:
            db.execute("DROP TABLE schema_migrations")
        report = audit(self.catalog_path, self.root)
        self.assertIn("missing_schema_migration_ledger", {item["code"] for item in report["findings"]})

    def test_incomplete_and_checksum_drifted_migration_history_are_reported(self):
        self.add_tenant(10)
        filename = self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=10"
        ).fetchone()[0]
        with sqlite3.connect(self.root / filename) as db:
            db.execute("DELETE FROM schema_migrations WHERE version=(SELECT MAX(version) FROM schema_migrations)")
            db.execute("UPDATE schema_migrations SET checksum_sha256='bad-checksum' WHERE version=(SELECT MIN(version) FROM schema_migrations)")
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"] if item["firm_id"] == 10}
        self.assertIn("incomplete_schema_migration_history", codes)
        self.assertIn("schema_migration_checksum_mismatch", codes)

    def test_wrong_catalog_profile_and_mutable_profile_guards_are_reported(self):
        with sqlite3.connect(self.catalog_path) as db:
            db.execute("DROP TRIGGER database_profile_no_update")
            db.execute("UPDATE database_profile SET profile='firm' WHERE singleton=1")
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"] if item["firm_id"] is None}
        self.assertIn("wrong_catalog_profile", codes)
        self.assertIn("mutable_catalog_profile_binding", codes)

    def test_missing_catalog_profile_is_reported(self):
        with sqlite3.connect(self.catalog_path) as db:
            db.execute("DROP TABLE database_profile")
        report = audit(self.catalog_path, self.root)
        self.assertIn(
            "missing_catalog_profile",
            {item["code"] for item in report["findings"] if item["firm_id"] is None},
        )

    def test_missing_catalog_migration_history_is_reported(self):
        with sqlite3.connect(self.catalog_path) as db:
            db.execute("DROP TABLE schema_migrations")
        report = audit(self.catalog_path, self.root)
        self.assertIn(
            "missing_catalog_migration_ledger",
            {item["code"] for item in report["findings"] if item["firm_id"] is None},
        )

    def test_catalog_migration_checksum_drift_is_reported(self):
        with sqlite3.connect(self.catalog_path) as db:
            db.execute("UPDATE schema_migrations SET checksum_sha256='bad-checksum' WHERE version=(SELECT MIN(version) FROM schema_migrations)")
        report = audit(self.catalog_path, self.root)
        self.assertIn(
            "catalog_migration_checksum_mismatch",
            {item["code"] for item in report["findings"] if item["firm_id"] is None},
        )

    def test_catalog_authority_failure_stops_before_opening_tenant_files(self):
        self.add_tenant(21)
        with sqlite3.connect(self.catalog_path) as db:
            db.execute("DROP TRIGGER database_profile_no_update")
            db.execute("UPDATE database_profile SET profile='firm' WHERE singleton=1")
        report = audit(self.catalog_path, self.root)
        self.assertEqual(report["tenant_databases_inspected"], 0)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("wrong_catalog_profile", codes)
        self.assertNotIn("database_unreadable", codes)

    def test_missing_catalog_firm_foreign_key_is_reported_before_tenant_inspection(self):
        self.add_tenant(22)
        with sqlite3.connect(self.catalog_path) as db:
            db.execute("PRAGMA foreign_keys=OFF")
            db.execute("ALTER TABLE tenant_database_catalog RENAME TO old_tenant_catalog")
            db.execute("""
                CREATE TABLE tenant_database_catalog (
                    firm_id INTEGER PRIMARY KEY,
                    database_file TEXT,
                    status TEXT
                )
            """)
            db.execute("""
                INSERT INTO tenant_database_catalog(firm_id, database_file, status)
                SELECT firm_id, database_file, status FROM old_tenant_catalog
            """)
            db.execute("DROP TABLE old_tenant_catalog")
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("missing_catalog_firm_foreign_key", codes)
        self.assertEqual(report["tenant_databases_inspected"], 0)

    @unittest.skipUnless(os.name == "posix", "POSIX file permission bits are required")
    def test_open_tenant_database_permissions_are_reported(self):
        filename = self.add_tenant(25)
        os.chmod(self.root / filename, 0o644)
        report = audit(self.catalog_path, self.root)
        findings = [item for item in report["findings"] if item["firm_id"] == 25]
        self.assertIn("database_permissions_too_open", {item["code"] for item in findings})

    @unittest.skipUnless(os.name == "posix", "POSIX file permission bits are required")
    def test_open_catalog_permissions_are_reported(self):
        os.chmod(self.catalog_path, 0o644)
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"] if item["firm_id"] is None}
        self.assertIn("catalog_permissions_too_open", codes)

    @unittest.skipUnless(os.name == "posix", "POSIX file permission bits are required")
    def test_open_tenant_sqlite_sidecar_permissions_are_reported(self):
        filename = self.add_tenant(26)
        sidecar = Path(str(self.root / filename) + "-wal")
        sidecar.write_text("synthetic WAL sidecar", encoding="utf-8")
        os.chmod(sidecar, 0o644)
        report = audit(self.catalog_path, self.root)
        findings = [item for item in report["findings"] if item["firm_id"] == 26]
        self.assertIn("database_sidecar_permissions_too_open", {item["code"] for item in findings})
        self.assertEqual(report["tenant_databases_inspected"], 0)

    @unittest.skipUnless(os.name == "posix", "POSIX symlinks are required")
    def test_tenant_sqlite_sidecar_symlink_is_reported(self):
        filename = self.add_tenant(27)
        sidecar = Path(str(self.root / filename) + "-wal")
        target = self.root / "sidecar-target"
        target.write_text("synthetic WAL sidecar", encoding="utf-8")
        sidecar.symlink_to(target)
        report = audit(self.catalog_path, self.root)
        findings = [item for item in report["findings"] if item["firm_id"] == 27]
        self.assertIn("database_sidecar_symlink", {item["code"] for item in findings})
        self.assertEqual(report["tenant_databases_inspected"], 0)

    @unittest.skipUnless(os.name == "posix", "POSIX symlinks are required")
    def test_catalog_sidecar_symlink_prevents_catalog_open(self):
        sidecar = Path(str(self.catalog_path) + "-wal")
        target = Path(self.temp.name) / "catalog-sidecar-target"
        target.write_text("synthetic WAL sidecar", encoding="utf-8")
        sidecar.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "unsafe SQLite sidecar"):
            audit(self.catalog_path, self.root)

    @unittest.skipUnless(os.name == "posix", "POSIX named pipes are required")
    def test_tenant_fifo_sidecar_is_reported_and_database_is_not_opened(self):
        filename = self.add_tenant(28)
        os.mkfifo(Path(str(self.root / filename) + "-wal"))
        report = audit(self.catalog_path, self.root)
        findings = [item for item in report["findings"] if item["firm_id"] == 28]
        self.assertIn("database_sidecar_not_regular_file", {item["code"] for item in findings})
        self.assertEqual(report["tenant_databases_inspected"], 0)

    def test_missing_database_is_reported(self):
        self.add_tenant(2, filename=f"tenant-2-{uuid.uuid4().hex}.sqlite3")
        (self.root / self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=2"
        ).fetchone()[0]).unlink()
        report = audit(self.catalog_path, self.root)
        self.assertIn("database_missing", {item["code"] for item in report["findings"]})

    def test_invalid_mapping_and_not_ready_tenant_are_reported(self):
        self.catalog.execute("INSERT INTO firms(id,name) VALUES(3,'Firm 3')")
        self.catalog.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) VALUES(3,?,?)",
            ("../../outside.sqlite3", "provisioned"),
        )
        self.catalog.commit()
        self.add_tenant(4, status="provisioning")
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("invalid_database_reference", codes)
        self.assertIn("tenant_not_ready", codes)


    def test_active_firm_without_provisioned_catalog_entry_is_reported(self):
        self.catalog.execute("INSERT INTO firms(id,name,status) VALUES(40,'Missing Catalog Firm','active')")
        self.catalog.commit()
        report = audit(self.catalog_path, self.root)
        findings = [item for item in report["findings"] if item["firm_id"] == 40]
        self.assertIn("active_firm_catalog_mismatch", {item["code"] for item in findings})

    def test_disabled_firm_with_provisioned_catalog_entry_is_reported(self):
        self.add_tenant(41)
        self.catalog.execute("UPDATE firms SET status='disabled' WHERE id=41")
        self.catalog.commit()
        report = audit(self.catalog_path, self.root)
        findings = [item for item in report["findings"] if item["firm_id"] == 41]
        self.assertIn("disabled_firm_catalog_mismatch", {item["code"] for item in findings})

    def test_unreferenced_tenant_database_file_is_reported(self):
        filename = self.add_tenant(42)
        self.catalog.execute("DELETE FROM tenant_database_catalog WHERE firm_id=42")
        self.catalog.commit()
        report = audit(self.catalog_path, self.root)
        self.assertIn(
            "unreferenced_database_file",
            {item["code"] for item in report["findings"]},
        )
        self.assertIn(
            "active_firm_catalog_mismatch",
            {item["code"] for item in report["findings"] if item["firm_id"] == 42},
        )
        self.assertTrue((self.root / filename).is_file(), "read-only audit must not delete orphaned files")

    def test_stale_provisioning_firm_is_reported(self):
        self.add_tenant(43, status="provisioning")
        self.catalog.execute("UPDATE firms SET status='provisioning' WHERE id=43")
        self.catalog.commit()
        report = audit(self.catalog_path, self.root)
        findings = [item for item in report["findings"] if item["firm_id"] == 43]
        self.assertIn("firm_stuck_provisioning", {item["code"] for item in findings})

    def test_wrong_profile_and_embedded_firm_binding_are_reported(self):
        self.add_tenant(6)
        filename = self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=6"
        ).fetchone()[0]
        with sqlite3.connect(self.root / filename) as db:
            db.execute("DROP TRIGGER database_profile_no_update")
            db.execute("DROP TRIGGER tenant_database_binding_no_update")
            db.execute("UPDATE database_profile SET profile='legal_corpus' WHERE singleton=1")
            db.execute("UPDATE tenant_database_binding SET firm_id=99 WHERE singleton=1")
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("wrong_database_profile", codes)
        self.assertIn("tenant_firm_binding_mismatch", codes)
        self.assertIn("mutable_database_profile_binding", codes)
        self.assertIn("mutable_tenant_firm_binding", codes)

    def test_trigger_names_with_noop_bodies_are_not_accepted_as_immutable_guards(self):
        self.add_tenant(8)
        filename = self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=8"
        ).fetchone()[0]
        with sqlite3.connect(self.root / filename) as db:
            db.execute("DROP TRIGGER database_profile_no_update")
            db.execute("DROP TRIGGER database_profile_no_delete")
            db.execute("DROP TRIGGER tenant_database_binding_no_update")
            db.execute("DROP TRIGGER tenant_database_binding_no_delete")
            db.executescript("""
                CREATE TRIGGER database_profile_no_update BEFORE UPDATE ON database_profile BEGIN SELECT 1; END;
                CREATE TRIGGER database_profile_no_delete BEFORE DELETE ON database_profile BEGIN SELECT 1; END;
                CREATE TRIGGER tenant_database_binding_no_update BEFORE UPDATE ON tenant_database_binding BEGIN SELECT 1; END;
                CREATE TRIGGER tenant_database_binding_no_delete BEFORE DELETE ON tenant_database_binding BEGIN SELECT 1; END;
            """)
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"] if item["firm_id"] == 8}
        self.assertIn("mutable_database_profile_binding", codes)
        self.assertIn("mutable_tenant_firm_binding", codes)

    def test_missing_profile_and_firm_binding_are_reported(self):
        self.add_tenant(7)
        filename = self.catalog.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=7"
        ).fetchone()[0]
        with sqlite3.connect(self.root / filename) as db:
            db.execute("DROP TABLE database_profile")
            db.execute("DROP TABLE tenant_database_binding")
        report = audit(self.catalog_path, self.root)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("missing_database_profile", codes)
        self.assertIn("missing_tenant_firm_binding", codes)


    def test_symlinked_catalog_database_is_rejected(self):
        link = self.base / "catalog-link.sqlite3"
        link.symlink_to(self.catalog_path)
        with self.assertRaisesRegex(ValueError, "catalog database must not be a symlink"):
            audit(link, self.root)

    def test_symlinked_storage_root_is_rejected(self):
        real_root = self.base / "real-tenants"
        real_root.mkdir()
        target = real_root / f"tenant-7-{uuid.uuid4().hex}.sqlite3"
        with sqlite3.connect(target) as db:
            db.execute("CREATE TABLE marker (value TEXT)")
        link_root = self.base / "tenants-link"
        link_root.symlink_to(real_root, target_is_directory=True)

        with self.assertRaisesRegex(ValueError, "storage root must not be a symlink"):
            audit(self.catalog_path, link_root)

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
