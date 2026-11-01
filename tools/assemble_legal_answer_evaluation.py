#!/usr/bin/env python3
"""Join machine evidence-behavior results to qualified-human reviews by exact answer ID.

This is a linkage and audit report only. It does not infer legal correctness,
select a winning reviewer, or convert synthetic test fixtures into legal evidence.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DIMENSIONS = (
    "legal_correctness", "source_support", "citation_precision",
    "temporal_correctness", "completeness_issue_spotting",
    "arabic_clarity", "uncertainty_abstention",
)
DISPOSITIONS = {
    "pass_for_this_case", "needs_revision", "unsafe",
    "not_scored_insufficient_evidence",
}
VALID_SCORES = {0, 1, 2, "not_applicable"}
MACHINE_SCHEMA_VERSION = 2
HUMAN_SCHEMA_VERSION = 2


class AssemblyError(ValueError):
    """Raised when the two input reports cannot be safely linked."""


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _machine_rows(report):
    if not isinstance(report, dict) or report.get("schema_version") != MACHINE_SCHEMA_VERSION:
        raise AssemblyError("machine report must use schema_version=2 with stable answer IDs")
    rows = report.get("results")
    if not isinstance(rows, list):
        raise AssemblyError("machine report results must be a list")
    question_ids = set()
    answer_ids = set()
    normalized = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise AssemblyError(f"machine result {index} must be an object")
        question_id = row.get("id")
        if not _nonempty(question_id):
            raise AssemblyError(f"machine result {index} requires a non-empty id")
        if question_id in question_ids:
            raise AssemblyError(f"duplicate machine question id: {question_id}")
        question_ids.add(question_id)
        answer_id = row.get("answer_id")
        if answer_id is not None:
            if not _nonempty(answer_id):
                raise AssemblyError(f"{question_id}: answer_id must be a non-empty stable identifier")
            answer_id = answer_id.strip()
            if answer_id in answer_ids:
                raise AssemblyError(f"duplicate machine answer_id: {answer_id}")
            answer_ids.add(answer_id)
        normalized.append((question_id, answer_id, row))
    return normalized, answer_ids


def _human_assessments(report):
    if not isinstance(report, dict) or report.get("schema_version") != HUMAN_SCHEMA_VERSION:
        raise AssemblyError("human review report must use schema_version=2")
    rows = report.get("answer_assessments")
    if not isinstance(rows, list):
        raise AssemblyError("human review report answer_assessments must be a list")
    if report.get("valid_assessments") != len(rows):
        raise AssemblyError("human report valid_assessments does not match answer_assessments length")

    assessment_ids = set()
    reviewer_answer_pairs = set()
    normalized = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise AssemblyError(f"human assessment {index} must be an object")
        for field in ("assessment_id", "case_id", "reviewer_id", "disposition"):
            if not _nonempty(row.get(field)):
                raise AssemblyError(f"human assessment {index} requires a non-empty {field}")
        assessment_id = row["assessment_id"].strip()
        if assessment_id in assessment_ids:
            raise AssemblyError(f"duplicate human assessment_id: {assessment_id}")
        assessment_ids.add(assessment_id)
        if row["disposition"] not in DISPOSITIONS:
            raise AssemblyError(f"{assessment_id}: unsupported disposition")
        answer_id = row.get("answer_id")
        if answer_id is not None:
            if not _nonempty(answer_id):
                raise AssemblyError(f"{assessment_id}: answer_id must be non-empty when supplied")
            answer_id = answer_id.strip()
            reviewer_pair = (row["case_id"].strip(), answer_id, row["reviewer_id"].strip())
            if reviewer_pair in reviewer_answer_pairs:
                raise AssemblyError(
                    f"{assessment_id}: duplicate reviewer assessment for the same case and answer"
                )
            reviewer_answer_pairs.add(reviewer_pair)
        scores = row.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(DIMENSIONS):
            raise AssemblyError(f"{assessment_id}: scores must contain every documented dimension")
        for dimension, value in scores.items():
            if type(value) is bool or value not in VALID_SCORES:
                raise AssemblyError(f"{assessment_id}: invalid score for {dimension}")
        critical = row.get("critical_defect")
        if not isinstance(critical, bool):
            raise AssemblyError(f"{assessment_id}: critical_defect must be boolean")
        categories = row.get("critical_defect_categories", [])
        if not isinstance(categories, list) or any(not _nonempty(value) for value in categories):
            raise AssemblyError(f"{assessment_id}: critical_defect_categories must be a string list")
        if len(categories) != len(set(categories)):
            raise AssemblyError(f"{assessment_id}: duplicate critical defect category")
        if not critical and categories:
            raise AssemblyError(f"{assessment_id}: non-critical assessment cannot carry defect categories")
        normalized.append({
            "assessment_id": assessment_id,
            "case_id": row["case_id"].strip(),
            "answer_id": answer_id,
            "reviewer_id": row["reviewer_id"].strip(),
            "disposition": row["disposition"],
            "scores": scores,
            "critical_defect": critical,
            "critical_defect_categories": categories,
        })
    return normalized


def _summarize_human_group(group):
    dispositions = sorted({row["disposition"] for row in group})
    dimension_agreement = {}
    differing_dimensions = []
    for dimension in DIMENSIONS:
        values = sorted(
            {row["scores"][dimension] for row in group},
            key=lambda value: (str(type(value)), str(value)),
        )
        exact = len(values) == 1
        dimension_agreement[dimension] = {
            "exact_agreement": exact,
            "values": values,
            "review_count": len(group),
        }
        if not exact:
            differing_dimensions.append(dimension)

    category_counts = Counter(
        category
        for row in group if row["critical_defect"]
        for category in row["critical_defect_categories"]
    )
    critical_count = sum(1 for row in group if row["critical_defect"])
    disposition_agreement = len(dispositions) == 1
    insufficient_conflict = (
        "not_scored_insufficient_evidence" in dispositions and len(dispositions) > 1
    )
    requires_adjudication = not disposition_agreement or bool(differing_dimensions)
    return {
        "review_count": len(group),
        "assessment_ids": sorted(row["assessment_id"] for row in group),
        "reviewer_ids": sorted({row["reviewer_id"] for row in group}),
        "dispositions": dispositions,
        "disposition_agreement": disposition_agreement,
        "insufficient_evidence_conflict": insufficient_conflict,
        "dimension_disagreements": differing_dimensions,
        "dimension_agreement": dimension_agreement,
        "critical_defect_present": critical_count > 0,
        "critical_defect_assessment_count": critical_count,
        "critical_defect_category_counts": dict(sorted(category_counts.items())),
        "requires_adjudication": requires_adjudication,
        "requires_follow_up": requires_adjudication or critical_count > 0,
    }


def assemble(machine_report, human_report):
    machine_rows, machine_answer_ids = _machine_rows(machine_report)
    human_rows = _human_assessments(human_report)

    human_by_answer = defaultdict(list)
    human_without_answer_id = 0
    for row in human_rows:
        if row["answer_id"] is None:
            human_without_answer_id += 1
        else:
            human_by_answer[row["answer_id"]].append(row)

    machine_results = []
    linked = 0
    awaiting = 0
    missing_machine_id = 0
    ambiguous_ids = []
    adjudication_count = 0
    critical_answer_count = 0
    for question_id, answer_id, machine_row in machine_rows:
        machine_metrics = {
            key: machine_row.get(key)
            for key in ("source_precision", "pin_cite_precision", "abstention_accuracy",
                        "invalid_citation_index_count", "unexpected_source_count",
                        "unexpected_pin_cite_count")
            if key in machine_row
        }
        item = {
            "question_id": question_id,
            "answer_id": answer_id,
            "machine_metrics": machine_metrics,
            "human_review_status": "missing_answer_id",
            "human_review": None,
        }
        if answer_id is None:
            missing_machine_id += 1
            machine_results.append(item)
            continue
        group = human_by_answer.get(answer_id, [])
        if not group:
            awaiting += 1
            item["human_review_status"] = "awaiting_human_review"
            machine_results.append(item)
            continue
        case_ids = sorted({row["case_id"] for row in group})
        if len(case_ids) != 1:
            ambiguous_ids.append(answer_id)
            item["human_review_status"] = "ambiguous_cross_case_answer_id"
            item["human_review"] = {"review_count": len(group), "case_count": len(case_ids)}
            machine_results.append(item)
            continue
        summary = _summarize_human_group(group)
        linked += 1
        adjudication_count += int(summary["requires_adjudication"])
        critical_answer_count += int(summary["critical_defect_present"])
        item["human_review_status"] = "linked"
        item["human_review"] = summary
        machine_results.append(item)

    unmatched_human_ids = sorted(set(human_by_answer) - machine_answer_ids)
    linked_coverage = (
        round(linked / len(machine_answer_ids), 4) if machine_answer_ids else None
    )
    return {
        "schema_version": 1,
        "report_type": "machine_and_human_answer_evidence_linkage",
        "input_schema_versions": {
            "machine": MACHINE_SCHEMA_VERSION,
            "human_review": HUMAN_SCHEMA_VERSION,
        },
        "counts": {
            "machine_results": len(machine_rows),
            "machine_results_with_answer_id": len(machine_answer_ids),
            "machine_results_without_answer_id": missing_machine_id,
            "human_assessments": len(human_rows),
            "human_assessments_with_answer_id": len(human_rows) - human_without_answer_id,
            "human_assessments_without_answer_id": human_without_answer_id,
            "linked_answers": linked,
            "answers_awaiting_human_review": awaiting,
            "answers_requiring_adjudication": adjudication_count,
            "answers_with_critical_defects": critical_answer_count,
            "ambiguous_cross_case_answer_ids": len(ambiguous_ids),
            "unmatched_human_answer_ids": len(unmatched_human_ids),
        },
        "answer_id_linkage_coverage": linked_coverage,
        "ambiguous_cross_case_answer_ids": sorted(ambiguous_ids),
        "unmatched_human_answer_ids": unmatched_human_ids,
        "results": machine_results,
        "limitations": [
            "Linkage is by exact opaque answer_id only; question IDs and case IDs are not substitutes.",
            "A matching ID proves record linkage, not that a reviewer or machine metric is legally correct.",
            "Disagreement flags identify cases for human follow-up; the assembler never chooses a winning reviewer.",
            "Only valid human assessments exported by the review evaluator are included; invalid assessments remain in that evaluator's separate invalid_records list.",
            "Machine metrics cover citation and abstention behavior only; they do not score semantic legal correctness.",
            "Keep both input reports and reviewer registry in private controlled storage; this output contains pseudonymous reviewer and assessment IDs.",
        ],
    }


def _write_report(path, rendered):
    with Path(path).open("x", encoding="utf-8", newline="\\n") as handle:
        handle.write(rendered)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine-report", required=True, help="Schema-v2 output from evaluate_legal_answers.py")
    parser.add_argument("--human-review-report", required=True, help="Schema-v2 output from evaluate_legal_answer_reviews.py")
    parser.add_argument("--out", help="Optional output path; existing reports are never overwritten")
    args = parser.parse_args(argv)
    try:
        machine_bytes = Path(args.machine_report).read_bytes()
        human_bytes = Path(args.human_review_report).read_bytes()
        machine_report = json.loads(machine_bytes.decode("utf-8"))
        human_report = json.loads(human_bytes.decode("utf-8"))
        report = assemble(machine_report, human_report)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, AssemblyError) as exc:
        print(f"assembly refused: {exc}", file=sys.stderr)
        return 2

    report["provenance"] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "inputs": {
            "machine_report": {
                "sha256": hashlib.sha256(machine_bytes).hexdigest(),
                "size_bytes": len(machine_bytes),
            },
            "human_review_report": {
                "sha256": hashlib.sha256(human_bytes).hexdigest(),
                "size_bytes": len(human_bytes),
            },
        },
        "limitations": [
            "Input paths and report contents are omitted from this provenance block.",
            "SHA-256 identifies the exact input bytes; it does not prove authorship or provide a trusted timestamp.",
        ],
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\\n"
    if args.out:
        try:
            _write_report(args.out, rendered)
        except FileExistsError:
            print(f"assembly refused: output already exists: {args.out}; choose a new path to preserve prior evidence", file=sys.stderr)
            return 2
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
