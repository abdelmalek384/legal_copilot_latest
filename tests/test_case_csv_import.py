"""Bounded, firm-scoped matter CSV import tests."""
import unittest

import app

from tests.invoice_test_support import InvoiceTestSupport


class CaseCSVImportTests(InvoiceTestSupport, unittest.TestCase):
    def test_admin_imports_multiple_matters_for_one_client_and_skips_duplicates(self):
        payload = {
            "csv": (
                "\ufefftitle;client;stage;case_number;case_year;court;circuit;opposing_party\n"
                "Employment claim;Imported CSV Client;Labour;100/2025;2025;Cairo Court;Labour Circuit;Employer A\n"
                "Contract dispute;Imported CSV Client;Civil;101/2025;2025;Cairo Court;Civil Circuit;Supplier B\n"
                "Contract dispute;Imported CSV Client;Civil;101/2025;2025;Cairo Court;Civil Circuit;Supplier B\n"
            )
        }
        control_before = self.runtime.control_connection()
        before_metrics = app._pilot_metrics_rows(control_before, weeks=1)
        before_cases_created = next(row for row in before_metrics if row["firm_id"] == self.firm_a)["cases_created"]
        response = self.mutate(self.client_a, "post", "/cases/import.csv", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {"created": 2, "skipped": 1, "rows": 3})

        cases = self.client_a.get("/cases").json()
        imported = [row for row in cases if row["title"] in {"Employment claim", "Contract dispute"}]
        self.assertEqual(len(imported), 2)
        self.assertEqual({row["client"] for row in imported}, {"Imported CSV Client"})
        self.assertEqual(len({row["client_id"] for row in imported}), 1)
        self.assertEqual(self.client_b.get("/cases").json(), [])

        control = self.runtime.control_connection()
        owner_id = control.execute(
            "SELECT id FROM users WHERE email_normalized=?",
            ("invoice-owner-a@example.test",),
        ).fetchone()["id"]
        tenant = self.runtime.firm_connection(
            self.runtime.resolve_context(owner_id, self.firm_a)
        )
        audit = " ".join(
            row["event"] for row in tenant.execute("SELECT event FROM security_audit_events").fetchall()
        )
        self.assertIn("case_csv_import:created=2;skipped=1", audit)
        self.assertNotIn("Employment claim", audit)
        self.assertNotIn("Imported CSV Client", audit)
        metrics = app._pilot_metrics_rows(control, weeks=1)
        firm_a_week = next(row for row in metrics if row["firm_id"] == self.firm_a)
        self.assertEqual(firm_a_week["cases_created"], before_cases_created + 2)

        repeated = self.mutate(self.client_a, "post", "/cases/import.csv", json=payload)
        self.assertEqual(repeated.status_code, 200, repeated.text)
        self.assertEqual(repeated.json(), {"created": 0, "skipped": 3, "rows": 3})

    def test_formula_like_imported_case_title_is_inert_and_neutralized_on_invoice_export(self):
        formula = '=HYPERLINK("https://attacker.invalid","open")'
        csv_text = (
            'title;client;stage;case_number;case_year;court;circuit;opposing_party\n'
            '"=HYPERLINK(""https://attacker.invalid"",""open"")";Synthetic CSV Client;Labour;901/2026;2026;Cairo Court;Labour Circuit;Synthetic Opponent\n'
        )
        imported = self.mutate(
            self.client_a, "post", "/cases/import.csv", json={"csv": csv_text}
        )
        self.assertEqual(imported.status_code, 200, imported.text)
        case = next(
            row for row in self.client_a.get("/cases").json()
            if row["title"] == formula
        )
        self.assertEqual(case["client"], "Synthetic CSV Client")

        draft = self.mutate(
            self.client_a, "post", f"/cases/{case['id']}/invoices",
            json={
                "description": "Synthetic import security test",
                "due_date": "2099-01-01",
                "lines": [{"description": "Synthetic service", "quantity_milli": 1000, "unit_price_piasters": 100}],
            },
        )
        self.assertEqual(draft.status_code, 200, draft.text)
        issued = self.mutate(
            self.client_a, "post", f"/invoices/{draft.json()['id']}/issue"
        )
        self.assertEqual(issued.status_code, 200, issued.text)

        import csv
        import io
        exported = self.client_a.get("/invoices/export.csv")
        self.assertEqual(exported.status_code, 200, exported.text)
        rows = list(csv.DictReader(io.StringIO(exported.content.decode("utf-8-sig"))))
        exported_case = next(row for row in rows if row["invoice_number"] == issued.json()["invoice_number"])
        self.assertEqual(exported_case["case_title"], "'" + formula)
        self.assertNotIn("\r\n" + formula, exported.text)

    def test_non_admin_and_malformed_imports_are_rejected_without_partial_writes(self):
        denied = self.mutate(
            self.client_nonmember, "post", "/cases/import.csv",
            json={"csv": "title\nUnauthorized matter\n"},
        )
        self.assertEqual(denied.status_code, 403)

        before = len(self.client_a.get("/cases").json())
        malformed = self.mutate(
            self.client_a, "post", "/cases/import.csv",
            json={"csv": "title,client\nValid matter,Client A\nBroken row,Client B,extra\n"},
        )
        self.assertEqual(malformed.status_code, 422, malformed.text)
        self.assertEqual(len(self.client_a.get("/cases").json()), before)

    def test_import_rejects_more_than_500_rows_before_writing(self):
        csv_text = "title\n" + "".join(f"CSV Matter {index}\n" for index in range(501))
        response = self.mutate(
            self.client_a, "post", "/cases/import.csv", json={"csv": csv_text}
        )
        self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(len(self.client_a.get("/cases").json()), 1)


if __name__ == "__main__":
    unittest.main()
