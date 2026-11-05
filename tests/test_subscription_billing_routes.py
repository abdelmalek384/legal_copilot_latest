"""Subscription plans, trial, manual transfer approval and seat limits."""
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class SubscriptionBillingRouteTests(unittest.TestCase):
    def test_platform_payment_review_routes_are_owned_by_platform_router(self):
        expected = {
            "/platform/billing/payment-submissions": {"GET"},
            "/platform/billing/payment-submissions/{submission_id}/approve": {"POST"},
            "/platform/billing/payment-submissions/{submission_id}/reject": {"POST"},
        }
        routes = {r.path: r for r in app.app.routes if getattr(r, "path", None) in expected}
        self.assertEqual(set(routes), set(expected))
        self.assertTrue(all(routes[p].methods == methods and routes[p].endpoint.__module__ == "routers.platform" for p, methods in expected.items()))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-subscription-")
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_OBJECT_STORAGE_ROOT",
            "COPILOT_OBJECT_STORAGE_BACKEND", "COPILOT_ENV", "ADMIN_TOKEN",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ.pop("COPILOT_DB", None)
        os.environ.update(
            COPILOT_CONTROL_DB=str(self.root / "control.sqlite3"),
            COPILOT_TENANT_DB_ROOT=str(self.root / "tenants"),
            COPILOT_CORPUS_DB=str(self.root / "corpus.sqlite3"),
            COPILOT_OBJECT_STORAGE_ROOT=str(self.root / "objects"),
            COPILOT_OBJECT_STORAGE_BACKEND="local",
            COPILOT_ENV="development",
            ADMIN_TOKEN="subscription-route-test-admin-token",
        )
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Subscription Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Subscription Firm B")
        self.password_a = "Subscription-test-password-A-2026!"
        self.password_b = "Subscription-test-password-B-2026!"
        self.runtime.create_initial_firm_owner(
            self.firm_a, "Subscription Owner A", "subscription-a@example.test",
            app.hash_pw(self.password_a),
        )
        self.runtime.create_initial_firm_owner(
            self.firm_b, "Subscription Owner B", "subscription-b@example.test",
            app.hash_pw(self.password_b),
        )
        self.user_a_id = int(app.control_conn().execute(
            "SELECT id FROM users WHERE email_normalized=?", ("subscription-a@example.test",)
        ).fetchone()["id"])
        self.runtime.create_firm_membership(self.user_a_id, self.firm_b, "lawyer")
        control = app.control_conn()
        self.user_b_id = int(control.execute(
            "SELECT id FROM users WHERE email_normalized=?", ("subscription-b@example.test",)
        ).fetchone()["id"])
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_admin')",
            (self.user_b_id,),
        )
        control.commit()
        self.client_a = TestClient(app.app)
        self.client_b = TestClient(app.app)
        self._login(self.client_a, "subscription-a@example.test", self.password_a)
        self._login(self.client_b, "subscription-b@example.test", self.password_b)
        lawyer_password = "Subscription-lawyer-password-2026!"
        lawyer_id = self.runtime.create_global_identity(
            "Subscription Lawyer", "subscription-lawyer@example.test", app.hash_pw(lawyer_password)
        )
        self.runtime.create_firm_membership(lawyer_id, self.firm_a, "lawyer")
        self.client_lawyer = TestClient(app.app)
        self._login(self.client_lawyer, "subscription-lawyer@example.test", lawyer_password)

    def tearDown(self):
        self.client_a.close()
        self.client_b.close()
        self.client_lawyer.close()
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
        response = client.post("/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200, response.text)

    def _mutate(self, client, method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = client.cookies.get("lc_csrf", "")
        return getattr(client, method)(url, headers=headers, **kwargs)

    def test_trial_manual_transfer_and_platform_approval_are_firm_scoped(self):
        empty = self.client_a.get("/billing")
        self.assertEqual(empty.status_code, 200, empty.text)
        self.assertIsNone(empty.json()["subscription"])
        self.assertEqual({p["code"] for p in empty.json()["plans"]}, {"solo", "small_firm"})

        started = self._mutate(self.client_a, "post", "/billing/subscribe", json={"plan_code": "solo"})
        self.assertEqual(started.status_code, 200, started.text)
        trial = started.json()["subscription"]
        self.assertEqual(trial["status"], "trial")
        self.assertEqual(trial["seat_limit"], 1)
        self.assertEqual(trial["trial_ends_at"] - trial["trial_started_at"], 14 * 86400)

        submission = self._mutate(self.client_a, "post", "/billing/payment-submissions", json={
            "amount_piasters": 250000, "method": "bank_transfer", "transfer_reference": "BANK-REF-2026-001",
        })
        self.assertEqual(submission.status_code, 200, submission.text)
        self.assertEqual(submission.json()["status"], "pending")
        duplicate = self._mutate(self.client_a, "post", "/billing/payment-submissions", json={
            "amount_piasters": 250000, "method": "bank_transfer", "transfer_reference": "BANK-REF-2026-001",
        })
        self.assertEqual(duplicate.status_code, 409)

        denied = self._mutate(self.client_a, "post",
            f"/platform/billing/payment-submissions/{submission.json()['submission_id']}/approve")
        self.assertEqual(denied.status_code, 403)

        queue = self.client_b.get("/platform/billing/payment-submissions")
        self.assertEqual(queue.status_code, 200, queue.text)
        self.assertEqual(queue.json()[0]["firm_id"], self.firm_a)
        approved = self._mutate(self.client_b, "post",
            f"/platform/billing/payment-submissions/{submission.json()['submission_id']}/approve")
        self.assertEqual(approved.status_code, 200, approved.text)
        active = self.client_a.get("/billing").json()["subscription"]
        self.assertEqual(active["status"], "active")
        self.assertGreater(active["current_period_end"], active["current_period_start"])
        self.assertEqual(self.client_b.get("/billing").json()["subscription"], None)
        self.assertEqual(self.client_b.get("/billing").json()["subscription_events"], [])
        audit = self.client_a.get("/billing").json()["subscription_events"]
        self.assertEqual(
            {event["event_type"] for event in audit},
            {"trial_started", "payment_submitted", "payment_approved"},
        )
        self.assertTrue(all(event["actor_name"] for event in audit if event["event_type"] != "trial_started"))
        self.assertEqual(audit[0]["details"]["amount_piasters"], 250000)
        self.assertEqual(self.client_b.get("/platform/billing/payment-submissions").json(), [])
        small_firm = self._mutate(self.client_b, "post", "/billing/subscribe", json={"plan_code": "small_firm"})
        self.assertEqual(small_firm.status_code, 200, small_firm.text)
        self.assertEqual(small_firm.json()["subscription"]["seat_limit"], 5)

    def test_expired_trial_is_read_only_but_payment_and_reads_remain_available(self):
        started = self._mutate(
            self.client_a, "post", "/billing/subscribe", json={"plan_code": "solo"}
        )
        self.assertEqual(started.status_code, 200, started.text)
        matter = self._mutate(
            self.client_a, "post", "/cases",
            json={"title": "Retained after expiry", "client": "Expiry Test Client"},
        )
        self.assertEqual(matter.status_code, 200, matter.text)
        matter_id = matter.json()["id"]
        control = self.runtime.control_connection()
        expired_at = int(app.time.time()) - 3600
        control.execute(
            "UPDATE firm_subscriptions SET trial_ends_at=? WHERE firm_id=?",
            (expired_at, self.firm_a),
        )
        control.commit()

        billing = self.client_a.get("/billing")
        self.assertEqual(billing.status_code, 200, billing.text)
        self.assertTrue(billing.json()["read_only"])
        self.assertEqual(billing.json()["subscription"]["status"], "expired")
        self.assertGreaterEqual(billing.json()["grace_days_remaining"], 1)
        self.assertEqual(billing.json()["days_remaining"], 0)
        self.assertEqual(billing.json()["grace_period_ends_at"], expired_at + 7 * 86400)

        retained_list = self.client_a.get("/cases")
        self.assertEqual(retained_list.status_code, 200, retained_list.text)
        self.assertIn(matter_id, {row["id"] for row in retained_list.json()})
        retained_detail = self.client_a.get(f"/cases/{matter_id}")
        self.assertEqual(retained_detail.status_code, 200, retained_detail.text)
        self.assertEqual(retained_detail.json()["title"], "Retained after expiry")
        blocked_edit = self._mutate(
            self.client_a, "patch", f"/cases/{matter_id}", json={"stage": "should remain unchanged"}
        )
        self.assertEqual(blocked_edit.status_code, 423, blocked_edit.text)
        unchanged = self.client_a.get(f"/cases/{matter_id}")
        self.assertEqual(unchanged.json()["stage"], "")

        # An owner who belongs to multiple firms must be able to leave an expired firm.
        switched = self._mutate(self.client_a, "post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        switched_billing = self.client_a.get("/billing")
        self.assertEqual(switched_billing.status_code, 403, switched_billing.text)
        switched_back = self._mutate(self.client_a, "post", "/session/firm", json={"firm_id": self.firm_a})
        self.assertEqual(switched_back.status_code, 200, switched_back.text)

        export = self.client_a.get("/firm/data-export.zip")
        self.assertEqual(export.status_code, 200, export.text)
        self.assertIn("application/zip", export.headers.get("content-type", ""))

        blocked = self._mutate(self.client_a, "post", "/invitations", json={
            "email": "expired-seat@example.test", "role": "lawyer",
        })
        self.assertEqual(blocked.status_code, 423, blocked.text)

        payment = self._mutate(self.client_a, "post", "/billing/payment-submissions", json={
            "amount_piasters": 250000, "method": "bank_transfer",
            "transfer_reference": "EXPIRED-TRIAL-RENEWAL-001",
        })
        self.assertEqual(payment.status_code, 200, payment.text)
        self.assertEqual(payment.json()["status"], "pending")
        after_payment = self.client_a.get("/billing")
        self.assertEqual(after_payment.status_code, 200, after_payment.text)
        self.assertTrue(after_payment.json()["read_only"])
        self.assertEqual(after_payment.json()["subscription"]["status"], "pending_payment")

    def test_seat_limit_blocks_invites_and_non_admin_cannot_manage_billing(self):
        started = self._mutate(self.client_a, "post", "/billing/subscribe", json={"plan_code": "solo"})
        self.assertEqual(started.status_code, 200, started.text)
        self.assertEqual(started.json()["seat_usage"]["limit"], 1)
        invite = self._mutate(self.client_a, "post", "/invitations", json={
            "email": "extra-lawyer@example.test", "role": "lawyer",
        })
        self.assertEqual(invite.status_code, 409)
        self.assertEqual(self.client_b.get("/billing").status_code, 200)
        self.assertEqual(self.client_b.get("/platform/billing/payment-submissions").status_code, 200)
        self.assertEqual(self.client_lawyer.get("/billing").status_code, 403)
        denied_plan = self._mutate(self.client_lawyer, "post", "/billing/subscribe", json={"plan_code": "small_firm"})
        self.assertEqual(denied_plan.status_code, 403)


if __name__ == "__main__":
    unittest.main()
