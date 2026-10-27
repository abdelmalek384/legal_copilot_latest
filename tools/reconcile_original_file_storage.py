#!/usr/bin/env python3
"""Run a read-only reconciliation of firm original-file metadata and local objects."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import asdict
from pathlib import Path

from database_runtime import DatabaseRuntime
from original_file_reconciliation import TenantDatabase, reconcile_original_file_storage
from tenant_catalog import TenantCatalogError, resolve_tenant_database


def _read_only(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Configured control-plane database is missing or unsafe: {path}")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only check of tenant original-file metadata against local object bytes."
    )
    parser.add_argument(
        "--object-root",
        default=os.environ.get("COPILOT_OBJECT_STORAGE_ROOT", "").strip(),
        help="Local object root (defaults to COPILOT_OBJECT_STORAGE_ROOT).",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    if not args.object_root:
        parser.error("set COPILOT_OBJECT_STORAGE_ROOT or pass --object-root")

    try:
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
                raise RuntimeError(
                    "Active firms lack provisioned tenant catalog entries: "
                    + ", ".join(str(firm_id) for firm_id in missing)
                )
            tenants = []
            for firm_id in sorted(provisioned):
                path = resolve_tenant_database(control, firm_id, runtime.paths.tenant_root)
                tenants.append(TenantDatabase(firm_id=firm_id, path=path))
        finally:
            control.close()

        report = reconcile_original_file_storage(args.object_root, tenants)
    except (RuntimeError, ValueError, sqlite3.Error, TenantCatalogError) as exc:
        print(f"reconciliation could not safely complete: {exc}", file=sys.stderr)
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
            "Original-file reconciliation: "
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
