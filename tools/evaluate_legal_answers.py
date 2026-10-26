#!/usr/bin/env python3
"""Score citation and abstention behavior only on explicitly lawyer-approved questions.

This tool does not judge semantic legal correctness. It refuses to score unreviewed
draft questions and reports source-ID recall, pin-citation recall, citation presence,
and abstention agreement against a lawyer-authored answerability label.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

APPROVED = "lawyer_approved"


class EvaluationError(ValueError):
    pass


def read_jsonl(path):
    rows = []
    for line_no, raw in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"{path}:{line_no}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise EvaluationError(f"{path}:{line_no}: each JSONL row must be an object")
        rows.append(row)
    return rows


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _string_list(value, label, question_id):
    if not isinstance(value, list) or any(not _nonempty(x) for x in value):
        raise EvaluationError(f"{question_id}: {label} must be a list of non-empty strings")
    cleaned = [x.strip() for x in value]
    if len(cleaned) != len(set(cleaned)):
        raise EvaluationError(f"{question_id}: {label} contains duplicates")
    return cleaned


def _pin_cites(value, label, question_id):
    if not isinstance(value, list):
        raise EvaluationError(f"{question_id}: {label} must be a list")
    pairs = []
    for item in value:
        if not isinstance(item, dict) or not _nonempty(item.get("source_id")) or not _nonempty(item.get("pin_cite")):
            raise EvaluationError(f"{question_id}: each {label} item needs source_id and pin_cite")
        pair = (item["source_id"].strip(), item["pin_cite"].strip())
        if pair in pairs:
            raise EvaluationError(f"{question_id}: {label} contains duplicate pin citations")
        pairs.append(pair)
    return pairs


def _validate_reviewed_question(row):
    qid = row.get("id")
    if not _nonempty(qid):
        raise EvaluationError("question id must be a non-empty string")
    if row.get("review_status") != APPROVED:
        raise EvaluationError(f"{qid}: only review_status={APPROVED!r} can be scored")
    if not _nonempty(row.get("reviewer_name")):
        raise EvaluationError(f"{qid}: reviewer_name is required")
    review_date = row.get("review_date")
    if not isinstance(review_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", review_date):
        raise EvaluationError(f"{qid}: review_date must be ISO YYYY-MM-DD")
    try:
        reviewed_on = date.fromisoformat(review_date)
    except ValueError:
        raise EvaluationError(f"{qid}: review_date must be a real calendar date in YYYY-MM-DD form")
    if reviewed_on > date.today():
        raise EvaluationError(f"{qid}: review_date cannot be in the future")
    if not isinstance(row.get("answerable"), bool):
        raise EvaluationError(f"{qid}: lawyer-reviewed answerable must be true or false")
    if not _nonempty(row.get("expected_answer")):
        raise EvaluationError(f"{qid}: expected_answer is required, including for approved abstention cases")
    sources = _string_list(row.get("expected_sources"), "expected_sources", qid)
    pins = _pin_cites(row.get("expected_pin_cites"), "expected_pin_cites", qid)
    if row["answerable"] and not sources:
        raise EvaluationError(f"{qid}: answerable questions require at least one expected source")
    if row["answerable"] and not pins:
        raise EvaluationError(f"{qid}: answerable questions require at least one expected pin citation")
    if not row["answerable"] and row.get("must_abstain_if_unverified", True) is not True:
        raise EvaluationError(f"{qid}: unanswerable questions must require abstention")
    return sources, pins


def _validate_result(row):
    qid = row.get("id")
    if not _nonempty(qid):
        raise EvaluationError("result id must be a non-empty string")
    if not isinstance(row.get("abstained"), bool):
        raise EvaluationError(f"{qid}: result abstained must be true or false")
    sources = _string_list(row.get("cited_sources", []), "cited_sources", qid)
    pins = _pin_cites(row.get("cited_pin_cites", []), "cited_pin_cites", qid)
    return sources, pins


def _ratio(numerator, denominator):
    return round(numerator / denominator, 4) if denominator else None


def evaluate(question_rows, result_rows):
    question_map = {}
    for row in question_rows:
        qid = row.get("id")
        if not _nonempty(qid):
            raise EvaluationError("question id must be a non-empty string")
        if qid in question_map:
            raise EvaluationError(f"duplicate question id: {qid}")
        question_map[qid] = row

    result_map = {}
    for row in result_rows:
        qid = row.get("id")
        if not _nonempty(qid):
            raise EvaluationError("result id must be a non-empty string")
        if qid in result_map:
            raise EvaluationError(f"duplicate result id: {qid}")
        result_map[qid] = row

    reviewed = {}
    excluded = []
    for qid, row in question_map.items():
        if row.get("review_status") != APPROVED:
            excluded.append(qid)
            continue
        reviewed[qid] = _validate_reviewed_question(row)
    if not reviewed:
        raise EvaluationError(f"no questions with review_status={APPROVED!r}; drafts are not scoreable")
    unknown = sorted(set(result_map) - set(question_map))
    if unknown:
        raise EvaluationError("results contain unknown question ids: " + ", ".join(unknown))
    missing = sorted(set(reviewed) - set(result_map))
    if missing:
        raise EvaluationError("missing results for lawyer-approved questions: " + ", ".join(missing))

    rows = []
    by_area = defaultdict(list)
    for qid, (expected_sources, expected_pins) in reviewed.items():
        q = question_map[qid]
        actual_sources, actual_pins = _validate_result(result_map[qid])
        source_hits = len(set(expected_sources) & set(actual_sources))
        pin_hits = len(set(expected_pins) & set(actual_pins))
        expected_abstain = not q["answerable"]
        abstention_correct = result_map[qid]["abstained"] == expected_abstain
        citation_present = bool(actual_sources or actual_pins)
        item = {
            "id": qid,
            "practice_area": q.get("practice_area", "unspecified"),
            "answerable": q["answerable"],
            "expected_abstain": expected_abstain,
            "actual_abstained": result_map[qid]["abstained"],
            "abstention_correct": abstention_correct,
            "expected_source_count": len(expected_sources),
            "cited_source_count": len(actual_sources),
            "matched_expected_source_count": source_hits,
            "unexpected_source_count": len(set(actual_sources) - set(expected_sources)),
            "source_recall": _ratio(source_hits, len(expected_sources)),
            "source_precision": _ratio(source_hits, len(actual_sources)),
            "expected_pin_cite_count": len(expected_pins),
            "cited_pin_cite_count": len(actual_pins),
            "matched_expected_pin_cite_count": pin_hits,
            "unexpected_pin_cite_count": len(set(actual_pins) - set(expected_pins)),
            "pin_cite_recall": _ratio(pin_hits, len(expected_pins)),
            "pin_cite_precision": _ratio(pin_hits, len(actual_pins)),
            "citation_present": citation_present,
        }
        rows.append(item)
        by_area[item["practice_area"]].append(item)

    def summarize(items):
        n = len(items)
        answerable = [x for x in items if x["answerable"]]
        abstention_cases = [x for x in items if not x["answerable"]]
        return {
            "questions_scored": n,
            "answerable_questions": len(answerable),
            "abstention_cases": len(abstention_cases),
            "source_recall": _ratio(sum(x["matched_expected_source_count"] for x in answerable),
                                    sum(x["expected_source_count"] for x in answerable)),
            "source_precision": _ratio(sum(x["matched_expected_source_count"] for x in answerable),
                                        sum(x["cited_source_count"] for x in answerable)),
            "pin_cite_recall": _ratio(sum(x["matched_expected_pin_cite_count"] for x in answerable),
                                      sum(x["expected_pin_cite_count"] for x in answerable)),
            "pin_cite_precision": _ratio(sum(x["matched_expected_pin_cite_count"] for x in answerable),
                                         sum(x["cited_pin_cite_count"] for x in answerable)),
            "answerable_citation_presence": _ratio(sum(x["citation_present"] for x in answerable), len(answerable)),
            "abstention_accuracy": _ratio(sum(x["abstention_correct"] for x in items), n),
            "unanswerable_abstention_recall": _ratio(sum(x["actual_abstained"] for x in abstention_cases),
                                                       len(abstention_cases)),
            "unanswerable_citation_rate": _ratio(sum(x["citation_present"] for x in abstention_cases),
                                                  len(abstention_cases)),
        }

    return {
        "schema_version": 1,
        "evaluation_scope": "citation_and_abstention_behavior_only",
        "semantic_legal_correctness_scored": False,
        "approval_gate": APPROVED,
        "questions_available": len(question_map),
        "questions_scored": len(rows),
        "unreviewed_questions_excluded": len(excluded),
        "excluded_question_ids": sorted(excluded),
        "overall": summarize(rows),
        "by_practice_area": {area: summarize(items) for area, items in sorted(by_area.items())},
        "results": rows,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", required=True, help="Lawyer-reviewed question JSONL")
    parser.add_argument("--results", required=True, help="Model output JSONL, one record per question")
    parser.add_argument("--out", help="Write report JSON here; default is stdout")
    args = parser.parse_args(argv)
    try:
        report = evaluate(read_jsonl(args.questions), read_jsonl(args.results))
    except (OSError, EvaluationError) as exc:
        print(f"evaluation refused: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
