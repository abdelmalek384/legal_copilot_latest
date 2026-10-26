"""End-to-end fresh-install and restart checks for the application SQLite schema."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class FreshInstallSchemaTests(unittest.TestCase):
    def test_fresh_install_creates_all_migration_tables_and_restart_preserves_rows(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "fresh-install.sqlite3"
            env = os.environ.copy()
            env["COPILOT_DB"] = str(database)
            env["PYTHONPATH"] = str(root)

            first_start = r"""
import sqlite3
from pathlib import Path
import app

db = app.conn()
expected_tables = {
    "schema_migrations",
    "auth_sessions",
    "notes",
    "fees",
    "tasks",
    "events",
    "sessions",
    "legal_version_relations",
    "security_audit_events",
    "document_extraction_reviews",
}
actual_tables = {
    row[0] for row in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
}
missing = expected_tables - actual_tables
assert not missing, f"fresh install missing tables: {sorted(missing)}"

expected_versions = [
    int(path.name[:4]) for path in sorted(Path("migrations").glob("*.sql"))
]
applied_versions = [
    row[0] for row in db.execute(
        "SELECT version FROM schema_migrations ORDER BY version"
    )
]
assert applied_versions == expected_versions, (
    f"migration ledger mismatch: expected {expected_versions}, got {applied_versions}"
)
db.execute(
    "INSERT INTO notes(id, case_id, text) VALUES(987654, 1, 'restart sentinel')"
)
db.commit()
"""
            result = subprocess.run(
                [sys.executable, "-c", first_start],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(
                result.returncode, 0,
                msg=f"fresh startup failed:\n{result.stdout}\n{result.stderr}",
            )

            second_start = r"""
import app
db = app.conn()
row = db.execute(
    "SELECT text FROM notes WHERE id=987654"
).fetchone()
assert row is not None and row[0] == "restart sentinel", (
    "restart failed to preserve existing application data"
)
"""
            result = subprocess.run(
                [sys.executable, "-c", second_start],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(
                result.returncode, 0,
                msg=f"restart against existing database failed:\n{result.stdout}\n{result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
