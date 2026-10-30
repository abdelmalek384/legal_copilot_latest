#!/usr/bin/env python3
"""Validate source-permission evidence and block unsupported rights claims."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs" / "source_permission_register.json"

COLLECTION_STATES = {
    "unknown",
    "not_allowed_without_explicit_exception_or_license",
    "allowed_limited",
    "allowed",
    "prohibited",
}
COMMERCIAL_STATES = {
    "unknown",
    "not_allowed_without_explicit_exception_or_license",
    "prior_written_permission_required_per_published_terms",
    "allowed_limited",
    "allowed",
    "prohibited",
}
REQUIRED = {
    "source_id", "authority", "source_page", "material_types", "access_status",
    "collection_permission", "commercial_reuse_permission", "required_next_action",
}
EXPLICIT_PERMISSION_STATES = {"allowed", "allowed_limited", "prohibited",
                              "not_allowed_without_explicit_exception_or_license",
                              "prior_written_permission_required_per_published_terms"}


def _https_url(value: object) -> bool:
    if not isinstance(value, str) or not value or value != value.strip() or any(char.isspace() for char in value):
        return False
    try:
        parsed = urlparse(value)
        port = parsed.port
        return (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and (port is None or 1 <= port <= 65535)
            and parsed.username is None
            and parsed.password is None
            and not any(ord(char) < 32 for char in value)
        )
    except ValueError:
        return False


def _valid_review_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError:
        return False
    # Reviewers may record the local Cairo date while GitHub-hosted CI still
    # runs on the previous UTC date. Allow only that one-day timezone skew;
    # genuinely future-dated evidence remains invalid.
    return parsed.isoformat() == value and parsed <= dt.date.today() + dt.timedelta(days=1)


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        return ["root must contain a sources list"]
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if not _valid_review_date(data.get("assessment_date")):
        errors.append("assessment_date must be a valid ISO date no later than today")

    seen: set[str] = set()
    for i, source in enumerate(data["sources"]):
        label = f"sources[{i}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED - source.keys()
        if missing:
            errors.append(f"{label} missing fields: {', '.join(sorted(missing))}")

        sid = source.get("source_id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"{label} requires non-empty source_id")
        elif sid != sid.strip():
            errors.append(f"{label}.source_id must not have surrounding whitespace")
        elif sid in seen:
            errors.append(f"duplicate source_id: {sid}")
        else:
            seen.add(sid)

        if not isinstance(source.get("authority"), str) or not source.get("authority", "").strip():
            errors.append(f"{label}.authority must be a non-empty string")
        if not _https_url(source.get("source_page")):
            errors.append(f"{label}.source_page must be an HTTPS URL without credentials")
        if "terms_url" in source and source["terms_url"] is not None and not _https_url(source["terms_url"]):
            errors.append(f"{label}.terms_url must be an HTTPS URL or null")
        for field in ("permission_evidence_url", "commercial_reuse_evidence_url"):
            if source.get(field) is not None and not _https_url(source.get(field)):
                errors.append(f"{label}.{field} must be an HTTPS URL without credentials or null")
        if source.get("collection_permission") in {"allowed", "allowed_limited"}:
            if not _https_url(source.get("permission_evidence_url")):
                errors.append(f"{label} allowed collection requires permission_evidence_url linking to inspectable rights evidence")

        material_types = source.get("material_types")
        if not isinstance(material_types, list) or not material_types or any(
            not isinstance(item, str) or not item.strip() for item in material_types
        ):
            errors.append(f"{label}.material_types must be a non-empty list of strings")

        collection = source.get("collection_permission")
        commercial = source.get("commercial_reuse_permission")
        if collection not in COLLECTION_STATES:
            errors.append(f"{label}.collection_permission has unsupported value")
        if commercial not in COMMERCIAL_STATES:
            errors.append(f"{label}.commercial_reuse_permission has unsupported value")
        if commercial in {"allowed", "allowed_limited"}:
            commercial_evidence = source.get("commercial_reuse_evidence")
            if not isinstance(commercial_evidence, str) or not commercial_evidence.strip():
                errors.append(f"{label} commercial reuse permission requires separate commercial_reuse_evidence")
            if not _valid_review_date(source.get("commercial_terms_checked_on")):
                errors.append(f"{label} commercial reuse permission requires a valid commercial_terms_checked_on date")
            if not _https_url(source.get("commercial_reuse_evidence_url")):
                errors.append(f"{label} allowed commercial reuse requires commercial_reuse_evidence_url linking to separate inspectable rights evidence")

        checked_on = source.get("terms_checked_on")
        evidence = source.get("permission_evidence")
        explicit_claim = collection in EXPLICIT_PERMISSION_STATES or commercial in EXPLICIT_PERMISSION_STATES
        if explicit_claim:
            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(f"{label} records an explicit permission/restriction state without permission_evidence")
            if not _valid_review_date(checked_on):
                errors.append(f"{label} records an explicit permission/restriction state without a valid terms_checked_on date")
        elif checked_on is not None and not _valid_review_date(checked_on):
            errors.append(f"{label}.terms_checked_on must be a valid ISO date or null")

        if source.get("access_status") is not None and (
            not isinstance(source.get("access_status"), str) or not source.get("access_status", "").strip()
        ):
            errors.append(f"{label}.access_status must be a non-empty string")
        if not isinstance(source.get("required_next_action"), str) or not source.get("required_next_action", "").strip():
            errors.append(f"{label}.required_next_action must be a non-empty string")

    if not data["sources"]:
        errors.append("sources must not be empty")
    return errors


if __name__ == "__main__":
    try:
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Source permission register could not be read: {exc}") from exc
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Source permission register valid: {len(data['sources'])} source records; no permission is inferred.")
