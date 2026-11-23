"""Invoice payment, aging, and receipt route tests."""
import sqlite3
import unittest

from fastapi.testclient import TestClient

import app

from tests.invoice_test_support import InvoiceTestSupport


class InvoicePaymentRouteTests(InvoiceTestSupport, unittest.TestCase):
    def test_non_lead_case_member_cannot_create_or_mutate_financial_records(self):
        draft_response = self.create_draft()
        self.assertEqual(draft_response.status_code, 200, draft_response.text)
        draft = draft_response.json()
        issued_response = self.mutate(
            self.client_a, "post", f"/invoices/{draft['id']}/issue"
        )
        self.assertEqual(issued_response.status_code, 200, issued_response.text)
        issued = issued_response.json()
        recorded_fee = self.mutate(
            self.client_a, "post", f"/cases/{self.case_id}/fees",
            json={"title": "Confidential fee", "amount": 5000, "paid": 0, "due": "2099-01-01", "note": ""},
        )
        self.assertEqual(recorded_fee.status_code, 200, recorded_fee.text)

        lawyer_id = self.runtime.create_global_identity(
            "Invoice Case Lawyer", "invoice-case-lawyer@example.test",
            app.hash_pw(self.password),
        )
        self.runtime.create_firm_membership(lawyer_id, self.firm_a, "lawyer")
        tenant = self.runtime._tenant_router.connection_for_firm(self.firm_a)
        tenant.execute(
            "INSERT INTO members(case_id,user_id,role) VALUES(?,?,'member')",
            (self.case_id, lawyer_id),
        )
        tenant.commit()

        lawyer = TestClient(app.app)
        try:
            login = lawyer.post(
                "/login",
                json={"email": "invoice-case-lawyer@example.test", "password": self.password},
            )
            self.assertEqual(login.status_code, 200, login.text)

            create = self.mutate(
                lawyer, "post", f"/cases/{self.case_id}/invoices",
                json={
                    "description": "Unauthorized draft",
                    "due_date": "2099-01-01",
                    "lines": [{"description": "Work", "quantity_milli": 1000, "unit_price_piasters": 1000}],
                },
            )
            self.assertEqual(create.status_code, 404, create.text)

            fee = self.mutate(
                lawyer, "post", f"/cases/{self.case_id}/fees",
                json={"title": "Unauthorized fee", "amount": 1000, "paid": 0, "due": None, "note": ""},
            )
            self.assertEqual(fee.status_code, 404, fee.text)

            edit = self.mutate(
                lawyer, "put", f"/invoices/{draft['id']}",
                json={
                    "description": "Unauthorized edit",
                    "due_date": "2099-01-01",
                    "lines": [{"description": "Work", "quantity_milli": 1000, "unit_price_piasters": 1000}],
                },
            )
            self.assertEqual(edit.status_code, 404, edit.text)
            issue = self.mutate(lawyer, "post", f"/invoices/{draft['id']}/issue")
            self.assertEqual(issue.status_code, 404, issue.text)

            payment = self.mutate(
                lawyer, "post", f"/invoices/{issued['id']}/payments",
                json={
                    "amount_piasters": 1000, "paid_on": "2026-11-16",
                    "method": "cash", "reference": "", "note": "",
                    "idempotency_key": "nonlead-payment-key-01",
                },
            )
            self.assertEqual(payment.status_code, 404, payment.text)
            void = self.mutate(
                lawyer, "post", f"/invoices/{issued['id']}/void",
                json={"reason": "Unauthorized void attempt"},
            )
            self.assertEqual(void.status_code, 404, void.text)

            self.assertEqual(
                lawyer.get(f"/invoices/{issued['id']}").status_code, 404
            )
            self.assertEqual(lawyer.get("/invoices").json()["invoices"], [])
            self.assertEqual(
                lawyer.get(f"/invoices?case_id={self.case_id}").json()["invoices"], []
            )
            ledger_export = lawyer.get("/invoices/export.csv")
            self.assertEqual(ledger_export.status_code, 200, ledger_export.text)
            self.assertNotIn(issued["invoice_number"], ledger_export.text)
            case_detail = lawyer.get(f"/cases/{self.case_id}")
            self.assertEqual(case_detail.status_code, 200, case_detail.text)
            self.assertEqual(case_detail.json()["fees"], [])
            self.assertEqual(
                lawyer.get("/finance/invoices/overview").json()["outstanding_piasters"], 0
            )
            self.assertEqual(lawyer.get("/finance/overview").json()["fee_count"], 0)
        finally:
            lawyer.close()

    def test_partial_full_payment_idempotency_and_overpayment(self):
        invoice = self.create_draft().json()
        invoice = self.mutate(self.client_a, "post", f"/invoices/{invoice['id']}/issue").json()
        payload = {
            "amount_piasters": 5000, "paid_on": "2026-11-02", "method": "instapay",
            "reference": " IP-REF-001 ", "note": " Part payment ", "idempotency_key": "payment-key-0001",
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
        self.assertEqual(
            self.client_nonmember.get(f"/invoices/{issued['id']}/payments/{payment_id}/receipt").status_code,
            404,
        )
        self.assertEqual(
            self.mutate(self.client_nonmember, "post", f"/invoices/{issued['id']}/payments", json=payment).status_code,
            404,
        )
        self.assertEqual(
            self.client_nonmember.get("/finance/invoices/overview").json()["outstanding_piasters"],
            0,
        )

    def test_issued_lines_and_payment_ledger_are_append_only(self):
        draft = self.create_draft().json()
        issued = self.mutate(self.client_a, "post", f"/invoices/{draft['id']}/issue").json()
        tenant = self.runtime._tenant_router.connection_for_firm(self.firm_a)
        with self.assertRaises(sqlite3.IntegrityError):
            tenant.execute(
                "UPDATE invoice_lines SET description='tampered' WHERE invoice_id=?",
                (issued["id"],),
            )
        tenant.rollback()
        payment = {
            "amount_piasters": 1000, "paid_on": "2026-11-02", "method": "cash",
            "reference": "", "note": "", "idempotency_key": "append-only-key-01",
        }
        recorded = self.mutate(
            self.client_a, "post", f"/invoices/{issued['id']}/payments", json=payment,
        )
        self.assertEqual(recorded.status_code, 200, recorded.text)
        payment_id = recorded.json()["payments"][0]["id"]
        with self.assertRaises(sqlite3.IntegrityError):
            tenant.execute(
                "UPDATE invoice_payments SET amount_piasters=1 WHERE id=?",
                (payment_id,),
            )
        tenant.rollback()
        with self.assertRaises(sqlite3.IntegrityError):
            tenant.execute("DELETE FROM invoice_payments WHERE id=?", (payment_id,))
        tenant.rollback()
        blocked_void = self.mutate(
            self.client_a, "post", f"/invoices/{issued['id']}/void",
            json={"reason": "Attempt to void paid invoice"},
        )
        self.assertEqual(blocked_void.status_code, 409)

    def test_print_view_is_arabic_and_disclaims_tax_invoice_status(self):
        invoice = self.create_draft().json()
        response = self.client_a.get(f"/invoices/{invoice['id']}/print")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("dir=\"rtl\"", response.text)
        self.assertIn("فاتورة أتعاب قانونية", response.text)
        self.assertIn("ليس فاتورة ضريبية إلكترونية", response.text)
        self.assertIn("Client Snapshot", response.text)

if __name__ == "__main__":
    unittest.main()
