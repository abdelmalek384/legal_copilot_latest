#!/usr/bin/env python3
"""Recover only verifiable staged original files after an interrupted upload."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

from database_runtime import DatabaseRuntime
from original_file_storage import LocalPrivateObjectStore, ObjectStorageError
from s3_original_file_storage import S3PrivateObjectStore
from tenant_catalog import TenantCatalogError, resolve_tenant_database


def _connect_control(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Control-plane database is missing or unsafe")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def _process_tenant(database_path: Path, firm_id: int, store: LocalPrivateObjectStore, apply: bool):
    findings = []
    recovered = 0
    if database_path.is_symlink() or not database_path.is_file():
        raise RuntimeError(f"Tenant database for firm {firm_id} is missing or unsafe")
    if apply:
        connection = sqlite3.connect(database_path, timeout=30)
    else:
        connection = sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        if not apply:
            connection.execute("PRAGMA query_only=ON")
        binding = connection.execute(
            "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
        ).fetchone()
        if binding is None or int(binding["firm_id"]) != firm_id:
            raise RuntimeError(f"Tenant database binding mismatch for firm {firm_id}")
        rows = connection.execute(
            "SELECT object_id,firm_id,sha256,byte_size,state FROM original_file_objects "
            "WHERE state='staged' ORDER BY object_id"
        ).fetchall()
        for row in rows:
            object_id = row["object_id"]
            if int(row["firm_id"]) != firm_id:
                findings.append({
                    "firm_id": firm_id, "object_id": object_id,
                    "status": "manual_review_required",
                    "detail": "metadata firm ID does not match the trusted tenant catalog",
                })
                continue
            if apply:
                connection.execute("BEGIN IMMEDIATE")
                current = connection.execute(
                    "SELECT sha256,byte_size,state FROM original_file_objects "
                    "WHERE object_id=? AND firm_id=?",
                    (object_id, firm_id),
                ).fetchone()
                if current is None or current["state"] != "staged":
                    connection.rollback()
                    findings.append({
                        "firm_id": firm_id, "object_id": object_id,
                        "status": "skipped_concurrent_change",
                        "detail": "metadata changed before recovery; rerun reconciliation",
                    })
                    continue
                digest, size = current["sha256"], int(current["byte_size"])
            else:
                digest, size = row["sha256"], int(row["byte_size"])

            try:
                staged_exists, final_exists = store.object_presence(firm_id, object_id)
                staged_ok = staged_exists and store.verify_staged(
                    firm_id, object_id, expected_sha256=digest, expected_size=size
                )
                final_ok = final_exists and store.verify(
                    firm_id, object_id, expected_sha256=digest, expected_size=size
                )
            except (ObjectStorageError, ValueError) as exc:
                if apply:
                    connection.rollback()
                findings.append({
                    "firm_id": firm_id, "object_id": object_id,
                    "status": "manual_review_required",
                    "detail": str(exc),
                })
                continue

            action = None
            if staged_exists and final_exists:
                detail = "both staged and finalized files exist; preserving both for manual review"
            elif not staged_exists and not final_exists:
                detail = "metadata has no staged or finalized bytes"
            elif staged_exists and not staged_ok:
                detail = "staged bytes fail SHA-256 or size verification"
            elif final_exists and not final_ok:
                detail = "finalized bytes fail SHA-256 or size verification"
            elif staged_ok:
                action = "finalize_staged_object"
                detail = "staged bytes match tenant metadata"
            elif final_ok:
                action = "mark_verified_final_object_ready"
                detail = "finalized bytes match tenant metadata"
            else:
                detail = "object state is ambiguous; manual review is required"

            if action is None:
                if apply:
                    connection.rollback()
                findings.append({
                    "firm_id": firm_id, "object_id": object_id,
                    "status": "manual_review_required", "detail": detail,
                })
                continue

            if not apply:
                findings.append({
                    "firm_id": firm_id, "object_id": object_id,
                    "status": "recoverable_candidate", "action": action, "detail": detail,
                })
                continue

            try:
                if action == "finalize_staged_object":
                    store.finalize(firm_id, object_id)
                updated = connection.execute(
                    "UPDATE original_file_objects SET state='ready',updated_at=datetime('now') "
                    "WHERE object_id=? AND firm_id=? AND state='staged'",
                    (object_id, firm_id),
                )
                if updated.rowcount != 1:
                    raise RuntimeError("metadata state changed during recovery")
                connection.commit()
                recovered += 1
                findings.append({
                    "firm_id": firm_id, "object_id": object_id,
                    "status": "recovered", "action": action, "detail": detail,
                })
            except Exception:
                connection.rollback()
                # If finalization succeeded but commit failed, the next run can
                # safely recognize and verify the finalized blob.
                raise
    finally:
        connection.close()
    return recovered, findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recover only verified staged original-file uploads; no orphan deletion."
    )
    parser.add_argument("--object-root", default=os.environ.get("COPILOT_OBJECT_STORAGE_ROOT", "").strip())
    parser.add_argument("--apply", action="store_true", help="Perform safe state recovery.")
    parser.add_argument(
        "--quiesced", action="store_true",
        help="Assert that all application writes to tenant DBs and object storage are paused.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    if args.apply and not args.quiesced:
        parser.error("--apply requires --quiesced")
    if args.quiesced and not args.apply:
        parser.error("--quiesced is only meaningful with --apply")

    backend = os.environ.get("COPILOT_OBJECT_STORAGE_BACKEND", "local").strip().lower()
    production = os.environ.get("COPILOT_ENV", "").strip().lower() in {"prod", "production"}
    if backend == "local":
        if production:
            parser.error("local filesystem recovery is disabled in production mode")
        if not args.object_root:
            parser.error("set COPILOT_OBJECT_STORAGE_ROOT or pass --object-root")
    elif backend == "s3":
        if args.object_root:
            parser.error("--object-root is only valid for the local backend")
    else:
        parser.error("COPILOT_OBJECT_STORAGE_BACKEND must be local or s3")

    try:
        runtime = DatabaseRuntime.from_env()
        if backend == "local":
            raw_root = Path(args.object_root).expanduser()
            if raw_root.is_symlink() or not raw_root.is_dir():
                raise RuntimeError("Object storage root must be an existing non-symlink directory")
            object_root = raw_root.resolve()
            tenant_root = runtime.paths.tenant_root.resolve()
            control_path = runtime.paths.control_plane.resolve()
            corpus_path = runtime.paths.legal_corpus.resolve()
            if (
                object_root == tenant_root
                or object_root in tenant_root.parents
                or tenant_root in object_root.parents
            ):
                raise RuntimeError("Object storage must be separate from the tenant database root")
            for label, database_path in (("control-plane", control_path), ("legal-corpus", corpus_path)):
                if object_root == database_path or object_root in database_path.parents:
                    raise RuntimeError(f"Object storage must not contain the {label} database")
            store = LocalPrivateObjectStore(object_root)
        else:
            bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
            region = os.environ.get("COPILOT_S3_REGION", "").strip()
            kms_key_id = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
            endpoint = os.environ.get("COPILOT_S3_ENDPOINT_URL", "").strip() or None
            if not bucket or not region or not kms_key_id:
                raise RuntimeError("S3 bucket, region, and KMS key ID must be configured")
            try:
                import boto3
            except ImportError as exc:
                raise RuntimeError("AWS SDK is not installed") from exc
            store = S3PrivateObjectStore(
                boto3.client("s3", region_name=region, endpoint_url=endpoint),
                bucket=bucket, kms_key_id=kms_key_id,
            )
            control_path = runtime.paths.control_plane

        control = _connect_control(control_path)
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
                raise RuntimeError(
                    "Active firms lack provisioned tenant catalog entries: "
                    + ", ".join(str(firm_id) for firm_id in missing)
                )
            tenant_paths = [
                (firm_id, resolve_tenant_database(control, firm_id, runtime.paths.tenant_root))
                for firm_id in sorted(provisioned)
            ]
        finally:
            control.close()

        findings = []
        recovered = 0
        for firm_id, database_path in tenant_paths:
            count, tenant_findings = _process_tenant(database_path, firm_id, store, args.apply)
            recovered += count
            findings.extend(tenant_findings)
    except (RuntimeError, ValueError, sqlite3.Error, TenantCatalogError, ObjectStorageError) as exc:
        print(f"staged-object recovery could not safely complete: {exc}", file=sys.stderr)
        return 2

    unresolved = any(
        item["status"] in {"manual_review_required", "skipped_concurrent_change"}
        for item in findings
    )
    candidates = any(item["status"] == "recoverable_candidate" for item in findings)
    payload = {
        "backend": backend,
        "apply": args.apply,
        "quiescence_asserted": args.quiesced,
        "recovered_count": recovered,
        "findings": findings,
        "mutations_performed": recovered,
        "manual_review_required": unresolved,
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(
            f"Staged original-file recovery ({backend}): "
            + ("MANUAL REVIEW REQUIRED" if unresolved else "RECOVERY CANDIDATES" if candidates else "COMPLETE")
            + f"; recovered={recovered}; findings={len(findings)}"
        )
        for item in findings:
            print(
                f"- {item['status']} firm={item['firm_id']} object={item['object_id']}: "
                f"{item['detail']}"
            )
    if unresolved:
        return 1
    if candidates and not args.apply:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
