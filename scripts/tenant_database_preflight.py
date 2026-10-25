"""Read-only integrity preflight for a tenant database catalog.

Usage:
  python scripts/tenant_database_preflight.py CATALOG_DB TENANT_STORAGE_ROOT

Exit codes: 0 = no detected problems; 1 = findings; 2 = input/catalog error.
The tool never provisions, repairs, migrates, or modifies a database.
"""
from __future__ import annotations

import argparse
import hashlib
from contextlib import closing
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

_FILENAME = re.compile(r"^tenant-(?P<firm_id>[1-9][0-9]*)-(?P<nonce>[0-9a-f]{32})\.sqlite3$")


def _readonly(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)


def _has_immutable_guard(sql: str | None, table: str, operation: str, message: str) -> bool:
    """Check that a named trigger actually rejects mutation, not just that it exists."""
    if not isinstance(sql, str):
        return False
    normalized = " ".join(sql.lower().split())
    return (
        f"before {operation.lower()} on {table.lower()}" in normalized
        and "raise(abort" in normalized
        and message.lower() in normalized
    )


def _expected_firm_migrations() -> dict[int, tuple[str, str]]:
    """Read the trusted firm-profile migration manifest without opening a database."""
    directory = Path(__file__).resolve().parents[1] / "migrations" / "firm"
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("trusted firm migration directory is unavailable")
    expected: dict[int, tuple[str, str]] = {}
    for path in sorted(directory.glob("*.sql")):
        if path.is_symlink() or path.resolve().parent != directory.resolve():
            raise ValueError("firm migration sources must be regular files in the trusted directory")
        match = re.fullmatch(r"([0-9]{4,})_[a-z0-9_]+\.sql", path.name)
        if match is None:
            raise ValueError(f"invalid firm migration filename: {path.name}")
        version = int(match.group(1))
        sql = path.read_text(encoding="utf-8")
        if version in expected:
            raise ValueError(f"duplicate firm migration version: {version}")
        expected[version] = (path.name, hashlib.sha256(sql.encode("utf-8")).hexdigest())
    if not expected:
        raise ValueError("trusted firm migration directory contains no migrations")
    return expected


def audit(catalog_path: Path, storage_root: Path) -> dict[str, Any]:
    """Inspect catalog mappings and provisioned SQLite files without writing."""
    findings: list[dict[str, Any]] = []
    expected_migrations = _expected_firm_migrations()

    requested_catalog = Path(catalog_path).expanduser()
    # Match the storage-root policy: do not silently follow a configured
    # catalog symlink to a different database during a read-only audit.
    if requested_catalog.is_symlink():
        raise ValueError("tenant catalog database must not be a symlink")
    resolved_catalog = requested_catalog.resolve(strict=True)
    if not resolved_catalog.is_file():
        raise ValueError("tenant catalog database must be a regular file")

    def add(code: str, firm_id: int | None, detail: str) -> None:
        findings.append({"code": code, "firm_id": firm_id, "detail": detail})

    requested_root = storage_root.expanduser()
    # Check the configured directory entry before resolve(), otherwise a
    # symlinked root would be silently converted to its target path.
    if requested_root.is_symlink():
        raise ValueError("tenant storage root must not be a symlink")
    root = requested_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("tenant storage root must be a directory")

    with closing(_readonly(resolved_catalog)) as catalog:
        tables = {row[0] for row in catalog.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "database_profile" not in tables:
            add("missing_catalog_profile", None, "catalog database has no schema profile marker")
        else:
            try:
                profile_rows = catalog.execute(
                    "SELECT profile FROM database_profile WHERE singleton=1"
                ).fetchall()
                if len(profile_rows) != 1:
                    add("invalid_catalog_profile_binding", None, "expected exactly one control-plane profile marker")
                elif profile_rows[0][0] != "control_plane":
                    add("wrong_catalog_profile", None, "catalog database profile is not 'control_plane'")
            except sqlite3.Error:
                add("invalid_catalog_profile_binding", None, "control-plane profile marker could not be read")
            profile_triggers = {
                row[0]: row[1] for row in catalog.execute(
                    "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
                    "AND name IN ('database_profile_no_update','database_profile_no_delete')"
                )
            }
            if not (
                _has_immutable_guard(profile_triggers.get("database_profile_no_update"), "database_profile", "UPDATE", "database profile binding is immutable")
                and _has_immutable_guard(profile_triggers.get("database_profile_no_delete"), "database_profile", "DELETE", "database profile binding is immutable")
            ):
                add("mutable_catalog_profile_binding", None, "control-plane profile marker lacks effective immutable update/delete guards")
        if "tenant_database_catalog" not in tables:
            raise ValueError("catalog is missing tenant_database_catalog")
        rows = catalog.execute(
            "SELECT firm_id, database_file, status FROM tenant_database_catalog ORDER BY firm_id"
        ).fetchall()

    seen_files: dict[str, int] = {}
    inspected = 0
    for firm_id, filename, status in rows:
        if status != "provisioned":
            if status in ("provisioning", "failed"):
                add("tenant_not_ready", firm_id, f"catalog status is {status!r}")
            elif status == "disabled":
                continue
            else:
                add("unknown_catalog_status", firm_id, f"unexpected status {status!r}")
            continue
        if not filename:
            add("missing_database_reference", firm_id, "provisioned tenant has no database filename")
            continue
        match = _FILENAME.fullmatch(filename)
        if not match or int(match.group("firm_id")) != firm_id:
            add("invalid_database_reference", firm_id, "filename does not match the expected tenant naming format")
            continue
        if filename in seen_files:
            add("duplicate_database_reference", firm_id, f"database file is also mapped to firm {seen_files[filename]}")
            continue
        seen_files[filename] = firm_id

        candidate = root / filename
        if candidate.is_symlink():
            add("database_symlink", firm_id, "tenant database file is a symbolic link")
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            add("database_missing", firm_id, "catalog references a file that does not exist")
            continue
        if resolved.parent != root or not resolved.is_file():
            add("database_path_escape", firm_id, "resolved database is not a regular file directly under the storage root")
            continue
        try:
            with closing(_readonly(resolved)) as tenant:
                tables = {
                    row[0] for row in tenant.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                if "database_profile" not in tables:
                    add("missing_database_profile", firm_id, "tenant database has no schema profile marker")
                else:
                    try:
                        profile_rows = tenant.execute(
                            "SELECT profile FROM database_profile WHERE singleton=1"
                        ).fetchall()
                        if len(profile_rows) != 1:
                            add("invalid_database_profile_binding", firm_id, "expected exactly one profile marker")
                        elif profile_rows[0][0] != "firm":
                            add("wrong_database_profile", firm_id, "tenant database profile is not 'firm'")
                    except sqlite3.Error:
                        add("invalid_database_profile_binding", firm_id, "schema profile marker could not be read")
                    profile_triggers = {
                        row[0]: row[1] for row in tenant.execute(
                            "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
                            "AND name IN ('database_profile_no_update','database_profile_no_delete')"
                        )
                    }
                    if not (
                        _has_immutable_guard(profile_triggers.get("database_profile_no_update"), "database_profile", "UPDATE", "database profile binding is immutable")
                        and _has_immutable_guard(profile_triggers.get("database_profile_no_delete"), "database_profile", "DELETE", "database profile binding is immutable")
                    ):
                        add("mutable_database_profile_binding", firm_id, "schema profile marker lacks effective immutable update/delete guards")

                if "tenant_database_binding" not in tables:
                    add("missing_tenant_firm_binding", firm_id, "tenant database has no embedded firm ID binding")
                else:
                    try:
                        binding_rows = tenant.execute(
                            "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
                        ).fetchall()
                        if len(binding_rows) != 1:
                            add("invalid_tenant_firm_binding", firm_id, "expected exactly one embedded firm ID binding")
                        elif binding_rows[0][0] != firm_id:
                            add("tenant_firm_binding_mismatch", firm_id, "embedded firm ID does not match the catalog")
                    except sqlite3.Error:
                        add("invalid_tenant_firm_binding", firm_id, "embedded firm ID binding could not be read")
                    binding_triggers = {
                        row[0]: row[1] for row in tenant.execute(
                            "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
                            "AND name IN ('tenant_database_binding_no_update','tenant_database_binding_no_delete')"
                        )
                    }
                    if not (
                        _has_immutable_guard(binding_triggers.get("tenant_database_binding_no_update"), "tenant_database_binding", "UPDATE", "tenant database firm binding is immutable")
                        and _has_immutable_guard(binding_triggers.get("tenant_database_binding_no_delete"), "tenant_database_binding", "DELETE", "tenant database firm binding is immutable")
                    ):
                        add("mutable_tenant_firm_binding", firm_id, "embedded firm ID lacks effective immutable update/delete guards")

                if "schema_migrations" not in tables:
                    add("missing_schema_migration_ledger", firm_id, "tenant database has no versioned migration ledger")
                else:
                    try:
                        ledger_rows = tenant.execute(
                            "SELECT version, name, checksum_sha256 FROM schema_migrations"
                        ).fetchall()
                        recorded = {int(row[0]): (str(row[1]), str(row[2])) for row in ledger_rows}
                        expected_versions = set(expected_migrations)
                        recorded_versions = set(recorded)
                        missing_versions = sorted(expected_versions - recorded_versions)
                        unexpected_versions = sorted(recorded_versions - expected_versions)
                        if missing_versions:
                            add("incomplete_schema_migration_history", firm_id, f"missing firm migration versions: {missing_versions}")
                        if unexpected_versions:
                            add("unexpected_schema_migration_history", firm_id, f"unknown firm migration versions: {unexpected_versions}")
                        mismatched = sorted(
                            version for version in expected_versions & recorded_versions
                            if recorded[version] != expected_migrations[version]
                        )
                        if mismatched:
                            add("schema_migration_checksum_mismatch", firm_id, f"migration name/checksum differs for versions: {mismatched}")
                    except (sqlite3.Error, ValueError, TypeError, IndexError):
                        add("invalid_schema_migration_ledger", firm_id, "tenant migration ledger is malformed or unreadable")

                quick = tenant.execute("PRAGMA quick_check").fetchall()
                if len(quick) != 1 or quick[0][0] != "ok":
                    add("sqlite_quick_check_failed", firm_id, "; ".join(str(r[0]) for r in quick[:5]))
                fk = tenant.execute("PRAGMA foreign_key_check").fetchmany(20)
                if fk:
                    add("foreign_key_violations", firm_id, f"{len(fk)} or more violation rows (first 20 checked)")
                inspected += 1
        except sqlite3.Error:
            add("database_unreadable", firm_id, "SQLite could not open or inspect the database read-only")

    return {
        "mode": "read_only",
        "catalog": str(resolved_catalog),
        "tenant_storage_root": str(root),
        "catalog_entries": len(rows),
        "tenant_databases_inspected": inspected,
        "finding_count": len(findings),
        "status": "review_required" if findings else "no_detected_problems",
        "findings": findings,
        "limitations": [
            "A clean report does not prove tenant authorization or cross-firm isolation.",
            "This checks catalog mappings and SQLite integrity only; it does not inspect application queries, file storage, backups, or deployment configuration.",
            "Disabled tenants are not opened. Provisioning and failed entries are reported but never repaired.",
            "The catalog and tenant files can change after inspection; run during a quiet maintenance window for a stable snapshot.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog_db", type=Path, help="existing control-plane SQLite catalog")
    parser.add_argument("storage_root", type=Path, help="existing tenant database directory")
    args = parser.parse_args(argv)
    if not args.catalog_db.is_file():
        print(json.dumps({"error": "catalog database file not found"}), file=sys.stderr)
        return 2
    if not args.storage_root.is_dir():
        print(json.dumps({"error": "tenant storage root not found"}), file=sys.stderr)
        return 2
    try:
        report = audit(args.catalog_db, args.storage_root)
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(json.dumps({"error": "preflight failed", "detail": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["finding_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
