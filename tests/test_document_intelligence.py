"""Tests for conservative Legal Research document-intelligence helpers."""
import unittest

from tools.document_intelligence import (
    classify_document, compare_extracted_text, extract_review_candidates, extract_structured_candidates,
    build_date_mention_timeline, group_same_matter_duplicates, normalized_text_digest, sha256_bytes,
)


class DocumentIntelligenceTests(unittest.TestCase):
    def test_classification_is_transparent_and_never_auto_approved(self):
        result = classify_document("judgment.pdf", "حكم المحكمة في الدعوى")
        self.assertEqual(result["category"], "court_judgment")
        self.assertEqual(result["signal_strength"], "multiple_keyword_matches")
        self.assertTrue(result["requires_review"])
        self.assertIn("حكم", result["matched_terms"])

    def test_unknown_document_remains_unclassified(self):
        result = classify_document("scan.pdf", "نص غير واضح")
        self.assertEqual(result["category"], "unclassified")
        self.assertEqual(result["signal_strength"], "no_keyword_match")
        self.assertTrue(result["requires_review"])

    def test_extracts_literal_candidates_with_pdf_page_provenance(self):
        text = ("[[PDF_PAGE:3]]\nدعوى رقم ١٢٣/٢٠٢٥ بتاريخ ١٥/٠٣/٢٠٢٥. "
                "المدعي: أحمد محمد. والمبلغ ٥٠٠٠ جنيه.")
        result = extract_review_candidates(text)
        by_kind = {}
        for item in result["candidates"]:
            by_kind.setdefault(item["kind"], []).append(item)
            self.assertEqual(item["page"], 3)
            self.assertEqual(item["review_status"], "candidate_unverified")
            self.assertTrue(item["excerpt"])
        self.assertIn("case_reference", by_kind)
        self.assertIn("date", by_kind)
        self.assertIn("amount", by_kind)
        self.assertIn("party_label", by_kind)

    def test_docx_style_text_has_no_invented_page_number(self):
        result = extract_review_candidates("عقد بتاريخ 2025-04-03")
        self.assertTrue(result["candidates"])
        self.assertTrue(all(item["page"] is None for item in result["candidates"]))

    def test_text_size_is_bounded(self):
        with self.assertRaises(ValueError):
            extract_review_candidates("x" * 1_000_001)

    def test_exact_bytes_and_normalized_text_have_separate_hash_helpers(self):
        self.assertNotEqual(sha256_bytes(b"a\nb"), sha256_bytes(b"a b"))
        self.assertEqual(normalized_text_digest("a\nb"), normalized_text_digest("a  b"))

    def test_structured_candidates_link_entities_events_and_explicit_arabic_relationships(self):
        text = (
            "[[PDF_PAGE:4]]\\n"
            "المدعي: أحمد محمد. أحمد محمد وكيل عن شركة النور، وتحددت جلسة الدعوى بتاريخ 15/03/2025."
        )
        result = extract_structured_candidates(text)
        self.assertTrue(result["requires_review"])
        self.assertTrue(any(
            item["entity_type"] == "labelled_party" and item["name_mention"] == "أحمد محمد"
            for item in result["entities"]
        ))
        self.assertTrue(any(
            item["trigger"] == "جلسة"
            and "15/03/2025" in item["date_mentions"]
            and item["page"] == 4
            for item in result["events"]
        ))
        self.assertTrue(any(
            item["subject_mention"] == "أحمد محمد"
            and item["relation_mention"] == "وكيل عن"
            and item["object_mention"] == "شركة النور"
            and item["page"] == 4
            for item in result["relationships"]
        ))
        self.assertTrue(all(
            item["review_status"].endswith("unverified") or "requires_human_context" in item["review_status"]
            for group in ("entities", "events", "relationships")
            for item in result[group]
        ))

    def test_structured_candidates_link_english_event_date_and_relation(self):
        text = (
            "[[PDF_PAGE:7]]\\n"
            "Alice Smith represents Northwind LLC. The hearing occurred on 2025-03-15."
        )
        result = extract_structured_candidates(text)
        self.assertTrue(any(
            item["subject_mention"] == "Alice Smith"
            and item["relation_mention"] == "represents"
            and item["object_mention"] == "Northwind LLC"
            for item in result["relationships"]
        ))
        self.assertTrue(any(
            item["trigger"].lower() == "hearing"
            and "2025-03-15" in item["date_mentions"]
            and item["page"] == 7
            for item in result["events"]
        ))

    def test_structured_candidates_do_not_infer_relationships_or_events_from_unrelated_sentences(self):
        result = extract_structured_candidates(
            "Alice Smith signed a letter. The unrelated hearing occurred later."
        )
        self.assertEqual(result["relationships"], [])
        self.assertTrue(all(not item["date_mentions"] for item in result["events"]))

    def test_structured_candidate_limit_is_enforced(self):
        result = extract_structured_candidates(
            "جلسة 01/01/2025. " * 30, max_items=3
        )
        self.assertLessEqual(len(result["entities"]), 3)
        self.assertLessEqual(len(result["events"]), 3)
        self.assertLessEqual(len(result["relationships"]), 3)

    def test_comparison_reports_literal_changes_for_review(self):
        changes = compare_extracted_text("قيمة العقد ١٠٠٠ جنيه", "قيمة العقد ٢٠٠٠ جنيه")
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["change_type"], "replace")
        self.assertIn("١٠٠٠", changes[0]["before"])
        self.assertIn("٢٠٠٠", changes[0]["after"])
        self.assertEqual(changes[0]["review_status"], "requires_lawyer_review")

    def test_comparison_rejects_invalid_context(self):
        with self.assertRaises(ValueError):
            compare_extracted_text("a", "b", context_chars=-1)

    def test_comparison_has_a_separate_cpu_bound(self):
        with self.assertRaises(ValueError):
            compare_extracted_text("a" * 100_001, "b")


    def test_timeline_sorts_date_mentions_and_keeps_document_provenance(self):
        documents = [
            {"document_id": "doc-b", "filename": "second.pdf", "candidates": [
                {"kind": "date", "value": "١٥/٠٣/٢٠٢٥", "page": 4, "excerpt": "تاريخ الجلسة"}
            ]},
            {"document_id": "doc-a", "filename": "first.docx", "candidates": [
                {"kind": "date", "value": "2025-01-02", "page": None, "excerpt": "تاريخ العقد"}
            ]},
        ]
        result = build_date_mention_timeline(documents)
        self.assertEqual([x["normalized_date"] for x in result["dated_mentions"]],
                         ["2025-01-02", "2025-03-15"])
        self.assertEqual(result["dated_mentions"][1]["document_id"], "doc-b")
        self.assertEqual(result["dated_mentions"][1]["page"], 4)
        self.assertEqual(result["dated_mentions"][1]["review_status"],
                         "date_mention_requires_human_context")

    def test_timeline_does_not_guess_two_digit_years_or_invalid_dates(self):
        documents = [{"document_id": "doc", "filename": "x.pdf", "candidates": [
            {"kind": "date", "value": "01/02/25"},
            {"kind": "date", "value": "31/02/2025"},
        ]}]
        result = build_date_mention_timeline(documents)
        self.assertEqual(result["dated_mentions"], [])
        self.assertEqual(len(result["unparsed_mentions"]), 2)

    def test_timeline_requires_document_scope_identity(self):
        with self.assertRaises(ValueError):
            build_date_mention_timeline([{"filename": "x.pdf", "candidates": []}])


    def test_duplicate_groups_are_scoped_to_same_firm_and_matter(self):
        digest = "a" * 64
        documents = [
            {"firm_id": "firm-a", "matter_id": "matter-1", "document_id": "doc-1",
             "original_sha256": digest},
            {"firm_id": "firm-a", "matter_id": "matter-1", "document_id": "doc-2",
             "original_sha256": digest},
            {"firm_id": "firm-b", "matter_id": "matter-1", "document_id": "doc-3",
             "original_sha256": digest},
            {"firm_id": "firm-a", "matter_id": "matter-2", "document_id": "doc-4",
             "original_sha256": digest},
        ]
        groups = group_same_matter_duplicates(documents)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["firm_id"], "firm-a")
        self.assertEqual(groups[0]["matter_id"], "matter-1")
        self.assertEqual(groups[0]["document_ids"], ["doc-1", "doc-2"])
        self.assertEqual(groups[0]["review_status"], "possible_duplicate_requires_review")

    def test_duplicate_group_rejects_invalid_hash(self):
        with self.assertRaises(ValueError):
            group_same_matter_duplicates([{
                "firm_id": "firm", "matter_id": "matter", "document_id": "doc",
                "original_sha256": "not-a-hash",
            }])


    def test_extracts_legal_references_and_event_mentions_as_unverified_candidates(self):
        result = extract_review_candidates(
            "المادة ١٠١ من القانون رقم ١٢ لسنة ٢٠٢٠. تحددت جلسة الدعوى."
        )
        kinds = {item["kind"] for item in result["candidates"]}
        self.assertIn("legal_reference", kinds)
        self.assertIn("event_mention", kinds)
        self.assertTrue(all(item["review_status"] == "candidate_unverified" for item in result["candidates"]))

    def test_candidate_extraction_enforces_a_hard_result_limit(self):
        result = extract_review_candidates("01/01/2025 " * 300, max_candidates=10)
        self.assertEqual(result["candidate_count"], 10)
        self.assertEqual(len(result["candidates"]), 10)
        self.assertTrue(result["truncated"])

    def test_candidate_limit_rejects_invalid_values(self):
        for value in (0, -1, 1001, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    extract_review_candidates("text", max_candidates=value)


if __name__ == "__main__":
    unittest.main()
