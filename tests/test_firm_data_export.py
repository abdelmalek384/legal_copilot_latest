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

        original_bytes = b"verified original pleading bytes"
        staged = app._original_file_store().stage(self.firm_a, original_bytes)
        app._original_file_store().finalize(self.firm_a, staged.object_id)
        doc = tenant.execute(
            "INSERT INTO docs(case_id,name,added,firm_id,uploader_user_id,sha256,"
            "content_type,byte_size,extraction_status,ocr_used) "
            "VALUES(?,?,datetime('now'),?,?,?,?,?,'complete',0)",
            (
                self.case_id, "pleading.pdf", self.firm_a, owner_id,
                staged.sha256, "application/pdf", staged.byte_size,
            ),
        )
        tenant.execute(
            "INSERT INTO original_file_objects(object_id,document_id,firm_id,"
            "storage_backend,sha256,byte_size,content_type,state) "
            "VALUES(?,?,?,'local',?,?,?,'ready')",
            (
                staged.object_id, doc.lastrowid, self.firm_a, staged.sha256,
                staged.byte_size, "application/pdf",
            ),
        )
        tenant.execute(
            "UPDATE original_file_objects SET legal_hold=1,hold_reason=?,"
            "hold_set_by=?,hold_set_at=datetime('now') WHERE object_id=?",
            ("Retain original pleading for the pilot test", owner_id, staged.object_id),
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
            "case_deletion_audit.csv", "security_audit_events.csv", "documents.csv",
            "document_extraction_reviews.csv", "matter_chunks.csv", "research_conversations.csv",
            "research_messages.csv", "original_file_hold_events.csv", "product_feedback.csv",
            "product_feedback_events.csv", "original_files_manifest.csv",
            "firm_memberships.csv", "firm_invitations.csv", "identity_lifecycle_events.csv",
        }
        self.assertTrue(expected.issubset(names), sorted(expected - names))

        cases = self._zip_csv(response, "cases.csv")
        self.assertEqual([row["title"] for row in cases], ["Invoice matter"])
        self.assertNotIn("Firm B confidential matter", str(cases))
        self.assertIn("Client Snapshot", str(self._zip_csv(response, "clients.csv")))
        members = self._zip_csv(response, "firm_memberships.csv")
        self.assertEqual([row["email_display"] for row in members], ["invoice-owner-a@example.test", "invoice-nonmember@example.test"])
        self.assertEqual(members[0]["firm_role"], "admin")
        self.assertEqual(members[1]["firm_role"], "lawyer")
        invitation_header = zipfile.ZipFile(io.BytesIO(response.content)).read(
            "firm_invitations.csv"
        ).decode("utf-8-sig").splitlines()[0]
        self.assertIn("email_display", invitation_header)
        self.assertNotIn("token_hash", invitation_header)
        self.assertIn("Firm A private note", str(self._zip_csv(response, "notes.csv")))
        self.assertIn("Firm A hearing", str(self._zip_csv(response, "deadlines.csv")))
        self.assertIn("Firm A session", str(self._zip_csv(response, "sessions.csv")))
        self.assertIn("Firm A fee", str(self._zip_csv(response, "fees.csv")))
        self.assertEqual(len(self._zip_csv(response, "invoices.csv")), 1)
        documents = self._zip_csv(response, "documents.csv")
        self.assertEqual(documents[0]["name"], "pleading.pdf")
        manifest = self._zip_csv(response, "original_files_manifest.csv")
        self.assertEqual(manifest[0]["export_status"], "included")
        self.assertEqual(manifest[0]["legal_hold"], "1")
        original_path = manifest[0]["included_path"]
        self.assertEqual(archive.read(original_path), original_bytes)

        audit = tenant.execute(
            "SELECT user_id,event FROM security_audit_events "
            "WHERE firm_id=? AND event='firm_data_export'",
            (self.firm_a,),
        ).fetchall()
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["user_id"], owner_id)

    def test_cross_firm_and_non_admin_requests_are_not_found_or_forbidden(self):
        other_firm_export = self.client_b.get(
            f"/firm/data-export.zip?firm_id={self.firm_a}"
        )
        self.assertEqual(other_firm_export.status_code, 200, other_firm_export.text)
        other_archive = zipfile.ZipFile(io.BytesIO(other_firm_export.content))
        other_cases = other_archive.read("cases.csv").decode("utf-8-sig")
        self.assertIn("Firm B confidential matter", other_cases)
        self.assertNotIn("Invoice matter", other_cases)

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
            self.assertEqual(nonmember_export.status_code, 200, nonmember_export.text)
            nonmember_archive = zipfile.ZipFile(io.BytesIO(nonmember_export.content))
            nonmember_cases = nonmember_archive.read("cases.csv").decode("utf-8-sig")
            self.assertNotIn("Invoice matter", nonmember_cases)
        finally:
            client_c.close()

        same_firm_non_admin = self.client_nonmember.get(
            f"/firm/data-export.zip?firm_id={self.firm_a}"
        )
        self.assertEqual(same_firm_non_admin.status_code, 403)

    def test_demo_firm_export_is_not_available(self):
        demo_firm, _ = self.runtime.provision_firm("Demo Export Firm")
        control = self.runtime.control_connection()
        control.execute("UPDATE firms SET is_demo=1 WHERE id=?", (demo_firm,))
        control.commit()
        self.runtime.create_initial_firm_owner(
            demo_firm, "Demo Export Owner", "demo-export-owner@example.test",
            app.hash_pw(self.password),
        )
        demo_client = TestClient(app.app)
        try:
            login = demo_client.post(
                "/login",
                json={"email": "demo-export-owner@example.test", "password": self.password},
            )
            self.assertEqual(login.status_code, 200, login.text)
            response = demo_client.get(f"/firm/data-export.zip?firm_id={demo_firm}")
            self.assertEqual(response.status_code, 404)
        finally:
            demo_client.close()

    def test_original_integrity_mismatch_fails_closed_without_audit_event(self):
        tenant, owner_id = self._tenant_a()
        original_bytes = b"original bytes whose integrity must be checked"
        staged = app._original_file_store().stage(self.firm_a, original_bytes)
        app._original_file_store().finalize(self.firm_a, staged.object_id)
        doc = tenant.execute(
            "INSERT INTO docs(case_id,name,added,firm_id,uploader_user_id,sha256,"
            "content_type,byte_size,extraction_status,ocr_used) "
            "VALUES(?,?,datetime('now'),?,?,?,?,?,'complete',0)",
            (
                self.case_id, "integrity-check.pdf", self.firm_a, owner_id,
                staged.sha256, "application/pdf", staged.byte_size,
            ),
        )
        tenant.execute(
            "INSERT INTO original_file_objects(object_id,document_id,firm_id,"
            "storage_backend,sha256,byte_size,content_type,state) "
            "VALUES(?,?,?,'local',?,?,?,'ready')",
            (
                staged.object_id, doc.lastrowid, self.firm_a, staged.sha256,
                staged.byte_size, "application/pdf",
            ),
        )
        tenant.execute(
            "UPDATE original_file_objects SET sha256=? WHERE object_id=?",
            ("0" * 64, staged.object_id),
        )
        tenant.commit()

        response = self.client_a.get(f"/firm/data-export.zip?firm_id={self.firm_a}")
        self.assertEqual(response.status_code, 503)
        audit_count = tenant.execute(
            "SELECT COUNT(*) FROM security_audit_events "
            "WHERE firm_id=? AND event='firm_data_export'",
            (self.firm_a,),
        ).fetchone()[0]
        self.assertEqual(audit_count, 0)

    def test_export_is_rate_limited(self):
        url = f"/firm/data-export.zip?firm_id={self.firm_a}"
        for _ in range(2):
            response = self.client_a.get(url)
            self.assertEqual(response.status_code, 200, response.text)
        limited = self.client_a.get(url)
        self.assertEqual(limited.status_code, 429)


if __name__ == "__main__":
    unittest.main()
