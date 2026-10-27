#!/usr/bin/env python3
"""Read-only purge/offboarding gate for a disabled tenant database."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

from original_file_reconciliation import TenantDatabase, reconcile_original_file_storage
from tenant_catalog import (
    TenantCatalogError,
    initialize_catalog,
    resolve_tenant_database_for_maintenance,
)


def _read_only(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise ValueError("control-plane database is missing or unsafe")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def inspect_firm_offboarding(
    control_db: str | Path,
    tenant_root: str | Path,
    corpus_db: str | Path,
    object_root: str | Path,
    firm_id: int,
) -> dict:
    """Check access revocation, database integrity, holds, and object integrity without mutation."""
    if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
        raise ValueError("firm_id must be a positive integer")
    control_path = Path(control_db).expanduser()
    tenant_root_path = Path(tenant_root).expanduser()
    object_root_path = Path(object_root).expanduser()
    if object_root_path.is_symlink() or not object_root_path.is_dir():
        raise ValueError("object storage root must be an existing non-symlink directory")
    if tenant_root_path.is_symlink() or not tenant_root_path.is_dir():
        raise ValueError("tenant storage root must be an existing non-symlink directory")
    object_resolved = object_root_path.resolve()
    tenant_resolved = tenant_root_path.resolve()
    control_resolved = control_path.resolve()
    corpus_resolved = Path(corpus_db).expanduser().resolve()
    if (
        object_resolved == tenant_resolved
        or object_resolved in tenant_resolved.parents
        or tenant_resolved in object_resolved.parents
        or object_resolved == control_resolved
        or object_resolved in control_resolved.parents
        or object_resolved == corpus_resolved
        or object_resolved in corpus_resolved.parents
    ):
        raise ValueError("object storage must be separate from database paths")

    findings: list[dict] = []
    database_path = None
    firm_status = None
    catalog_status = None
    active_memberships = None
    object_count = 0
    purged_tombstone_count = 0
    active_holds = 0

    control = _read_only(control_path)
    try:
        initialize_catalog(control)
        firm = control.execute("SELECT status FROM firms WHERE id=?", (firm_id,)).fetchone()
        if firm is None:
            raise ValueError("firm does not exist")
        firm_status = firm["status"]
        catalog = control.execute(
            "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
        ).fetchone()
        if catalog is None:
            raise ValueError("firm has no trusted tenant catalog entry")
        catalog_status = catalog["status"]
        if firm_status != "disabled":
            findings.append({"code": "firm_access_not_disabled"})
        if catalog_status != "disabled":
            findings.append({"code": "tenant_catalog_not_disabled"})
        active_memberships = int(control.execute(
            "SELECT COUNT(*) FROM firm_memberships fm JOIN users u ON u.id=fm.user_id "
            "WHERE fm.firm_id=? AND fm.status='active' AND u.status='active'",
            (firm_id,),
        ).fetchone()[0])
        if active_memberships:
            findings.append({"code": "active_memberships_remain", "count": active_memberships})
        database_path = resolve_tenant_database_for_maintenance(
            control, firm_id, tenant_root_path
        )
    finally:
        control.close()

    tenant = sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    tenant.row_factory = sqlite3.Row
    tenant.execute("PRAGMA query_only=ON")
    try:
        integrity = tenant.execute("PRAGMA integrity_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            findings.append({"code": "sqlite_integrity_check_failed"})
        if tenant.execute("PRAGMA foreign_key_check").fetchall():
            findings.append({"code": "foreign_key_check_failed"})
        binding = tenant.execute(
            "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
        ).fetchone()
        if binding is None or int(binding["firm_id"]) != firm_id:
            findings.append({"code": "tenant_binding_mismatch"})
        tables = {row[0] for row in tenant.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "original_file_objects" not in tables:
            findings.append({"code": "original_file_schema_missing"})
        else:
            rows = tenant.execute(
                "SELECT object_id,state,legal_hold,purged_at FROM original_file_objects ORDER BY object_id"
            ).fetchall()
            active_rows = [row for row in rows if row["purged_at"] is None]
            object_count = len(active_rows)
            purged_tombstone_count = len(rows) - len(active_rows)
            active_holds = sum(1 for row in active_rows if int(row["legal_hold"]) == 1)
            if active_holds:
                findings.append({"code": "active_legal_holds_remain", "count": active_holds})
            staged_count = sum(1 for row in active_rows if row["state"] == "staged")
            if staged_count:
                findings.append({"code": "staged_uploads_require_review", "count": staged_count})
            quarantined_count = sum(1 for row in active_rows if row["state"] == "quarantined")
            if quarantined_count:
                findings.append({
                    "code": "quarantined_originals_require_review", "count": quarantined_count
                })
    finally:
        tenant.close()

    try:
        reconciliation = reconcile_original_file_storage(
            object_resolved, [TenantDatabase(firm_id=firm_id, path=database_path)]
        )
        for finding in reconciliation.findings:
            # Other firms' namespaces are outside this firm's purge decision.
            if finding.firm_id not in {None, firm_id}:
                continue
            findings.append({
                "code": finding.code,
                "object_id": finding.object_id,
                "detail": finding.detail,
            })
    except (ValueError, OSError) as exc:
        findings.append({"code": "object_reconciliation_failed", "detail": type(exc).__name__})

    findings.sort(key=lambda item: (item["code"], str(item.get("object_id", ""))))
    return {
        "firm_id": firm_id,
        "firm_status": firm_status,
        "catalog_status": catalog_status,
        "active_memberships": active_memberships,
        "original_object_count": object_count,
        "purged_tombstone_count": purged_tombstone_count,
        "active_legal_hold_count": active_holds,
        "findings": findings,
        "purge_preflight_clear": not findings,
        "mutations_performed": 0,
        "warning": (
            "A clear preflight is not legal authorization to delete. Confirm retention duties, "
            "backup/export requirements, contractual obligations, and legal holds before any purge."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only offboarding/purge preflight; this command never deletes data."
    )
    parser.add_argument("--firm-id", type=int, required=True)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
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
        report = inspect_firm_offboarding(
            required["COPILOT_CONTROL_DB"],
            required["COPILOT_TENANT_DB_ROOT"],
            required["COPILOT_CORPUS_DB"],
            required["COPILOT_OBJECT_STORAGE_ROOT"],
            args.firm_id,
        )
    except (ValueError, OSError, sqlite3.Error, TenantCatalogError) as exc:
        print(f"offboarding preflight could not safely complete: {type(exc).__name__}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(
            f"Firm {args.firm_id} offboarding preflight: "
            + ("CLEAR FOR POLICY REVIEW" if report["purge_preflight_clear"] else "BLOCKED")
            + f"; objects={report['original_object_count']}"
            + f"; active_holds={report['active_legal_hold_count']}"
        )
        for finding in report["findings"]:
            print(f"- {finding['code']}")
        print(report["warning"])
    return 0 if report["purge_preflight_clear"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
