"""Firm-admin ZIP exports stay inside the active tenant and are audited."""
import csv
import io
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class FirmDataExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-firm-export-")
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_OBJECT_STORAGE_ROOT",
            "COPILOT_OBJECT_STORAGE_BACKEND", "COPILOT_ENV", "ADMIN_TOKEN",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        for name in self.env_names:
            os.environ.pop(name, None)
        os.environ.update({
            "COPILOT_CONTROL_DB": str(self.root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(self.root / "tenants"),
            "COPILOT_CORPUS_DB": str(self.root / "corpus.sqlite3"),
            "COPILOT_OBJECT_STORAGE_ROOT": str(self.root / "objects"),
            "COPILOT_OBJECT_STORAGE_BACKEND": "local",
            "COPILOT_ENV": "development",
            "ADMIN_TOKEN": "firm-export-test-admin-token-long-enough",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Export Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Export Firm B")
        self.clients = {}
        self.user_ids = {}
        for key, firm_id in (("a", self.firm_a), ("b", self.firm_b)):
            email = f"export-{key}@example.test"
            password = f"Export-{key}-Strong-Password-2026!"
            self.runtime.create_initial_firm_owner(
                firm_id, f"Export Admin {key}", email, app.hash_pw(password)
            )
            user_id = int(self.runtime.control_connection().execute(
                "SELECT id FROM users WHERE email_normalized=?", (email,)
            ).fetchone()["id"])
            self.user_ids[key] = user_id
            client = TestClient(app.app)
            response = client.post("/login", json={"email": email, "password": password})
            self.assertEqual(response.status_code, 200, response.text)
            self.clients[key] = client

        member_id = self.runtime.create_global_identity(
            "Export Firm A Lawyer", "export-member@example.test",
            app.hash_pw("Export-member-Strong-Password-2026!"),
        )
        self.runtime.create_firm_membership(member_id, self.firm_a, "lawyer")
        member_client = TestClient(app.app)
        response = member_client.post("/login", json={
            "email": "export-member@example.test",
            "password": "Export-member-Strong-Password-2026!",
        })
        self.assertEqual(response.status_code, 200, response.text)
        self.clients["member"] = member_client
        self._seed_firm(self.firm_a, self.user_ids["a"], "A_CASE_PRIVATE_91",
                        '=HYPERLINK("https://evil.invalid")')
        self._seed_firm(self.firm_b, self.user_ids["b"], "B_CASE_PRIVATE_92",
                        "Firm B confidential client")

    def _seed_firm(self, firm_id, user_id, title, client_name):
        context = self.runtime.resolve_context(user_id, firm_id)
        tenant = self.runtime.firm_connection(context)
        case_id = int(tenant.execute(
            "INSERT INTO cases(title,client,stage,status,created_by,firm_id) "
            "VALUES(?,?,?,'open',?,?)",
            (title, client_name, "استئناف", user_id, firm_id),
        ).lastrowid)
        tenant.execute("UPDATE cases SET client=? WHERE id=?", (client_name, case_id))
        stored_client = tenant.execute(
            "SELECT client,firm_id FROM cases WHERE id=?", (case_id,)
        ).fetchone()
        if stored_client["client"] != client_name or int(stored_client["firm_id"]) != firm_id:
            raise AssertionError("firm export fixture did not persist its client/firm linkage")
        tenant.execute(
            "INSERT INTO notes(case_id,created_by,text) VALUES(?,?,?)",
            (case_id, user_id, f"{title} private note"),
        )
        tenant.execute(
            "INSERT INTO deadlines(case_id,title,due,note,created_by) VALUES(?,?,?,?,?)",
            (case_id, "Export deadline", "2026-12-10", f"{title} deadline note", user_id),
        )
        tenant.execute(
            "INSERT INTO sessions(case_id,date,note,done) VALUES(?,?,?,0)",
            (case_id, "2026-12-11", f"{title} hearing note"),
        )
        tenant.execute(
            "INSERT INTO fees(case_id,title,amount,paid,due,note,created_by) VALUES(?,?,?,?,?,?,?)",
            (case_id, "Consultation fee", 1000, 250, "2026-12-15", f"{title} fee note", user_id),
        )
        tenant.execute(
            "INSERT INTO tasks(case_id,title,assignee,due,status,created_by) VALUES(?,?,?,?,?,?)",
            (case_id, "Prepare bundle", user_id, "2026-12-12", "open", user_id),
        )
        tenant.execute(
            "INSERT INTO events(case_id,who,at,text) VALUES(?,?,?,?)",
            (case_id, "Export Admin", "2026-11-03", f"{title} history event"),
        )
        tenant.execute(
            "INSERT INTO members(case_id,user_id,role) VALUES(?,?,?)",
            (case_id, user_id, "lead"),
        )
        invoice_id = int(tenant.execute(
            "INSERT INTO invoices(case_id,invoice_number,status,currency,client_name_snapshot,"
            "case_title_snapshot,description,subtotal_piasters,total_piasters,issue_date,due_date,"
            "created_by,issued_at) VALUES(?,NULL,'draft','EGP',?,?,?,?,?,?,?,?,NULL)",
            (case_id, client_name, title, "Export invoice",
             10000, 10000, "2026-11-03", "2026-12-03", user_id),
        ).lastrowid)
        tenant.execute(
            "INSERT INTO invoice_lines(invoice_id,position,description,quantity_milli,"
            "unit_price_piasters,line_total_piasters) VALUES(?,1,?,1000,10000,10000)",
            (invoice_id, "Legal service"),
        )
        tenant.execute(
            "UPDATE invoices SET status='issued',invoice_number=?,issued_at=? WHERE id=?",
            (f"EXP-{firm_id}-001", "2026-11-03 10:00:00", invoice_id),
        )
        tenant.execute(
            "INSERT INTO invoice_payments(invoice_id,amount_piasters,paid_on,method,reference,note,"
            "idempotency_key,recorded_by) VALUES(?,2500,'2026-11-04','bank_transfer','REF-001',"
            "'partial payment','export-payment-key-001',?)",
            (invoice_id, user_id),
        )
        tenant.execute(
            "INSERT INTO invoice_events(invoice_id,actor_user_id,event_type,details_json) "
            "VALUES(?,?,'issued','{}')",
            (invoice_id, user_id),
        )
        tenant.commit()

    def tearDown(self):
        for client in self.clients.values():
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

    def test_admin_export_contains_requested_csvs_and_only_active_firm_data(self):
        response = self.clients["a"].get("/firm/data-export.zip")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("application/zip", response.headers.get("content-type", ""))
        self.assertEqual(response.headers.get("cache-control"), "no-store")
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            names = set(archive.namelist())
            self.assertTrue({
                "cases.csv", "clients.csv", "notes.csv", "deadlines.csv", "sessions.csv",
                "fees.csv", "invoices.csv", "invoice_lines.csv", "invoice_payments.csv",
            }.issubset(names))
            all_text = "\n".join(
                archive.read(name).decode("utf-8-sig") for name in names
            )
            self.assertIn("A_CASE_PRIVATE_91", all_text)
            self.assertNotIn("B_CASE_PRIVATE_92", all_text)
            self.assertNotIn("Firm B confidential client", all_text)
            clients_csv = archive.read("clients.csv").decode("utf-8-sig")
            self.assertIn("client_name", clients_csv)
            self.assertIn("'=HYPERLINK", clients_csv)
            self.assertIn("https://evil.invalid", clients_csv)
            self.assertIn("Export invoice", archive.read("invoices.csv").decode("utf-8-sig"))
            self.assertIn("partial payment", archive.read("invoice_payments.csv").decode("utf-8-sig"))

        context = self.runtime.resolve_context(self.user_ids["a"], self.firm_a)
        tenant = self.runtime.firm_connection(context)
        audit = tenant.execute(
            "SELECT firm_id,user_id,event FROM security_audit_events WHERE event='firm_data_export'"
        ).fetchall()
        self.assertEqual(len(audit), 1)
        self.assertEqual((audit[0]["firm_id"], audit[0]["user_id"]),
                         (self.firm_a, self.user_ids["a"]))

    def test_other_firm_exports_its_own_data_and_cannot_read_firm_a(self):
        response = self.clients["b"].get("/firm/data-export.zip?firm_id=" + str(self.firm_a))
        self.assertEqual(response.status_code, 200, response.text)
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            cases = archive.read("cases.csv").decode("utf-8-sig")
            self.assertIn("B_CASE_PRIVATE_92", cases)
            self.assertNotIn("A_CASE_PRIVATE_91", cases)

    def test_non_admin_firm_member_is_denied(self):
        response = self.clients["member"].get("/firm/data-export.zip")
        self.assertEqual(response.status_code, 403, response.text)

    def test_export_is_rate_limited(self):
        first = self.clients["a"].get("/firm/data-export.zip")
        second = self.clients["a"].get("/firm/data-export.zip")
        third = self.clients["a"].get("/firm/data-export.zip")
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual(third.status_code, 429, third.text)


if __name__ == "__main__":
    unittest.main()
