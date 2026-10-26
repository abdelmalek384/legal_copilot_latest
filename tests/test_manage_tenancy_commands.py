"""Integration tests for separate-database firm provisioning and membership CLI."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from database_runtime import DatabaseRuntime


ROOT = Path(__file__).resolve().parents[1]
MANAGE = ROOT / "manage.py"


class TenancyCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = os.environ.copy()
        self.env.update({
            "COPILOT_CONTROL_DB": str(self.root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(self.root / "tenants"),
            "COPILOT_CORPUS_DB": str(self.root / "corpus.sqlite3"),
            "PYTHONPATH": str(ROOT),
        })
        self.runtime = DatabaseRuntime(
            self.env["COPILOT_CONTROL_DB"],
            self.env["COPILOT_TENANT_DB_ROOT"],
            self.env["COPILOT_CORPUS_DB"],
        )
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Firm A")
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_a, "Global Owner", "global-owner@example.test", "test-hash"
        )

    def tearDown(self):
        self.runtime.close_current_thread()
        self.temp.cleanup()

    def run_manage(self, *args):
        return subprocess.run(
            [sys.executable, str(MANAGE), *args],
            cwd=ROOT,
            env=self.env,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )

    def test_adduser_rejects_inactive_firm_without_creating_identity(self):
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firms SET status='disabled',updated_at=datetime('now') WHERE id=?",
            (self.firm_a,),
        )
        control.commit()

        result = subprocess.run(
            [sys.executable, str(MANAGE), "adduser", "Blocked User",
             "blocked-user@example.test", "lawyer", "--firm-id", str(self.firm_a)],
            cwd=ROOT,
            env=self.env,
            input="StrongPassphrase-2026!\n",
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inactive firm", result.stderr)
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM users WHERE email_normalized=?",
                ("blocked-user@example.test",),
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE firm_id=?",
                (self.firm_a,),
            ).fetchone()[0],
            1,
        )

    def test_provision_firm_and_attach_existing_global_identity(self):
        provisioned = self.run_manage("provision-firm", "Firm B")
        self.assertEqual(provisioned.returncode, 0, provisioned.stderr)
        report = json.loads(provisioned.stdout)
        self.assertEqual(report["status"], "provisioned")
        firm_b = report["firm_id"]
        database_path = Path(report["database_path"])
        self.assertTrue(database_path.is_file())

        added = self.run_manage(
            "addmembership", " GLOBAL-OWNER@EXAMPLE.TEST ",
            "--firm-id", str(firm_b), "--role", "lawyer",
        )
        self.assertEqual(added.returncode, 0, added.stderr)
        membership = json.loads(added.stdout)
        self.assertEqual(membership["status"], "membership_created")
        self.assertEqual(membership["user_id"], self.user_id)
        self.assertEqual(membership["firm_id"], firm_b)

        control = self.runtime.control_connection()
        rows = control.execute(
            "SELECT firm_id,firm_role,status FROM firm_memberships WHERE user_id=? ORDER BY firm_id",
            (self.user_id,),
        ).fetchall()
        self.assertEqual(
            [(row["firm_id"], row["firm_role"], row["status"]) for row in rows],
            [(self.firm_a, "admin", "active"), (firm_b, "lawyer", "active")],
        )

        duplicate = self.run_manage(
            "addmembership", "global-owner@example.test",
            "--firm-id", str(firm_b), "--role", "lawyer",
        )
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn("Membership already exists", duplicate.stderr)
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE user_id=? AND firm_id=?",
                (self.user_id, firm_b),
            ).fetchone()[0],
            1,
        )


if __name__ == "__main__":
    unittest.main()
