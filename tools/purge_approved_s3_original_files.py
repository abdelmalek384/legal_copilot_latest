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
    load_acceptance_manifest,
    load_staging_purge_acceptance_manifest,
    original_storage_config_fingerprint,
)
from tools.firm_offboarding_preflight import inspect_firm_offboarding
from tools.purge_approved_original_files import (
    _read_only,
    purge_approved_requests,
)


def _staging_acceptance(path: str, fingerprint: str | None) -> tuple[bool, list[str]]:
    report = load_staging_purge_acceptance_manifest(
        path or None,
        expected_storage_config_sha256=fingerprint,
    )
    blockers = [
        f"{item.get('gate', 'manifest')}:{item.get('code', 'blocked')}"
        for item in report.get("blockers", [])
    ]
    return bool(report.get("ready")), blockers


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
        acceptance = {"passed_count": 3, "required_count": 3}
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
            staging_drill=staging_drill,
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
