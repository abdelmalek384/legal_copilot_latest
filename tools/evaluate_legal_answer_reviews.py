#!/usr/bin/env python3
"""Aggregate qualified-human review records for Egyptian legal answers.

This tool validates recorded assessments and summarizes them. It does not score
legal answers automatically, infer ground truth, or establish legal accuracy.
Use synthetic or approved anonymized records only.
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

DIMENSIONS = (
    "legal_correctness", "source_support", "citation_precision",
    "temporal_correctness", "completeness_issue_spotting",
    "arabic_clarity", "uncertainty_abstention",
)
SCORES = {0, 1, 2}
NOT_APPLICABLE = "not_applicable"
DISPOSITIONS = {
    "pass_for_this_case", "needs_revision", "unsafe",
    "not_scored_insufficient_evidence",
}


def load_jsonl(path):
    """Read JSONL, preserving line numbers in errors."""
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: each JSONL row must be an object")
            rows.append(row)
    return rows


def validate_review(record):
    """Return schema/evidence errors without inventing or repairing labels."""
    errors = []
    for field in ("case_id", "practice_area", "reviewer_name", "review_date", "disposition"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"missing or empty {field}")
    if record.get("disposition") not in DISPOSITIONS:
        errors.append("disposition must be one of the documented values")

    scores = record.get("scores")
    rationales = record.get("rationales")
    if not isinstance(scores, dict):
        errors.append("scores must be an object keyed by review dimension")
        scores = {}
    if not isinstance(rationales, dict):
        errors.append("rationales must be an object keyed by review dimension")
        rationales = {}

    unknown = sorted(set(scores) - set(DIMENSIONS))
    if unknown:
        errors.append("unknown score dimensions: " + ", ".join(unknown))
    for dimension in DIMENSIONS:
        value = scores.get(dimension)
        valid_numeric = type(value) is int and value in SCORES
        if not valid_numeric and value != NOT_APPLICABLE:
            errors.append(f"{dimension} must be 0, 1, 2, or {NOT_APPLICABLE}")
            continue
        rationale = rationales.get(dimension)
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"{dimension} requires an evidence-based rationale")
        if value == NOT_APPLICABLE and isinstance(rationale, str) and "not applicable" not in rationale.lower() and "n/a" not in rationale.lower():
            errors.append(f"{dimension} not_applicable rationale must explain why it does not apply")

    critical = record.get("critical_defect")
    if not isinstance(critical, bool):
        errors.append("critical_defect must be an explicit boolean")
    elif critical and record.get("disposition") != "unsafe":
        errors.append("critical_defect=true requires disposition=unsafe")
    if record.get("disposition") == "unsafe" and critical is not True:
        errors.append("unsafe disposition requires critical_defect=true and a recorded critical_defect_description")
    if critical and not (isinstance(record.get("critical_defect_description"), str) and record["critical_defect_description"].strip()):
        errors.append("critical_defect=true requires critical_defect_description")
    if record.get("disposition") == "pass_for_this_case":
        scored = [v for v in scores.values() if type(v) is int and v in SCORES]
        if not scored:
            errors.append("pass_for_this_case requires at least one numerically scored dimension")
    if record.get("disposition") == "not_scored_insufficient_evidence" and critical is True:
        errors.append("insufficient-evidence disposition cannot suppress a recorded critical defect")
    return errors


def summarize_reviews(records):
    """Summarize valid records; invalid rows are reported and never scored."""
    valid, invalid, seen = [], [], set()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            invalid.append({"record": f"line-{index}", "record_index": index, "errors": ["record must be an object"]})
            continue
        errors = validate_review(record)
        case_id = record.get("case_id", f"line-{index}")
        if errors:
            invalid.append({"record": case_id, "record_index": index, "errors": errors})
            continue
        if record["case_id"] in seen:
            invalid.append({
                "record": record["case_id"], "record_index": index,
                "errors": ["duplicate case_id; use a unique case_id for each assessment"],
            })
            continue
        seen.add(record["case_id"])
        valid.append(record)

    counts = Counter(record["disposition"] for record in valid)
    dimension_values = defaultdict(list)
    for record in valid:
        if record["disposition"] == "not_scored_insufficient_evidence":
            continue
        for dimension in DIMENSIONS:
            value = record["scores"][dimension]
            if type(value) is int and value in SCORES:
                dimension_values[dimension].append(value)

    dimension_summary = {}
    for dimension in DIMENSIONS:
        values = dimension_values[dimension]
        dimension_summary[dimension] = {
            "scored_assessments": len(values),
            "mean_score_0_to_2": round(sum(values) / len(values), 4) if values else None,
            "score_counts": {str(score): values.count(score) for score in (0, 1, 2)},
        }
    practice_areas = Counter(record["practice_area"] for record in valid)
    critical_defects = [
        {"case_id": record["case_id"], "description": record["critical_defect_description"]}
        for record in valid if record["critical_defect"]
    ]
    return {
        "valid_assessments": len(valid),
        "invalid_assessments_excluded": len(invalid),
        "invalid_records": invalid,
        "disposition_counts": {name: counts.get(name, 0) for name in sorted(DISPOSITIONS)},
        "practice_area_counts": dict(sorted(practice_areas.items())),
        "critical_defect_count": len(critical_defects),
        "critical_defects": critical_defects,
        "dimension_summary": dimension_summary,
        "limitations": [
            "Only recorded qualified-human assessments that pass schema validation are summarized.",
            "not_scored_insufficient_evidence is not a pass and is excluded from dimension means.",
            "Critical defects are reported separately and must not be hidden by averages.",
            "A benchmark summary does not establish general legal accuracy, current-law coverage, or production readiness.",
            "Do not publish confidential, privileged, or re-identifiable matter data in evaluation records.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reviews", type=Path, help="UTF-8 JSONL containing human review records")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON report")
    args = parser.parse_args()
    report = summarize_reviews(load_jsonl(args.reviews))
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
