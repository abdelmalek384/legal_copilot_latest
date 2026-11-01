"""Regression tests for Arabic query expansion and preliminary conflict-name matching."""
import unittest

from app import SYS, conflict_name_matches, expanded_tokens, matched_surface_terms, tokens
from tools.arabic_legal_matching import orthographic_variants


class ArabicMatchingTests(unittest.TestCase):
    def test_model_prompt_handles_egyptian_arabic_without_treating_synonyms_as_evidence(self):
        self.assertIn("Egyptian Arabic", SYS)
        self.assertIn("retrieval hints", SYS)
        self.assertIn("exact formal statutory wording", SYS)
        self.assertIn("ask a focused clarification", SYS)

    def test_article_prefix_and_accusative_alif_variant_are_query_expanded(self):
        query = expanded_tokens("الشيك")
        self.assertIn("شيك", query)
        self.assertIn("شيكا", query)

    def test_delay_derivation_variants_are_query_expanded(self):
        query = expanded_tokens("التأخير")
        # Retrieval tokens use the same canonical form as norm()/tokens():
        # hamza-bearing alef variants are normalized, not preserved as separate IDs.
        self.assertIn(tokens("تأخير")[0], query)
        self.assertIn(tokens("تأخر")[0], query)
        self.assertEqual(tokens("تأخير"), tokens("تاخير"))

    def test_matched_surface_terms_highlight_retrieved_arabic_variants(self):
        self.assertIn("شيكا", matched_surface_terms("حرر المدين شيكا للمستفيد", expanded_tokens("الشيك")))
        self.assertIn("تأخر", matched_surface_terms("عند تأخر المدين في السداد", expanded_tokens("التأخير")))

    def test_selected_egyptian_colloquial_legal_queries_expand_conservatively(self):
        wage = expanded_tokens("المرتب")
        self.assertIn(tokens("أجر")[0], wage)
        self.assertIn(tokens("راتب")[0], wage)

        dismissal = expanded_tokens("اترفدت")
        self.assertIn(tokens("فصل")[0], dismissal)
        self.assertIn(tokens("إنهاء الخدمة")[0], dismissal)

        cheque = expanded_tokens("شيك مرتجع")
        self.assertIn(tokens("شيك")[0], cheque)
        self.assertIn(tokens("مرفوض")[0], cheque)

        trust_receipt = expanded_tokens("وصل أمانة")
        self.assertIn(tokens("إيصال")[0], trust_receipt)

        family_support = expanded_tokens("مصاريف العيال")
        self.assertIn(tokens("نفقة")[0], family_support)

    def test_phrase_level_egyptian_colloquial_queries_expand_to_legal_retrieval_hints(self):
        cases = (
            ("صاحب الشغل مش بيدفع المرتب", ("صاحب العمل", "عدم سداد الأجر", "الأجر المتأخر")),
            ("المرتب متأخر", ("تأخر صرف الأجر", "مستحقات العامل")),
            ("طردني من الشغل", ("فصل العامل", "إنهاء الخدمة")),
            ("الشيك رجع", ("شيك مرتجع", "شيك مرفوض")),
            ("مفيش رصيد", ("بدون رصيد", "شيك مرتجع")),
            ("وصل أمانة", ("إيصال أمانة",)),
            ("صاحب البيت", ("المؤجر", "مالك العقار")),
            ("عايز يطردني", ("الإخلاء", "إخلاء المستأجر")),
            ("مصاريف العيال", ("نفقة الصغار", "نفقة الأولاد")),
            ("جوزي مش بيصرف", ("نفقة الزوجة", "الامتناع عن الإنفاق")),
            ("عايز أرفع قضية", ("رفع دعوى", "صحيفة الدعوى")),
            ("حد نصب عليا", ("احتيال", "استرداد المبالغ")),
            ("فلوسي عند حد", ("دين", "مطالبة مالية")),
            ("مش عارف أفسخ العقد", ("فسخ العقد", "إنهاء العقد")),
        )
        for question, expected_phrases in cases:
            with self.subTest(question=question):
                expanded = set(expanded_tokens(question))
                for phrase in expected_phrases:
                    self.assertTrue(
                        set(tokens(phrase)).issubset(expanded),
                        f"{question!r} did not expand to {phrase!r}",
                    )

    def test_extended_egyptian_colloquial_phrases_expand_across_practice_areas(self):
        cases = (
            ("المرتب مش نازل", ("عدم صرف الأجر", "الأجر المتأخر")),
            ("خصموا من مرتبي", ("خصم الأجر", "الاستقطاع من الأجر")),
            ("شغال من غير عقد", ("إثبات علاقة العمل", "عقد العمل")),
            ("فصلوني تعسفي", ("الفصل التعسفي", "التعويض عن الفصل")),
            ("اشتغلت إضافي ومخدتش فلوس", ("ساعات العمل الإضافية", "مقابل العمل الإضافي")),
            ("مأمنوش عليا", ("التأمين الاجتماعي", "التأمينات الاجتماعية")),
            ("صاحب البيت عايز يطردني", ("إخلاء المستأجر", "دعوى الإخلاء")),
            ("الإيجار زاد عليا", ("زيادة الأجرة", "القيمة الإيجارية")),
            ("مش بيرجعلي التأمين", ("رد التأمين", "المطالبة المالية")),
            ("مديونلي ومش بيدفع", ("الوفاء بالدين", "المطالبة بالدين")),
            ("باعلي حاجة مضروبة", ("العيب الخفي", "ضمان العيوب")),
            ("عملت توكيل وعايز ألغيه", ("إلغاء التوكيل", "عزل الوكيل")),
            ("الحكم غيابي", ("الحكم الغيابي", "المعارضة في الحكم")),
            ("وصلني إنذار", ("الإنذار الرسمي", "إجراءات الإعلان")),
            ("مش بيدفع نفقة", ("الامتناع عن سداد النفقة", "تنفيذ حكم النفقة")),
            ("عايزة أخلع", ("دعوى الخلع", "إجراءات الخلع")),
            ("ورث ومش راضي يوزع", ("قسمة التركة", "حقوق الورثة")),
            ("حد نصب عليا أونلاين", ("الاحتيال الإلكتروني", "جرائم تقنية المعلومات")),
            ("العربية اتخبطت", ("حادث سيارة", "التعويض عن حوادث السيارات")),
            ("عملولي محضر", ("تحرير محضر", "محضر الشرطة")),
            ("اتعمل ضدي محضر", ("محضر الشرطة", "التحقيق الجنائي")),
            ("الشرطة استدعتني", ("استدعاء الشرطة", "سماع الأقوال")),
            ("اتقبض عليا", ("القبض", "ضمانات القبض")),
            ("اتحبست", ("الحبس الاحتياطي", "ضمانات المتهم")),
            ("عايز أعمل محضر", ("تحرير محضر", "تقديم بلاغ")),
            ("اتظلمت من قرار", ("التظلم من القرار الإداري", "القرار الإداري")),
            ("الجهة رفضت طلبي", ("رفض الطلب", "التظلم الإداري")),
            ("مش عارف آخد ورثي", ("قسمة التركة", "حقوق الورثة")),
            ("اخواتي مش بيدوني حقي في الورث", ("قسمة التركة", "دعوى القسمة")),
            ("الشركة مخصمتليش التأمينات", ("اشتراكات التأمين الاجتماعي", "التأمينات الاجتماعية")),
            ("مضوني على استقالة", ("الاستقالة", "صحة الاستقالة")),
            ("مضوني على ورق", ("الإكراه", "صحة المحررات")),
            ("عايز أفسخ عقد الإيجار", ("فسخ عقد الإيجار", "إنهاء عقد الإيجار")),
            ("مش بيرجعلي فلوسي", ("رد المبالغ", "دعوى المطالبة")),
        )
        for question, expected_phrases in cases:
            with self.subTest(question=question):
                expanded = set(expanded_tokens(question))
                for phrase in expected_phrases:
                    self.assertTrue(
                        set(tokens(phrase)).issubset(expanded),
                        f"{question!r} did not expand to {phrase!r}",
                    )

    def test_extended_colloquial_expansion_keeps_negation_and_original_query_terms(self):
        for question in ("مش بيدفعلي مرتبي", "مش راضي يطلع من الشقة", "مش بيدفع نفقة"):
            expanded = expanded_tokens(question)
            self.assertTrue(set(tokens(question)).issubset(set(expanded)))
            self.assertTrue(any(token in expanded for token in tokens("مش")))

    def test_separate_lexicon_covers_missing_labour_and_legacy_rent_phrases(self):
        cases = (
            ("فصلني من الشغل", ("فصل العامل", "إنهاء عقد العمل")),
            ("عايز إجازة", ("إجازة سنوية", "الإجازة السنوية")),
            ("الإيجار القديم", ("العلاقة الإيجارية القديمة", "امتداد عقد الإيجار")),
        )
        for question, expected_phrases in cases:
            with self.subTest(question=question):
                expanded = set(expanded_tokens(question))
                for phrase in expected_phrases:
                    self.assertTrue(
                        set(tokens(phrase)).issubset(expanded),
                        f"{question!r} did not expand to {phrase!r}",
                    )

    def test_orthographic_variants_are_narrow_and_symmetric(self):
        self.assertEqual(orthographic_variants("اجازة"), ("اجازة", "اجازه"))
        self.assertEqual(orthographic_variants("اجازه"), ("اجازه", "اجازة"))
        self.assertEqual(orthographic_variants("عامل"), ("عامل",))

    def test_lexicon_expansion_preserves_negation_and_original_query_terms(self):
        question = "فصلني ومش عايز إجازة"
        expanded = expanded_tokens(question)
        self.assertTrue(set(tokens(question)).issubset(set(expanded)))
        self.assertIn(tokens("مش")[0], expanded)

    def test_phrase_expansion_preserves_original_terms_and_negation(self):
        question = "صاحب الشغل مش بيدفع المرتب"
        expanded = expanded_tokens(question)
        self.assertTrue(set(tokens(question)).issubset(set(expanded)))
        self.assertIn(tokens("مش")[0], expanded)
        self.assertEqual(expanded_tokens(question), expanded_tokens(question))

    def test_phrase_expansion_requires_word_boundaries(self):
        self.assertNotIn(tokens("المؤجر")[0], expanded_tokens("صاحب البيتزا"))

    def test_colloquial_expansion_only_highlights_actual_source_words(self):
        query = expanded_tokens("اترفدت")
        self.assertIn("فصل", matched_surface_terms("تم فصل العامل من العمل", query))
        self.assertNotIn("اترفدت", matched_surface_terms("تم فصل العامل من العمل", query))

    def test_matched_surface_terms_preserve_diacritics_for_highlighting(self):
        self.assertIn("شيكًا", matched_surface_terms("حرر المدين شيكًا للمستفيد", expanded_tokens("الشيك")))

    def test_matched_surface_terms_are_bounded_and_deduplicated(self):
        terms = matched_surface_terms("شيكا شيكا شيكا", expanded_tokens("الشيك"), limit=2)
        self.assertEqual(terms, ["شيكا"])

    def test_arabic_diacritics_and_tatweel_do_not_break_query_matching(self):
        self.assertEqual(tokens("الشَّيْك"), tokens("الشـيك"))
        self.assertEqual(tokens("الشَّيْك"), tokens("الشيك"))

    def test_legal_negation_tokens_are_not_removed_as_stopwords(self):
        self.assertIn("لا", tokens("لا يجوز"))
        self.assertIn("لم", tokens("لم يسدد"))

    def test_arabic_case_search_keeps_the_surface_text_unchanged(self):
        self.assertEqual(tokens("الشيك"), ["شيك"])
        # Expansion is for retrieval only; it does not rewrite document evidence.
        self.assertIn("شيكا", expanded_tokens("الشيك"))

    def test_conflict_name_match_ignores_repeated_whitespace_and_word_order(self):
        self.assertTrue(conflict_name_matches("عمر فتحي", "فتحي  عمر"))

    def test_conflict_name_match_ignores_common_company_descriptor(self):
        self.assertTrue(conflict_name_matches("شركة النيل", "النيل"))
        self.assertTrue(conflict_name_matches("النيل", "شركة النيل للتوريدات"))

    def test_generic_descriptor_alone_does_not_match_every_company(self):
        self.assertFalse(conflict_name_matches("شركة", "شركة النيل"))
        self.assertFalse(conflict_name_matches("شركة", "شركة أخرى"))

    def test_empty_names_never_match(self):
        self.assertFalse(conflict_name_matches("", "عمر فتحي"))
        self.assertFalse(conflict_name_matches("عمر فتحي", ""))


if __name__ == "__main__":
    unittest.main()
