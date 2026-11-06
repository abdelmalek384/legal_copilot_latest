"""Persistent client profile, multi-matter, and case-team visibility tests."""
import sqlite3
import unittest
from pathlib import Path

from tests.invoice_test_support import InvoiceTestSupport


class ClientProfileTests(InvoiceTestSupport, unittest.TestCase):
    def test_multiple_matters_share_one_profile_and_visibility_follows_case_membership(self):
        first = self.mutate(
            self.client_a, "post", "/cases",
            json={"title": "Second Client Snapshot matter", "client": "Client Snapshot"},
        )
        second = self.mutate(
            self.client_a, "post", "/cases",
            json={"title": "Third Client Snapshot matter", "client": " client snapshot "},
        )
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        first_case = self.client_a.get(f"/cases/{first.json()['id']}")
        second_case = self.client_a.get(f"/cases/{second.json()['id']}")
        self.assertEqual(first_case.json()["client_id"], second_case.json()["client_id"])

        profiles = self.client_a.get("/clients").json()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["name"], "Client Snapshot")
        self.assertEqual(len(profiles[0]["matters"]), 3)
        self.assertEqual(
            {matter["id"] for matter in profiles[0]["matters"]},
            {self.case_id, first.json()["id"], second.json()["id"]},
        )
        self.assertEqual(self.client_b.get("/clients").json(), [])
        self.assertEqual(self.client_nonmember.get("/clients").json(), [])
        guessed_link = self.mutate(
            self.client_nonmember, "post", "/cases",
            json={"title": "Guessed profile matter", "client": "Client Snapshot"},
        )
        self.assertEqual(guessed_link.status_code, 409)
        self.assertEqual(
            self.client_nonmember.get(f"/clients/{profiles[0]['id']}").status_code,
            404,
        )

    def test_admin_can_create_update_and_link_client_profile(self):
        created = self.mutate(
            self.client_a, "post", "/clients",
            json={
                "name": "شركة النيل للتجارة", "phone": "+20 100 111 2222",
                "email": "client@example.test", "address": "Cairo",
                "notes": "Synthetic client profile",
            },
        )
        self.assertEqual(created.status_code, 200, created.text)
        profile = created.json()
        self.assertEqual(profile["matters"], [])
        self.assertEqual(profile["phone"], "+20 100 111 2222")

        duplicate = self.mutate(
            self.client_a, "post", "/clients",
            json={"name": " شركة النيل للتجارة "},
        )
        self.assertEqual(duplicate.status_code, 409)

        first_matter = self.mutate(
            self.client_a, "post", "/cases",
            json={"title": "First Nile matter", "client_id": profile["id"]},
        )
        self.assertEqual(first_matter.status_code, 200, first_matter.text)

        hidden = self.client_nonmember.get(f"/clients/{profile['id']}")
        self.assertEqual(hidden.status_code, 404)
        forbidden_link = self.mutate(
            self.client_nonmember, "post", "/cases",
            json={"title": "Unauthorized client matter", "client_id": profile["id"]},
        )
        self.assertEqual(forbidden_link.status_code, 404)

        updated = self.mutate(
            self.client_a, "put", f"/clients/{profile['id']}",
            json={
                "name": "شركة النيل للتجارة", "phone": "+20 100 333 4444",
                "email": "client@example.test", "address": "Cairo",
                "notes": "Updated synthetic profile",
            },
        )
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual(updated.json()["phone"], "+20 100 333 4444")
        owner_id = self.runtime.control_connection().execute(
            "SELECT id FROM users WHERE email_normalized=?", ("invoice-owner-a@example.test",)
        ).fetchone()["id"]
        context = self.runtime.resolve_context(owner_id, self.firm_a)
        tenant = self.runtime.firm_connection(context)
        audit_events = [row["event"] for row in tenant.execute(
            "SELECT event FROM security_audit_events ORDER BY id"
        )]
        self.assertTrue(any(event.startswith("client_profile_created:") for event in audit_events))
        self.assertTrue(any(event.startswith("client_profile_updated:") for event in audit_events))
        self.assertNotIn("شركة النيل للتجارة", " ".join(audit_events))

        denied = self.mutate(
            self.client_nonmember, "post", "/clients",
            json={"name": "Unauthorized profile"},
        )
        self.assertEqual(denied.status_code, 403)
        hidden_update = self.mutate(
            self.client_nonmember, "put", f"/clients/{profile['id']}",
            json={"name":"شركة النيل للتجارة","phone":"","email":"","address":"","notes":""},
        )
        self.assertEqual(hidden_update.status_code, 404)

        matter = self.mutate(
            self.client_a, "post", "/cases",
            json={"title": "Nile client matter", "client_id": profile["id"]},
        )
        self.assertEqual(matter.status_code, 200, matter.text)
        case = self.client_a.get(f"/cases/{matter.json()['id']}")
        self.assertEqual(case.status_code, 200, case.text)
        self.assertEqual(case.json()["client"], "شركة النيل للتجارة")
        self.assertEqual(case.json()["client_id"], profile["id"])
        first_case = self.client_a.get(f"/cases/{first_matter.json()['id']}")
        self.assertEqual(first_case.status_code, 200, first_case.text)
        self.assertEqual(first_case.json()["client"], "شركة النيل للتجارة")

    def test_migration_backfills_existing_case_names_once(self):
        root = Path(__file__).resolve().parents[1] / "migrations" / "firm"
        migration = (root / "0019_client_profiles.sql").read_text(encoding="utf-8")
        db = sqlite3.connect(":memory:")
        db.execute(
            "CREATE TABLE cases(id INTEGER PRIMARY KEY,title TEXT,client TEXT,created_by INTEGER,created_at TEXT)"
        )
        db.executemany(
            "INSERT INTO cases(id,title,client,created_by,created_at) VALUES(?,?,?,?,?)",
            [
                (1, "Matter A", "Client Snapshot", 7, "2026-01-01 00:00:00"),
                (2, "Matter B", " client snapshot ", 8, "2026-02-01 00:00:00"),
                (3, "Matter C", "", 9, "2026-03-01 00:00:00"),
            ],
        )
        db.executescript(migration)
        profiles = db.execute("SELECT id,name,normalized_name FROM clients").fetchall()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0][1], "Client Snapshot")
        self.assertEqual(profiles[0][2], "client snapshot")
        links = db.execute("SELECT id,client_id FROM cases ORDER BY id").fetchall()
        self.assertEqual(links[0][1], profiles[0][0])
        self.assertEqual(links[1][1], profiles[0][0])
        self.assertIsNone(links[2][1])
        db.close()


    def test_invalid_client_names_return_422_on_every_write_path(self):
        invalid_names = ("A", "   ", "X" * 201)
        tenant = self.runtime.firm_connection(
            self.runtime.resolve_context(
                self.runtime.control_connection().execute(
                    "SELECT id FROM users WHERE email_normalized=?",
                    ("invoice-owner-a@example.test",),
                ).fetchone()["id"],
                self.firm_a,
            )
        )
        before = tenant.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        profile = self.mutate(
            self.client_a, "post", "/clients",
            json={"name": "Validation target"},
        )
        self.assertEqual(profile.status_code, 200, profile.text)
        profile_id = profile.json()["id"]
        before += 1

        for name in invalid_names:
            with self.subTest(path="case creation", name_length=len(name)):
                response = self.mutate(
                    self.client_a, "post", "/cases",
                    json={"title": "Invalid client name matter", "client": name},
                )
                self.assertEqual(response.status_code, 422, response.text)
                self.assertIn("اسم العميل", response.text)
                self.assertNotEqual(response.status_code, 503)

            with self.subTest(path="client creation", name_length=len(name)):
                response = self.mutate(
                    self.client_a, "post", "/clients", json={"name": name},
                )
                self.assertEqual(response.status_code, 422, response.text)

            with self.subTest(path="client update", name_length=len(name)):
                response = self.mutate(
                    self.client_a, "put", f"/clients/{profile_id}",
                    json={"name": name},
                )
                self.assertEqual(response.status_code, 422, response.text)

            with self.subTest(path="client CSV import", name_length=len(name)):
                response = self.mutate(
                    self.client_a, "post", "/clients/import.csv",
                    json={"csv": "name" + chr(10) + name + chr(10)},
                )
                self.assertEqual(response.status_code, 422, response.text)

            with self.subTest(path="case CSV import", name_length=len(name)):
                response = self.mutate(
                    self.client_a, "post", "/cases/import.csv",
                    json={"csv": "title,client" + chr(10) + "Invalid matter," + name + chr(10)},
                )
                self.assertEqual(response.status_code, 422, response.text)

        self.assertEqual(tenant.execute("SELECT COUNT(*) FROM clients").fetchone()[0], before)


if __name__ == "__main__":
    unittest.main()
