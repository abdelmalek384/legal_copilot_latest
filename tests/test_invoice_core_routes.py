"""Invoice draft and issue route tests."""
import unittest

from tests.invoice_test_support import InvoiceTestSupport


class InvoiceCoreRouteTests(InvoiceTestSupport, unittest.TestCase):
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

    def test_money_fields_reject_float_values(self):
        response = self.mutate(
            self.client_a, "post", f"/cases/{self.case_id}/invoices",
            json={"lines": [{"description": "Fraction", "quantity_milli": 1000,
                             "unit_price_piasters": 10.5}]},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
