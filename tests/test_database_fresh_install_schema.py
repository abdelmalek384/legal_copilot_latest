"""Fresh-install and restart checks for the approved profile-separated database runtime."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class FreshInstallSchemaTests(unittest.TestCase):
    def test_fresh_install_creates_all_profile_migrations_and_restart_preserves_rows(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            env = os.environ.copy()
            env.pop("COPILOT_DB", None)
            env["COPILOT_ENV"] = "development"
            env["COPILOT_CONTROL_DB"] = str(directory / "control.sqlite3")
            env["COPILOT_TENANT_DB_ROOT"] = str(directory / "tenants")
            env["COPILOT_CORPUS_DB"] = str(directory / "corpus.sqlite3")
            env["PYTHONPATH"] = str(root)

            first_start = r"""
from pathlib import Path
from database_runtime import DatabaseRuntime

runtime = DatabaseRuntime.from_env()
runtime.initialize()
firm_id, tenant_path = runtime.provision_firm("Fresh install restart fixture")
user_id = runtime.create_initial_firm_owner(
    firm_id, "Fresh Install Owner", "fresh-install-owner@example.test", "test-password-hash"
)
context = runtime.resolve_context(user_id, firm_id)
firm_db = runtime.firm_connection(context)
firm_db.execute(
    "INSERT INTO cases(id,title,firm_id) VALUES(987654,'restart sentinel case',?)",
    (firm_id,),
)
firm_db.execute(
    "INSERT INTO notes(case_id,text) VALUES(987654,'restart sentinel')"
)
firm_db.commit()

root = Path("migrations")
profiles = {
    "control_plane": runtime.paths.control_plane,
    "firm": tenant_path,
    "legal_corpus": runtime.paths.legal_corpus,
}
expected_tables = {
    "control_plane": {"auth_sessions", "firm_memberships", "tenant_database_catalog"},
    "firm": {"cases", "notes", "tasks", "fees"},
    "legal_corpus": {"legal_sources", "legal_documents", "legal_document_versions", "legal_version_relations"},
}
for profile, path in profiles.items():
    import sqlite3
    db = sqlite3.connect(path)
    try:
        marker = db.execute("SELECT profile FROM database_profile WHERE singleton=1").fetchone()
        assert marker == (profile,), f"{profile}: incorrect immutable profile marker {marker}"
        actual = {
            row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT GLOB 'sqlite_*'"
            )
        }
        missing = expected_tables[profile] - actual
        assert not missing, f"{profile}: missing tables {sorted(missing)}"
        expected_versions = [
            int(file.name[:4]) for file in sorted((root / profile).glob("*.sql"))
        ]
        applied_versions = [
            row[0] for row in db.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            )
        ]
        assert applied_versions == expected_versions, (
            f"{profile}: migration ledger mismatch: expected {expected_versions}, got {applied_versions}"
        )
    finally:
        db.close()
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
                msg=f"profile-separated fresh startup failed:\\n{result.stdout}\\n{result.stderr}",
            )

            second_start = r"""
from database_runtime import DatabaseRuntime

runtime = DatabaseRuntime.from_env()
runtime.initialize()
control = runtime.control_connection()
firm_id = control.execute(
    "SELECT id FROM firms WHERE name=?", ("Fresh install restart fixture",)
).fetchone()[0]
user_id = control.execute(
    "SELECT id FROM users WHERE email_normalized=?",
    ("fresh-install-owner@example.test",),
).fetchone()[0]
context = runtime.resolve_context(user_id, firm_id)
firm_db = runtime.firm_connection(context)
row = firm_db.execute(
    "SELECT text FROM notes WHERE case_id=987654"
).fetchone()
assert row is not None and row[0] == "restart sentinel", (
    "restart failed to preserve firm database rows"
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
                msg=f"profile-separated restart failed:\\n{result.stdout}\\n{result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
