"""Bounded, tenant-local CSV client import tests."""
import unittest

from tests.invoice_test_support import InvoiceTestSupport


class ClientCSVImportTests(InvoiceTestSupport, unittest.TestCase):
    def test_admin_imports_profiles_and_skips_existing_names_without_auditing_pii(self):
        payload = {
            "csv": (
                "\ufeffname;phone;email;address;notes\n"
                "New CSV Client;+20 100 222 3333;new@example.test;Cairo;Imported synthetic record\n"
                "Client Snapshot;;;;Existing profile must not be overwritten\n"
                " new csv client ;+20 100 999 8888;duplicate@example.test;;\n"
            )
        }
        response = self.mutate(self.client_a, "post", "/clients/import.csv", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {"created": 1, "skipped": 2, "rows": 3})
        profiles = self.client_a.get("/clients").json()
        imported = next(item for item in profiles if item["name"] == "New CSV Client")
        self.assertEqual(imported["phone"], "+20 100 222 3333")
        self.assertEqual(imported["email"], "new@example.test")
        self.assertEqual(self.client_b.get("/clients").json(), [])
        events = self.runtime.firm_connection(
            self.runtime.resolve_context(
                self.runtime.control_connection().execute(
                    "SELECT id FROM users WHERE email_normalized=?",
                    ("invoice-owner-a@example.test",),
                ).fetchone()["id"],
                self.firm_a,
            )
        ).execute("SELECT event FROM security_audit_events").fetchall()
        audit = " ".join(row["event"] for row in events)
        self.assertIn("client_csv_import:created=1;skipped=1", audit)
        self.assertNotIn("New CSV Client", audit)
        self.assertNotIn("new@example.test", audit)

    def test_non_admin_and_malformed_or_oversized_imports_are_rejected_without_partial_writes(self):
        denied = self.mutate(
            self.client_nonmember, "post", "/clients/import.csv",
            json={"csv": "name\nUnauthorized Client\n"},
        )
        self.assertEqual(denied.status_code, 403)

        malformed = self.mutate(
            self.client_a, "post", "/clients/import.csv",
            json={"csv": "name,phone\nValid Client,123\nBroken Row,123,extra\n"},
        )
        self.assertEqual(malformed.status_code, 422, malformed.text)
        self.assertEqual(
            [item["name"] for item in self.client_a.get("/clients").json()],
            ["Client Snapshot"],
        )

        oversized = self.mutate(
            self.client_a, "post", "/clients/import.csv",
            json={"csv": "name\n" + ("A" * 201) + "\n"},
        )
        self.assertEqual(oversized.status_code, 422, oversized.text)

    def test_import_rejects_more_than_500_data_rows(self):
        csv_text = "name\n" + "".join(f"CSV Client {i}\n" for i in range(501))
        response = self.mutate(
            self.client_a, "post", "/clients/import.csv", json={"csv": csv_text}
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            [item["name"] for item in self.client_a.get("/clients").json()],
            ["Client Snapshot"],
        )


if __name__ == "__main__":
    unittest.main()
