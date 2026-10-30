#!/usr/bin/env python3
"""Purge approved originals only after a disabled-firm, quiesced, integrity-clean gate."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

from original_file_storage import LocalPrivateObjectStore, ObjectStorageError
from s3_original_file_storage import S3PrivateObjectStore
from tenant_catalog import (
    TenantCatalogError,
    initialize_catalog,
    resolve_tenant_database_for_maintenance,
)
from tools.firm_offboarding_preflight import inspect_firm_offboarding


def _read_only(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Control-plane database is missing or unsafe")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def _eligible_operator(control: sqlite3.Connection, operator_user_id: int) -> bool:
    row = control.execute(
        "SELECT u.status FROM users u JOIN user_platform_roles p ON p.user_id=u.id "
        "WHERE u.id=? AND p.role_name='platform_admin'",
        (operator_user_id,),
    ).fetchone()
    return row is not None and row["status"] == "active"


def _inspect_request(connection, store, firm_id: int, request_id: int):
    row = connection.execute(
        "SELECT r.id,r.object_id,r.document_id,r.firm_id,r.requested_by_user_id,"
        "r.request_reason,r.status,r.approved_by_user_id,r.approval_reason,"
        "o.sha256,o.byte_size,o.state,o.legal_hold,o.purged_at "
        "FROM original_file_deletion_requests r "
        "JOIN original_file_objects o ON o.object_id=r.object_id AND o.firm_id=r.firm_id "
        "WHERE r.id=? AND r.firm_id=?",
        (request_id, firm_id),
    ).fetchone()
    if row is None:
        return None, "deletion request or original metadata is missing"
    if row["status"] != "approved":
        return None, f"request status is {row['status']}, not approved"
    if row["legal_hold"] or row["purged_at"] is not None or row["state"] != "ready":
        return None, "original is held, already purged, or not ready"
    if row["approved_by_user_id"] is None or int(row["approved_by_user_id"]) == int(row["requested_by_user_id"]):
        return None, "request does not have a distinct second-admin approval"
    try:
        staged_exists, final_exists = store.object_presence(firm_id, row["object_id"])
        if staged_exists or not final_exists:
            return None, "original must have exactly one finalized object and no staged copy"
        if not store.verify(
            firm_id, row["object_id"],
            expected_sha256=row["sha256"], expected_size=int(row["byte_size"]),
        ):
            return None, "original bytes fail SHA-256 or size verification"
    except (ObjectStorageError, ValueError):
        return None, "original object path is unsafe or unavailable"
    return row, None


def purge_approved_requests(
    database_path: str | Path,
    object_root: str | Path,
    firm_id: int,
    operator_user_id: int,
    *,
    apply: bool,
    control_database_path: str | Path,
    tenant_root: str | Path,
    corpus_database_path: str | Path,
    object_store=None,
    quiesced: bool = False,
) -> dict:
    """Purge approved requests only after revalidating the trusted offboarding gate.

    Filesystem deletion cannot be rolled back. If the process stops after unlink but
    before SQLite commit, the request remains approved and the missing object requires
    manual review; this function never infers that an absent file was safely purged.
    The authority checks live here as well as in the CLI so an internal caller cannot
    bypass disabled-firm, active-platform-admin, or clean-preflight requirements.
    """
    backend = os.environ.get("COPILOT_OBJECT_STORAGE_BACKEND", "local").strip().lower()
    if object_store is None and os.environ.get("COPILOT_ENV", "").strip().lower() in {"prod", "production"}:
        raise RuntimeError("local filesystem purge is disabled in production mode")
    if object_store is None and backend != "local":
        raise RuntimeError("local purge requires the local development storage backend")
    if object_store is not None and (backend != "s3" or not isinstance(object_store, S3PrivateObjectStore)):
        raise RuntimeError("injected production purge store must be the configured S3 adapter")
    if object_store is not None and apply and quiesced is not True:
        raise RuntimeError("S3 physical purge requires an explicit quiescence assertion")
    if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
        raise ValueError("firm_id must be a positive integer")
    if (isinstance(operator_user_id, bool) or not isinstance(operator_user_id, int)
            or operator_user_id <= 0):
        raise ValueError("operator_user_id must be a positive integer")
    database_path = Path(database_path)
    control_path = Path(control_database_path)
    tenant_root_path = Path(tenant_root)
    corpus_path = Path(corpus_database_path)

    control = _read_only(control_path)
    try:
        initialize_catalog(control)
        if not _eligible_operator(control, operator_user_id):
            raise RuntimeError("Purge operator must be an active platform administrator")
        firm = control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()
        catalog = control.execute(
            "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
        ).fetchone()
        if firm is None or firm["status"] != "disabled":
            raise RuntimeError("Firm must be disabled before original-file purge")
        if catalog is None or catalog["status"] != "disabled":
            raise RuntimeError("Tenant catalog entry must be disabled before original-file purge")
        active_memberships = int(control.execute(
            "SELECT COUNT(*) FROM firm_memberships fm JOIN users u ON u.id=fm.user_id "
            "WHERE fm.firm_id=? AND fm.status='active' AND u.status='active'",
            (firm_id,),
        ).fetchone()[0])
        if active_memberships:
            raise RuntimeError("Active firm memberships must be revoked before original-file purge")
        trusted_database_path = resolve_tenant_database_for_maintenance(
            control, firm_id, tenant_root_path
        )
    finally:
        control.close()

    if database_path.resolve() != trusted_database_path.resolve():
        raise RuntimeError("Supplied tenant database does not match the trusted catalog")
    database_path = trusted_database_path
    preflight = inspect_firm_offboarding(
        control_path, tenant_root_path, corpus_path,
        None if object_store is not None else object_root, firm_id,
        s3_store=object_store,
    )
    if not preflight["purge_preflight_clear"]:
        raise RuntimeError("Original-file purge is blocked by offboarding preflight findings")

    store = object_store or LocalPrivateObjectStore(object_root)
    connection = sqlite3.connect(database_path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    results = []
    purged = 0
    try:
        binding = connection.execute(
            "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
        ).fetchone()
        if binding is None or int(binding["firm_id"]) != firm_id:
            raise RuntimeError("Tenant database binding mismatch")
        requests = connection.execute(
            "SELECT id FROM original_file_deletion_requests "
            "WHERE firm_id=? AND status IN ('approved','purging') ORDER BY id",
            (firm_id,),
        ).fetchall()
        for request in requests:
            request_id = int(request["id"])
            if not apply:
                row, error = _inspect_request(connection, store, firm_id, request_id)
                if error:
                    results.append({"request_id": request_id, "status": "manual_review_required", "detail": error})
                elif operator_user_id in {
                    int(row["requested_by_user_id"]), int(row["approved_by_user_id"])
                }:
                    results.append({
                        "request_id": request_id, "status": "manual_review_required",
                        "detail": "purge operator must be distinct from requester and approver",
                    })
                else:
                    results.append({
                        "request_id": request_id,
                        "status": "recoverable_candidate",
                        "object_id": row["object_id"],
                    })
                continue

            connection.execute("BEGIN IMMEDIATE")
            row, error = _inspect_request(connection, store, firm_id, request_id)
            if error:
                connection.rollback()
                results.append({"request_id": request_id, "status": "manual_review_required", "detail": error})
                continue
            if operator_user_id in {
                int(row["requested_by_user_id"]), int(row["approved_by_user_id"])
            }:
                connection.rollback()
                results.append({
                    "request_id": request_id, "status": "manual_review_required",
                    "detail": "purge operator must be distinct from requester and approver",
                })
                continue
            try:
                started = connection.execute(
                    "UPDATE original_file_deletion_requests SET status='purging',"
                    "purge_started_by_user_id=?,purge_started_at=datetime('now') "
                    "WHERE id=? AND firm_id=? AND status='approved'",
                    (operator_user_id, request_id, firm_id),
                )
                if started.rowcount != 1:
                    raise RuntimeError("deletion request changed during purge")
                if isinstance(store, S3PrivateObjectStore):
                    removed = store.purge_unversioned(
                        firm_id, row["object_id"],
                        expected_sha256=row["sha256"], expected_size=int(row["byte_size"]),
                    )
                else:
                    removed = store.delete(firm_id, row["object_id"])
                if not removed:
                    raise RuntimeError("original object disappeared during purge")
                reason = (
                    str(row["request_reason"]).strip()
                    + " | approved: "
                    + str(row["approval_reason"]).strip()
                )
                updated = connection.execute(
                    "UPDATE original_file_objects SET purged_at=datetime('now'),"
                    "purged_by_user_id=?,purge_reason=?,updated_at=datetime('now') "
                    "WHERE object_id=? AND firm_id=? AND legal_hold=0 AND purged_at IS NULL",
                    (operator_user_id, reason, row["object_id"], firm_id),
                )
                if updated.rowcount != 1:
                    raise RuntimeError("original metadata changed during purge")
                completed = connection.execute(
                    "UPDATE original_file_deletion_requests SET status='completed',"
                    "completed_by_user_id=?,completed_at=datetime('now') "
                    "WHERE id=? AND firm_id=? AND status='purging'",
                    (operator_user_id, request_id, firm_id),
                )
                if completed.rowcount != 1:
                    raise RuntimeError("deletion request could not be completed")
                connection.commit()
                purged += 1
                results.append({"request_id": request_id, "status": "purged", "object_id": row["object_id"]})
            except Exception:
                connection.rollback()
                # Never infer success if a file was unlinked but the DB commit failed.
                results.append({
                    "request_id": request_id,
                    "status": "manual_review_required",
                    "detail": "purge interrupted or database commit failed; reconcile before retrying",
                })
    finally:
        connection.close()
    return {"purged_count": purged, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Purge two-admin-approved original files for a disabled firm; no automatic cleanup."
    )
    parser.add_argument("--firm-id", type=int, required=True)
    parser.add_argument("--operator-user-id", type=int, required=True)
    parser.add_argument("--apply", action="store_true", help="Perform approved purges.")
    parser.add_argument("--quiesced", action="store_true", help="Assert firm writes are paused.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    if args.apply and not args.quiesced:
        parser.error("--apply requires --quiesced")
    if args.quiesced and not args.apply:
        parser.error("--quiesced is only meaningful with --apply")
    if os.environ.get("COPILOT_ENV", "").strip().lower() in {"prod", "production"}:
        parser.error("local filesystem purge is disabled in production mode")
    if os.environ.get("COPILOT_OBJECT_STORAGE_BACKEND", "local").strip().lower() != "local":
        parser.error("this command supports only the local development storage backend")
    required = {
        "COPILOT_CONTROL_DB": os.environ.get("COPILOT_CONTROL_DB", "").strip(),
        "COPILOT_TENANT_DB_ROOT": os.environ.get("COPILOT_TENANT_DB_ROOT", "").strip(),
        "COPILOT_CORPUS_DB": os.environ.get("COPILOT_CORPUS_DB", "").strip(),
        "COPILOT_OBJECT_STORAGE_ROOT": os.environ.get("COPILOT_OBJECT_STORAGE_ROOT", "").strip(),
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        parser.error("missing required environment variables: " + ", ".join(missing))

    try:
        control = _read_only(Path(required["COPILOT_CONTROL_DB"]))
        try:
            initialize_catalog(control)
            operator_ok = _eligible_operator(control, args.operator_user_id)
            if not operator_ok:
                raise RuntimeError("Purge operator must be an active platform administrator")
            firm = control.execute(
                "SELECT status FROM firms WHERE id=?", (args.firm_id,)
            ).fetchone()
            if firm is None or firm["status"] != "disabled":
                raise RuntimeError("Firm must be disabled before original-file purge")
            catalog = control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (args.firm_id,)
            ).fetchone()
            if catalog is None or catalog["status"] != "disabled":
                raise RuntimeError("Tenant catalog entry must be disabled before original-file purge")
            database_path = resolve_tenant_database_for_maintenance(
                control, args.firm_id, required["COPILOT_TENANT_DB_ROOT"]
            )
        finally:
            control.close()

        preflight = inspect_firm_offboarding(
            required["COPILOT_CONTROL_DB"],
            required["COPILOT_TENANT_DB_ROOT"],
            required["COPILOT_CORPUS_DB"],
            required["COPILOT_OBJECT_STORAGE_ROOT"],
            args.firm_id,
        )
        if not preflight["purge_preflight_clear"]:
            report = {
                "purged_count": 0,
                "preflight": preflight,
                "results": [{"status": "blocked_by_offboarding_preflight"}],
                "mutations_performed": 0,
            }
            if args.json:
                print(json.dumps(report, sort_keys=True))
            else:
                print(f"Firm {args.firm_id} purge blocked by offboarding preflight")
            return 1

        result = purge_approved_requests(
            database_path,
            required["COPILOT_OBJECT_STORAGE_ROOT"],
            args.firm_id,
            args.operator_user_id,
            apply=args.apply,
            control_database_path=required["COPILOT_CONTROL_DB"],
            tenant_root=required["COPILOT_TENANT_DB_ROOT"],
            corpus_database_path=required["COPILOT_CORPUS_DB"],
        )
        report = {
            **result,
            "apply": args.apply,
            "quiescence_asserted": args.quiesced,
            "preflight": preflight,
            "mutations_performed": result["purged_count"],
        }
    except (RuntimeError, ValueError, OSError, sqlite3.Error, TenantCatalogError) as exc:
        print(f"original-file purge could not safely complete: {type(exc).__name__}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(
            f"Original-file purge: purged={report['purged_count']}; "
            f"requests={len(report['results'])}; apply={args.apply}"
        )
        for item in report["results"]:
            print(f"- request={item['request_id']} status={item['status']}")
    if any(item["status"] == "manual_review_required" for item in report["results"]):
        return 1
    if any(item["status"] == "recoverable_candidate" for item in report["results"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
