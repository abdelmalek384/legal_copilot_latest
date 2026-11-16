import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.validate_law14_eval_draft as validator
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

    def test_rejects_non_arabic_question_text(self):
        report = validate_rows([question(question_ar="What does this article say?")], minimum_questions=1)
        self.assertTrue(any("must contain Arabic text" in item for item in report["errors"]))

    def test_rejects_article_pin_without_both_question_styles(self):
        report = validate_rows([
            question(),
            question(id="Q-002", question_ar="ما المقصود بهذا الحكم؟"),
        ], minimum_questions=1)
        self.assertTrue(any("exactly one formal and one colloquial" in item for item in report["errors"]))

    def test_rejects_unhashable_question_style_without_crashing(self):
        report = validate_rows([question(question_style=["formal"])], minimum_questions=1)
        self.assertTrue(any("question_style" in item for item in report["errors"]))

    def test_rejects_mismatched_article_pin(self):
        report = validate_rows([
            question(expected_article_id="EG-LABOUR-LAW-14-2025-ART-13")
        ], minimum_questions=1)
        self.assertTrue(any("does not match" in item for item in report["errors"]))

    def test_jsonl_reader_rejects_duplicate_keys_at_all_object_depths(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.jsonl"
            for raw in (
                '{"id":"Q1","id":"Q2"}',
                '{"id":"Q1","metadata":{"review_status":"needs_lawyer_review","review_status":"verified"}}',
            ):
                path.write_text(raw + "\n", encoding="utf-8")
                with self.subTest(raw=raw), self.assertRaisesRegex(
                    ValueError, r"1: duplicate JSON object key '"
                ):
                    read_jsonl(path)

    def test_jsonl_reader_rejects_symlinks_special_files_and_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.jsonl"
            target.write_text('{"id":"Q1"}\n', encoding="utf-8")
            link = root / "linked.jsonl"
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "bounded regular file|cannot safely read"):
                read_jsonl(link)
            if hasattr(os, "mkfifo"):
                fifo = root / "questions.fifo"
                os.mkfifo(fifo)
                with self.assertRaisesRegex(ValueError, "bounded regular file"):
                    read_jsonl(fifo)
            invalid = root / "invalid.jsonl"
            invalid.write_bytes(b"\xff")
            with self.assertRaisesRegex(ValueError, "valid UTF-8"):
                read_jsonl(invalid)

    def test_jsonl_reader_rejects_symlink_replacement_between_check_and_open(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "questions.jsonl"
            path.write_text('{"id":"Q1"}\n', encoding="utf-8")
            external = root / "external.jsonl"
            external.write_text('{"id":"OUTSIDE"}\n', encoding="utf-8")
            real_open = validator.os.open
            swapped = False

            def replace_before_open(target, flags, *args, **kwargs):
                nonlocal swapped
                if Path(target) == path and not swapped:
                    swapped = True
                    path.unlink()
                    path.symlink_to(external)
                return real_open(target, flags, *args, **kwargs)

            with patch.object(validator.os, "open", side_effect=replace_before_open):
                with self.assertRaisesRegex(ValueError, "cannot safely read evaluation draft"):
                    read_jsonl(path)
            self.assertTrue(swapped)
            self.assertEqual(external.read_text(encoding="utf-8"), '{"id":"OUTSIDE"}\n')

    def test_jsonl_reader_rejects_non_object_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.jsonl"
            path.write_text(json.dumps([question()], ensure_ascii=False) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be an object"):
                read_jsonl(path)


if __name__ == "__main__":
    unittest.main()
