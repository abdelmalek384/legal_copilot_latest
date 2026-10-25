"""Structural checks for the unreviewed Egyptian labour-law draft benchmark.

These checks validate dataset shape only. They do not validate legal answers or law coverage.
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSONL = ROOT / "tests" / "legal_eval" / "labour_law_questions.draft.jsonl"
CSV_FILE = ROOT / "tests" / "legal_eval" / "labour_law_questions_for_lawyer.csv"


def test_labour_law_draft_questions_are_unreviewed_and_well_formed():
    records = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(records) == 61
    ids = [record["id"] for record in records]
    assert len(set(ids)) == len(ids)
    assert all(record["practice_area"] == "labour_law" for record in records)
    assert all(record["question_ar"].strip() for record in records)
    assert all(record["expected_answer"] is None for record in records)
    assert all(record["expected_sources"] == [] for record in records)
    assert all(record["review_status"] == "needs_lawyer_review" for record in records)
    assert all(record["reviewer_name"] is None and record["review_date"] is None for record in records)
    counts = Counter(record["id"][-1] for record in records)
    assert counts == {"D": 20, "P": 10, "C": 10, "S": 10, "T": 6, "X": 5}


def test_lawyer_csv_matches_jsonl_questions_without_filling_answer_key():
    records = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    with CSV_FILE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(records)
    assert [row["id"] for row in rows] == [record["id"] for record in records]
    assert all(not row["الإجابة الصحيحة (يملؤها المحامي)"].strip() for row in rows)
    assert all(not row["المصدر: القانون/المادة/عدد الجريدة"].strip() for row in rows)
    assert all(not row["اسم المراجع"].strip() and not row["تاريخ المراجعة"].strip() for row in rows)
