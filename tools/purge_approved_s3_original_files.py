#!/usr/bin/env python3
"""Audited production S3 purge; fails closed without accepted deployment evidence."""
from __future__ import annotations

import argparse
import json
import os
import sys

from database_runtime import DatabaseRuntime
from s3_original_file_storage import S3PrivateObjectStore
from tenant_catalog import initialize_catalog, resolve_tenant_database_for_maintenance
from tools.database_release_acceptance import (
    REQUIRED_GATES,
    _read_acceptance_manifest_file,
    _timestamp,
    load_acceptance_manifest,
    original_storage_config_fingerprint,
)
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _staging_acceptance(path: str, fingerprint: str | None) -> tuple[bool, list[str]]:
    """Require live storage acceptance and approved retention policy for synthetic staging drills."""
    try:
        manifest = _read_acceptance_manifest_file(Path(path))
    except Exception as exc:
        return False, [type(exc).__name__]
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        return False, ["invalid_manifest"]
    gates = manifest.get("gates")
    if not isinstance(gates, dict):
        return False, ["gates_missing"]
    now = datetime.now(timezone.utc)
    blockers = []
    for name in ("original_file_storage", "retention_export_deletion_policy"):
        spec = REQUIRED_GATES[name]
        item = gates.get(name)
        if not isinstance(item, dict) or item.get("status") != "passed":
            blockers.append(name + ":not_passed")
            continue
        if not isinstance(item.get("evidence_ref"), str) or not item["evidence_ref"].strip():
            blockers.append(name + ":evidence_missing")
            continue
        actor_field = "verified_by" if name == "original_file_storage" else "approved_by"
        time_field = "verified_at" if name == "original_file_storage" else "approved_at"
        if not isinstance(item.get(actor_field), str) or not item[actor_field].strip():
            blockers.append(name + ":actor_missing")
            continue
        timestamp = _timestamp(item.get(time_field))
        if timestamp is None or timestamp > now + timedelta(minutes=5):
            blockers.append(name + ":timestamp_invalid")
            continue
        if now - timestamp > timedelta(days=spec["max_age_days"]):
            blockers.append(name + ":evidence_expired")
            continue
        if name == "original_file_storage" and (
            not fingerprint or item.get("storage_config_sha256") != fingerprint
        ):
            blockers.append(name + ":storage_target_mismatch")
    return not blockers, blockers
from tools.firm_offboarding_preflight import inspect_firm_offboarding
from tools.purge_approved_original_files import (
    _read_only,
    purge_approved_requests,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute approved original-file purge against the accepted production S3 target."
    )
    parser.add_argument("--firm-id", type=int, required=True)
    parser.add_argument("--operator-user-id", type=int, required=True)
    parser.add_argument("--apply", action="store_true", help="Perform approved physical purges.")
    parser.add_argument("--staging-drill", action="store_true", help="Allow only a synthetic-firm staging deletion-recovery rehearsal.")
    parser.add_argument("--quiesced", action="store_true", help="Assert all firm writers are paused.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.apply and not args.quiesced:
        parser.error("--apply requires --quiesced")
    if args.quiesced and not args.apply:
        parser.error("--quiesced is only meaningful with --apply")
    environment = os.environ.get("COPILOT_ENV", "").strip().lower()
    if os.environ.get("COPILOT_OBJECT_STORAGE_BACKEND", "").strip().lower() != "s3":
        parser.error("COPILOT_OBJECT_STORAGE_BACKEND must be s3")

    manifest_path = os.environ.get("COPILOT_DATABASE_ACCEPTANCE_FILE", "").strip()
    fingerprint = original_storage_config_fingerprint()
    staging_drill = args.staging_drill
    if staging_drill:
        if environment != "staging":
            parser.error("--staging-drill is restricted to COPILOT_ENV=staging")
        if (
            os.environ.get("COPILOT_S3_PURGE_STAGING_BUCKET", "").strip()
            != os.environ.get("COPILOT_S3_BUCKET", "").strip()
            or os.environ.get("COPILOT_S3_PURGE_STAGING_FIRM_ID", "").strip()
            != str(args.firm_id)
        ):
            parser.error("staging bucket and firm must match the explicit purge allowlist")
        ready, blockers = _staging_acceptance(manifest_path, fingerprint)
        if not ready:
            print(json.dumps({
                "decision": "blocked",
                "reason": "staging_storage_or_retention_acceptance_incomplete",
                "blockers": blockers,
                "mutations_performed": 0,
            }, sort_keys=True))
            return 2
        acceptance = {"passed_count": 2, "required_count": 2}
    else:
        if environment not in {"prod", "production"}:
            parser.error("production purge requires COPILOT_ENV=production; use --staging-drill for synthetic staging")
        acceptance = load_acceptance_manifest(
            manifest_path or None,
            expected_storage_config_sha256=fingerprint or "",
        )
        if not acceptance.get("ready"):
            print(json.dumps({
                "decision": "blocked",
                "reason": "database_release_acceptance_incomplete",
                "blockers": acceptance.get("blockers", []),
                "mutations_performed": 0,
            }, sort_keys=True))
            return 2

    runtime = None
    try:
        import boto3

        bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
        region = os.environ.get("COPILOT_S3_REGION", "").strip()
        kms_key_id = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
        endpoint = os.environ.get("COPILOT_S3_ENDPOINT_URL", "").strip() or None
        if not bucket or not region or not kms_key_id or not fingerprint:
            raise RuntimeError("accepted S3 target configuration is incomplete")

        runtime = DatabaseRuntime.from_env()
        store = S3PrivateObjectStore(
            boto3.client("s3", region_name=region, endpoint_url=endpoint),
            bucket=bucket,
            kms_key_id=kms_key_id,
            kms_client=boto3.client("kms", region_name=region),
        )
        control = _read_only(runtime.paths.control_plane)
        try:
            initialize_catalog(control)
            if staging_drill:
                firm_row = control.execute("SELECT name FROM firms WHERE id=?", (args.firm_id,)).fetchone()
                if firm_row is None or not str(firm_row["name"]).startswith("SYNTHETIC-ACCEPTANCE-"):
                    raise RuntimeError("staging purge is restricted to SYNTHETIC-ACCEPTANCE- firms")
            database_path = resolve_tenant_database_for_maintenance(
                control, args.firm_id, runtime.paths.tenant_root
            )
        finally:
            control.close()

        preflight = inspect_firm_offboarding(
            runtime.paths.control_plane,
            runtime.paths.tenant_root,
            runtime.paths.legal_corpus,
            None,
            args.firm_id,
            s3_store=store,
        )
        if not preflight["purge_preflight_clear"]:
            report = {
                "decision": "blocked",
                "reason": "s3_offboarding_preflight_failed",
                "preflight": preflight,
                "purged_count": 0,
                "mutations_performed": 0,
            }
            print(json.dumps(report, sort_keys=True))
            return 1

        result = purge_approved_requests(
            database_path,
            None,
            args.firm_id,
            args.operator_user_id,
            apply=args.apply,
            control_database_path=runtime.paths.control_plane,
            tenant_root=runtime.paths.tenant_root,
            corpus_database_path=runtime.paths.legal_corpus,
            object_store=store,
            quiesced=args.quiesced,
        )
        report = {
            "decision": "completed" if args.apply else "dry_run",
            "execution_scope": "synthetic_staging_drill" if staging_drill else "production",
            "apply": args.apply,
            "quiescence_asserted": args.quiesced,
            "acceptance_gates_passed": acceptance["passed_count"],
            "acceptance_gates_required": acceptance["required_count"],
            "storage_config_sha256": fingerprint,
            "preflight": preflight,
            **result,
            "mutations_performed": result["purged_count"],
        }
    except ImportError:
        print("production S3 purge unavailable: AWS SDK is not installed", file=sys.stderr)
        return 2
    except Exception as exc:
        print(
            f"production S3 purge could not safely complete: {type(exc).__name__}",
            file=sys.stderr,
        )
        return 2
    finally:
        if runtime is not None:
            try:
                runtime.close_current_thread()
            except Exception:
                pass

    print(json.dumps(report, sort_keys=True))
    if any(item["status"] == "manual_review_required" for item in report["results"]):
        return 1
    if any(item["status"] == "recoverable_candidate" for item in report["results"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
