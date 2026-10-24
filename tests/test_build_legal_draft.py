import unittest
from tools.build_legal_draft import render_draft

def good_source(**overrides):
    source = {
        "title": "قانون افتراضي للاختبار", "citation": "المادة ١",
        "url": "https://example.org/law", "lawyer_approved": True,
        "legal_status": "in_force", "status_verified": True,
        "permission_status": "allowed", "effective_date": "2020-01-01",
        "reviewed_at": "2025-01-01", "repeal_date": None,
    }
    source.update(overrides)
    return source

def payload(**overrides):
    result = {
        "draft_type": "defense_memo", "as_of_date": "2025-06-01",
        "case": {"court": "محكمة الاختبار", "case_number": "١٢/٢٠٢٥"},
        "facts": ["واقعة قدمها المحامي"], "lawyer_arguments": ["دفع صاغه المحامي"],
        "requests": ["رفض الدعوى"], "missing_information": ["صورة رسمية من المستند"],
        "sources": [good_source()],
    }
    result.update(overrides)
    return result

class DraftBuilderTests(unittest.TestCase):
    def test_renders_supplied_material_and_reviewable_source(self):
        result = render_draft(payload())
        self.assertIn("واقعة قدمها المحامي", result)
        self.assertIn("دفع صاغه المحامي", result)
        self.assertIn("[S1]", result)
        self.assertIn("مسودة عمل غير معتمدة للإيداع", result)
        self.assertIn("صورة رسمية من المستند", result)

    def test_unreviewed_or_unpermitted_sources_are_not_cited(self):
        sources = [
            good_source(lawyer_approved=False), good_source(legal_status="unknown"),
            good_source(status_verified=False), good_source(permission_status="unknown"),
            good_source(permission_status="prohibited"),
        ]
        result = render_draft(payload(sources=sources))
        self.assertNotIn("[S1]", result)
        self.assertIn("لم تُقدَّم مصادر تستوفي", result)

    def test_date_boundaries_exclude_future_and_repealed_sources(self):
        result = render_draft(payload(sources=[
            good_source(effective_date="2026-01-01"),
            good_source(repeal_date="2025-06-01"),
            good_source(reviewed_at="2025-06-02"),
        ]))
        self.assertNotIn("[S1]", result)
        self.assertNotIn("[S2]", result)
        self.assertNotIn("[S3]", result)

    def test_missing_fields_become_explicit_placeholders(self):
        result = render_draft(payload(case={}, facts=[], lawyer_arguments=[], requests=[], missing_information=[]))
        self.assertIn("تُحدد المحكمة والدائرة", result)
        self.assertIn("تُستكمل الوقائع من المحامي", result)
        self.assertIn("تُحدد الطلبات الختامية بمعرفة المحامي", result)

    def test_invalid_type_or_date_rejected(self):
        with self.assertRaises(ValueError):
            render_draft(payload(draft_type="anything"))
        with self.assertRaises(ValueError):
            render_draft(payload(as_of_date="not-a-date"))

    def test_claim_form_uses_requested_title(self):
        result = render_draft(payload(draft_type="statement_of_claim"))
        self.assertIn("# صحيفة دعوى", result)

if __name__ == "__main__":
    unittest.main()
