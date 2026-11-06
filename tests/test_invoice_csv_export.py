"""Authorization and spreadsheet-safe CSV export for the invoice ledger."""
import csv
import io
import unittest

from tests.invoice_test_support import InvoiceTestSupport


class InvoiceCsvExportTests(InvoiceTestSupport, unittest.TestCase):
    def test_export_contains_exact_piaster_totals_and_only_visible_firm_invoices(self):
        draft = self.create_draft().json()
        issued = self.mutate(self.client_a, "post", f"/invoices/{draft['id']}/issue").json()
        payment = {
            "amount_piasters": 5000, "paid_on": "2026-11-03", "method": "instapay",
            "reference": "CSV-REF-001", "note": "", "idempotency_key": "csv-export-key-01",
        }
        self.mutate(self.client_a, "post", f"/invoices/{issued['id']}/payments", json=payment)

        response = self.client_a.get("/invoices/export.csv")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("text/csv", response.headers["content-type"])
        self.assertIn('attachment; filename="legal-copilot-invoices.csv"',
                      response.headers["content-disposition"])
        self.assertTrue(response.content.startswith(b"\xef\xbb\xbf"))
        rows = list(csv.DictReader(io.StringIO(response.content.decode("utf-8-sig"))))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["invoice_number"], issued["invoice_number"])
        self.assertEqual(row["payment_state"], "partially_paid")
        self.assertEqual(row["total_egp"], "175.00")
        self.assertEqual(row["paid_egp"], "50.00")
        self.assertEqual(row["balance_egp"], "125.00")
        self.assertEqual(row["currency"], "EGP")

        other_firm = self.client_b.get("/invoices/export.csv")
        self.assertEqual(other_firm.status_code, 200, other_firm.text)
        self.assertEqual(
            list(csv.DictReader(io.StringIO(other_firm.content.decode("utf-8-sig")))),
            [],
        )
        nonmember = self.client_nonmember.get("/invoices/export.csv")
        self.assertEqual(nonmember.status_code, 200, nonmember.text)
        self.assertEqual(
            list(csv.DictReader(io.StringIO(nonmember.content.decode("utf-8-sig")))),
            [],
        )

    def test_export_filters_match_invoice_list_and_formula_prefixes_are_neutralized(self):
        draft = self.create_draft().json()
        issued = self.mutate(self.client_a, "post", f"/invoices/{draft['id']}/issue").json()
        unpaid = self.client_a.get("/invoices/export.csv?payment_state=unpaid")
        self.assertEqual(unpaid.status_code, 200, unpaid.text)
        rows = list(csv.DictReader(io.StringIO(unpaid.content.decode("utf-8-sig"))))
        self.assertEqual([row["invoice_number"] for row in rows], [issued["invoice_number"]])

        self.assertEqual(app_safe("=HYPERLINK(\"https://bad.example\")"),
                         "'=HYPERLINK(\"https://bad.example\")")
        self.assertEqual(app_safe("  @SUM(1,1)"), "'  @SUM(1,1)")
        self.assertEqual(app_safe("Client Snapshot"), "Client Snapshot")


def app_safe(value):
    import app
    return app._invoice_csv_text(value)


if __name__ == "__main__":
    unittest.main()
