"""Fictional demo-firm provisioning, marking, seeding, and guarded removal."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from fastapi.testclient import TestClient
from unittest.mock import patch

import app
import manage
from database_runtime import DatabaseRuntime


class DemoFirmCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-demo-firm-")
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_OBJECT_STORAGE_ROOT",
            "COPILOT_OBJECT_STORAGE_BACKEND", "COPILOT_ENV", "ADMIN_TOKEN",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ.pop("COPILOT_DB", None)
        os.environ.update({
            "COPILOT_CONTROL_DB": str(self.root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(self.root / "tenants"),
            "COPILOT_CORPUS_DB": str(self.root / "corpus.sqlite3"),
            "COPILOT_OBJECT_STORAGE_ROOT": str(self.root / "objects"),
            "COPILOT_OBJECT_STORAGE_BACKEND": "local",
            "COPILOT_ENV": "development",
            "ADMIN_TOKEN": "demo-firm-test-admin-token-long-enough",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()

    def tearDown(self):
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

    def run_cli(self, args, password="DemoFirm-Strong-Password-2026!"):
        output = io.StringIO()
        with patch.object(manage, "read_password", return_value=password), contextlib.redirect_stdout(output):
            manage.demo_firm_cli(args)
        return json.loads(output.getvalue())

    def test_create_seeds_ten_fictional_cases_deadlines_fees_and_issued_invoice(self):
        result = self.run_cli(Namespace(
            demo_action="create", firm_name="مكتب تجريبي للاختبار",
            owner_name="مدير المكتب التجريبي", owner_email="demo-owner@example.test",
        ))
        self.assertEqual(result["status"], "created")
        self.assertTrue(result["demo"])
        self.assertEqual(result["cases"], 10)
        self.assertEqual(result["deadlines"], 10)
        self.assertEqual(result["fees"], 10)
        self.assertEqual(result["issued_invoices"], 1)
        firm_id = result["firm_id"]
        control = self.runtime.control_connection()
        firm = control.execute("SELECT is_demo,status FROM firms WHERE id=?", (firm_id,)).fetchone()
        self.assertEqual((firm["is_demo"], firm["status"]), (1, "active"))
        owner_id = control.execute(
            "SELECT user_id FROM firm_memberships WHERE firm_id=?", (firm_id,)
        ).fetchone()["user_id"]
        context = self.runtime.resolve_context(owner_id, firm_id)
        tenant = self.runtime.firm_connection(context)
        self.assertEqual(tenant.execute("SELECT COUNT(*) FROM cases").fetchone()[0], 10)
        self.assertEqual(tenant.execute("SELECT COUNT(*) FROM deadlines").fetchone()[0], 10)
        self.assertEqual(tenant.execute("SELECT COUNT(*) FROM fees").fetchone()[0], 10)
        invoice = tenant.execute("SELECT status,description FROM invoices").fetchone()
        self.assertEqual(invoice["status"], "issued")
        self.assertIn("تجريبية", invoice["description"])

        client = TestClient(app.app)
        login = client.post("/login", json={
            "email": "demo-owner@example.test",
            "password": "DemoFirm-Strong-Password-2026!",
        })
        self.assertEqual(login.status_code, 200, login.text)
        session = client.get("/session")
        self.assertEqual(session.status_code, 200, session.text)
        self.assertIs(session.json().get("is_demo"), True)
        client.close()
        app._meter_pilot_metric({"firm_id": firm_id}, "cases_created")
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM pilot_metrics_weekly_counts WHERE firm_id=?",
                (firm_id,),
            ).fetchone()[0],
            0,
        )
        self.assertFalse(any(
            row["firm_id"] == firm_id for row in app._pilot_metrics_rows(control, weeks=1)
        ))

    def test_removal_refuses_demo_with_original_file_objects(self):
        result = self.run_cli(Namespace(
            demo_action="create", firm_name="Demo with retained original",
            owner_name="Demo Owner", owner_email="demo-original@example.test",
        ))
        firm_id = result["firm_id"]
        control = self.runtime.control_connection()
        filename = control.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
        ).fetchone()["database_file"]
        db_path = self.root / "tenants" / filename
        owner_id = control.execute(
            "SELECT id FROM users WHERE email_normalized=?",
            ("demo-original@example.test",),
        ).fetchone()["id"]
        context = self.runtime.resolve_context(int(owner_id), firm_id)
        tenant = self.runtime.firm_connection(context)
        case_id = tenant.execute("SELECT id FROM cases ORDER BY id LIMIT 1").fetchone()["id"]
        doc = tenant.execute(
            "INSERT INTO docs(case_id,name,added,firm_id,sha256,content_type,byte_size,extraction_status,ocr_used) "
            "VALUES(?,?,datetime('now'),?,?,?,1,'complete',0)",
            (case_id, "demo-original.pdf", firm_id, "a" * 64, "application/pdf"),
        )
        tenant.execute(
            "INSERT INTO original_file_objects(object_id,document_id,firm_id,storage_backend,sha256,byte_size,content_type,state) "
            "VALUES(?,?,?,'local',?,1,'application/pdf','ready')",
            ("d" * 32, int(doc.lastrowid), firm_id, "a" * 64),
        )
        tenant.commit()

        with self.assertRaisesRegex(SystemExit, "original-file objects"):
            self.run_cli(Namespace(
                demo_action="remove", firm_id=firm_id, confirm_remove=True,
            ))
        self.assertTrue(db_path.is_file())
        firm = control.execute(
            "SELECT status,is_demo FROM firms WHERE id=?", (firm_id,)
        ).fetchone()
        self.assertEqual((firm["status"], firm["is_demo"]), ("active", 1))

    def test_removal_refuses_non_demo_and_removes_only_marked_demo_firm(self):
        normal_id, _ = self.runtime.provision_firm("Ordinary Firm")
        with self.assertRaisesRegex(SystemExit, "not marked as demo"):
            self.run_cli(Namespace(demo_action="remove", firm_id=normal_id, confirm_remove=True))
        result = self.run_cli(Namespace(
            demo_action="create", firm_name="مكتب تجريبي للحذف",
            owner_name="مدير تجريبي", owner_email="demo-remove@example.test",
        ))
        firm_id = result["firm_id"]
        control = self.runtime.control_connection()
        filename = control.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
        ).fetchone()["database_file"]
        db_path = self.root / "tenants" / filename
        self.assertTrue(db_path.is_file())
        removed = self.run_cli(Namespace(
            demo_action="remove", firm_id=firm_id, confirm_remove=True,
        ))
        self.assertTrue(removed["database_deleted"])
        self.assertFalse(db_path.exists())
        firm = control.execute("SELECT status,is_demo FROM firms WHERE id=?", (firm_id,)).fetchone()
        self.assertEqual((firm["status"], firm["is_demo"]), ("disabled", 1))
        catalog = control.execute(
            "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
        ).fetchone()
        self.assertEqual((catalog["status"], catalog["database_file"]), ("disabled", None))
        self.assertEqual(
            control.execute("SELECT status FROM firm_memberships WHERE firm_id=?", (firm_id,)).fetchone()["status"],
            "revoked",
        )


if __name__ == "__main__":
    unittest.main()
