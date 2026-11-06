"""Tests for the reviewed-label-only Arabic retrieval scorer."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.score_arabic_retrieval import benchmark_fingerprint, score


def reviewed(qid, *, answerable=True, article="LABOUR-ART-1", style="formal", tags=None):
    return {
        "id": qid,
        "question_style": style,
        "question_style_review_status": "lawyer_approved",
        "retrieval_tags": tags or [],
        "retrieval_tags_review_status": "lawyer_approved",
        "review_status": "lawyer_reviewed",
        "label_status": "lawyer_approved",
        "reviewer_id": "reviewer-test-1",
        "reviewer_role": "egyptian_lawyer",
        "lawyer_approved_answer": "Approved test answer.",
        "answerable": answerable,
        "expected_article": article if answerable else None,
        "must_abstain_if_unverified": True,
        "reviewer_name": "Test Reviewer",
        "review_date": "2026-11-05",
        "review_evidence_url": "https://example.gov.eg/review-record",
    }


class ArabicRetrievalScorerTests(unittest.TestCase):
    def test_benchmark_fingerprint_survives_counsel_labeling_but_detects_prompt_edits(self):
        q = {
            "id": "Q1", "practice_area": "labour", "question_ar": "سؤال تجريبي",
            "question_origin": "curated_candidate_not_user_observed",
            "expected_article": None, "expected_article_id": None,
            "lawyer_approved_answer": None, "review_status": "needs_lawyer_review",
            "label_status": "unlabeled", "question_style": "colloquial",
            "question_style_review_status": "needs_lawyer_review",
            "retrieval_tags": ["synonym"], "retrieval_tags_review_status": "needs_lawyer_review",
        }
        before = benchmark_fingerprint([q])
        labeled = dict(q)
        labeled.update({
            "expected_article": "المادة 12",
            "expected_article_id": "EG-LABOUR-14-2025::law:قانون العمل رقم 14 لسنة 2025 [block 1]::article:12",
            "lawyer_approved_answer": "إجابة معتمدة للاختبار",
            "review_status": "lawyer_reviewed",
            "label_status": "lawyer_approved",
            "question_style_review_status": "lawyer_approved",
            "retrieval_tags_review_status": "lawyer_approved",
        })
        self.assertEqual(before, benchmark_fingerprint([labeled]))
        edited = dict(labeled, question_ar="سؤال مختلف")
        self.assertNotEqual(before, benchmark_fingerprint([edited]))

    def test_unlabeled_rows_and_their_captured_runs_are_excluded_and_metrics_are_null(self):
        q = {"id": "Q1", "review_status": "needs_lawyer_review", "expected_article": None}
        run = {"question_id": "Q1", "retrieved_article_ids": ["EG-LAW::article:1"],
               "cited_article_ids": [], "abstained": True}
        result = score([q], [run])
        self.assertEqual(result["reviewed_questions"], 0)
        self.assertEqual(result["unlabeled_or_unreviewed_excluded"], 1)
        self.assertEqual(result["unlabeled_run_records_excluded"], 1)
        self.assertIsNone(result["top3_hit_rate"])
        self.assertIsNone(result["wrong_article_rate"])
        self.assertIsNone(result["abstention_rate"])

    def test_correct_colloquial_article_is_a_top3_hit_with_zero_wrong_article_rate(self):
        q = reviewed("Q1", style="colloquial")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-ART-1", "LABOUR-ART-2"],
               "cited_article_ids": ["LABOUR-ART-1"], "abstained": False}
        result = score([q], [run])
        self.assertEqual(result["top3_hit_rate"], 1.0)
        self.assertEqual(result["top3_hit_rate_colloquial"], 1.0)
        self.assertEqual(result["top3_hit_rate_colloquial_or_synonym"], 1.0)
        self.assertEqual(result["wrong_article_rate"], 0.0)

    def test_unverified_source_citation_blocks_target_even_when_article_id_matches(self):
        q = reviewed("Q1", style="colloquial", tags=["synonym"])
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-ART-1"],
               "cited_article_ids": ["LABOUR-ART-1"], "abstained": False,
               "used_unverified_source": True}
        result = score([q], [run])
        self.assertEqual(result["wrong_article_rate"], 0.0)
        self.assertEqual(result["unverified_source_answers"], 1)
        self.assertEqual(result["target_status"], "below_target")

    def test_targets_require_both_colloquial_and_synonym_recall_and_zero_wrong_articles(self):
        colloquial = reviewed("Q-C", style="colloquial")
        synonym = reviewed("Q-S", style="formal", tags=["synonym"])
        good = [
            {"question_id": "Q-C", "retrieved_article_ids": ["LABOUR-ART-1"],
             "cited_article_ids": ["LABOUR-ART-1"], "abstained": False},
            {"question_id": "Q-S", "retrieved_article_ids": ["LABOUR-ART-1"],
             "cited_article_ids": ["LABOUR-ART-1"], "abstained": False},
        ]
        self.assertEqual(score([colloquial, synonym], good)["target_status"], "targets_met")
        bad = [
            {"question_id": "Q-C", "retrieved_article_ids": ["LABOUR-ART-1", "LABOUR-ART-2"],
             "cited_article_ids": ["LABOUR-ART-2"], "abstained": False},
            good[1],
        ]
        self.assertEqual(score([colloquial, synonym], bad)["target_status"], "below_target")

    def test_target_status_is_not_evaluable_without_approved_slice_or_citations(self):
        q = reviewed("Q1", style="formal")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-ART-1"],
               "cited_article_ids": [], "abstained": False}
        self.assertEqual(score([q], [run])["target_status"],
                         "not_evaluable_missing_approved_labels_or_cited_runs")

    def test_canonical_expected_article_id_is_used_for_hits_and_citations(self):
        q = reviewed("Q1")
        q["expected_article"] = "المادة 12 من قانون العمل"
        q["expected_article_id"] = "EG-LABOUR-14-2025::law:قانون العمل رقم 14 لسنة 2025 [block 1]::article:12"
        run = {"question_id": "Q1",
               "retrieved_article_ids": ["EG-LABOUR-14-2025::law:قانون العمل رقم 14 لسنة 2025 [block 1]::article:12"],
               "cited_article_ids": ["EG-LABOUR-14-2025::law:قانون العمل رقم 14 لسنة 2025 [block 1]::article:12"],
               "abstained": False}
        result = score([q], [run])
        self.assertEqual(result["top3_hit_rate"], 1.0)
        self.assertEqual(result["wrong_article_rate"], 0.0)

    def test_unverified_source_citation_blocks_target_even_when_article_matches(self):
        q = reviewed("Q-UNVERIFIED", style="colloquial", tags=["synonym"])
        run = {
            "question_id": "Q-UNVERIFIED",
            "retrieved_article_ids": ["LABOUR-ART-1"],
            "cited_article_ids": ["LABOUR-ART-1"],
            "abstained": False,
            "used_unverified_source": True,
        }
        result = score([q], [run])
        self.assertEqual(result["wrong_article_rate"], 0.0)
        self.assertEqual(result["unverified_source_answers"], 1)
        self.assertEqual(result["unverified_source_rate"], 1.0)
        self.assertEqual(result["target_status"], "below_target")

    def test_rejects_cited_article_not_present_in_retrieved_results(self):
        q = reviewed("Q1")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-ART-1"],
               "cited_article_ids": ["LABOUR-ART-2"], "abstained": False}
        with self.assertRaisesRegex(ValueError, "must be present in retrieved_article_ids"):
            score([q], [run])

    def test_wrong_cited_article_is_counted(self):
        q = reviewed("Q1")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-ART-1", "LABOUR-ART-2"],
               "cited_article_ids": ["LABOUR-ART-2"], "abstained": False}
        result = score([q], [run])
        self.assertEqual(result["wrong_article_rate"], 1.0)
        self.assertEqual(result["wrong_article_answers"], 1)

    def test_synonym_tag_is_included_in_target_slice(self):
        q = reviewed("Q1", tags=["synonym"])
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-ART-1"],
               "cited_article_ids": ["LABOUR-ART-1"], "abstained": False}
        result = score([q], [run])
        self.assertEqual(result["top3_hit_rate_synonym"], 1.0)
        self.assertEqual(result["top3_hit_rate_colloquial_or_synonym"], 1.0)
        self.assertEqual(result["colloquial_or_synonym_questions"], 1)

    def test_review_status_without_approved_label_status_is_rejected(self):
        q = reviewed("Q1")
        q["label_status"] = "unlabeled"
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-ART-1"],
               "cited_article_ids": ["LABOUR-ART-1"], "abstained": False}
        with self.assertRaisesRegex(ValueError, "approved label_status"):
            score([q], [run])

    def test_unanswerable_case_requires_abstention(self):
        q = reviewed("Q1", answerable=False)
        run = {"question_id": "Q1", "retrieved_article_ids": [], "cited_article_ids": [],
               "abstained": True}
        result = score([q], [run])
        self.assertEqual(result["abstention_rate"], 1.0)
        self.assertEqual(result["abstention_compliance_unanswerable"], 1.0)

    def test_uncited_non_abstained_answer_is_reported_separately(self):
        q = reviewed("Q1")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-ART-1"],
               "cited_article_ids": [], "abstained": False}
        result = score([q], [run])
        self.assertEqual(result["uncited_non_abstained_answers"], 1)
        self.assertIsNone(result["wrong_article_rate"])

    def test_run_for_unknown_question_is_rejected(self):
        q = reviewed("Q1")
        run = {"question_id": "UNKNOWN", "retrieved_article_ids": [], "cited_article_ids": [], "abstained": True}
        with self.assertRaisesRegex(ValueError, "unknown question_id"):
            score([q], [run])



if __name__ == "__main__":
    unittest.main()
