"""Firm-scoped exact-piaster invoice and payment API tests."""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class InvoiceTestSupport:
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

