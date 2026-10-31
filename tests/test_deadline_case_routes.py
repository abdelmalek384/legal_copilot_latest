"""Authenticated case-scoped deadline estimate route tests.

All firms, users, cases, and dates are synthetic. The route must enforce the
same case-membership boundary as the existing case workspace.
"""
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class CaseDeadlineEstimateRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-deadline-route-")
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
            ADMIN_TOKEN="deadline-route-test-admin-token-long-enough",
        )
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Deadline Test Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Deadline Test Firm B")
        self.password_a = "Deadline-test-password-A-2026!"
        self.password_b = "Deadline-test-password-B-2026!"
        self.runtime.create_initial_firm_owner(
            self.firm_a, "Deadline Owner A", "deadline-a@example.test",
            app.hash_pw(self.password_a),
        )
        self.runtime.create_initial_firm_owner(
            self.firm_b, "Deadline Owner B", "deadline-b@example.test",
            app.hash_pw(self.password_b),
        )
        self.client = TestClient(app.app)
        login = self.client.post(
            "/login", json={"email": "deadline-a@example.test", "password": self.password_a}
        )
        self.assertEqual(login.status_code, 200, login.text)
        created = self._mutate(
            "post", "/cases", json={"title": "Synthetic deadline matter", "client": "Synthetic client"}
        )
        self.assertEqual(created.status_code, 200, created.text)
        self.case_id = created.json()["id"]

    def tearDown(self):
        self.client.close()
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

    def _mutate(self, method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = self.client.cookies.get("lc_csrf", "")
        return getattr(self.client, method)(url, headers=headers, **kwargs)

    def test_authenticated_user_can_list_draft_rules_and_preview_case_deadline(self):
        catalog = self.client.get("/deadline-rules")
        self.assertEqual(catalog.status_code, 200, catalog.text)
        self.assertEqual(catalog.json()["status"], "draft_unverified")
        self.assertTrue(catalog.json()["rules"])
        self.assertTrue(all(not rule["verified"] for rule in catalog.json()["rules"]))

        response = self.client.get(
            f"/cases/{self.case_id}/deadline-estimate",
            params={"rule_id": "civil_cassation_60d", "trigger": "2026-10-26"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["final_due"], "2026-12-27")
        self.assertFalse(result["verified_rule"])
        self.assertTrue(result["warnings"])
        self.assertIn("disclaimer", result)

    def test_case_brief_uses_authorized_case_records_and_validates_citations(self):
        self._mutate("post", f"/cases/{self.case_id}/notes", json={"text": "تم تقديم صحيفة الدعوى"})
        self._mutate("post", f"/cases/{self.case_id}/sessions", json={"date": "2026-11-10", "note": "تأجيل لنظر المستندات"})
        captured = {}
        def fake_llm(prompt):
            captured["prompt"] = prompt
            return "تتضمن القضية ملاحظة عن صحيفة الدعوى [2]."
        with patch.dict("os.environ", {"LLM_FIRM_DATA_PROCESSING_APPROVED": "1"}), patch.object(app, "LLM", side_effect=fake_llm):
            response = self._mutate("post", f"/cases/{self.case_id}/brief", json={"firm_authorized": True, "client_authorized": True})
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertTrue(result["generated"])
        self.assertEqual(result["answer"], "تتضمن القضية ملاحظة عن صحيفة الدعوى [2].")
        self.assertIn("JSON lines", captured["prompt"])
        self.assertIn("case_note", captured["prompt"])
        self.assertIn("hearing_session", captured["prompt"])
        self.assertNotIn("deadline-b@example.test", captured["prompt"])

    def test_case_brief_minimizes_case_identifiers_and_redacts_common_pii(self):
        sensitive_note = (
            "بيانات اختبار: رقم قومي 29001011234567، هاتف 01012345678، "
            "هاتف دولي +201012345678، بريد private.client@example.test"
        )
        self._mutate("post", f"/cases/{self.case_id}/notes", json={"text": sensitive_note})
        captured = {}
        def fake_llm(prompt):
            captured["prompt"] = prompt
            return "تتضمن الملاحظة عبارة بيانات اختبار [2]."
        with patch.dict("os.environ", {"LLM_FIRM_DATA_PROCESSING_APPROVED": "1"}), patch.object(
            app, "LLM", side_effect=fake_llm
        ):
            response = self._mutate("post", f"/cases/{self.case_id}/brief", json={"firm_authorized": True, "client_authorized": True})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["generated"])
        prompt = captured["prompt"]
        for raw_identifier in (
            "Synthetic deadline matter",
            "Synthetic client",
            "29001011234567",
            "01012345678",
            "+201012345678",
            "private.client@example.test",
        ):
            self.assertNotIn(raw_identifier, prompt)
        self.assertIn("رقم قومي محجوب", prompt)
        self.assertIn("رقم هاتف محجوب", prompt)
        self.assertIn("بريد إلكتروني محجوب", prompt)
        self.assertIn("not complete anonymization", prompt)

    def test_case_brief_requires_explicit_firm_and_client_authorization(self):
        payloads = (
            {},
            {"firm_authorized": True, "client_authorized": False},
            {"firm_authorized": False, "client_authorized": True},
        )
        for payload in payloads:
            with self.subTest(payload=payload), patch.dict(
                "os.environ", {"LLM_FIRM_DATA_PROCESSING_APPROVED": "1"}
            ), patch.object(app, "LLM") as llm:
                response = self._mutate(
                    "post", f"/cases/{self.case_id}/brief", json=payload
                )
            self.assertEqual(response.status_code, 403, response.text)
            llm.assert_not_called()

    def test_case_brief_does_not_call_model_without_firm_data_approval(self):
        with patch.dict("os.environ", {"LLM_FIRM_DATA_PROCESSING_APPROVED": ""}), patch.object(app, "LLM") as llm:
            response = self._mutate("post", f"/cases/{self.case_id}/brief", json={"firm_authorized": True, "client_authorized": True})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertFalse(response.json()["available"])
        self.assertTrue(response.json()["abstained"])
        llm.assert_not_called()

    def test_case_brief_still_requires_general_llm_approval(self):
        settings = {
            "LLM_URL": "https://llm.example.test/v1/chat/completions",
            "LLM_KEY": "synthetic-test-key",
            "LLM_DATA_PROCESSING_APPROVED": "",
            "LLM_FIRM_DATA_PROCESSING_APPROVED": "1",
        }
        with patch.dict("os.environ", settings), patch.object(app, "_llm_open") as open_llm:
            response = self._mutate("post", f"/cases/{self.case_id}/brief", json={"firm_authorized": True, "client_authorized": True})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertFalse(response.json()["generated"])
        self.assertTrue(response.json()["abstained"])
        open_llm.assert_not_called()

    def test_case_brief_rejects_uncited_or_unanchored_model_output(self):
        with patch.dict("os.environ", {"LLM_FIRM_DATA_PROCESSING_APPROVED": "1"}), patch.object(
            app, "LLM", return_value="The case will definitely succeed."
        ):
            response = self._mutate("post", f"/cases/{self.case_id}/brief", json={"firm_authorized": True, "client_authorized": True})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertFalse(response.json()["generated"])
        self.assertTrue(response.json()["abstained"])
        self.assertNotIn("answer", response.json())

    def test_other_firm_cannot_generate_a_case_brief(self):
        self.client.cookies.clear()
        login = self.client.post(
            "/login", json={"email": "deadline-b@example.test", "password": self.password_b}
        )
        self.assertEqual(login.status_code, 200, login.text)
        denied = self._mutate("post", f"/cases/{self.case_id}/brief", json={"firm_authorized": True, "client_authorized": True})
        self.assertEqual(denied.status_code, 404, denied.text)

    def test_unknown_rule_and_impossible_trigger_are_rejected(self):
        unknown = self.client.get(
            f"/cases/{self.case_id}/deadline-estimate",
            params={"rule_id": "unknown-rule", "trigger": "2026-10-26"},
        )
        self.assertEqual(unknown.status_code, 404, unknown.text)
        invalid_date = self.client.get(
            f"/cases/{self.case_id}/deadline-estimate",
            params={"rule_id": "civil_cassation_60d", "trigger": "2026-02-30"},
        )
        self.assertEqual(invalid_date.status_code, 422, invalid_date.text)

    def test_other_firm_cannot_estimate_a_case_deadline(self):
        self.client.cookies.clear()
        login = self.client.post(
            "/login", json={"email": "deadline-b@example.test", "password": self.password_b}
        )
        self.assertEqual(login.status_code, 200, login.text)
        denied = self.client.get(
            f"/cases/{self.case_id}/deadline-estimate",
            params={"rule_id": "civil_cassation_60d", "trigger": "2026-10-26"},
        )
        self.assertEqual(denied.status_code, 404, denied.text)


if __name__ == "__main__":
    unittest.main()
