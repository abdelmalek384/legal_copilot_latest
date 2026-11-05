"""Invoice schema migration contract tests."""
import sqlite3
import unittest
from pathlib import Path

from schema_profiles import apply_profile_migrations


ROOT = Path(__file__).resolve().parents[1]


class InvoiceSchemaMigrationTests(unittest.TestCase):
    def test_firm_profile_applies_invoice_tables_and_append_only_guards(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        try:
            applied = apply_profile_migrations(connection, "firm", ROOT / "migrations")
            self.assertIn(16, applied)
            self.assertIn(21, applied)
            tables = {
                row["name"] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            self.assertTrue({
                "invoice_sequences", "invoices", "invoice_lines",
                "invoice_payments", "invoice_events",
            }.issubset(tables))
            triggers = {
                row["name"] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='trigger'"
                )
            }
            indexes = {
                row["name"] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='index'"
                )
            }
            self.assertIn("idx_invoices_created_id_case", indexes)
            self.assertTrue({
                "invoice_lines_insert_only_draft",
                "invoice_lines_update_only_draft",
                "invoice_lines_delete_only_draft",
                "invoice_issued_content_immutable",
                "invoice_payments_no_update",
                "invoice_payments_no_delete",
                "invoice_events_no_update",
                "invoice_events_no_delete",
            }.issubset(triggers))
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
