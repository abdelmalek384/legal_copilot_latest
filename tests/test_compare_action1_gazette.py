import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.compare_action1_gazette import (
    build_report, compare_articles, load_article_candidates, normalize_arabic_text,
)


class Action1GazetteComparisonTests(unittest.TestCase):
    def test_normalization_handles_arabic_digits_diacritics_and_layout_whitespace(self):
        self.assertEqual(
            normalize_arabic_text("أَلْمَادَّةُ ١ ـ العمل\n  واجب"),
            normalize_arabic_text("المادة 1 العمل واجب"),
        )

    def test_full_article_match_can_span_multiple_pdf_pages(self):
        candidate = {
            "law": "قانون العمل",
            "article": "1",
            "text": normalize_arabic_text("المادة 1 نطاق القانون ينظم هذا القانون علاقات العمل"),
            "text_sha256": "a" * 64,
            "normalized_character_count": 50,
            "source_chunk_count": 2,
        }
        report = compare_articles(
            [candidate],
            ["مقدمة المادة ١ نطاق القانون ينظم", "هذا القانون علاقات العمل خاتمة"],
        )
        result = report["matches"][0]
        self.assertEqual(result["status"], "exact_text_match")
        self.assertEqual(result["pdf_page_indices_zero_based"], [0, 1])
        self.assertEqual(report["match_counts"]["exact_text_match"], 1)

    def test_duplicate_exact_occurrences_are_not_silently_treated_as_unique(self):
        text = normalize_arabic_text("المادة 2 نص تجريبي للمطابقة")
        candidate = {
            "law": "قانون",
            "article": "2",
            "text": text,
            "text_sha256": "b" * 64,
            "normalized_character_count": len(text),
            "source_chunk_count": 1,
        }
        report = compare_articles([candidate], [text, text])
        self.assertEqual(report["matches"][0]["status"], "exact_text_match_multiple_occurrences")
        self.assertEqual(report["matches"][0]["pdf_page_indices_zero_based"], [0, 1])

    def test_partial_anchors_are_not_reported_as_exact_matches(self):
        text = normalize_arabic_text("المادة 3 " + "نص قانوني تجريبي " * 20 + " نهاية المادة")
        candidate = {
            "law": "قانون",
            "article": "3",
            "text": text,
            "text_sha256": "c" * 64,
            "normalized_character_count": len(text),
            "source_chunk_count": 1,
        }
        report = compare_articles([candidate], ["مقدمة " + text[:120] + " نص مختلف في منتصف المادة"])
        self.assertEqual(report["matches"][0]["status"], "start_anchor_only")
        self.assertNotEqual(report["matches"][0]["status"], "exact_text_match")

    def test_grouping_concatenates_chunks_without_exposing_text(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "law_rows_ar.jsonl"
            path.write_text(
                '{"law":"قانون العمل","article":"1","text":"الجزء الأول"}\n'
                '{"law":"قانون العمل","article":"1","text":"الجزء الثاني"}\n'
                '{"law":"قانون العمل","article":"2","text":"المادة الثانية"}\n',
                encoding="utf-8",
            )
            candidates, digest = load_article_candidates(path)
            self.assertEqual(len(candidates), 2)
            self.assertEqual(candidates[0]["source_chunk_count"], 2)
            self.assertEqual(len(digest), 64)
            self.assertNotIn("الجزء الأول", json.dumps(candidates))

    def test_invalid_jsonl_and_non_object_rows_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.jsonl"
            path.write_text('{"law":"قانون","article":1,"text":"نص"}\nnot-json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2 is invalid JSON"):
                load_article_candidates(path)
            path.write_text('[]\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 1 must be an object"):
                load_article_candidates(path)

    def test_report_is_metadata_only_and_never_promotes_legal_status(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pdf = root / "gazette.pdf"
            pdf.write_bytes(b"%PDF-1.7\nfixture")
            rows = root / "law_rows_ar.jsonl"
            rows.write_text(
                '{"law":"قانون العمل","article":"1","text":"نص المادة السرّي"}\n',
                encoding="utf-8",
            )
            with patch(
                "tools.compare_action1_gazette.read_pdf_text",
                return_value=(["نص المادة السرّي"], "d" * 64),
            ):
                report = build_report(pdf, rows)
            serialized = json.dumps(report, ensure_ascii=False)
            self.assertNotIn("نص المادة السرّي", serialized)
            self.assertFalse(report["comparison"]["safety_boundary"]["legal_authenticity_verified"])
            self.assertFalse(report["comparison"]["safety_boundary"]["currentness_or_amendment_status_verified"])
            self.assertFalse(report["comparison"]["safety_boundary"]["retrieval_eligible"])

    def test_no_text_layer_is_a_distinct_result_not_a_failed_legal_match(self):
        candidate = {
            "law": "قانون",
            "article": "1",
            "text": "المادة 1 نص",
            "text_sha256": "e" * 64,
            "normalized_character_count": 10,
            "source_chunk_count": 1,
        }
        report = compare_articles([candidate], ["", "  "])
        self.assertEqual(report["matches"][0]["status"], "no_pdf_text_layer")
        self.assertEqual(report["match_counts"]["no_pdf_text_layer"], 1)


if __name__ == "__main__":
    unittest.main()
