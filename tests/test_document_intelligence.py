"""Tests for conservative Legal Research document-intelligence helpers."""
import unittest

from tools.document_intelligence import (
    classify_document, compare_extracted_text, extract_review_candidates, extract_structured_candidates,
    build_date_mention_timeline, group_candidate_entity_mentions, group_same_matter_duplicates, normalized_text_digest, sha256_bytes,
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
            "[[PDF_PAGE:4]]\n"
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

    def test_event_candidates_preserve_exact_date_and_party_offsets(self):
        text = (
            "[[PDF_PAGE:4]]\\n"
            "المدعي: أحمد محمد، وتحددت جلسة الدعوى بتاريخ 15/03/2025."
        )
        result = extract_structured_candidates(text)
        event = next(item for item in result["events"] if item["trigger"] == "جلسة")
        self.assertEqual(event["page"], 4)
        date_evidence = event["date_evidence"][0]
        party_evidence = event["party_evidence"][0]
        self.assertEqual(text[date_evidence["start"]:date_evidence["end"]], "15/03/2025")
        self.assertEqual(text[party_evidence["start"]:party_evidence["end"]], "المدعي: أحمد محمد")
        self.assertEqual(event["date_mentions"], [date_evidence["mention"]])
        self.assertEqual(event["party_mentions"], [party_evidence["mention"]])

    def test_structured_candidates_link_english_event_date_and_relation(self):
        text = (
            "[[PDF_PAGE:7]]\n"
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

    def test_structured_entity_cap_does_not_let_dates_starve_other_signal_families(self):
        text = (
            "01/01/2025 " * 20
            + "المدعي: أحمد محمد. دعوى رقم 123/2025. المادة 10 من القانون رقم 12 لسنة 2020. "
            + "المبلغ 5000 جنيه."
        )
        result = extract_structured_candidates(text, max_items=10)
        kinds = {item["entity_type"] for item in result["entities"]}
        self.assertTrue({
            "labelled_party", "case_reference", "legal_reference", "monetary_amount", "date_mention"
        }.issubset(kinds))
        self.assertTrue(result["truncated"])

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


    def test_candidate_entity_mentions_group_exact_names_only_within_same_matter(self):
        documents = [
            {"firm_id": "firm-a", "matter_id": "matter-1", "document_id": "doc-1", "filename": "one.pdf",
             "entities": [{"entity_type": "labelled_party", "mention": "Plaintiff: Alice Smith",
                           "name_mention": "Alice Smith", "role_label": "Plaintiff", "page": 2, "chunk_id": 11}]},
            {"firm_id": "firm-a", "matter_id": "matter-1", "document_id": "doc-2", "filename": "two.docx",
             "entities": [{"entity_type": "labelled_party", "mention": "Defendant: alice   smith",
                           "name_mention": "alice   smith", "role_label": "Defendant", "page": None, "chunk_id": 22}]},
            {"firm_id": "firm-a", "matter_id": "matter-2", "document_id": "doc-3", "filename": "three.pdf",
             "entities": [{"entity_type": "labelled_party", "mention": "Plaintiff: Alice Smith",
                           "name_mention": "Alice Smith"}]},
            {"firm_id": "firm-b", "matter_id": "matter-1", "document_id": "doc-4", "filename": "four.pdf",
             "entities": [{"entity_type": "labelled_party", "mention": "Plaintiff: Alice Smith",
                           "name_mention": "Alice Smith"}]},
        ]
        result = group_candidate_entity_mentions(documents)
        self.assertEqual(result["group_count"], 1)
        group = result["groups"][0]
        self.assertEqual(group["document_ids"], ["doc-1", "doc-2"])
        self.assertEqual(group["match_basis"], "exact_nfkc_casefold_whitespace")
        self.assertEqual(group["review_status"], "possible_repeat_mention_requires_human_review")
        self.assertEqual({member["role_label"] for member in group["members"]}, {"Plaintiff", "Defendant"})
        self.assertIn("do not establish identity", result["warning"])

    def test_candidate_entity_grouping_ignores_other_entity_types_and_caps_work(self):
        documents = [{
            "firm_id": "firm-a", "matter_id": "matter-1", "document_id": "doc-1",
            "entities": [
                {"entity_type": "date_mention", "mention": "2025-01-01"},
                {"entity_type": "amount", "mention": "5000 EGP"},
                {"entity_type": "legal_reference", "mention": "Article 10"},
                {"entity_type": "legal_reference", "mention": "Article 11"},
            ],
        }]
        result = group_candidate_entity_mentions(documents, max_candidates=1)
        self.assertEqual(result["groups"], [])
        self.assertEqual(result["candidate_count"], 1)
        self.assertTrue(result["truncated"])

    def test_amount_candidates_normalize_explicit_currency_and_flag_ambiguous_labels(self):
        result = extract_structured_candidates(
            "قيمة المطالبة ١٬٥٠٠٫٢٥ جنيه. ومبلغ آخر 200 ريال. Another amount 1,000.50 USD."
        )
        amounts = [
            item for item in result["entities"]
            if item["entity_type"] == "monetary_amount"
        ]
        egp = next(item for item in amounts if item["currency_label"] == "جنيه")
        ambiguous = next(item for item in amounts if item["currency_label"] == "ريال")
        self.assertEqual(egp["amount_numeric"], "1500.25")
        self.assertEqual(egp["currency_code"], "EGP")
        self.assertEqual(egp["currency_resolution"], "explicit_currency")
        self.assertEqual(ambiguous["amount_numeric"], "200")
        self.assertIsNone(ambiguous["currency_code"])
        self.assertEqual(ambiguous["currency_resolution"], "ambiguous_currency_label")
        usd = next(item for item in amounts if item["currency_code"] == "USD")
        self.assertEqual(usd["amount_numeric"], "1000.5")
        comma_decimal = extract_structured_candidates("المبلغ 5000,50 EGP.")
        self.assertFalse(any(
            item["entity_type"] == "monetary_amount"
            for item in comma_decimal["entities"]
        ))

    def test_case_reference_extraction_supports_english_and_arabic_labels(self):
        text = (
            "Case No. 123/2025. Appeal Number A-17/2024. "
            "الدعوى رقم ٥٠/٢٠٢٤."
        )
        result = extract_review_candidates(text)
        references = [
            item["value"] for item in result["candidates"]
            if item["kind"] == "case_reference"
        ]
        self.assertEqual(
            references,
            ["Case No. 123/2025", "Appeal Number A-17/2024", "الدعوى رقم ٥٠/٢٠٢٤"],
        )

    def test_arabic_and_english_named_month_dates_are_parsed_without_guessing_years(self):
        text = (
            "[[PDF_PAGE:6]]\\n"
            "تحددت جلسة الدعوى بتاريخ ١٥ مارس ٢٠٢٥. "
            "The hearing was listed for March 16, 2025. "
            "A prior note says 15 March 25 and another says 32 مارس 2025."
        )
        extracted = extract_review_candidates(text)
        date_candidates = [item for item in extracted["candidates"] if item["kind"] == "date"]
        timeline = build_date_mention_timeline([{
            "document_id": "doc-6",
            "filename": "named-dates.pdf",
            "candidates": date_candidates,
        }])
        self.assertEqual(
            [item["normalized_date"] for item in timeline["dated_mentions"]],
            ["2025-03-15", "2025-03-16"],
        )
        self.assertEqual(
            {item["date_mention"] for item in timeline["unparsed_mentions"]},
            {"15 March 25", "32 مارس 2025"},
        )
        self.assertTrue(all(item["page"] == 6 for item in timeline["dated_mentions"]))

    def test_hijri_date_mentions_are_preserved_as_unconverted(self):
        text = "[[PDF_PAGE:9]]\\nتاريخ المحضر ١٥ رمضان ١٤٤٦هـ."
        extracted = extract_review_candidates(text)
        date_candidates = [item for item in extracted["candidates"] if item["kind"] == "date"]
        self.assertEqual(len(date_candidates), 1)
        timeline = build_date_mention_timeline([{
            "document_id": "hijri-doc",
            "filename": "hijri-note.pdf",
            "candidates": date_candidates,
        }])
        self.assertEqual(timeline["dated_mentions"], [])
        self.assertEqual(len(timeline["unparsed_mentions"]), 1)
        item = timeline["unparsed_mentions"][0]
        self.assertEqual(item["calendar_system"], "hijri")
        self.assertEqual(item["interpretation"], "hijri_unconverted")
        self.assertIsNone(item["normalized_date"])
        self.assertEqual(item["page"], 9)

    def test_timeline_sorts_date_mentions_and_keeps_document_provenance(self):
        documents = [
            {"document_id": "doc-b", "filename": "second.pdf", "candidates": [
                {"kind": "date", "value": "١٥/٠٣/٢٠٢٥", "page": 4, "chunk_id": 41, "chunk_ref": "chunk-41", "start": 10, "end": 20, "excerpt": "تاريخ الجلسة"}
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
        self.assertEqual(result["dated_mentions"][1]["chunk_id"], 41)
        self.assertEqual(result["dated_mentions"][1]["chunk_ref"], "chunk-41")
        self.assertEqual(result["dated_mentions"][1]["start"], 10)
        self.assertEqual(result["dated_mentions"][1]["end"], 20)
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
