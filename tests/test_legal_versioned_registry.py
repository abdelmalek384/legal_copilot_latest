import os
import sqlite3
import tempfile
import unittest
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
        os.environ["COPILOT_DB"] = str(Path(self.tmp.name) / "registry.db")
        import importlib
        import app
        self.app = importlib.reload(app)
        self.db = self.app.conn()

    def tearDown(self):
        try:
            self.db.close()
        finally:
            import app
            app._t.c = None
            app._schema_ready = False
            self.tmp.cleanup()
            os.environ.pop("COPILOT_DB", None)

    def test_registry_tables_exist_and_legacy_chunks_are_linkable(self):
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


    def _make_linked_chunk(self, version_label, effective_date, repeal_date=None, review_status="verified", legal_status="in_force", authenticity_verified=1, status_verified=1, text="versionprobe legal text"):
        self.db.execute("INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
                        ("S_" + version_label, "Example Authority", "https://example.gov"))
        self.db.execute("INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
                        ("D_" + version_label, "S_" + version_label, "Test law", "legislation"))
        cur = self.db.execute(
            "INSERT INTO legal_document_versions(document_id,version_label,source_url,effective_date,repeal_date,legal_status,review_status,authenticity_verified,status_verified) VALUES(?,?,?,?,?,?,?,?,?)",
            ("D_" + version_label, version_label, "https://example.gov/" + version_label + ".pdf", effective_date, repeal_date, legal_status, review_status, authenticity_verified, status_verified)
        )
        self.app.add_chunks(self.db, [{"ref":"Test law - article 1","article":"1","text":text,"in_force":1,"verified":1,"source":"https://example.gov"}])
        chunk_id = self.db.execute("SELECT id FROM chunks WHERE ref='Test law - article 1' ORDER BY id DESC LIMIT 1").fetchone()[0]
        self.db.execute("UPDATE chunks SET document_version_id=? WHERE id=?", (cur.lastrowid, chunk_id))
        self.db.commit()
        return chunk_id, cur.lastrowid

    def test_linked_version_requires_review_and_status_verification(self):
        chunk_id, version_id = self._make_linked_chunk("pending", "2020-01-01", review_status="pending_lawyer_review", authenticity_verified=0, status_verified=0)
        self.assertEqual(self.app.search(self.db, "versionprobe", as_of="2026-10-23"), [])
        self.db.execute("UPDATE legal_document_versions SET review_status='verified',authenticity_verified=1,status_verified=1 WHERE version_id=?", (version_id,))
        self.db.commit()
        hits = self.app.search(self.db, "versionprobe", as_of="2026-10-23")
        self.assertEqual([h["id"] for h in hits], [chunk_id])
        self.assertEqual(hits[0]["requested_as_of"], "2026-10-23")

    def test_future_effective_version_is_excluded_until_effective_date(self):
        chunk_id, _ = self._make_linked_chunk("future", "2027-10-01", text="futureprobe law text")
        self.assertEqual(self.app.search(self.db, "futureprobe", as_of="2026-10-23"), [])
        hits = self.app.search(self.db, "futureprobe", as_of="2027-10-01")
        self.assertEqual([h["id"] for h in hits], [chunk_id])

    def test_repealed_version_is_excluded_on_and_after_repeal_date(self):
        chunk_id, _ = self._make_linked_chunk("repealed", "2020-01-01", repeal_date="2026-01-01", text="repealprobe law text")
        self.assertEqual(self.app.search(self.db, "repealprobe", as_of="2026-01-01"), [])
        self.assertEqual([h["id"] for h in self.app.search(self.db, "repealprobe", as_of="2025-12-31")], [chunk_id])

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

    def test_unlinked_legacy_citation_is_explicitly_labelled(self):
        self.app.add_chunks(self.db, [{"ref":"Legacy source","text":"legacyprobe passage","in_force":1,"verified":1,"source":"legacy"}])
        hit = self.app.search(self.db, "legacyprobe")[0]
        self.assertEqual(hit["provenance"]["status"], "legacy_unlinked")

if __name__ == "__main__":
    unittest.main()
