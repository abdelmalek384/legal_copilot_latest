"""Tests for the reviewed-label-only Arabic retrieval scorer."""
import contextlib
import io
import sys
import tempfile
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.score_arabic_retrieval import benchmark_fingerprint, main, score

TEST_REVIEWER_REGISTRY = {
    "reviewers": [
        {
            "reviewer_id": "reviewer-test-1",
            "status": "approved",
            "display_name": "Test Reviewer",
            "qualification_basis": "synthetic test fixture",
            "evidence_reference": "private-fixture:reviewer-test-1",
            "verified_by": "test administrator",
            "professional_role": "egyptian_lawyer",
            "jurisdiction": "Egypt",
            "practice_areas": [
                "constitutional_law",
                "civil_law",
                "civil_procedure",
                "evidence",
                "arbitration",
                "criminal_law",
                "criminal_procedure",
                "labour",
                "unspecified"
            ],
            "verified_on": "2026-11-05"
        }
    ]
}


def reviewed(qid, *, answerable=True, article="المادة 1 من قانون العمل", style="formal", tags=None):
    return {
        "id": qid,
        "practice_area": "labour",
        "question_style": style,
        "question_origin": "observed_anonymized_query",
        "question_origin_reference": f"synthetic-test-fixture:{qid}",
        "question_collection_date": "2026-11-04",
        "privacy_review_status": "approved",
        "consent_or_reuse_basis": "synthetic test fixture only",
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
        "expected_article_id": (
            "LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"
            if answerable else None
        ),
        "must_abstain_if_unverified": True,
        "reviewer_name": "Test Reviewer",
        "review_date": "2026-11-05",
        "review_evidence_url": "https://example.gov.eg/review-record",
    }


class ArabicRetrievalScorerTests(unittest.TestCase):
    def test_reviewer_must_be_in_approved_registry_and_practice_area(self):
        q = reviewed("Q-REGISTRY")
        run = {"question_id": "Q-REGISTRY",
               "retrieved_article_ids": [q["expected_article_id"]],
               "cited_article_ids": [q["expected_article_id"]],
               "abstained": False, "used_unverified_source": False}
        altered = dict(q, reviewer_name="Unregistered Reviewer")
        with self.assertRaisesRegex(ValueError, "reviewer_name must match"):
            score([altered], [run], TEST_REVIEWER_REGISTRY)
        altered = dict(q, practice_area="criminal_law")
        with self.assertRaisesRegex(ValueError, "not approved for this practice_area"):
            score([altered], [run], TEST_REVIEWER_REGISTRY)

    def test_cli_reports_malformed_json_without_traceback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            questions = Path(temp_dir) / "questions.jsonl"
            runs = Path(temp_dir) / "runs.jsonl"
            questions.write_text("{not-json}\\n", encoding="utf-8")
            runs.write_text("", encoding="utf-8")
            registry = Path(temp_dir) / "reviewers.json"
            registry.write_text(__import__("json").dumps(TEST_REVIEWER_REGISTRY), encoding="utf-8")
            stderr = io.StringIO()
            with mock.patch("sys.argv", [
                "score_arabic_retrieval.py",
                "--questions", str(questions),
                "--runs", str(runs),
                "--reviewer-registry", str(registry),
                "--phase", "before",
            ]), contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main()
            self.assertEqual(raised.exception.code, 2)
            self.assertIn("invalid JSON", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_rejects_measurement_report_with_wrong_json_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            questions = Path(temp_dir) / "questions.jsonl"
            runs = Path(temp_dir) / "runs.jsonl"
            report = Path(temp_dir) / "report.json"
            questions.write_text('{"id":"Q1","review_status":"needs_lawyer_review"}\\n', encoding="utf-8")
            runs.write_text("", encoding="utf-8")
            report.write_text("[]", encoding="utf-8")
            registry = Path(temp_dir) / "reviewers.json"
            registry.write_text(__import__("json").dumps(TEST_REVIEWER_REGISTRY), encoding="utf-8")
            stderr = io.StringIO()
            with mock.patch("sys.argv", [
                "score_arabic_retrieval.py",
                "--questions", str(questions),
                "--runs", str(runs),
                "--reviewer-registry", str(registry),
                "--phase", "before",
                "--output", str(report),
            ]), contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main()
            self.assertEqual(raised.exception.code, 2)
            self.assertIn("phases object", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_curated_candidate_cannot_enter_real_question_scoring(self):
        question = reviewed("Q-CURATED")
        question["question_origin"] = "curated_candidate_not_user_observed"
        with self.assertRaisesRegex(ValueError, "observed questions"):
            score([question], [], TEST_REVIEWER_REGISTRY)

    def test_scoring_requires_privacy_and_reuse_approval(self):
        question = reviewed("Q-PRIVACY")
        question["privacy_review_status"] = "not_reviewed"
        with self.assertRaisesRegex(ValueError, "privacy_review_status"):
            score([question], [], TEST_REVIEWER_REGISTRY)

        question = reviewed("Q-REUSE")
        question["consent_or_reuse_basis"] = ""
        with self.assertRaisesRegex(ValueError, "consent_or_reuse_basis"):
            score([question], [], TEST_REVIEWER_REGISTRY)

    def test_non_string_reviewer_evidence_url_is_rejected_as_invalid_metadata(self):
        question = reviewed("Q-BAD-URL")
        question["review_evidence_url"] = 123
        with self.assertRaisesRegex(ValueError, "review_evidence_url must be clean HTTPS"):
            score([question], [], TEST_REVIEWER_REGISTRY)

    def test_reviewer_evidence_url_rejects_controls_delimiters_and_credentials(self):
        for url in (
            "https://example.gov/review path",
            "https://example.gov/review\\nrecord",
            "https://example.gov/review\\t",
            "https://example.gov/review\\x7f",
            "https://example.gov/review?",
            "https://example.gov/review#",
            "https://example.gov/review?token=",
            "https://example.gov/review#section",
            "https://@example.gov/review",
            "https://example.gov:/review",
        ):
            with self.subTest(url=url):
                question = reviewed("Q-BAD-URL")
                question["review_evidence_url"] = url
                with self.assertRaisesRegex(ValueError, "review_evidence_url must be clean HTTPS"):
                    score([question], [], TEST_REVIEWER_REGISTRY)

    def test_benchmark_fingerprint_survives_counsel_labeling_but_detects_prompt_edits(self):
        q = {
            "id": "Q1", "practice_area": "labour", "question_ar": "سؤال تجريبي",
            "question_origin": "curated_candidate_not_user_observed",
            "expected_article": None, "expected_article_id": None,
            "lawyer_approved_answer": None, "review_status": "needs_lawyer_review",
            "label_status": "unlabeled", "question_style": "colloquial",
            "question_style_review_status": "needs_lawyer_review",
            "retrieval_tags": ["synonym", "colloquial"], "retrieval_tags_review_status": "needs_lawyer_review",
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
        edited_style = dict(labeled, question_style="formal")
        self.assertNotEqual(before, benchmark_fingerprint([edited_style]))
        edited_tags = dict(labeled, retrieval_tags=["synonym", "colloquial", "new-tag"])
        self.assertNotEqual(before, benchmark_fingerprint([edited_tags]))
        reordered_tags = dict(labeled, retrieval_tags=["colloquial", "synonym"])
        self.assertEqual(before, benchmark_fingerprint([reordered_tags]))

    def test_unlabeled_rows_and_their_captured_runs_are_excluded_and_metrics_are_null(self):
        q = {"id": "Q1", "review_status": "needs_lawyer_review", "expected_article": None}
        run = {"question_id": "Q1", "retrieved_article_ids": ["EG-LAW::article:1"],
               "cited_article_ids": [], "abstained": True, "used_unverified_source": False}
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["reviewed_questions"], 0)
        self.assertEqual(result["unlabeled_or_unreviewed_excluded"], 1)
        self.assertEqual(result["unlabeled_run_records_excluded"], 1)
        self.assertIsNone(result["top3_hit_rate"])
        self.assertIsNone(result["wrong_article_rate"])
        self.assertIsNone(result["abstention_rate"])

    def test_correct_colloquial_article_is_a_top3_hit_with_zero_wrong_article_rate(self):
        q = reviewed("Q1", style="colloquial")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1", "LABOUR-SOURCE::law:قانون العمل [block 1]::article:2"],
               "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"], "abstained": False, "used_unverified_source": False}
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["top3_hit_rate"], 1.0)
        self.assertEqual(result["top3_hit_rate_colloquial"], 1.0)
        self.assertEqual(result["top3_hit_rate_colloquial_or_synonym"], 1.0)
        self.assertEqual(result["wrong_article_rate"], 0.0)

    def test_answerable_abstentions_are_reported_separately_from_unanswerable_safety(self):
        question = reviewed("Q-ANSWERABLE")
        run = {
            "question_id": "Q-ANSWERABLE",
            "retrieved_article_ids": [
                "LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"
            ],
            "cited_article_ids": [],
            "abstained": True,
            "used_unverified_source": False,
        }
        result = score([question], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["answerable_abstained_answers"], 1)
        self.assertEqual(result["answerable_non_abstained_answers"], 0)
        self.assertEqual(result["answerable_abstention_rate"], 1.0)

    def test_targets_require_both_colloquial_and_synonym_recall_and_zero_wrong_articles(self):
        colloquial = [reviewed(f"Q-C-{i}", style="colloquial") for i in range(20)]
        synonym = [reviewed(f"Q-S-{i}", style="formal", tags=["synonym"]) for i in range(20)]
        formal = [reviewed(f"Q-F-{i}") for i in range(60)]
        unanswerable = reviewed("Q-U", answerable=False)
        questions = colloquial + synonym + formal + [unanswerable]
        article_id = "LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"
        good = [
            {"question_id": q["id"],
             "retrieved_article_ids": [article_id] if q["answerable"] else [],
             "cited_article_ids": [article_id] if q["answerable"] else [],
             "abstained": not q["answerable"], "used_unverified_source": False}
            for q in questions
        ]
        self.assertEqual(score(questions, good, TEST_REVIEWER_REGISTRY)["target_status"], "targets_met")
        bad = [dict(run) for run in good]
        bad[0]["retrieved_article_ids"] = [
            "LABOUR-SOURCE::law:قانون العمل [block 1]::article:1",
            "LABOUR-SOURCE::law:قانون العمل [block 1]::article:2",
        ]
        bad[0]["cited_article_ids"] = ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:2"]
        self.assertEqual(score(questions, bad, TEST_REVIEWER_REGISTRY)["target_status"], "below_target")

    def test_target_requires_100_reviewed_real_questions(self):
        questions = (
            [reviewed(f"Q-C-{i}", style="colloquial") for i in range(20)]
            + [reviewed(f"Q-S-{i}", style="formal", tags=["synonym"]) for i in range(20)]
            + [reviewed("Q-U", answerable=False)]
        )
        article_id = "LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"
        runs = [
            {"question_id": q["id"], "retrieved_article_ids": [article_id] if q["answerable"] else [],
             "cited_article_ids": [article_id] if q["answerable"] else [],
             "abstained": not q["answerable"], "used_unverified_source": False}
            for q in questions
        ]
        result = score(questions, runs, TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["reviewed_questions"], 41)
        self.assertEqual(result["target_minimum_reviewed_questions"], 100)
        self.assertEqual(result["target_status"],
                         "not_evaluable_missing_approved_labels_or_cited_runs")

    def test_target_requires_an_unanswerable_question_to_measure_abstention(self):
        questions = (
            [reviewed(f"Q-C-{i}", style="colloquial") for i in range(20)]
            + [reviewed(f"Q-S-{i}", style="formal", tags=["synonym"]) for i in range(20)]
            + [reviewed(f"Q-F-{i}") for i in range(60)]
        )
        article_id = "LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"
        runs = [
            {"question_id": q["id"], "retrieved_article_ids": [article_id],
             "cited_article_ids": [article_id], "abstained": False,
             "used_unverified_source": False}
            for q in questions
        ]
        result = score(questions, runs, TEST_REVIEWER_REGISTRY)
        self.assertIsNone(result["abstention_compliance_unanswerable"])
        self.assertEqual(result["target_minimum_unanswerable_questions"], 1)
        self.assertEqual(result["target_status"],
                         "not_evaluable_missing_approved_labels_or_cited_runs")

    def test_non_abstained_unanswerable_answer_blocks_target(self):
        questions = (
            [reviewed(f"Q-C-{i}", style="colloquial") for i in range(20)]
            + [reviewed(f"Q-S-{i}", style="formal", tags=["synonym"]) for i in range(20)]
            + [reviewed(f"Q-F-{i}") for i in range(60)]
            + [reviewed("Q-U", answerable=False)]
        )
        article_id = "LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"
        runs = [
            {"question_id": q["id"], "retrieved_article_ids": [article_id] if q["answerable"] else [],
             "cited_article_ids": [article_id] if q["answerable"] else [],
             "abstained": False, "used_unverified_source": False}
            for q in questions
        ]
        result = score(questions, runs, TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["abstention_compliance_unanswerable"], 0.0)
        self.assertEqual(result["target_status"], "below_target")

    def test_target_status_is_not_evaluable_below_minimum_approved_cohort_size(self):
        questions = [
            reviewed("Q-C", style="colloquial"),
            reviewed("Q-S", style="formal", tags=["synonym"]),
        ]
        runs = [
            {"question_id": q["id"], "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
             "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
             "abstained": False, "used_unverified_source": False}
            for q in questions
        ]
        result = score(questions, runs, TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["target_minimum_cohort_size"], 20)
        self.assertEqual(result["target_status"], "not_evaluable_missing_approved_labels_or_cited_runs")

    def test_target_status_is_not_evaluable_without_approved_slice_or_citations(self):
        q = reviewed("Q1", style="formal")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
               "cited_article_ids": [], "abstained": False, "used_unverified_source": False}
        self.assertEqual(score([q], [run], TEST_REVIEWER_REGISTRY)["target_status"],
                         "not_evaluable_missing_approved_labels_or_cited_runs")

    def test_canonical_expected_article_id_is_used_for_hits_and_citations(self):
        q = reviewed("Q1")
        q["expected_article"] = "المادة 12 من قانون العمل"
        q["expected_article_id"] = "EG-LABOUR-14-2025::law:قانون العمل رقم 14 لسنة 2025 [block 1]::article:12"
        run = {"question_id": "Q1",
               "retrieved_article_ids": ["EG-LABOUR-14-2025::law:قانون العمل رقم 14 لسنة 2025 [block 1]::article:12"],
               "cited_article_ids": ["EG-LABOUR-14-2025::law:قانون العمل رقم 14 لسنة 2025 [block 1]::article:12"],
               "abstained": False, "used_unverified_source": False}
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["top3_hit_rate"], 1.0)
        self.assertEqual(result["wrong_article_rate"], 0.0)

    def test_missing_unverified_source_flag_is_rejected(self):
        q = reviewed("Q-MISSING-FLAG")
        run = {
            "question_id": "Q-MISSING-FLAG",
            "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "abstained": False,
        }
        with self.assertRaisesRegex(ValueError, "used_unverified_source must be boolean"):
            score([q], [run], TEST_REVIEWER_REGISTRY)

    def test_unverified_source_citation_blocks_target_even_when_article_matches(self):
        q = reviewed("Q-UNVERIFIED", style="colloquial", tags=["synonym"])
        run = {
            "question_id": "Q-UNVERIFIED",
            "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "abstained": False,
            "used_unverified_source": True,
        }
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["wrong_article_rate"], 0.0)
        self.assertEqual(result["unverified_source_answers"], 1)
        self.assertEqual(result["unverified_source_rate"], 1.0)
        self.assertEqual(result["target_status"], "below_target")

    def test_rejects_cited_article_not_present_in_retrieved_results(self):
        q = reviewed("Q1")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
               "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:2"], "abstained": False, "used_unverified_source": False}
        with self.assertRaisesRegex(ValueError, "must be present in retrieved_article_ids"):
            score([q], [run], TEST_REVIEWER_REGISTRY)

    def test_wrong_cited_article_is_counted(self):
        q = reviewed("Q1")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1", "LABOUR-SOURCE::law:قانون العمل [block 1]::article:2"],
               "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:2"], "abstained": False, "used_unverified_source": False}
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["wrong_article_rate"], 1.0)
        self.assertEqual(result["wrong_article_answers"], 1)

    def test_synonym_tag_is_included_in_target_slice(self):
        q = reviewed("Q1", tags=["synonym"])
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
               "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"], "abstained": False, "used_unverified_source": False}
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["top3_hit_rate_synonym"], 1.0)
        self.assertEqual(result["top3_hit_rate_colloquial_or_synonym"], 1.0)
        self.assertEqual(result["colloquial_or_synonym_questions"], 1)

    def test_preliminary_style_and_synonym_tags_do_not_enter_approved_cohorts(self):
        q = reviewed("Q-PRELIMINARY", style="colloquial", tags=["synonym"])
        q["question_style_review_status"] = "needs_lawyer_review"
        q["retrieval_tags_review_status"] = "needs_lawyer_review"
        run = {
            "question_id": "Q-PRELIMINARY",
            "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["colloquial_questions"], 0)
        self.assertEqual(result["synonym_questions"], 0)
        self.assertEqual(result["target_status"], "not_evaluable_missing_approved_labels_or_cited_runs")

    def test_answerable_reviewed_question_requires_canonical_article_id(self):
        q = reviewed("Q-NO-CANONICAL-ID")
        q["expected_article_id"] = None
        run = {
            "question_id": "Q-NO-CANONICAL-ID",
            "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "abstained": False,
            "used_unverified_source": False,
        }
        with self.assertRaisesRegex(ValueError, "needs canonical expected_article_id"):
            score([q], [run], TEST_REVIEWER_REGISTRY)

    def test_answerable_reviewed_question_requires_human_readable_article_label(self):
        q = reviewed("Q-NO-ARTICLE-TEXT")
        q["expected_article"] = None
        run = {
            "question_id": "Q-NO-ARTICLE-TEXT",
            "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
            "abstained": False,
            "used_unverified_source": False,
        }
        with self.assertRaisesRegex(ValueError, "needs a human-readable expected_article"):
            score([q], [run], TEST_REVIEWER_REGISTRY)

    def test_review_status_without_approved_label_status_is_rejected(self):
        q = reviewed("Q1")
        q["label_status"] = "unlabeled"
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
               "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"], "abstained": False, "used_unverified_source": False}
        with self.assertRaisesRegex(ValueError, "approved label_status"):
            score([q], [run], TEST_REVIEWER_REGISTRY)

    def test_unanswerable_case_requires_abstention(self):
        q = reviewed("Q1", answerable=False)
        run = {"question_id": "Q1", "retrieved_article_ids": [], "cited_article_ids": [],
               "abstained": True, "used_unverified_source": False}
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["abstention_rate"], 1.0)
        self.assertEqual(result["abstention_compliance_unanswerable"], 1.0)

    def test_uncited_non_abstained_answer_blocks_targets(self):
        colloquial = reviewed("Q-C", style="colloquial")
        synonym = reviewed("Q-S", tags=["synonym"])
        runs = [
            {"question_id": "Q-C", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
             "cited_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"], "abstained": False,
             "used_unverified_source": False},
            {"question_id": "Q-S", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
             "cited_article_ids": [], "abstained": False,
             "used_unverified_source": False},
        ]
        result = score([colloquial, synonym], runs, TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["top3_hit_rate_colloquial"], 1.0)
        self.assertEqual(result["top3_hit_rate_synonym"], 1.0)
        self.assertEqual(result["wrong_article_rate"], 0.0)
        self.assertEqual(result["uncited_non_abstained_answers"], 1)
        self.assertEqual(result["target_status"], "below_target")

    def test_uncited_non_abstained_answer_is_reported_separately(self):
        q = reviewed("Q1")
        run = {"question_id": "Q1", "retrieved_article_ids": ["LABOUR-SOURCE::law:قانون العمل [block 1]::article:1"],
               "cited_article_ids": [], "abstained": False, "used_unverified_source": False}
        result = score([q], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(result["uncited_non_abstained_answers"], 1)
        self.assertIsNone(result["wrong_article_rate"])

    def test_run_for_unknown_question_is_rejected(self):
        q = reviewed("Q1")
        run = {"question_id": "UNKNOWN", "retrieved_article_ids": [], "cited_article_ids": [], "abstained": True, "used_unverified_source": False}
        with self.assertRaisesRegex(ValueError, "unknown question_id"):
            score([q], [run], TEST_REVIEWER_REGISTRY)




    def test_unhashable_review_enum_values_are_rejected_without_type_errors(self):
        run = {
            "question_id": "Q-ENUM",
            "retrieved_article_ids": [reviewed("Q-ENUM")["expected_article_id"]],
            "cited_article_ids": [reviewed("Q-ENUM")["expected_article_id"]],
            "abstained": False,
            "used_unverified_source": False,
        }
        # Unknown/malformed review status is excluded from scoring, never treated as approved.
        malformed_status = reviewed("Q-ENUM")
        malformed_status["review_status"] = []
        report = score([malformed_status], [run], TEST_REVIEWER_REGISTRY)
        self.assertEqual(report["reviewed_questions"], 0)

        for field, expected_message in (
            ("question_origin", "only provenance-cleared observed questions"),
            ("label_status", "approved label_status"),
            ("reviewer_role", "reviewer_role must identify qualified Egyptian counsel"),
        ):
            question = reviewed("Q-ENUM")
            question[field] = []
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, expected_message):
                score([question], [run], TEST_REVIEWER_REGISTRY)

if __name__ == "__main__":
    unittest.main()
