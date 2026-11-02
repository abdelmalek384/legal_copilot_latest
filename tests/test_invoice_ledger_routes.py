"""Firm-scoped exact-piaster invoice and payment API tests."""
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class InvoiceLedgerRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-invoices-")
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
            ADMIN_TOKEN="invoice-ledger-test-admin-token-long-enough",
        )
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Invoice Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Invoice Firm B")
        self.password = "Invoice-ledger-test-password-2026!"
        self.runtime.create_initial_firm_owner(
            self.firm_a, "Invoice Owner A", "invoice-owner-a@example.test",
            app.hash_pw(self.password),
        )
        self.runtime.create_initial_firm_owner(
            self.firm_b, "Invoice Owner B", "invoice-owner-b@example.test",
            app.hash_pw(self.password),
        )
        self.nonmember_id = self.runtime.create_global_identity(
            "Invoice Nonmember", "invoice-nonmember@example.test",
            app.hash_pw(self.password),
        )
        self.runtime.create_firm_membership(self.nonmember_id, self.firm_a, "lawyer")
        self.client_a = TestClient(app.app)
        self.client_b = TestClient(app.app)
        self.client_nonmember = TestClient(app.app)
        for client, email in (
            (self.client_a, "invoice-owner-a@example.test"),
            (self.client_b, "invoice-owner-b@example.test"),
            (self.client_nonmember, "invoice-nonmember@example.test"),
        ):
            response = client.post("/login", json={"email": email, "password": self.password})
            self.assertEqual(response.status_code, 200, response.text)
        case = self.mutate(
            self.client_a, "post", "/cases",
            json={"title": "Invoice matter", "client": "Client Snapshot"},
        )
        self.assertEqual(case.status_code, 200, case.text)
        self.case_id = case.json()["id"]

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

    @staticmethod
    def mutate(client, method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = client.cookies.get("lc_csrf", "")
        return getattr(client, method)(url, headers=headers, **kwargs)

    def create_draft(self, *, due_date="2099-01-01"):
        return self.mutate(
            self.client_a, "post", f"/cases/{self.case_id}/invoices",
            json={
                "description": "Legal services",
                "due_date": due_date,
                "lines": [
                    {"description": "Consultation", "quantity_milli": 1500, "unit_price_piasters": 10000},
                    {"description": "Court filing", "quantity_milli": 1000, "unit_price_piasters": 2500},
                ],
            },
        )

    def test_create_draft_calculates_exact_piasters_and_snapshots_client(self):
        response = self.create_draft()
        self.assertEqual(response.status_code, 200, response.text)
        invoice = response.json()
        self.assertEqual(invoice["status"], "draft")
        self.assertEqual(invoice["payment_state"], "draft")
        self.assertEqual(invoice["currency"], "EGP")
        self.assertEqual(invoice["client_name_snapshot"], "Client Snapshot")
        self.assertEqual(invoice["case_title_snapshot"], "Invoice matter")
        self.assertEqual(invoice["subtotal_piasters"], 17500)
        self.assertEqual(invoice["total_piasters"], 17500)
        self.assertEqual([line["line_total_piasters"] for line in invoice["lines"]], [15000, 2500])

    def test_issue_assigns_firm_local_sequential_number_and_freezes_content(self):
        first = self.create_draft().json()
        second = self.create_draft().json()
        issued_a = self.mutate(self.client_a, "post", f"/invoices/{first['id']}/issue")
        issued_b = self.mutate(self.client_a, "post", f"/invoices/{second['id']}/issue")
        self.assertEqual(issued_a.status_code, 200, issued_a.text)
        self.assertEqual(issued_b.status_code, 200, issued_b.text)
        self.assertRegex(issued_a.json()["invoice_number"], r"^INV-20\d{2}-\d{6}$")
        self.assertNotEqual(issued_a.json()["invoice_number"], issued_b.json()["invoice_number"])
        edited = self.mutate(
            self.client_a, "put", f"/invoices/{first['id']}",
            json={"description": "Changed", "due_date": "2099-01-01",
                  "lines": [{"description": "Changed line", "quantity_milli": 1000, "unit_price_piasters": 1}]},
        )
        self.assertEqual(edited.status_code, 409)

    def test_partial_full_payment_idempotency_and_overpayment(self):
        invoice = self.create_draft().json()
        invoice = self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/issue").json()
        payload = {
            "amount_piasters": 5000, "paid_on": "2026-11-02", "method": "instapay",
            "reference": "IP-REF-001", "note": "Part payment", "idempotency_key": "payment-key-0001",
        }
        first = self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/payments", json=payload)
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(first.json()["payment_state"], "partially_paid")
        self.assertEqual(first.json()["balance_piasters"], 12500)
        duplicate = self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/payments", json=payload)
        self.assertEqual(duplicate.status_code, 200, duplicate.text)
        self.assertEqual(len(duplicate.json()["payments"]), 1)
        conflict = dict(payload, amount_piasters=5001)
        self.assertEqual(
            self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/payments", json=conflict).status_code,
            409,
        )
        over = dict(payload, amount_piasters=12501, idempotency_key="payment-key-0002")
        self.assertEqual(
            self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/payments", json=over).status_code,
            422,
        )
        final = dict(payload, amount_piasters=12500, idempotency_key="payment-key-0003")
        paid = self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/payments", json=final)
        self.assertEqual(paid.status_code, 200, paid.text)
        self.assertEqual(paid.json()["payment_state"], "paid")
        self.assertEqual(paid.json()["balance_piasters"], 0)

    def test_void_requires_no_payments_and_is_audited(self):
        invoice = self.create_draft().json()
        issued = self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/issue").json()
        voided = self.mutate(
            self.client_a, "post", f"/invoices/{invoice['id']}/void",
            json={"reason": "Created in error"},
        )
        self.assertEqual(voided.status_code, 200, voided.text)
        self.assertEqual(voided.json()["status"], "void")
        self.assertEqual(voided.json()["payment_state"], "void")
        self.assertTrue(any(event["event_type"] == "voided" for event in voided.json()["events"]))

    def test_firm_and_case_membership_boundaries_return_404(self):
        invoice = self.create_draft().json()
        issued = self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/issue").json()
        self.assertEqual(self.client_b.get(f"/invoices/{invoice['id']}").status_code, 404)
        self.assertEqual(self.client_nonmember.get(f"/invoices/{invoice['id']}").status_code, 404)
        self.assertEqual(self.client_b.get("/invoices").json()["invoices"], [])

    def test_invoice_number_sequence_is_independent_per_firm(self):
        draft_a = self.create_draft().json()
        issued_a = self.mutate(self.client_a, "post", f"/invoices/{draft_a['id']}/issue").json()
        case_b = self.mutate(
            self.client_b, "post", "/cases",
            json={"title": "Firm B matter", "client": "Firm B client"},
        ).json()
        draft_b = self.mutate(
            self.client_b, "post", f"/cases/{case_b['id']}/invoices",
            json={"description": "Services", "lines": [
                {"description": "Consultation", "quantity_milli": 1000, "unit_price_piasters": 10000},
            ]},
        ).json()
        issued_b = self.mutate(self.client_b, "post", f"/invoices/{draft_b['id']}/issue").json()
        self.assertEqual(issued_a["invoice_number"], issued_b["invoice_number"])

    def test_finance_overview_aggregates_case_client_and_aging_totals(self):
        draft = self.create_draft().json()
        issued = self.mutate(self.client_a, "post", f"/invoices/{draft['id']}/issue").json()
        payment = {
            "amount_piasters": 5000, "paid_on": "2026-11-02", "method": "bank_transfer",
            "reference": "BANK-001", "note": "", "idempotency_key": "overview-key-001",
        }
        self.mutate(self.client_a, "post", f"/invoices/{issued['id']}/payments", json=payment)
        overview = self.client_a.get("/finance/invoices/overview")
        self.assertEqual(overview.status_code, 200, overview.text)
        data = overview.json()
        self.assertEqual(data["currency"], "EGP")
        self.assertEqual(data["issued_piasters"], 17500)
        self.assertEqual(data["paid_piasters"], 5000)
        self.assertEqual(data["outstanding_piasters"], 12500)
        self.assertEqual(data["cases"][0]["case_id"], self.case_id)
        self.assertEqual(data["clients"][0]["client_name"], "Client Snapshot")
        self.assertEqual(data["cases"][0]["aging"]["current"], 12500)
        other = self.client_b.get("/finance/invoices/overview").json()
        self.assertEqual(other["outstanding_piasters"], 0)

    def test_payment_receipt_is_printable_and_bound_to_invoice(self):
        draft = self.create_draft().json()
        issued = self.mutate(self.client_a, "post", f"/invoices/{draft['id']}/issue").json()
        payment = {
            "amount_piasters": 5000, "paid_on": "2026-11-02", "method": "instapay",
            "reference": "IP-RECEIPT-1", "note": "دفعة أولى", "idempotency_key": "receipt-key-001",
        }
        recorded = self.mutate(self.client_a, "post", f"/invoices/{issued['id']}/payments", json=payment)
        self.assertEqual(recorded.status_code, 200, recorded.text)
        payment_id = recorded.json()["payments"][0]["id"]
        receipt = self.client_a.get(f"/invoices/{issued['id']}/payments/{payment_id}/receipt")
        self.assertEqual(receipt.status_code, 200, receipt.text)
        self.assertIn("إيصال استلام دفعة أتعاب", receipt.text)
        self.assertIn("IP-RECEIPT-1", receipt.text)
        self.assertIn("ليس إيصالاً ضريبياً إلكترونياً", receipt.text)
        self.assertEqual(
            self.client_b.get(f"/invoices/{issued['id']}/payments/{payment_id}/receipt").status_code,
            404,
        )

    def test_print_view_is_arabic_and_disclaims_tax_invoice_status(self):
        invoice = self.create_draft().json()
        response = self.client_a.get(f"/invoices/{invoice['id']}/print")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("dir=\"rtl\"", response.text)
        self.assertIn("فاتورة أتعاب قانونية", response.text)
        self.assertIn("ليس فاتورة ضريبية إلكترونية", response.text)
        self.assertIn("Client Snapshot", response.text)

    def test_money_fields_reject_float_values(self):
        response = self.mutate(
            self.client_a, "post", f"/cases/{self.case_id}/invoices",
            json={"lines": [{"description": "Fraction", "quantity_milli": 1000,
                             "unit_price_piasters": 10.5}]},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
