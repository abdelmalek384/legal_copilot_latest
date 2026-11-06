#!/usr/bin/env python3
"""Validate Legal Copilot's source registry, coverage matrix, and Arabic eval seeds."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "docs/source_manifest.json"
coverage_path = ROOT / "docs/legal_coverage_matrix.csv"
questions_path = ROOT / "tests/legal_eval/practice_questions.seed.jsonl"


def require(condition, message):
    if not condition:
        raise SystemExit("VALIDATION FAILED: " + message)


manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
require(isinstance(manifest, dict), "source manifest must be a JSON object")
sources = manifest.get("sources")
require(isinstance(sources, list) and sources, "manifest needs a non-empty sources list")
source_ids = []
for index, source in enumerate(sources, start=1):
    require(isinstance(source, dict), f"source #{index} must be a JSON object")
    require(all(isinstance(source.get(field), str) and source[field].strip()
                for field in ("id", "name", "category")),
            f"source #{index} needs non-empty string id, name, and category")
    for field in ("license_status", "access_status", "priority"):
        require(source.get(field), f"{source.get('id', 'source #' + str(index))} needs {field}")
    # Group entries (e.g. books, journals, commercial databases) intentionally have no single URL.
    if source.get("url") is None:
        require(source.get("category") in {
            "books_secondary_literature", "commercial_legal_database"
        }, f"{source['id']} has no URL but is not a grouped source")
    source_ids.append(source["id"])
require(len(source_ids) == len(set(source_ids)), "duplicate source IDs")

with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
require(rows, "coverage matrix is empty")
required_columns = {
    "practice_area", "priority", "core_materials", "judgment_sources",
    "temporal_checks", "evaluation_owner", "status"
}
require(required_columns.issubset(rows[0].keys()), "coverage matrix is missing required columns")
areas = [row["practice_area"].strip() for row in rows]
require(all(areas), "empty practice area")
require(len(areas) == len(set(areas)), "duplicate practice areas")

questions = []
for line_number, line in enumerate(questions_path.read_text(encoding="utf-8").splitlines(), start=1):
    if not line.strip():
        continue
    try:
        question = json.loads(line)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"VALIDATION FAILED: question seed line {line_number}: {exc}") from exc
    require(isinstance(question, dict), f"question seed line {line_number} must be a JSON object")
    for field in ("id", "practice_area", "question_ar", "review_status"):
        require(isinstance(question.get(field), str) and question[field].strip(),
                f"question seed line {line_number} needs non-empty string {field}")
    require(question.get("expected_answer") is None,
            f"{question['id']} must not start with an invented answer")
    require(question.get("expected_sources") == [],
            f"{question['id']} must start without unreviewed expected sources")
    require(question.get("must_abstain_if_unverified") is True,
            f"{question['id']} must require abstention for unverified sources")
    require(question.get("review_status") == "needs_lawyer_review",
            f"{question['id']} must be marked needs_lawyer_review")
    questions.append(question)
question_ids = [question["id"] for question in questions]
require(questions and len(question_ids) == len(set(question_ids)),
        "question seeds are empty or contain duplicate IDs")

print(
    "Legal data foundation validation passed: "
    f"{len(source_ids)} sources, {len(areas)} practice areas, "
    f"{len(questions)} lawyer-review question seeds."
)
