"""Invoice routes use integer piasters and isolate firm/case access."""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime
from tools.invoice_money import InvoiceMoneyError, egp_to_piasters, piasters_to_egp


class InvoiceRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-invoice-routes-")
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
            ADMIN_TOKEN="invoice-route-test-admin-token-long-enough",
        )
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Invoice Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Invoice Firm B")
        self.password_a = "Invoice-test-password-A-2026!"
        self.password_b = "Invoice-test-password-B-2026!"
        self.runtime.create_initial_firm_owner(
            self.firm_a, "Invoice Owner A", "invoice-a@example.test", app.hash_pw(self.password_a)
        )
        self.runtime.create_initial_firm_owner(
            self.firm_b, "Invoice Owner B", "invoice-b@example.test", app.hash_pw(self.password_b)
        )
        self.client_a = TestClient(app.app)
        self.client_b = TestClient(app.app)
        self._login(self.client_a, "invoice-a@example.test", self.password_a)
        self._login(self.client_b, "invoice-b@example.test", self.password_b)
        created = self._mutate(self.client_a, "post", "/cases", json={
            "title": "Synthetic invoice matter", "client": "شركة اختبار",
        })
        self.assertEqual(created.status_code, 200, created.text)
        self.case_id = created.json()["id"]
        self.tenant_a = self.runtime._tenant_router.connection_for_firm(self.firm_a)
        self.other_password = "Invoice-nonmember-password-2026!"
        self.other_id = self.runtime.create_global_identity(
            "Invoice Nonmember", "invoice-nonmember@example.test", app.hash_pw(self.other_password)
        )
        self.runtime.create_firm_membership(self.other_id, self.firm_a, "lawyer")
        self.client_nonmember = TestClient(app.app)
        self._login(self.client_nonmember, "invoice-nonmember@example.test", self.other_password)

    def tearDown(self):
        for client in (self.client_a, self.client_b, self.client_nonmember):
            client.close()
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

    def _create_and_issue(self):
        created = self._mutate(self.client_a, "post", f"/cases/{self.case_id}/invoices", json={
            "client_name": "شركة اختبار",
            "issue_date": "2026-11-02",
            "due_date": "2026-10-01",
            "note": "فاتورة تجريبية",
            "lines": [
                {"description": "أتعاب استشارة", "quantity": 2, "unit_price_egp": "100.25"},
                {"description": "مصروفات", "quantity": 1, "unit_price_egp": "50"},
            ],
        })
        self.assertEqual(created.status_code, 200, created.text)
        self.assertEqual(created.json()["invoice_number"], "LC-2026-00001")
        self.assertEqual(created.json()["total_piasters"], 25050)
        invoice_id = created.json()["id"]
        issued = self._mutate(self.client_a, "post", f"/invoices/{invoice_id}/issue")
        self.assertEqual(issued.status_code, 200, issued.text)
        return invoice_id

    def test_money_helpers_never_use_float_arithmetic(self):
        self.assertEqual(egp_to_piasters("100.25"), 10025)
        self.assertEqual(egp_to_piasters("0.5"), 50)
        self.assertEqual(piasters_to_egp(25050), "250.50")
        for value in ("1.234", "-1", "1e3", "01.00", "1,000", ""):
            with self.subTest(value=value), self.assertRaises(InvoiceMoneyError):
                egp_to_piasters(value)

    def test_invoice_issue_payment_receipt_and_aging_overview(self):
        invoice_id = self._create_and_issue()
        details = self.client_a.get(f"/invoices/{invoice_id}")
        self.assertEqual(details.status_code, 200, details.text)
        self.assertEqual(details.json()["status"], "issued")
        self.assertEqual(details.json()["subtotal_piasters"], 25050)
        self.assertEqual(details.json()["lines"][0]["line_total_piasters"], 20050)

        payment = self._mutate(self.client_a, "post", f"/invoices/{invoice_id}/payments", json={
            "amount_egp": "100.00", "method": "instapay", "reference": "IP-TEST-001",
            "paid_on": "2026-11-02",
        })
        self.assertEqual(payment.status_code, 200, payment.text)
        self.assertEqual(payment.json()["amount_piasters"], 10000)
        self.assertEqual(payment.json()["receipt_number"], "RC-2026-000001")
        overpay = self._mutate(self.client_a, "post", f"/invoices/{invoice_id}/payments", json={
            "amount_egp": "150.51", "method": "cash", "paid_on": "2026-11-02",
        })
        self.assertEqual(overpay.status_code, 422)

        receipt = self.client_a.get(
            f"/invoices/{invoice_id}/payments/{payment.json()['id']}/receipt"
        )
        self.assertEqual(receipt.status_code, 200)
        self.assertIn("RC-2026-000001", receipt.text)
        printable = self.client_a.get(f"/invoices/{invoice_id}/print")
        self.assertEqual(printable.status_code, 200)
        self.assertIn("LC-2026-00001", printable.text)
        self.assertIn("250.50", printable.text)

        overview = self.client_a.get("/finance/invoices/overview")
        self.assertEqual(overview.status_code, 200, overview.text)
        data = overview.json()
        self.assertEqual(data["invoiced_piasters"], 25050)
        self.assertEqual(data["paid_piasters"], 10000)
        self.assertEqual(data["outstanding_piasters"], 15050)
        self.assertEqual(data["aging"]["31_60_days"], 15050)
        self.assertEqual(data["by_client"]["شركة اختبار"]["outstanding_piasters"], 15050)

        with self.assertRaises(sqlite3.IntegrityError):
            self.tenant_a.execute("UPDATE invoice_payments SET reference='changed' WHERE id=?", (payment.json()["id"],))

    def test_firm_b_and_same_firm_nonmember_cannot_read_firm_a_invoice(self):
        invoice_id = self._create_and_issue()
        self.assertEqual(self.client_b.get("/invoices").json(), [])
        self.assertEqual(self.client_b.get("/invoices/" + str(invoice_id)).status_code, 404)
        self.assertEqual(self.client_b.get("/finance/invoices/overview").json()["outstanding_piasters"], 0)
        self.assertEqual(self.client_nonmember.get(f"/invoices/{invoice_id}").status_code, 404)
        denied = self._mutate(self.client_nonmember, "post", f"/cases/{self.case_id}/invoices", json={
            "client_name": "غير مصرح", "issue_date": "2026-11-02",
            "lines": [{"description": "x", "quantity": 1, "unit_price_egp": "1"}],
        })
        self.assertEqual(denied.status_code, 404)
        self.assertEqual(self.client_a.get("/invoices").json()[0]["id"], invoice_id)


if __name__ == "__main__":
    unittest.main()
