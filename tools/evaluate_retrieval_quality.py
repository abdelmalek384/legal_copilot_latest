#!/usr/bin/env python3
"""Score retrieval and citation quality only against lawyer-reviewed evaluation labels.

Input JSONL rows must contain a reviewed question and a corresponding run record.
Unreviewed question seeds are reported as excluded, never treated as negative examples.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTIONS = ROOT / "tests" / "legal_eval" / "practice_questions.seed.jsonl"
DEFAULT_RUNS = ROOT / "tests" / "legal_eval" / "runs.example.jsonl"
REVIEWED_STATES = {"lawyer_reviewed", "approved_for_evaluation"}


def _load_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def validate_reviewed_question(question):
    """Return validation errors; no labels are inferred or generated."""
    errors = []
    if question.get("review_status") not in REVIEWED_STATES:
        return ["question is not marked lawyer_reviewed/approved_for_evaluation"]
    for field in ("id", "practice_area", "question_ar"):
        if not question.get(field):
            errors.append("missing " + field)
    if not question.get("reviewer_name") or not question.get("review_date"):
        errors.append("reviewer_name and review_date are required")
    expected = question.get("expected_source_ids")
    if not isinstance(expected, list) or not expected or not all(isinstance(x, str) and x.strip() for x in expected):
        errors.append("expected_source_ids must be a non-empty list of reviewed source IDs")
    if question.get("answerable") not in (True, False):
        errors.append("answerable must be an explicit boolean")
    if question.get("must_abstain_if_unverified") is not True:
        errors.append("must_abstain_if_unverified must remain true")
    pin_cites = question.get("expected_pin_cites")
    if pin_cites is not None and not isinstance(pin_cites, list):
        errors.append("expected_pin_cites must be a list when supplied")
    return errors


def _unique_ids(values):
    return list(dict.fromkeys(x for x in values if isinstance(x, str) and x.strip()))


def score_evaluation(questions, runs, k_values=(1, 3, 5)):
    """Calculate retrieval, citation, and abstention metrics on reviewed cases only.

    Each run row: {"question_id": "...", "retrieved_source_ids": [...],
    "citations": [{"source_id": "...", "pin_cite": "Article 12"}],
    "abstained": true|false, "used_unverified_source": true|false}.
    """
    question_by_id = {q.get("id"): q for q in questions if q.get("id")}
    run_by_id = {}
    duplicate_runs = []
    for run in runs:
        qid = run.get("question_id")
        if not qid:
            continue
        if qid in run_by_id:
            duplicate_runs.append(qid)
        run_by_id[qid] = run

    reviewed = []
    excluded = []
    for qid, question in question_by_id.items():
        errors = validate_reviewed_question(question)
        if errors:
            excluded.append({"question_id": qid, "reasons": errors})
        elif qid not in run_by_id:
            excluded.append({"question_id": qid, "reasons": ["no run record"]})
        else:
            reviewed.append((question, run_by_id[qid]))

    metrics = {}
    for k in k_values:
        hits = 0
        reciprocal_ranks = []
        for question, run in reviewed:
            expected = set(question["expected_source_ids"])
            ranked = _unique_ids(run.get("retrieved_source_ids", []))
            rank = next((index for index, source_id in enumerate(ranked, 1) if source_id in expected), None)
            if rank is not None and rank <= k:
                hits += 1
            reciprocal_ranks.append(1.0 / rank if rank is not None and rank <= k else 0.0)
        metrics[f"recall_at_{k}"] = round(hits / len(reviewed), 4) if reviewed else None
        metrics[f"mrr_at_{k}"] = round(sum(reciprocal_ranks) / len(reviewed), 4) if reviewed else None

    citation_total = citation_correct = pin_cite_total = pin_cite_correct = 0
    abstention_cases = abstention_correct = unsafe_unverified_uses = 0
    for question, run in reviewed:
        expected_sources = set(question["expected_source_ids"])
        for citation in run.get("citations", []):
            citation_total += 1
            if citation.get("source_id") in expected_sources:
                citation_correct += 1
            expected_pin_cites = question.get("expected_pin_cites") or []
            if expected_pin_cites:
                pin_cite_total += 1
                if any(
                    citation.get("source_id") == expected.get("source_id")
                    and citation.get("pin_cite") == expected.get("pin_cite")
                    for expected in expected_pin_cites
                ):
                    pin_cite_correct += 1
        if question["answerable"] is False:
            abstention_cases += 1
            if run.get("abstained") is True and run.get("used_unverified_source") is not True:
                abstention_correct += 1
        if run.get("used_unverified_source") is True and run.get("abstained") is not True:
            unsafe_unverified_uses += 1

    count = len(reviewed)
    return {
        "reviewed_cases_scored": count,
        "excluded_cases": excluded,
        "duplicate_run_question_ids": sorted(set(duplicate_runs)),
        "metrics": metrics,
        "citation_precision": round(citation_correct / citation_total, 4) if citation_total else None,
        "citation_correct": citation_correct,
        "citation_count": citation_total,
        "pin_cite_accuracy": round(pin_cite_correct / pin_cite_total, 4) if pin_cite_total else None,
        "pin_cite_correct": pin_cite_correct,
        "pin_cite_count": pin_cite_total,
        "abstention_compliance": round(abstention_correct / abstention_cases, 4) if abstention_cases else None,
        "abstention_correct": abstention_correct,
        "unanswerable_reviewed_cases": abstention_cases,
        "unsafe_unverified_source_uses": unsafe_unverified_uses,
        "limitations": [
            "Scores cover only lawyer-reviewed cases with explicit expected source IDs and a matching run.",
            "Metrics do not establish legal correctness, completeness, or current-law status.",
            "Review labels must be assigned by a qualified reviewer; this tool never generates ground truth.",
            "Pin-cite accuracy is scored only where reviewed expected_pin_cites are provided.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = score_evaluation(_load_jsonl(args.questions), _load_jsonl(args.runs))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
