#!/usr/bin/env python3
"""Validate source permission register shape and block accidental permission claims."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs" / "source_permission_register.json"
ALLOWED_COLLECTION = {"unknown", "not_allowed_without_explicit_exception_or_license", "allowed_limited", "allowed", "prohibited"}
REQUIRED = {"source_id", "authority", "source_page", "material_types", "access_status", "collection_permission", "commercial_reuse_permission", "required_next_action"}

def validate(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        return ["root must contain a sources list"]
    seen = set()
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
        elif sid in seen:
            errors.append(f"duplicate source_id: {sid}")
        else:
            seen.add(sid)
        for field in ("source_page", "terms_url"):
            value = source.get(field)
            if value is None and field == "terms_url":
                continue
            if not isinstance(value, str) or urlparse(value).scheme != "https" or not urlparse(value).netloc:
                errors.append(f"{label}.{field} must be an HTTPS URL")
        permission = source.get("collection_permission")
        if permission not in ALLOWED_COLLECTION:
            errors.append(f"{label}.collection_permission has unsupported value")
        # A permission claim is invalid without evidence and a review date.
        if permission in {"allowed", "allowed_limited"}:
            if not source.get("permission_evidence") or not source.get("terms_checked_on"):
                errors.append(f"{label} claims permission without permission_evidence and terms_checked_on")
    return errors

if __name__ == "__main__":
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Source permission register valid: {len(data['sources'])} source records; no permission is inferred.")
