#!/usr/bin/env python3
"""Import verified backup originals into a target S3 bucket after isolated restore.

Dry-run is the default. --apply mutates only the supplied restore directory and the
configured S3 bucket; it refuses paths that overlap the currently configured live DBs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

from database_runtime import DatabaseRuntime
from original_file_storage import ObjectStorageError
from s3_original_file_storage import S3PrivateObjectStore
from tenant_catalog import TenantCatalogError, resolve_tenant_database


def _readonly(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Restore database is missing or unsafe")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def _digest(path: Path) -> tuple[str, int]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Restored original is missing or unsafe")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run or import verified restored original files into the configured S3/KMS backend."
    )
    parser.add_argument("--restore-root", required=True, help="Isolated directory produced by restore-tenancy.")
    parser.add_argument("--apply", action="store_true", help="Upload originals and update only restored tenant DB metadata.")
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
        root_raw = Path(args.restore_root).expanduser().absolute()
        if root_raw.is_symlink() or not root_raw.is_dir():
            raise RuntimeError("Restore root must be an existing non-symlink directory")
        root = root_raw.resolve()
        runtime = DatabaseRuntime.from_env()
        live_paths = [
            runtime.paths.control_plane.resolve(),
            runtime.paths.legal_corpus.resolve(),
            runtime.paths.tenant_root.resolve(),
        ]
        for live in live_paths:
            if root == live or root in live.parents or live in root.parents:
                raise RuntimeError("Restore root overlaps a currently configured live database path")
        control_path = root / "control_plane.sqlite3"
        tenant_root = root / "tenants"
        object_root = root / "objects"
        if not tenant_root.is_dir() or tenant_root.is_symlink() or not object_root.is_dir() or object_root.is_symlink():
            raise RuntimeError("Restore root must contain safe tenants/ and objects/ directories")

        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("AWS SDK is not installed") from exc
        store = S3PrivateObjectStore(
            boto3.client("s3", region_name=region, endpoint_url=endpoint),
            bucket=bucket, kms_key_id=kms_key_id,
        )
        control = _readonly(control_path)
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
            if active_firms - provisioned:
                raise RuntimeError("Restore catalog has active firms without provisioned tenant databases")
            tenants = [
                (firm_id, resolve_tenant_database(control, firm_id, tenant_root))
                for firm_id in sorted(provisioned)
            ]
        finally:
            control.close()

        actions = []
        for firm_id, database_path in tenants:
            db = sqlite3.connect(database_path if args.apply else database_path.resolve().as_uri() + "?mode=ro",
                                 uri=not args.apply, timeout=30)
            db.row_factory = sqlite3.Row
            try:
                binding = db.execute(
                    "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
                ).fetchone()
                if binding is None or int(binding["firm_id"]) != firm_id:
                    raise RuntimeError("Restored tenant binding does not match the control-plane catalog")
                columns = {row[1] for row in db.execute("PRAGMA table_info(original_file_objects)")}
                if not {"object_id", "firm_id", "storage_backend", "sha256", "byte_size", "state"}.issubset(columns):
                    continue
                has_purged = "purged_at" in columns
                query = "SELECT object_id,firm_id,storage_backend,sha256,byte_size,state"
                query += ",purged_at" if has_purged else ""
                query += " FROM original_file_objects ORDER BY object_id"
                for row in db.execute(query).fetchall():
                    object_id = row["object_id"]
                    if int(row["firm_id"]) != firm_id:
                        raise RuntimeError("Restored original metadata crosses its tenant binding")
                    purged = has_purged and row["purged_at"] is not None
                    namespace = object_root / f"firm-{firm_id}"
                    source = namespace / f"{object_id}.blob"
                    if purged:
                        if namespace.is_symlink() or source.exists() or source.is_symlink():
                            raise RuntimeError("Purged original unexpectedly exists in restored object inventory")
                        continue
                    if namespace.is_symlink() or not namespace.is_dir():
                        raise RuntimeError("Restored firm object namespace is missing or unsafe")
                    if row["state"] not in {"ready", "quarantined"}:
                        raise RuntimeError("Restore contains unfinished original-object metadata")
                    digest, size = _digest(source)
                    if digest != row["sha256"] or size != int(row["byte_size"]):
                        raise RuntimeError("Restored original fails its recorded digest/size")
                    staged_exists, final_exists = store.object_presence(firm_id, object_id)
                    if final_exists:
                        if staged_exists or not store.verify(
                            firm_id, object_id, expected_sha256=digest, expected_size=size
                        ):
                            raise RuntimeError("Target S3 object conflicts with restored original metadata")
                        action = "already_verified"
                    elif staged_exists:
                        if not store.verify_staged(
                            firm_id, object_id, expected_sha256=digest, expected_size=size
                        ):
                            raise RuntimeError("Target S3 staged object conflicts with restored original metadata")
                        action = "staged_recovery_candidate"
                        if args.apply:
                            store.finalize(firm_id, object_id)
                            if not store.verify(firm_id, object_id, expected_sha256=digest, expected_size=size):
                                store.delete(firm_id, object_id)
                                raise RuntimeError("Recovered final S3 object failed integrity verification")
                            action = "imported"
                    else:
                        action = "would_import"
                        if args.apply:
                            store.stage_with_id(firm_id, object_id, source.read_bytes())
                            if not store.verify_staged(
                                firm_id, object_id, expected_sha256=digest, expected_size=size
                            ):
                                store.delete(firm_id, object_id)
                                raise RuntimeError("Uploaded staged object failed integrity verification")
                            store.finalize(firm_id, object_id)
                            if not store.verify(firm_id, object_id, expected_sha256=digest, expected_size=size):
                                store.delete(firm_id, object_id)
                                raise RuntimeError("Final S3 object failed integrity verification")
                            action = "imported"
                    if args.apply and row["storage_backend"] != "s3":
                        try:
                            db.execute("BEGIN IMMEDIATE")
                            updated = db.execute(
                                "UPDATE original_file_objects SET storage_backend='s3',updated_at=datetime('now') "
                                "WHERE object_id=? AND firm_id=? AND storage_backend=? AND state=?",
                                (object_id, firm_id, row["storage_backend"], row["state"]),
                            )
                            if updated.rowcount != 1:
                                db.rollback()
                                raise RuntimeError("Restored metadata changed during backend migration")
                            db.commit()
                        except Exception:
                            if db.in_transaction:
                                db.rollback()
                            if action == "imported":
                                try:
                                    store.delete(firm_id, object_id)
                                except ObjectStorageError:
                                    pass
                            raise
                    actions.append({"firm_id": firm_id, "object_id": object_id, "action": action})
            finally:
                db.close()

        print(json.dumps({
            "mode": "apply" if args.apply else "dry_run",
            "bucket": bucket,
            "objects_checked": len(actions),
            "actions": actions,
            "mutations_performed": sum(item["action"] == "imported" for item in actions),
        }, sort_keys=True))
    except (RuntimeError, ValueError, sqlite3.Error, TenantCatalogError, ObjectStorageError, OSError) as exc:
        print(f"S3 restore import could not safely complete: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
