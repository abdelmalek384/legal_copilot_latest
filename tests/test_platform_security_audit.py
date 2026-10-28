import json
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
        self.reset_user_id = self.runtime.create_global_identity(
            "Audit Reset User", "audit-reset@example.test", "old-password-hash"
        )
        self.runtime.create_firm_membership(self.reset_user_id, self.firm_id, "lawyer")
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO auth_sessions(token_hash,user_id,expires) VALUES('hashed-session',?,9999999999)",
            (self.reset_user_id,),
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
            manage.resetpw(Namespace(email=" AUDIT-RESET@example.test "))
        control = self.runtime.control_connection()
        self.assertEqual(control.execute("SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (self.reset_user_id,)).fetchone()[0], 0)
        event = control.execute(
            "SELECT actor_user_id,target_user_id,event_type,detail_json FROM platform_security_events WHERE event_type='password_reset_cli'"
        ).fetchone()
        self.assertIsNone(event["actor_user_id"])
        self.assertEqual(event["target_user_id"], self.reset_user_id)
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
        old_hash = control.execute("SELECT password_hash FROM users WHERE id=?", (self.reset_user_id,)).fetchone()[0]
        with patch("manage.read_password", return_value="NewStrongPassphrase_2026"):
            with self.assertRaisesRegex(Exception, "audit unavailable"):
                manage.resetpw(Namespace(email="audit-reset@example.test"))
        control = self.runtime.control_connection()
        self.assertEqual(control.execute("SELECT password_hash FROM users WHERE id=?", (self.reset_user_id,)).fetchone()[0], old_hash)
        self.assertEqual(control.execute("SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (self.reset_user_id,)).fetchone()[0], 1)
        self.assertEqual(control.execute("SELECT COUNT(*) FROM platform_security_events WHERE event_type='password_reset_cli'").fetchone()[0], 0)

    def test_firm_lifecycle_and_membership_changes_are_audited(self):
        control = self.runtime.control_connection()
        events = {row["event_type"] for row in control.execute("SELECT event_type FROM platform_security_events")}
        self.assertIn("firm_provisioned", events)
        self.assertIn("initial_owner_bootstrapped", events)
        cursor = control.execute(
            "INSERT INTO users(name,email_display,email_normalized,password_hash,status) "
            "VALUES('Second User','second@example.test','second@example.test','test-hash','active')"
        )
        second_id = cursor.lastrowid
        control.commit()
        self.runtime.create_firm_membership(second_id, self.firm_id, "lawyer", created_by_user_id=self.user_id)
        self.assertTrue(self.runtime.disable_firm(self.firm_id))
        control = self.runtime.control_connection()
        logged = {(row["event_type"], row["target_user_id"], row["firm_id"]) for row in control.execute(
            "SELECT event_type,target_user_id,firm_id FROM platform_security_events"
        )}
        self.assertIn(("membership_created", second_id, self.firm_id), logged)
        self.assertIn(("firm_disabled", None, self.firm_id), logged)

    def test_membership_audit_failure_rolls_back_membership_and_closes_transaction(self):
        control = self.runtime.control_connection()
        cursor = control.execute(
            "INSERT INTO users(name,email_display,email_normalized,password_hash,status) "
            "VALUES('Audit target','target@example.test','target@example.test','test-hash','active')"
        )
        target_id = cursor.lastrowid
        control.execute("""
            CREATE TRIGGER reject_membership_audit BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='membership_created'
            BEGIN SELECT RAISE(ABORT, 'membership audit unavailable'); END
        """)
        control.commit()
        with self.assertRaisesRegex(Exception, "membership audit unavailable"):
            self.runtime.create_firm_membership(
                target_id, self.firm_id, "lawyer", created_by_user_id=self.user_id
            )
        self.assertFalse(control.in_transaction, "failed membership transaction must be rolled back")
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM firm_memberships WHERE user_id=? AND firm_id=?",
            (target_id, self.firm_id),
        ).fetchone()[0], 0)
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE target_user_id=? AND event_type='membership_created'",
            (target_id,),
        ).fetchone()[0], 0)

    def test_provisioning_audit_failure_leaves_firm_and_catalog_disabled(self):
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_firm_provision_audit BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='firm_provisioned'
            BEGIN SELECT RAISE(ABORT, 'provision audit unavailable'); END
        """)
        control.commit()
        with self.assertRaisesRegex(Exception, "provision audit unavailable"):
            self.runtime.provision_firm("Audit-failure firm")
        control = self.runtime.control_connection()
        firm = control.execute("SELECT id,status FROM firms WHERE name='Audit-failure firm'").fetchone()
        self.assertIsNotNone(firm)
        self.assertEqual(firm["status"], "disabled")
        catalog = control.execute("SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm["id"],)).fetchone()
        self.assertIsNotNone(catalog)
        self.assertEqual(catalog["status"], "disabled")
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE firm_id=? AND event_type='firm_provisioned'",
            (firm["id"],),
        ).fetchone()[0], 0)

    def test_cli_adduser_records_membership_without_granting_platform_role(self):
        with patch("manage.read_password", return_value="NewStrongPassphrase_2026"):
            manage.adduser(Namespace(name="CLI User", email="cli-user@example.test", role="lawyer", firm_id=self.firm_id))
        control = self.runtime.control_connection()
        target = control.execute("SELECT id FROM users WHERE email_normalized='cli-user@example.test'").fetchone()
        self.assertIsNotNone(target)
        event = control.execute(
            "SELECT event_type,firm_id,detail_json FROM platform_security_events WHERE target_user_id=? ORDER BY id DESC LIMIT 1",
            (target["id"],),
        ).fetchone()
        self.assertEqual(event["event_type"], "membership_created")
        self.assertEqual(event["firm_id"], self.firm_id)
        self.assertIn('"method": "manage.py adduser"', event["detail_json"])
        self.assertEqual(control.execute("SELECT COUNT(*) FROM user_platform_roles WHERE user_id=?", (target["id"],)).fetchone()[0], 0)

    def test_platform_audit_cli_filters_and_bounds_output(self):
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            manage.platform_audit(Namespace(limit=20, event_type="firm_provisioned", firm_id=self.firm_id, target_user_id=None))
        result = __import__("json").loads(output.getvalue())
        self.assertEqual(result["limit"], 20)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["event_type"], "firm_provisioned")
        self.assertEqual(result["items"][0]["firm_id"], self.firm_id)
        self.assertIn("detail", result["items"][0])
        with self.assertRaisesRegex(SystemExit, "between 1 and 500"):
            manage.platform_audit(Namespace(limit=501, event_type=None, firm_id=None, target_user_id=None))
        with self.assertRaisesRegex(SystemExit, "integer between 1 and 500"):
            manage.platform_audit(Namespace(limit=True, event_type=None, firm_id=None, target_user_id=None))

    def test_platform_role_grant_and_revoke_are_authorized_and_audited(self):
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_admin')",
            (self.user_id,),
        )
        target_id = self.runtime.create_global_identity(
            "Platform Target", "platform-target@example.test", "target-hash"
        )
        control.commit()
        args = Namespace(
            actor_email=" AUDIT-OWNER@example.test ", target_email="PLATFORM-TARGET@example.test",
            role="platform_reviewer", reason="Review legal corpus access",
        )
        manage.grant_platform_role(args)
        self.assertIsNotNone(control.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (target_id,),
        ).fetchone())
        granted = control.execute(
            "SELECT actor_user_id,target_user_id,event_type,detail_json FROM platform_security_events "
            "WHERE event_type='platform_role_granted' AND target_user_id=? ORDER BY id DESC LIMIT 1",
            (target_id,),
        ).fetchone()
        self.assertEqual(granted["actor_user_id"], self.user_id)
        self.assertIn("Review legal corpus access", granted["detail_json"])
        manage.revoke_platform_role(args)
        self.assertIsNone(control.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (target_id,),
        ).fetchone())
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='platform_role_revoked' AND target_user_id=?",
            (target_id,),
        ).fetchone()[0], 1)

    def test_platform_role_change_requires_admin_and_preserves_last_admin(self):
        target_id = self.runtime.create_global_identity(
            "No Privilege Target", "no-privilege@example.test", "target-hash"
        )
        control = self.runtime.control_connection()
        with self.assertRaisesRegex(SystemExit, "Only an active platform_admin"):
            manage.grant_platform_role(Namespace(
                actor_email="audit-owner@example.test", target_email="no-privilege@example.test",
                role="platform_reviewer", reason="Review legal corpus access",
            ))
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_admin')",
            (self.user_id,),
        )
        control.commit()
        with self.assertRaisesRegex(SystemExit, "last active platform_admin"):
            manage.revoke_platform_role(Namespace(
                actor_email="audit-owner@example.test", target_email="audit-owner@example.test",
                role="platform_admin", reason="Remove administrator role",
            ))
        self.assertIsNotNone(control.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (self.user_id,),
        ).fetchone())
        self.assertIsNone(control.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (target_id,),
        ).fetchone())

    def test_platform_role_revoke_rolls_back_if_audit_write_fails(self):
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_admin')",
            (self.user_id,),
        )
        target_id = self.runtime.create_global_identity(
            "Revoke Audit Target", "revoke-audit-target@example.test", "target-hash"
        )
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name,granted_by_user_id) VALUES(?,'platform_reviewer',?)",
            (target_id, self.user_id),
        )
        control.execute("""
            CREATE TRIGGER reject_platform_role_revoke_audit BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='platform_role_revoked'
            BEGIN SELECT RAISE(ABORT, 'platform role revoke audit unavailable'); END
        """)
        control.commit()
        with self.assertRaisesRegex(SystemExit, "audit write failed"):
            manage.revoke_platform_role(Namespace(
                actor_email="audit-owner@example.test", target_email="revoke-audit-target@example.test",
                role="platform_reviewer", reason="Remove reviewer access",
            ))
        self.assertIsNotNone(control.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (target_id,),
        ).fetchone())
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='platform_role_revoked' AND target_user_id=?",
            (target_id,),
        ).fetchone()[0], 0)

    def test_platform_role_grant_rolls_back_if_audit_write_fails(self):
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_admin')",
            (self.user_id,),
        )
        target_id = self.runtime.create_global_identity(
            "Audit Failure Target", "audit-failure-target@example.test", "target-hash"
        )
        control.execute("""
            CREATE TRIGGER reject_platform_role_audit BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='platform_role_granted'
            BEGIN SELECT RAISE(ABORT, 'platform role audit unavailable'); END
        """)
        control.commit()
        with self.assertRaisesRegex(SystemExit, "audit write failed"):
            manage.grant_platform_role(Namespace(
                actor_email="audit-owner@example.test", target_email="audit-failure-target@example.test",
                role="platform_reviewer", reason="Review legal corpus access",
            ))
        self.assertIsNone(control.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (target_id,),
        ).fetchone())
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='platform_role_granted' AND target_user_id=?",
            (target_id,),
        ).fetchone()[0], 0)

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

    def test_firm_disable_is_atomically_audited_and_idempotent(self):
        changed = self.runtime.disable_firm(self.firm_id)
        self.assertTrue(changed)
        control = self.runtime.control_connection()
        firm = control.execute(
            "SELECT status FROM firms WHERE id=?", (self.firm_id,)
        ).fetchone()
        catalog = control.execute(
            "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (self.firm_id,)
        ).fetchone()
        event = control.execute(
            "SELECT actor_user_id,firm_id,event_type,detail_json "
            "FROM platform_security_events WHERE event_type='firm_disabled'"
        ).fetchone()
        self.assertEqual(firm["status"], "disabled")
        self.assertEqual(catalog["status"], "disabled")
        self.assertIsNone(event["actor_user_id"])
        self.assertEqual(event["firm_id"], self.firm_id)
        self.assertEqual(event["event_type"], "firm_disabled")
        self.assertEqual(
            json.loads(event["detail_json"]),
            {"new_status": "disabled", "previous_status": "active"},
        )

        self.assertFalse(self.runtime.disable_firm(self.firm_id))
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events WHERE firm_id=? AND event_type='firm_disabled'",
                (self.firm_id,),
            ).fetchone()[0],
            1,
            "repeated disable must not duplicate the lifecycle audit event",
        )

    def test_firm_disable_rolls_back_if_platform_audit_write_fails(self):
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_firm_disable_audit
            BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='firm_disabled'
            BEGIN SELECT RAISE(ABORT, 'audit unavailable'); END
        """)
        control.commit()

        with self.assertRaisesRegex(Exception, "audit unavailable"):
            self.runtime.disable_firm(self.firm_id)

        self.assertEqual(
            control.execute("SELECT status FROM firms WHERE id=?", (self.firm_id,)).fetchone()[0],
            "active",
        )
        self.assertEqual(
            control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (self.firm_id,)
            ).fetchone()[0],
            "provisioned",
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events WHERE firm_id=? AND event_type='firm_disabled'",
                (self.firm_id,),
            ).fetchone()[0],
            0,
        )



    def test_membership_creation_rolls_back_if_audit_write_fails(self):
        target_user_id = self.runtime.create_global_identity(
            "Membership Target", "membership-target@example.test", "test-password-hash"
        )
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_membership_audit
            BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='membership_created'
            BEGIN SELECT RAISE(ABORT, 'audit unavailable'); END
        """)
        control.commit()

        with self.assertRaisesRegex(Exception, "audit unavailable"):
            self.runtime.create_firm_membership(
                target_user_id, self.firm_id, "lawyer", created_by_user_id=self.user_id
            )

        self.assertFalse(control.in_transaction, "failed audited mutation must leave no open transaction")
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE user_id=? AND firm_id=?",
                (target_user_id, self.firm_id),
            ).fetchone()[0],
            0,
            "membership must not persist when its audit event cannot be written",
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM platform_security_events "
                "WHERE event_type='membership_created' AND target_user_id=?",
                (target_user_id,),
            ).fetchone()[0],
            0,
        )



if __name__ == "__main__":
    unittest.main()
