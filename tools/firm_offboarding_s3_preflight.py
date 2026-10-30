#!/usr/bin/env python3
"""Read-only S3-aware firm offboarding preflight; never deletes objects."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict

from database_runtime import DatabaseRuntime
from s3_original_file_storage import S3PrivateObjectStore
from tools.firm_offboarding_preflight import inspect_firm_offboarding


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only S3 offboarding preflight. This command never purges objects."
    )
    parser.add_argument("--firm-id", type=int, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if os.environ.get("COPILOT_OBJECT_STORAGE_BACKEND", "").strip().lower() != "s3":
        parser.error("set COPILOT_OBJECT_STORAGE_BACKEND=s3")
    bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
    region = os.environ.get("COPILOT_S3_REGION", "").strip()
    kms_key_id = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
    endpoint = os.environ.get("COPILOT_S3_ENDPOINT_URL", "").strip() or None
    if not bucket or not region or not kms_key_id:
        parser.error("COPILOT_S3_BUCKET, COPILOT_S3_REGION, and COPILOT_S3_KMS_KEY_ID are required")

    runtime = None
    try:
        import boto3

        runtime = DatabaseRuntime.from_env()
        store = S3PrivateObjectStore(
            boto3.client("s3", region_name=region, endpoint_url=endpoint),
            bucket=bucket,
            kms_key_id=kms_key_id,
            kms_client=boto3.client("kms", region_name=region),
        )
        report = inspect_firm_offboarding(
            runtime.paths.control_plane,
            runtime.paths.tenant_root,
            runtime.paths.legal_corpus,
            None,
            args.firm_id,
            s3_store=store,
        )
    except ImportError:
        print("S3 offboarding preflight unavailable: AWS SDK is not installed", file=sys.stderr)
        return 2
    except Exception as exc:
        print(
            f"S3 offboarding preflight could not safely complete: {type(exc).__name__}",
            file=sys.stderr,
        )
        return 2
    finally:
        if runtime is not None:
            try:
                runtime.close_current_thread()
            except Exception:
                pass

    payload = {
        **report,
        "findings": report["findings"],
        "mutations_performed": 0,
        "production_purge_authorized": False,
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(
            f"Firm {args.firm_id} S3 offboarding preflight: "
            + ("CLEAR FOR POLICY REVIEW" if report["purge_preflight_clear"] else "BLOCKED")
            + f"; versioning={report['s3_bucket_versioning_status']}"
            + f"; objects={report['original_object_count']}"
        )
        for finding in report["findings"]:
            print(f"- {finding['code']}")
        print(report["warning"])
    return 0 if report["purge_preflight_clear"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
