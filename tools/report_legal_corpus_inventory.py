#!/usr/bin/env python3
"""Produce an honest, read-only inventory of legal-corpus planning artifacts.

This inventories metadata registers, not legal text. It deliberately never
infers that a candidate is collected, authentic, current, licensed, or lawyer
reviewed merely because it appears in a JSON file.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = {
    "manifest": ROOT / "docs/source_manifest.json",
    "permissions": ROOT / "docs/source_permission_register.json",
    "candidates": ROOT / "docs/legal_document_candidates.json",
    "evidence": ROOT / "docs/phase_2_source_evidence_register.json",
    "queue": ROOT / "docs/phase_2_authorized_acquisition_queue.json",
    "coverage": ROOT / "docs/legal_coverage_matrix.csv",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def list_of_objects(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{label}: expected a list")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{label}: every list entry must be an object")
    return value


def counts(values: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(v or "unknown") for v in values).items()))


def build_report(paths: dict[str, Path]) -> dict[str, Any]:
    manifest = read_json(paths["manifest"])
    permissions = read_json(paths["permissions"])
    candidates = read_json(paths["candidates"])
    evidence = read_json(paths["evidence"])
    queue = read_json(paths["queue"])

    manifest_sources = list_of_objects(manifest.get("sources"), "source_manifest.sources")
    permission_sources = list_of_objects(permissions.get("sources"), "source_permission_register.sources")
    candidate_sources = list_of_objects(candidates.get("sources"), "legal_document_candidates.sources")
    documents = list_of_objects(candidates.get("documents"), "legal_document_candidates.documents")
    evidence_sources = list_of_objects(evidence.get("sources"), "phase_2_source_evidence_register.sources")
    queue_items = list_of_objects(queue.get("queue"), "phase_2_authorized_acquisition_queue.queue")

    with paths["coverage"].open(encoding="utf-8-sig", newline="") as stream:
        coverage = list(csv.DictReader(stream))
    if not coverage:
        raise ValueError(f"{paths['coverage']}: coverage matrix is empty")

    permission_ids = {str(s.get("source_id")) for s in permission_sources if s.get("source_id")}
    candidate_source_ids = {str(s.get("source_id")) for s in candidate_sources if s.get("source_id")}
    manifest_source_ids = {str(s.get("id")) for s in manifest_sources if s.get("id")}
    document_source_ids = {str(d.get("source_id")) for d in documents if d.get("source_id")}
    document_ids = {str(d.get("document_id")) for d in documents if d.get("document_id")}

    permission_states = counts(s.get("collection_permission") for s in permission_sources)
    commercial_states = counts(s.get("commercial_reuse_permission") for s in permission_sources)
    evidence_states = counts(s.get("source_state") for s in evidence_sources)
    queue_states = counts(s.get("acquisition_state") for s in queue_items)
    review_states = counts(s.get("legal_review_state") for s in queue_items)
    candidate_states = counts(d.get("candidate_status") for d in documents)
    coverage_states = counts(row.get("status") for row in coverage)

    queue_document_ids = {
        str(doc_id)
        for item in queue_items
        for doc_id in (item.get("document_ids") or [])
        if isinstance(doc_id, str)
    }
    issues: list[dict[str, Any]] = []
    for label, ids in (
        ("candidate_sources_missing_permission_register", candidate_source_ids - permission_ids),
        ("manifest_sources_missing_permission_register", manifest_source_ids - permission_ids),
        ("documents_reference_unknown_candidate_source", document_source_ids - candidate_source_ids),
        ("candidate_documents_missing_from_acquisition_queue", document_ids - queue_document_ids),
        ("queue_references_unknown_candidate_document", queue_document_ids - document_ids),
    ):
        if ids:
            issues.append({"code": label, "count": len(ids), "ids": sorted(ids)})

    # The repository's candidate registers are not proof of downloaded files.
    # Report declared acquisition state separately and do not infer corpus size.
    declared_acquired = sum(
        1 for item in queue_items
        if str(item.get("acquisition_state", "")).strip().lower() == "acquired"
    )
    report = {
        "report_type": "legal_corpus_artifact_inventory",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "scope": "Repository metadata registers only; this is not a filesystem or database scan.",
        "corpus_claims": {
            "candidate_catalogue_is_legal_corpus": False,
            "legal_text_files_verified_by_this_report": 0,
            "authenticity_or_currentness_certified": False,
            "permission_or_commercial_reuse_granted": False,
            "lawyer_review_inferred": False,
            "declared_acquired_queue_items": declared_acquired,
            "note": "A zero here means this report did not inspect legal-text files; it is not a claim that no files exist outside the inspected scope."
        },
        "inputs": {name: str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path) for name, path in paths.items()},
        "counts": {
            "manifest_sources": len(manifest_sources),
            "permission_register_sources": len(permission_sources),
            "candidate_sources": len(candidate_sources),
            "candidate_documents": len(documents),
            "source_evidence_records": len(evidence_sources),
            "acquisition_queue_items": len(queue_items),
            "coverage_practice_areas": len(coverage),
        },
        "statuses": {
            "collection_permission": permission_states,
            "commercial_reuse_permission": commercial_states,
            "candidate_document_status": candidate_states,
            "source_evidence_state": evidence_states,
            "declared_acquisition_state": queue_states,
            "declared_legal_review_state": review_states,
            "coverage_status": coverage_states,
        },
        "cross_registry_issues": issues,
        "limitations": [
            "Source catalogues and acquisition queues are planning metadata, not collected legal documents.",
            "An acquisition state in a queue is self-reported metadata; original-file existence and SHA-256 are not checked by this report.",
            "A source permission label is not independently authenticated here.",
            "Legal authenticity, effective dates, amendments, currentness, citations, and lawyer review require separate evidence.",
        ],
    }
    return report


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Legal-corpus artifact inventory",
        "",
        f"- Generated: {report['generated_at']}",
        "- Scope: repository metadata registers only; no database or legal-text files were scanned.",
        "- **Status: planning inventory, not a verified legal corpus.**",
        "",
        "## Counts",
        "",
        "| Register | Records |",
        "|---|---:|",
    ]
    for key, value in report["counts"].items():
        lines.append(f"| {key.replace('_', ' ')} | {value} |")
    lines += ["", "## Declared statuses", ""]
    for group, values in report["statuses"].items():
        lines.append(f"### {group.replace('_', ' ').title()}")
        if values:
            lines.extend(f"- {name}: {number}" for name, number in values.items())
        else:
            lines.append("- No records")
        lines.append("")
    lines += ["## Cross-register consistency", ""]
    if report["cross_registry_issues"]:
        for issue in report["cross_registry_issues"]:
            lines.append(f"- **{issue['code']}** ({issue['count']}): {', '.join(issue['ids'])}")
    else:
        lines.append("No missing cross-register identifiers were detected by these checks.")
    lines += [
        "",
        "## Important limits",
        "",
        *[f"- {item}" for item in report["limitations"]],
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in DEFAULTS.items():
        parser.add_argument(f"--{name}", type=Path, default=default, help=f"Input file (default: {default})")
    parser.add_argument("--out", type=Path, help="Write JSON report to this path")
    parser.add_argument("--markdown-out", type=Path, help="Write Markdown report to this path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if cross-register identifier issues exist")
    args = parser.parse_args(argv)
    paths = {name: getattr(args, name) for name in DEFAULTS}
    try:
        report = build_report(paths)
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, ValueError) as exc:
        parser.error(str(exc))
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown(report), encoding="utf-8")
    return 1 if args.strict and report["cross_registry_issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
