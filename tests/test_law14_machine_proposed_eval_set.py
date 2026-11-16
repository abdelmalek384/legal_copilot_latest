"""Structural checks only for the unapproved Law 14/2025 retrieval-question drafts."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "tests" / "legal_eval" / "law_14_2025_machine_proposed_questions.draft.jsonl"


def test_law14_machine_proposed_questions_are_unique_article_mapped_and_unapproved():
    from tools.validate_law14_eval_draft import (
        _reject_duplicate_json_keys, read_jsonl_with_digest, read_regular_file, validate_rows,
    )

    rows, dataset_sha256 = read_jsonl_with_digest(DATASET)
    baseline_path = ROOT / "docs" / "legal_evidence" / "law14_2025_retrieval_baseline_unreviewed.json"
    baseline = json.loads(
        read_regular_file(baseline_path).decode("utf-8"),
        object_pairs_hook=_reject_duplicate_json_keys,
    )
    assert baseline["dataset_sha256"] == dataset_sha256
    assert baseline["status"] == "unreviewed_not_scored"
    assert baseline["answer_keys_approved"] == 0
    assert all(value is None for value in baseline["metrics"].values())
    report = validate_rows(rows)
    assert report["valid"], report["errors"]
    assert report["trust_boundary"].startswith("Structural validation only")
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
