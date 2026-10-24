#!/usr/bin/env python3
"""Validate the metadata-only Phase 2 Egyptian instrument inventory."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "docs" / "phase_2_document_inventory.json"

REQUIRED_DOCUMENT_FIELDS = (
    "document_id", "official_title_ar", "document_type", "source_id",
    "source_status", "collection_permission", "legal_status", "review_status",
)
COLLECTION_STATES = {
    "unknown", "permission_pending", "allowed", "allowed_limited", "prohibited",
    "not_allowed_without_explicit_exception_or_license",
    "prior_written_permission_required_per_published_terms",
}
LEGAL_STATES = {
    "unknown", "not_applicable", "under_review", "not_yet_in_force",
    "in_force", "partially_repealed", "repealed", "historical",
}
REVIEW_STATES = {
    "discovery_only", "blocked_pending_permission", "pending_source_review",
    "pending_lawyer_review", "verified", "rejected",
}
SOURCE_STATES = {
    "discovery_only", "official_copy_candidate", "official_text_candidate",
    "later_official_citation_only", "official_court_candidate",
    "official_index_discovered_primary_text_pending",
}
FORBIDDEN_CONTENT_KEYS = {
    "full_text", "article_text", "passage_text", "downloaded_text",
    "extracted_text", "legal_text", "document_bytes",
}


def _walk(value, path="$"):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, path + "." + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, path + "[" + str(index) + "]")


def validate_inventory(data):
    """Return validation errors; validation never changes permission or legal status."""
    errors = []
    if not isinstance(data, dict):
        return ["inventory root must be an object"]
    for field in ("schema_version", "inventory_id", "prepared_on", "purpose", "policy"):
        if not data.get(field):
            errors.append("missing root field: " + field)
    sources = data.get("source_ids")
    documents = data.get("documents")
    actions = data.get("next_actions")
    if not isinstance(sources, dict) or not sources:
        errors.append("source_ids must be a non-empty object")
        sources = {}
    if not isinstance(documents, list) or not documents:
        errors.append("documents must be a non-empty list")
        documents = []
    if not isinstance(actions, list) or not actions:
        errors.append("next_actions must be a non-empty list")
        actions = []

    ids = []
    for index, document in enumerate(documents):
        label = "document[%d]" % index
        if not isinstance(document, dict):
            errors.append(label + " must be an object")
            continue
        for field in REQUIRED_DOCUMENT_FIELDS:
            if document.get(field) is None or document.get(field) == "":
                errors.append(label + " missing " + field)
        document_id = document.get("document_id")
        if document_id:
            ids.append(document_id)
        source_id = document.get("source_id")
        if source_id and source_id not in sources:
            errors.append(label + " references unknown source_id " + str(source_id))
        if document.get("source_status") not in SOURCE_STATES:
            errors.append(label + " has unsupported source_status")
        if document.get("collection_permission") not in COLLECTION_STATES:
            errors.append(label + " has unsupported collection_permission")
        if document.get("legal_status") not in LEGAL_STATES:
            errors.append(label + " has unsupported legal_status")
        if document.get("review_status") not in REVIEW_STATES:
            errors.append(label + " has unsupported review_status")
        if document.get("review_status") == "verified":
            if document.get("collection_permission") != "allowed":
                errors.append(label + " cannot be verified without explicit collection permission")
            if document.get("commercial_reuse_permission") != "allowed":
                errors.append(label + " cannot be verified without explicit commercial reuse permission")
            if not str(document.get("permission_evidence") or "").strip():
                errors.append(label + " cannot be verified without permission evidence")
        if document.get("legal_status") == "in_force":
            if document.get("review_status") != "verified" or not document.get("effective_date"):
                errors.append(label + " cannot be labelled in_force without verified review and effective_date")
        for path, value in _walk(document, label):
            if isinstance(value, dict):
                for key in value:
                    if key.lower() in FORBIDDEN_CONTENT_KEYS:
                        errors.append(path + " contains content field " + key)
                    if key in {"url", "source_url"} and value[key] is not None:
                        if not isinstance(value[key], str) or not value[key].startswith("https://"):
                            errors.append(path + "." + key + " must be HTTPS or null")
            elif isinstance(value, str) and value.startswith(("http://", "https://")):
                # URLs are accepted only in explicitly named URL fields.
                final_key = path.rsplit(".", 1)[-1]
                if final_key not in {"source_url", "url"}:
                    errors.append(path + " stores a URL under an unexpected field")

    if len(ids) != len(set(ids)):
        errors.append("duplicate document_id values")
    action_ids = []
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            errors.append("next_actions[%d] must be an object" % index)
            continue
        for field in ("id", "action", "owner", "status"):
            if not action.get(field):
                errors.append("next_actions[%d] missing %s" % (index, field))
        if action.get("id"):
            action_ids.append(action["id"])
        if action.get("status") not in {"not_started", "in_progress", "blocked", "complete"}:
            errors.append("next_actions[%d] has unsupported status" % index)
    if len(action_ids) != len(set(action_ids)):
        errors.append("duplicate next_action IDs")
    return errors


def main():
    data = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))
    errors = validate_inventory(data)
    if errors:
        raise SystemExit("INVENTORY VALIDATION FAILED:\n- " + "\n- ".join(errors))
    print(
        "Phase 2 metadata inventory validation passed: "
        + str(len(data["documents"])) + " instruments, "
        + str(len(data["source_ids"])) + " source records; metadata-only and permission-gated."
    )


if __name__ == "__main__":
    main()
