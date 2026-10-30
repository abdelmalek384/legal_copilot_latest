#!/usr/bin/env python3
"""Validate explicit operational evidence required before production database release."""
from __future__ import annotations

import hashlib
import json
import os
import stat
from datetime import datetime, timedelta, timezone
from pathlib import Path

REQUIRED_GATES = {
    "original_file_storage": {
        "description": "Live object-storage, KMS/key policy, authorization, integrity, and reconciliation validation",
        "fields": ("verified_at", "verified_by", "storage_config_sha256"),
        "witness_required": False,
        "max_age_days": 90,
    },
    "backup_restore_rollback": {
        "description": "Witnessed staging restore, rollback, staged-upload recovery, and deletion-recovery drill",
        "fields": ("verified_at", "verified_by", "witnessed_by"),
        "witness_required": True,
        "required_scenarios": ("staging_restore", "rollback", "staged_upload_recovery", "deletion_recovery"),
        "max_age_days": 90,
    },
    "retention_export_deletion_policy": {
        "description": "Approved retention, tenant export, and deletion policy",
        "fields": ("approved_at", "approved_by"),
        "witness_required": False,
        "max_age_days": 365,
    },
    "production_identity_email": {
        "description": "Production email delivery, recovery messaging, and multi-host rate-limit validation",
        "fields": ("verified_at", "verified_by"),
        "witness_required": False,
        "max_age_days": 90,
    },
    "privileged_recovery_bootstrap": {
        "description": "Privileged-account recovery and first-platform-admin bootstrap rehearsal",
        "fields": ("verified_at", "verified_by", "witnessed_by"),
        "witness_required": True,
        "max_age_days": 180,
    },
    "independent_security_review": {
        "description": "Independent security review with no unresolved critical/high findings",
        "fields": ("reviewed_at", "reviewer"),
        "witness_required": False,
        "max_age_days": 90,
    },
}


def original_storage_config_fingerprint(env: object | None = None) -> str | None:
    """Fingerprint non-secret S3/KMS target settings so evidence cannot be reused for another target."""
    source = os.environ if env is None else env
    if not hasattr(source, "get"):
        return None
    values = {
        "backend": str(source.get("COPILOT_OBJECT_STORAGE_BACKEND", "")).strip().lower(),
        "bucket": str(source.get("COPILOT_S3_BUCKET", "")).strip(),
        "region": str(source.get("COPILOT_S3_REGION", "")).strip(),
        "kms_key_id": str(source.get("COPILOT_S3_KMS_KEY_ID", "")).strip(),
        "endpoint_url": str(source.get("COPILOT_S3_ENDPOINT_URL", "")).strip(),
    }
    if values["backend"] != "s3" or not values["bucket"] or not values["region"] or not values["kms_key_id"]:
        return None
    payload = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_acceptance_manifest(manifest: object, *, now: datetime | None = None, expected_storage_config_sha256: str | None = None) -> dict:
    """Return a sanitized decision; never echo evidence references or secret values."""
    blockers: list[dict[str, str]] = []
    if not isinstance(manifest, dict):
        return {
            "ready": False,
            "decision": "blocked",
            "passed_count": 0,
            "required_count": len(REQUIRED_GATES),
            "blockers": [{"gate": "manifest", "code": "invalid_manifest_shape"}],
        }
    if type(manifest.get("schema_version")) is not int or manifest.get("schema_version") != 1:
        blockers.append({"gate": "manifest", "code": "unsupported_schema_version"})
    gates = manifest.get("gates")
    if not isinstance(gates, dict):
        gates = {}
        blockers.append({"gate": "manifest", "code": "gates_object_missing"})
    for name in sorted(set(gates) - set(REQUIRED_GATES)):
        blockers.append({"gate": name, "code": "unexpected_gate"})
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    current = current.astimezone(timezone.utc)
    passed_count = 0
    for name, spec in REQUIRED_GATES.items():
        item = gates.get(name)
        if not isinstance(item, dict):
            blockers.append({"gate": name, "code": "evidence_missing"})
            continue
        if item.get("status") != "passed":
            blockers.append({"gate": name, "code": "not_passed"})
            continue
        required_fields = ("evidence_ref",) + spec["fields"]
        missing_fields = [
            field for field in required_fields
            if not isinstance(item.get(field), str) or not item[field].strip()
        ]
        if missing_fields:
            blockers.append({"gate": name, "code": "required_evidence_fields_missing"})
            continue
        required_scenarios = spec.get("required_scenarios", ())
        if required_scenarios:
            verified_scenarios = item.get("verified_scenarios")
            if (
                not isinstance(verified_scenarios, list)
                or any(not isinstance(value, str) or not value.strip() for value in verified_scenarios)
            ):
                blockers.append({"gate": name, "code": "invalid_verified_scenarios"})
                continue
            missing_scenarios = sorted(set(required_scenarios) - set(verified_scenarios))
            if missing_scenarios:
                blockers.append({"gate": name, "code": "required_scenarios_missing"})
                continue
        if name == "original_file_storage":
            recorded_fingerprint = item.get("storage_config_sha256")
            if not _valid_sha256(recorded_fingerprint):
                blockers.append({"gate": name, "code": "invalid_storage_configuration_fingerprint"})
                continue
            if expected_storage_config_sha256 is not None:
                if not _valid_sha256(expected_storage_config_sha256):
                    blockers.append({"gate": name, "code": "storage_configuration_unavailable"})
                    continue
                if recorded_fingerprint.lower() != expected_storage_config_sha256.lower():
                    blockers.append({"gate": name, "code": "storage_configuration_mismatch"})
                    continue
        evidence_ref = item["evidence_ref"].strip()
        if len(evidence_ref) > 500 or evidence_ref.lower() in {"todo", "tbd", "pending", "n/a"}:
            blockers.append({"gate": name, "code": "invalid_evidence_reference"})
            continue
        timestamp_fields = [field for field in spec["fields"] if field.endswith("_at")]
        timestamps_valid = True
        for field in timestamp_fields:
            parsed = _timestamp(item.get(field))
            if parsed is None:
                blockers.append({"gate": name, "code": "invalid_or_timezone_free_timestamp"})
                timestamps_valid = False
                break
            if parsed > current + timedelta(minutes=5):
                blockers.append({"gate": name, "code": "evidence_timestamp_in_future"})
                timestamps_valid = False
                break
            if current - parsed > timedelta(days=spec["max_age_days"]):
                blockers.append({"gate": name, "code": "evidence_expired"})
                timestamps_valid = False
                break
        if not timestamps_valid:
            continue
        if spec["witness_required"]:
            actor = item.get("verified_by")
            witness = item.get("witnessed_by")
            if not isinstance(actor, str) or not isinstance(witness, str) or actor.strip().casefold() == witness.strip().casefold():
                blockers.append({"gate": name, "code": "independent_witness_required"})
                continue
        if name == "independent_security_review":
            unresolved = item.get("unresolved_critical_high")
            if type(unresolved) is not int or unresolved != 0:
                blockers.append({"gate": name, "code": "unresolved_critical_or_high_findings"})
                continue
            reviewer = item.get("reviewer", "").strip().casefold()
            operational_actors = set()
            for other_name, other_item in gates.items():
                if other_name == name or not isinstance(other_item, dict) or other_item.get("status") != "passed":
                    continue
                for actor_field in ("verified_by", "witnessed_by", "approved_by"):
                    actor = other_item.get(actor_field)
                    if isinstance(actor, str) and actor.strip():
                        operational_actors.add(actor.strip().casefold())
            if reviewer in operational_actors:
                blockers.append({"gate": name, "code": "reviewer_not_independent_of_operators"})
                continue
        passed_count += 1
    return {
        "ready": not blockers and passed_count == len(REQUIRED_GATES),
        "decision": "ready" if not blockers and passed_count == len(REQUIRED_GATES) else "blocked",
        "passed_count": passed_count,
        "required_count": len(REQUIRED_GATES),
        "blockers": blockers,
    }


class AcceptanceManifestFileError(ValueError):
    """A sanitized filesystem-integrity rejection for the acceptance manifest."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _read_acceptance_manifest_file(path: Path) -> object:
    """Read a bounded regular file without following a manifest symlink."""
    if path.is_symlink():
        raise AcceptanceManifestFileError("manifest_symlink_forbidden")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode):
            raise AcceptanceManifestFileError("manifest_not_regular_file")
        if metadata.st_size > 1_000_000:
            raise AcceptanceManifestFileError("manifest_too_large")
        if os.name == "posix" and stat.S_IMODE(metadata.st_mode) & 0o022:
            raise AcceptanceManifestFileError("manifest_group_or_other_writable")
        return json.load(stream)


def load_acceptance_manifest(path: str | Path | None, *, now: datetime | None = None, expected_storage_config_sha256: str | None = None) -> dict:
    if path is None:
        return {
            "ready": False,
            "decision": "blocked",
            "passed_count": 0,
            "required_count": len(REQUIRED_GATES),
            "blockers": [{"gate": "manifest", "code": "manifest_path_required"}],
        }
    manifest_path = Path(path).expanduser()
    try:
        manifest = _read_acceptance_manifest_file(manifest_path)
    except AcceptanceManifestFileError as exc:
        return {
            "ready": False,
            "decision": "blocked",
            "passed_count": 0,
            "required_count": len(REQUIRED_GATES),
            "blockers": [{"gate": "manifest", "code": exc.code}],
        }
    except FileNotFoundError:
        return {
            "ready": False,
            "decision": "blocked",
            "passed_count": 0,
            "required_count": len(REQUIRED_GATES),
            "blockers": [{"gate": "manifest", "code": "manifest_not_found"}],
        }
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "ready": False,
            "decision": "blocked",
            "passed_count": 0,
            "required_count": len(REQUIRED_GATES),
            "blockers": [{"gate": "manifest", "code": "manifest_unreadable_or_invalid_json"}],
        }
    return validate_acceptance_manifest(manifest, now=now, expected_storage_config_sha256=expected_storage_config_sha256)

def load_staging_purge_acceptance_manifest(
    path: str | Path | None,
    *,
    expected_storage_config_sha256: str | None,
    now: datetime | None = None,
) -> dict:
    """Validate live-storage and retention gates for a synthetic staging purge drill."""
    if path is None:
        return {
            "ready": False, "decision": "blocked", "passed_count": 0,
            "required_count": 2,
            "blockers": [{"gate": "manifest", "code": "manifest_path_required"}],
        }
    try:
        manifest = _read_acceptance_manifest_file(Path(path).expanduser())
    except AcceptanceManifestFileError as exc:
        return {
            "ready": False, "decision": "blocked", "passed_count": 0,
            "required_count": 2,
            "blockers": [{"gate": "manifest", "code": exc.code}],
        }
    except FileNotFoundError:
        return {
            "ready": False, "decision": "blocked", "passed_count": 0,
            "required_count": 2,
            "blockers": [{"gate": "manifest", "code": "manifest_not_found"}],
        }
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "ready": False, "decision": "blocked", "passed_count": 0,
            "required_count": 2,
            "blockers": [{"gate": "manifest", "code": "manifest_unreadable_or_invalid_json"}],
        }
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        return {
            "ready": False, "decision": "blocked", "passed_count": 0,
            "required_count": 2,
            "blockers": [{"gate": "manifest", "code": "invalid_manifest"}],
        }
    gates = manifest.get("gates")
    if not isinstance(gates, dict):
        return {
            "ready": False, "decision": "blocked", "passed_count": 0,
            "required_count": 2,
            "blockers": [{"gate": "manifest", "code": "gates_missing"}],
        }
    current = now or datetime.now(timezone.utc)
    blockers = []
    passed = 0
    for name in ("original_file_storage", "retention_export_deletion_policy"):
        spec = REQUIRED_GATES[name]
        item = gates.get(name)
        if not isinstance(item, dict) or item.get("status") != "passed":
            blockers.append({"gate": name, "code": "not_passed"})
            continue
        if not isinstance(item.get("evidence_ref"), str) or not item["evidence_ref"].strip():
            blockers.append({"gate": name, "code": "evidence_missing"})
            continue
        actor_field = "verified_by" if name == "original_file_storage" else "approved_by"
        time_field = "verified_at" if name == "original_file_storage" else "approved_at"
        if not isinstance(item.get(actor_field), str) or not item[actor_field].strip():
            blockers.append({"gate": name, "code": "actor_missing"})
            continue
        timestamp = _timestamp(item.get(time_field))
        if timestamp is None or timestamp > current + timedelta(minutes=5):
            blockers.append({"gate": name, "code": "timestamp_invalid"})
            continue
        if current - timestamp > timedelta(days=spec["max_age_days"]):
            blockers.append({"gate": name, "code": "evidence_expired"})
            continue
        if name == "original_file_storage" and (
            not expected_storage_config_sha256
            or item.get("storage_config_sha256") != expected_storage_config_sha256
        ):
            blockers.append({"gate": name, "code": "storage_target_mismatch"})
            continue
        passed += 1
    return {
        "ready": not blockers and passed == 2,
        "decision": "ready" if not blockers and passed == 2 else "blocked",
        "passed_count": passed,
        "required_count": 2,
        "blockers": blockers,
    }

