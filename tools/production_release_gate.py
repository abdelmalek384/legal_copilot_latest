#!/usr/bin/env python3
"""Aggregate strict deployment, legal-corpus, and lawyer-approved benchmark release gates."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.deployment_preflight import inspect_environment
from tools.evaluate_legal_answers import APPROVED, EvaluationError, _validate_reviewed_question, read_jsonl
from tools.validate_legal_release_readiness import (
    DEFAULT_CANDIDATES,
    DEFAULT_COVERAGE_MATRIX,
    DEFAULT_REGISTER,
    build_report as build_legal_report,
)

DEFAULT_BENCHMARK = ROOT / "tests" / "legal_eval" / "multi_area_questions.draft.jsonl"
MIN_APPROVED_QUESTIONS = 94
MIN_PRACTICE_AREAS = 10


def _normalize_pin_cite(value: object) -> str:
    if not isinstance(value, str):
        return ""
    text = value.strip().lower()
    text = text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    text = text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    text = re.sub(r"^(?:المادة|article|الفقرة|paragraph|para\.?)", "", text)
    return re.sub(r"\s+", "", text).strip("()")


def _ready_candidate_source_index(candidate_paths, legal_report):
    """Map only release-ready candidate source IDs to versioned pinpoint anchors."""
    ready_paths = set()
    candidates = legal_report.get("candidates", [])
    if isinstance(candidates, list):
        for item in candidates:
            if isinstance(item, dict) and item.get("ready") is True and isinstance(item.get("candidate_file"), str):
                ready_paths.add(Path(item["candidate_file"]).resolve())
    source_index = {}
    for path in candidate_paths:
        if Path(path).resolve() not in ready_paths:
            continue
        try:
            candidate = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(candidate, dict):
            continue
        document = candidate.get("document")
        version = candidate.get("version")
        if not isinstance(document, dict) or not isinstance(version, dict):
            continue
        source_id = document.get("source_id")
        anchors = version.get("article_identifiers")
        effective_date = version.get("effective_date")
        repeal_date = version.get("repeal_date")
        if (not isinstance(source_id, str) or not source_id.strip()
                or not isinstance(anchors, list)):
            continue
        effective = _parse_iso_date(effective_date)
        repeal = None if repeal_date is None else _parse_iso_date(repeal_date)
        if effective is None or (repeal_date is not None and repeal is None):
            continue
        normalized = {
            _normalize_pin_cite(anchor)
            for anchor in anchors
            if isinstance(anchor, str) and _normalize_pin_cite(anchor)
        }
        if normalized:
            source_index.setdefault(source_id.strip(), []).append({
                "effective_date": effective,
                "repeal_date": repeal,
                "anchors": normalized,
            })
    return source_index


def _parse_iso_date(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def _active_source_versions(source_id, as_of_date, source_index):
    active = []
    for version in source_index.get(source_id, []):
        effective = version["effective_date"]
        repeal = version["repeal_date"]
        if effective <= as_of_date and (repeal is None or repeal > as_of_date):
            active.append(version)
    return active


def evaluate_release(
    *,
    env=None,
    candidate_paths=None,
    candidates_dir: Path = DEFAULT_CANDIDATES,
    register_path: Path = DEFAULT_REGISTER,
    coverage_matrix_path: Path = DEFAULT_COVERAGE_MATRIX,
    benchmark_path: Path = DEFAULT_BENCHMARK,
    root: Path = ROOT,
) -> dict:
    """Read-only release decision. Any warning, missing gate, or malformed evidence blocks release."""
    blockers = []
    passed, warnings, errors = inspect_environment(env, require_separate=True)
    if errors:
        blockers.append({"gate": "deployment_environment", "code": "environment_errors", "count": len(errors),
                         "details": errors})
    if warnings:
        blockers.append({"gate": "deployment_environment", "code": "environment_warnings", "count": len(warnings),
                         "details": warnings})

    paths = [Path(path) for path in candidate_paths] if candidate_paths is not None else sorted(
        Path(candidates_dir).glob("**/registry_candidate.json")
    )
    if not paths:
        legal_report = {
            "schema_version": 1, "error": "No candidate registry JSON files found.",
            "candidates": [], "ready_count": 0, "blocked_count": 0,
        }
        blockers.append({"gate": "legal_corpus", "code": "no_candidates", "count": 0})
    else:
        legal_report = build_legal_report(
            paths, Path(register_path), Path(root), Path(coverage_matrix_path)
        )
        if legal_report.get("error"):
            blockers.append({"gate": "legal_corpus", "code": "release_report_error"})
        ready_count = legal_report.get("ready_count")
        blocked_count = legal_report.get("blocked_count")
        if (type(ready_count) is not int or type(blocked_count) is not int
                or ready_count != len(paths) or blocked_count != 0):
            blockers.append({
                "gate": "legal_corpus", "code": "candidate_versions_blocked",
                "candidate_count": len(paths),
                "ready_count": ready_count if type(ready_count) is int else None,
                "blocked_count": blocked_count if type(blocked_count) is int else None,
            })

    benchmark_report = {
        "path": str(benchmark_path),
        "question_count": 0,
        "approved_count": 0,
        "unreviewed_count": 0,
        "invalid_approved_count": 0,
        "practice_area_count": 0,
    }
    try:
        questions = read_jsonl(benchmark_path)
    except (OSError, EvaluationError) as exc:
        questions = []
        benchmark_report["error"] = str(exc)
        blockers.append({"gate": "lawyer_approved_benchmark", "code": "benchmark_unreadable"})
    benchmark_report["question_count"] = len(questions)
    approved = [row for row in questions if row.get("review_status") == APPROVED]
    unreviewed = [row for row in questions if row.get("review_status") != APPROVED]
    benchmark_report["approved_count"] = len(approved)
    benchmark_report["unreviewed_count"] = len(unreviewed)

    invalid = []
    unlinked_sources = []
    unmatched_pin_cites = []
    areas = set()
    source_index = _ready_candidate_source_index(paths, legal_report)
    for row in approved:
        try:
            expected_sources, expected_pins = _validate_reviewed_question(row)
        except EvaluationError as exc:
            invalid.append({"id": row.get("id"), "reason": str(exc)})
        else:
            qid = row.get("id")
            as_of_date = _parse_iso_date(row.get("as_of_date"))
            active_versions = {}
            for source_id in expected_sources:
                versions = _active_source_versions(source_id, as_of_date, source_index)
                if not versions:
                    unlinked_sources.append({
                        "id": qid, "source_id": source_id, "as_of_date": row.get("as_of_date"),
                        "reason": "no_version_active_on_as_of_date",
                    })
                elif len(versions) > 1:
                    unlinked_sources.append({
                        "id": qid, "source_id": source_id, "as_of_date": row.get("as_of_date"),
                        "reason": "overlapping_active_versions",
                    })
                else:
                    active_versions[source_id] = versions[0]
            for source_id, pin_cite in expected_pins:
                version = active_versions.get(source_id)
                if version is None:
                    continue
                normalized_pin = _normalize_pin_cite(pin_cite)
                if normalized_pin not in version["anchors"]:
                    unmatched_pin_cites.append({
                        "id": qid, "source_id": source_id, "pin_cite": pin_cite,
                        "as_of_date": row.get("as_of_date"),
                    })
        area = row.get("practice_area")
        if isinstance(area, str) and area.strip():
            areas.add(area.strip())
    benchmark_report["invalid_approved_count"] = len(invalid)
    benchmark_report["practice_area_count"] = len(areas)
    benchmark_report["ready_source_count"] = len(source_index)
    benchmark_report["unlinked_expected_source_count"] = len(unlinked_sources)
    benchmark_report["unmatched_expected_pin_cite_count"] = len(unmatched_pin_cites)
    if len(questions) < MIN_APPROVED_QUESTIONS or len(approved) < MIN_APPROVED_QUESTIONS:
        blockers.append({
            "gate": "lawyer_approved_benchmark", "code": "benchmark_below_minimum",
            "required": MIN_APPROVED_QUESTIONS, "question_count": len(questions),
            "approved_count": len(approved),
        })
    if unreviewed:
        blockers.append({
            "gate": "lawyer_approved_benchmark", "code": "unreviewed_questions_present",
            "count": len(unreviewed),
        })
    if invalid:
        blockers.append({
            "gate": "lawyer_approved_benchmark", "code": "approved_questions_invalid",
            "count": len(invalid), "examples": invalid[:10],
        })
    if len(areas) < MIN_PRACTICE_AREAS:
        blockers.append({
            "gate": "lawyer_approved_benchmark", "code": "practice_area_coverage_below_minimum",
            "required": MIN_PRACTICE_AREAS, "actual": len(areas),
        })
    if unlinked_sources:
        blockers.append({
            "gate": "lawyer_approved_benchmark", "code": "benchmark_sources_not_in_ready_corpus",
            "count": len(unlinked_sources), "examples": unlinked_sources[:10],
        })
    if unmatched_pin_cites:
        blockers.append({
            "gate": "lawyer_approved_benchmark", "code": "benchmark_pin_cites_not_in_ready_corpus",
            "count": len(unmatched_pin_cites), "examples": unmatched_pin_cites[:10],
        })

    return {
        "schema_version": 1,
        "ready": not blockers,
        "decision": "ready" if not blockers else "blocked",
        "environment": {"passed_checks": len(passed), "warnings": warnings, "errors": errors},
        "legal_corpus": {
            "candidate_count": len(paths),
            "ready_count": legal_report.get("ready_count", 0),
            "blocked_count": legal_report.get("blocked_count", 0),
            "error": legal_report.get("error"),
            "blocker_codes": sorted({
                blocker.get("code")
                for candidate in legal_report.get("candidates", [])
                for blocker in candidate.get("blockers", [])
                if isinstance(blocker, dict) and isinstance(blocker.get("code"), str)
            }),
        },
        "benchmark": benchmark_report,
        "blockers": blockers,
        "disclaimer": (
            "A pass only means these structural gates passed. It does not prove legal correctness, "
            "permission authenticity, statistical reliability, or production security."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", help="Candidate registry JSON path; repeat as needed.")
    parser.add_argument("--candidates-dir", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--coverage-matrix", type=Path, default=DEFAULT_COVERAGE_MATRIX)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, help="Optional JSON report path.")
    args = parser.parse_args(argv)

    report = evaluate_release(
        candidate_paths=args.candidate,
        candidates_dir=args.candidates_dir,
        register_path=args.register,
        coverage_matrix_path=args.coverage_matrix,
        benchmark_path=args.benchmark,
        root=args.root,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        destination = args.out.resolve()
        protected_files = {Path(args.register).resolve(), Path(args.coverage_matrix).resolve(),
                           Path(args.benchmark).resolve()}
        protected_files.update(Path(path).resolve() for path in (args.candidate or []))
        protected_directories = {
            Path(args.candidates_dir).resolve(),
            Path(args.root).resolve() / "originals",
            Path(args.root).resolve() / "extracted",
        }
        if destination in protected_files or any(
            destination == directory or directory in destination.parents for directory in protected_directories
        ):
            print(json.dumps({"ready": False, "error": "Report output must not overwrite release-gate inputs or corpus artifacts."}))
            return 2
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
