"""Integration tests for separate-database firm provisioning and membership CLI."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from database_backup import create_backup_bundle
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
            "UPDATE firms SET status='disabled' WHERE id=?",
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

    def test_disable_firm_blocks_catalog_routing_without_deleting_database(self):
        _, database_path = self.runtime.provision_firm("Firm to Disable")
        firm_id = self.runtime.control_connection().execute(
            "SELECT id FROM firms WHERE name='Firm to Disable'"
        ).fetchone()[0]

        result = self.run_manage("disable-firm", str(firm_id))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "disabled")
        self.assertTrue(report["changed"])
        self.assertFalse(report["data_deleted"])
        self.assertTrue(database_path.is_file())

        control = self.runtime.control_connection()
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "disabled",
        )
        self.assertEqual(
            control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
            ).fetchone()[0],
            "disabled",
        )

        repeated = self.run_manage("disable-firm", str(firm_id))
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertFalse(json.loads(repeated.stdout)["changed"])
        self.assertTrue(database_path.is_file())

    def test_disable_firm_rejects_unknown_firm_without_creating_catalog_rows(self):
        result = self.run_manage("disable-firm", "999999")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Firm does not exist", result.stderr)
        self.assertEqual(
            self.runtime.control_connection().execute(
                "SELECT COUNT(*) FROM tenant_database_catalog WHERE firm_id=999999"
            ).fetchone()[0],
            0,
        )

    def test_reconcile_interrupted_provisioning_cli_requires_both_confirmations(self):
        control = self.runtime.control_connection()
        firm_id = int(control.execute(
            "INSERT INTO firms(name,status) VALUES('CLI Interrupted Firm','provisioning')"
        ).lastrowid)
        control.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) "
            "VALUES(?,NULL,'provisioning')",
            (firm_id,),
        )
        control.commit()

        args = (
            "reconcile-interrupted-provisioning",
            "--firm-id", str(firm_id),
            "--reason", "reconcile after host restart and confirmed worker shutdown",
            "--operator-reference", "incident-cli-123",
            "--change-reference", "change-cli-456",
        )
        refused = self.run_manage(*args)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("--confirm-workers-stopped", refused.stderr)
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "provisioning",
        )

        refused = self.run_manage(*args, "--confirm-workers-stopped")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("--confirm-reconcile", refused.stderr)
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "provisioning",
        )

        completed = self.run_manage(
            *args, "--confirm-workers-stopped", "--confirm-reconcile"
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["firm_id"], firm_id)
        self.assertEqual(report["recovery"], "reconciled_interrupted_provisioning")
        self.assertTrue(report["retry_allowed"])
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "disabled",
        )
        event = control.execute(
            "SELECT detail_json FROM platform_security_events "
            "WHERE firm_id=? AND event_type='firm_provisioning_reconciled_failed'",
            (firm_id,),
        ).fetchone()
        self.assertIsNotNone(event)
        detail = json.loads(event["detail_json"])
        self.assertEqual(detail["operator_reference"], "incident-cli-123")
        self.assertEqual(detail["change_reference"], "change-cli-456")

    def test_retry_failed_provisioning_cli_requires_confirmation_and_audits_recovery(self):
        control = self.runtime.control_connection()
        cursor = control.execute(
            "INSERT INTO firms(name,status) VALUES('Failed Firm Recovery','disabled')"
        )
        firm_id = int(cursor.lastrowid)
        control.execute(
            "INSERT INTO tenant_database_catalog(firm_id,database_file,status) VALUES(?,NULL,'failed')",
            (firm_id,),
        )
        control.commit()

        refused = self.run_manage(
            "retry-failed-provisioning",
            "--firm-id", str(firm_id),
            "--reason", "retry failed tenant initialization",
            "--operator-reference", "operator-ticket-123",
            "--change-reference", "change-456",
        )
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("--confirm-retry", refused.stderr)
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "disabled",
        )

        retried = self.run_manage(
            "retry-failed-provisioning",
            "--firm-id", str(firm_id),
            "--reason", "retry failed tenant initialization",
            "--operator-reference", "operator-ticket-123",
            "--change-reference", "change-456",
            "--confirm-retry",
        )
        self.assertEqual(retried.returncode, 0, retried.stderr)
        report = json.loads(retried.stdout)
        self.assertEqual(report["status"], "provisioned")
        self.assertEqual(report["firm_id"], firm_id)
        self.assertEqual(report["recovery"], "retried_failed_provisioning")
        self.assertTrue((self.root / "tenants" / report["database_file"]).is_file())
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()[0],
            "active",
        )
        event = control.execute(
            "SELECT detail_json FROM platform_security_events "
            "WHERE firm_id=? AND event_type='firm_provisioning_retried'",
            (firm_id,),
        ).fetchone()
        self.assertIsNotNone(event)
        detail = json.loads(event["detail_json"])
        self.assertEqual(detail["reason"], "retry failed tenant initialization")
        self.assertEqual(detail["operator_reference"], "operator-ticket-123")
        self.assertEqual(detail["change_reference"], "change-456")

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


    def test_init_tenancy_bootstraps_a_clean_install_without_platform_privileges(self):
        fresh = self.root / "fresh-bootstrap"
        fresh.mkdir()
        env = self.env.copy()
        env.update({
            "COPILOT_CONTROL_DB": str(fresh / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(fresh / "tenants"),
            "COPILOT_CORPUS_DB": str(fresh / "corpus.sqlite3"),
        })
        result = subprocess.run(
            [
                sys.executable, str(MANAGE), "init-tenancy",
                "--firm-name", "First Firm",
                "--owner-name", "Initial Owner",
                "--owner-email", "initial-owner@example.test",
            ],
            cwd=ROOT,
            env=env,
            input="StrongPassphrase-2026!\n",
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("لم يتم منح دور إداري على مستوى المنصة", result.stdout)

        runtime = DatabaseRuntime(
            env["COPILOT_CONTROL_DB"], env["COPILOT_TENANT_DB_ROOT"], env["COPILOT_CORPUS_DB"]
        )
        try:
            runtime.initialize()
            control = runtime.control_connection()
            owner = control.execute(
                "SELECT id,email_normalized,status FROM users"
            ).fetchone()
            self.assertEqual(
                (owner["email_normalized"], owner["status"]),
                ("initial-owner@example.test", "active"),
            )
            membership = control.execute(
                "SELECT firm_id,firm_role,status FROM firm_memberships WHERE user_id=?",
                (owner["id"],),
            ).fetchone()
            self.assertEqual(
                (membership["firm_role"], membership["status"]), ("admin", "active")
            )
            self.assertEqual(
                control.execute("SELECT COUNT(*) FROM firms WHERE status='active'").fetchone()[0],
                1,
            )
            self.assertEqual(
                control.execute("SELECT COUNT(*) FROM user_platform_roles WHERE user_id=?",
                                (owner["id"],)).fetchone()[0],
                0,
            )
            context = runtime.resolve_context(owner["id"], membership["firm_id"])
            self.assertTrue(runtime.firm_connection(context).execute(
                "SELECT profile FROM database_profile WHERE singleton=1"
            ).fetchone()[0] == "firm")
        finally:
            runtime.close_current_thread()

    def test_init_tenancy_refuses_to_replace_an_existing_owner(self):
        control = self.runtime.control_connection()
        firms_before = control.execute("SELECT COUNT(*) FROM firms").fetchone()[0]
        users_before = control.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        result = subprocess.run(
            [
                sys.executable, str(MANAGE), "init-tenancy",
                "--firm-name", "Must Not Be Created",
                "--owner-name", "Replacement Owner",
                "--owner-email", "replacement-owner@example.test",
            ],
            cwd=ROOT,
            env=self.env,
            input="StrongPassphrase-2026!\n",
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("active firm membership already exists", result.stderr)
        self.assertEqual(control.execute("SELECT COUNT(*) FROM firms").fetchone()[0], firms_before)
        self.assertEqual(control.execute("SELECT COUNT(*) FROM users").fetchone()[0], users_before)
        self.assertIsNone(control.execute(
            "SELECT id FROM users WHERE email_normalized='replacement-owner@example.test'"
        ).fetchone())


    def test_verify_backup_tenancy_cli_reports_verified_bundle_without_persistent_restore(self):
        backup_dir = self.root / "verification-bundles"
        backup_dir.mkdir()
        key = Fernet.generate_key()
        bundle = create_backup_bundle(
            self.runtime, Fernet(key), backup_dir, quiesced=True
        )
        env = self.env.copy()
        env["BACKUP_KEY"] = key.decode("ascii")
        temp_root = self.root / "verification-temp"
        temp_root.mkdir()
        env["TMPDIR"] = str(temp_root)
        before = {path.name for path in self.root.iterdir()}

        result = subprocess.run(
            [sys.executable, str(MANAGE), "verify-backup-tenancy", str(bundle)],
            cwd=ROOT, env=env, text=True, capture_output=True, timeout=60, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["verified"])
        self.assertEqual(report["tenant_database_count"], 1)
        self.assertFalse(report["plaintext_retained"])
        self.assertIn("not guaranteed secure erasure", report["warning"])
        self.assertEqual({path.name for path in self.root.iterdir()}, before)
        self.assertEqual(list(temp_root.iterdir()), [], "temporary plaintext restore directory must be removed")

    def test_verify_backup_tenancy_cli_rejects_wrong_key_without_persistent_restore(self):
        backup_dir = self.root / "wrong-key-bundles"
        backup_dir.mkdir()
        key = Fernet.generate_key()
        bundle = create_backup_bundle(
            self.runtime, Fernet(key), backup_dir, quiesced=True
        )
        env = self.env.copy()
        env["BACKUP_KEY"] = Fernet.generate_key().decode("ascii")
        temp_root = self.root / "wrong-key-verification-temp"
        temp_root.mkdir()
        env["TMPDIR"] = str(temp_root)
        before = {path.name for path in self.root.iterdir()}
        result = subprocess.run(
            [sys.executable, str(MANAGE), "verify-backup-tenancy", str(bundle)],
            cwd=ROOT, env=env, text=True, capture_output=True, timeout=60, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Backup verification failed", result.stderr)
        self.assertEqual({path.name for path in self.root.iterdir()}, before)
        self.assertEqual(list(temp_root.iterdir()), [], "failed verification must clean temporary plaintext")



    def test_init_tenancy_refuses_to_bootstrap_over_disabled_existing_state(self):
        self.assertTrue(self.runtime.disable_firm(self.firm_a))
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE users SET status='disabled' WHERE id=?", (self.user_id,)
        )
        control.commit()
        firms_before = control.execute("SELECT COUNT(*) FROM firms").fetchone()[0]
        users_before = control.execute("SELECT COUNT(*) FROM users").fetchone()[0]

        result = subprocess.run(
            [
                sys.executable, str(MANAGE), "init-tenancy",
                "--firm-name", "Must Not Replace Disabled State",
                "--owner-name", "Replacement Owner",
                "--owner-email", "replacement-owner@example.test",
            ],
            cwd=ROOT,
            env=self.env,
            input="StrongPassphrase-2026!\n",
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Existing identities or firm records need explicit recovery review", result.stderr)
        self.assertEqual(control.execute("SELECT COUNT(*) FROM firms").fetchone()[0], firms_before)
        self.assertEqual(control.execute("SELECT COUNT(*) FROM users").fetchone()[0], users_before)
        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (self.firm_a,)).fetchone()[0],
            "disabled",
        )
        self.assertEqual(
            control.execute("SELECT status FROM users WHERE id=?", (self.user_id,)).fetchone()[0],
            "disabled",
        )
        self.assertIsNone(control.execute(
            "SELECT id FROM users WHERE email_normalized='replacement-owner@example.test'"
        ).fetchone())



    def test_adduser_atomically_audits_identity_and_membership_creation(self):
        result = subprocess.run(
            [
                sys.executable, str(MANAGE), "adduser", "Audited User",
                "audited-user@example.test", "lawyer", "--firm-id", str(self.firm_a),
            ],
            cwd=ROOT,
            env=self.env,
            input="StrongPassphrase-2026!\n",
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        control = self.runtime.control_connection()
        user = control.execute(
            "SELECT id FROM users WHERE email_normalized='audited-user@example.test'"
        ).fetchone()
        self.assertIsNotNone(user)
        membership = control.execute(
            "SELECT status,firm_role FROM firm_memberships WHERE user_id=? AND firm_id=?",
            (user["id"], self.firm_a),
        ).fetchone()
        self.assertEqual((membership["status"], membership["firm_role"]), ("active", "lawyer"))
        events = control.execute(
            "SELECT event_type,detail_json FROM platform_security_events "
            "WHERE target_user_id=? ORDER BY id",
            (user["id"],),
        ).fetchall()
        self.assertEqual(
            [event["event_type"] for event in events],
            ["identity_created_cli", "membership_created"],
        )
        self.assertEqual(json.loads(events[0]["detail_json"]), {"method": "manage.py adduser"})
        self.assertEqual(
            json.loads(events[1]["detail_json"]),
            {"firm_role": "lawyer", "method": "manage.py adduser"},
        )

    def test_adduser_rolls_back_identity_and_membership_if_audit_fails(self):
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_adduser_membership_audit
            BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='membership_created'
            BEGIN SELECT RAISE(ABORT, 'audit unavailable'); END
        """)
        control.commit()
        result = subprocess.run(
            [
                sys.executable, str(MANAGE), "adduser", "Unaudited User",
                "unaudited-user@example.test", "lawyer", "--firm-id", str(self.firm_a),
            ],
            cwd=ROOT,
            env=self.env,
            input="StrongPassphrase-2026!\n",
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("audit unavailable", result.stderr)
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM users WHERE email_normalized='unaudited-user@example.test'"
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE user_id IN "
                "(SELECT id FROM users WHERE email_normalized='unaudited-user@example.test')"
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events "
                "WHERE event_type IN ('identity_created_cli','membership_created') "
                "AND detail_json LIKE '%manage.py adduser%'"
            ).fetchone()[0],
            0,
        )



if __name__ == "__main__":
    unittest.main()
