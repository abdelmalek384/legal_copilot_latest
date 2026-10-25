"""Tests for the read-only startup DDL inventory."""
import tempfile
import unittest
from pathlib import Path

from scripts.database_startup_ddl_inventory import inventory


class DatabaseStartupDDLInventoryTests(unittest.TestCase):
    def test_inventory_counts_schema_and_legacy_alters_without_opening_database(self):
        root = Path(__file__).resolve().parents[1]
        report = inventory(root / "app.py", root / "migrations")
        self.assertEqual(report["mode"], "source_only_read_only")
        self.assertFalse(report["database_opened"])
        self.assertGreater(report["startup_schema"]["counts"]["create_table"], 0)
        self.assertGreater(report["startup_schema"]["counts"]["create_virtual_table"], 0)
        self.assertEqual(report["startup_schema"]["counts"]["create_index"], 0)
        self.assertNotIn("CREATE TABLE IF NOT EXISTS legal_version_relations", (root / "app.py").read_text(encoding="utf-8"))
        self.assertTrue(report["startup_ddl_outside_schema_literal"])
        operations = {item["operation"] for item in report["startup_ddl_outside_schema_literal"]}
        self.assertIn("alter table", operations)
        self.assertEqual(
            [item["file"] for item in report["migrations"]],
            sorted(item["file"] for item in report["migrations"]),
        )
        self.assertEqual(len(report["migrations"]), 4)

    def test_inventory_uses_explicit_paths_and_does_not_require_a_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = root / "app.py"
            migrations = root / "migrations"
            migrations.mkdir()
            app.write_text('SCHEMA = """CREATE TABLE IF NOT EXISTS sample(id INTEGER);"""\n', encoding="utf-8")
            (migrations / "0001_sample.sql").write_text(
                "CREATE INDEX IF NOT EXISTS idx_sample ON sample(id);", encoding="utf-8"
            )
            report = inventory(app, migrations)
            self.assertEqual(report["startup_schema"]["counts"]["create_table"], 1)
            self.assertEqual(report["migrations"][0]["counts"]["create_index"], 1)
            self.assertFalse(report["database_opened"])


if __name__ == "__main__":
    unittest.main()
