import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_law14_eval_draft import DEFAULT_DATASET, read_jsonl, validate_rows


def question(**overrides):
    row = {
        "id": "Q-001",
        "question_ar": "ما نطاق تطبيق القانون؟",
        "question_style": "formal",
        "question_origin": "curated_candidate_not_user_observed",
        "source_document_id": "EG-LABOUR-LAW-14-2025",
        "expected_article": "المادة 12",
        "expected_article_number": 12,
        "expected_article_id": "EG-LABOUR-LAW-14-2025-ART-12",
        "expected_article_status": "machine-proposed, unapproved",
        "label_status": "machine_proposed_unapproved",
        "review_status": "needs_lawyer_review",
        "expected_answer": None,
        "lawyer_approved_answer": None,
        "expected_sources": [],
        "expected_pin_cites": [],
        "answerable": None,
        "must_abstain_if_unverified": True,
        "reviewer_id": None,
        "reviewer_name": None,
        "review_date": None,
        "source_text_page_reviewed": False,
        "amendment_history_verified": False,
        "release_eligible": False,
        "targeted_pdf_text_reviewed": False,
        "original_pdf_downloaded": False,
        "full_visual_review": False,
    }
    row.update(overrides)
    return row


class Law14DraftInventoryTests(unittest.TestCase):
    def test_current_inventory_is_structurally_valid_and_unapproved(self):
        rows = read_jsonl(DEFAULT_DATASET)
        report = validate_rows(rows)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["questions"], 116)
        self.assertEqual(report["styles"], {"colloquial_egyptian": 58, "formal": 58})
        self.assertEqual(report["targeted_pdf_text_reviewed_count"], 48)

    def test_rejects_duplicate_ids_and_question_text(self):
        first = question()
        second = question(id="Q-002")
        report = validate_rows([first, second], minimum_questions=1)
        self.assertTrue(any("duplicate Arabic question text" in item for item in report["errors"]))

    def test_rejects_any_machine_proposed_to_reviewed_promotion(self):
        report = validate_rows([
            question(expected_article_status="verified", release_eligible=True)
        ], minimum_questions=1)
        self.assertTrue(any("expected_article_status" in item for item in report["errors"]))
        self.assertTrue(any("release_eligible" in item for item in report["errors"]))

    def test_rejects_unhashable_question_style_without_crashing(self):
        report = validate_rows([question(question_style=["formal"])], minimum_questions=1)
        self.assertTrue(any("question_style" in item for item in report["errors"]))

    def test_rejects_mismatched_article_pin(self):
        report = validate_rows([
            question(expected_article_id="EG-LABOUR-LAW-14-2025-ART-13")
        ], minimum_questions=1)
        self.assertTrue(any("does not match" in item for item in report["errors"]))

    def test_jsonl_reader_rejects_non_object_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.jsonl"
            path.write_text(json.dumps([question()], ensure_ascii=False) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be an object"):
                read_jsonl(path)


if __name__ == "__main__":
    unittest.main()
