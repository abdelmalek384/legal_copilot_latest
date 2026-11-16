import importlib
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.register_labour_law_candidate import load_candidate_record  # noqa: E402


class LabourLawCandidateRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_env = {
            name: os.environ.get(name)
            for name in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB", "COPILOT_DB", "COPILOT_ENV")
        }
        os.environ["COPILOT_CONTROL_DB"] = str(Path(self.tmp.name) / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(Path(self.tmp.name) / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(Path(self.tmp.name) / "corpus.sqlite3")
        os.environ["COPILOT_ENV"] = "test"
        os.environ.pop("COPILOT_DB", None)
        import app
        self.app = importlib.reload(app)
        self.runtime = self.app.DatabaseRuntime.from_env()
        self.runtime.initialize()
        from tools.register_labour_law_candidate import register, DEFAULT_RECORD, load_candidate_record
        self.register = register
        self.record = json.loads(DEFAULT_RECORD.read_text(encoding="utf-8"))
        self.db = self.runtime.legal_corpus_connection()

    def tearDown(self):
        try:
            self.runtime.close_current_thread()
        finally:
            self.app._database_runtime = None
            for name, value in self.old_env.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            self.tmp.cleanup()

    def test_candidate_record_loader_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "candidate.json"
            for raw in (
                '{"document":{"document_id":"LAW-1"},"document":{"document_id":"LAW-2"}}',
                '{"document":{"document_id":"LAW-1","nested":{"review":"pending","review":"approved"}}}',
            ):
                path.write_text(raw, encoding="utf-8")
                with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "unreadable, ambiguous, or unsafe"):
                    load_candidate_record(path)

    def test_candidate_record_loader_rejects_non_object_and_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "candidate.json"
            path.write_text('[]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "root must be a JSON object"):
                load_candidate_record(path)
            target = root / "target.json"
            target.write_text('{"document":{}}', encoding="utf-8")
            path.unlink()
            try:
                path.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {type(exc).__name__}")
            with self.assertRaisesRegex(ValueError, "unreadable, ambiguous, or unsafe"):
                load_candidate_record(path)

    def test_registers_pending_metadata_without_chunks(self):
        result = self.register(self.db, self.record)
        self.assertEqual(result["version_state"]["legal_status"], "under_review")
        self.assertEqual(result["version_state"]["review_status"], "pending_source_review")
        self.assertEqual(result["version_state"]["authenticity_verified"], 0)
        self.assertEqual(result["version_state"]["status_verified"], 0)
        self.assertEqual(result["version_state"]["amendment_history_verified"], 0)
        self.assertEqual(result["linked_chunk_count"], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_review_events").fetchone()[0], 6)

    def test_registration_does_not_recreate_pending_event_after_review_decision(self):
        first = self.register(self.db, self.record)
        event = self.db.execute(
            """SELECT review_type FROM legal_review_events
               WHERE version_id=? LIMIT 1""",
            (first["version_id"],),
        ).fetchone()
        self.assertIsNotNone(event)
        review_type = event["review_type"]
        self.db.execute(
            """UPDATE legal_review_events SET outcome='pass', reviewer='egyptian-counsel',
               notes='Human review decision' WHERE version_id=? AND review_type=?""",
            (first["version_id"], review_type),
        )
        self.db.commit()
        self.register(self.db, self.record)
        rows = self.db.execute(
            """SELECT outcome,reviewer,notes FROM legal_review_events
               WHERE version_id=? AND review_type=?""",
            (first["version_id"], review_type),
        ).fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(tuple(rows[0]), ("pass", "egyptian-counsel", "Human review decision"))

    def test_registration_commits_candidate_for_independent_connection(self):
        self.register(self.db, self.record)
        observer = sqlite3.connect(os.environ["COPILOT_CORPUS_DB"])
        try:
            row = observer.execute(
                "SELECT document_id FROM legal_documents WHERE document_id=?",
                (self.record["document"]["document_id"],),
            ).fetchone()
            self.assertEqual(row[0], self.record["document"]["document_id"])
        finally:
            observer.close()

    def test_registration_rolls_back_earlier_sources_on_later_source_conflict(self):
        candidate = dict(self.record)
        candidate["sources"] = [dict(item) for item in self.record["sources"]]
        first = dict(candidate["sources"][0])
        second = dict(first)
        second.update({
            "source_id": "EG-SECOND-SOURCE",
            "authority": "Second source",
            "source_page": "https://second.example.gov/law",
        })
        candidate["sources"].append(second)
        self.db.execute(
            """INSERT INTO legal_sources
               (source_id,authority,source_page,access_status,collection_permission,
                commercial_reuse_permission,terms_url,terms_checked_on,permission_evidence)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            ("EG-SECOND-SOURCE", "Conflicting authority", second["source_page"],
             "unknown", "unknown", "unknown", None, None, "pre-existing record"),
        )
        self.db.commit()
        with self.assertRaisesRegex(ValueError, "Existing source metadata conflicts"):
            self.register(self.db, candidate)
        self.assertIsNone(self.db.execute(
            "SELECT 1 FROM legal_sources WHERE source_id=?",
            (first["source_id"],),
        ).fetchone())
        self.assertIsNone(self.db.execute(
            "SELECT 1 FROM legal_documents WHERE document_id=?",
            (candidate["document"]["document_id"],),
        ).fetchone())

    def test_registration_preflights_all_candidate_shapes_before_writing(self):
        malformed = []
        non_object_source = dict(self.record)
        non_object_source["sources"] = ["not-an-object"]
        malformed.append((non_object_source, "source entries must be objects"))
        missing_permission = dict(self.record)
        missing_permission["sources"] = [dict(item) for item in self.record["sources"]]
        missing_permission["sources"][0].pop("collection_permission")
        malformed.append((missing_permission, "source collection_permission must be a non-empty string"))
        missing_source_authority = dict(self.record)
        missing_source_authority["sources"] = [dict(item) for item in self.record["sources"]]
        missing_source_authority["sources"][0].pop("authority")
        malformed.append((missing_source_authority, "source authority must be a non-empty string"))
        missing_document = dict(self.record)
        missing_document["document"] = None
        malformed.append((missing_document, "document must be an object"))
        missing_version_date = dict(self.record)
        missing_version_date["version"] = dict(self.record["version"])
        missing_version_date["version"]["publication_date"] = "2025-13-40"
        malformed.append((missing_version_date, "publication_date must be an ISO"))
        unhashable_review_type = dict(self.record)
        unhashable_review_type["reviews"] = [dict(item) for item in self.record["reviews"]]
        unhashable_review_type["reviews"][0]["review_type"] = ["lawyer_approval"]
        malformed.append((unhashable_review_type, "review_type values must be unique"))
        duplicate_review = dict(self.record)
        duplicate_review["reviews"] = [dict(item) for item in self.record["reviews"]]
        duplicate_review["reviews"].append(dict(duplicate_review["reviews"][0]))
        malformed.append((duplicate_review, "review_type values must be unique"))
        for candidate, expected in malformed:
            with self.subTest(expected=expected), self.assertRaisesRegex(ValueError, expected):
                self.register(self.db, candidate)
            self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_sources").fetchone()[0], 0)
            self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_documents").fetchone()[0], 0)
            self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_document_versions").fetchone()[0], 0)

    def test_registration_rejects_unsafe_candidate_evidence_urls(self):
        cases = (
            ("source_page", "https://user:secret@example.gov/law.pdf", "source_page"),
            ("source_page", "https://example.gov/law.pdf?access_token=secret", "source_page"),
            ("source_page", "https://example.gov/law.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256", "source_page"),
            ("source_page", "https://example.gov/law.pdf?GoogleAccessId=account", "source_page"),
            ("version_source_url", "https://example.gov/law.pdf#fragment", "source_url"),
            ("version_source_url_host", "https://other.gov/law.pdf", "host must match"),
            ("review_evidence_url", "https://example.gov/review.pdf\x7f", "evidence_url"),
        )
        for field, value, expected in cases:
            candidate = dict(self.record)
            candidate["sources"] = [dict(item) for item in self.record["sources"]]
            candidate["version"] = dict(self.record["version"])
            candidate["reviews"] = [dict(item) for item in self.record.get("reviews", [])]
            if field == "source_page":
                candidate["sources"][0]["source_page"] = value
            elif field in ("version_source_url", "version_source_url_host"):
                candidate["version"]["source_url"] = value
            else:
                candidate["reviews"][0]["evidence_url"] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, expected):
                self.register(self.db, candidate)
            self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_sources").fetchone()[0], 0)

    def test_registration_cannot_grant_source_collection_or_commercial_reuse(self):
        for field, value, message in (
            ("collection_permission", "allowed", "cannot grant collection permission"),
            ("commercial_reuse_permission", "allowed_limited", "cannot grant commercial reuse permission"),
            ("collection_permission", ["allowed"], "must be a non-empty string"),
        ):
            candidate = dict(self.record)
            candidate["sources"] = [dict(item) for item in self.record["sources"]]
            candidate["sources"][-1][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, message):
                self.register(self.db, candidate)
            self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_sources").fetchone()[0], 0)
            self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_documents").fetchone()[0], 0)

    def test_registration_ignores_candidate_supplied_verification_and_status_claims(self):
        candidate = dict(self.record)
        candidate["version"] = dict(self.record["version"])
        candidate["version"].update({
            "legal_status": "in_force",
            "review_status": "verified",
            "authenticity_verified": 1,
            "status_verified": 1,
            "amendment_history_verified": 1,
        })
        result = self.register(self.db, candidate)
        state = result["version_state"]
        self.assertEqual(state["legal_status"], "under_review")
        self.assertEqual(state["review_status"], "pending_source_review")
        self.assertEqual(state["authenticity_verified"], 0)
        self.assertEqual(state["status_verified"], 0)
        self.assertEqual(state["amendment_history_verified"], 0)
        self.assertEqual(result["linked_chunk_count"], 0)

    def test_registration_is_idempotent_and_preserves_review_decisions(self):
        first = self.register(self.db, self.record)
        self.register(self.db, self.record)
        self.db.execute(
            "UPDATE legal_document_versions SET review_status='pending_lawyer_review' WHERE version_id=?",
            (first["version_id"],),
        )
        self.db.execute(
            "UPDATE legal_sources SET collection_permission='not_allowed_without_explicit_exception_or_license' WHERE source_id=?",
            (self.record["sources"][0]["source_id"],),
        )
        self.db.commit()
        self.register(self.db, self.record)
        row = self.db.execute(
            "SELECT review_status FROM legal_document_versions WHERE version_id=?",
            (first["version_id"],),
        ).fetchone()
        self.assertEqual(row[0], "pending_lawyer_review")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_document_versions").fetchone()[0], 1)
        permission = self.db.execute(
            "SELECT collection_permission FROM legal_sources WHERE source_id=?",
            (self.record["sources"][0]["source_id"],),
        ).fetchone()[0]
        self.assertEqual(permission, "not_allowed_without_explicit_exception_or_license")


if __name__ == "__main__":
    unittest.main()
