"""Structural checks only for the unapproved Law 14/2025 retrieval-question drafts."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "tests" / "legal_eval" / "law_14_2025_machine_proposed_questions.draft.jsonl"


def test_law14_machine_proposed_questions_are_unique_article_mapped_and_unapproved():
    rows = [
        json.loads(line)
        for line in DATASET.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 116
    assert len({row["id"] for row in rows}) == len(rows)
    assert len({row["question_ar"] for row in rows}) == len(rows)
    assert Counter(row["question_style"] for row in rows) == {
        "formal": 58,
        "colloquial_egyptian": 58,
    }
    assert all(row["practice_area"] == "labour_law" for row in rows)
    assert all(row["expected_article"] and row["expected_article_id"] for row in rows)
    assert all(row["expected_article_status"] == "machine-proposed, unapproved" for row in rows)
    assert all(row["label_status"] == "machine_proposed_unapproved" for row in rows)
    assert all(row["review_status"] == "needs_lawyer_review" for row in rows)
    assert all(row["expected_answer"] is None for row in rows)
    assert all(row["lawyer_approved_answer"] is None for row in rows)
    assert all(row["expected_sources"] == [] and row["expected_pin_cites"] == [] for row in rows)
    assert all(row["must_abstain_if_unverified"] is True for row in rows)
    assert all(row["release_eligible"] is False for row in rows)


if __name__ == "__main__":
    test_law14_machine_proposed_questions_are_unique_article_mapped_and_unapproved()
