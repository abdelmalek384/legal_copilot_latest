import json
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import sys
from pathlib import Path

# Running `python tests/test_legal_versioned_registry.py` sets sys.path[0] to tests/.
# Explicitly add the repository root so the application module is importable in CI.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

class LegalVersionedRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_ENV",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        root = Path(self.tmp.name)
        os.environ.pop("COPILOT_DB", None)
        os.environ["COPILOT_ENV"] = "development"
        os.environ["COPILOT_CONTROL_DB"] = str(root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(root / "corpus.sqlite3")
        import importlib
        import app
        self.app = importlib.reload(app)
        self.runtime = self.app.get_database_runtime()
        self.runtime.initialize()
        self.db = self.app.corpus_conn()

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

    def test_corpus_profile_exposes_versioned_legal_registry_schema(self):
        tables = {r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for name in ("legal_sources", "legal_documents", "legal_document_versions", "legal_version_relations", "legal_review_events"):
            self.assertIn(name, tables)
        cols = {r[1] for r in self.db.execute("PRAGMA table_info(chunks)")}
        self.assertIn("document_version_id", cols)

    def test_unknown_is_default_and_verified_requires_explicit_update(self):
        self.db.execute(
            "INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
            ("S1", "Example Authority", "https://example.gov")
        )
        self.db.execute(
            "INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
            ("D1", "S1", "عنوان تجريبي", "legislation")
        )
        cur = self.db.execute(
            "INSERT INTO legal_document_versions(document_id,version_label,source_url) VALUES(?,?,?)",
            ("D1", "original", "https://example.gov/law.pdf")
        )
        row = self.db.execute("SELECT legal_status,review_status,authenticity_verified,status_verified FROM legal_document_versions WHERE version_id=?", (cur.lastrowid,)).fetchone()
        self.assertEqual(tuple(row), ("unknown", "pending_source_review", 0, 0))

    def test_invalid_status_and_relation_types_are_rejected(self):
        self.db.execute("INSERT INTO legal_sources(source_id,authority,source_page) VALUES('S1','Example','https://example.gov')")
        self.db.execute("INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES('D1','S1','Test','law')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url,legal_status) VALUES('D1','bad','https://example.gov/bad.pdf','probably_current')")
        self.db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url) VALUES('D1','v1','https://example.gov/v1.pdf')")
        self.db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url) VALUES('D1','v2','https://example.gov/v2.pdf')")
        ids = [x[0] for x in self.db.execute("SELECT version_id FROM legal_document_versions ORDER BY version_id")]
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO legal_version_relations(from_version_id,to_version_id,relation_type) VALUES(?,?,?)", (ids[0], ids[1], "magic"))


    def _make_linked_chunk(self, version_label, effective_date, repeal_date=None, review_status="verified", legal_status="in_force", authenticity_verified=1, status_verified=1, amendment_history_verified=1, text="versionprobe legal text", chunk_in_force=1):
        self.db.execute("INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
                        ("S_" + version_label, "Example Authority", "https://example.gov"))
        self.db.execute(
            "UPDATE legal_sources SET collection_permission='allowed',commercial_reuse_permission='allowed',permission_evidence=? WHERE source_id=?",
            ("https://example.gov/terms#commercial-reuse", "S_" + version_label)
        )
        self.db.execute("INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
                        ("D_" + version_label, "S_" + version_label, "Test law", "legislation"))
        cur = self.db.execute(
            "INSERT INTO legal_document_versions(document_id,version_label,source_url,effective_date,repeal_date,legal_status,review_status,authenticity_verified,status_verified) VALUES(?,?,?,?,?,?,?,?,?)",
            ("D_" + version_label, version_label, "https://example.gov/" + version_label + ".pdf", effective_date, repeal_date, legal_status, review_status, authenticity_verified, status_verified)
        )
        self.db.execute(
            "UPDATE legal_document_versions SET amendment_history_verified=?,permission_evidence=? WHERE version_id=?",
            (amendment_history_verified, "https://example.gov/terms#commercial-reuse", cur.lastrowid)
        )
        for review_type in ("source_authenticity", "extraction_quality", "legal_status", "amendment_history", "licensing", "lawyer_approval"):
            notes = "Reviewed against evidence."
            if review_type == "lawyer_approval":
                notes = "[qualified_egyptian_counsel_attested:user_id=42] " + notes
            self.db.execute(
                "INSERT INTO legal_review_events(version_id,reviewer,review_type,outcome,notes,evidence_url) VALUES(?,?,?,?,?,?)",
                (cur.lastrowid, "Reviewer", review_type, "pass", notes, "https://example.gov/review"),
            )
        chunk = self.db.execute(
            "INSERT INTO chunks(ref,article,page,text,norm,document_version_id,in_force,as_of,source,verified) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                "Test law - article 1", "1", None, text, self.app.norm(text),
                cur.lastrowid, int(chunk_in_force), effective_date,
                "https://example.gov", 1,
            ),
        )
        chunk_id = chunk.lastrowid
        self.db.commit()
        return chunk_id, cur.lastrowid

    def test_corpus_hit_without_permission_register_match_cannot_generate_answer(self):
        _chunk_id, _version_id = self._make_linked_chunk(
            "register-crosscheck", "2020-01-01", text="registercrosscheck legal text"
        )
        hits = self.app.search(self.db, "registercrosscheck", as_of="2026-10-23")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["source_status"], "outdated_or_under_review")
        with patch.object(self.app, "LLM") as llm:
            result = self.app.ask(
                self.db, "registercrosscheck",
                as_of="2026-10-23", scope="verified_corpus",
            )
        self.assertTrue(result["abstained"])
        self.assertIsNone(result["answer"])
        llm.assert_not_called()

    def test_linked_version_requires_review_and_status_verification(self):
        chunk_id, version_id = self._make_linked_chunk("pending", "2020-01-01", review_status="pending_lawyer_review", authenticity_verified=0, status_verified=0)
        self.assertEqual(self.app.search(self.db, "versionprobe", as_of="2026-10-23"), [])
        self.db.execute("UPDATE legal_document_versions SET review_status='verified',authenticity_verified=1,status_verified=1 WHERE version_id=?", (version_id,))
        self.db.commit()
        hits = self.app.search(self.db, "versionprobe", as_of="2026-10-23")
        self.assertEqual([h["id"] for h in hits], [chunk_id])
        self.assertEqual(hits[0]["requested_as_of"], "2026-10-23")

    def test_commercial_reuse_permission_and_evidence_are_required_for_search(self):
        chunk_id, version_id = self._make_linked_chunk(
            "permission-gate", "2020-01-01", text="permissiongateprobe legal text"
        )
        self.db.execute(
            "UPDATE legal_sources SET collection_permission='unknown',commercial_reuse_permission='unknown',permission_evidence=NULL WHERE source_id=?",
            ("S_permission-gate",)
        )
        self.db.commit()
        self.assertEqual(self.app.search(self.db, "permissiongateprobe", as_of="2026-10-23"), [])
        self.assertEqual(self.app.search(self.db, "المادة 1", as_of="2026-10-23"), [])
        self.db.execute(
            "UPDATE legal_sources SET collection_permission='allowed',commercial_reuse_permission='allowed',permission_evidence=? WHERE source_id=?",
            ("https://example.gov/terms#commercial-reuse", "S_permission-gate")
        )
        self.db.execute(
            "UPDATE legal_document_versions SET permission_evidence=? WHERE version_id=?",
            ("https://example.gov/terms#commercial-reuse", version_id)
        )
        self.db.commit()
        self.assertEqual([h["id"] for h in self.app.search(self.db, "permissiongateprobe", as_of="2026-10-23")], [chunk_id])
        self.assertIn(chunk_id, [h["id"] for h in self.app.search(self.db, "المادة 1", as_of="2026-10-23")])

    def test_latest_licensing_and_lawyer_approval_events_gate_regular_and_exact_search(self):
        chunk_id, version_id = self._make_linked_chunk(
            "review-event-gate", "2020-01-01", text="revieweventgateprobe legal text"
        )
        for review_type in ("licensing", "lawyer_approval"):
            with self.subTest(review_type=review_type):
                self.db.execute(
                    "DELETE FROM legal_review_events WHERE version_id=? AND review_type=?",
                    (version_id, review_type),
                )
                self.db.commit()
                self.assertEqual(self.app.search(self.db, "revieweventgateprobe", as_of="2026-10-23"), [])
                self.assertEqual(self.app.search(self.db, "المادة 1", as_of="2026-10-23"), [])
                notes = "Reviewed against evidence."
                if review_type == "lawyer_approval":
                    notes = "[qualified_egyptian_counsel_attested:user_id=42] " + notes
                self.db.execute(
                    "INSERT INTO legal_review_events(version_id,reviewer,review_type,outcome,notes,evidence_url) VALUES(?,?,?,?,?,?)",
                    (version_id, "Reviewer", review_type, "pass", notes, "https://example.gov/review"),
                )
                self.db.commit()
                self.assertEqual([h["id"] for h in self.app.search(self.db, "revieweventgateprobe", as_of="2026-10-23")], [chunk_id])
                self.db.execute(
                    "UPDATE legal_review_events SET outcome='fail' WHERE review_event_id=(SELECT MAX(review_event_id) FROM legal_review_events WHERE version_id=? AND review_type=?)",
                    (version_id, review_type),
                )
                self.db.commit()
                self.assertEqual(self.app.search(self.db, "revieweventgateprobe", as_of="2026-10-23"), [])
                notes = "Re-reviewed against evidence."
                if review_type == "lawyer_approval":
                    notes = "[qualified_egyptian_counsel_attested:user_id=42] " + notes
                self.db.execute(
                    "INSERT INTO legal_review_events(version_id,reviewer,review_type,outcome,notes,evidence_url) VALUES(?,?,?,?,?,?)",
                    (version_id, "Reviewer", review_type, "pass", notes, "https://example.gov/review"),
                )
                self.db.commit()
                self.assertEqual([h["id"] for h in self.app.search(self.db, "revieweventgateprobe", as_of="2026-10-23")], [chunk_id])

    def test_unattested_lawyer_approval_blocks_regular_and_exact_search(self):
        chunk_id, version_id = self._make_linked_chunk(
            "counsel-attestation-gate", "2020-01-01", text="counselattestationprobe legal text"
        )
        self.db.execute(
            "UPDATE legal_review_events SET notes='Reviewed by a platform reviewer' "
            "WHERE version_id=? AND review_type='lawyer_approval'",
            (version_id,),
        )
        self.db.commit()
        self.assertEqual(self.app.search(self.db, "counselattestationprobe", as_of="2026-10-23"), [])
        self.assertEqual(self.app.search(self.db, "المادة 1", as_of="2026-10-23"), [])
        self.db.execute(
            "UPDATE legal_review_events SET notes=? WHERE version_id=? AND review_type='lawyer_approval'",
            ("[qualified_egyptian_counsel_attested:user_id=42] reviewed", version_id),
        )
        self.db.commit()
        self.assertIn(chunk_id, [hit["id"] for hit in self.app.search(
            self.db, "counselattestationprobe", as_of="2026-10-23"
        )])

    def test_amendment_history_must_be_verified_for_regular_and_exact_search(self):
        chunk_id, version_id = self._make_linked_chunk(
            "amendment-gate", "2020-01-01", amendment_history_verified=0,
            text="amendmentgateprobe legal text"
        )
        self.assertEqual(self.app.search(self.db, "amendmentgateprobe", as_of="2026-10-23"), [])
        self.assertEqual(self.app.search(self.db, "المادة 1", as_of="2026-10-23"), [])
        self.db.execute(
            "UPDATE legal_document_versions SET amendment_history_verified=1 WHERE version_id=?",
            (version_id,)
        )
        self.db.commit()
        self.assertEqual([h["id"] for h in self.app.search(self.db, "amendmentgateprobe", as_of="2026-10-23")], [chunk_id])
        self.assertIn(chunk_id, [h["id"] for h in self.app.search(self.db, "المادة 1", as_of="2026-10-23")])

    def test_future_effective_version_is_excluded_until_effective_date(self):
        chunk_id, _ = self._make_linked_chunk("future", "2027-10-01", text="futureprobe law text")
        self.assertEqual(self.app.search(self.db, "futureprobe", as_of="2026-10-23"), [])
        hits = self.app.search(self.db, "futureprobe", as_of="2027-10-01")
        self.assertEqual([h["id"] for h in hits], [chunk_id])

        # Exact article lookup must apply the same effective-date gate as normal
        # retrieval; otherwise a future law could appear to answer a numbered
        # article question before the law enters into force.
        self.assertEqual(self.app.search(self.db, "المادة 1", as_of="2026-10-23"), [])
        exact_hits = self.app.search(self.db, "المادة 1", as_of="2027-10-01")
        self.assertIn(chunk_id, [h["id"] for h in exact_hits])

    def test_repealed_version_is_excluded_on_and_after_repeal_date(self):
        chunk_id, _ = self._make_linked_chunk("repealed", "2020-01-01", repeal_date="2026-01-01", text="repealprobe law text")
        self.assertEqual(self.app.search(self.db, "repealprobe", as_of="2026-01-01"), [])
        self.assertEqual([h["id"] for h in self.app.search(self.db, "repealprobe", as_of="2025-12-31")], [chunk_id])

    def test_repealed_version_remains_available_before_its_repeal_date(self):
        chunk_id, version_id = self._make_linked_chunk(
            "historical-before-repeal", "2010-01-01", repeal_date="2024-01-01",
            legal_status="repealed", text="historicalbeforeprobe legal passage", chunk_in_force=0
        )
        before = self.app.search(self.db, "historicalbeforeprobe", as_of="2023-12-31")
        on_repeal = self.app.search(self.db, "historicalbeforeprobe", as_of="2024-01-01")
        self.assertEqual([hit["id"] for hit in before], [chunk_id])
        self.assertTrue(before[0]["applies_as_of"])
        self.assertEqual(on_repeal, [])
        answer = self.app.ask(self.db, "historicalbeforeprobe", as_of="2023-12-31")
        self.assertEqual(answer["not_in_force"], [])
        exact_before = self.app.search(self.db, "المادة 1", as_of="2023-12-31")
        exact_on_repeal = self.app.search(self.db, "المادة 1", as_of="2024-01-01")
        self.assertIn(chunk_id, [hit["id"] for hit in exact_before])
        self.assertNotIn(chunk_id, [hit["id"] for hit in exact_on_repeal])

    def test_historical_version_without_repeal_boundary_is_excluded(self):
        self._make_linked_chunk(
            "historical-unknown-boundary", "2010-01-01", repeal_date=None,
            legal_status="historical", text="unknownboundaryprobe legal passage"
        )
        self.assertEqual(self.app.search(self.db, "unknownboundaryprobe", as_of="2020-01-01"), [])

    def test_answer_prompt_includes_version_and_gazette_provenance(self):
        _, version_id = self._make_linked_chunk(
            "prompt-provenance", "2020-01-01", text="promptprovenanceprobe legal passage"
        )
        self.db.execute(
            "UPDATE legal_document_versions SET gazette_issue='77',gazette_pages='12-16',original_sha256=? WHERE version_id=?",
            ("a" * 64, version_id)
        )
        self.db.commit()
        captured = []
        rights_evidence = {
            "source_permission_register_match": True,
            "source_permission_register_collection_permission": "allowed",
            "source_permission_register_commercial_reuse_permission": "allowed",
            "permission_evidence_url": "https://example.gov/rights/collection",
            "commercial_reuse_evidence_url": "https://example.gov/rights/commercial",
            "terms_checked_on": "2026-10-20",
            "commercial_terms_checked_on": "2026-10-20",
        }
        with patch.object(self.app, "_central_source_permission_evidence", return_value=rights_evidence):
            hits = self.app.search(self.db, "promptprovenanceprobe", scope="verified_corpus")
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["source_status"], "verified_operative_text", hits[0]["provenance"])
            self.app.LLM = lambda prompt: captured.append(prompt) or "الإجابة مدعومة بالمصدر [1]"
            result = self.app.ask(self.db, "promptprovenanceprobe", scope="verified_corpus")
        self.assertTrue(result["found"])
        source_section = captured[0].split(
            "The JSON records are the only legal evidence supplied for this answer:\n", 1
        )[1].split("\n\nCurrent question", 1)[0]
        source_record = json.loads(source_section)
        provenance = json.loads(source_record["recorded_provenance"])
        self.assertEqual(provenance["version_label"], "prompt-provenance")
        self.assertEqual(provenance["gazette_issue"], "77")
        self.assertIn("Metadata is not a substitute for the cited legal text.", captured[0])

    def test_invalid_as_of_date_is_rejected(self):
        with self.assertRaises(ValueError):
            self.app.search(self.db, "anything", as_of="not-a-date")

    def test_search_citation_contains_exact_version_and_review_provenance(self):
        chunk_id, version_id = self._make_linked_chunk("provenance", "2020-01-01", text="provenanceprobe legal passage")
        self.db.execute(
            "UPDATE legal_document_versions SET publication_date='2019-12-15',gazette_issue='123',gazette_pages='4-8',consolidated_as_of='2024-01-01',amendment_history_verified=1 WHERE version_id=?",
            (version_id,)
        )
        self.db.execute(
            "INSERT INTO legal_review_events(version_id,reviewer,review_type,outcome,notes,evidence_url) VALUES(?,?,?,?,?,?)",
            (version_id, "reviewer-test", "amendment_history", "pass", "fixture only", "https://example.gov/review-evidence")
        )
        _, amended_version_id = self._make_linked_chunk("provenance-amended", "2024-01-01", text="otherprovenanceprobe amended legal passage")
        self.db.execute(
            "INSERT INTO legal_version_relations(from_version_id,to_version_id,relation_type,notes) VALUES(?,?,?,?)",
            (version_id, amended_version_id, "amends", "fixture only")
        )
        self.db.commit()
        hit = self.app.search(self.db, "provenanceprobe", as_of="2026-10-23")[0]
        p = hit["provenance"]
        self.assertEqual(hit["id"], chunk_id)
        self.assertEqual(p["status"], "registry_linked")
        self.assertEqual(p["version_id"], version_id)
        self.assertEqual(p["official_title"], "Test law")
        self.assertEqual(p["gazette_issue"], "123")
        self.assertTrue(p["amendment_history_verified"])
        self.assertEqual(p["review_evidence"][0]["evidence_url"], "https://example.gov/review-evidence")
        self.assertEqual(p["relations"][0]["relation_type"], "amends")
        self.assertEqual(p["relations"][0]["to_version_id"], amended_version_id)

    def test_corpus_profile_rejects_unlinked_legacy_chunks(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO chunks(ref,article,text,norm,in_force,source,verified) "
                "VALUES(?,?,?,?,?,?,?)",
                ("Legacy source", "1", "legacyprobe passage",
                 self.app.norm("legacyprobe passage"), 1, "legacy", 1),
            )
        self.db.rollback()
        self.assertEqual(self.app.search(self.db, "legacyprobe"), [])
        self.assertEqual(self.app.search(self.db, "المادة 1"), [])

if __name__ == "__main__":
    unittest.main()
