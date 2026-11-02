"""Ensure firm-context setup cannot leave a stale tenant WAL snapshot open."""
import os
import tempfile
import unittest
from pathlib import Path

import app
from database_runtime import DatabaseRuntime


class TenantContextTransactionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-context-tx-")
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_OBJECT_STORAGE_ROOT",
            "COPILOT_OBJECT_STORAGE_BACKEND", "COPILOT_ENV",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ.pop("COPILOT_DB", None)
        os.environ.update({
            "COPILOT_CONTROL_DB": str(self.root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(self.root / "tenants"),
            "COPILOT_CORPUS_DB": str(self.root / "corpus.sqlite3"),
            "COPILOT_OBJECT_STORAGE_ROOT": str(self.root / "objects"),
            "COPILOT_OBJECT_STORAGE_BACKEND": "local",
            "COPILOT_ENV": "development",
        })
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_id, _ = self.runtime.provision_firm("Context Transaction Firm")
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_id, "Context Owner", "context-owner@example.test",
            app.hash_pw("Context-owner-password-2026!"),
        )
        self.context = self.runtime.resolve_context(self.user_id, self.firm_id)

    def tearDown(self):
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        for name, value in self.old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        self.temp.cleanup()

    def test_context_setup_commits_before_route_and_same_firm_reuse_does_not_commit_route_work(self):
        connection = self.runtime.firm_connection(self.context)
        self.assertFalse(connection.in_transaction)

        connection.execute(
            "INSERT INTO cases(title,created_by,firm_id) VALUES(?,?,?)",
            ("Uncommitted matter", self.user_id, self.firm_id),
        )
        self.assertTrue(connection.in_transaction)

        same_connection = self.runtime.firm_connection(self.context)
        self.assertIs(same_connection, connection)
        self.assertTrue(
            connection.in_transaction,
            "same-firm context reuse must not commit a route's active transaction",
        )
        connection.rollback()
        self.assertFalse(connection.in_transaction)


if __name__ == "__main__":
    unittest.main()
