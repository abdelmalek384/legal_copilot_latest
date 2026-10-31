"""End-to-end retrieval regressions over explicitly fictional legal passages.

These fixtures exercise the production search path and its evidence filters. They are
not Egyptian legislation, legal guidance, or a source of evaluation ground truth.
"""
import sqlite3
import unittest
from unittest import mock

import app


REVIEW_TYPES = (
    "source_authenticity",
    "extraction_quality",
    "legal_status",
    "amendment_history",
    "licensing",
    "lawyer_approval",
)


class SyntheticCorpus:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript(
            """
            CREATE TABLE chunks (
                id INTEGER PRIMARY KEY, ref TEXT, article TEXT, page TEXT, text TEXT,
                case_id INTEGER, in_force INTEGER, verified INTEGER, as_of TEXT,
                source TEXT, document_version_id INTEGER
            );
            CREATE VIRTUAL TABLE chunks_fts USING fts5(norm);
            CREATE TABLE legal_sources (
                source_id TEXT PRIMARY KEY, collection_permission TEXT,
                commercial_reuse_permission TEXT, permission_evidence TEXT
            );
            CREATE TABLE legal_documents (
                document_id TEXT PRIMARY KEY, source_id TEXT, official_title TEXT
            );
            CREATE TABLE legal_document_versions (
                version_id INTEGER PRIMARY KEY, document_id TEXT,
                review_status TEXT, authenticity_verified INTEGER,
                status_verified INTEGER, amendment_history_verified INTEGER,
                legal_status TEXT, effective_date TEXT, repeal_date TEXT,
                permission_evidence TEXT
            );
            CREATE TABLE legal_review_events (
                review_event_id INTEGER PRIMARY KEY, version_id INTEGER,
                review_type TEXT, outcome TEXT, notes TEXT, reviewer TEXT,
                evidence_url TEXT, reviewed_at TEXT
            );
            """
        )

    def add_passage(
        self, source_id, text, *, verified=True, collection="allowed",
        commercial="allowed", effective="2020-01-01", repeal=None,
        review_status="verified", article="12",
    ):
        version_id = self.db.execute(
            "SELECT COALESCE(MAX(version_id), 0) + 1 FROM legal_document_versions"
        ).fetchone()[0]
        document_id = "DOC-" + source_id
        self.db.execute(
            "INSERT INTO legal_sources VALUES (?, ?, ?, ?)",
            (source_id, collection, commercial, "SYNTHETIC TEST PERMISSION"),
        )
        self.db.execute(
            "INSERT INTO legal_documents VALUES (?, ?, ?)",
            (document_id, source_id, "Fictional test instrument — not law"),
        )
        self.db.execute(
            """INSERT INTO legal_document_versions
               VALUES (?, ?, ?, 1, 1, 1, 'in_force', ?, ?, 'SYNTHETIC TEST PERMISSION')""",
            (version_id, document_id, review_status, effective, repeal),
        )
        for index, review_type in enumerate(REVIEW_TYPES, 1):
            self.db.execute(
                """INSERT INTO legal_review_events
                   VALUES (?, ?, ?, 'pass', 'synthetic fixture only',
                           'Automated test fixture', 'https://example.test/evidence',
                           '2026-01-01T00:00:00')""",
                (version_id * 10 + index, version_id, review_type),
            )
        cursor = self.db.execute(
            """INSERT INTO chunks
               (ref, article, page, text, case_id, in_force, verified, as_of,
                source, document_version_id)
               VALUES (?, ?, 'TEST-PAGE', ?, NULL, 1, ?, '2026-01-01',
                       'SYNTHETIC FIXTURE — NOT LAW', ?)""",
            ("Synthetic " + source_id, article, text, int(verified), version_id),
        )
        chunk_id = cursor.lastrowid
        self.db.execute(
            "INSERT INTO chunks_fts(rowid, norm) VALUES (?, ?)",
            (chunk_id, " ".join(app.tokens(text))),
        )
        self.db.commit()
        return chunk_id


class SyntheticRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SyntheticCorpus()
        self.patches = [
            mock.patch.object(app, "corpus_conn", return_value=self.fixture.db),
            mock.patch.object(
                app, "citation_provenance",
                side_effect=lambda _db, version_id: {
                    "status": "registry_linked", "source_id": "SYNTHETIC",
                    "version_id": version_id, "legal_status": "in_force",
                },
            ),
            mock.patch.object(
                app, "source_status", return_value="verified_operative_text"
            ),
            mock.patch.object(
                app, "citation_text", return_value="Synthetic test citation"
            ),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.fixture.db.close()

    def search(self, query, *, as_of="2026-01-01"):
        return app.search(
            None, query, k=10, scope="verified_corpus", as_of=as_of
        )

    def test_egyptian_colloquial_query_retrieves_intended_synthetic_passage(self):
        intended_id = self.fixture.add_passage(
            "SYNTH-WORK-01",
            "نص اختبار خيالي وليس قانونا: إثبات علاقة العمل وعقد العمل عند العمل دون عقد مكتوب.",
        )
        self.fixture.add_passage(
            "SYNTH-RENT-01",
            "نص اختبار خيالي وليس قانونا: أحكام الإيجار وتسليم العين المؤجرة.",
        )

        hits = self.search("شغال من غير عقد")

        self.assertTrue(hits)
        self.assertEqual(hits[0]["id"], intended_id)
        self.assertIn("عقد", hits[0]["matched_terms"])

    def test_unrelated_synthetic_passage_does_not_become_a_result(self):
        self.fixture.add_passage(
            "SYNTH-CRIM-01",
            "نص اختبار خيالي وليس قانونا: اختصاصات محكمة النقض في الطعون الجنائية.",
        )

        self.assertEqual(self.search("عايزة أخلع"), [])

    def test_unverified_or_permission_blocked_passages_are_excluded(self):
        allowed_id = self.fixture.add_passage(
            "SYNTH-ALLOW-01",
            "نص اختبار خيالي وليس قانونا: دعوى الخلع وإجراءات الخلع والتطليق خلعاً.",
        )
        self.fixture.add_passage(
            "SYNTH-UNVERIFIED-01",
            "نص اختبار خيالي وليس قانونا: دعوى الخلع وإجراءات الخلع.",
            verified=False,
        )
        self.fixture.add_passage(
            "SYNTH-NO-RIGHTS-01",
            "نص اختبار خيالي وليس قانونا: دعوى الخلع وإجراءات الخلع.",
            commercial="unknown",
        )

        hits = self.search("عايزة أخلع")

        self.assertEqual([hit["id"] for hit in hits], [allowed_id])

    def test_future_and_expired_versions_are_excluded_as_of_requested_date(self):
        valid_id = self.fixture.add_passage(
            "SYNTH-CURRENT-01",
            "نص اختبار خيالي وليس قانونا: دعوى الخلع وإجراءات الخلع.",
            effective="2020-01-01",
        )
        self.fixture.add_passage(
            "SYNTH-FUTURE-01",
            "نص اختبار خيالي وليس قانونا: دعوى الخلع وإجراءات الخلع.",
            effective="2027-01-01",
        )
        self.fixture.add_passage(
            "SYNTH-EXPIRED-01",
            "نص اختبار خيالي وليس قانونا: دعوى الخلع وإجراءات الخلع.",
            effective="2020-01-01",
            repeal="2025-12-31",
        )

        hits = self.search("عايزة أخلع", as_of="2026-01-01")

        self.assertEqual([hit["id"] for hit in hits], [valid_id])

    def test_empty_retrieval_abstains_without_calling_the_model(self):
        result = app.ask(
            None, "سؤال غير موجود في بيانات الاختبار",
            scope="verified_corpus", as_of="2026-01-01",
        )

        self.assertFalse(result["found"])
        self.assertTrue(result["abstained"])
        self.assertEqual(result["sources"], [])

    def test_unrelated_cited_claim_and_uncited_claim_fail_closed(self):
        hits = [{"text": "نص اختبار خيالي: العامل يستحق إجازة سنوية."}]

        self.assertTrue(app._answer_has_unanchored_citations(
            "يلتزم المستأجر بدفع مبلغ 90000 جنيه [1].", hits
        ))
        self.assertTrue(app._answer_has_uncited_claims(
            "يلتزم المستأجر بدفع مبلغ 90000 جنيه."
        ))


if __name__ == "__main__":
    unittest.main()
