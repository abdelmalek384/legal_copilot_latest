import os
import sqlite3
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class SeparateDatabaseApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env_names = ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB",
                          "COPILOT_OBJECT_STORAGE_ROOT", "COPILOT_OBJECT_STORAGE_BACKEND",
                          "COPILOT_ENV", "ADMIN_TOKEN")
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ["COPILOT_CONTROL_DB"] = str(self.root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(self.root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(self.root / "corpus.sqlite3")
        os.environ["COPILOT_OBJECT_STORAGE_ROOT"] = str(self.root / "objects")
        os.environ["COPILOT_OBJECT_STORAGE_BACKEND"] = "local"
        os.environ["COPILOT_ENV"] = "development"
        self.admin_token = "test-only-shared-corpus-import-token-2026"
        os.environ["ADMIN_TOKEN"] = self.admin_token
        app._database_runtime = None

        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Firm B")
        self.password = "LongUniqueTestPassphrase-2026!"
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_a, "First Owner", "owner@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(self.user_id, self.firm_b, "lawyer")
        self.client = TestClient(app.app)

    def tearDown(self):
        self.client.close()
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

    def _mutate(self, method, url, **kwargs):
        csrf = self.client.cookies.get("lc_csrf")
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = csrf or ""
        return getattr(self.client, method)(url, headers=headers, **kwargs)

    def test_web_user_creation_records_platform_membership_audit(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/users",
            json={"name": "Audited User", "email": "audited-user@example.test",
                  "password": self.password, "role": "lawyer"},
        )
        self.assertEqual(created.status_code, 200, created.text)
        control = self.runtime.control_connection()
        event = control.execute(
            "SELECT actor_user_id,target_user_id,firm_id,event_type,detail_json FROM platform_security_events "
            "WHERE event_type='membership_created' AND target_user_id=? ORDER BY id DESC LIMIT 1",
            (created.json()["id"],),
        ).fetchone()
        self.assertIsNotNone(event)
        self.assertEqual(event["actor_user_id"], self.user_id)
        self.assertEqual(event["firm_id"], self.firm_a)
        self.assertIn('"method": "web"', event["detail_json"])

    def test_membership_suspension_audit_failure_keeps_membership_active(self):
        target_id = self.runtime.create_global_identity(
            "Suspension Audit Target", "suspension-audit-target@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(target_id, self.firm_a, "lawyer")
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_membership_suspension_audit BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='membership_suspended'
            BEGIN SELECT RAISE(ABORT, 'membership suspension audit unavailable'); END
        """)
        control.commit()
        response = self._mutate("post", f"/users/{target_id}/disable")
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(control.execute(
            "SELECT status FROM firm_memberships WHERE user_id=? AND firm_id=?",
            (target_id, self.firm_a),
        ).fetchone()["status"], "active")
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='membership_suspended' AND target_user_id=?",
            (target_id,),
        ).fetchone()[0], 0)

    def test_web_user_creation_audit_failure_rolls_back_identity_and_membership(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        control = self.runtime.control_connection()
        before_events = control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='membership_created'"
        ).fetchone()[0]
        control.execute("""
            CREATE TRIGGER reject_membership_creation_audit BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='membership_created'
            BEGIN SELECT RAISE(ABORT, 'membership creation audit unavailable'); END
        """)
        control.commit()
        response = self._mutate(
            "post", "/users",
            json={"name": "Not Created", "email": "not-created@example.test",
                  "password": self.password, "role": "lawyer"},
        )
        self.assertEqual(response.status_code, 503, response.text)
        self.assertIsNone(control.execute(
            "SELECT id FROM users WHERE email_normalized='not-created@example.test'"
        ).fetchone())
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='membership_created'"
        ).fetchone()[0], before_events)

    def test_membership_writers_recheck_active_firm_inside_write_transaction(self):
        target_user = self.runtime.create_global_identity(
            "Second Firm User", "second-firm-user@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(target_user, self.firm_b, "admin")
        self.assertTrue(self.runtime.disable_firm(self.firm_a))
        admin_context = {"id": self.user_id, "firm_id": self.firm_a, "role": "admin"}

        with self.assertRaises(HTTPException) as create_error:
            app.create_user(
                app.UserCreateIn(
                    name="Must Not Exist",
                    email="must-not-exist@example.test",
                    password=self.password,
                    role="lawyer",
                ),
                admin_context,
            )
        self.assertEqual(create_error.exception.status_code, 409)

        with self.assertRaises(HTTPException) as membership_error:
            app.add_existing_user_membership(
                app.ExistingMembershipIn(email="second-firm-user@example.test", role="lawyer"),
                admin_context,
            )
        self.assertEqual(membership_error.exception.status_code, 409)

        control = self.runtime.control_connection()
        self.assertIsNone(
            control.execute(
                "SELECT id FROM users WHERE email_normalized=?",
                ("must-not-exist@example.test",),
            ).fetchone()
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE user_id=? AND firm_id=?",
                (target_user, self.firm_a),
            ).fetchone()[0],
            0,
        )

    def test_disabled_global_identity_cannot_receive_new_membership(self):
        firm_c, _ = self.runtime.provision_firm("Disabled Identity Firm")
        disabled_user_id = self.runtime.create_initial_firm_owner(
            firm_c, "Disabled Owner", "disabled-owner@example.test", app.hash_pw(self.password)
        )
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE users SET status='disabled',updated_at=datetime('now') WHERE id=?",
            (disabled_user_id,),
        )
        control.commit()

        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        response = self._mutate(
            "post", "/memberships",
            json={"email": "disabled-owner@example.test", "role": "lawyer"},
        )
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE user_id=? AND firm_id=?",
                (disabled_user_id, self.firm_a),
            ).fetchone()[0],
            0,
        )

    def test_existing_session_loses_suspended_firm_access_immediately(self):
        target_id = self.runtime.create_global_identity(
            "Existing Session Target", "existing-session-target@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(target_id, self.firm_a, "lawyer")
        self.runtime.create_firm_membership(target_id, self.firm_b, "lawyer")
        target_client = TestClient(app.app)
        try:
            target_login = target_client.post(
                "/login",
                json={"email": "existing-session-target@example.test", "password": self.password},
            )
            self.assertEqual(target_login.status_code, 200, target_login.text)
            csrf = target_client.cookies.get("lc_csrf") or ""
            selected_a = target_client.post(
                "/session/firm", json={"firm_id": self.firm_a},
                headers={"X-CSRF-Token": csrf},
            )
            self.assertEqual(selected_a.status_code, 200, selected_a.text)
            self.assertEqual(target_client.get("/cases").status_code, 200)

            owner_login = self.client.post(
                "/login", json={"email": "owner@example.test", "password": self.password},
            )
            self.assertEqual(owner_login.status_code, 200, owner_login.text)
            suspended = self._mutate("post", f"/users/{target_id}/disable")
            self.assertEqual(suspended.status_code, 200, suspended.text)

            # Keep the same authenticated session and cached firm connection:
            # the next request must re-check membership instead of trusting cache.
            denied_a = target_client.get("/cases")
            self.assertEqual(denied_a.status_code, 403, denied_a.text)
            selected_b = target_client.post(
                "/session/firm", json={"firm_id": self.firm_b},
                headers={"X-CSRF-Token": csrf},
            )
            self.assertEqual(selected_b.status_code, 200, selected_b.text)
            self.assertEqual(target_client.get("/cases").status_code, 200)
        finally:
            target_client.close()

    def test_suspending_one_membership_preserves_other_firm_access(self):
        target_id = self.runtime.create_global_identity(
            "Multi-firm Target", "multi-firm-target@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(target_id, self.firm_a, "lawyer")
        self.runtime.create_firm_membership(target_id, self.firm_b, "lawyer")
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        disabled = self._mutate("post", f"/users/{target_id}/disable")
        self.assertEqual(disabled.status_code, 200, disabled.text)
        self.assertTrue(disabled.json()["membership_suspended"])
        control = self.runtime.control_connection()
        self.assertEqual(
            control.execute("SELECT status FROM users WHERE id=?", (target_id,)).fetchone()["status"],
            "active",
        )
        memberships = {
            row["firm_id"]: row["status"] for row in control.execute(
                "SELECT firm_id,status FROM firm_memberships WHERE user_id=?", (target_id,)
            ).fetchall()
        }
        self.assertEqual(memberships[self.firm_a], "suspended")
        self.assertEqual(memberships[self.firm_b], "active")
        suspended_event = control.execute(
            "SELECT actor_user_id,target_user_id,firm_id,event_type FROM platform_security_events "
            "WHERE event_type='membership_suspended' AND target_user_id=? ORDER BY id DESC LIMIT 1",
            (target_id,),
        ).fetchone()
        self.assertIsNotNone(suspended_event)
        self.assertEqual(suspended_event["actor_user_id"], self.user_id)
        self.assertEqual(suspended_event["firm_id"], self.firm_a)

        from fastapi.testclient import TestClient
        target_client = TestClient(app.app)
        try:
            target_login = target_client.post(
                "/login", json={"email": "multi-firm-target@example.test", "password": self.password}
            )
            self.assertEqual(target_login.status_code, 200, target_login.text)
            denied_a = target_client.post(
                "/session/firm", json={"firm_id": self.firm_a},
                headers={"X-CSRF-Token": target_client.cookies.get("lc_csrf") or ""},
            )
            self.assertEqual(denied_a.status_code, 403, denied_a.text)
            allowed_b = target_client.post(
                "/session/firm", json={"firm_id": self.firm_b},
                headers={"X-CSRF-Token": target_client.cookies.get("lc_csrf") or ""},
            )
            self.assertEqual(allowed_b.status_code, 200, allowed_b.text)
            self.assertEqual(target_client.get("/cases").status_code, 200)
        finally:
            target_client.close()

    def test_firm_admin_cannot_suspend_another_firms_membership(self):
        firm_b_only_user = self.runtime.create_global_identity(
            "Firm B Only User", "firm-b-admin-isolation@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(firm_b_only_user, self.firm_b, "lawyer")
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        denied = self._mutate("post", f"/users/{firm_b_only_user}/disable")
        self.assertEqual(denied.status_code, 404, denied.text)
        membership = self.runtime.control_connection().execute(
            "SELECT status FROM firm_memberships WHERE user_id=? AND firm_id=?",
            (firm_b_only_user, self.firm_b),
        ).fetchone()
        self.assertIsNotNone(membership)
        self.assertEqual(membership["status"], "active")
        self.assertEqual(
            self.runtime.control_connection().execute(
                "SELECT status FROM users WHERE id=?", (firm_b_only_user,)
            ).fetchone()["status"],
            "active",
        )

    def test_user_listing_is_scoped_to_active_firm_memberships(self):
        firm_b_only_user = self.runtime.create_global_identity(
            "Firm B Only User", "firm-b-only@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(firm_b_only_user, self.firm_b, "lawyer")
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        firm_a_users = self.client.get("/users")
        self.assertEqual(firm_a_users.status_code, 200, firm_a_users.text)
        self.assertFalse(any(row["id"] == firm_b_only_user for row in firm_a_users.json()))

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        firm_b_users = self.client.get("/users")
        self.assertEqual(firm_b_users.status_code, 200, firm_b_users.text)
        self.assertTrue(any(row["id"] == firm_b_only_user for row in firm_b_users.json()))

    def test_existing_global_identity_can_join_another_firm_without_duplication(self):
        firm_c, _ = self.runtime.provision_firm("Firm C")
        existing_user_id = self.runtime.create_initial_firm_owner(
            firm_c, "Second Firm Owner", "second-owner@example.test", app.hash_pw(self.password)
        )

        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        added = self._mutate(
            "post",
            "/memberships",
            json={"email": " SECOND-OWNER@EXAMPLE.TEST ", "role": "lawyer"},
        )
        self.assertEqual(added.status_code, 201, added.text)
        self.assertEqual(added.json()["user_id"], existing_user_id)
        self.assertEqual(added.json()["firm_id"], self.firm_a)

        control = self.runtime.control_connection()
        created_event = control.execute(
            "SELECT actor_user_id,target_user_id,firm_id,event_type FROM platform_security_events "
            "WHERE event_type='membership_created' AND target_user_id=? AND firm_id=? ORDER BY id DESC LIMIT 1",
            (existing_user_id, self.firm_a),
        ).fetchone()
        self.assertIsNotNone(created_event)
        self.assertEqual(created_event["actor_user_id"], self.user_id)
        memberships = control.execute(
            "SELECT firm_id,firm_role,status FROM firm_memberships WHERE user_id=? ORDER BY firm_id",
            (existing_user_id,),
        ).fetchall()
        self.assertEqual(
            [(row["firm_id"], row["firm_role"], row["status"]) for row in memberships],
            [(self.firm_a, "lawyer", "active"), (firm_c, "admin", "active")],
        )
        listed = self.client.get("/users")
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertTrue(any(row["id"] == existing_user_id for row in listed.json()))

        duplicate = self._mutate(
            "post", "/memberships",
            json={"email": "second-owner@example.test", "role": "lawyer"},
        )
        self.assertEqual(duplicate.status_code, 409, duplicate.text)
        missing = self._mutate(
            "post", "/memberships",
            json={"email": "unknown@example.test", "role": "lawyer"},
        )
        self.assertEqual(missing.status_code, 404, missing.text)
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE user_id=?",
                (existing_user_id,),
            ).fetchone()[0],
            2,
        )

    def test_case_delete_audit_failure_rolls_back_entire_deletion(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/cases", json={"title": "Deletion rollback sentinel"}
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]

        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        tenant_db = self.runtime.firm_connection(context)
        tenant_db.execute("""
            CREATE TRIGGER reject_case_deletion_audit
            BEFORE INSERT ON case_deletion_audit
            BEGIN SELECT RAISE(ABORT, 'injected audit persistence failure'); END
        """)
        tenant_db.commit()

        response = self._mutate("delete", f"/cases/{case_id}")
        self.assertEqual(response.status_code, 503, response.text)
        self.assertIsNotNone(
            tenant_db.execute(
                "SELECT id FROM cases WHERE id=? AND firm_id=?", (case_id, self.firm_a)
            ).fetchone(),
            "a case must not be deleted if its required audit snapshot cannot persist",
        )
        self.assertEqual(
            tenant_db.execute(
                "SELECT COUNT(*) FROM case_deletion_audit WHERE case_id=? AND firm_id=?",
                (case_id, self.firm_a),
            ).fetchone()[0],
            0,
        )
        self.assertIsNotNone(
            tenant_db.execute(
                "SELECT id FROM events WHERE case_id=?", (case_id,)
            ).fetchone(),
            "related matter history must remain intact after failed deletion",
        )

    def test_case_detail_hydrates_identity_names_from_control_plane_view(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate("post", "/cases", json={"title": "Identity Hydration Matter"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]

        member_id = self.runtime.create_global_identity(
            "Matter Associate", "matter-associate@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(member_id, self.firm_a, "lawyer")
        added = self._mutate(
            "post", f"/cases/{case_id}/members", json={"user_id": member_id, "role": "associate"}
        )
        self.assertEqual(added.status_code, 200, added.text)
        task = self._mutate(
            "post", f"/cases/{case_id}/tasks", json={"title": "Assigned to associate", "assignee": member_id}
        )
        self.assertEqual(task.status_code, 200, task.text)
        note = self._mutate(
            "post", f"/cases/{case_id}/notes", json={"text": "Identity hydration note"}
        )
        self.assertEqual(note.status_code, 200, note.text)

        detail = self.client.get(f"/cases/{case_id}")
        self.assertEqual(detail.status_code, 200, detail.text)
        body = detail.json()
        self.assertTrue(any(
            row["user_id"] == member_id and row["name"] == "Matter Associate"
            for row in body["members"]
        ))
        self.assertTrue(any(
            row["assignee"] == member_id and row["assignee_name"] == "Matter Associate"
            for row in body["tasks"]
        ))
        self.assertTrue(any(
            row["author"] == "First Owner" and row["text"] == "Identity hydration note"
            for row in body["notes"]
        ))

    def test_case_detail_update_and_delete_are_isolated_between_firms(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/cases", json={"title": "Firm A protected matter"}
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]

        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        db_a = self.runtime.firm_connection(context_a)
        self.assertEqual(
            db_a.execute("SELECT title FROM cases WHERE id=?", (case_id,)).fetchone()[0],
            "Firm A protected matter",
        )
        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)

        detail = self.client.get(f"/cases/{case_id}")
        self.assertEqual(detail.status_code, 404, detail.text)
        update = self._mutate(
            "patch", f"/cases/{case_id}", json={"stage": "closed"}
        )
        self.assertEqual(update.status_code, 404, update.text)
        deletion = self._mutate("delete", f"/cases/{case_id}")
        self.assertEqual(deletion.status_code, 404, deletion.text)

        self.assertEqual(
            db_a.execute("SELECT title FROM cases WHERE id=?", (case_id,)).fetchone()[0],
            "Firm A protected matter",
        )

    def test_child_writes_reject_a_case_id_from_another_firm(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/cases", json={"title": "Firm A child-write boundary"}
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        attempts = (
            ("post", f"/cases/{case_id}/notes", {"text": "cross-firm note"}),
            ("post", f"/cases/{case_id}/deadlines", {"title": "Cross-firm deadline", "due": "2027-01-15"}),
            ("post", f"/cases/{case_id}/fees", {"title": "Cross-firm fee", "amount": 100, "paid": 0}),
            ("post", f"/cases/{case_id}/sessions", {"date": "2027-01-15", "note": "cross-firm session"}),
        )
        for method, path, payload in attempts:
            with self.subTest(path=path):
                response = self._mutate(method, path, json=payload)
                self.assertEqual(response.status_code, 404, response.text)

        upload = self._mutate(
            "post", f"/cases/{case_id}/upload",
            files={"file": ("private.txt", b"private source text", "text/plain")},
        )
        self.assertEqual(upload.status_code, 404, upload.text)

        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        context_b = self.runtime.resolve_context(self.user_id, self.firm_b)
        db_a = self.runtime.firm_connection(context_a)
        db_b = self.runtime.firm_connection(context_b)
        for table in ("notes", "deadlines", "fees", "sessions"):
            with self.subTest(table=table):
                self.assertEqual(db_a.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)
                self.assertEqual(db_b.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)
        self.assertEqual(
            db_a.execute("SELECT title FROM cases WHERE id=?", (case_id,)).fetchone()[0],
            "Firm A child-write boundary",
        )

    def test_original_file_upload_download_integrity_and_cross_firm_denial(self):
        import hashlib
        import io
        from docx import Document

        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate("post", "/cases", json={"title": "Original File Test"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]

        buffer = io.BytesIO()
        source = Document()
        source.add_paragraph("Confidential original contract text for storage verification.")
        source.save(buffer)
        original = buffer.getvalue()
        with patch.object(app, "_mfa_required_for_user", return_value=False):
            uploaded = self._mutate(
                "post", f"/cases/{case_id}/upload",
                files={"file": ("original-contract.docx", original,
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        body = uploaded.json()
        self.assertTrue(body["original_file_retained"])
        document_id = body["document_id"]

        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        firm_db = self.runtime.firm_connection(context)
        # Keep a read snapshot open while another request writes its audit event.
        # WAL must allow the download/audit write to complete without blocking.
        if not firm_db.in_transaction:
            firm_db.execute("BEGIN")
        metadata = firm_db.execute(
            "SELECT object_id,sha256,byte_size,state FROM original_file_objects WHERE document_id=? AND firm_id=?",
            (document_id, self.firm_a),
        ).fetchone()
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["state"], "ready")
        self.assertEqual(metadata["sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(metadata["byte_size"], len(original))
        self.assertTrue((self.root / "objects" / f"firm-{self.firm_a}" /
                         (metadata["object_id"] + ".blob")).is_file())

        downloaded = self.client.get(f"/cases/{case_id}/docs/{document_id}/original")
        self.assertEqual(downloaded.status_code, 200, downloaded.text)
        self.assertEqual(downloaded.content, original)
        self.assertEqual(downloaded.headers["content-type"], "application/octet-stream")
        self.assertEqual(downloaded.headers["cache-control"], "no-store")
        # End the older snapshot before checking the newly committed audit row.
        firm_db.commit()
        self.assertTrue(firm_db.execute(
            "SELECT 1 FROM security_audit_events WHERE firm_id=? AND user_id=? AND event=?",
            (self.firm_a, self.user_id, f"original_document_download:{document_id}"),
        ).fetchone())

        # A case member who is not a firm admin must not be able to change legal holds.
        member_id = self.runtime.create_global_identity(
            "Original File Junior", "original-file-junior@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(member_id, self.firm_a, "lawyer")
        added_member = self._mutate(
            "post", f"/cases/{case_id}/members", json={"user_id": member_id, "role": "junior"}
        )
        self.assertEqual(added_member.status_code, 200, added_member.text)
        member_client = TestClient(app.app)
        try:
            member_login = member_client.post(
                "/login", json={"email": "original-file-junior@example.test", "password": self.password}
            )
            self.assertEqual(member_login.status_code, 200, member_login.text)
            member_csrf = member_client.cookies.get("lc_csrf") or ""
            denied_hold = member_client.post(
                f"/cases/{case_id}/docs/{document_id}/original/legal-hold",
                json={"reason": "unauthorized hold attempt"},
                headers={"X-CSRF-Token": member_csrf},
            )
            self.assertEqual(denied_hold.status_code, 403, denied_hold.text)
        finally:
            member_client.close()

        # A failed audit insert must abort the hold state change atomically.
        firm_db.execute("""
            CREATE TRIGGER reject_original_hold_audit
            BEFORE INSERT ON security_audit_events
            WHEN NEW.event LIKE 'original_document_legal_hold_set:%'
            BEGIN SELECT RAISE(ABORT, 'hold audit unavailable'); END
        """)
        firm_db.commit()
        failed_hold = self._mutate(
            "post",
            f"/cases/{case_id}/docs/{document_id}/original/legal-hold",
            json={"reason": "This hold must roll back"},
        )
        self.assertEqual(failed_hold.status_code, 503, failed_hold.text)
        firm_db.commit()
        self.assertEqual(
            firm_db.execute(
                "SELECT legal_hold FROM original_file_objects WHERE document_id=?", (document_id,)
            ).fetchone()["legal_hold"],
            0,
        )
        firm_db.execute("DROP TRIGGER reject_original_hold_audit")
        firm_db.commit()

        held = self._mutate(
            "post",
            f"/cases/{case_id}/docs/{document_id}/original/legal-hold",
            json={"reason": "Preserve original evidence for pending proceedings"},
        )
        self.assertEqual(held.status_code, 200, held.text)
        self.assertTrue(held.json()["legal_hold"])
        firm_db.commit()
        hold_metadata = firm_db.execute(
            "SELECT legal_hold,hold_reason,hold_set_by,hold_set_at FROM original_file_objects WHERE document_id=?",
            (document_id,),
        ).fetchone()
        self.assertEqual(hold_metadata["legal_hold"], 1)
        self.assertEqual(hold_metadata["hold_reason"], "Preserve original evidence for pending proceedings")
        self.assertEqual(hold_metadata["hold_set_by"], self.user_id)
        self.assertTrue(hold_metadata["hold_set_at"])

        with self.assertRaises(sqlite3.IntegrityError):
            firm_db.execute(
                "DELETE FROM original_file_objects WHERE document_id=?", (document_id,)
            )
        firm_db.rollback()

        released = self._mutate(
            "post",
            f"/cases/{case_id}/docs/{document_id}/original/legal-hold/release",
            json={"reason": "The preservation instruction has been withdrawn"},
        )
        self.assertEqual(released.status_code, 200, released.text)
        self.assertFalse(released.json()["legal_hold"])
        firm_db.commit()
        release_metadata = firm_db.execute(
            "SELECT legal_hold,hold_released_by,hold_released_at,hold_release_reason "
            "FROM original_file_objects WHERE document_id=?",
            (document_id,),
        ).fetchone()
        self.assertEqual(release_metadata["legal_hold"], 0)
        self.assertEqual(release_metadata["hold_released_by"], self.user_id)
        self.assertTrue(release_metadata["hold_released_at"])
        self.assertEqual(
            release_metadata["hold_release_reason"], "The preservation instruction has been withdrawn"
        )
        for event in (
            f"original_document_legal_hold_set:{document_id}",
            f"original_document_legal_hold_released:{document_id}",
        ):
            self.assertTrue(firm_db.execute(
                "SELECT 1 FROM security_audit_events WHERE firm_id=? AND user_id=? AND event=?",
                (self.firm_a, self.user_id, event),
            ).fetchone(), event)

        hold_events = firm_db.execute(
            "SELECT id,action,reason,actor_user_id,occurred_at FROM original_file_hold_events "
            "WHERE firm_id=? AND document_id=? ORDER BY id",
            (self.firm_a, document_id),
        ).fetchall()
        self.assertEqual([event["action"] for event in hold_events], ["set", "release"])
        self.assertEqual(
            [event["reason"] for event in hold_events],
            [
                "Preserve original evidence for pending proceedings",
                "The preservation instruction has been withdrawn",
            ],
        )
        self.assertEqual([event["actor_user_id"] for event in hold_events], [self.user_id, self.user_id])
        self.assertTrue(all(event["occurred_at"] for event in hold_events))
        history_response = self.client.get(
            f"/cases/{case_id}/docs/{document_id}/original/legal-hold/events"
        )
        self.assertEqual(history_response.status_code, 200, history_response.text)
        self.assertEqual(
            [event["reason"] for event in history_response.json()["events"]],
            [
                "Preserve original evidence for pending proceedings",
                "The preservation instruction has been withdrawn",
            ],
        )
        with self.assertRaises(sqlite3.IntegrityError):
            firm_db.execute(
                "UPDATE original_file_hold_events SET reason='rewritten history' WHERE id=?",
                (hold_events[0]["id"],),
            )
        firm_db.rollback()
        with self.assertRaises(sqlite3.IntegrityError):
            firm_db.execute(
                "DELETE FROM original_file_hold_events WHERE id=?",
                (hold_events[0]["id"],),
            )
        firm_db.rollback()

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        denied = self.client.get(f"/cases/{case_id}/docs/{document_id}/original")
        self.assertEqual(denied.status_code, 404, denied.text)
        denied_history = self.client.get(
            f"/cases/{case_id}/docs/{document_id}/original/legal-hold/events"
        )
        self.assertEqual(denied_history.status_code, 404, denied_history.text)

    def test_original_file_deletion_requires_distinct_admin_and_legal_hold_cancels_it(self):
        import hashlib
        from original_file_storage import LocalPrivateObjectStore

        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate("post", "/cases", json={"title": "Deletion Workflow Matter"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]

        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        firm_db = self.runtime.firm_connection(context)
        original = b"original evidence for deletion workflow"
        _, document_id = app.save_doc(
            firm_db,
            {"id": self.user_id, "firm_id": self.firm_a, "name": "First Owner"},
            case_id,
            "deletion-workflow.txt",
            "Extracted evidence text",
            content_hash=hashlib.sha256(original).hexdigest(),
            content_type="text/plain",
            byte_size=len(original),
        )
        store = LocalPrivateObjectStore(self.root / "objects")
        staged = store.stage(self.firm_a, original)
        store.finalize(self.firm_a, staged.object_id)
        firm_db.execute(
            "INSERT INTO original_file_objects("
            "object_id,document_id,firm_id,storage_backend,sha256,byte_size,content_type,state"
            ") VALUES(?,?,?,'local',?,?,?,'ready')",
            (
                staged.object_id, document_id, self.firm_a, staged.sha256,
                staged.byte_size, "text/plain",
            ),
        )
        firm_db.commit()

        requested = self._mutate(
            "post",
            f"/cases/{case_id}/docs/{document_id}/original/deletion-requests",
            json={"reason": "Remove a duplicate original after export review"},
        )
        self.assertEqual(requested.status_code, 200, requested.text)
        request_id = requested.json()["request_id"]

        same_admin_approval = self._mutate(
            "post",
            f"/cases/{case_id}/docs/{document_id}/original/deletion-requests/{request_id}/approve",
            json={"reason": "Attempted self-approval"},
        )
        self.assertEqual(same_admin_approval.status_code, 403, same_admin_approval.text)

        second_id = self.runtime.create_global_identity(
            "Second Firm Admin", "second-deletion-admin@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(second_id, self.firm_a, "admin")
        second_client = TestClient(app.app)
        try:
            second_login = second_client.post(
                "/login",
                json={"email": "second-deletion-admin@example.test", "password": self.password},
            )
            self.assertEqual(second_login.status_code, 200, second_login.text)
            approved = second_client.post(
                f"/cases/{case_id}/docs/{document_id}/original/deletion-requests/{request_id}/approve",
                json={"reason": "Second admin confirms approved export and deletion"},
                headers={"X-CSRF-Token": second_client.cookies.get("lc_csrf") or ""},
            )
            self.assertEqual(approved.status_code, 200, approved.text)
        finally:
            second_client.close()

        # A new legal hold supersedes a pending approved purge and appends an audit event.
        held = self._mutate(
            "post",
            f"/cases/{case_id}/docs/{document_id}/original/legal-hold",
            json={"reason": "Preserve evidence for newly identified litigation"},
        )
        self.assertEqual(held.status_code, 200, held.text)
        listed = self.client.get(
            f"/cases/{case_id}/docs/{document_id}/original/deletion-requests"
        )
        self.assertEqual(listed.status_code, 200, listed.text)
        request_record = listed.json()["requests"][0]
        self.assertEqual(request_record["status"], "cancelled")
        self.assertEqual(
            [event["action"] for event in request_record["events"]],
            ["requested", "approved", "cancelled"],
        )
        self.assertEqual(
            request_record["events"][-1]["reason"], "Automatically cancelled by legal hold"
        )

        under_hold = self._mutate(
            "post",
            f"/cases/{case_id}/docs/{document_id}/original/deletion-requests",
            json={"reason": "Must be rejected while held"},
        )
        self.assertEqual(under_hold.status_code, 409, under_hold.text)
        self.assertTrue(store.verify(
            self.firm_a, staged.object_id,
            expected_sha256=staged.sha256, expected_size=staged.byte_size,
        ))

    def test_original_file_storage_fails_closed_in_production_until_backend_is_available(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate("post", "/cases", json={"title": "Production Storage Gate"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        from docx import Document
        import io
        buffer = io.BytesIO()
        document = Document()
        document.add_paragraph("Production gate test content")
        document.save(buffer)
        os.environ["COPILOT_ENV"] = "production"
        os.environ["COPILOT_OBJECT_STORAGE_BACKEND"] = "s3"
        try:
            with patch.object(app, "_mfa_required_for_user", return_value=False):
                response = self._mutate(
                    "post", f"/cases/{case_id}/upload",
                    files={"file": ("production-gate.docx", buffer.getvalue(),
                                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                )
        finally:
            os.environ["COPILOT_ENV"] = "development"
            os.environ["COPILOT_OBJECT_STORAGE_BACKEND"] = "local"
        self.assertEqual(response.status_code, 503, response.text)
        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        firm_db = self.runtime.firm_connection(context)
        self.assertEqual(firm_db.execute(
            "SELECT COUNT(*) FROM docs WHERE case_id=?", (case_id,)
        ).fetchone()[0], 0)

    def test_cross_firm_document_and_membership_writes_are_denied(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/cases", json={"title": "Firm A document boundary"}
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        context_a_before = self.runtime.resolve_context(self.user_id, self.firm_a)
        db_a_before = self.runtime.firm_connection(context_a_before)
        initial_member_count = db_a_before.execute(
            "SELECT COUNT(*) FROM members WHERE case_id=?", (case_id,)
        ).fetchone()[0]
        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)

        attempts = (
            ("post", f"/cases/{case_id}/docs", {"name": "secret.txt", "text": "firm A private evidence"}),
            ("post", f"/cases/{case_id}/members", {"user_id": self.user_id, "role": "lead"}),
            ("post", f"/cases/{case_id}/tasks", {"title": "Cross-firm task"}),
        )
        for method, path, payload in attempts:
            with self.subTest(path=path):
                response = self._mutate(method, path, json=payload)
                self.assertEqual(response.status_code, 404, response.text)

        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        context_b = self.runtime.resolve_context(self.user_id, self.firm_b)
        db_a = self.runtime.firm_connection(context_a)
        db_b = self.runtime.firm_connection(context_b)
        self.assertEqual(db_a.execute("SELECT COUNT(*) FROM docs WHERE case_id=?", (case_id,)).fetchone()[0], 0)
        self.assertEqual(db_a.execute("SELECT COUNT(*) FROM tasks WHERE case_id=?", (case_id,)).fetchone()[0], 0)
        self.assertEqual(db_a.execute("SELECT COUNT(*) FROM members WHERE case_id=?", (case_id,)).fetchone()[0], initial_member_count)
        for table in ("docs", "tasks", "members"):
            with self.subTest(table=table):
                self.assertEqual(db_b.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)

    def test_legacy_review_capability_respects_email_allowlist(self):
        previous = os.environ.get("LEGAL_REVIEWER_EMAILS")
        os.environ["LEGAL_REVIEWER_EMAILS"] = "reviewer@example.test"
        try:
            with patch.object(app, "_separate_runtime_enabled", return_value=False):
                self.assertTrue(app._user_can_review_legal({
                    "id": 10, "role": "admin", "email": "REVIEWER@example.test"
                }))
                self.assertFalse(app._user_can_review_legal({
                    "id": 11, "role": "admin", "email": "other@example.test"
                }))
                self.assertFalse(app._user_can_review_legal({
                    "id": 12, "role": "member", "email": "reviewer@example.test"
                }))
        finally:
            if previous is None:
                os.environ.pop("LEGAL_REVIEWER_EMAILS", None)
            else:
                os.environ["LEGAL_REVIEWER_EMAILS"] = previous

    def test_platform_reviewer_role_is_separate_and_revocation_is_immediate(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        corpus = self.runtime.legal_corpus_connection()
        corpus.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("platform-review-source", "Platform review test", "https://example.test/source"),
        )
        corpus.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
            ("platform-review-doc", "platform-review-source", "Review test document", "statute"),
        )
        corpus.execute(
            "INSERT INTO legal_document_versions(version_id,document_id,version_label,source_url) VALUES(?,?,?,?)",
            (777, "platform-review-doc", "v1", "https://example.test/source/v1"),
        )
        corpus.commit()
        payload = {"review_type": "source_authenticity", "outcome": "pending", "notes": "test event"}
        url = "/legal-review/versions/777/events"

        # Firm-owner/admin membership does not imply a platform reviewer role.
        denied = self._mutate("post", url, json=payload)
        self.assertEqual(denied.status_code, 403, denied.text)

        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,?)",
            (self.user_id, "platform_reviewer"),
        )
        control.commit()
        allowed = self._mutate("post", url, json=payload)
        self.assertEqual(allowed.status_code, 201, allowed.text)

        control.execute(
            "DELETE FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (self.user_id,),
        )
        control.commit()
        denied_after_revocation = self._mutate("post", url, json=payload)
        self.assertEqual(denied_after_revocation.status_code, 403, denied_after_revocation.text)
        self.assertEqual(
            corpus.execute("SELECT COUNT(*) FROM legal_review_events WHERE version_id=777").fetchone()[0],
            1,
        )

    def test_dashboard_calendar_and_finance_are_isolated_between_firms(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/cases", json={"title": "FIRM_A_PRIVATE_DASHBOARD_SENTINEL"}
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        deadline = self._mutate(
            "post", f"/cases/{case_id}/deadlines",
            json={"title": "FIRM_A_PRIVATE_DEADLINE_SENTINEL", "due": "2026-11-10"},
        )
        self.assertEqual(deadline.status_code, 200, deadline.text)
        fee = self._mutate(
            "post", f"/cases/{case_id}/fees",
            json={"title": "FIRM_A_PRIVATE_FEE_SENTINEL", "amount": 1234, "paid": 0, "due": "2026-11-10"},
        )
        self.assertEqual(fee.status_code, 200, fee.text)

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        dashboard = self.client.get("/dashboard")
        self.assertEqual(dashboard.status_code, 200, dashboard.text)
        self.assertNotIn("FIRM_A_PRIVATE", dashboard.text)
        calendar = self.client.get("/calendar.ics")
        self.assertEqual(calendar.status_code, 200, calendar.text)
        self.assertNotIn("FIRM_A_PRIVATE", calendar.text)
        finance = self.client.get("/finance/overview")
        self.assertEqual(finance.status_code, 200, finance.text)
        self.assertEqual(finance.json()["fee_count"], 0)
        self.assertEqual(finance.json()["total_amount"], 0)

    def test_conflict_check_does_not_disclose_other_firm_matter(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/cases",
            json={"title": "Firm A conflict sentinel", "opposing_party": "CONFIDENTIAL_FIRM_A_OPPOSING_PARTY"},
        )
        self.assertEqual(created.status_code, 200, created.text)

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        response = self._mutate(
            "post", "/conflicts", json={"q": "CONFIDENTIAL_FIRM_A_OPPOSING_PARTY"}
        )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["matches"], [])
        self.assertFalse(result["possible_conflict"])
        self.assertFalse(result["admin_review_required"])

    def test_platform_reviewer_role_guards_all_shared_corpus_review_reads(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        self.assertFalse(login.json()["can_review_legal"])
        self.assertFalse(self.client.get("/session").json()["can_review_legal"])
        corpus = self.runtime.legal_corpus_connection()
        corpus.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("review-read-source", "Review read test", "https://example.test/source"),
        )
        corpus.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
            ("review-read-doc", "review-read-source", "Review read document", "statute"),
        )
        corpus.execute(
            "INSERT INTO legal_document_versions(version_id,document_id,version_label,source_url) VALUES(?,?,?,?)",
            (778, "review-read-doc", "v1", "https://example.test/source/v1"),
        )
        corpus.commit()
        urls = [
            "/legal-review/queue",
            "/legal-review/coverage",
            "/legal-review/catalog?kind=sources",
            "/legal-review/versions/778/events",
        ]

        for url in urls:
            with self.subTest(url=url):
                denied = self.client.get(url)
                self.assertEqual(denied.status_code, 403, denied.text)

        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,?)",
            (self.user_id, "platform_reviewer"),
        )
        control.commit()
        self.assertTrue(self.client.get("/session").json()["can_review_legal"])
        for url in urls:
            with self.subTest(url=url, role="platform_reviewer"):
                allowed = self.client.get(url)
                self.assertEqual(allowed.status_code, 200, allowed.text)

        control.execute(
            "DELETE FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (self.user_id,),
        )
        control.commit()
        self.assertFalse(self.client.get("/session").json()["can_review_legal"])
        for url in urls:
            with self.subTest(url=url, role="revoked"):
                denied = self.client.get(url)
                self.assertEqual(denied.status_code, 403, denied.text)

    def test_platform_reviewer_role_guards_shared_corpus_review_writes(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        corpus = self.runtime.legal_corpus_connection()
        corpus.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("review-write-source", "Review write test", "https://example.test/source"),
        )
        corpus.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
            ("review-write-doc", "review-write-source", "Review write document", "statute"),
        )
        corpus.execute(
            "INSERT INTO legal_document_versions(version_id,document_id,version_label,source_url) VALUES(?,?,?,?)",
            (779, "review-write-doc", "v1", "https://example.test/source/v1"),
        )
        corpus.commit()

        payload = {
            "review_type": "legal_status",
            "outcome": "pending",
            "notes": "Synthetic authorization regression test",
        }
        endpoint = "/legal-review/versions/779/events"
        denied = self._mutate("post", endpoint, json=payload)
        self.assertEqual(denied.status_code, 403, denied.text)

        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,?)",
            (self.user_id, "platform_reviewer"),
        )
        control.commit()
        allowed = self._mutate("post", endpoint, json=payload)
        self.assertEqual(allowed.status_code, 201, allowed.text)
        self.assertFalse(allowed.json()["status_changed"])

        control.execute(
            "DELETE FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (self.user_id,),
        )
        control.commit()
        denied_after_revocation = self._mutate("post", endpoint, json=payload)
        self.assertEqual(denied_after_revocation.status_code, 403, denied_after_revocation.text)
        self.assertEqual(
            corpus.execute(
                "SELECT COUNT(*) FROM legal_review_events WHERE version_id=779"
            ).fetchone()[0],
            1,
            "revoked platform role must not append a review event",
        )

    def test_shared_registry_discovery_never_returns_private_firm_documents(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/cases", json={"title": "Private matter discovery isolation"}
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        private_doc = self._mutate(
            "post", f"/cases/{case_id}/docs",
            json={"name": "PRIVATE_FIRM_ONLY_DISCOVERY_SENTINEL.pdf",
                  "text": "Confidential private firm document contents for discovery isolation test."},
        )
        self.assertEqual(private_doc.status_code, 200, private_doc.text)

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        response = self._mutate(
            "post", "/research/discover", json={"q": "PRIVATE_FIRM_ONLY_DISCOVERY_SENTINEL"}
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["scope"], "metadata_only")
        self.assertEqual(response.json()["results"], [])
        self.assertFalse(response.json()["found"])

        # Metadata discovery is not the only public search path: ordinary
        # retrieval with no case_id must also exclude other firms' matter chunks.
        for endpoint in ("/search", "/ask"):
            retrieved = self._mutate(
                "post", endpoint,
                json={"q": "PRIVATE_FIRM_ONLY_DISCOVERY_SENTINEL", "scope": "all_permitted"},
            )
            self.assertEqual(retrieved.status_code, 200, retrieved.text)
            self.assertNotIn("PRIVATE_FIRM_ONLY_DISCOVERY_SENTINEL", retrieved.text)

    def test_search_and_ask_reject_case_ids_from_another_firm(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        created_case = self._mutate(
            "post", "/cases", json={"title": "Firm A confidential search matter"}
        )
        self.assertEqual(created_case.status_code, 200, created_case.text)
        case_id = created_case.json()["id"]
        uploaded = self._mutate(
            "post", f"/cases/{case_id}/docs",
            json={"name": "search-private.txt", "text": "FIRM_A_ONLY_SEARCH_SENTINEL " * 12},
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)

        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        db_a = self.runtime.firm_connection(context_a)
        self.assertEqual(
            db_a.execute("SELECT COUNT(*) FROM docs WHERE case_id=?", (case_id,)).fetchone()[0],
            1,
        )
        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)

        for endpoint in ("/search", "/ask"):
            response = self._mutate(
                "post", endpoint,
                json={"q": "FIRM_A_ONLY_SEARCH_SENTINEL", "case_id": case_id,
                      "scope": "all_permitted"},
            )
            self.assertEqual(response.status_code, 404, f"{endpoint}: {response.text}")
            self.assertNotIn("FIRM_A_ONLY_SEARCH_SENTINEL", response.text)

        # Cross-firm attempts cannot change the source firm's case or document.
        self.assertEqual(
            db_a.execute("SELECT COUNT(*) FROM cases WHERE id=?", (case_id,)).fetchone()[0],
            1,
        )
        self.assertEqual(
            db_a.execute("SELECT COUNT(*) FROM docs WHERE case_id=?", (case_id,)).fetchone()[0],
            1,
        )

    def test_child_records_and_task_actions_are_isolated_between_firms(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        created = self._mutate("post", "/cases", json={"title": "Firm A child-record matter"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        task_response = self._mutate(
            "post", f"/cases/{case_id}/tasks", json={"title": "Firm A confidential task"}
        )
        self.assertEqual(task_response.status_code, 200, task_response.text)

        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        firm_a_db = self.runtime.firm_connection(context_a)
        task = firm_a_db.execute(
            "SELECT id,title FROM tasks WHERE case_id=?", (case_id,)
        ).fetchone()
        self.assertIsNotNone(task)
        task_id = task["id"]

        switched = self._mutate(
            "post", "/session/firm", json={"firm_id": self.firm_b}
        )
        self.assertEqual(switched.status_code, 200, switched.text)
        self.assertEqual(self.client.get("/cases").json(), [])

        # A child-record ID from Firm A must not resolve against Firm B's DB.
        cross_firm_action = self._mutate("post", f"/tasks/{task_id}/done")
        self.assertEqual(cross_firm_action.status_code, 404, cross_firm_action.text)
        context_b = self.runtime.resolve_context(self.user_id, self.firm_b)
        firm_b_db = self.runtime.firm_connection(context_b)
        self.assertEqual(
            firm_b_db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0], 0
        )
        self.assertEqual(
            firm_a_db.execute("SELECT title FROM tasks WHERE id=?", (task_id,)).fetchone()[0],
            "Firm A confidential task",
        )

    def test_disabled_firm_is_denied_at_api_and_retains_its_database(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        created = self._mutate(
            "post", "/cases", json={"title": "Disabled firm retained sentinel"}
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        control = self.runtime.control_connection()
        filename = control.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=?",
            (self.firm_b,),
        ).fetchone()["database_file"]
        database_path = self.root / "tenants" / filename

        self.assertTrue(self.runtime.disable_firm(self.firm_b))
        denied = self.client.get("/cases")
        self.assertEqual(denied.status_code, 403, denied.text)
        status = control.execute("SELECT status FROM firms WHERE id=?", (self.firm_b,)).fetchone()["status"]
        self.assertEqual(status, "disabled")
        self.assertTrue(database_path.is_file())

        import sqlite3
        read_only = sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            row = read_only.execute("SELECT title FROM cases WHERE id=?", (case_id,)).fetchone()
            self.assertEqual(row[0], "Disabled firm retained sentinel")
        finally:
            read_only.close()

    def test_password_change_audit_failure_rolls_back_credential_and_sessions(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        control = self.runtime.control_connection()
        control.execute("""
            CREATE TRIGGER reject_web_password_audit BEFORE INSERT ON platform_security_events
            WHEN NEW.event_type='password_changed_web'
            BEGIN SELECT RAISE(ABORT, 'password audit unavailable'); END
        """)
        control.commit()
        before_hash = control.execute("SELECT password_hash FROM users WHERE id=?", (self.user_id,)).fetchone()[0]
        response = self._mutate(
            "post", "/account/password",
            json={"current_password": self.password,
                  "new_password": "EvenLongerUniqueTestPassphrase-2026!"},
        )
        self.assertEqual(response.status_code, 503, response.text)
        control = self.runtime.control_connection()
        after_hash = control.execute("SELECT password_hash FROM users WHERE id=?", (self.user_id,)).fetchone()[0]
        self.assertEqual(after_hash, before_hash)
        self.assertGreater(control.execute("SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (self.user_id,)).fetchone()[0], 0)
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM platform_security_events WHERE event_type='password_changed_web' AND target_user_id=?",
            (self.user_id,),
        ).fetchone()[0], 0)

    def test_password_change_revokes_sessions_across_all_firm_memberships(self):
        first_login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(first_login.status_code, 200, first_login.text)
        from fastapi.testclient import TestClient
        other_client = TestClient(app.app)
        try:
            second_login = other_client.post(
                "/login", json={"email": "OWNER@example.test", "password": self.password}
            )
            self.assertEqual(second_login.status_code, 200, second_login.text)
            switch = other_client.post(
                "/session/firm", json={"firm_id": self.firm_b},
                headers={"X-CSRF-Token": other_client.cookies.get("lc_csrf") or ""},
            )
            self.assertEqual(switch.status_code, 200, switch.text)
            self.assertEqual(other_client.get("/cases").status_code, 200)

            changed = self._mutate(
                "post", "/account/password",
                json={"current_password": self.password,
                      "new_password": "EvenLongerUniqueTestPassphrase-2026!"},
            )
            self.assertEqual(changed.status_code, 200, changed.text)
            self.assertEqual(other_client.get("/cases").status_code, 401)
            self.assertEqual(
                self.runtime.control_connection().execute(
                    "SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (self.user_id,)
                ).fetchone()[0],
                0,
            )
            event = self.runtime.control_connection().execute(
                "SELECT actor_user_id,target_user_id,event_type,detail_json FROM platform_security_events "
                "WHERE event_type='password_changed_web' AND target_user_id=? ORDER BY id DESC LIMIT 1",
                (self.user_id,),
            ).fetchone()
            self.assertIsNotNone(event)
            self.assertEqual(event["actor_user_id"], self.user_id)
            self.assertIn('"sessions_revoked": true', event["detail_json"])
            self.assertEqual(
                self.runtime.control_connection().execute(
                    "SELECT status FROM firm_memberships WHERE user_id=? AND firm_id=?",
                    (self.user_id, self.firm_b),
                ).fetchone()["status"],
                "active",
            )
            new_login = self.client.post(
                "/login", json={"email": "OWNER@example.test",
                                "password": "EvenLongerUniqueTestPassphrase-2026!"},
            )
            self.assertEqual(new_login.status_code, 200, new_login.text)
        finally:
            other_client.close()

    def test_deadline_action_cannot_mutate_another_firms_deadline(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate("post", "/cases", json={"title": "Firm A deadline action matter"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        created_deadline = self._mutate(
            "post", f"/cases/{case_id}/deadlines",
            json={"title": "Firm A protected deadline", "due": "2099-01-01"},
        )
        self.assertEqual(created_deadline.status_code, 200, created_deadline.text)
        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        db_a = self.runtime.firm_connection(context_a)
        deadline_id = db_a.execute(
            "SELECT id FROM deadlines WHERE case_id=?", (case_id,)
        ).fetchone()["id"]

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        denied = self._mutate("post", f"/deadlines/{deadline_id}/done")
        self.assertEqual(denied.status_code, 404, denied.text)
        self.assertEqual(
            db_a.execute("SELECT status FROM deadlines WHERE id=?", (deadline_id,)).fetchone()["status"],
            "open",
        )
        context_b = self.runtime.resolve_context(self.user_id, self.firm_b)
        db_b = self.runtime.firm_connection(context_b)
        self.assertEqual(db_b.execute("SELECT COUNT(*) FROM deadlines").fetchone()[0], 0)

    def test_cross_firm_task_claim_and_completion_are_denied(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate("post", "/cases", json={"title": "Firm A task action matter"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        created_task = self._mutate(
            "post", f"/cases/{case_id}/tasks", json={"title": "Firm A protected task"}
        )
        self.assertEqual(created_task.status_code, 200, created_task.text)
        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        db_a = self.runtime.firm_connection(context_a)
        task = db_a.execute(
            "SELECT id,status,assignee FROM tasks WHERE case_id=?", (case_id,)
        ).fetchone()
        task_id = task["id"]

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        self.assertEqual(self._mutate("post", f"/tasks/{task_id}/claim").status_code, 404)
        self.assertEqual(self._mutate("post", f"/tasks/{task_id}/done").status_code, 404)
        after = db_a.execute(
            "SELECT status,assignee FROM tasks WHERE id=?", (task_id,)
        ).fetchone()
        self.assertEqual(after["status"], "open")
        self.assertIsNone(after["assignee"])
        context_b = self.runtime.resolve_context(self.user_id, self.firm_b)
        db_b = self.runtime.firm_connection(context_b)
        self.assertEqual(db_b.execute("SELECT COUNT(*) FROM tasks").fetchone()[0], 0)

    def test_nonmember_cannot_switch_firms_and_revoked_membership_blocks_cached_session(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        unassigned_firm, _ = self.runtime.provision_firm("Unassigned Firm")
        denied = self._mutate(
            "post", "/session/firm", json={"firm_id": unassigned_firm}
        )
        self.assertEqual(denied.status_code, 403, denied.text)

        switched = self._mutate(
            "post", "/session/firm", json={"firm_id": self.firm_b}
        )
        self.assertEqual(switched.status_code, 200, switched.text)
        # Prime the tenant connection cache before revoking membership.
        self.assertEqual(self.client.get("/cases").status_code, 200)

        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='revoked', updated_at=datetime('now') "
            "WHERE user_id=? AND firm_id=?",
            (self.user_id, self.firm_b),
        )
        control.commit()

        # Every request must revalidate membership, even with a cached firm DB
        # connection and a still-valid authentication session cookie.
        denied_after_revocation = self.client.get("/cases")
        self.assertEqual(denied_after_revocation.status_code, 403,
                         denied_after_revocation.text)
        self.assertEqual(
            self.runtime.firm_connection(
                self.runtime.resolve_context(self.user_id, self.firm_a)
            ).execute("SELECT COUNT(*) FROM cases").fetchone()[0],
            0,
        )

    def test_audit_lists_and_csv_exports_are_scoped_to_active_firm(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        db_a = self.runtime.firm_connection(context_a)
        db_a.execute(
            "INSERT INTO case_deletion_audit(firm_id,case_id,actor_user_id,actor_name,"
            "case_snapshot_json,events_snapshot_json,related_counts_json) VALUES(?,?,?,?,?,?,?)",
            (self.firm_a, 101, self.user_id, "Owner A", '{"title":"FIRM_A_AUDIT_SENTINEL"}', "[]", "{}"),
        )
        db_a.execute(
            "INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(?,?,?)",
            (self.firm_a, self.user_id, "FIRM_A_SECURITY_SENTINEL"),
        )
        db_a.commit()

        context_b = self.runtime.resolve_context(self.user_id, self.firm_b)
        db_b = self.runtime.firm_connection(context_b)
        db_b.execute(
            "INSERT INTO case_deletion_audit(firm_id,case_id,actor_user_id,actor_name,"
            "case_snapshot_json,events_snapshot_json,related_counts_json) VALUES(?,?,?,?,?,?,?)",
            (self.firm_b, 202, self.user_id, "Owner B", '{"title":"FIRM_B_AUDIT_SENTINEL"}', "[]", "{}"),
        )
        db_b.execute(
            "INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(?,?,?)",
            (self.firm_b, self.user_id, "FIRM_B_SECURITY_SENTINEL"),
        )
        db_b.commit()

        audit_a = self.client.get("/audit/case-deletions")
        self.assertEqual(audit_a.status_code, 200, audit_a.text)
        self.assertEqual([item["firm_id"] for item in audit_a.json()["items"]], [self.firm_a])
        self.assertIn("FIRM_A_AUDIT_SENTINEL", audit_a.text)
        self.assertNotIn("FIRM_B_AUDIT_SENTINEL", audit_a.text)

        events_a = self.client.get("/audit/security-events")
        self.assertEqual(events_a.status_code, 200, events_a.text)
        self.assertEqual([item["firm_id"] for item in events_a.json()["items"]], [self.firm_a])
        csv_a = self.client.get("/audit/security-events.csv")
        self.assertEqual(csv_a.status_code, 200, csv_a.text)
        self.assertIn("FIRM_A_SECURITY_SENTINEL", csv_a.text)
        self.assertNotIn("FIRM_B_SECURITY_SENTINEL", csv_a.text)

        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET firm_role='admin' WHERE user_id=? AND firm_id=?",
            (self.user_id, self.firm_b),
        )
        control.commit()
        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)

        audit_b = self.client.get("/audit/case-deletions")
        self.assertEqual(audit_b.status_code, 200, audit_b.text)
        self.assertEqual([item["firm_id"] for item in audit_b.json()["items"]], [self.firm_b])
        self.assertIn("FIRM_B_AUDIT_SENTINEL", audit_b.text)
        self.assertNotIn("FIRM_A_AUDIT_SENTINEL", audit_b.text)

        events_b = self.client.get("/audit/security-events")
        self.assertEqual(events_b.status_code, 200, events_b.text)
        self.assertEqual([item["firm_id"] for item in events_b.json()["items"]], [self.firm_b])
        csv_b = self.client.get("/audit/security-events.csv")
        self.assertEqual(csv_b.status_code, 200, csv_b.text)
        self.assertIn("FIRM_B_SECURITY_SENTINEL", csv_b.text)
        self.assertNotIn("FIRM_A_SECURITY_SENTINEL", csv_b.text)

    def test_document_extraction_review_routes_are_isolated_across_firms(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        created_case = self._mutate("post", "/cases", json={"title": "Firm A review matter"})
        self.assertEqual(created_case.status_code, 200, created_case.text)
        case_id = created_case.json()["id"]
        uploaded = self._mutate(
            "post",
            f"/cases/{case_id}/docs",
            json={"name": "private-review.txt", "text": "CONFIDENTIAL-REVIEW-SENTINEL " * 12},
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        document_id = uploaded.json()["document_id"]
        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        firm_a_db = self.runtime.firm_connection(context_a)
        chunk = firm_a_db.execute(
            "SELECT id,text FROM chunks WHERE document_id=? AND case_id=? ORDER BY id LIMIT 1",
            (document_id, case_id),
        ).fetchone()
        self.assertIsNotNone(chunk)
        chunk_id, original_text = chunk["id"], chunk["text"]
        import hashlib
        original_digest = hashlib.sha256(original_text.encode("utf-8")).hexdigest()

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        for method, url, kwargs in (
            ("get", f"/cases/{case_id}/docs/{document_id}/reviews", {}),
            ("get", f"/cases/{case_id}/docs/{document_id}/chunks", {}),
            ("post", f"/cases/{case_id}/docs/{document_id}/chunks/{chunk_id}/review", {
                "json": {
                    "outcome": "corrected",
                    "corrected_text": "UNAUTHORIZED-CROSS-FIRM-CORRECTION",
                    "expected_text_sha256": original_digest,
                },
            }),
        ):
            response = self._mutate(method, url, **kwargs) if method != "get" else self.client.get(url)
            self.assertEqual(response.status_code, 404, response.text)

        # Denied review requests must not alter the source firm's extracted text.
        unchanged = firm_a_db.execute(
            "SELECT text FROM chunks WHERE id=? AND document_id=? AND case_id=?",
            (chunk_id, document_id, case_id),
        ).fetchone()
        self.assertIsNotNone(unchanged)
        self.assertEqual(unchanged["text"], original_text)
        self.assertEqual(
            firm_a_db.execute(
                "SELECT COUNT(*) FROM document_extraction_reviews WHERE chunk_id=?",
                (chunk_id,),
            ).fetchone()[0],
            0,
        )

    def test_research_conversations_are_isolated_across_firms(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        created = self._mutate("post", "/research/conversations")
        self.assertEqual(created.status_code, 200, created.text)
        conversation_id = created.json()["id"]
        context_a = self.runtime.resolve_context(self.user_id, self.firm_a)
        firm_a_db = self.runtime.firm_connection(context_a)
        self.assertEqual(
            firm_a_db.execute(
                "SELECT COUNT(*) FROM research_conversations WHERE id=? AND firm_id=? AND user_id=?",
                (conversation_id, self.firm_a, self.user_id),
            ).fetchone()[0],
            1,
        )

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        self.assertEqual(self.client.get("/research/conversations").json(), [])

        detail = self.client.get(f"/research/conversations/{conversation_id}")
        self.assertEqual(detail.status_code, 404, detail.text)
        rename = self._mutate(
            "patch", f"/research/conversations/{conversation_id}",
            json={"title": "Unauthorized cross-firm rename"},
        )
        self.assertEqual(rename.status_code, 404, rename.text)
        send_message = self._mutate(
            "post", f"/research/conversations/{conversation_id}/messages",
            json={"message": "CONFIDENTIAL-RESEARCH-SENTINEL", "scope": "verified_corpus"},
        )
        self.assertEqual(send_message.status_code, 404, send_message.text)
        save_to_matter = self._mutate(
            "post", f"/research/conversations/{conversation_id}/save-to-matter",
            json={"case_id": 1, "message_id": 1},
        )
        self.assertEqual(save_to_matter.status_code, 404, save_to_matter.text)
        delete = self._mutate("delete", f"/research/conversations/{conversation_id}")
        self.assertEqual(delete.status_code, 404, delete.text)

        # Attempts in Firm B must not mutate or delete Firm A's conversation.
        self.assertEqual(
            firm_a_db.execute(
                "SELECT COUNT(*) FROM research_conversations WHERE id=? AND firm_id=?",
                (conversation_id, self.firm_a),
            ).fetchone()[0],
            1,
        )
        self.assertEqual(
            firm_a_db.execute(
                "SELECT COUNT(*) FROM research_messages WHERE conversation_id=?",
                (conversation_id,),
            ).fetchone()[0],
            0,
        )

    def test_login_firm_switch_and_shared_corpus_are_separated(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        self.assertEqual(len(login.json()["firms"]), 2)
        self.assertEqual(login.json()["firm_id"], self.firm_a)

        created = self._mutate("post", "/cases", json={"title": "Firm A matter"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        uploaded = self._mutate(
            "post",
            f"/cases/{case_id}/docs",
            json={"name": "private.txt", "text": "firmonlysentinel confidential matter passage"},
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        matter_search = self._mutate(
            "post",
            "/search",
            json={"q": "firmonlysentinel", "case_id": case_id, "scope": "firm_documents"},
        )
        self.assertEqual(matter_search.status_code, 200, matter_search.text)
        self.assertTrue(any("firmonlysentinel" in hit["text"] for hit in matter_search.json()))

        # The legal corpus is central and shared; matter content is not.
        corpus = self.runtime.legal_corpus_connection()
        corpus.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page,collection_permission,"
            "commercial_reuse_permission,permission_evidence) VALUES(?,?,?,?,?,?)",
            ("test-source", "Test authority", "https://example.test/law", "allowed", "allowed", "test evidence"),
        )
        corpus.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type,practice_area) "
            "VALUES(?,?,?,?,?)",
            ("test-law", "test-source", "Test Law", "statute", "general"),
        )
        version_id = corpus.execute(
            "INSERT INTO legal_document_versions(document_id,version_label,source_url,effective_date,"
            "legal_status,review_status,authenticity_verified,status_verified,amendment_history_verified,"
            "permission_evidence) VALUES(?,?,?,?,?,?,?,?,?,?)",
            ("test-law", "current", "https://example.test/law/current", "2020-01-01",
             "in_force", "verified", 1, 1, 1, "version evidence"),
        ).lastrowid
        for review_type in ("source_authenticity", "extraction_quality", "legal_status", "amendment_history", "licensing", "lawyer_approval"):
            corpus.execute(
                "INSERT INTO legal_review_events(version_id,reviewer,review_type,outcome,notes,evidence_url) VALUES(?,?,?,?,?,?)",
                (version_id, "Test reviewer", review_type, "pass", "Reviewed test fixture.", "https://example.test/review"),
            )
        corpus.execute(
            "INSERT INTO chunks(ref,article,page,text,norm,document_version_id,in_force,as_of,source,verified) "
            "VALUES(?,?,?,?,?,?,?,?,?,1)",
            ("Test Law Article 1", "1", "1", "corpusonlysentinel statutory rule",
             "corpusonlysentinel statutory rule", version_id, 1, "2020-01-01", "test-source"),
        )
        corpus.commit()

        # A firm admin is not a platform legal reviewer.
        self.assertEqual(self.client.get("/legal-review/queue").status_code, 403)

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        self.assertEqual(switched.json()["firm_id"], self.firm_b)
        self.assertEqual(self.client.get("/cases").json(), [])
        guessed_case = self._mutate(
            "post",
            "/search",
            json={"q": "firmonlysentinel", "case_id": case_id, "scope": "firm_documents"},
        )
        self.assertEqual(guessed_case.status_code, 404)

        shared_search = self._mutate(
            "post", "/search", json={"q": "corpusonlysentinel", "scope": "verified_corpus"}
        )
        self.assertEqual(shared_search.status_code, 200, shared_search.text)
        self.assertTrue(any("corpusonlysentinel" in hit["text"] for hit in shared_search.json()))

        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_reviewer')",
            (self.user_id,),
        )
        control.commit()
        reviewer_queue = self.client.get("/legal-review/queue")
        self.assertEqual(reviewer_queue.status_code, 200, reviewer_queue.text)


    def test_shared_corpus_import_requires_platform_reviewer_not_firm_admin(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        payload = [{
            "law": "Synthetic staged law import",
            "article": "1",
            "text": "Synthetic passage for platform authorization regression coverage.",
            "source": "TEST-ONLY",
            "verified": 1,
            "in_force": 1,
        }]
        headers = {"X-Admin-Token": self.admin_token}

        # The initial owner is a firm administrator, not a platform reviewer.
        denied = self._mutate("post", "/law/import", json=payload, headers=headers)
        self.assertEqual(denied.status_code, 403, denied.text)
        corpus = self.runtime.legal_corpus_connection()
        self.assertEqual(
            corpus.execute(
                "SELECT COUNT(*) FROM legal_import_staging WHERE law=?",
                ("Synthetic staged law import",),
            ).fetchone()[0],
            0,
        )

        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) "
            "VALUES(?,'platform_reviewer')",
            (self.user_id,),
        )
        control.commit()
        allowed = self._mutate("post", "/law/import", json=payload, headers=headers)
        self.assertEqual(allowed.status_code, 200, allowed.text)
        self.assertTrue(allowed.json()["review_required"])
        self.assertFalse(allowed.json()["search_eligible"])
        self.assertEqual(
            corpus.execute(
                "SELECT COUNT(*) FROM legal_import_staging WHERE law=?",
                ("Synthetic staged law import",),
            ).fetchone()[0],
            1,
        )
        # Caller-supplied trust flags must not bypass the reviewed-corpus workflow.
        self.assertEqual(
            corpus.execute(
                "SELECT COUNT(*) FROM legal_documents WHERE official_title=?",
                ("Synthetic staged law import",),
            ).fetchone()[0],
            0,
        )

        control.execute(
            "DELETE FROM user_platform_roles WHERE user_id=? AND role_name='platform_reviewer'",
            (self.user_id,),
        )
        control.commit()
        revoked = self._mutate("post", "/law/import", json=payload, headers=headers)
        self.assertEqual(revoked.status_code, 403, revoked.text)
        self.assertEqual(
            corpus.execute(
                "SELECT COUNT(*) FROM legal_import_staging WHERE law=?",
                ("Synthetic staged law import",),
            ).fetchone()[0],
            1,
        )


    def test_assigned_tasks_do_not_bypass_case_membership_in_dashboard_or_calendar(self):
        owner_login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(owner_login.status_code, 200, owner_login.text)
        select_firm = self._mutate("post", "/session/firm", json={"firm_id": self.firm_a})
        self.assertEqual(select_firm.status_code, 200, select_firm.text)
        case_response = self._mutate(
            "post", "/cases", json={"title": "NONMEMBER_CASE_TITLE_SENTINEL"}
        )
        self.assertEqual(case_response.status_code, 200, case_response.text)
        case_id = case_response.json()["id"]

        nonmember_id = self.runtime.create_global_identity(
            "Case Nonmember", "case-nonmember@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(nonmember_id, self.firm_a, "lawyer")
        due = (date.today() + timedelta(days=10)).isoformat()
        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        tenant = self.runtime.firm_connection(context)
        self.assertEqual(
            tenant.execute("SELECT title FROM cases WHERE id=?", (case_id,)).fetchone()["title"],
            "NONMEMBER_CASE_TITLE_SENTINEL",
        )
        tenant.execute(
            "INSERT INTO tasks(case_id,title,assignee,due,status,created_by) VALUES(?,?,?,?,?,?)",
            (case_id, "NONMEMBER_ASSIGNED_TASK_SENTINEL", nonmember_id, due, "open", self.user_id),
        )
        tenant.commit()

        nonmember_client = TestClient(app.app)
        try:
            login = nonmember_client.post(
                "/login",
                json={"email": "case-nonmember@example.test", "password": self.password},
            )
            self.assertEqual(login.status_code, 200, login.text)
            dashboard = nonmember_client.get("/dashboard")
            self.assertEqual(dashboard.status_code, 200, dashboard.text)
            self.assertNotIn("NONMEMBER_ASSIGNED_TASK_SENTINEL", dashboard.text)
            self.assertNotIn("NONMEMBER_CASE_TITLE_SENTINEL", dashboard.text)

            calendar = nonmember_client.get("/calendar.ics")
            self.assertEqual(calendar.status_code, 200, calendar.text)
            self.assertEqual(calendar.headers.get("Cache-Control"), "no-store")
            self.assertEqual(calendar.headers.get("Pragma"), "no-cache")
            self.assertNotIn("NONMEMBER_ASSIGNED_TASK_SENTINEL", calendar.text)
            self.assertNotIn("NONMEMBER_CASE_TITLE_SENTINEL", calendar.text)
        finally:
            nonmember_client.close()

        # Firm admins retain access to the case and its task detail.
        admin_case = self.client.get(f"/cases/{case_id}")
        self.assertEqual(admin_case.status_code, 200, admin_case.text)
        self.assertIn("NONMEMBER_ASSIGNED_TASK_SENTINEL", admin_case.text)


    def test_application_responses_are_not_cacheable(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        responses = (
            self.client.get("/cases"),
            self.client.get("/audit/security-events"),
            self.client.get("/calendar.ics"),
            self.client.get("/cases/999999"),
        )
        self.assertEqual([response.status_code for response in responses], [200, 200, 200, 404])
        for response in responses:
            with self.subTest(path=response.request.url.path, status=response.status_code):
                self.assertEqual(response.headers.get("Cache-Control"), "no-store")
                self.assertEqual(response.headers.get("Pragma"), "no-cache")
                self.assertEqual(response.headers.get("Expires"), "0")


    def test_nonmember_cannot_infer_finance_deadline_or_hearing_data(self):
        owner_login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(owner_login.status_code, 200, owner_login.text)
        select_firm = self._mutate("post", "/session/firm", json={"firm_id": self.firm_a})
        self.assertEqual(select_firm.status_code, 200, select_firm.text)
        case_response = self._mutate(
            "post", "/cases", json={"title": "NONMEMBER_FINANCIAL_CASE_SENTINEL"}
        )
        self.assertEqual(case_response.status_code, 200, case_response.text)
        case_id = case_response.json()["id"]

        nonmember_id = self.runtime.create_global_identity(
            "Finance Nonmember", "finance-nonmember@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(nonmember_id, self.firm_a, "lawyer")
        due = (date.today() + timedelta(days=10)).isoformat()
        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        tenant = self.runtime.firm_connection(context)
        self.assertEqual(
            tenant.execute("SELECT title FROM cases WHERE id=?", (case_id,)).fetchone()["title"],
            "NONMEMBER_FINANCIAL_CASE_SENTINEL",
        )
        tenant.execute(
            "INSERT INTO fees(case_id,title,amount,paid,due,note,created_by) VALUES(?,?,?,?,?,?,?)",
            (case_id, "NONMEMBER_FEE_SENTINEL", 9876.50, 0, due, "", self.user_id),
        )
        tenant.execute(
            "INSERT INTO deadlines(case_id,title,due,note,created_by,status) VALUES(?,?,?,?,?,'open')",
            (case_id, "NONMEMBER_DEADLINE_SENTINEL", due, "", self.user_id),
        )
        tenant.execute(
            "INSERT INTO sessions(case_id,date,note,done) VALUES(?,?,?,0)",
            (case_id, due, "NONMEMBER_HEARING_SENTINEL",),
        )
        tenant.commit()

        nonmember_client = TestClient(app.app)
        try:
            login = nonmember_client.post(
                "/login",
                json={"email": "finance-nonmember@example.test", "password": self.password},
            )
            self.assertEqual(login.status_code, 200, login.text)

            dashboard = nonmember_client.get("/dashboard")
            self.assertEqual(dashboard.status_code, 200, dashboard.text)
            for sentinel in (
                "NONMEMBER_FINANCIAL_CASE_SENTINEL",
                "NONMEMBER_DEADLINE_SENTINEL",
                "NONMEMBER_HEARING_SENTINEL",
            ):
                self.assertNotIn(sentinel, dashboard.text)

            calendar = nonmember_client.get("/calendar.ics")
            self.assertEqual(calendar.status_code, 200, calendar.text)
            for sentinel in (
                "NONMEMBER_FINANCIAL_CASE_SENTINEL",
                "NONMEMBER_DEADLINE_SENTINEL",
                "NONMEMBER_HEARING_SENTINEL",
            ):
                self.assertNotIn(sentinel, calendar.text)

            finance = nonmember_client.get("/finance/overview")
            self.assertEqual(finance.status_code, 200, finance.text)
            self.assertEqual(finance.json()["fee_count"], 0)
            self.assertEqual(finance.json()["total_amount"], 0)
            self.assertEqual(finance.json()["outstanding_amount"], 0)
        finally:
            nonmember_client.close()


    def test_same_firm_nonmember_cannot_read_or_mutate_case_data(self):
        owner_login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(owner_login.status_code, 200, owner_login.text)
        select_firm = self._mutate("post", "/session/firm", json={"firm_id": self.firm_a})
        self.assertEqual(select_firm.status_code, 200, select_firm.text)
        case_response = self._mutate(
            "post", "/cases", json={"title": "SAME_FIRM_PRIVATE_CASE_SENTINEL"}
        )
        self.assertEqual(case_response.status_code, 200, case_response.text)
        case_id = case_response.json()["id"]
        document_response = self._mutate(
            "post",
            f"/cases/{case_id}/docs",
            json={"name": "private-evidence.txt", "text": "SAME_FIRM_PRIVATE_DOCUMENT_SENTINEL source text"},
        )
        self.assertEqual(document_response.status_code, 200, document_response.text)
        document_id = document_response.json()["document_id"]

        nonmember_id = self.runtime.create_global_identity(
            "Same Firm Nonmember", "same-firm-nonmember@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(nonmember_id, self.firm_a, "lawyer")
        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        tenant = self.runtime.firm_connection(context)
        baseline = {
            table: tenant.execute(f"SELECT COUNT(*) FROM {table} WHERE case_id=?", (case_id,)).fetchone()[0]
            for table in ("docs", "chunks", "notes", "deadlines", "fees", "sessions", "tasks", "events")
        }
        case_before = tenant.execute(
            "SELECT title,stage,status FROM cases WHERE id=?", (case_id,)
        ).fetchone()

        nonmember_client = TestClient(app.app)
        try:
            login = nonmember_client.post(
                "/login",
                json={"email": "same-firm-nonmember@example.test", "password": self.password},
            )
            self.assertEqual(login.status_code, 200, login.text)
            csrf = nonmember_client.cookies.get("lc_csrf") or ""
            headers = {"X-CSRF-Token": csrf}

            reads = (
                nonmember_client.get(f"/cases/{case_id}"),
                nonmember_client.get(f"/cases/{case_id}/docs/{document_id}/chunks"),
                nonmember_client.get(f"/cases/{case_id}/docs/{document_id}/reviews"),
            )
            for response in reads:
                with self.subTest(method="GET", path=response.request.url.path):
                    self.assertEqual(response.status_code, 404, response.text)
                    self.assertNotIn("SAME_FIRM_PRIVATE", response.text)

            mutations = (
                ("patch", f"/cases/{case_id}", {"stage": "closed"}),
                ("post", f"/cases/{case_id}/notes", {"text": "unauthorized note"}),
                ("post", f"/cases/{case_id}/deadlines", {"title": "unauthorized deadline", "due": "2026-11-10"}),
                ("post", f"/cases/{case_id}/fees", {"title": "unauthorized fee", "amount": 10, "paid": 0}),
                ("post", f"/cases/{case_id}/sessions", {"date": "2026-11-10", "note": "unauthorized session"}),
                ("post", f"/cases/{case_id}/tasks", {"title": "unauthorized task"}),
                ("post", f"/cases/{case_id}/docs", {"name": "unauthorized.txt", "text": "unauthorized document"}),
            )
            for method_name, path, payload in mutations:
                with self.subTest(method=method_name.upper(), path=path):
                    response = getattr(nonmember_client, method_name)(
                        path, json=payload, headers=headers
                    )
                    self.assertEqual(response.status_code, 404, response.text)

            upload = nonmember_client.post(
                f"/cases/{case_id}/upload",
                headers=headers,
                files={"file": ("unauthorized.txt", b"unauthorized upload text", "text/plain")},
            )
            self.assertEqual(upload.status_code, 404, upload.text)
            deletion = nonmember_client.delete(f"/cases/{case_id}", headers=headers)
            self.assertEqual(deletion.status_code, 404, deletion.text)
        finally:
            nonmember_client.close()

        case_after = tenant.execute(
            "SELECT title,stage,status FROM cases WHERE id=?", (case_id,)
        ).fetchone()
        self.assertEqual(tuple(case_after), tuple(case_before))
        for table, count in baseline.items():
            with self.subTest(table=table):
                self.assertEqual(
                    tenant.execute(f"SELECT COUNT(*) FROM {table} WHERE case_id=?", (case_id,)).fetchone()[0],
                    count,
                )


    def test_document_persistence_rolls_back_metadata_chunks_and_event_together(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        select_firm = self._mutate("post", "/session/firm", json={"firm_id": self.firm_a})
        self.assertEqual(select_firm.status_code, 200, select_firm.text)
        case_response = self._mutate(
            "post", "/cases", json={"title": "Document Atomicity Case"}
        )
        self.assertEqual(case_response.status_code, 200, case_response.text)
        case_id = case_response.json()["id"]

        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        tenant = self.runtime.firm_connection(context)
        before = {
            table: tenant.execute(f"SELECT COUNT(*) FROM {table} WHERE case_id=?", (case_id,)).fetchone()[0]
            for table in ("docs", "chunks", "events")
        }
        tenant.execute("""
            CREATE TRIGGER reject_document_audit_event
            BEFORE INSERT ON events
            WHEN NEW.text LIKE '%إضافة مستند:%'
            BEGIN SELECT RAISE(ABORT, 'document audit unavailable'); END
        """)
        tenant.commit()

        response = self._mutate(
            "post",
            f"/cases/{case_id}/docs",
            json={"name": "atomicity-test.txt", "text": "DOCUMENT_ATOMICITY_SENTINEL extracted source text"},
        )
        self.assertEqual(response.status_code, 503, response.text)
        for table, count in before.items():
            with self.subTest(table=table):
                self.assertEqual(
                    tenant.execute(f"SELECT COUNT(*) FROM {table} WHERE case_id=?", (case_id,)).fetchone()[0],
                    count,
                )
        self.assertFalse(tenant.in_transaction)


    def test_failed_matter_write_rolls_back_before_connection_is_reused(self):
        client = TestClient(app.app, raise_server_exceptions=False)
        try:
            login = client.post(
                "/login", json={"email": "OWNER@example.test", "password": self.password}
            )
            self.assertEqual(login.status_code, 200, login.text)
            csrf = client.cookies.get("lc_csrf") or ""
            headers = {"X-CSRF-Token": csrf}
            switched = client.post(
                "/session/firm", json={"firm_id": self.firm_a}, headers=headers
            )
            self.assertEqual(switched.status_code, 200, switched.text)
            case_response = client.post(
                "/cases", json={"title": "Failed Write Rollback Case"}, headers=headers
            )
            self.assertEqual(case_response.status_code, 200, case_response.text)
            case_id = case_response.json()["id"]

            context = self.runtime.resolve_context(self.user_id, self.firm_a)
            tenant = self.runtime.firm_connection(context)
            tenant.execute("""
                CREATE TRIGGER reject_note_event
                BEFORE INSERT ON events
                WHEN NEW.text LIKE '%إضافة ملاحظة%'
                BEGIN SELECT RAISE(ABORT, 'note audit unavailable'); END
            """)
            tenant.commit()

            failed = client.post(
                f"/cases/{case_id}/notes",
                json={"text": "FAILED_NOTE_MUST_NOT_PERSIST"},
                headers=headers,
            )
            self.assertEqual(failed.status_code, 503, failed.text)
            self.assertEqual(failed.headers.get("Cache-Control"), "no-store")

            tenant.execute("DROP TRIGGER reject_note_event")
            tenant.commit()
            succeeding = client.post(
                f"/cases/{case_id}/notes",
                json={"text": "successful follow-up note"},
                headers=headers,
            )
            self.assertEqual(succeeding.status_code, 200, succeeding.text)

            rows = tenant.execute(
                "SELECT text FROM notes WHERE case_id=? ORDER BY id", (case_id,)
            ).fetchall()
            self.assertEqual([row["text"] for row in rows], ["successful follow-up note"])
            events = tenant.execute(
                "SELECT text FROM events WHERE case_id=? ORDER BY id", (case_id,)
            ).fetchall()
            self.assertFalse(any("FAILED_NOTE_MUST_NOT_PERSIST" in row["text"] for row in events))
        finally:
            client.close()


    def test_failed_shared_corpus_import_rolls_back_partial_batch(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_reviewer')",
            (self.user_id,),
        )
        control.commit()

        corpus = self.runtime.legal_corpus_connection()
        corpus.execute("""
            CREATE TRIGGER reject_second_staged_import
            BEFORE INSERT ON legal_import_staging
            WHEN NEW.law='Atomic staged import' AND NEW.article='2'
            BEGIN SELECT RAISE(ABORT, 'staging insert unavailable'); END
        """)
        corpus.commit()
        payload = [
            {"law": "Atomic staged import", "article": "1", "text": "first batch row", "source": "TEST"},
            {"law": "Atomic staged import", "article": "2", "text": "second batch row", "source": "TEST"},
        ]
        headers = {"X-Admin-Token": self.admin_token}
        failed = self._mutate("post", "/law/import", json=payload, headers=headers)
        self.assertEqual(failed.status_code, 503, failed.text)
        self.assertEqual(
            corpus.execute(
                "SELECT COUNT(*) FROM legal_import_staging WHERE law=?",
                ("Atomic staged import",),
            ).fetchone()[0],
            0,
        )

        corpus.execute("DROP TRIGGER reject_second_staged_import")
        corpus.commit()
        succeeding = self._mutate(
            "post",
            "/law/import",
            json=[{"law": "Atomic staged import", "article": "3", "text": "successful follow-up row", "source": "TEST"}],
            headers=headers,
        )
        self.assertEqual(succeeding.status_code, 200, succeeding.text)
        rows = corpus.execute(
            "SELECT article FROM legal_import_staging WHERE law=? ORDER BY article",
            ("Atomic staged import",),
        ).fetchall()
        self.assertEqual([row["article"] for row in rows], ["3"])


    def test_tenant_and_corpus_mutation_routes_declare_rollback_guards(self):
        mutation_methods = {"POST", "PUT", "PATCH", "DELETE"}
        tenant_prefixes = ("/cases", "/tasks", "/deadlines", "/research/conversations")
        corpus_write_paths = {
            "/law/import",
            "/legal-review/versions/{version_id}/events",
        }
        seen_tenant = set()
        seen_corpus = set()
        for route in app.app.routes:
            path = getattr(route, "path", "")
            methods = set(getattr(route, "methods", set())) & mutation_methods
            if not methods:
                continue
            domain = getattr(route.endpoint, "_rollback_transaction_domain", None)
            if path.startswith(tenant_prefixes):
                seen_tenant.update((method, path) for method in methods)
                with self.subTest(methods=sorted(methods), path=path):
                    self.assertEqual(domain, "tenant")
            if path in corpus_write_paths:
                seen_corpus.update((method, path) for method in methods)
                with self.subTest(methods=sorted(methods), path=path):
                    self.assertEqual(domain, "corpus")

        self.assertTrue(seen_tenant, "expected to inspect tenant mutation routes")
        self.assertIn(("POST", "/cases"), seen_tenant)
        self.assertIn(("POST", "/research/conversations"), seen_tenant)
        self.assertEqual(seen_corpus, {
            ("POST", "/law/import"),
            ("POST", "/legal-review/versions/{version_id}/events"),
        })


    def test_same_firm_research_conversations_are_private_to_their_owner(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate("post", "/research/conversations")
        self.assertEqual(created.status_code, 200, created.text)
        conversation_id = created.json()["id"]
        renamed = self._mutate(
            "patch",
            f"/research/conversations/{conversation_id}",
            json={"title": "SAME_FIRM_PRIVATE_RESEARCH_SENTINEL"},
        )
        self.assertEqual(renamed.status_code, 200, renamed.text)

        nonmember_id = self.runtime.create_global_identity(
            "Research Colleague", "research-colleague@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(nonmember_id, self.firm_a, "lawyer")
        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        tenant = self.runtime.firm_connection(context)

        nonmember_client = TestClient(app.app)
        try:
            nonmember_login = nonmember_client.post(
                "/login",
                json={"email": "research-colleague@example.test", "password": self.password},
            )
            self.assertEqual(nonmember_login.status_code, 200, nonmember_login.text)
            csrf = nonmember_client.cookies.get("lc_csrf") or ""
            headers = {"X-CSRF-Token": csrf}

            listing = nonmember_client.get("/research/conversations")
            self.assertEqual(listing.status_code, 200, listing.text)
            self.assertNotIn("SAME_FIRM_PRIVATE_RESEARCH_SENTINEL", listing.text)
            detail = nonmember_client.get(f"/research/conversations/{conversation_id}")
            self.assertEqual(detail.status_code, 404, detail.text)
            rename_attempt = nonmember_client.patch(
                f"/research/conversations/{conversation_id}",
                json={"title": "UNAUTHORIZED_RESEARCH_RENAME"},
                headers=headers,
            )
            self.assertEqual(rename_attempt.status_code, 404, rename_attempt.text)
            message_attempt = nonmember_client.post(
                f"/research/conversations/{conversation_id}/messages",
                json={"message": "UNAUTHORIZED_RESEARCH_MESSAGE", "scope": "verified_corpus"},
                headers=headers,
            )
            self.assertEqual(message_attempt.status_code, 404, message_attempt.text)
            save_attempt = nonmember_client.post(
                f"/research/conversations/{conversation_id}/save-to-matter",
                json={"case_id": 1, "message_id": 1},
                headers=headers,
            )
            self.assertEqual(save_attempt.status_code, 404, save_attempt.text)
            delete_attempt = nonmember_client.delete(
                f"/research/conversations/{conversation_id}", headers=headers
            )
            self.assertEqual(delete_attempt.status_code, 404, delete_attempt.text)
        finally:
            nonmember_client.close()

        row = tenant.execute(
            "SELECT title,user_id,firm_id FROM research_conversations WHERE id=?",
            (conversation_id,),
        ).fetchone()
        self.assertEqual(row["title"], "SAME_FIRM_PRIVATE_RESEARCH_SENTINEL")
        self.assertEqual(row["user_id"], self.user_id)
        self.assertEqual(row["firm_id"], self.firm_a)
        self.assertEqual(
            tenant.execute(
                "SELECT COUNT(*) FROM research_messages WHERE conversation_id=?",
                (conversation_id,),
            ).fetchone()[0],
            0,
        )


    def test_failed_legal_review_event_write_rolls_back_and_returns_503(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        corpus = self.runtime.legal_corpus_connection()
        corpus.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("review-rollback-source", "Review rollback test", "https://example.test/source"),
        )
        corpus.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
            ("review-rollback-doc", "review-rollback-source", "Review rollback document", "statute"),
        )
        corpus.execute(
            "INSERT INTO legal_document_versions(version_id,document_id,version_label,source_url) VALUES(?,?,?,?)",
            (780, "review-rollback-doc", "v1", "https://example.test/source/v1"),
        )
        corpus.commit()

        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_reviewer')",
            (self.user_id,),
        )
        control.commit()
        corpus.execute("""
            CREATE TRIGGER reject_review_event_780
            BEFORE INSERT ON legal_review_events
            WHEN NEW.version_id=780
            BEGIN SELECT RAISE(ABORT, 'review event unavailable'); END
        """)
        corpus.commit()

        endpoint = "/legal-review/versions/780/events"
        payload = {
            "review_type": "legal_status",
            "outcome": "pending",
            "notes": "Synthetic rollback regression",
        }
        failed = self._mutate("post", endpoint, json=payload)
        self.assertEqual(failed.status_code, 503, failed.text)
        self.assertEqual(
            corpus.execute(
                "SELECT COUNT(*) FROM legal_review_events WHERE version_id=780"
            ).fetchone()[0],
            0,
        )

        corpus.execute("DROP TRIGGER reject_review_event_780")
        corpus.commit()
        succeeding = self._mutate("post", endpoint, json=payload)
        self.assertEqual(succeeding.status_code, 201, succeeding.text)
        self.assertEqual(
            corpus.execute(
                "SELECT COUNT(*) FROM legal_review_events WHERE version_id=780"
            ).fetchone()[0],
            1,
        )


    def test_unhandled_errors_return_generic_non_cacheable_responses(self):
        original_rate_limit = app._rate_limit
        client = TestClient(app.app, raise_server_exceptions=False)
        def fail_rate_limit(_request):
            raise RuntimeError("SENSITIVE_ERROR_SENTINEL")
        app._rate_limit = fail_rate_limit
        try:
            response = client.get("/")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"detail": "internal server error"})
            self.assertNotIn("SENSITIVE_ERROR_SENTINEL", response.text)
            self.assertEqual(response.headers.get("Cache-Control"), "no-store")
            self.assertEqual(response.headers.get("Pragma"), "no-cache")
            self.assertEqual(response.headers.get("Expires"), "0")
        finally:
            app._rate_limit = original_rate_limit
            client.close()


if __name__ == "__main__":
    unittest.main()
