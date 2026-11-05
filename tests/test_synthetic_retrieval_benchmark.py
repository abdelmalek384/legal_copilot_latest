"""Known-answer retrieval benchmark over a wholly fictional Arabic corpus.

This measures retrieval and abstention mechanics only, never Egyptian legal correctness.
"""
import json
import unittest
from unittest import mock

import app
from test_synthetic_retrieval import SyntheticCorpus


TOPICS = {
    "employment": (
        ("تأخر صرف الأجر", "عدم دفع المقابل المالي عن العمل", "المرتب متأخر ومش نازل", "الأجر المستحق", "أجور العاملين المتأخرة"),
        ("الإجازة السنوية", "رصيد العطلات السنوي للعامل", "عايز آخد إجازتي السنوية", "العطلة السنوية", "إجازات العامل"),
        ("ساعات العمل الإضافية", "مقابل ساعات العمل الزائدة", "اشتغلت زيادة ومخدتش فلوس", "العمل فوق الساعات المقررة", "ساعات العامل الإضافية"),
        ("الفصل التعسفي", "إنهاء خدمة العامل دون سبب مشروع", "فصلوني من غير حق", "إنهاء غير مبرر لعلاقة العمل", "حالات فصل العامل تعسفيا"),
    ),
    "tenancy": (
        ("زيادة الأجرة", "رفع القيمة المالية للانتفاع بالعين", "صاحب البيت زود الإيجار عليا", "رفع القيمة الإيجارية", "زيادات الإيجارات"),
        ("رد مبلغ التأمين الإيجاري", "استرداد المبلغ المودع عند انتهاء الإيجار", "مش بيرجعلي تأمين الشقة", "استرداد وديعة الإيجار", "التأمينات الإيجارية"),
        ("إخلاء المستأجر", "إنهاء شغل العين المؤجرة وتسليمها", "عايز يطردني من الشقة", "طرد شاغل العين", "حالات إخلاء المستأجرين"),
        ("صيانة العين المؤجرة", "التزام المالك بإصلاح العقار", "الشقة فيها عطل وصاحب البيت مش بيصلح", "إصلاح المسكن المؤجر", "صيانة الوحدات المؤجرة"),
    ),
    "family": (
        ("نفقة الصغار", "التزام الأب بالإنفاق على الأبناء", "أبو العيال مش بيصرف عليهم", "مصاريف الأولاد", "نفقات الأطفال"),
        ("أجر الحضانة", "المقابل المالي لرعاية الصغير", "عايزة فلوس الحضانة", "مقابل رعاية الطفل", "أجور الحاضنات"),
        ("رؤية الصغير", "تنظيم لقاء الوالد غير الحاضن بالطفل", "مش بيخلوني أشوف ابني", "زيارة الطفل", "مواعيد رؤية الأطفال"),
        ("قسمة التركة", "توزيع أموال المتوفى على الورثة", "إخواتي مش بيدوني حقي في الورث", "تقسيم الميراث", "حقوق الورثة في التركة"),
    ),
    "procedure": (
        ("ميعاد الاستئناف", "الفترة المقررة للطعن على الحكم أمام الدرجة الأعلى", "لسه قدامي وقت أستأنف", "أجل الطعن بالاستئناف", "مواعيد الاستئنافات"),
        ("إعلان صحيفة الدعوى", "إبلاغ الخصم بورقة افتتاح الخصومة", "الخصم موصلوش ورق القضية", "إخطار المدعى عليه بالدعوى", "إعلانات صحف الدعاوى"),
        ("وقف التنفيذ", "تعليق تنفيذ الحكم مؤقتا", "عايز أوقف تنفيذ الحكم", "تعليق التنفيذ القضائي", "طلبات وقف التنفيذ"),
        ("الاختصاص المحلي", "تحديد المحكمة المختصة بحسب الموطن", "أرفع القضية في محكمة أنهي مكان", "اختصاص المحكمة المكاني", "قواعد الاختصاص المحلي"),
    ),
    "cheques": (
        ("الشيك المرتجع", "رفض البنك صرف الشيك لعدم كفاية الرصيد", "الشيك رجع من البنك", "شيك مرفوض الصرف", "الشيكات المرتجعة"),
        ("تظهير الشيك", "نقل الحق في الشيك إلى مستفيد آخر بالتوقيع", "عايز أحول الشيك لحد تاني", "نقل ملكية الشيك بالتظهير", "تظهيرات الشيكات"),
        ("ميعاد تقديم الشيك", "الفترة المقررة لتقديم الورقة للبنك", "آخر وقت أقدم فيه الشيك إمتى", "مدة تقديم الشيك للصرف", "مواعيد تقديم الشيكات"),
        ("توقيع الساحب", "صحة إمضاء محرر الشيك", "الإمضا على الشيك مش بتاعه", "توقيع محرر الشيك", "توقيعات الساحبين"),
    ),
    "tax": (
        ("الإقرار الضريبي", "تقديم بيان سنوي عن الدخل والضريبة", "إمتى أقدم ورق الضرايب", "بيان الدخل الخاضع للضريبة", "الإقرارات الضريبية"),
        ("الفحص الضريبي", "مراجعة حسابات الممول ومستنداته", "المأمورية عايزة تراجع حساباتي", "مراجعة الملف الضريبي", "إجراءات فحص الممولين"),
        ("ضريبة القيمة المضافة", "الضريبة المفروضة على تداول السلع والخدمات", "الضريبة اللي على البيع والخدمات", "ضريبة الاستهلاك غير المباشر", "ضرائب القيمة المضافة"),
        ("التظلم الضريبي", "الاعتراض الإداري على ربط الضريبة", "عايز أعترض على الضريبة", "منازعة تقدير الضريبة", "طلبات التظلمات الضريبية"),
    ),
    "social_insurance": (
        ("اشتراكات التأمين الاجتماعي", "المبالغ الدورية المستحقة لهيئة التأمينات", "الشركة مش بتدفع التأمينات", "مساهمات الضمان الاجتماعي", "اشتراكات المؤمن عليهم"),
        ("المعاش المبكر", "استحقاق المعاش قبل بلوغ السن القانونية", "عايز أطلع معاش بدري", "التقاعد قبل السن", "حالات المعاشات المبكرة"),
        ("إصابة العمل", "الحادث الذي يقع أثناء أداء الوظيفة", "اتصبت وأنا في الشغل", "إصابة أثناء العمل", "إصابات العاملين"),
        ("تعويض البطالة", "المبلغ المستحق عند فقد العمل", "اترفدت وعايز تعويض بطالة", "إعانة فقد الوظيفة", "تعويضات العاطلين"),
    ),
    "data_protection": (
        ("موافقة صاحب البيانات", "إذن الشخص بجمع بياناته ومعالجتها", "ينفع ياخدوا بياناتي من غير إذني", "إذن الشخص المعني", "موافقات أصحاب البيانات"),
        ("نقل البيانات الشخصية", "إرسال معلومات الأفراد إلى جهة أخرى", "بياناتي اتبعتت لشركة تانية", "تحويل المعلومات الشخصية", "عمليات نقل البيانات"),
        ("الإخطار باختراق البيانات", "إبلاغ الجهة المختصة عند تسرب المعلومات", "حصل تسريب لبيانات العملاء", "إشعار حادث أمن المعلومات", "إخطارات خروقات البيانات"),
        ("حقوق صاحب البيانات", "حقوق الفرد في الوصول إلى بياناته وتصحيحها", "عايز أعرف بياناتي وأعدلها", "صلاحيات الشخص المعني", "حقوق الأفراد في بياناتهم"),
    ),
}

DECOYS = {
    "employment": ("مكان أداء العمل", "السجل الوظيفي", "العطلات الرسمية", "التحقيق الداخلي", "تسليم أدوات العمل", "تسوية العهدة"),
    "tenancy": ("صيانة المصعد", "تسليم المفاتيح", "تأمين المرافق", "مرافق المبنى", "ترخيص النشاط", "اتحاد الشاغلين"),
    "family": ("توثيق الزواج", "إثبات النسب", "تغيير اسم الطفل", "توثيق الطلاق", "إثبات الغيبة", "إدارة أموال القاصر"),
    "procedure": ("وقف الخصومة", "رد القاضي", "ضم الدعاوى", "تصحيح الحكم", "إيداع الأمانة", "إثبات الحالة"),
    "cheques": ("تظهير الكمبيالة", "تاريخ الاستحقاق", "الشيك السياحي", "الشيك لحامله", "تقديم الورقة", "اعتراض الساحب"),
    "tax": ("الإعفاء الضريبي", "الخصم والتحصيل", "ضريبة العقارات", "السجل التجاري", "الطعن في التقدير", "دفاتر الممول"),
    "social_insurance": ("سن التقاعد", "المعاش المبكر الجزئي", "إصابة الطريق", "الاشتراكات الاختيارية", "المستحقون للمعاش", "تعويض الوفاة"),
    "data_protection": ("موافقة المعالجة", "نقل السجلات", "تسريب كلمات المرور", "حقوق المستخدم", "الاحتفاظ بالسجلات", "ترخيص مركز البيانات"),
}

MUST_ABSTAIN = (
    "كم سعر تذكرة الطيران إلى باريس؟",
    "الطقس في الإسكندرية غدا؟",
    "كيف أطبخ الملوخية؟",
    "ما أفضل كاميرا للتصوير الليلي؟",
    "هل سأكسب قضيتي؟",
    "هل سأربح قضيتي؟",
    "ماذا سيحدث في حياتي القادمة؟",
    "هل ستسير أموري كما أتمنى مهما كانت الظروف؟",
)


class FictionalRetrievalMeasurementTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SyntheticCorpus()
        self.patches = [
            mock.patch.dict("os.environ", {"LEGAL_QUALIFIED_EGYPTIAN_COUNSEL_USER_IDS": "42"}),
            mock.patch.object(app, "corpus_conn", side_effect=lambda: self.fixture.db),
            mock.patch.object(
                app, "citation_provenance",
                side_effect=lambda _db, version_id: {
                    "status": "registry_linked", "source_id": "SYNTHETIC",
                    "version_id": version_id, "legal_status": "in_force",
                },
            ),
            mock.patch.object(app, "source_status", return_value="verified_operative_text"),
            mock.patch.object(app, "citation_text", return_value="Synthetic test citation"),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.fixture.db.close()

    def search(self, query, as_of="2024-06-01"):
        return app.search(None, query, k=10, scope="verified_corpus", as_of=as_of)

    def test_200_known_answer_queries_across_eight_fictional_areas(self):
        styles = ("direct", "paraphrase", "colloquial", "synonym", "word_form", "date_sensitive")
        expected = {}
        article_number = 0

        for area, topics in TOPICS.items():
            for variants in topics:
                article_number += 1
                direct, paraphrase, colloquial, synonym, word_form = variants
                body = "نص قانون خيالي للاختبار فقط: " + "؛ ".join(variants)
                source_id = f"BENCH-{area.upper()}-{article_number:02d}"
                self.fixture.add_passage(source_id, body, article=str(article_number))
                queries = {
                    "direct": direct,
                    "paraphrase": paraphrase,
                    "colloquial": colloquial,
                    "synonym": synonym,
                    "word_form": word_form,
                    "date_sensitive": direct,
                }
                for style, query in queries.items():
                    expected.setdefault(style, []).append((query, str(article_number)))

        # Add 48 distractor articles: six in each of the eight practice areas.
        for area, phrases in DECOYS.items():
            for phrase in phrases:
                article_number += 1
                self.fixture.add_passage(
                    f"BENCH-DECOY-{article_number:02d}",
                    f"نص قانون خيالي للاختبار فقط: {phrase}.",
                    article=str(article_number),
                )
        self.assertEqual(article_number, 80)

        # Future and expired versions deliberately repeat an in-scope article's words.
        # Date filtering must keep them out of the 2024 answer set.
        base_body = "نص قانون خيالي للاختبار فقط: " + "؛ ".join(TOPICS["employment"][0])
        future_id = self.fixture.add_passage(
            "BENCH-FUTURE", base_body, article="1", effective="2025-01-01"
        )
        expired_id = self.fixture.add_passage(
            "BENCH-EXPIRED", base_body, article="1",
            effective="2020-01-01", repeal="2023-12-31",
        )

        report = {}
        for style in styles:
            cases = expected[style]
            top1 = top3 = wrong = served = 0
            wrong_details = []
            for query, intended_article in cases:
                as_of = "2024-06-01" if style == "date_sensitive" else "2026-06-01"
                hits = self.search(query, as_of=as_of)
                articles = [str(hit["article"]) for hit in hits]
                rank = articles.index(intended_article) + 1 if intended_article in articles else None
                top1 += int(rank == 1)
                top3 += int(rank is not None and rank <= 3)
                if articles and articles[0] != intended_article:
                    wrong += 1
                    wrong_details.append({"query": query, "expected": intended_article, "actual": articles[0], "top3": articles[:3]})
                served += int(bool(hits))
            report[style] = {
                "n": len(cases), "top1": top1, "top3": top3,
                "wrong_article_answers": wrong,
                "refusal_correct": served, "refusal_total": len(cases),
            }
            self.assertEqual(wrong, 0, f"wrong article ranked to answer position for {style}: {json.dumps(wrong_details, ensure_ascii=False)}")
            self.assertEqual(served, len(cases), f"answerable {style} query was refused")

        abstained = 0
        for query in MUST_ABSTAIN:
            hits = self.search(query)
            self.assertEqual(hits, [], f"must-abstain query retrieved a source: {query!r}")
            abstained += 1
        report["must_abstain"] = {
            "n": len(MUST_ABSTAIN), "top1": None, "top3": None,
            "wrong_article_answers": 0,
            "refusal_correct": abstained, "refusal_total": len(MUST_ABSTAIN),
        }
        self.assertEqual(abstained, 8)

        date_query = f"ما القاعدة بشأن {TOPICS['employment'][0][0]} بتاريخ 2024-06-01"
        date_hits = self.search(date_query)
        returned_ids = {hit["id"] for hit in date_hits}
        self.assertNotIn(future_id, returned_ids)
        self.assertNotIn(expired_id, returned_ids)

        total = sum(item["n"] for item in report.values())
        self.assertEqual(total, 200)
        print("FICTIONAL_RETRIEVAL_BENCHMARK=" + json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
