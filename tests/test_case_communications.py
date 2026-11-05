"""Firm-isolated case communication history route tests."""
import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
import app
from database_runtime import DatabaseRuntime


class CaseCommunicationRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-communications-")
        root = Path(self.temp.name)
        names = ("COPILOT_DB","COPILOT_CONTROL_DB","COPILOT_TENANT_DB_ROOT","COPILOT_CORPUS_DB",
                 "COPILOT_OBJECT_STORAGE_ROOT","COPILOT_OBJECT_STORAGE_BACKEND","COPILOT_ENV","ADMIN_TOKEN")
        self.old_env = {name: os.environ.get(name) for name in names}
        os.environ.pop("COPILOT_DB", None)
        os.environ.update(COPILOT_CONTROL_DB=str(root/"control.sqlite3"),
            COPILOT_TENANT_DB_ROOT=str(root/"tenants"), COPILOT_CORPUS_DB=str(root/"corpus.sqlite3"),
            COPILOT_OBJECT_STORAGE_ROOT=str(root/"objects"), COPILOT_OBJECT_STORAGE_BACKEND="local",
            COPILOT_ENV="development", ADMIN_TOKEN="communications-test-admin-token-long")
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Communications Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Communications Firm B")
        self.password_a = "Communications-password-A-2026!"
        self.password_b = "Communications-password-B-2026!"
        self.owner_a_id = self.runtime.create_initial_firm_owner(
            self.firm_a, "Owner A", "comm-a@example.test", app.hash_pw(self.password_a)
        )
        self.runtime.create_initial_firm_owner(
            self.firm_b, "Owner B", "comm-b@example.test", app.hash_pw(self.password_b)
        )
        self.client = TestClient(app.app)
        self._login("comm-a@example.test",self.password_a)
        created = self._mutate("post","/cases",json={"title":"Synthetic communications matter","client":"Synthetic client"})
        self.assertEqual(created.status_code,200,created.text)
        self.case_id = created.json()["id"]

    def tearDown(self):
        self.client.close()
        try: self.runtime.close_current_thread()
        except Exception: pass
        app._database_runtime = None
        for name,value in self.old_env.items():
            if value is None: os.environ.pop(name,None)
            else: os.environ[name]=value
        self.temp.cleanup()

    def _login(self,email,password):
        response=self.client.post("/login",json={"email":email,"password":password})
        self.assertEqual(response.status_code,200,response.text)

    def _mutate(self,method,url,**kwargs):
        headers=dict(kwargs.pop("headers",{}) or {})
        headers["X-CSRF-Token"]=self.client.cookies.get("lc_csrf","")
        return getattr(self.client,method)(url,headers=headers,**kwargs)

    def test_create_list_and_tenant_isolation(self):
        payload={"channel":"email","subject":"Contract update","summary":"Sent revised draft to client.",
                 "occurred_at":"2026-11-03T10:30:00+02:00"}
        created=self._mutate("post",f"/cases/{self.case_id}/communications",json=payload)
        self.assertEqual(created.status_code,200,created.text)
        listed=self.client.get(f"/cases/{self.case_id}/communications")
        self.assertEqual(listed.status_code,200,listed.text)
        self.assertEqual(listed.json()[0]["subject"],"Contract update")
        self.assertEqual(listed.json()[0]["occurred_at"],"2026-11-03T08:30:00+00:00")
        self.assertEqual(listed.json()[0]["summary"],"Sent revised draft to client.")
        self._login("comm-b@example.test",self.password_b)
        denied=self.client.get(f"/cases/{self.case_id}/communications")
        denied_write=self._mutate("post",f"/cases/{self.case_id}/communications",json=payload)
        self.assertEqual(denied.status_code,404)
        self.assertEqual(denied_write.status_code,404)
        owner_context=self.runtime.resolve_context(self.owner_a_id,self.firm_a)
        owner_db=self.runtime.firm_connection(owner_context)
        self.assertEqual(
            owner_db.execute(
                "SELECT COUNT(*) FROM case_communications WHERE case_id=?",
                (self.case_id,),
            ).fetchone()[0],
            1,
        )

    def test_same_firm_nonmember_cannot_read_or_write_case_communications(self):
        password = "Communications-nonmember-password-2026!"
        user_id = self.runtime.create_global_identity(
            "Same Firm Nonmember", "comm-nonmember@example.test", app.hash_pw(password)
        )
        self.runtime.create_firm_membership(
            user_id, self.firm_a, "lawyer", created_by_user_id=self.owner_a_id
        )
        nonmember = TestClient(app.app)
        try:
            login = nonmember.post(
                "/login", json={"email": "comm-nonmember@example.test", "password": password}
            )
            self.assertEqual(login.status_code, 200, login.text)
            headers = {"X-CSRF-Token": nonmember.cookies.get("lc_csrf", "")}
            before = self.runtime.firm_connection(
                self.runtime.resolve_context(self.owner_a_id, self.firm_a)
            ).execute(
                "SELECT COUNT(*) FROM case_communications WHERE case_id=?",
                (self.case_id,),
            ).fetchone()[0]
            read = nonmember.get(f"/cases/{self.case_id}/communications")
            write = nonmember.post(
                f"/cases/{self.case_id}/communications",
                headers=headers,
                json={
                    "channel": "call",
                    "subject": "Unauthorized",
                    "summary": "Must not be recorded",
                },
            )
            self.assertEqual(read.status_code, 404, read.text)
            self.assertEqual(write.status_code, 404, write.text)
            after = self.runtime.firm_connection(
                self.runtime.resolve_context(self.owner_a_id, self.firm_a)
            ).execute(
                "SELECT COUNT(*) FROM case_communications WHERE case_id=?",
                (self.case_id,),
            ).fetchone()[0]
            self.assertEqual(after, before)
        finally:
            nonmember.close()

    def test_reject_invalid_channel_and_timezone_less_timestamp(self):
        for payload in (
            {"channel":"whatsapp","subject":"Call","summary":"Summary"},
            {"channel":"call","subject":"Call","summary":"Summary","occurred_at":"2026-11-03T10:30:00"},
            {"channel":"call","subject":"   ","summary":"Summary"},
            {"channel":"call","subject":"Call","summary":"   "},
        ):
            response=self._mutate("post",f"/cases/{self.case_id}/communications",json=payload)
            self.assertEqual(response.status_code,422,response.text)


if __name__ == "__main__":
    unittest.main()
