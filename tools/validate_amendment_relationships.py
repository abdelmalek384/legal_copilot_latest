#!/usr/bin/env python3
"""Validate structural integrity of the Phase 2 legal-instrument relationship register.

Read-only preflight. It does not verify legislation, establish legal effect, or approve
a consolidated/current-law view.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELATIONSHIPS = ROOT / "docs" / "phase_2_amendment_relationships.json"
DEFAULT_INVENTORY = ROOT / "docs" / "phase_2_document_inventory.json"
BASE_TYPES = {"base_instrument"}
KNOWN_RELATIONSHIP_TYPES = {
    "base_instrument",
    "amends_commencement_provision",
    "amends_specified_provisions",
    "amends_specified_schedules",
    "repeals",
    "repeals_specified_provisions",
    "corrects",
    "supersedes",
    "implements",
    "consolidates",
}
KNOWN_STATES = {
    "official_text_discovered_provision_mapping_pending",
    "source_discovered_instrument_record_pending",
    "later_official_citation_only",
    "provision_mapping_pending",
    "under_review",
    "reviewed_confirmed",
    "reviewed_rejected",
}


def _https_url(value: object) -> bool:
    """Validate URL syntax only; the audit does not verify evidence authenticity."""
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if any(ch.isspace() or ord(ch) < 32 for ch in value):
        return False
    try:
        parsed = urlparse(value)
        port = parsed.port  # Forces urllib to reject malformed and out-of-range ports.
        return (
            parsed.scheme.lower() == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not parsed.netloc.endswith(":")
            and (port is None or 1 <= port <= 65535)
        )
    except (ValueError, TypeError):
        return False


def validate(relationships_doc: dict, inventory_doc: dict) -> dict:
    issues: list[dict] = []
    relationships = relationships_doc.get("relationships") if isinstance(relationships_doc, dict) else None
    documents = inventory_doc.get("documents") if isinstance(inventory_doc, dict) else None
    if not isinstance(relationships, list):
        return {
            "schema_version": "1.0",
            "audit_type": "read_only_amendment_relationship_integrity",
            "schema_error": "relationship register must contain a relationships list",
            "relationships_checked": 0,
            "error_count": 0,
            "warning_count": 0,
            "errors": [],
            "warnings": [],
            "limitations": [
                "Schema errors prevent structural validation; no legal status or effect is inferred."
            ],
        }
    if not isinstance(documents, list):
        return {
            "schema_version": "1.0",
            "audit_type": "read_only_amendment_relationship_integrity",
            "schema_error": "document inventory must contain a documents list",
            "relationships_checked": len(relationships),
            "error_count": 0,
            "warning_count": 0,
            "errors": [],
            "warnings": [],
            "limitations": [
                "Schema errors prevent structural validation; no legal status or effect is inferred."
            ],
        }

    document_ids: set[str] = set()
    seen_document_ids: set[str] = set()
    seen: set[str] = set()
    errors: list[dict] = []
    warnings: list[dict] = []

    def add(severity: str, code: str, relationship_id: str | None, detail: str) -> None:
        target = errors if severity == "error" else warnings
        target.append({
            "severity": severity,
            "code": code,
            "relationship_id": relationship_id,
            "detail": detail,
        })

    for index, item in enumerate(documents):
        if not isinstance(item, dict):
            add("error", "invalid_document_entry", None, f"Inventory entry at index {index} is not an object.")
            continue
        document_id = item.get("document_id")
        if not isinstance(document_id, str) or not document_id.strip():
            add("error", "missing_document_id", None, f"Inventory entry at index {index} must have a non-empty document_id.")
            continue
        if document_id in seen_document_ids:
            add("error", "duplicate_document_id", None, f"document_id {document_id!r} occurs more than once in the inventory.")
            continue
        seen_document_ids.add(document_id)
        document_ids.add(document_id)

    for index, item in enumerate(relationships):
        if not isinstance(item, dict):
            add("error", "invalid_relationship_entry", None, f"Entry at index {index} is not an object.")
            continue
        rid = item.get("relationship_id")
        rid_label = rid if isinstance(rid, str) and rid.strip() else None
        if rid_label is None:
            add("error", "missing_relationship_id", None, f"Entry at index {index} has no relationship_id.")
        elif rid_label in seen:
            add("error", "duplicate_relationship_id", rid_label, "relationship_id must be unique.")
        else:
            seen.add(rid_label)

        source_id = item.get("source_instrument_id")
        target_id = item.get("target_instrument_id")
        relation_type = item.get("relationship_type")
        status = item.get("status")

        if not isinstance(source_id, str) or source_id not in document_ids:
            add("error", "source_instrument_missing_from_inventory", rid_label, f"Unknown source instrument: {source_id!r}.")
        if not isinstance(relation_type, str) or relation_type not in KNOWN_RELATIONSHIP_TYPES:
            add("error", "unknown_relationship_type", rid_label, f"Unrecognized relationship_type: {relation_type!r}.")
        if relation_type == "base_instrument":
            if target_id is not None:
                add("error", "base_instrument_must_not_have_target", rid_label, "A base_instrument record must use target_instrument_id=null.")
        elif not isinstance(target_id, str) or target_id not in document_ids:
            add("error", "target_instrument_missing_from_inventory", rid_label, f"Non-base relationship target is missing or unknown: {target_id!r}.")

        if not _https_url(item.get("source_url")):
            add("error", "missing_or_invalid_https_source_url", rid_label, "A direct evidence URL using HTTPS is required.")
        evidence = item.get("required_evidence")
        if not isinstance(evidence, list) or not evidence or any(not isinstance(x, str) or not x.strip() for x in evidence):
            add("error", "required_evidence_list_missing", rid_label, "required_evidence must be a non-empty list of non-empty strings.")

        if not isinstance(status, str) or status not in KNOWN_STATES:
            add("warning", "unrecognized_or_missing_status", rid_label, f"Review status requires normalization: {status!r}.")
        if status != "reviewed_confirmed":
            add("warning", "relationship_not_reviewed_confirmed", rid_label, "Do not treat this edge as legally confirmed or use it alone to construct current law.")
        if relation_type != "base_instrument" and not item.get("affected_provision") and not item.get("affected_provisions"):
            add("warning", "provision_mapping_not_recorded", rid_label, "Record affected articles/schedules when evidence supports the mapping.")
        effective_date = item.get("instrument_effective_date")
        if effective_date not in (None, "unknown_pending_gazette_verification"):
            valid_date = False
            if isinstance(effective_date, str):
                try:
                    parsed_date = date.fromisoformat(effective_date)
                    valid_date = parsed_date.isoformat() == effective_date
                except ValueError:
                    valid_date = False
            if not valid_date:
                add("error", "invalid_effective_date_value", rid_label, "Effective date must be a valid calendar date in YYYY-MM-DD format, null, or the explicit unknown sentinel.")
        if effective_date == "unknown_pending_gazette_verification":
            add("warning", "effective_date_unknown", rid_label, "Unknown commencement/effective date remains unresolved; do not infer it from publication date.")

        # A status label alone must never make a relationship look legally confirmed.
        # Require an explicit, inspectable review record and the key publication
        # metadata before accepting reviewed_confirmed as structurally complete.
        if status == "reviewed_confirmed":
            confirmation = item.get("confirmation_evidence")
            if not isinstance(confirmation, dict):
                add(
                    "error",
                    "confirmed_relationship_missing_confirmation_evidence",
                    rid_label,
                    "reviewed_confirmed requires a confirmation_evidence object with Gazette publication and reviewer details.",
                )
            else:
                for field in ("gazette_issue", "gazette_page_range", "reviewer_id", "review_basis"):
                    value = confirmation.get(field)
                    if not isinstance(value, str) or not value.strip():
                        add(
                            "error",
                            "confirmed_relationship_missing_confirmation_field",
                            rid_label,
                            f"confirmation_evidence.{field} must be a non-empty string.",
                        )
                if confirmation.get("reviewer_role") != "qualified_egyptian_lawyer":
                    add(
                        "error",
                        "confirmed_relationship_reviewer_not_qualified",
                        rid_label,
                        "confirmation_evidence.reviewer_role must be qualified_egyptian_lawyer before a legal relationship can be marked reviewed_confirmed.",
                    )
                if not _https_url(confirmation.get("evidence_url")):
                    add(
                        "error",
                        "confirmed_relationship_missing_traceable_evidence_url",
                        rid_label,
                        "confirmation_evidence.evidence_url must be a valid HTTPS URL without embedded credentials.",
                    )
                evidence_hash = confirmation.get("evidence_sha256")
                if not (
                    isinstance(evidence_hash, str)
                    and len(evidence_hash) == 64
                    and all(ch in "0123456789abcdefABCDEF" for ch in evidence_hash)
                ):
                    add(
                        "error",
                        "confirmed_relationship_invalid_evidence_sha256",
                        rid_label,
                        "confirmation_evidence.evidence_sha256 must be a 64-character hexadecimal SHA-256 digest for the reviewed evidence artifact.",
                    )
                parsed_dates = {}
                for field in ("gazette_publication_date", "reviewed_on"):
                    value = confirmation.get(field)
                    valid_date = False
                    parsed_date = None
                    if isinstance(value, str):
                        try:
                            parsed_date = date.fromisoformat(value)
                            valid_date = parsed_date.isoformat() == value
                        except ValueError:
                            valid_date = False
                    if not valid_date:
                        add(
                            "error",
                            "confirmed_relationship_invalid_confirmation_date",
                            rid_label,
                            f"confirmation_evidence.{field} must be a real YYYY-MM-DD calendar date.",
                        )
                    elif parsed_date is not None:
                        parsed_dates[field] = parsed_date
                        if parsed_date > date.today():
                            add(
                                "error",
                                "confirmed_relationship_future_confirmation_date",
                                rid_label,
                                f"confirmation_evidence.{field} cannot be in the future.",
                            )
                if (
                    "gazette_publication_date" in parsed_dates
                    and "reviewed_on" in parsed_dates
                    and parsed_dates["reviewed_on"] < parsed_dates["gazette_publication_date"]
                ):
                    add(
                        "error",
                        "confirmed_relationship_review_precedes_publication",
                        rid_label,
                        "The confirmation review date cannot precede the Gazette publication date.",
                    )
            if relation_type != "base_instrument" and not item.get("affected_provision") and not item.get("affected_provisions"):
                add(
                    "error",
                    "confirmed_relationship_missing_provision_mapping",
                    rid_label,
                    "A confirmed non-base relationship requires an explicit affected article, provision, or schedule mapping.",
                )
            if effective_date in (None, "unknown_pending_gazette_verification"):
                add(
                    "error",
                    "confirmed_relationship_effective_date_unresolved",
                    rid_label,
                    "A confirmed relationship must record a verified effective date; publication date alone is not a substitute.",
                )

    # Build a metadata-only directed graph to flag duplicate edges and cycles for review.
    # These are warnings, not legal conclusions: cross-amendments can be legally complex.
    adjacency: dict[str, list[tuple[str, str]]] = {}
    seen_edges: dict[tuple[str, str, str, str], str] = {}
    cycle_signatures: set[frozenset[str]] = set()
    for item in relationships:
        if not isinstance(item, dict):
            continue
        source_id = item.get("source_instrument_id")
        target_id = item.get("target_instrument_id")
        relation_type = item.get("relationship_type")
        rid = item.get("relationship_id")
        if (
            not isinstance(relation_type, str)
            or relation_type not in KNOWN_RELATIONSHIP_TYPES
            or relation_type == "base_instrument"
            or not isinstance(source_id, str)
            or source_id not in document_ids
            or not isinstance(target_id, str)
            or target_id not in document_ids
        ):
            continue

        affected = item.get("affected_provision", item.get("affected_provisions"))
        affected_key = json.dumps(affected, ensure_ascii=False, sort_keys=True, default=str)
        edge_key = (source_id, target_id, relation_type, affected_key)
        if edge_key in seen_edges:
            add(
                "warning",
                "duplicate_relationship_edge",
                rid if isinstance(rid, str) else None,
                f"Relationship duplicates edge {seen_edges[edge_key]!r} for the same source, target, type, and affected-provision metadata.",
            )
        else:
            seen_edges[edge_key] = rid if isinstance(rid, str) else "(missing relationship ID)"
        adjacency.setdefault(source_id, []).append(
            (target_id, rid if isinstance(rid, str) else "(missing relationship ID)")
        )

    visited: set[str] = set()
    active: list[str] = []
    active_set: set[str] = set()

    def visit(node: str) -> None:
        visited.add(node)
        active.append(node)
        active_set.add(node)
        for target, _relationship_id in sorted(adjacency.get(node, [])):
            if target in active_set:
                cycle_start = active.index(target)
                cycle_nodes = active[cycle_start:] + [target]
                signature = frozenset(cycle_nodes)
                if signature not in cycle_signatures:
                    cycle_signatures.add(signature)
                    add(
                        "warning",
                        "relationship_graph_cycle_detected",
                        None,
                        "Directed instrument relationship cycle needs manual review: " + " -> ".join(cycle_nodes) + ".",
                    )
            elif target not in visited:
                visit(target)
        active.pop()
        active_set.remove(node)

    for node in sorted(adjacency):
        if node not in visited:
            visit(node)

    return {
        "schema_version": "1.0",
        "audit_type": "read_only_amendment_relationship_integrity",
        "relationships_checked": len(relationships),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "Structural validation does not establish that an instrument exists, the source is authentic, or the described legal effect is correct.",
            "An amendment edge requires the official instrument, exact provision mapping, publication and commencement analysis, and qualified Egyptian-lawyer review before use in current-law answers.",
            "The tool does not download documents, alter relationship status, or consolidate legal text.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--relationships", type=Path, default=DEFAULT_RELATIONSHIPS)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--out", type=Path, help="Optional JSON report path")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if structural errors are found")
    args = parser.parse_args()
    try:
        relationships_doc = json.loads(args.relationships.read_text(encoding="utf-8"))
        inventory_doc = json.loads(args.inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    report = validate(relationships_doc, inventory_doc)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if report.get("schema_error"):
        return 2
    if args.strict and report["error_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
