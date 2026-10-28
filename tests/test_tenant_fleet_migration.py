"""Behavioral tests for backup-first tenant fleet migrations."""
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from database_runtime import DatabaseRuntime
from tools.migrate_tenant_fleet import FleetMigrationError, apply_fleet, build_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = REPO_ROOT / "migrations"


class TenantFleetMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = DatabaseRuntime(
            self.root / "control.sqlite3",
            self.root / "tenants",
            self.root / "corpus.sqlite3",
        )
        self.runtime.initialize()
        self.firm_id, self.tenant_path = self.runtime.provision_firm("Fleet Migration Test Firm")
        self.migrations_root = self.root / "migrations"
        shutil.copytree(MIGRATIONS, self.migrations_root)

    def tearDown(self):
        self.runtime.close_current_thread()
        self.temp.cleanup()

    def _add_pending_migration(self):
        path = self.migrations_root / "firm" / "9999_fleet_test_table.sql"
        path.write_text(
            "CREATE TABLE fleet_migration_test (id INTEGER PRIMARY KEY, value TEXT NOT NULL);\n",
            encoding="utf-8",
        )
        return path

    def test_plan_is_read_only_and_reports_pending_versions(self):
        self._add_pending_migration()
        before = self.tenant_path.stat().st_mtime_ns
        plan = build_plan(
            self.runtime.paths.control_plane,
            self.runtime.paths.tenant_root,
            self.migrations_root,
        )
        self.assertEqual(plan["target_count"], 1)
        self.assertEqual(plan["pending_database_count"], 1)
        self.assertEqual(plan["targets"][0]["firm_id"], self.firm_id)
        self.assertEqual(plan["targets"][0]["pending_versions"], [9999])
        self.assertEqual(self.tenant_path.stat().st_mtime_ns, before)
        with sqlite3.connect(self.tenant_path) as connection:
            self.assertIsNone(connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='fleet_migration_test'"
            ).fetchone())

    def test_preflight_rejects_migration_fifo_without_blocking(self):
        if not hasattr(os, "mkfifo") or os.name != "posix":
            self.skipTest("FIFO behavior is POSIX-specific")
        fifo = self.migrations_root / "firm" / "9999_wait_forever.sql"
        os.mkfifo(fifo)
        with self.assertRaisesRegex(FleetMigrationError, "Unsafe migration input"):
            build_plan(
                self.runtime.paths.control_plane,
                self.runtime.paths.tenant_root,
                self.migrations_root,
            )

    def test_apply_requires_explicit_worker_stop_confirmation(self):
        self._add_pending_migration()
        with self.assertRaisesRegex(FleetMigrationError, "worker-stop confirmation"):
            apply_fleet(
                self.runtime.paths.control_plane,
                self.runtime.paths.tenant_root,
                self.migrations_root,
                self.root / "backups",
                confirm_workers_stopped=False,
            )
        with sqlite3.connect(self.tenant_path) as connection:
            self.assertIsNone(connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='fleet_migration_test'"
            ).fetchone())

    def test_apply_snapshots_before_migration_and_applies_pending_schema(self):
        self._add_pending_migration()
        result = apply_fleet(
            self.runtime.paths.control_plane,
            self.runtime.paths.tenant_root,
            self.migrations_root,
            self.root / "backups",
            confirm_workers_stopped=True,
        )
        self.assertTrue(result["all_targets_migrated"], result)
        self.assertEqual(result["outcome"][0]["applied_versions"], [9999])
        backup = Path(result["backups"][0]["path"])
        self.assertTrue(backup.is_file())
        if os.name == "posix":
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
            self.assertEqual((self.root / "backups").stat().st_mode & 0o777, 0o700)
        with sqlite3.connect(self.tenant_path) as connection:
            self.assertIsNotNone(connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='fleet_migration_test'"
            ).fetchone())
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        with sqlite3.connect(backup) as connection:
            self.assertIsNone(connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='fleet_migration_test'"
            ).fetchone())

    def test_preflight_refuses_catalog_file_belonging_to_another_firm(self):
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE tenant_database_catalog SET database_file=? WHERE firm_id=?",
            (f"tenant-{self.firm_id + 100}-{'a' * 32}.sqlite3", self.firm_id),
        )
        control.commit()
        with self.assertRaisesRegex(FleetMigrationError, "invalid or mismatched"):
            build_plan(
                self.runtime.paths.control_plane,
                self.runtime.paths.tenant_root,
                self.migrations_root,
            )

    def test_preflight_refuses_tenant_firm_binding_mismatch(self):
        connection = sqlite3.connect(self.tenant_path)
        connection.execute("DROP TRIGGER tenant_database_binding_no_update")
        connection.execute("UPDATE tenant_database_binding SET firm_id=?", (self.firm_id + 1,))
        connection.commit()
        connection.close()
        with self.assertRaisesRegex(FleetMigrationError, "binding does not match"):
            build_plan(
                self.runtime.paths.control_plane,
                self.runtime.paths.tenant_root,
                self.migrations_root,
            )

    def test_preflight_refuses_firm_and_catalog_lifecycle_mismatch(self):
        control = self.runtime.control_connection()
        control.execute("UPDATE firms SET status='disabled' WHERE id=?", (self.firm_id,))
        control.commit()
        with self.assertRaisesRegex(FleetMigrationError, "conflicts with provisioned catalog state"):
            build_plan(
                self.runtime.paths.control_plane,
                self.runtime.paths.tenant_root,
                self.migrations_root,
            )

    def test_preflight_refuses_unreferenced_tenant_database_file(self):
        # Keep the orphan filename in the tenant naming family so the test
        # proves catalog reconciliation, not filename parsing, catches it.
        orphan_path = self.root / ("tenant-999-" + "a" * 32 + ".sqlite3")
        sqlite3.connect(orphan_path).close()
        if os.name == "posix":
            os.chmod(orphan_path, 0o600)
        with self.assertRaisesRegex(FleetMigrationError, "unreferenced files"):
            build_plan(
                self.runtime.paths.control_plane,
                self.runtime.paths.tenant_root,
                self.migrations_root,
            )

    def test_preflight_refuses_missing_provisioned_tenant_database(self):
        self.tenant_path.unlink()
        with self.assertRaisesRegex(FleetMigrationError, "missing or unsafe"):
            build_plan(
                self.runtime.paths.control_plane,
                self.runtime.paths.tenant_root,
                self.migrations_root,
            )


if __name__ == "__main__":
    unittest.main()
