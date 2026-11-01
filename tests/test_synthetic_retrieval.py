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
            notes = "synthetic fixture only"
            if review_type == "lawyer_approval":
                notes = "[qualified_egyptian_counsel_attested:user_id=42] synthetic fixture only"
            self.db.execute(
                """INSERT INTO legal_review_events
                   VALUES (?, ?, ?, 'pass', ?, 'Automated test fixture',
                           'https://example.test/evidence', '2026-01-01T00:00:00')""",
                (version_id * 10 + index, version_id, review_type, notes),
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
            mock.patch.object(app, "corpus_conn", side_effect=lambda: self.fixture.db),
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

    def test_multi_area_egyptian_colloquial_queries_retrieve_their_intended_synthetic_passages(self):
        # Fictional passages validate retrieval routing only; they are not legal authorities.
        cases = (
            ("المرتب متأخر", "تأخر صرف الأجر ومستحقات العامل"),
            ("طردني من الشغل", "فصل العامل وإنهاء الخدمة"),
            ("صاحب البيت عايز يطردني", "إخلاء المستأجر ودعوى الإخلاء"),
            ("جوزي مش بيصرف", "نفقة الزوجة والامتناع عن الإنفاق"),
            ("مش عارف آخد ورثي", "قسمة التركة وحقوق الورثة"),
            ("اتقبض عليا", "القبض وضمانات القبض"),
            ("اتظلمت من قرار", "التظلم من القرار الإداري والقرار الإداري"),
            ("الشيك رجع", "شيك مرتجع وشيك مرفوض"),
            ("حد نصب عليا أونلاين", "الاحتيال الإلكتروني وجرائم تقنية المعلومات"),
            ("مش بيرجعلي فلوسي", "رد المبالغ ودعوى المطالبة"),
        )

        for index, (query, expected_phrase) in enumerate(cases, start=1):
            with self.subTest(query=query):
                self.fixture.db.close()
                self.fixture = SyntheticCorpus()
                intended_id = self.fixture.add_passage(
                    f"SYNTH-DIALECT-{index:02d}",
                    f"نص اختبار خيالي وليس قانونا: {expected_phrase}.",
                )
                self.fixture.add_passage(
                    f"SYNTH-DECOY-{index:02d}",
                    "نص اختبار خيالي وليس قانونا: صيانة المحركات البحرية وجدول المد والجزر.",
                )

                hits = self.search(query)

                self.assertTrue(hits, f"no synthetic passage retrieved for {query!r}")
                self.assertEqual(hits[0]["id"], intended_id, f"wrong passage ranked first for {query!r}")

    def test_new_lexicon_phrases_retrieve_the_intended_passage_in_top_three(self):
        cases = (
            ("فصلني من الشغل", "فصل العامل وإنهاء عقد العمل وإنهاء الخدمة"),
            ("عايز إجازة", "الإجازة السنوية للعامل وشروط الإجازة"),
            ("الإيجار القديم", "امتداد عقد الإيجار القديم والعلاقة الإيجارية القديمة"),
        )
        for index, (query, passage) in enumerate(cases, start=1):
            with self.subTest(query=query):
                self.fixture.db.close()
                self.fixture = SyntheticCorpus()
                intended_id = self.fixture.add_passage(
                    f"SYNTH-LEXICON-{index:02d}",
                    f"نص اختبار خيالي وليس قانونا: {passage}.",
                )
                self.fixture.add_passage(
                    f"SYNTH-LEXICON-DECOY-{index:02d}",
                    "نص اختبار خيالي وليس قانونا: صيانة المحركات البحرية وجدول المد والجزر.",
                )
                hits = self.search(query)
                self.assertIn(intended_id, [hit["id"] for hit in hits[:3]])

    def test_colloquial_queries_retrieve_intended_synthetic_passages_in_top_three(self):
        # These are retrieval fixtures, not lawyer-reviewed questions or legal ground truth.
        cases = (
            ("صاحب الشغل مش بيدفع المرتب", "صاحب العمل عدم سداد الأجر الأجر المتأخر"),
            ("المرتب متأخر", "تأخر صرف الأجر مستحقات العامل"),
            ("طردني من الشغل", "فصل العامل إنهاء الخدمة"),
            ("الشيك رجع", "شيك مرتجع شيك مرفوض"),
            ("مفيش رصيد", "بدون رصيد شيك مرتجع"),
            ("وصل أمانة", "إيصال أمانة"),
            ("صاحب البيت", "المؤجر مالك العقار"),
            ("عايز يطردني", "الإخلاء إخلاء المستأجر"),
            ("مصاريف العيال", "نفقة الصغار نفقة الأولاد"),
            ("جوزي مش بيصرف", "نفقة الزوجة الامتناع عن الإنفاق"),
            ("عايز أرفع قضية", "رفع دعوى صحيفة الدعوى"),
            ("حد نصب عليا", "احتيال استرداد المبالغ"),
            ("فلوسي عند حد", "دين مطالبة مالية"),
            ("مش عارف أفسخ العقد", "فسخ العقد إنهاء العقد"),
            ("المرتب مش نازل", "عدم صرف الأجر الأجر المتأخر"),
            ("خصموا من مرتبي", "خصم الأجر الاستقطاع من الأجر"),
            ("شغال من غير عقد", "إثبات علاقة العمل عقد العمل"),
            ("فصلوني تعسفي", "الفصل التعسفي التعويض عن الفصل"),
            ("اشتغلت إضافي ومخدتش فلوس", "ساعات العمل الإضافية مقابل العمل الإضافي"),
            ("مأمنوش عليا", "التأمين الاجتماعي التأمينات الاجتماعية"),
            ("صاحب البيت عايز يطردني", "إخلاء المستأجر دعوى الإخلاء"),
            ("الإيجار زاد عليا", "زيادة الأجرة القيمة الإيجارية"),
            ("مش بيرجعلي التأمين", "رد التأمين المطالبة المالية"),
            ("مديونلي ومش بيدفع", "الوفاء بالدين المطالبة بالدين"),
            ("باعلي حاجة مضروبة", "العيب الخفي ضمان العيوب"),
            ("عملت توكيل وعايز ألغيه", "إلغاء التوكيل عزل الوكيل"),
            ("الحكم غيابي", "الحكم الغيابي المعارضة في الحكم"),
            ("وصلني إنذار", "الإنذار الرسمي إجراءات الإعلان"),
            ("مش بيدفع نفقة", "الامتناع عن سداد النفقة تنفيذ حكم النفقة"),
            ("عايزة أخلع", "دعوى الخلع إجراءات الخلع"),
            ("ورث ومش راضي يوزع", "قسمة التركة حقوق الورثة"),
            ("حد نصب عليا أونلاين", "الاحتيال الإلكتروني جرائم تقنية المعلومات"),
            ("العربية اتخبطت", "حادث سيارة التعويض عن حوادث السيارات"),
            ("عملولي محضر", "تحرير محضر محضر الشرطة"),
            ("اتعمل ضدي محضر", "محضر الشرطة التحقيق الجنائي"),
            ("الشرطة استدعتني", "استدعاء الشرطة سماع الأقوال"),
            ("اتقبض عليا", "القبض ضمانات القبض"),
            ("اتحبست", "الحبس الاحتياطي ضمانات المتهم"),
            ("عايز أعمل محضر", "تحرير محضر تقديم بلاغ"),
            ("اتظلمت من قرار", "التظلم من القرار الإداري القرار الإداري"),
            ("الجهة رفضت طلبي", "رفض الطلب التظلم الإداري"),
            ("مش عارف آخد ورثي", "قسمة التركة حقوق الورثة"),
            ("اخواتي مش بيدوني حقي في الورث", "قسمة التركة دعوى القسمة"),
            ("الشركة مخصمتليش التأمينات", "اشتراكات التأمين الاجتماعي التأمينات الاجتماعية"),
            ("مضوني على استقالة", "الاستقالة صحة الاستقالة"),
            ("مضوني على ورق", "الإكراه صحة المحررات"),
            ("عايز أفسخ عقد الإيجار", "فسخ عقد الإيجار إنهاء عقد الإيجار"),
            ("مش بيرجعلي فلوسي", "رد المبالغ دعوى المطالبة"),
            ("فصلني من الشغل", "فصل العامل إنهاء عقد العمل"),
            ("عايز إجازة", "إجازة سنوية الإجازة السنوية"),
            ("الإيجار القديم", "العلاقة الإيجارية القديمة امتداد عقد الإيجار"),
        )
        ranks = []
        for index, (query, intended_text) in enumerate(cases, start=1):
            with self.subTest(query=query):
                self.fixture.db.close()
                self.fixture = SyntheticCorpus()
                intended_id = self.fixture.add_passage(
                    f"SYNTH-TOP3-{index:02d}",
                    f"نص اختبار خيالي وليس قانونا: {intended_text}.",
                )
                self.fixture.add_passage(
                    f"SYNTH-TOP3-DECOY-{index:02d}",
                    "نص اختبار خيالي وليس قانونا: إجراءات التقاضي والإعلان ومواعيد الطعن والمحاكم المختصة.",
                )
                self.fixture.add_passage(
                    f"SYNTH-TOP3-OFFTOPIC-{index:02d}",
                    "نص اختبار خيالي وليس قانونا: صيانة المحركات البحرية وجدول المد والجزر.",
                )
                hits = self.search(query)
                ids = [hit["id"] for hit in hits[:3]]
                self.assertIn(intended_id, ids, f"intended passage fell outside top three for {query!r}")
                ranks.append(ids.index(intended_id) + 1)
        top_one = sum(rank == 1 for rank in ranks)
        print(f"synthetic colloquial retrieval: top-3 {len(ranks)}/{len(cases)}; top-1 {top_one}/{len(cases)}")
        self.assertEqual(len(ranks), len(cases))

    def test_out_of_corpus_questions_abstain_on_unrelated_fictional_corpus(self):
        unrelated_questions = (
            "حالة الطقس غدا",
            "وصفة شوربة العدس",
            "أفضل كاميرا رقمية",
            "كيف أزرع النعناع",
            "تعلم العزف على العود",
            "تاريخ الحضارة الصينية",
            "كم عدد كواكب المجموعة الشمسية",
            "طريقة إصلاح دراجة هوائية",
            "برنامج تعديل الصور",
            "رحلات الطيران إلى طوكيو",
        )
        self.fixture.add_passage(
            "SYNTH-ONLY-LAW",
            "نص اختبار خيالي وليس قانونا: اختصاصات محكمة النقض في الطعون الجنائية.",
        )
        for query in unrelated_questions:
            with self.subTest(query=query):
                self.assertEqual(self.search(query), [], f"unrelated query retrieved a passage: {query!r}")

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
        with mock.patch.object(app, "LLM") as model:
            result = app.ask(
                None, "سؤال غير موجود في بيانات الاختبار",
                scope="verified_corpus", as_of="2026-01-01",
            )
            model.assert_not_called()

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
