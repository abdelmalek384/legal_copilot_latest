"""Read-only consistency audit for the separate-database tenant lifecycle.

This module never initializes schemas, creates directories, repairs catalog rows,
or changes database state. It is an operator preflight, not a reconciliation tool.
"""
from __future__ import annotations

import os
import re
import sqlite3
import stat
from pathlib import Path
from typing import Any


_TENANT_FILENAME = re.compile(r"tenant-(\d+)-([0-9a-f]{32})\.sqlite3\Z")


def _finding(findings: list[dict[str, Any]], severity: str, code: str, detail: str, firm_id: int | None = None) -> None:
    item: dict[str, Any] = {"severity": severity, "code": code, "detail": detail}
    if firm_id is not None:
        item["firm_id"] = firm_id
    findings.append(item)


def _read_only_connection(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def _private_regular_file(path: Path, label: str, findings: list[dict[str, Any]]) -> bool:
    if path.is_symlink():
        _finding(findings, "error", "symlinked_database", f"{label} database path is a symlink")
        return False
    if not path.is_file():
        _finding(findings, "error", "missing_database", f"{label} database file is missing or not a regular file")
        return False
    if os.name == "posix":
        try:
            mode = stat.S_IMODE(path.stat().st_mode)
        except OSError:
            _finding(findings, "error", "unverifiable_permissions", f"{label} database permissions cannot be verified")
            return False
        if mode & 0o077:
            _finding(findings, "error", "unsafe_permissions", f"{label} database permissions allow group/other access")
            return False
    return True


def _check_profile(path: Path, expected_profile: str, findings: list[dict[str, Any]], firm_id: int | None = None) -> bool:
    connection = None
    try:
        connection = _read_only_connection(path)
        row = connection.execute(
            "SELECT profile FROM database_profile WHERE singleton=1"
        ).fetchone()
        if row is None or row["profile"] != expected_profile:
            _finding(findings, "error", "wrong_database_profile", f"Database does not carry the expected {expected_profile!r} profile marker", firm_id)
            return False
        if expected_profile == "firm":
            binding = connection.execute(
                "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
            ).fetchone()
            if binding is None or firm_id is None or int(binding["firm_id"]) != firm_id:
                _finding(findings, "error", "wrong_tenant_binding", "Tenant database binding does not match the trusted catalog firm ID", firm_id)
                return False
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        if len(integrity) != 1 or integrity[0][0] != "ok":
            _finding(findings, "error", "integrity_check_failed", "Database integrity_check did not return exactly 'ok'", firm_id)
            return False
        foreign_key_violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_violations:
            _finding(findings, "error", "foreign_key_check_failed", f"Database has {len(foreign_key_violations)} foreign-key violation(s)", firm_id)
            return False
        return True
    except (sqlite3.Error, OSError, ValueError) as exc:
        _finding(findings, "error", "database_unreadable", f"Database could not be audited ({type(exc).__name__})", firm_id)
        return False
    finally:
        if connection is not None:
            connection.close()


def audit_tenant_lifecycle(control_plane_path: str | Path, tenant_root: str | Path, legal_corpus_path: str | Path) -> dict[str, Any]:
    """Return consistency findings without creating or mutating any configured file."""
    control_path = Path(control_plane_path).expanduser()
    root = Path(tenant_root).expanduser()
    corpus_path = Path(legal_corpus_path).expanduser()
    findings: list[dict[str, Any]] = []

    if _private_regular_file(control_path, "control-plane", findings):
        _check_profile(control_path, "control_plane", findings)
    if _private_regular_file(corpus_path, "legal-corpus", findings):
        _check_profile(corpus_path, "legal_corpus", findings)

    if root.is_symlink():
        _finding(findings, "error", "symlinked_tenant_root", "Tenant storage root must not be a symlink")
        return {"ok": False, "findings": findings, "firms_checked": 0, "tenant_databases_checked": 0}
    if not root.is_dir():
        _finding(findings, "error", "missing_tenant_root", "Tenant storage root does not exist or is not a directory")
        return {"ok": False, "findings": findings, "firms_checked": 0, "tenant_databases_checked": 0}
    if not _private_regular_file(control_path, "control-plane", []) :
        # The first validation already reported the useful error. Do not open an
        # absent/unsafe control-plane file merely to discover a secondary error.
        return {"ok": False, "findings": findings, "firms_checked": 0, "tenant_databases_checked": 0}

    control = None
    firms_checked = 0
    tenant_databases_checked = 0
    referenced_files: set[str] = set()
    try:
        control = _read_only_connection(control_path)
        firms = {
            int(row["id"]): dict(row)
            for row in control.execute("SELECT id,name,status FROM firms").fetchall()
        }
        catalog_rows = control.execute(
            "SELECT firm_id,database_file,status FROM tenant_database_catalog ORDER BY firm_id"
        ).fetchall()
        catalog = {int(row["firm_id"]): dict(row) for row in catalog_rows}
        firms_checked = len(firms)

        for firm_id, firm in firms.items():
            row = catalog.get(firm_id)
            status = firm["status"]
            if status == "active" and (row is None or row["status"] != "provisioned"):
                _finding(findings, "error", "active_firm_without_provisioned_database", "Active firm lacks a provisioned catalog entry", firm_id)
            elif status == "provisioning":
                _finding(findings, "error", "stale_provisioning_firm", "Firm remains in provisioning state and needs operator review", firm_id)
            elif status not in {"active", "disabled"}:
                _finding(findings, "error", "unknown_firm_status", f"Firm has unrecognized lifecycle status {status!r}", firm_id)
            if status == "disabled" and row is not None and row["status"] not in {"disabled", "failed"}:
                _finding(findings, "error", "disabled_firm_catalog_mismatch", "Disabled firm has a catalog entry that is not disabled/failed", firm_id)

        for firm_id, row in catalog.items():
            if firm_id not in firms:
                _finding(findings, "error", "catalog_entry_without_firm", "Tenant catalog entry references an unknown firm", firm_id)
                continue
            status = row["status"]
            database_file = row["database_file"]
            if status == "provisioning":
                _finding(findings, "error", "stale_catalog_provisioning", "Tenant catalog entry remains in provisioning state", firm_id)
            elif status == "failed":
                _finding(findings, "warning", "failed_provisioning_record", "Tenant provisioning previously failed; inspect before retrying", firm_id)
            elif status not in {"provisioned", "disabled", "failed"}:
                _finding(findings, "error", "unknown_catalog_status", f"Tenant catalog has unrecognized status {status!r}", firm_id)

            if not database_file:
                if status == "provisioned":
                    _finding(findings, "error", "provisioned_database_reference_missing", "Provisioned catalog entry has no database filename", firm_id)
                continue
            if not isinstance(database_file, str) or Path(database_file).name != database_file:
                _finding(findings, "error", "unsafe_catalog_filename", "Catalog database filename is not a simple basename", firm_id)
                continue
            match = _TENANT_FILENAME.fullmatch(database_file)
            if match is None or int(match.group(1)) != firm_id:
                _finding(findings, "error", "invalid_catalog_filename", "Catalog database filename does not match the trusted firm namespace", firm_id)
                continue

            path = root / database_file
            referenced_files.add(database_file)
            if path.is_symlink():
                _finding(findings, "error", "tenant_database_symlink", "Cataloged tenant database is a symlink", firm_id)
                continue
            if not path.is_file():
                _finding(findings, "error", "cataloged_database_missing", "Catalog references a tenant database that is missing", firm_id)
                continue
            if os.name == "posix":
                try:
                    mode = stat.S_IMODE(path.stat().st_mode)
                except OSError:
                    _finding(findings, "error", "tenant_permissions_unverifiable", "Tenant database permissions cannot be verified", firm_id)
                    continue
                if mode & 0o077:
                    _finding(findings, "error", "tenant_permissions_unsafe", "Tenant database permissions allow group/other access", firm_id)
                    continue
            if status in {"provisioned", "disabled"}:
                if _check_profile(path, "firm", findings, firm_id):
                    tenant_databases_checked += 1

        for path in sorted(root.glob("tenant-*.sqlite3")):
            if path.name not in referenced_files:
                code = "orphaned_tenant_symlink" if path.is_symlink() else "unreferenced_tenant_database"
                _finding(findings, "error", code, "Tenant database file is not referenced by the trusted catalog")
    except (sqlite3.Error, OSError, ValueError) as exc:
        _finding(findings, "error", "control_plane_audit_failed", f"Tenant lifecycle audit could not complete ({type(exc).__name__})")
    finally:
        if control is not None:
            control.close()

    return {
        "ok": not any(item["severity"] == "error" for item in findings),
        "findings": findings,
        "firms_checked": firms_checked,
        "tenant_databases_checked": tenant_databases_checked,
    }
