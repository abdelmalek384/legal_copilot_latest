#!/usr/bin/env python3
"""Validate the Law 14/2025 machine-proposed question inventory without approving it.

This is a structural/safety audit only. It does not verify legal text, article pins,
question answerability, or expected answers, and it never creates reviewed labels.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "tests" / "legal_eval" / "law_14_2025_machine_proposed_questions.draft.jsonl"
SOURCE_ID = "EG-LABOUR-LAW-14-2025"
UNAPPROVED_STATUS = "machine-proposed, unapproved"
REQUIRED_NULL_FIELDS = (
    "expected_answer",
    "lawyer_approved_answer",
    "answerable",
    "reviewer_id",
    "reviewer_name",
    "review_date",
)
REQUIRED_FALSE_FIELDS = (
    "source_text_page_reviewed",
    "amendment_history_verified",
    "release_eligible",
    "original_pdf_downloaded",
    "full_visual_review",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: question row must be an object")
            rows.append(value)
    return rows


def validate_rows(rows: list[dict[str, Any]], minimum_questions: int = 100) -> dict[str, Any]:
    errors: list[str] = []
    styles: Counter[str] = Counter()
    ids: set[str] = set()
    question_texts: set[str] = set()
    article_ids: set[str] = set()
    article_styles: dict[str, list[str]] = {}
    targeted_text_review_count = 0

    if not isinstance(rows, list):
        return {"valid": False, "errors": ["dataset must be a list"], "questions": 0}
    if len(rows) < minimum_questions:
        errors.append(f"dataset must contain at least {minimum_questions} questions")

    for index, row in enumerate(rows, start=1):
        label = f"row {index}"
        if not isinstance(row, dict):
            errors.append(f"{label}: question row must be an object")
            continue

        for field in ("id", "question_ar", "expected_article", "expected_article_id",
                      "expected_article_status", "label_status", "review_status",
                      "question_style", "question_origin", "source_document_id"):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: {field} must be a non-empty string")

        question_id = row.get("id")
        if isinstance(question_id, str) and question_id:
            if question_id in ids:
                errors.append(f"{label}: duplicate question id {question_id}")
            ids.add(question_id)

        question = row.get("question_ar")
        if isinstance(question, str) and question.strip():
            normalized = question.strip()
            if normalized in question_texts:
                errors.append(f"{label}: duplicate Arabic question text")
            question_texts.add(normalized)
            if not re.search(r"[\u0600-\u06FF]", normalized):
                errors.append(f"{label}: question_ar must contain Arabic text")

        style = row.get("question_style")
        if not isinstance(style, str) or style not in {"formal", "colloquial_egyptian"}:
            errors.append(f"{label}: question_style must be formal or colloquial_egyptian")
        else:
            styles[style] += 1

        if row.get("question_origin") != "curated_candidate_not_user_observed":
            errors.append(f"{label}: question_origin must remain curated_candidate_not_user_observed")
        if row.get("source_document_id") != SOURCE_ID:
            errors.append(f"{label}: source_document_id must identify Labour Law 14/2025")

        article_number = row.get("expected_article_number")
        if isinstance(article_number, bool) or not isinstance(article_number, int) or article_number < 1:
            errors.append(f"{label}: expected_article_number must be a positive integer")
        else:
            article_id = row.get("expected_article_id")
            article_label = row.get("expected_article", "")
            expected_suffix = (
                f"{SOURCE_ID}-PROMULGATION-ART-{article_number}"
                if isinstance(article_label, str) and article_label.startswith("مادة الإصدار")
                else f"{SOURCE_ID}-ART-{article_number}"
            )
            if article_id != expected_suffix:
                errors.append(f"{label}: expected_article_id does not match the proposed article number")
            article_ids.add(str(article_id))
            if isinstance(article_id, str) and isinstance(style, str) and style in {"formal", "colloquial_egyptian"}:
                article_styles.setdefault(article_id, []).append(style)

        if row.get("expected_article_status") != UNAPPROVED_STATUS:
            errors.append(f"{label}: expected_article_status must remain machine-proposed, unapproved")
        if row.get("label_status") != "machine_proposed_unapproved":
            errors.append(f"{label}: label_status must remain machine_proposed_unapproved")
        if row.get("review_status") != "needs_lawyer_review":
            errors.append(f"{label}: review_status must remain needs_lawyer_review")
        if row.get("must_abstain_if_unverified") is not True:
            errors.append(f"{label}: must_abstain_if_unverified must be true")
        if row.get("expected_sources") != [] or row.get("expected_pin_cites") != []:
            errors.append(f"{label}: unapproved questions must not contain approved source/pin-cite keys")

        for field in REQUIRED_NULL_FIELDS:
            if row.get(field) is not None:
                errors.append(f"{label}: {field} must remain null until lawyer review")
        for field in REQUIRED_FALSE_FIELDS:
            if row.get(field) is not False:
                errors.append(f"{label}: {field} must remain false until review evidence exists")
        if not isinstance(row.get("targeted_pdf_text_reviewed"), bool):
            errors.append(f"{label}: targeted_pdf_text_reviewed must be an explicit boolean")
        elif row["targeted_pdf_text_reviewed"]:
            targeted_text_review_count += 1

    if not styles.get("formal") or not styles.get("colloquial_egyptian"):
        errors.append("dataset must include both formal and colloquial_egyptian questions")
    for article_id, pair_styles in article_styles.items():
        if sorted(pair_styles) != ["colloquial_egyptian", "formal"]:
            errors.append(f"article pin {article_id} must have exactly one formal and one colloquial question")

    return {
        "valid": not errors,
        "questions": len(rows),
        "unique_ids": len(ids),
        "unique_question_texts": len(question_texts),
        "unique_expected_article_ids": len(article_ids),
        "targeted_pdf_text_reviewed_count": targeted_text_review_count,
        "styles": dict(sorted(styles.items())),
        "unapproved_label": UNAPPROVED_STATUS,
        "errors": errors,
        "trust_boundary": "Structural validation only; no legal approval, answer key, verification, or release eligibility is inferred.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", nargs="?", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--minimum-questions", type=int, default=100)
    args = parser.parse_args(argv)
    if args.minimum_questions < 1:
        parser.error("--minimum-questions must be positive")
    try:
        report = validate_rows(read_jsonl(args.dataset), args.minimum_questions)
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
