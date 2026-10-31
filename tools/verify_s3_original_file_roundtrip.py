#!/usr/bin/env python3
"""Explicit live S3/KMS original-file acceptance probe for a synthetic firm.

This command performs a write/read/delete round trip with synthetic bytes. It is
not a production-release approval: independent policy review and witnessed
backup/restore/deletion drills remain separate mandatory gates.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from database_runtime import DatabaseRuntime
from s3_original_file_storage import S3PrivateObjectStore
from tools.validate_s3_original_file_storage import validate_s3_configuration
from tools.database_release_acceptance import original_storage_config_fingerprint


def verify_synthetic_firm(runtime: DatabaseRuntime, firm_id: int) -> dict[str, Any]:
    """Require a dedicated empty acceptance firm before writing a probe object."""
    if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
        raise ValueError("firm_id must be a positive integer")
    control = runtime.control_connection()
    firm = control.execute(
        "SELECT id,name,status FROM firms WHERE id=?", (firm_id,)
    ).fetchone()
    if firm is None or not str(firm["name"]).startswith("SYNTHETIC-ACCEPTANCE-"):
        raise ValueError("firm must be a provisioned SYNTHETIC-ACCEPTANCE-* test firm")
    if firm["status"] != "active":
        raise ValueError("synthetic acceptance firm must be active for trusted storage routing")
    catalog = control.execute(
        "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
        (firm_id,),
    ).fetchone()
    if catalog is None or catalog["status"] != "provisioned" or not catalog["database_file"]:
        raise ValueError("synthetic acceptance firm must have a provisioned tenant database")
    membership = control.execute(
        "SELECT user_id FROM firm_memberships WHERE firm_id=? AND status='active' "
        "ORDER BY user_id LIMIT 1",
        (firm_id,),
    ).fetchone()
    if membership is None:
        raise ValueError("synthetic acceptance firm needs an active membership for trusted routing")
    context = runtime.resolve_context(int(membership["user_id"]), firm_id)
    tenant = runtime.firm_connection(context)
    # Count every application table, not just cases and object metadata. A tenant
    # with orphaned chunks, documents, audit rows, or lifecycle records is not an
    # empty acceptance target and must never be used for a live probe.
    metadata_tables = {"database_profile", "schema_migrations", "tenant_database_binding"}
    table_names = [
        str(row[0]) for row in tenant.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        if str(row[0]) not in metadata_tables and not str(row[0]).startswith("chunks_fts_")
    ]
    tenant_data_counts: dict[str, int] = {}
    for table_name in table_names:
        quoted = '"' + table_name.replace('"', '""') + '"'
        count = int(tenant.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0])
        if count:
            tenant_data_counts[table_name] = count
    case_count = tenant_data_counts.get("cases", 0)
    object_count = tenant_data_counts.get("original_file_objects", 0)
    if case_count:
        raise ValueError("synthetic acceptance firm must contain no cases")
    if object_count:
        raise ValueError("synthetic acceptance firm must contain no original-file metadata")
    unexpected_data = {
        table: count for table, count in tenant_data_counts.items()
        if table not in {"cases", "original_file_objects"}
    }
    if unexpected_data:
        table_list = ", ".join(sorted(unexpected_data))
        raise ValueError(
            "synthetic acceptance firm must contain no tenant matter data; "
            f"non-empty tables: {table_list}"
        )
    return {
        "firm_id": firm_id,
        "firm_name": str(firm["name"]),
        "case_count": case_count,
        "original_file_metadata_count": object_count,
        "nonempty_tenant_tables": tenant_data_counts,
    }


def run_s3_roundtrip(store: S3PrivateObjectStore, firm_id: int, payload: bytes | None = None) -> dict[str, Any]:
    """Exercise staged write, KMS verification, finalization, readback, and cleanup."""
    import hashlib
    import os

    if payload is None:
        payload = b"LEGAL-COPILOT-S3-ACCEPTANCE-V1:" + os.urandom(32)
    if not isinstance(payload, bytes) or not payload:
        raise ValueError("acceptance payload must be non-empty synthetic bytes")
    expected_digest = hashlib.sha256(payload).hexdigest()
    checks: list[dict[str, Any]] = []
    staged = None
    cleanup_pending = False

    def record(name: str, passed: bool, detail: str):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    try:
        staged = store.stage(firm_id, payload)
        record("stage", True, "synthetic bytes staged under an opaque firm-scoped key")
        staged_ok = store.verify_staged(
            firm_id, staged.object_id, expected_sha256=expected_digest, expected_size=len(payload)
        )
        record("staged_integrity_and_kms", staged_ok, "staged bytes and configured KMS identity verified")
        if not staged_ok:
            raise RuntimeError("staged object verification failed")

        store.finalize(firm_id, staged.object_id)
        presence = store.object_presence(firm_id, staged.object_id)
        finalized_ok = presence == (False, True)
        record("finalization", finalized_ok, "final object exists and staged key is absent")
        if not finalized_ok:
            raise RuntimeError("finalized object state is inconsistent")

        final_ok = store.verify(
            firm_id, staged.object_id, expected_sha256=expected_digest, expected_size=len(payload)
        )
        record("final_integrity_and_kms", final_ok, "final object digest, size, and KMS identity verified")
        if not final_ok:
            raise RuntimeError("final object integrity verification failed")

        with store.open(firm_id, staged.object_id) as handle:
            readback = handle.read()
        readback_ok = readback == payload
        record("authorized_adapter_readback", readback_ok, "readback bytes match the synthetic payload")
        if not readback_ok:
            raise RuntimeError("final object readback mismatch")

        deleted = store.delete(firm_id, staged.object_id)
        empty_after_delete = store.object_presence(firm_id, staged.object_id) == (False, False)
        cleanup_ok = deleted and empty_after_delete
        record("cleanup", cleanup_ok, "probe keys removed from the active object namespace")
        if not cleanup_ok:
            raise RuntimeError("probe object cleanup could not be confirmed")
        return {"passed": True, "object_id": staged.object_id, "sha256": expected_digest,
                "byte_size": len(payload), "checks": checks, "cleanup_pending": False}
    except Exception as exc:
        if staged is not None:
            try:
                store.delete(firm_id, staged.object_id)
                presence = store.object_presence(firm_id, staged.object_id)
                cleanup_pending = presence != (False, False)
            except Exception:
                # Provider policy or transport failures can prevent cleanup;
                # leave the opaque object ID for operator reconciliation.
                cleanup_pending = True
        return {
            "passed": False,
            "object_id": staged.object_id if staged is not None else None,
            "sha256": expected_digest,
            "byte_size": len(payload),
            "checks": checks,
            "error_type": type(exc).__name__,
            "cleanup_pending": cleanup_pending,
        }


def roundtrip_preflight_blockers(preflight: dict[str, Any]) -> list[str]:
    """Return every configuration failure for the approved original-object bucket.

    The two-bucket design puts version history in the separate recovery archive;
    the original-object bucket itself must be confirmed never-versioned.
    """
    failed = preflight.get("failed_checks", [])
    if not isinstance(failed, list):
        return ["invalid_preflight_result"]
    return sorted({item for item in failed if isinstance(item, str)})


def build_acceptance_report() -> dict[str, Any]:
    """Create a sanitized report bound to the exact configured S3/KMS target."""
    return {
        "production_approval": False,
        "storage_config_sha256": original_storage_config_fingerprint(),
        "manual_review_required": [
            "independent review of bucket policy and IAM/KMS grants",
            "witnessed backup/restore and rollback rehearsal",
            "retention/export/deletion policy approval",
            "independent security review",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a synthetic S3/KMS round trip; never treats this as production approval."
    )
    parser.add_argument("--firm-id", type=int, required=True,
                        help="ID of an empty SYNTHETIC-ACCEPTANCE-* firm")
    parser.add_argument("--confirm-synthetic-firm", action="store_true",
                        help="Confirm this firm is dedicated to non-client acceptance data")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    environment = os.environ.get("COPILOT_ENV", "").strip().lower()
    backend = os.environ.get("COPILOT_OBJECT_STORAGE_BACKEND", "").strip().lower()
    bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
    region = os.environ.get("COPILOT_S3_REGION", "").strip()
    key_id = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
    endpoint = os.environ.get("COPILOT_S3_ENDPOINT_URL", "").strip() or None
    if not args.confirm_synthetic_firm:
        parser.error("pass --confirm-synthetic-firm only for a dedicated non-client acceptance firm")
    if environment not in {"staging", "production"}:
        parser.error("COPILOT_ENV must be staging or production for live storage acceptance")
    if backend != "s3":
        parser.error("COPILOT_OBJECT_STORAGE_BACKEND must be s3")
    if not bucket or not region or not key_id:
        parser.error("COPILOT_S3_BUCKET, COPILOT_S3_REGION, and COPILOT_S3_KMS_KEY_ID are required")
    if os.environ.get("COPILOT_DB", "").strip():
        parser.error("COPILOT_DB must be unset; configure the three separate database paths")

    runtime = None
    report = build_acceptance_report()
    try:
        import boto3
        runtime = DatabaseRuntime.from_env()
        runtime.initialize()
        report["synthetic_firm"] = verify_synthetic_firm(runtime, args.firm_id)

        s3_client = boto3.client("s3", region_name=region, endpoint_url=endpoint)
        kms_client = boto3.client("kms", region_name=region)
        preflight = validate_s3_configuration(
            s3_client, kms_client, bucket=bucket, configured_key=key_id
        )
        report["configuration_preflight"] = preflight
        blocking_checks = roundtrip_preflight_blockers(preflight)
        report["configuration_preflight"]["roundtrip_blocking_checks"] = blocking_checks
        purge_check = next(
            (item for item in preflight["checks"]
             if item.get("name") == "physical_purge_versioning_compatibility"),
            {"passed": False},
        )
        report["physical_purge_compatibility"] = bool(purge_check.get("passed"))
        if blocking_checks:
            report["live_roundtrip"] = {"passed": False, "skipped": True,
                                        "reason": "S3/KMS configuration preflight failed",
                                        "blocking_checks": blocking_checks}
            if args.json:
                print(json.dumps(report, sort_keys=True))
            else:
                print("S3/KMS acceptance blocked: configuration preflight failed.")
            return 1

        store = S3PrivateObjectStore(
            s3_client, bucket=bucket, kms_key_id=key_id, kms_client=kms_client
        )
        roundtrip = run_s3_roundtrip(store, args.firm_id)
        roundtrip["version_history_may_remain"] = preflight.get("bucket_versioning_status") == "Enabled"
        report["live_roundtrip"] = roundtrip
        if args.json:
            print(json.dumps(report, sort_keys=True))
        else:
            print(f"S3/KMS live acceptance for synthetic firm {args.firm_id}")
            for check in preflight["checks"]:
                print(f"- {'PASS' if check['passed'] else 'FAIL'} {check['name']}")
            for check in roundtrip["checks"]:
                print(f"- {'PASS' if check['passed'] else 'FAIL'} {check['name']}")
            print(f"Physical purge compatible: {'YES' if report.get('physical_purge_compatibility') else 'NO'}")
            if report["live_roundtrip"].get("version_history_may_remain"):
                print("Synthetic probe versions may remain in version history; do not claim permanent erasure.")
            print("Production approval: NO; independent review and witnessed drills remain mandatory.")
            if roundtrip.get("cleanup_pending"):
                print(f"MANUAL REVIEW REQUIRED for probe object {roundtrip.get('object_id')}")
        return 0 if roundtrip["passed"] else 1
    except Exception as exc:
        report["error_type"] = type(exc).__name__
        if args.json:
            print(json.dumps(report, sort_keys=True))
        else:
            print("S3/KMS acceptance could not safely complete; inspect the sanitized JSON report.")
        return 2
    finally:
        if runtime is not None:
            try:
                runtime.close_current_thread()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
