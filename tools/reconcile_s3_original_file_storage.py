#!/usr/bin/env python3
"""Read-only S3 original-file reconciliation using the trusted tenant catalog."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import asdict
from pathlib import Path

from database_runtime import DatabaseRuntime
from original_file_reconciliation import TenantDatabase
from original_file_s3_reconciliation import reconcile_s3_original_file_storage
from s3_original_file_storage import S3PrivateObjectStore
from tenant_catalog import TenantCatalogError, resolve_tenant_database


def _read_only(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Configured control-plane database is missing or unsafe")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only compare of S3 original objects and tenant metadata."
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    if os.environ.get("COPILOT_OBJECT_STORAGE_BACKEND", "").strip().lower() != "s3":
        parser.error("set COPILOT_OBJECT_STORAGE_BACKEND=s3")
    bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
    region = os.environ.get("COPILOT_S3_REGION", "").strip()
    kms_key_id = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
    endpoint = os.environ.get("COPILOT_S3_ENDPOINT_URL", "").strip() or None
    if not bucket or not region or not kms_key_id:
        parser.error("COPILOT_S3_BUCKET, COPILOT_S3_REGION, and COPILOT_S3_KMS_KEY_ID are required")

    try:
        import boto3
        store = S3PrivateObjectStore(
            boto3.client("s3", region_name=region, endpoint_url=endpoint),
            bucket=bucket, kms_key_id=kms_key_id,
            kms_client=boto3.client("kms", region_name=region),
        )
        runtime = DatabaseRuntime.from_env()
        control = _read_only(runtime.paths.control_plane)
        try:
            active_firms = {
                int(row["id"]) for row in control.execute(
                    "SELECT id FROM firms WHERE status='active' ORDER BY id"
                )
            }
            provisioned = {
                int(row["firm_id"]) for row in control.execute(
                    "SELECT firm_id FROM tenant_database_catalog WHERE status='provisioned'"
                )
            }
            missing = sorted(active_firms - provisioned)
            if missing:
                raise RuntimeError("Active firms lack provisioned tenant catalog entries")
            tenants = [
                TenantDatabase(
                    firm_id=firm_id,
                    path=resolve_tenant_database(control, firm_id, runtime.paths.tenant_root),
                )
                for firm_id in sorted(provisioned)
            ]
        finally:
            control.close()
        report = reconcile_s3_original_file_storage(store, tenants)
    except ImportError:
        print("S3 reconciliation unavailable: AWS SDK is not installed", file=sys.stderr)
        return 2
    except (RuntimeError, ValueError, sqlite3.Error, TenantCatalogError) as exc:
        print(f"S3 reconciliation could not safely complete: {exc}", file=sys.stderr)
        return 2

    payload = {
        "clean": report.clean,
        "checked_databases": report.checked_databases,
        "checked_metadata_rows": report.checked_metadata_rows,
        "checked_objects": report.checked_objects,
        "findings": [asdict(finding) for finding in report.findings],
        "mutations_performed": 0,
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(
            "S3 original-file reconciliation: "
            + ("CLEAN" if report.clean else "FINDINGS")
            + f"; databases={report.checked_databases}"
            + f"; metadata_rows={report.checked_metadata_rows}"
            + f"; objects={report.checked_objects}"
        )
        for finding in report.findings:
            firm = f"firm={finding.firm_id}" if finding.firm_id is not None else "firm=unknown"
            object_id = f" object={finding.object_id}" if finding.object_id else ""
            print(f"- {finding.code} {firm}{object_id}: {finding.detail}")
    return 0 if report.clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
