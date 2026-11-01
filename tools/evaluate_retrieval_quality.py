#!/usr/bin/env python3
"""Score retrieval and citation quality only against lawyer-reviewed evaluation labels.

Input JSONL rows must contain a reviewed question and a corresponding run record.
Unreviewed question seeds are reported as excluded, never treated as negative examples.
Malformed records are reported and excluded rather than crashing or being scored as misses.
"""
import argparse
import json
import math
import re
import sys
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
    source_summary = run.get("source_summary")
    if source_summary is not None:
        if not isinstance(source_summary, list):
            errors.append("source_summary must be a list when supplied")
        else:
            summary_by_id = {}
            for index, item in enumerate(source_summary):
                if not isinstance(item, dict) or not _nonempty_string(item.get("source_id")):
                    errors.append(f"source_summary[{index}] must contain a non-empty source_id")
                    continue
                source_id = item["source_id"].strip()
                status = item.get("source_status")
                if status is not None and not _nonempty_string(status):
                    errors.append(f"source_summary[{index}].source_status must be non-empty when supplied")
                if source_id in summary_by_id and summary_by_id[source_id] != status:
                    errors.append("source_summary contains conflicting statuses for " + source_id)
                summary_by_id[source_id] = status
            if isinstance(citations, list):
                for citation in citations:
                    if not isinstance(citation, dict) or not _nonempty_string(citation.get("source_id")):
                        continue
                    source_id = citation["source_id"].strip()
                    if source_id not in summary_by_id:
                        errors.append("cited source is missing from source_summary: " + source_id)
                    elif summary_by_id[source_id] != "verified_operative_text" and run.get("used_unverified_source") is False:
                        errors.append("used_unverified_source is false but cited source is not verified: " + source_id)
    if "invalid_citation_indices" in run:
        invalid_indices = run["invalid_citation_indices"]
        if not isinstance(invalid_indices, list) or any(type(index) is not int or index < 1 for index in invalid_indices):
            errors.append("invalid_citation_indices must be a list of positive integers when supplied")
        elif len(set(invalid_indices)) != len(invalid_indices):
            errors.append("invalid_citation_indices must not contain duplicates")
    for field in ("abstained", "used_unverified_source"):
        if not isinstance(run.get(field), bool):
            errors.append(field + " must be an explicit boolean")
    return errors


def _unique_ids(values):
    return list(dict.fromkeys(x.strip() for x in values if _nonempty_string(x)))


def _effective_unverified_source(run):
    """Fail closed when a cited source lacks explicit verified-status evidence."""
    if run.get("used_unverified_source") is True:
        return True
    citations = run.get("citations") if isinstance(run.get("citations"), list) else []
    cited_ids = {
        citation["source_id"].strip()
        for citation in citations
        if isinstance(citation, dict) and _nonempty_string(citation.get("source_id"))
    }
    if not cited_ids:
        return False
    summary = run.get("source_summary")
    if not isinstance(summary, list):
        return True
    statuses = {
        item["source_id"].strip(): item.get("source_status")
        for item in summary
        if isinstance(item, dict) and _nonempty_string(item.get("source_id"))
    }
    return any(statuses.get(source_id) != "verified_operative_text" for source_id in cited_ids)


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
    source_status_evidence_missing_count = 0
    invalid_citation_index_count = 0
    invalid_citation_index_records = []
    expected_pin_cite_total = expected_pin_cite_correct = 0
    answerable_cases = answerable_with_expected_citation = 0
    citations_outside_retrieval = []
    abstention_cases = abstention_correct = unsafe_unverified_uses = 0
    for question, run in reviewed:
        expected_sources = set(_expected_source_ids(question))
        expected_pin_cites = question.get("expected_pin_cites") or []
        if run.get("citations") and not isinstance(run.get("source_summary"), list):
            source_status_evidence_missing_count += 1
        invalid_indices = run.get("invalid_citation_indices", [])
        invalid_citation_index_count += len(invalid_indices)
        if invalid_indices:
            invalid_citation_index_records.append({
                "question_id": question["id"],
                "indices": list(invalid_indices),
            })
        retrieved_source_ids = set(_unique_ids(run["retrieved_source_ids"]))
        cited_expected_sources = {
            citation["source_id"].strip()
            for citation in run["citations"]
            if citation["source_id"].strip() in expected_sources
            and citation["source_id"].strip() in retrieved_source_ids
        }
        if question["answerable"] is True:
            answerable_cases += 1
            if cited_expected_sources:
                answerable_with_expected_citation += 1
        for citation in run["citations"]:
            citation_total += 1
            cited_source_id = citation["source_id"].strip()
            is_retrieved = cited_source_id in retrieved_source_ids
            if not is_retrieved:
                citations_outside_retrieval.append({
                    "question_id": question["id"],
                    "source_id": cited_source_id,
                    "pin_cite": citation.get("pin_cite"),
                })
            if is_retrieved and cited_source_id in expected_sources:
                citation_correct += 1
            if expected_pin_cites:
                pin_cite_total += 1
                if is_retrieved and any(
                    cited_source_id == expected["source_id"]
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
            (citation["source_id"].strip(), citation.get("pin_cite"))
            for citation in run["citations"]
            if citation["source_id"].strip() in retrieved_source_ids
        }
        expected_pin_cite_total += len(expected_pairs)
        expected_pin_cite_correct += len(expected_pairs & actual_pairs)
        if question["answerable"] is False:
            abstention_cases += 1
            if run["abstained"] is True and run["used_unverified_source"] is not True:
                abstention_correct += 1
        if _effective_unverified_source(run) and run["abstained"] is not True:
            unsafe_unverified_uses += 1

    practice_area_counts = {}
    for question, _run in reviewed:
        area = question["practice_area"].strip()
        counts = practice_area_counts.setdefault(area, {"reviewed_cases": 0, "answerable_cases": 0,
                                                          "unanswerable_cases": 0})
        counts["reviewed_cases"] += 1
        counts["answerable_cases" if question["answerable"] else "unanswerable_cases"] += 1

    return {
        "reviewed_cases_scored": len(reviewed),
        "practice_area_counts": {area: practice_area_counts[area] for area in sorted(practice_area_counts)},
        "excluded_cases": excluded,
        "invalid_question_records": invalid_questions,
        "invalid_run_records": invalid_runs,
        "duplicate_question_ids": duplicate_question_ids,
        "duplicate_run_question_ids": duplicate_run_ids,
        "metrics": metrics,
        "citation_precision": round(citation_correct / (citation_total + invalid_citation_index_count), 4) if citation_total + invalid_citation_index_count else None,
        "citation_correct": citation_correct,
        "citation_count": citation_total + invalid_citation_index_count,
        "source_citation_count": citation_total,
        "invalid_citation_index_count": invalid_citation_index_count,
        "invalid_citation_index_records": invalid_citation_index_records,
        "citations_outside_retrieval": citations_outside_retrieval,
        "citations_outside_retrieval_count": len(citations_outside_retrieval),
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
        "source_status_evidence_missing_count": source_status_evidence_missing_count,
        "limitations": [
            "Scores cover only lawyer-reviewed cases with explicit expected source IDs and a matching valid run.",
            "Malformed records and duplicate question/run IDs are excluded and listed; resolve them before relying on a score.",
            "Metrics do not establish legal correctness, completeness, or current-law status.",
            "Review labels must be assigned by a qualified reviewer; this tool never generates ground truth.",
            "Pin-cite precision (pin_cite_accuracy) is scored only where reviewed expected_pin_cites are provided; expected_pin_cite_recall measures how many reviewed expected citation pairs were returned.",
            "Citation coverage measures the share of answerable reviewed cases that cite at least one expected source; it complements citation precision so answers with no citations are not silently omitted from the coverage view.",
            "Citations whose source IDs were not present in the retrieved source set count as incorrect and are listed; they do not contribute to citation coverage or expected pin-cite recall.",
            "Invalid visible citation indices are counted as incorrect citation markers and reported separately; they cannot improve citation precision.",
        ],
    }


def _retrieval_release_gate(report, args):
    """Evaluate explicitly configured quality and benchmark-coverage thresholds."""
    thresholds = {
        "recall_at_5": args.min_recall_at_5,
        "mrr_at_5": args.min_mrr_at_5,
        "citation_precision": args.min_citation_precision,
        "citation_coverage": args.min_citation_coverage,
        "expected_pin_cite_recall": args.min_expected_pin_cite_recall,
        "abstention_compliance": args.min_abstention_compliance,
    }
    enabled = (any(value is not None for value in thresholds.values())
               or any(getattr(args, name) is not None for name in (
                   "min_reviewed_cases", "min_practice_areas", "min_cases_per_practice_area",
                   "min_answerable_cases", "min_unanswerable_cases", "min_expected_pin_cites",
                   "max_excluded_cases", "max_unsafe_unverified_source_uses")))
    checks = []
    def add(metric, actual, operator, threshold):
        passed = actual is not None and (actual >= threshold if operator == ">=" else actual <= threshold)
        checks.append({"metric": metric, "operator": operator, "threshold": threshold,
                       "actual": actual, "passed": passed})

    if args.min_reviewed_cases is not None:
        add("reviewed_cases_scored", report["reviewed_cases_scored"], ">=", args.min_reviewed_cases)
    if args.min_practice_areas is not None:
        add("practice_area_count", len(report["practice_area_counts"]), ">=", args.min_practice_areas)
    if args.min_cases_per_practice_area is not None:
        for area, counts in report["practice_area_counts"].items():
            add("cases_per_practice_area:" + area, counts["reviewed_cases"], ">=",
                args.min_cases_per_practice_area)
    if args.min_answerable_cases is not None:
        add("answerable_reviewed_cases", report["answerable_reviewed_cases"], ">=", args.min_answerable_cases)
    if args.min_unanswerable_cases is not None:
        add("unanswerable_reviewed_cases", report["unanswerable_reviewed_cases"], ">=",
            args.min_unanswerable_cases)
    if args.min_expected_pin_cites is not None:
        add("expected_pin_cite_count", report["expected_pin_cite_count"], ">=",
            args.min_expected_pin_cites)
    for metric, threshold in thresholds.items():
        if threshold is not None:
            actual = report["metrics"].get(metric) if metric in {"recall_at_5", "mrr_at_5"} else report.get(metric)
            add(metric, actual, ">=", threshold)
    if args.max_excluded_cases is not None:
        add("excluded_cases", len(report["excluded_cases"]), "<=", args.max_excluded_cases)
    if args.max_unsafe_unverified_source_uses is not None:
        add("unsafe_unverified_source_uses", report["unsafe_unverified_source_uses"], "<=",
            args.max_unsafe_unverified_source_uses)
    return {"enabled": enabled, "passed": all(item["passed"] for item in checks) if enabled else None,
            "checks": checks}


def _write_report(path, rendered):
    """Create a new report without ever overwriting prior evaluation evidence."""
    target = Path(path)
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-reviewed-cases", type=int)
    parser.add_argument("--min-practice-areas", type=int)
    parser.add_argument("--min-cases-per-practice-area", type=int)
    parser.add_argument("--min-answerable-cases", type=int)
    parser.add_argument("--min-unanswerable-cases", type=int)
    parser.add_argument("--min-expected-pin-cites", type=int)
    parser.add_argument("--min-recall-at-5", type=float)
    parser.add_argument("--min-mrr-at-5", type=float)
    parser.add_argument("--min-citation-precision", type=float)
    parser.add_argument("--min-citation-coverage", type=float)
    parser.add_argument("--min-expected-pin-cite-recall", type=float)
    parser.add_argument("--min-abstention-compliance", type=float)
    parser.add_argument("--max-excluded-cases", type=int)
    parser.add_argument("--max-unsafe-unverified-source-uses", type=int)
    args = parser.parse_args(argv)
    for name in ("min_reviewed_cases", "min_practice_areas", "min_cases_per_practice_area",
                 "min_answerable_cases", "min_unanswerable_cases", "min_expected_pin_cites",
                 "max_excluded_cases", "max_unsafe_unverified_source_uses"):
        value = getattr(args, name)
        if value is not None and value < 0:
            parser.error("--" + name.replace("_", "-") + " must be a non-negative integer")
    for name in ("min_reviewed_cases", "min_practice_areas", "min_cases_per_practice_area",
                 "min_answerable_cases", "min_unanswerable_cases", "min_expected_pin_cites"):
        value = getattr(args, name)
        if value is not None and value < 1:
            parser.error("--" + name.replace("_", "-") + " must be a positive integer")
    for name in ("min_recall_at_5", "min_mrr_at_5", "min_citation_precision",
                 "min_citation_coverage", "min_expected_pin_cite_recall", "min_abstention_compliance"):
        value = getattr(args, name)
        if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)
                                  or not 0 <= value <= 1):
            parser.error("--" + name.replace("_", "-") + " must be a finite number between 0 and 1")
    quality_thresholds = (args.min_recall_at_5, args.min_mrr_at_5, args.min_citation_precision,
                          args.min_citation_coverage, args.min_expected_pin_cite_recall,
                          args.min_abstention_compliance)
    if any(value is not None for value in quality_thresholds):
        if args.min_reviewed_cases is None:
            parser.error("quality thresholds require --min-reviewed-cases")
        if args.min_practice_areas is None or args.min_cases_per_practice_area is None:
            parser.error("quality thresholds require --min-practice-areas and --min-cases-per-practice-area")
    if args.min_citation_coverage is not None and args.min_answerable_cases is None:
        parser.error("--min-citation-coverage requires --min-answerable-cases")
    if args.min_expected_pin_cite_recall is not None and args.min_expected_pin_cites is None:
        parser.error("--min-expected-pin-cite-recall requires --min-expected-pin-cites")
    if args.min_abstention_compliance is not None and args.min_unanswerable_cases is None:
        parser.error("--min-abstention-compliance requires --min-unanswerable-cases")
    result = score_evaluation(_load_jsonl(args.questions), _load_jsonl(args.runs))
    result["release_gate"] = _retrieval_release_gate(result, args)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            _write_report(args.output, rendered)
        except FileExistsError:
            print(f"evaluation report refused: output already exists: {args.output}; choose a new path to preserve prior results", file=sys.stderr)
            return 2
    print(rendered, end="")
    if result["release_gate"]["enabled"] and not result["release_gate"]["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
