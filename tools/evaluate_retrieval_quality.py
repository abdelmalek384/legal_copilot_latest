#!/usr/bin/env python3
"""Score retrieval and citation quality only against lawyer-reviewed evaluation labels.

Input JSONL rows must contain a reviewed question and a corresponding run record.
Unreviewed question seeds are reported as excluded, never treated as negative examples.
Malformed records are reported and excluded rather than crashing or being scored as misses.
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTIONS = ROOT / "tests" / "legal_eval" / "practice_questions.seed.jsonl"
DEFAULT_RUNS = ROOT / "tests" / "legal_eval" / "runs.example.jsonl"
REVIEWED_STATES = {"lawyer_reviewed", "approved_for_evaluation"}
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _valid_calendar_date(value):
    if not isinstance(value, str) or not _DATE_RE.fullmatch(value):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _expected_source_ids(question):
    """Support the seed schema's expected_sources and the evaluator's explicit ID field."""
    if "expected_source_ids" in question and "expected_sources" in question:
        if question["expected_source_ids"] != question["expected_sources"]:
            return None
        return question["expected_source_ids"]
    return question.get("expected_source_ids", question.get("expected_sources"))


def validate_reviewed_question(question):
    """Return validation errors; no labels are inferred or generated."""
    if not isinstance(question, dict):
        return ["question record must be a JSON object"]
    errors = []
    if question.get("review_status") not in REVIEWED_STATES:
        return ["question is not marked lawyer_reviewed/approved_for_evaluation"]
    for field in ("id", "practice_area", "question_ar"):
        if not _nonempty_string(question.get(field)):
            errors.append("missing or invalid " + field)
    if not _nonempty_string(question.get("reviewer_name")):
        errors.append("reviewer_name is required")
    if not _valid_calendar_date(question.get("review_date")):
        errors.append("review_date must be a real YYYY-MM-DD calendar date")
    expected = _expected_source_ids(question)
    if (not isinstance(expected, list) or not expected
            or not all(_nonempty_string(x) for x in expected)):
        errors.append("expected_source_ids/expected_sources must be a non-empty list of reviewed source IDs")
    if "expected_source_ids" in question and "expected_sources" in question and question["expected_source_ids"] != question["expected_sources"]:
        errors.append("expected_source_ids and expected_sources conflict; keep one canonical reviewed source list")
    pin_cites = question.get("expected_pin_cites")
    if pin_cites is not None:
        if not isinstance(pin_cites, list):
            errors.append("expected_pin_cites must be a list when supplied")
        else:
            for index, item in enumerate(pin_cites):
                if (not isinstance(item, dict)
                        or not _nonempty_string(item.get("source_id"))
                        or not _nonempty_string(item.get("pin_cite"))):
                    errors.append(f"expected_pin_cites[{index}] must contain non-empty source_id and pin_cite strings")
    if not isinstance(question.get("answerable"), bool):
        errors.append("answerable must be an explicit boolean")
    if question.get("must_abstain_if_unverified") is not True:
        errors.append("must_abstain_if_unverified must remain true")
    return errors


def validate_run_record(run):
    """Return errors for a run record so malformed results are never silently scored."""
    if not isinstance(run, dict):
        return ["run record must be a JSON object"]
    errors = []
    if not _nonempty_string(run.get("question_id")):
        errors.append("question_id must be a non-empty string")
    retrieved = run.get("retrieved_source_ids")
    if (not isinstance(retrieved, list)
            or not all(_nonempty_string(source_id) for source_id in retrieved)):
        errors.append("retrieved_source_ids must be a list of non-empty source ID strings")
    citations = run.get("citations")
    if not isinstance(citations, list):
        errors.append("citations must be a list")
    else:
        for index, citation in enumerate(citations):
            if not isinstance(citation, dict) or not _nonempty_string(citation.get("source_id")):
                errors.append(f"citations[{index}] must contain a non-empty source_id")
                continue
            if "pin_cite" in citation and not _nonempty_string(citation.get("pin_cite")):
                errors.append(f"citations[{index}].pin_cite must be a non-empty string when supplied")
    for field in ("abstained", "used_unverified_source"):
        if not isinstance(run.get(field), bool):
            errors.append(field + " must be an explicit boolean")
    return errors


def _unique_ids(values):
    return list(dict.fromkeys(x.strip() for x in values if _nonempty_string(x)))


def score_evaluation(questions, runs, k_values=(1, 3, 5)):
    """Calculate retrieval, citation, and abstention metrics on reviewed cases only.

    Each run row: {"question_id": "...", "retrieved_source_ids": [...],
    "citations": [{"source_id": "...", "pin_cite": "Article 12"}],
    "abstained": true|false, "used_unverified_source": true|false}.
    Duplicate question/run IDs are excluded instead of choosing an arbitrary record.
    """
    if not isinstance(questions, list) or not isinstance(runs, list):
        raise ValueError("questions and runs must each be a list of JSON objects")
    if (not isinstance(k_values, (list, tuple)) or not k_values
            or any(type(k) is not int or k < 1 for k in k_values)):
        raise ValueError("k_values must contain positive integers")

    question_by_id = {}
    question_counts = {}
    invalid_questions = []
    for index, question in enumerate(questions, start=1):
        errors = validate_reviewed_question(question)
        qid = question.get("id") if isinstance(question, dict) else None
        if not isinstance(qid, str) or not qid.strip():
            invalid_questions.append({"record": index, "question_id": None, "reasons": errors or ["id must be a non-empty string"]})
            continue
        question_counts[qid] = question_counts.get(qid, 0) + 1
        if errors:
            invalid_questions.append({"record": index, "question_id": qid, "reasons": errors})
        question_by_id[qid] = question

    duplicate_question_ids = sorted(qid for qid, count in question_counts.items() if count > 1)
    for qid in duplicate_question_ids:
        question_by_id.pop(qid, None)

    run_by_id = {}
    run_counts = {}
    invalid_runs = []
    invalid_run_ids = set()
    for index, run in enumerate(runs, start=1):
        errors = validate_run_record(run)
        qid = run.get("question_id") if isinstance(run, dict) else None
        if errors:
            invalid_runs.append({"record": index, "question_id": qid if isinstance(qid, str) else None, "reasons": errors})
            if isinstance(qid, str) and qid.strip():
                invalid_run_ids.add(qid)
            continue
        run_counts[qid] = run_counts.get(qid, 0) + 1
        run_by_id[qid] = run

    duplicate_run_ids = sorted(qid for qid, count in run_counts.items() if count > 1)
    for qid in duplicate_run_ids:
        run_by_id.pop(qid, None)

    reviewed = []
    excluded = []
    for qid, question in question_by_id.items():
        if qid in duplicate_question_ids:
            excluded.append({"question_id": qid, "reasons": ["duplicate question ID; resolve the reviewed labels before scoring"]})
        elif validate_reviewed_question(question):
            excluded.append({"question_id": qid, "reasons": validate_reviewed_question(question)})
        elif qid in duplicate_run_ids:
            excluded.append({"question_id": qid, "reasons": ["duplicate run records; resolve the runs before scoring"]})
        elif qid in invalid_run_ids:
            excluded.append({"question_id": qid, "reasons": ["run record is malformed; see invalid_run_records"]})
        elif qid not in run_by_id:
            excluded.append({"question_id": qid, "reasons": ["no valid run record"]})
        else:
            reviewed.append((question, run_by_id[qid]))
    for qid in duplicate_question_ids:
        if not any(item["question_id"] == qid for item in excluded):
            excluded.append({"question_id": qid, "reasons": ["duplicate question ID; resolve the reviewed labels before scoring"]})
    metrics = {}
    for k in k_values:
        recall_values = []
        reciprocal_ranks = []
        for question, run in reviewed:
            expected = set(_expected_source_ids(question))
            ranked = _unique_ids(run["retrieved_source_ids"])
            top_k = set(ranked[:k])
            recall_values.append(len(expected & top_k) / len(expected))
            rank = next((index for index, source_id in enumerate(ranked, 1) if source_id in expected), None)
            reciprocal_ranks.append(1.0 / rank if rank is not None and rank <= k else 0.0)
        metrics[f"recall_at_{k}"] = round(sum(recall_values) / len(recall_values), 4) if reviewed else None
        metrics[f"mrr_at_{k}"] = round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4) if reviewed else None

    citation_total = citation_correct = pin_cite_total = pin_cite_correct = 0
    expected_pin_cite_total = expected_pin_cite_correct = 0
    answerable_cases = answerable_with_expected_citation = 0
    abstention_cases = abstention_correct = unsafe_unverified_uses = 0
    for question, run in reviewed:
        expected_sources = set(_expected_source_ids(question))
        expected_pin_cites = question.get("expected_pin_cites") or []
        cited_expected_sources = {
            citation["source_id"]
            for citation in run["citations"]
            if citation["source_id"] in expected_sources
        }
        if question["answerable"] is True:
            answerable_cases += 1
            if cited_expected_sources:
                answerable_with_expected_citation += 1
        for citation in run["citations"]:
            citation_total += 1
            if citation["source_id"] in expected_sources:
                citation_correct += 1
            if expected_pin_cites:
                pin_cite_total += 1
                if any(
                    citation["source_id"] == expected["source_id"]
                    and citation.get("pin_cite") == expected["pin_cite"]
                    for expected in expected_pin_cites
                ):
                    pin_cite_correct += 1
        # Recall is measured against the reviewer's expected citation pairs, so
        # returning no citations cannot yield an undefined or perfect score.
        expected_pairs = {
            (item["source_id"], item["pin_cite"])
            for item in expected_pin_cites
        }
        actual_pairs = {
            (citation["source_id"], citation.get("pin_cite"))
            for citation in run["citations"]
        }
        expected_pin_cite_total += len(expected_pairs)
        expected_pin_cite_correct += len(expected_pairs & actual_pairs)
        if question["answerable"] is False:
            abstention_cases += 1
            if run["abstained"] is True and run["used_unverified_source"] is not True:
                abstention_correct += 1
        if run["used_unverified_source"] is True and run["abstained"] is not True:
            unsafe_unverified_uses += 1

    return {
        "reviewed_cases_scored": len(reviewed),
        "excluded_cases": excluded,
        "invalid_question_records": invalid_questions,
        "invalid_run_records": invalid_runs,
        "duplicate_question_ids": duplicate_question_ids,
        "duplicate_run_question_ids": duplicate_run_ids,
        "metrics": metrics,
        "citation_precision": round(citation_correct / citation_total, 4) if citation_total else None,
        "citation_correct": citation_correct,
        "citation_count": citation_total,
        "citation_coverage": round(answerable_with_expected_citation / answerable_cases, 4) if answerable_cases else None,
        "answerable_cases_with_expected_citation": answerable_with_expected_citation,
        "answerable_reviewed_cases": answerable_cases,
        "pin_cite_accuracy": round(pin_cite_correct / pin_cite_total, 4) if pin_cite_total else None,
        "pin_cite_correct": pin_cite_correct,
        "pin_cite_count": pin_cite_total,
        "expected_pin_cite_recall": round(expected_pin_cite_correct / expected_pin_cite_total, 4) if expected_pin_cite_total else None,
        "expected_pin_cites_found": expected_pin_cite_correct,
        "expected_pin_cite_count": expected_pin_cite_total,
        "abstention_compliance": round(abstention_correct / abstention_cases, 4) if abstention_cases else None,
        "abstention_correct": abstention_correct,
        "unanswerable_reviewed_cases": abstention_cases,
        "unsafe_unverified_source_uses": unsafe_unverified_uses,
        "limitations": [
            "Scores cover only lawyer-reviewed cases with explicit expected source IDs and a matching valid run.",
            "Malformed records and duplicate question/run IDs are excluded and listed; resolve them before relying on a score.",
            "Metrics do not establish legal correctness, completeness, or current-law status.",
            "Review labels must be assigned by a qualified reviewer; this tool never generates ground truth.",
            "Pin-cite precision (pin_cite_accuracy) is scored only where reviewed expected_pin_cites are provided; expected_pin_cite_recall measures how many reviewed expected citation pairs were returned.",
            "Citation coverage measures the share of answerable reviewed cases that cite at least one expected source; it complements citation precision so answers with no citations are not silently omitted from the coverage view.",
        ],
    }


def _write_report(path, rendered):
    """Create a new report without ever overwriting prior evaluation evidence."""
    target = Path(path)
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = score_evaluation(_load_jsonl(args.questions), _load_jsonl(args.runs))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            _write_report(args.output, rendered)
        except FileExistsError:
            print(f"evaluation report refused: output already exists: {args.output}; choose a new path to preserve prior results", file=sys.stderr)
            return 2
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    main()
