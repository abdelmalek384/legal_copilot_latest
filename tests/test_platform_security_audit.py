import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import manage
from database_runtime import DatabaseRuntime


class PlatformSecurityAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {
            "COPILOT_CONTROL_DB": str(self.root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(self.root / "tenants"),
            "COPILOT_CORPUS_DB": str(self.root / "corpus.sqlite3"),
        }, clear=False)
        self.env.start()
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_id, _ = self.runtime.provision_firm("Audit test firm")
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_id, "Audit Owner", "audit-owner@example.test", "old-password-hash"
        )
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO auth_sessions(token_hash,user_id,expires) VALUES('hashed-session',?,9999999999)",
            (self.user_id,),
        )
        control.commit()

    def tearDown(self):
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        self.env.stop()
        self.temp.cleanup()

    def test_password_reset_revokes_sessions_and_writes_atomic_platform_audit(self):
        with patch("manage.read_password", return_value="NewStrongPassphrase_2026"):
            manage.resetpw(Namespace(email=" AUDIT-OWNER@example.test "))
        control = self.runtime.control_connection()
        self.assertEqual(control.execute("SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (self.user_id,)).fetchone()[0], 0)
        event = control.execute(
            "SELECT actor_user_id,target_user_id,event_type,detail_json FROM platform_security_events"
        ).fetchone()
        self.assertIsNone(event["actor_user_id"])
        self.assertEqual(event["target_user_id"], self.user_id)
        self.assertEqual(event["event_type"], "password_reset_cli")
        self.assertIn('"sessions_revoked": true', event["detail_json"])
        self.assertTrue(control.execute("SELECT password_hash FROM users WHERE id=?", (self.user_id,)).fetchone()[0] != "old-password-hash")

    def test_audit_write_failure_rolls_back_password_change_and_session_revocation(self):
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_platform_audit BEFORE INSERT ON platform_security_events
            BEGIN SELECT RAISE(ABORT, 'audit unavailable'); END
        """)
        control.commit()
        old_hash = control.execute("SELECT password_hash FROM users WHERE id=?", (self.user_id,)).fetchone()[0]
        with patch("manage.read_password", return_value="NewStrongPassphrase_2026"):
            with self.assertRaisesRegex(Exception, "audit unavailable"):
                manage.resetpw(Namespace(email="audit-owner@example.test"))
        control = self.runtime.control_connection()
        self.assertEqual(control.execute("SELECT password_hash FROM users WHERE id=?", (self.user_id,)).fetchone()[0], old_hash)
        self.assertEqual(control.execute("SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (self.user_id,)).fetchone()[0], 1)
        self.assertEqual(control.execute("SELECT COUNT(*) FROM platform_security_events").fetchone()[0], 0)

    def test_platform_security_audit_is_append_only(self):
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO platform_security_events(event_type,detail_json) VALUES('firm_disabled','{}')"
        )
        control.commit()
        with self.assertRaisesRegex(Exception, "append-only"):
            control.execute("UPDATE platform_security_events SET detail_json='{}' WHERE id=1")
        control.rollback()
        with self.assertRaisesRegex(Exception, "append-only"):
            control.execute("DELETE FROM platform_security_events WHERE id=1")
        control.rollback()


if __name__ == "__main__":
    unittest.main()
