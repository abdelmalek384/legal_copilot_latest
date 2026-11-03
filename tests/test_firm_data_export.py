"""Firm-scoped, audited ZIP export of CSV data."""
import csv
import io
import unittest
import zipfile

import app
from fastapi.testclient import TestClient
from tests.invoice_test_support import InvoiceTestSupport


class FirmDataExportTests(InvoiceTestSupport, unittest.TestCase):
    def _tenant_a(self):
        control = self.runtime.control_connection()
        owner_id = control.execute(
            "SELECT id FROM users WHERE email_normalized=?",
            ("invoice-owner-a@example.test",),
        ).fetchone()["id"]
        context = self.runtime.resolve_context(int(owner_id), self.firm_a)
        return self.runtime.firm_connection(context), int(owner_id)

    def _zip_csv(self, response, name):
        archive = zipfile.ZipFile(io.BytesIO(response.content))
        return list(csv.DictReader(io.StringIO(
            archive.read(name).decode("utf-8-sig")
        )))

    def test_admin_export_contains_firm_data_and_audit_event_only(self):
        case_b = self.mutate(
            self.client_b, "post", "/cases",
            json={"title": "Firm B confidential matter", "client": "Firm B Client"},
        )
        self.assertEqual(case_b.status_code, 200, case_b.text)

        tenant, owner_id = self._tenant_a()
        tenant.execute(
            "INSERT INTO notes(case_id,created_by,text) VALUES(?,?,?)",
            (self.case_id, owner_id, "Firm A private note"),
        )
        tenant.execute(
            "INSERT INTO deadlines(case_id,title,due,note,created_by) VALUES(?,?,?,?,?)",
            (self.case_id, "Firm A hearing", "2026-12-10", "Court date", owner_id),
        )
        tenant.execute(
            "INSERT INTO sessions(case_id,date,note,done) VALUES(?,?,?,?)",
            (self.case_id, "2026-12-10", "Firm A session", 0),
        )
        tenant.execute(
            "INSERT INTO fees(case_id,title,amount,paid,due,note,created_by) VALUES(?,?,?,?,?,?,?)",
            (self.case_id, "Firm A fee", 125.5, 25.0, "2026-12-01", "Fee note", owner_id),
        )
        tenant.commit()

        draft = self.create_draft().json()
        issued = self.mutate(
            self.client_a, "post", f"/invoices/{draft['id']}/issue"
        )
        self.assertEqual(issued.status_code, 200, issued.text)

        response = self.client_a.get(f"/firm/data-export.zip?firm_id={self.firm_a}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["content-type"], "application/zip")
        self.assertIn("no-store", response.headers.get("cache-control", ""))
        self.assertIn(".zip", response.headers["content-disposition"])

        archive = zipfile.ZipFile(io.BytesIO(response.content))
        names = set(archive.namelist())
        expected = {
            "firm.csv", "cases.csv", "clients.csv", "notes.csv", "deadlines.csv",
            "sessions.csv", "fees.csv", "tasks.csv", "case_members.csv",
            "case_activity.csv", "invoices.csv", "invoice_lines.csv",
            "invoice_payments.csv", "invoice_events.csv",
            "case_deletion_audit.csv", "security_audit_events.csv",
        }
        self.assertTrue(expected.issubset(names), sorted(expected - names))

        cases = self._zip_csv(response, "cases.csv")
        self.assertEqual([row["title"] for row in cases], ["Invoice matter"])
        self.assertNotIn("Firm B confidential matter", str(cases))
        self.assertIn("Client Snapshot", str(self._zip_csv(response, "clients.csv")))
        self.assertIn("Firm A private note", str(self._zip_csv(response, "notes.csv")))
        self.assertIn("Firm A hearing", str(self._zip_csv(response, "deadlines.csv")))
        self.assertIn("Firm A session", str(self._zip_csv(response, "sessions.csv")))
        self.assertIn("Firm A fee", str(self._zip_csv(response, "fees.csv")))
        self.assertEqual(len(self._zip_csv(response, "invoices.csv")), 1)

        audit = tenant.execute(
            "SELECT user_id,event FROM security_audit_events "
            "WHERE firm_id=? AND event='firm_data_export_created'",
            (self.firm_a,),
        ).fetchall()
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["user_id"], owner_id)

    def test_cross_firm_and_non_admin_requests_are_not_found_or_forbidden(self):
        other_firm_export = self.client_b.get(
            f"/firm/data-export.zip?firm_id={self.firm_a}"
        )
        self.assertEqual(other_firm_export.status_code, 404)

        # This identity belongs to a different firm, not to the requested firm.
        firm_c, _ = self.runtime.provision_firm("Firm C")
        self.runtime.create_initial_firm_owner(
            firm_c, "Firm C Owner", "firm-c-owner@example.test",
            app.hash_pw(self.password),
        )
        client_c = TestClient(app.app)
        try:
            login = client_c.post(
                "/login",
                json={"email": "firm-c-owner@example.test", "password": self.password},
            )
            self.assertEqual(login.status_code, 200, login.text)
            nonmember_export = client_c.get(
                f"/firm/data-export.zip?firm_id={self.firm_a}"
            )
            self.assertEqual(nonmember_export.status_code, 404)
        finally:
            client_c.close()

        same_firm_non_admin = self.client_nonmember.get(
            f"/firm/data-export.zip?firm_id={self.firm_a}"
        )
        self.assertEqual(same_firm_non_admin.status_code, 403)

    def test_export_is_rate_limited(self):
        url = f"/firm/data-export.zip?firm_id={self.firm_a}"
        for _ in range(3):
            response = self.client_a.get(url)
            self.assertEqual(response.status_code, 200, response.text)
        limited = self.client_a.get(url)
        self.assertEqual(limited.status_code, 429)


if __name__ == "__main__":
    unittest.main()
