#!/usr/bin/env python3
"""Read-only reminder outbox health check for external monitoring.

Exit codes: 0 healthy, 1 operator attention required, 2 configuration/runtime error.
The command never claims SMTP acceptance is inbox delivery and never sends mail.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from database_runtime import DatabaseRuntime, DatabaseRuntimeError
from tenant_catalog import TenantCatalogError, resolve_tenant_database


def _read_only(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("database file is missing or is not a regular file")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def inspect_health(
    control_path: Path,
    tenant_root: Path,
    *,
    now: datetime | None = None,
    stale_queued_minutes: int = 30,
) -> dict:
    if isinstance(stale_queued_minutes, bool) or not isinstance(stale_queued_minutes, int) or not 1 <= stale_queued_minutes <= 10080:
        raise ValueError("stale_queued_minutes must be between 1 and 10080")
    current = datetime.now(timezone.utc) if now is None else now
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    current = current.astimezone(timezone.utc)
    cutoff = current - timedelta(minutes=stale_queued_minutes)
    report = {
        "mode": "read_only_health_check",
        "checked_at": current.isoformat(),
        "stale_queued_threshold_minutes": stale_queued_minutes,
        "healthy": True,
        "firms_scanned": 0,
        "totals": {
            "queued": 0, "sending": 0, "accepted_by_smtp": 0,
            "failed": 0, "ambiguous": 0,
            "stale_queued": 0, "expired_sending": 0,
        },
        "firms": [],
        "findings": [],
        "warnings": [
            "SMTP acceptance is not confirmation of inbox delivery.",
            "Ambiguous outcomes require operator reconciliation and must not be blindly retried.",
            "This check reads counts and timestamps only; it does not inspect message bodies or matter content.",
        ],
    }
    control = _read_only(control_path)
    try:
        rows = control.execute("SELECT id FROM firms WHERE status='active' ORDER BY id").fetchall()
        for row in rows:
            firm_id = int(row["id"])
            firm = {
                "firm_id": firm_id,
                "counts": {key: 0 for key in ("queued", "sending", "accepted_by_smtp", "failed", "ambiguous")},
                "stale_queued": 0,
                "expired_sending": 0,
                "healthy": True,
            }
            try:
                tenant_path = resolve_tenant_database(control, firm_id, tenant_root)
                tenant = _read_only(tenant_path)
                try:
                    table = tenant.execute(
                        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='reminder_deliveries'"
                    ).fetchone()
                    if table is None:
                        raise RuntimeError("reminder outbox schema is unavailable")
                    for item in tenant.execute(
                        "SELECT status,COUNT(*) AS total FROM reminder_deliveries GROUP BY status"
                    ).fetchall():
                        if item["status"] in firm["counts"]:
                            firm["counts"][item["status"]] = int(item["total"])
                    firm["stale_queued"] = int(tenant.execute(
                        "SELECT COUNT(*) FROM reminder_deliveries WHERE status='queued' "
                        "AND (julianday(COALESCE(next_attempt_at,updated_at,created_at)) IS NULL "
                        "OR julianday(COALESCE(next_attempt_at,updated_at,created_at)) <= julianday(?))",
                        (cutoff.isoformat(),),
                    ).fetchone()[0])
                    firm["expired_sending"] = int(tenant.execute(
                        "SELECT COUNT(*) FROM reminder_deliveries WHERE status='sending' "
                        "AND (lease_until IS NULL OR julianday(lease_until) IS NULL "
                        "OR julianday(lease_until) <= julianday(?))",
                        (current.isoformat(),),
                    ).fetchone()[0])
                finally:
                    tenant.close()
            except (TenantCatalogError, sqlite3.Error, OSError, RuntimeError):
                firm["healthy"] = False
                report["healthy"] = False
                report["findings"].append({
                    "firm_id": firm_id,
                    "code": "tenant_outbox_unavailable",
                    "severity": "critical",
                })
                report["firms"].append(firm)
                continue

            for key, value in firm["counts"].items():
                report["totals"][key] += value
            report["totals"]["stale_queued"] += firm["stale_queued"]
            report["totals"]["expired_sending"] += firm["expired_sending"]
            firm_issues = []
            if firm["counts"]["failed"]:
                firm_issues.append(("failed_reminders_present", "warning"))
            if firm["counts"]["ambiguous"]:
                firm_issues.append(("ambiguous_reminders_require_reconciliation", "critical"))
            if firm["stale_queued"]:
                firm_issues.append(("stale_queued_reminders", "warning"))
            if firm["expired_sending"]:
                firm_issues.append(("expired_or_missing_sender_lease", "critical"))
            for code, severity in firm_issues:
                report["findings"].append({"firm_id": firm_id, "code": code, "severity": severity})
            firm["healthy"] = not firm_issues
            if firm_issues:
                report["healthy"] = False
            report["firms_scanned"] += 1
            report["firms"].append(firm)
    finally:
        control.close()
    return report


def _write_report(path: Path, report: dict, runtime: DatabaseRuntime) -> None:
    if path.is_symlink():
        raise RuntimeError("report output must not be a symbolic link")
    destination = path.absolute()
    tenant_root = runtime.paths.tenant_root.resolve()
    protected = {runtime.paths.control_plane.resolve(), runtime.paths.legal_corpus.resolve()}
    if destination.resolve(strict=False) in protected or destination.resolve(strict=False) == tenant_root or tenant_root in destination.resolve(strict=False).parents:
        raise RuntimeError("report output must not overwrite or reside inside database storage")
    if destination.exists() and not destination.is_file():
        raise RuntimeError("report output must be a regular file")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stale-queued-minutes", type=int, default=30)
    parser.add_argument("--now", help="optional ISO timestamp with timezone offset")
    parser.add_argument("--out", type=Path, help="write sanitized JSON report outside database storage")
    args = parser.parse_args(argv)
    try:
        now = None
        if args.now:
            now = datetime.fromisoformat(args.now)
            if now.tzinfo is None or now.utcoffset() is None:
                raise ValueError("--now must include a timezone offset")
        runtime = DatabaseRuntime.from_env()
        report = inspect_health(
            runtime.paths.control_plane, runtime.paths.tenant_root,
            now=now, stale_queued_minutes=args.stale_queued_minutes,
        )
        if args.out:
            _write_report(args.out, report, runtime)
        else:
            print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
        return 0 if report["healthy"] else 1
    except (DatabaseRuntimeError, TenantCatalogError, sqlite3.Error, OSError, RuntimeError, ValueError) as exc:
        print(f"reminder health check could not complete: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
