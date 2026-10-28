#!/usr/bin/env python3
"""Run an isolated restore-and-routing drill for an encrypted database bundle."""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet

from database_backup import DatabaseBundleError, restore_backup_bundle
from database_runtime import DatabaseRuntime
from original_file_reconciliation import TenantDatabase, reconcile_original_file_storage
from tenant_context import FirmContextError

_TENANT_FILE = re.compile(r"^tenant-([1-9][0-9]*)-([0-9a-f]{32})\.sqlite3$")


def _integrity_findings(path: Path, label: str) -> list[dict]:
    findings = []
    if path.is_symlink() or not path.is_file():
        return [{"scope": label, "code": "database_missing_or_unsafe"}]
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            findings.append({"scope": label, "code": "sqlite_integrity_check_failed"})
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            findings.append({"scope": label, "code": "foreign_key_check_failed"})
    finally:
        connection.close()
    return findings


def run_recovery_drill(bundle_path: str | Path, cipher: Fernet, temp_parent: str | Path) -> dict:
    """Restore to a private temporary directory and verify database/runtime/object boundaries."""
    parent = Path(temp_parent).expanduser()
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("recovery-drill temp parent must be an existing non-symlink directory")

    findings: list[dict] = []
    database_count = 0
    active_routing_checks = 0
    object_count = 0
    with tempfile.TemporaryDirectory(prefix="legal-copilot-recovery-drill-", dir=parent) as raw_temp:
        temp_root = Path(raw_temp)
        if os.name == "posix":
            os.chmod(temp_root, 0o700)
        restored = restore_backup_bundle(bundle_path, cipher, temp_root / "restored")
        runtime = DatabaseRuntime(
            restored["control_plane"], restored["tenant_root"], restored["legal_corpus"]
        )
        try:
            runtime.initialize()
            control = runtime.control_connection()
            catalog_rows = control.execute(
                "SELECT firm_id,database_file,status FROM tenant_database_catalog ORDER BY firm_id"
            ).fetchall()
            tenant_databases = []
            tenant_paths: dict[int, Path] = {}
            tenant_root = restored["tenant_root"].resolve()
            for row in catalog_rows:
                firm_id = int(row["firm_id"])
                filename = row["database_file"]
                if not filename:
                    if row["status"] == "provisioned":
                        findings.append({
                            "scope": f"firm:{firm_id}", "code": "provisioned_catalog_entry_missing_filename"
                        })
                    continue
                match = _TENANT_FILE.fullmatch(str(filename))
                if match is None or int(match.group(1)) != firm_id:
                    findings.append({
                        "scope": f"firm:{firm_id}", "code": "unsafe_tenant_database_filename"
                    })
                    continue
                candidate = restored["tenant_root"] / filename
                if candidate.is_symlink() or not candidate.is_file() or candidate.resolve().parent != tenant_root:
                    findings.append({
                        "scope": f"firm:{firm_id}", "code": "tenant_database_missing_or_unsafe"
                    })
                    continue
                tenant_paths[firm_id] = candidate
                tenant_databases.append(TenantDatabase(firm_id=firm_id, path=candidate))
                findings.extend(_integrity_findings(candidate, f"firm:{firm_id}"))
                database_count += 1

            findings.extend(_integrity_findings(restored["control_plane"], "control_plane"))
            findings.extend(_integrity_findings(restored["legal_corpus"], "legal_corpus"))
            database_count += 2

            reconciliation = reconcile_original_file_storage(
                restored["object_storage"], tenant_databases
            )
            object_count = reconciliation.checked_objects
            for finding in reconciliation.findings:
                findings.append({
                    "scope": f"firm:{finding.firm_id}" if finding.firm_id is not None else "object_storage",
                    "code": finding.code,
                    "object_id": finding.object_id,
                    "detail": finding.detail,
                })

            active_firms = control.execute(
                "SELECT id FROM firms WHERE status='active' ORDER BY id"
            ).fetchall()
            all_users = control.execute(
                "SELECT id,status FROM users ORDER BY id"
            ).fetchall()
            active_membership_pairs = {
                (int(row["user_id"]), int(row["firm_id"]))
                for row in control.execute(
                    "SELECT fm.user_id,fm.firm_id FROM firm_memberships fm "
                    "JOIN users u ON u.id=fm.user_id "
                    "JOIN firms f ON f.id=fm.firm_id "
                    "WHERE fm.status='active' AND u.status='active' AND f.status='active'"
                ).fetchall()
            }
            for firm_row in active_firms:
                firm_id = int(firm_row["id"])
                members = control.execute(
                    "SELECT fm.user_id FROM firm_memberships fm "
                    "JOIN users u ON u.id=fm.user_id "
                    "WHERE fm.firm_id=? AND fm.status='active' AND u.status='active' "
                    "ORDER BY fm.user_id",
                    (firm_id,),
                ).fetchall()
                if not members:
                    findings.append({
                        "scope": f"firm:{firm_id}", "code": "active_firm_has_no_active_membership"
                    })
                    continue
                if firm_id not in tenant_paths:
                    findings.append({
                        "scope": f"firm:{firm_id}", "code": "active_firm_database_not_validated"
                    })
                    continue
                try:
                    context = runtime.resolve_context(int(members[0]["user_id"]), firm_id)
                    connection = runtime.firm_connection(context)
                    binding = connection.execute(
                        "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
                    ).fetchone()
                    if binding is None or int(binding["firm_id"]) != firm_id:
                        findings.append({
                            "scope": f"firm:{firm_id}", "code": "runtime_tenant_binding_mismatch"
                        })
                    else:
                        active_routing_checks += 1
                except Exception as exc:
                    findings.append({
                        "scope": f"firm:{firm_id}",
                        "code": "runtime_routing_failed",
                        "detail": type(exc).__name__,
                    })

            # Negative acceptance: every identity without an active membership
            # (including suspended/revoked memberships and disabled identities)
            # must be denied for every active firm's database after restore.
            for user_row in all_users:
                user_id = int(user_row["id"])
                for firm_row in active_firms:
                    firm_id = int(firm_row["id"])
                    if (user_id, firm_id) in active_membership_pairs:
                        continue
                    try:
                        runtime.resolve_context(user_id, firm_id)
                    except FirmContextError:
                        continue
                    except Exception as exc:
                        findings.append({
                            "scope": f"firm:{firm_id}",
                            "code": "membership_denial_check_failed",
                            "detail": type(exc).__name__,
                        })
                    else:
                        findings.append({
                            "scope": f"firm:{firm_id}",
                            "code": "inactive_membership_denial_failed",
                            "detail": f"user_id:{user_id}",
                        })
        finally:
            runtime.close_current_thread()

    return {
        "verified": not findings,
        "database_count": database_count,
        "active_firm_routing_checks": active_routing_checks,
        "object_file_count": object_count,
        "findings": findings,
        "plaintext_retained": False,
        "warning": (
            "Restore drill used temporary plaintext database files. Temporary cleanup is not "
            "guaranteed secure erasure on SSDs or copy-on-write filesystems."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restore an encrypted bundle into an isolated temporary directory and validate it."
    )
    parser.add_argument("--bundle", required=True, help="Path to an encrypted database bundle.")
    parser.add_argument(
        "--temp-parent",
        default=os.environ.get("COPILOT_RECOVERY_DRILL_TMP", "").strip() or tempfile.gettempdir(),
        help="Existing protected directory for temporary plaintext restore files.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    if os.environ.get("COPILOT_ENV", "").strip().lower() in {"prod", "production"}:
        parser.error("run the restore drill on a protected maintenance/staging host, not the application process")
    key = os.environ.get("COPILOT_BACKUP_FERNET_KEY", "").strip()
    if not key:
        parser.error("set COPILOT_BACKUP_FERNET_KEY; do not pass backup keys as command-line arguments")
    try:
        cipher = Fernet(key.encode("ascii"))
        report = run_recovery_drill(args.bundle, cipher, args.temp_parent)
    except (ValueError, OSError, sqlite3.Error, DatabaseBundleError) as exc:
        print(f"recovery drill could not safely complete: {type(exc).__name__}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(
            "Database recovery drill: "
            + ("PASS" if report["verified"] else "FINDINGS")
            + f"; databases={report['database_count']}"
            + f"; active_firm_routes={report['active_firm_routing_checks']}"
            + f"; object_files={report['object_file_count']}"
        )
        for finding in report["findings"]:
            print(f"- {finding['scope']}: {finding['code']}")
        print(report["warning"])
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
