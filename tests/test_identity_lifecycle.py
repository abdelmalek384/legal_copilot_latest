import hashlib
import os
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime
from identity_email import IdentityEmailError


class IdentityLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB",
            "COPILOT_PUBLIC_BASE_URL", "COPILOT_ENV", "COPILOT_DB",
            "COPILOT_EMAIL_SMTP_HOST", "COPILOT_EMAIL_FROM",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ["COPILOT_CONTROL_DB"] = str(self.root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(self.root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(self.root / "corpus.sqlite3")
        os.environ["COPILOT_PUBLIC_BASE_URL"] = "https://legal.example.test"
        os.environ.pop("COPILOT_ENV", None)
        os.environ.pop("COPILOT_DB", None)
        os.environ["COPILOT_EMAIL_SMTP_HOST"] = "smtp.example.test"
        os.environ["COPILOT_EMAIL_FROM"] = "legal-copilot@example.test"
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Invitation Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Invitation Firm B")
        self.password = "OwnerStrongPassphrase-2026!"
        self.owner_id = self.runtime.create_initial_firm_owner(
            self.firm_a, "Invitation Owner", "invitation-owner@example.test",
            app.hash_pw(self.password),
        )
        self.client = TestClient(app.app)

    def tearDown(self):
        self.client.close()
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        app._database_runtime = None
        for name, value in self.old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        self.temp.cleanup()

    def _login(self, client, email, password):
        return client.post("/login", json={"email": email, "password": password})

    def _mutate(self, method, path, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = self.client.cookies.get("lc_csrf") or ""
        return getattr(self.client, method)(path, headers=headers, **kwargs)

    @staticmethod
    def _token_from_email(mock_send):
        body = mock_send.call_args.args[2]
        match = re.search(r"#token=([A-Za-z0-9_-]+)", body)
        if not match:
            raise AssertionError("identity email did not contain a fragment token")
        return match.group(1)

    def test_identity_pages_use_csp_nonce_and_no_store_headers(self):
        for path in ("/invite/accept", "/account/recovery"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            policy = response.headers.get("Content-Security-Policy", "")
            match = re.search(r"script-src[^;]*'nonce-([^']+)'", policy)
            self.assertIsNotNone(match, policy)
            self.assertIn(f'<script nonce="{match.group(1)}">', response.text)
            self.assertEqual(response.headers.get("Cache-Control"), "no-store")
            self.assertEqual(response.headers.get("Referrer-Policy"), "no-referrer")

    def test_admin_can_list_and_revoke_only_own_firm_invitations(self):
        self.assertEqual(self._login(self.client, "invitation-owner@example.test", self.password).status_code, 200)
        with patch.object(app, "send_identity_email") as send:
            created = self._mutate(
                "post", "/invitations",
                json={"email": "revoke-me@example.test", "role": "lawyer"},
            )
        self.assertEqual(created.status_code, 200, created.text)
        token = self._token_from_email(send)
        invitation_id = created.json()["invitation_id"]

        listing = self.client.get("/invitations")
        self.assertEqual(listing.status_code, 200, listing.text)
        row = next(item for item in listing.json()["invitations"] if item["id"] == invitation_id)
        self.assertEqual(row["status"], "sent")
        self.assertEqual(row["email"], "revoke-me@example.test")
        self.assertNotIn("token_hash", row)
        self.assertNotIn(token, listing.text)

        revoked = self._mutate(
            "post", f"/invitations/{invitation_id}/revoke",
            json={"reason": "Pilot candidate withdrew"},
        )
        self.assertEqual(revoked.status_code, 200, revoked.text)
        self.assertEqual(revoked.json()["status"], "revoked")
        replay = self.client.post("/invitations/accept/new", json={
            "token": token, "name": "Revoked Candidate",
            "password": "RevokedCandidateStrongPassphrase-2026!",
        })
        self.assertEqual(replay.status_code, 400)

        firm_b_owner = self.runtime.create_initial_firm_owner(
            self.firm_b, "Firm B Owner", "firm-b-owner@example.test", app.hash_pw(self.password)
        )
        other = TestClient(app.app)
        try:
            login = self._login(other, "firm-b-owner@example.test", self.password)
            self.assertEqual(login.status_code, 200, login.text)
            other_listing = other.get("/invitations")
            self.assertEqual(other_listing.status_code, 200, other_listing.text)
            self.assertEqual(other_listing.json()["invitations"], [])
            response = other.post(
                f"/invitations/{invitation_id}/revoke",
                json={"reason": "Attempt cross-firm revocation"},
                headers={"X-CSRF-Token": other.cookies.get("lc_csrf") or ""},
            )
            self.assertEqual(response.status_code, 404, response.text)
        finally:
            other.close()
        control = self.runtime.control_connection()
        events = control.execute(
            "SELECT event_type,detail_json FROM identity_lifecycle_events "
            "WHERE invitation_id=? ORDER BY id",
            (invitation_id,),
        ).fetchall()
        self.assertEqual([event["event_type"] for event in events], [
            "invitation_created", "invitation_sent", "invitation_revoked"
        ])
        self.assertIn("Pilot candidate withdrew", events[-1]["detail_json"])

    def test_invitation_creates_new_identity_atomically_and_token_is_single_use(self):
        self.assertEqual(self._login(self.client, "invitation-owner@example.test", self.password).status_code, 200)
        with patch.object(app, "send_identity_email") as send:
            created = self._mutate(
                "post", "/invitations",
                json={"email": "New.Lawyer@example.test", "role": "lawyer"},
            )
        self.assertEqual(created.status_code, 200, created.text)
        self.assertEqual(created.json()["status"], "sent")
        self.assertNotIn("token", created.text.lower())
        send.assert_called_once()
        token = self._token_from_email(send)

        accepted = self.client.post(
            "/invitations/accept/new",
            json={
                "token": token, "name": "New Lawyer",
                "password": "NewLawyerStrongPassphrase-2026!",
            },
        )
        self.assertEqual(accepted.status_code, 200, accepted.text)
        new_user_id = self.runtime.control_connection().execute(
            "SELECT id FROM users WHERE email_normalized=?",
            ("new.lawyer@example.test",),
        ).fetchone()["id"]
        control = self.runtime.control_connection()
        membership = control.execute(
            "SELECT firm_id,firm_role,status FROM firm_memberships WHERE user_id=?",
            (new_user_id,),
        ).fetchone()
        self.assertEqual((membership["firm_id"], membership["firm_role"], membership["status"]),
                         (self.firm_a, "lawyer", "active"))
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM user_platform_roles WHERE user_id=?", (new_user_id,)
        ).fetchone()[0], 0)
        self.assertEqual(control.execute(
            "SELECT status FROM identity_invitations WHERE id=?",
            (created.json()["invitation_id"],),
        ).fetchone()["status"], "consumed")
        replay = self.client.post(
            "/invitations/accept/new",
            json={
                "token": token, "name": "Replay",
                "password": "ReplayStrongPassphrase-2026!",
            },
        )
        self.assertEqual(replay.status_code, 400)
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM users WHERE email_normalized=?",
            ("new.lawyer@example.test",),
        ).fetchone()[0], 1)

    def test_resending_invitation_revokes_previous_token(self):
        self.assertEqual(self._login(self.client, "invitation-owner@example.test", self.password).status_code, 200)
        with patch.object(app, "send_identity_email") as send:
            first = self._mutate("post", "/invitations",
                                 json={"email": "resend@example.test", "role": "junior"})
            self.assertEqual(first.status_code, 200, first.text)
            old_token = self._token_from_email(send)
            second = self._mutate("post", "/invitations",
                                  json={"email": "resend@example.test", "role": "junior"})
        self.assertEqual(second.status_code, 200, second.text)
        new_token = self._token_from_email(send)
        self.assertNotEqual(old_token, new_token)
        old = self.client.post("/invitations/accept/new", json={
            "token": old_token, "name": "Old Token",
            "password": "OldTokenStrongPassphrase-2026!",
        })
        self.assertEqual(old.status_code, 400)
        new = self.client.post("/invitations/accept/new", json={
            "token": new_token, "name": "Resend User",
            "password": "ResendUserStrongPassphrase-2026!",
        })
        self.assertEqual(new.status_code, 200, new.text)

    def test_existing_global_identity_can_accept_without_duplicate_identity(self):
        existing_id = self.runtime.create_global_identity(
            "Existing Multi Firm", "existing@example.test", app.hash_pw("ExistingStrongPassphrase-2026!")
        )
        self.runtime.create_firm_membership(existing_id, self.firm_b, "lawyer")
        self.assertEqual(self._login(self.client, "invitation-owner@example.test", self.password).status_code, 200)
        with patch.object(app, "send_identity_email") as send:
            invitation = self._mutate("post", "/invitations",
                                      json={"email": "existing@example.test", "role": "junior"})
        self.assertEqual(invitation.status_code, 200, invitation.text)
        token = self._token_from_email(send)
        existing_client = TestClient(app.app)
        try:
            login = self._login(existing_client, "existing@example.test", "ExistingStrongPassphrase-2026!")
            self.assertEqual(login.status_code, 200, login.text)
            csrf = existing_client.cookies.get("lc_csrf") or ""
            accepted = existing_client.post(
                "/invitations/accept-existing", json={"token": token},
                headers={"X-CSRF-Token": csrf},
            )
            self.assertEqual(accepted.status_code, 200, accepted.text)
        finally:
            existing_client.close()
        control = self.runtime.control_connection()
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM users WHERE email_normalized='existing@example.test'"
        ).fetchone()[0], 1)
        roles = {
            row["firm_id"]: row["firm_role"] for row in control.execute(
                "SELECT firm_id,firm_role FROM firm_memberships WHERE user_id=?", (existing_id,)
            )
        }
        self.assertEqual(roles, {self.firm_a: "junior", self.firm_b: "lawyer"})

    def test_recovery_is_generic_revokes_sessions_and_consumes_token_once(self):
        user_id = self.runtime.create_global_identity(
            "Recovery User", "recovery@example.test", app.hash_pw("RecoveryOldPassphrase-2026!")
        )
        self.runtime.create_firm_membership(user_id, self.firm_a, "lawyer")
        target = TestClient(app.app)
        try:
            self.assertEqual(self._login(target, "recovery@example.test", "RecoveryOldPassphrase-2026!").status_code, 200)
            with patch.object(app, "send_identity_email") as send:
                known = target.post("/account/recovery/request", json={"email": "recovery@example.test"})
            self.assertEqual(known.status_code, 200, known.text)
            token = self._token_from_email(send)
            unknown = target.post("/account/recovery/request", json={"email": "not-found@example.test"})
            self.assertEqual(unknown.status_code, 200)
            self.assertEqual(known.json(), unknown.json())
            self.assertNotIn(token, known.text)

            reset = target.post("/account/recovery/consume", json={
                "token": token, "new_password": "RecoveryNewPassphrase-2026!",
            })
            self.assertEqual(reset.status_code, 200, reset.text)
            old_session = target.get("/session")
            self.assertEqual(old_session.status_code, 401)
            self.assertEqual(self._login(target, "recovery@example.test", "RecoveryOldPassphrase-2026!").status_code, 401)
            self.assertEqual(self._login(target, "recovery@example.test", "RecoveryNewPassphrase-2026!").status_code, 200)
            replay = target.post("/account/recovery/consume", json={
                "token": token, "new_password": "AnotherRecoveryPassphrase-2026!",
            })
            self.assertEqual(replay.status_code, 400)
        finally:
            target.close()
        control = self.runtime.control_connection()
        self.assertEqual(control.execute(
            "SELECT status FROM password_recovery_tokens ORDER BY id DESC LIMIT 1"
        ).fetchone()["status"], "consumed")
        event = control.execute(
            "SELECT detail_json FROM identity_lifecycle_events WHERE event_type='recovery_consumed' "
            "AND target_user_id=? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        self.assertIn('"sessions_revoked":true', event["detail_json"])

    def test_recovery_email_budget_cannot_be_bypassed_by_rotating_source_ips(self):
        user_id = self.runtime.create_global_identity(
            "Distributed Recovery User", "distributed-recovery@example.test",
            app.hash_pw("DistributedRecoveryPassphrase-2026!"),
        )
        self.runtime.create_firm_membership(user_id, self.firm_a, "lawyer")
        request = app.RecoveryRequestIn(email="distributed-recovery@example.test")
        with patch.object(app, "_send_identity_link") as send:
            responses = [
                app.request_account_recovery(
                    request,
                    SimpleNamespace(client=SimpleNamespace(host=f"192.0.2.{index}")),
                )
                for index in range(1, 7)
            ]
        self.assertTrue(all(response == app._identity_recovery_generic_response() for response in responses))
        self.assertEqual(send.call_count, 5)
        control = self.runtime.control_connection()
        rate_limit = control.execute(
            "SELECT hits FROM api_rate_limit_windows WHERE bucket='identity_recovery_email' "
            "AND client_key=?",
            (hashlib.sha256(b"distributed-recovery@example.test").hexdigest(),),
        ).fetchone()
        self.assertEqual(rate_limit["hits"], 6)
        event = control.execute(
            "SELECT detail_json FROM identity_lifecycle_events WHERE event_type='recovery_rate_limited' "
            "AND target_user_id=? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        self.assertIn('"bucket":"identity_recovery_email"', event["detail_json"])

    def test_recovery_audit_failure_rolls_back_password_session_and_token(self):
        old_password = "AuditRecoveryOldPassphrase-2026!"
        new_password = "AuditRecoveryNewPassphrase-2026!"
        user_id = self.runtime.create_global_identity(
            "Audit Recovery User", "audit-recovery@example.test", app.hash_pw(old_password)
        )
        self.runtime.create_firm_membership(user_id, self.firm_a, "lawyer")
        target = TestClient(app.app)
        try:
            self.assertEqual(self._login(target, "audit-recovery@example.test", old_password).status_code, 200)
            with patch.object(app, "send_identity_email") as send:
                requested = target.post(
                    "/account/recovery/request", json={"email": "audit-recovery@example.test"}
                )
            self.assertEqual(requested.status_code, 200)
            token = self._token_from_email(send)
            control = self.runtime.control_connection()
            old_hash = control.execute(
                "SELECT password_hash FROM users WHERE id=?", (user_id,)
            ).fetchone()["password_hash"]
            control.execute("""
                CREATE TRIGGER reject_recovery_consumed_audit
                BEFORE INSERT ON identity_lifecycle_events
                WHEN NEW.event_type='recovery_consumed'
                BEGIN SELECT RAISE(ABORT, 'injected recovery audit failure'); END
            """)
            control.commit()
            reset = target.post("/account/recovery/consume", json={
                "token": token, "new_password": new_password,
            })
            self.assertEqual(reset.status_code, 503, reset.text)
            self.assertEqual(target.get("/session").status_code, 200)
            self.assertEqual(control.execute(
                "SELECT password_hash FROM users WHERE id=?", (user_id,)
            ).fetchone()["password_hash"], old_hash)
            self.assertEqual(control.execute(
                "SELECT status FROM password_recovery_tokens ORDER BY id DESC LIMIT 1"
            ).fetchone()["status"], "sent")
            self.assertEqual(control.execute(
                "SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (user_id,)
            ).fetchone()[0], 1)
        finally:
            target.close()

    def test_privileged_account_recovery_requires_assisted_verification(self):
        self.assertEqual(self._login(self.client, "invitation-owner@example.test", self.password).status_code, 200)
        with patch.object(app, "send_identity_email") as send:
            response = self.client.post(
                "/account/recovery/request", json={"email": "invitation-owner@example.test"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), app._identity_recovery_generic_response())
        send.assert_not_called()
        control = self.runtime.control_connection()
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM password_recovery_tokens t JOIN users u ON u.id=t.user_id "
            "WHERE u.email_normalized='invitation-owner@example.test'"
        ).fetchone()[0], 0)

    def test_invitation_audit_failure_rolls_back_identity_membership_and_consumption(self):
        self.assertEqual(self._login(self.client, "invitation-owner@example.test", self.password).status_code, 200)
        with patch.object(app, "send_identity_email") as send:
            invitation = self._mutate("post", "/invitations",
                                      json={"email": "rollback@example.test", "role": "lawyer"})
        self.assertEqual(invitation.status_code, 200, invitation.text)
        token = self._token_from_email(send)
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_invitation_accept_audit
            BEFORE INSERT ON identity_lifecycle_events
            WHEN NEW.event_type='invitation_accepted'
            BEGIN SELECT RAISE(ABORT, 'injected invitation audit failure'); END
        """)
        control.commit()
        accepted = self.client.post("/invitations/accept/new", json={
            "token": token, "name": "Rollback User",
            "password": "RollbackStrongPassphrase-2026!",
        })
        self.assertEqual(accepted.status_code, 503, accepted.text)
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM users WHERE email_normalized='rollback@example.test'"
        ).fetchone()[0], 0)
        self.assertEqual(control.execute(
            "SELECT status FROM identity_invitations WHERE id=?",
            (invitation.json()["invitation_id"],),
        ).fetchone()["status"], "sent")


if __name__ == "__main__":
    unittest.main()
