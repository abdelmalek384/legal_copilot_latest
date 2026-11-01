#!/usr/bin/env python3
"""Score citation and abstention behavior only on explicitly lawyer-approved questions.

This tool does not judge semantic legal correctness. It refuses to score unreviewed
draft questions and reports source-ID recall, pin-citation recall, citation presence,
and abstention agreement against a lawyer-authored answerability label.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

try:
    from tools.evaluate_legal_answer_reviews import validate_reviewer_registry
except ModuleNotFoundError:  # supports direct execution as python tools/evaluate_legal_answers.py
    from evaluate_legal_answer_reviews import validate_reviewer_registry

APPROVED = "lawyer_approved"


class EvaluationError(ValueError):
    pass


def _parse_jsonl_text(text, path):
    rows = []
    for line_no, raw in enumerate(text.splitlines(), 1):
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


def read_jsonl(path):
    return _parse_jsonl_text(Path(path).read_text(encoding="utf-8-sig"), path)


def _read_jsonl_with_provenance(path):
    raw = Path(path).read_bytes()
    rows = _parse_jsonl_text(raw.decode("utf-8-sig"), path)
    return rows, {"sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}


def _report_provenance(inputs):
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "inputs": inputs,
        "limitations": [
            "SHA-256 values identify the exact input bytes used; they do not prove authorship, reviewer qualification, or legal correctness.",
            "Input paths and input contents are intentionally omitted from this provenance block.",
        ],
    }


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


def _valid_review_evidence_url(value):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or any(ch.isspace() for ch in value):
        return False
    try:
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username is not None
                or parsed.password is not None or parsed.query or parsed.fragment):
            return False
        _ = parsed.port
        return True
    except ValueError:
        return False


def _validate_reviewed_question(row, approved_reviewers):
    qid = row.get("id")
    if not _nonempty(qid):
        raise EvaluationError("question id must be a non-empty string")
    if row.get("review_status") != APPROVED:
        raise EvaluationError(f"{qid}: only review_status={APPROVED!r} can be scored")
    practice_area = row.get("practice_area", "unspecified")
    if not _nonempty(practice_area):
        raise EvaluationError(f"{qid}: practice_area must be a non-empty string when supplied")
    as_of_text = row.get("as_of_date")
    if not isinstance(as_of_text, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of_text):
        raise EvaluationError(f"{qid}: as_of_date must be ISO YYYY-MM-DD")
    try:
        as_of_date = date.fromisoformat(as_of_text)
    except ValueError:
        raise EvaluationError(f"{qid}: as_of_date must be a real calendar date")
    if as_of_date.isoformat() != as_of_text or as_of_date > date.today():
        raise EvaluationError(f"{qid}: as_of_date must be a valid non-future date")
    if not _nonempty(row.get("reviewer_name")):
        raise EvaluationError(f"{qid}: reviewer_name is required")
    reviewer_id = row.get("reviewer_id")
    reviewer = approved_reviewers.get(reviewer_id) if isinstance(reviewer_id, str) else None
    if reviewer is None:
        raise EvaluationError(f"{qid}: reviewer_id must match a valid approved reviewer registry entry")
    if row.get("reviewer_name") != reviewer.get("display_name"):
        raise EvaluationError(f"{qid}: reviewer_name must match the approved reviewer registry display_name")
    if row.get("practice_area") not in reviewer.get("practice_areas", []):
        raise EvaluationError(f"{qid}: reviewer is not approved for this practice_area")
    reviewer_role = row.get("reviewer_role")
    if not isinstance(reviewer_role, str) or reviewer_role not in {"egyptian_lawyer", "qualified_egyptian_counsel"}:
        raise EvaluationError(f"{qid}: reviewer_role must identify qualified Egyptian counsel")
    if not _valid_review_evidence_url(row.get("review_evidence_url")):
        raise EvaluationError(f"{qid}: review_evidence_url must be HTTPS without credentials, query strings, or fragments")
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
    unlisted_pin_sources = sorted({source_id for source_id, _ in pins} - set(sources))
    if unlisted_pin_sources:
        raise EvaluationError(f"{qid}: expected pin citations reference sources absent from expected_sources")
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
    unlisted_pin_sources = sorted({source_id for source_id, _ in pins} - set(sources))
    if unlisted_pin_sources:
        raise EvaluationError(f"{qid}: result pin citations reference sources absent from cited_sources")
    return sources, pins


def _invalid_citation_indices(row):
    qid = row.get("id")
    value = row.get("invalid_citation_indices", [])
    if not isinstance(value, list) or any(type(index) is not int or index < 0 for index in value):
        raise EvaluationError(f"{qid}: invalid_citation_indices must be a list of non-negative integer citation indexes")
    if len(value) != len(set(value)):
        raise EvaluationError(f"{qid}: invalid_citation_indices contains duplicates")
    return value


def _ratio(numerator, denominator):
    return round(numerator / denominator, 4) if denominator else None


def _write_report(path, rendered):
    """Create a report without overwriting prior evaluation evidence."""
    target = Path(path)
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)


def evaluate(question_rows, result_rows, reviewer_registry):
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

    approved_reviewers, registry_errors = validate_reviewer_registry(reviewer_registry)
    if registry_errors:
        raise EvaluationError("reviewer registry contains invalid entries: " + "; ".join(
            f"{item.get('record')}: {', '.join(item.get('errors', []))}" for item in registry_errors
        ))
    if not approved_reviewers:
        raise EvaluationError("reviewer registry has no valid approved reviewers")

    reviewed = {}
    excluded = []
    for qid, row in question_map.items():
        if row.get("review_status") != APPROVED:
            excluded.append(qid)
            continue
        reviewed[qid] = _validate_reviewed_question(row, approved_reviewers)
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
        invalid_indices = _invalid_citation_indices(result_map[qid])
        source_hits = len(set(expected_sources) & set(actual_sources))
        pin_hits = len(set(expected_pins) & set(actual_pins))
        expected_abstain = not q["answerable"]
        abstention_correct = result_map[qid]["abstained"] == expected_abstain
        citation_present = bool(actual_sources or actual_pins)
        item = {
            "id": qid,
            "practice_area": q.get("practice_area", "unspecified").strip(),
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
            "invalid_citation_indices": invalid_indices,
            "invalid_citation_index_count": len(invalid_indices),
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
            "invalid_citation_index_count": sum(x["invalid_citation_index_count"] for x in items),
            "questions_with_invalid_citation_indices": sum(bool(x["invalid_citation_indices"]) for x in items),
            "invalid_citation_question_rate": _ratio(sum(bool(x["invalid_citation_indices"]) for x in items), n),
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


def _release_gate(report, args):
    minimums = {
        "source_precision": args.min_source_precision,
        "pin_cite_precision": args.min_pin_cite_precision,
        "abstention_accuracy": args.min_abstention_accuracy,
    }
    maximums = {
        "unanswerable_citation_rate": args.max_unanswerable_citation_rate,
        "invalid_citation_question_rate": args.max_invalid_citation_question_rate,
    }
    configured = {**minimums, **maximums}
    enabled = (any(value is not None for value in configured.values()) or args.min_questions is not None
               or args.min_practice_areas is not None or args.min_questions_per_practice_area is not None)
    checks = []
    if args.min_questions is not None:
        actual = report["questions_scored"]
        checks.append({"metric": "questions_scored", "operator": ">=", "threshold": args.min_questions,
                       "actual": actual, "passed": actual >= args.min_questions})
    if args.min_practice_areas is not None:
        actual = len(report["by_practice_area"])
        checks.append({"metric": "practice_area_count", "operator": ">=", "threshold": args.min_practice_areas,
                       "actual": actual, "passed": actual >= args.min_practice_areas})
    if args.min_questions_per_practice_area is not None:
        for area, metrics in sorted(report["by_practice_area"].items()):
            actual = metrics["questions_scored"]
            checks.append({"metric": "questions_per_practice_area", "practice_area": area, "operator": ">=",
                           "threshold": args.min_questions_per_practice_area, "actual": actual,
                           "passed": actual >= args.min_questions_per_practice_area})
    for metric, threshold in minimums.items():
        if threshold is not None:
            actual = report["overall"].get(metric)
            checks.append({"metric": metric, "operator": ">=", "threshold": threshold,
                           "actual": actual, "passed": actual is not None and actual >= threshold})
    for metric, threshold in maximums.items():
        if threshold is not None:
            actual = report["overall"].get(metric)
            checks.append({"metric": metric, "operator": "<=", "threshold": threshold,
                           "actual": actual, "passed": actual is not None and actual <= threshold})
    return {"enabled": enabled, "passed": all(check["passed"] for check in checks) if enabled else None,
            "checks": checks}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", required=True, help="Lawyer-reviewed question JSONL")
    parser.add_argument("--results", required=True, help="Model output JSONL, one record per question")
    parser.add_argument("--reviewer-registry", required=True, help="Private JSON registry of verified reviewer qualification checks")
    parser.add_argument("--out", help="Write report JSON here; default is stdout")
    parser.add_argument("--min-source-precision", type=float, help="Fail the technical gate if source precision is below this 0..1 threshold")
    parser.add_argument("--min-pin-cite-precision", type=float, help="Fail the technical gate if pinpoint-citation precision is below this 0..1 threshold")
    parser.add_argument("--min-abstention-accuracy", type=float, help="Fail the technical gate if abstention accuracy is below this 0..1 threshold")
    parser.add_argument("--max-unanswerable-citation-rate", type=float, help="Fail the technical gate if unanswerable cases contain citations above this 0..1 rate")
    parser.add_argument("--max-invalid-citation-question-rate", type=float, help="Fail the technical gate if questions with invalid citation indexes exceed this 0..1 rate")
    parser.add_argument("--min-questions", type=int, help="Fail the technical gate if fewer lawyer-approved questions are scored; required with quality thresholds")
    parser.add_argument("--min-practice-areas", type=int, help="Fail the technical gate if fewer distinct reviewed practice areas are scored")
    parser.add_argument("--min-questions-per-practice-area", type=int, help="Fail if any scored practice area has fewer reviewed questions than this value")
    args = parser.parse_args(argv)
    try:
        reviewer_registry_bytes = Path(args.reviewer_registry).read_bytes()
        reviewer_registry = json.loads(reviewer_registry_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        parser.error(f"invalid reviewer registry: {exc}")
    for name in ("min_questions", "min_practice_areas", "min_questions_per_practice_area"):
        value = getattr(args, name)
        if value is not None and value < 1:
            parser.error(f"--{name.replace('_', '-')} must be a positive integer")
    if (args.min_practice_areas is None) != (args.min_questions_per_practice_area is None):
        parser.error("--min-practice-areas and --min-questions-per-practice-area must be configured together")
    quality_thresholds = (args.min_source_precision, args.min_pin_cite_precision, args.min_abstention_accuracy,
                          args.max_unanswerable_citation_rate, args.max_invalid_citation_question_rate)
    if any(value is not None for value in quality_thresholds):
        if args.min_questions is None:
            parser.error("quality thresholds require an explicit --min-questions sample-size gate")
        if args.min_practice_areas is None:
            parser.error("quality thresholds require explicit practice-area coverage gates")
    for name in ("min_source_precision", "min_pin_cite_precision", "min_abstention_accuracy",
                 "max_unanswerable_citation_rate", "max_invalid_citation_question_rate"):
        value = getattr(args, name)
        if value is not None and (not math.isfinite(value) or not 0 <= value <= 1):
            parser.error(f"--{name.replace('_', '-')} must be a finite number between 0 and 1")
    try:
        question_rows, questions_meta = _read_jsonl_with_provenance(args.questions)
        result_rows, results_meta = _read_jsonl_with_provenance(args.results)
        report = evaluate(question_rows, result_rows, reviewer_registry)
    except (OSError, UnicodeDecodeError, EvaluationError) as exc:
        print(f"evaluation refused: {exc}", file=sys.stderr)
        return 2
    report["provenance"] = _report_provenance({
        "questions": questions_meta,
        "results": results_meta,
        "reviewer_registry": {
            "sha256": hashlib.sha256(reviewer_registry_bytes).hexdigest(),
            "size_bytes": len(reviewer_registry_bytes),
        },
    })
    report["release_gate"] = _release_gate(report, args)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        try:
            _write_report(args.out, rendered)
        except FileExistsError:
            print(f"evaluation refused: output already exists: {args.out}; choose a new path to preserve prior results", file=sys.stderr)
            return 2
    else:
        print(rendered, end="")
    if report["release_gate"]["enabled"] and not report["release_gate"]["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
