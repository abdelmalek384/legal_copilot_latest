import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class SeparateDatabaseApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env_names = ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB")
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ["COPILOT_CONTROL_DB"] = str(self.root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(self.root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(self.root / "corpus.sqlite3")
        app._database_runtime = None

        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Firm B")
        self.password = "LongUniqueTestPassphrase-2026!"
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_a, "First Owner", "owner@example.test", app.hash_pw(self.password)
        )
        self.runtime.create_firm_membership(self.user_id, self.firm_b, "lawyer")
        self.client = TestClient(app.app)

    def tearDown(self):
        self.client.close()
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        for name, value in self.old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        self.temp.cleanup()

    def _mutate(self, method, url, **kwargs):
        csrf = self.client.cookies.get("lc_csrf")
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = csrf or ""
        return getattr(self.client, method)(url, headers=headers, **kwargs)

    def test_nonmember_cannot_switch_firms_and_revoked_membership_blocks_cached_session(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

        unassigned_firm, _ = self.runtime.provision_firm("Unassigned Firm")
        denied = self._mutate(
            "post", "/session/firm", json={"firm_id": unassigned_firm}
        )
        self.assertEqual(denied.status_code, 403, denied.text)

        switched = self._mutate(
            "post", "/session/firm", json={"firm_id": self.firm_b}
        )
        self.assertEqual(switched.status_code, 200, switched.text)
        # Prime the tenant connection cache before revoking membership.
        self.assertEqual(self.client.get("/cases").status_code, 200)

        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='revoked', updated_at=datetime('now') "
            "WHERE user_id=? AND firm_id=?",
            (self.user_id, self.firm_b),
        )
        control.commit()

        # Every request must revalidate membership, even with a cached firm DB
        # connection and a still-valid authentication session cookie.
        denied_after_revocation = self.client.get("/cases")
        self.assertEqual(denied_after_revocation.status_code, 403,
                         denied_after_revocation.text)
        self.assertEqual(
            self.runtime.firm_connection(
                self.runtime.resolve_context(self.user_id, self.firm_a)
            ).execute("SELECT COUNT(*) FROM cases").fetchone()[0],
            0,
        )

    def test_login_firm_switch_and_shared_corpus_are_separated(self):
        login = self.client.post(
            "/login", json={"email": "OWNER@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)
        self.assertEqual(len(login.json()["firms"]), 2)
        self.assertEqual(login.json()["firm_id"], self.firm_a)

        created = self._mutate("post", "/cases", json={"title": "Firm A matter"})
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        uploaded = self._mutate(
            "post",
            f"/cases/{case_id}/docs",
            json={"name": "private.txt", "text": "firmonlysentinel confidential matter passage"},
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        matter_search = self._mutate(
            "post",
            "/search",
            json={"q": "firmonlysentinel", "case_id": case_id, "scope": "firm_documents"},
        )
        self.assertEqual(matter_search.status_code, 200, matter_search.text)
        self.assertTrue(any("firmonlysentinel" in hit["text"] for hit in matter_search.json()))

        # The legal corpus is central and shared; matter content is not.
        corpus = self.runtime.legal_corpus_connection()
        corpus.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page,collection_permission,"
            "commercial_reuse_permission,permission_evidence) VALUES(?,?,?,?,?,?)",
            ("test-source", "Test authority", "https://example.test/law", "allowed", "allowed", "test evidence"),
        )
        corpus.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type,practice_area) "
            "VALUES(?,?,?,?,?)",
            ("test-law", "test-source", "Test Law", "statute", "general"),
        )
        version_id = corpus.execute(
            "INSERT INTO legal_document_versions(document_id,version_label,source_url,effective_date,"
            "legal_status,review_status,authenticity_verified,status_verified,amendment_history_verified,"
            "permission_evidence) VALUES(?,?,?,?,?,?,?,?,?,?)",
            ("test-law", "current", "https://example.test/law/current", "2020-01-01",
             "in_force", "verified", 1, 1, 1, "version evidence"),
        ).lastrowid
        corpus.execute(
            "INSERT INTO chunks(ref,article,page,text,norm,document_version_id,in_force,as_of,source,verified) "
            "VALUES(?,?,?,?,?,?,?,?,?,1)",
            ("Test Law Article 1", "1", "1", "corpusonlysentinel statutory rule",
             "corpusonlysentinel statutory rule", version_id, 1, "2020-01-01", "test-source"),
        )
        corpus.commit()

        # A firm admin is not a platform legal reviewer.
        self.assertEqual(self.client.get("/legal-review/queue").status_code, 403)

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        self.assertEqual(switched.json()["firm_id"], self.firm_b)
        self.assertEqual(self.client.get("/cases").json(), [])
        guessed_case = self._mutate(
            "post",
            "/search",
            json={"q": "firmonlysentinel", "case_id": case_id, "scope": "firm_documents"},
        )
        self.assertEqual(guessed_case.status_code, 404)

        shared_search = self._mutate(
            "post", "/search", json={"q": "corpusonlysentinel", "scope": "verified_corpus"}
        )
        self.assertEqual(shared_search.status_code, 200, shared_search.text)
        self.assertTrue(any("corpusonlysentinel" in hit["text"] for hit in shared_search.json()))

        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_reviewer')",
            (self.user_id,),
        )
        control.commit()
        reviewer_queue = self.client.get("/legal-review/queue")
        self.assertEqual(reviewer_queue.status_code, 200, reviewer_queue.text)


if __name__ == "__main__":
    unittest.main()
