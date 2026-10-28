import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import manage
from database_runtime import DatabaseRuntime
import app


class PlatformAdminBootstrapCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB", "COPILOT_DB",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ["COPILOT_CONTROL_DB"] = str(self.root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(self.root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(self.root / "corpus.sqlite3")
        os.environ.pop("COPILOT_DB", None)
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_id, _ = self.runtime.provision_firm("Bootstrap Firm")
        self.owner_email = "bootstrap-owner@example.test"
        self.owner_id = self.runtime.create_initial_firm_owner(
            self.firm_id, "Bootstrap Owner", self.owner_email,
            app.hash_pw("BootstrapOwnerStrongPassphrase-2026!"),
        )

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

    def _argv(self, target_user_id=None, confirm=True):
        args = [
            "bootstrap-platform-admin",
            "--target-user-id", str(self.owner_id if target_user_id is None else target_user_id),
            "--reason", "First platform administrator for pilot deployment",
            "--operator-reference", "ops-team-2026",
            "--change-reference", "CHG-2026-10-28",
        ]
        if confirm:
            args.append("--confirm-bootstrap")
        return args

    def _run(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = manage.main(args)
        return result, output.getvalue()

    def test_bootstrap_atomically_grants_first_admin_and_audits_without_email(self):
        result, output = self._run(self._argv())
        self.assertEqual(result, 0)
        report = json.loads(output)
        self.assertEqual(report, {
            "status": "bootstrapped",
            "target_user_id": self.owner_id,
            "firm_id": self.firm_id,
            "event_type": "platform_admin_bootstrap_cli",
        })
        self.assertNotIn(self.owner_email, output)
        control = self.runtime.control_connection()
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (self.owner_id,),
        ).fetchone()[0], 1)
        event = control.execute(
            "SELECT actor_user_id,target_user_id,firm_id,event_type,detail_json "
            "FROM platform_security_events WHERE event_type='platform_admin_bootstrap_cli'"
        ).fetchone()
        self.assertIsNone(event["actor_user_id"])
        self.assertEqual(event["target_user_id"], self.owner_id)
        self.assertEqual(event["firm_id"], self.firm_id)
        detail = json.loads(event["detail_json"])
        self.assertEqual(detail["reason"], "First platform administrator for pilot deployment")
        self.assertEqual(detail["operator_reference"], "ops-team-2026")
        self.assertEqual(detail["change_reference"], "CHG-2026-10-28")
        with self.assertRaises(Exception):
            control.execute(
                "UPDATE platform_security_events SET detail_json='{}' WHERE event_type='platform_admin_bootstrap_cli'"
            )
        control.rollback()

    def test_bootstrap_requires_explicit_confirmation(self):
        with self.assertRaises(SystemExit):
            self._run(self._argv(confirm=False))
        control = self.runtime.control_connection()
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM user_platform_roles WHERE role_name='platform_admin'"
        ).fetchone()[0], 0)
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='platform_admin_bootstrap_cli'"
        ).fetchone()[0], 0)

    def test_existing_admin_blocks_bootstrap(self):
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_admin')",
            (self.owner_id,),
        )
        control.commit()
        with self.assertRaises(SystemExit):
            self._run(self._argv())
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='platform_admin_bootstrap_cli'"
        ).fetchone()[0], 0)

    def test_successful_bootstrap_event_permanently_blocks_rebootstrap(self):
        self._run(self._argv())
        control = self.runtime.control_connection()
        control.execute(
            "DELETE FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (self.owner_id,),
        )
        control.commit()
        with self.assertRaises(SystemExit):
            self._run(self._argv())
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='platform_admin_bootstrap_cli'"
        ).fetchone()[0], 1)
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM user_platform_roles WHERE role_name='platform_admin'"
        ).fetchone()[0], 0)

    def test_target_without_active_firm_admin_membership_is_rejected(self):
        other_id = self.runtime.create_global_identity(
            "No Membership", "no-membership@example.test",
            app.hash_pw("NoMembershipStrongPassphrase-2026!"),
        )
        with self.assertRaises(SystemExit):
            self._run(self._argv(target_user_id=other_id))
        control = self.runtime.control_connection()
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (other_id,),
        ).fetchone()[0], 0)

    def test_disabled_firm_membership_is_rejected(self):
        self.assertTrue(self.runtime.disable_firm(self.firm_id))
        with self.assertRaises(SystemExit):
            self._run(self._argv())
        control = self.runtime.control_connection()
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM user_platform_roles WHERE role_name='platform_admin'"
        ).fetchone()[0], 0)

    def test_audit_failure_rolls_back_platform_role(self):
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_platform_admin_bootstrap_audit
            BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='platform_admin_bootstrap_cli'
            BEGIN SELECT RAISE(ABORT, 'injected bootstrap audit failure'); END
        """)
        control.commit()
        with self.assertRaises(SystemExit):
            self._run(self._argv())
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (self.owner_id,),
        ).fetchone()[0], 0)
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='platform_admin_bootstrap_cli'"
        ).fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
