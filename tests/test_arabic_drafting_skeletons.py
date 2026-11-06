import unittest

from tools.arabic_drafting_skeletons import DRAFT_WARNING_AR, build_arabic_skeleton


class ArabicDraftingSkeletonTests(unittest.TestCase):
    def test_memorandum_contains_case_data_and_headings_only(self):
        output = build_arabic_skeleton({
            "court": "محكمة القاهرة الاقتصادية",
            "circuit": "الدائرة الثالثة",
            "case_number": "123",
            "case_year": "2026",
            "client": "شركة افتراضية",
            "opposing_party": "خصم افتراضي",
            "title": "نزاع تعاقدي",
        })
        self.assertIn(DRAFT_WARNING_AR, output)
        self.assertIn("محكمة القاهرة الاقتصادية", output)
        self.assertIn("123", output)
        self.assertIn("أولاً: موجز الوقائع", output)
        self.assertIn("ثالثاً: الأسانيد القانونية", output)
        self.assertIn("خامساً: الطلبات", output)
        self.assertNotIn("وحيث إن", output)
        self.assertNotIn("لذلك نلتمس", output)

    def test_missing_case_values_are_explicit_placeholders(self):
        output = build_arabic_skeleton({})
        self.assertIn("المحكمة: يُستكمل", output)
        self.assertIn("الموكل: يُستكمل", output)

    def test_pleading_has_separate_headings(self):
        output = build_arabic_skeleton({"case_number": "9"}, "pleading")
        self.assertIn("صحيفة دعوى", output)
        self.assertIn("ثالثاً: الطلبات", output)
        self.assertNotIn("أوجه الدفاع والرد", output)

    def test_rejects_unknown_template_and_non_mapping(self):
        with self.assertRaises(ValueError):
            build_arabic_skeleton({}, "contract")
        with self.assertRaises(TypeError):
            build_arabic_skeleton(None)

    def test_case_data_cannot_inject_new_lines(self):
        output = build_arabic_skeleton({"court": "محكمة\nخامساً: طلبات مزيفة"})
        self.assertNotIn("\\nخامساً: طلبات مزيفة\\n", output)
        self.assertIn("المحكمة: محكمة خامساً: طلبات مزيفة", output)


if __name__ == "__main__":
    unittest.main()
