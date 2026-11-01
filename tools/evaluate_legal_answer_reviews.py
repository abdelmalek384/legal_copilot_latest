#!/usr/bin/env python3
"""Aggregate qualified-human review records for Egyptian legal answers.

This tool validates recorded assessments and summarizes them. It does not score
legal answers automatically, infer ground truth, or establish legal accuracy.
Use synthetic or approved anonymized records only.
"""
import argparse
import json
import sys
from datetime import date
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
    for field in ("assessment_id", "case_id", "practice_area", "reviewer_id", "reviewer_name", "review_date", "disposition"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"missing or empty {field}")
    disposition = record.get("disposition")
    if not isinstance(disposition, str) or disposition not in DISPOSITIONS:
        errors.append("disposition must be one of the documented values")
    review_date = record.get("review_date")
    if isinstance(review_date, str) and review_date.strip():
        try:
            parsed_review_date = date.fromisoformat(review_date)
            if parsed_review_date.isoformat() != review_date:
                raise ValueError("date must use YYYY-MM-DD")
        except ValueError:
            errors.append("review_date must be a real calendar date in YYYY-MM-DD format")

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


def _valid_iso_date(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = date.fromisoformat(value)
        return parsed.isoformat() == value and parsed <= date.today()
    except ValueError:
        return False


def validate_reviewer_registry(registry):
    """Return approved reviewer identities and auditable registry errors.

    A registry entry is an administrative assertion that must be checked by a
    trusted operator against private credential evidence; this function cannot
    independently verify a professional license or identity.
    """
    errors = []
    if not isinstance(registry, dict) or not isinstance(registry.get("reviewers"), list):
        return {}, [{"record": "registry", "errors": ["reviewer registry must contain a reviewers list"]}]
    entries = {}
    duplicates = set()
    for index, entry in enumerate(registry["reviewers"], start=1):
        if not isinstance(entry, dict):
            errors.append({"record": f"reviewer-row-{index}", "errors": ["reviewer entry must be an object"]})
            continue
        reviewer_id = entry.get("reviewer_id")
        row_errors = []
        if not isinstance(reviewer_id, str) or not reviewer_id.strip():
            row_errors.append("missing or empty reviewer_id")
        elif reviewer_id in entries:
            duplicates.add(reviewer_id)
        status = entry.get("status")
        if status not in {"approved", "pending", "suspended", "rejected"}:
            row_errors.append("status must be approved, pending, suspended, or rejected")
        for field in ("display_name", "qualification_basis", "evidence_reference", "verified_by"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                row_errors.append(f"missing or empty {field}")
        if entry.get("professional_role") not in {"egyptian_lawyer", "qualified_egyptian_counsel"}:
            row_errors.append("professional_role must identify Egyptian legal counsel")
        if entry.get("jurisdiction") != "Egypt":
            row_errors.append("jurisdiction must be Egypt")
        practice_areas = entry.get("practice_areas")
        if (not isinstance(practice_areas, list) or not practice_areas
                or any(not isinstance(area, str) or not area.strip() for area in practice_areas)
                or len(practice_areas) != len(set(practice_areas))):
            row_errors.append("practice_areas must be a non-empty list of unique non-empty strings")
        if not _valid_iso_date(entry.get("verified_on")):
            row_errors.append("verified_on must be a real ISO date that is not in the future")
        if row_errors:
            errors.append({"record": reviewer_id or f"reviewer-row-{index}", "errors": row_errors})
        if isinstance(reviewer_id, str) and reviewer_id.strip():
            entries[reviewer_id] = entry
    for reviewer_id in sorted(duplicates):
        errors.append({"record": reviewer_id, "errors": ["duplicate reviewer_id; all duplicate entries are excluded"]})
    approved = {
        reviewer_id: entry for reviewer_id, entry in entries.items()
        if reviewer_id not in duplicates
        and entry.get("status") == "approved"
        and isinstance(entry.get("display_name"), str) and entry["display_name"].strip()
        and isinstance(entry.get("qualification_basis"), str) and entry["qualification_basis"].strip()
        and isinstance(entry.get("evidence_reference"), str) and entry["evidence_reference"].strip()
        and isinstance(entry.get("verified_by"), str) and entry["verified_by"].strip()
        and entry.get("professional_role") in {"egyptian_lawyer", "qualified_egyptian_counsel"}
        and entry.get("jurisdiction") == "Egypt"
        and isinstance(entry.get("practice_areas"), list) and bool(entry["practice_areas"])
        and all(isinstance(area, str) and area.strip() for area in entry["practice_areas"])
        and len(entry["practice_areas"]) == len(set(entry["practice_areas"]))
        and _valid_iso_date(entry.get("verified_on"))
    }
    return approved, errors


def summarize_reviews(records, reviewer_registry):
    """Summarize assessments only when reviewer identity is approved in the registry."""
    approved_reviewers, registry_errors = validate_reviewer_registry(reviewer_registry)
    valid, invalid, seen = [], [], set()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            invalid.append({"record": f"line-{index}", "record_index": index, "errors": ["record must be an object"]})
            continue
        errors = validate_review(record)
        assessment_id = record.get("assessment_id", f"line-{index}")
        reviewer_id = record.get("reviewer_id")
        reviewer = approved_reviewers.get(reviewer_id) if isinstance(reviewer_id, str) else None
        if reviewer is None:
            errors.append("reviewer_id is not present in the valid approved reviewer registry")
        elif record.get("reviewer_name") != reviewer.get("display_name"):
            errors.append("reviewer_name does not match the approved registry display_name")
        elif record.get("practice_area") not in reviewer.get("practice_areas", []):
            errors.append("reviewer is not approved for this practice_area")
        if errors:
            invalid.append({"record": assessment_id, "record_index": index, "errors": errors})
            continue
        if assessment_id in seen:
            invalid.append({
                "record": assessment_id, "record_index": index,
                "errors": ["duplicate assessment_id; each reviewer assessment must have a unique ID"],
            })
            continue
        seen.add(assessment_id)
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
        {"assessment_id": record["assessment_id"], "case_id": record["case_id"],
         "description": record["critical_defect_description"]}
        for record in valid if record["critical_defect"]
    ]
    return {
        "valid_assessments": len(valid),
        "invalid_assessments_excluded": len(invalid),
        "approved_reviewers_available": len(approved_reviewers),
        "reviewer_registry_errors": registry_errors,
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


def _write_report(path, rendered):
    """Create a review summary without overwriting prior evaluation evidence."""
    target = Path(path)
    with target.open("x", encoding="utf-8", newline="\\n") as handle:
        handle.write(rendered)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reviews", type=Path, help="UTF-8 JSONL containing human review records")
    parser.add_argument("--reviewer-registry", type=Path, required=True, help="Private JSON registry of reviewer qualification checks")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON report")
    args = parser.parse_args(argv)
    try:
        registry = json.loads(args.reviewer_registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"invalid reviewer registry: {exc}")
    report = summarize_reviews(load_jsonl(args.reviews), registry)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            _write_report(args.output, rendered)
        except FileExistsError:
            print(f"evaluation refused: output already exists: {args.output}; choose a new path to preserve prior results", file=sys.stderr)
            return 2
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    main()
