"""Quiesced, backup-first migration orchestration for firm-per-database deployments.

Plan mode is read-only. Apply mode requires explicit operator confirmations,
preflights every eligible database, snapshots every target before changing any
schema, then migrates sequentially and stops on the first failure. It never
creates, adopts, deletes, or reassigns tenant database files.
"""
from __future__ import annotations

import argparse
import hashlib
from contextlib import closing
import json
import os
import re
import sqlite3
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

# Support both "python -m tools.migrate_tenant_fleet" and direct script execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db_migrations import MigrationError, read_migration_file
from schema_profiles import apply_profile_migrations

_FILENAME = re.compile(r"^tenant-(?P<firm_id>[1-9][0-9]*)-(?P<nonce>[0-9a-f]{32})\.sqlite3$")
_MIGRATION = re.compile(r"^(?P<version>[0-9]{4,})_[a-z0-9_]+\.sql$")


class FleetMigrationError(RuntimeError):
    """Raised when fleet migration cannot safely proceed."""


def _secure_regular_file(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise FleetMigrationError(f"{label} must be a regular, non-symlink file")
    if os.name == "posix":
        try:
            mode = stat.S_IMODE(path.stat().st_mode)
        except OSError as exc:
            raise FleetMigrationError(f"{label} permissions cannot be inspected") from exc
        if mode & 0o077:
            raise FleetMigrationError(f"{label} permits group/other access; expected private mode")


def _secure_sidecars(path: Path) -> None:
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = Path(str(path) + suffix)
        if not sidecar.exists() and not sidecar.is_symlink():
            continue
        if sidecar.is_symlink() or not sidecar.is_file():
            raise FleetMigrationError(f"Unsafe SQLite sidecar for {path.name}")
        if os.name == "posix" and stat.S_IMODE(sidecar.stat().st_mode) & 0o077:
            raise FleetMigrationError(f"SQLite sidecar permissions are too broad for {path.name}")


def _open_readonly(path: Path) -> sqlite3.Connection:
    _secure_regular_file(path, "Database")
    _secure_sidecars(path)
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _migration_inventory(directory: Path) -> list[tuple[int, str, str]]:
    if directory.is_symlink() or not directory.is_dir():
        raise FleetMigrationError("Trusted firm migration directory is missing or unsafe")
    inventory = []
    seen = set()
    for path in sorted(directory.glob("*.sql")):
        if path.is_symlink() or path.resolve().parent != directory.resolve():
            raise FleetMigrationError(f"Unsafe migration file: {path.name}")
        match = _MIGRATION.fullmatch(path.name)
        if not match:
            raise FleetMigrationError(f"Invalid migration filename: {path.name}")
        version = int(match.group("version"))
        if version in seen:
            raise FleetMigrationError(f"Duplicate migration version: {version}")
        seen.add(version)
        try:
            sql = read_migration_file(path)
        except MigrationError as exc:
            raise FleetMigrationError(f"Unsafe migration input: {path.name}") from exc
        if not sql.strip():
            raise FleetMigrationError(f"Empty migration file: {path.name}")
        # Match db_migrations.apply_migrations exactly, including text-mode newline normalization.
        inventory.append((version, path.name, hashlib.sha256(sql.encode("utf-8")).hexdigest()))
    return sorted(inventory)


def _pending_versions(connection: sqlite3.Connection, migrations_root: Path) -> list[int]:
    inventory = _migration_inventory(migrations_root / "firm")
    try:
        recorded = {
            int(row["version"]): (str(row["name"]), str(row["checksum_sha256"]))
            for row in connection.execute(
                "SELECT version,name,checksum_sha256 FROM schema_migrations"
            )
        }
    except sqlite3.Error as exc:
        raise FleetMigrationError("Tenant migration ledger is missing or unreadable") from exc
    available = {version: (name, checksum) for version, name, checksum in inventory}
    missing = sorted(set(recorded) - set(available))
    if missing:
        raise FleetMigrationError(f"Applied migration files are missing: {missing}")
    if recorded:
        latest = max(recorded)
        expected_prefix = sorted(v for v in available if v <= latest)
        if sorted(recorded) != expected_prefix:
            raise FleetMigrationError("Applied migration history is not an ordered prefix")
    for version, value in recorded.items():
        if available[version] != value:
            raise FleetMigrationError(f"Applied migration {version} name/checksum drift")
    return [version for version in sorted(available) if version not in recorded]


def build_plan(control_db: str | Path, tenant_root: str | Path, migrations_root: str | Path) -> dict:
    control_path = Path(control_db).expanduser()
    root_arg = Path(tenant_root).expanduser()
    migration_arg = Path(migrations_root).expanduser()
    if control_path.is_symlink() or not control_path.is_file():
        raise FleetMigrationError("Control-plane database must already exist as a regular file")
    if root_arg.is_symlink() or not root_arg.is_dir():
        raise FleetMigrationError("Tenant storage root must already exist and must not be a symlink")
    if migration_arg.is_symlink() or not migration_arg.is_dir():
        raise FleetMigrationError("Trusted migrations root must exist and must not be a symlink")
    control_path = control_path.resolve()
    root = root_arg.resolve()
    migrations = migration_arg.resolve()
    if control_path.parent == root or control_path.is_relative_to(root):
        raise FleetMigrationError("Control-plane database must be outside tenant storage")
    if root.is_relative_to(migrations) or migrations.is_relative_to(root):
        raise FleetMigrationError("Migration source and tenant storage must be separate")

    with closing(_open_readonly(control_path)) as control:
        try:
            profile = control.execute(
                "SELECT profile FROM database_profile WHERE singleton=1"
            ).fetchone()
            if profile is None or profile["profile"] != "control_plane":
                raise FleetMigrationError("Control database is not immutably bound to control_plane")
            rows = control.execute(
                "SELECT c.firm_id,c.database_file,c.status,f.status AS firm_status "
                "FROM tenant_database_catalog c JOIN firms f ON f.id=c.firm_id "
                "ORDER BY c.firm_id"
            ).fetchall()
        except sqlite3.Error as exc:
            raise FleetMigrationError("Control-plane catalog is missing or unreadable") from exc

    # Every SQLite database file in this dedicated root must have one catalog
    # reference. Ignoring an orphan would make release preflight incomplete and
    # could leave matter data outside the backup/migration inventory.
    catalog_files = {
        row["database_file"] for row in rows
        if isinstance(row["database_file"], str) and row["database_file"]
    }
    try:
        actual_database_files = {
            entry.name for entry in root.iterdir() if entry.name.endswith(".sqlite3")
        }
    except OSError as exc:
        raise FleetMigrationError("Tenant storage inventory could not be read") from exc
    if actual_database_files != catalog_files:
        raise FleetMigrationError(
            "Tenant storage contains missing or unsafe database files, or unreferenced files"
        )

    targets = []
    skipped = []
    seen_files = set()
    for row in rows:
        firm_id = int(row["firm_id"])
        status = str(row["status"])
        firm_status = str(row["firm_status"])
        filename = row["database_file"]
        if status == "provisioned" and firm_status not in {"active", "suspended"}:
            raise FleetMigrationError(
                f"Firm {firm_id} lifecycle status {firm_status!r} conflicts with provisioned catalog state"
            )
        if status == "disabled" and firm_status != "disabled":
            raise FleetMigrationError(
                f"Firm {firm_id} lifecycle status {firm_status!r} conflicts with disabled catalog state"
            )
        if status not in {"provisioned", "disabled"}:
            skipped.append({"firm_id": firm_id, "catalog_status": status, "firm_status": firm_status,
                            "reason": "lifecycle state is not eligible for schema migration"})
            continue
        if not filename or not isinstance(filename, str):
            raise FleetMigrationError(f"Eligible firm {firm_id} has no database filename")
        match = _FILENAME.fullmatch(filename)
        if not match or int(match.group("firm_id")) != firm_id:
            raise FleetMigrationError(f"Catalog filename is invalid or mismatched for firm {firm_id}")
        if filename in seen_files:
            raise FleetMigrationError("Multiple firms reference the same tenant database filename")
        seen_files.add(filename)
        path = root / filename
        if path.is_symlink() or path.resolve().parent != root or not path.is_file():
            raise FleetMigrationError(f"Tenant database path is missing or unsafe for firm {firm_id}")
        with closing(_open_readonly(path)) as tenant:
            tenant_profile = tenant.execute(
                "SELECT profile FROM database_profile WHERE singleton=1"
            ).fetchone()
            binding = tenant.execute(
                "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
            ).fetchone()
            if tenant_profile is None or tenant_profile["profile"] != "firm":
                raise FleetMigrationError(f"Tenant {firm_id} has an invalid immutable schema profile")
            if binding is None or int(binding["firm_id"]) != firm_id:
                raise FleetMigrationError(f"Tenant {firm_id} immutable firm binding does not match catalog")
            integrity = tenant.execute("PRAGMA integrity_check").fetchone()
            if integrity is None or integrity[0] != "ok":
                raise FleetMigrationError(f"Tenant {firm_id} failed integrity_check")
            foreign_key_errors = tenant.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_key_errors:
                raise FleetMigrationError(f"Tenant {firm_id} failed foreign_key_check")
            pending = _pending_versions(tenant, migrations)
        metadata = path.stat()
        targets.append({
            "firm_id": firm_id,
            "file_identity": [metadata.st_dev, metadata.st_ino],
            "firm_status": firm_status,
            "catalog_status": status,
            "database_file": filename,
            "pending_versions": pending,
        })
    return {
        "schema": "tenant-fleet-migration-plan/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "targets": targets,
        "skipped": skipped,
        "target_count": len(targets),
        "pending_database_count": sum(bool(t["pending_versions"]) for t in targets),
        "pending_migration_count": sum(len(t["pending_versions"]) for t in targets),
    }


def _snapshot(path: Path, backup_dir: Path, firm_id: int, run_id: str) -> Path:
    destination = backup_dir / f"{run_id}-firm-{firm_id}.sqlite3"
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(destination, flags, 0o600)
    except OSError as exc:
        raise FleetMigrationError(f"Cannot create exclusive backup for firm {firm_id}") from exc
    os.close(fd)
    try:
        with closing(sqlite3.connect(path, timeout=30)) as source, closing(sqlite3.connect(destination, timeout=30)) as target:
            source.backup(target)
            target.execute("PRAGMA foreign_keys=ON")
            integrity = target.execute("PRAGMA integrity_check").fetchone()
            if integrity is None or integrity[0] != "ok":
                raise FleetMigrationError(f"Backup integrity check failed for firm {firm_id}")
        if os.name == "posix":
            os.chmod(destination, 0o600)
        return destination
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def _persist_manifest(directory: Path, run_id: str, payload: dict) -> str:
    destination = directory / f"{run_id}-manifest.json"
    temporary = directory / f".{run_id}-manifest-{os.getpid()}.tmp"
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(temporary, flags, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        if os.name == "posix":
            os.chmod(destination, 0o600)
        return str(destination)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def apply_fleet(control_db: str | Path, tenant_root: str | Path, migrations_root: str | Path,
                backup_dir: str | Path, *, confirm_workers_stopped: bool) -> dict:
    if not confirm_workers_stopped:
        raise FleetMigrationError("Refusing schema changes without explicit worker-stop confirmation")
    root = Path(tenant_root).expanduser().resolve()
    backup_arg = Path(backup_dir).expanduser()
    if backup_arg.is_symlink():
        raise FleetMigrationError("Backup directory must not be a symlink")
    backup_arg.mkdir(mode=0o700, parents=True, exist_ok=True)
    backup = backup_arg.resolve()
    if backup == root or backup.is_relative_to(root) or root.is_relative_to(backup):
        raise FleetMigrationError("Backup directory must be separate from tenant storage")
    control = Path(control_db).expanduser().resolve()
    if backup == control.parent or control.is_relative_to(backup):
        raise FleetMigrationError("Backup directory must be separate from the control-plane database")
    if os.name == "posix":
        os.chmod(backup, 0o700)
        if stat.S_IMODE(backup.stat().st_mode) & 0o077:
            raise FleetMigrationError("Backup directory is not private")
    plan = build_plan(control, root, migrations_root)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backups = []
    work_targets = [target for target in plan["targets"] if target["pending_versions"]]
    manifest = {
        "schema": "tenant-fleet-migration-result/v1",
        "run_id": run_id,
        "status": "preparing_backups",
        "preflight": plan,
        "backups": backups,
        "outcome": [],
    }
    manifest_path = _persist_manifest(backup, run_id, manifest)
    # Complete all snapshots before touching any schema; a backup failure means no migration begins.
    for target in work_targets:
        path = root / target["database_file"]
        _secure_regular_file(path, f"Tenant {target['firm_id']}")
        _secure_sidecars(path)
        identity = path.stat()
        if [identity.st_dev, identity.st_ino] != target["file_identity"]:
            raise FleetMigrationError(f"Tenant {target['firm_id']} file identity changed after preflight")
        snapshot = _snapshot(path, backup, target["firm_id"], run_id)
        identity_after = path.stat()
        if [identity_after.st_dev, identity_after.st_ino] != target["file_identity"]:
            raise FleetMigrationError(f"Tenant {target['firm_id']} file identity changed during backup")
        backups.append({"firm_id": target["firm_id"], "path": str(snapshot)})
        manifest["backups"] = list(backups)
        manifest["status"] = "backing_up"
        manifest_path = _persist_manifest(backup, run_id, manifest)
    outcome = [
        {"firm_id": target["firm_id"], "status": "up_to_date", "applied_versions": []}
        for target in plan["targets"] if not target["pending_versions"]
    ]
    for target in work_targets:
        firm_id = target["firm_id"]
        path = root / target["database_file"]
        try:
            _secure_regular_file(path, f"Tenant {firm_id}")
            _secure_sidecars(path)
            before = (path.stat().st_dev, path.stat().st_ino)
            if list(before) != target["file_identity"]:
                raise FleetMigrationError("Tenant database file identity changed after backup")
            with closing(sqlite3.connect(path, timeout=30)) as connection:
                connection.row_factory = sqlite3.Row
                connection.execute("PRAGMA foreign_keys=ON")
                if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
                    raise FleetMigrationError("Foreign-key enforcement could not be enabled")
                profile = connection.execute(
                    "SELECT profile FROM database_profile WHERE singleton=1"
                ).fetchone()
                binding = connection.execute(
                    "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
                ).fetchone()
                if profile is None or profile["profile"] != "firm" or binding is None or int(binding["firm_id"]) != firm_id:
                    raise FleetMigrationError("Tenant profile/binding changed after preflight")
                applied = apply_profile_migrations(connection, "firm", migrations_root)
                integrity = connection.execute("PRAGMA integrity_check").fetchone()
                if integrity is None or integrity[0] != "ok":
                    raise FleetMigrationError("Post-migration integrity_check failed")
                if connection.execute("PRAGMA foreign_key_check").fetchall():
                    raise FleetMigrationError("Post-migration foreign_key_check failed")
            after = (path.stat().st_dev, path.stat().st_ino)
            if before != after:
                raise FleetMigrationError("Tenant database file identity changed during migration")
            outcome.append({"firm_id": firm_id, "status": "migrated", "applied_versions": applied})
        except Exception as exc:
            outcome.append({"firm_id": firm_id, "status": "failed", "error": str(exc)})
            manifest["outcome"] = list(outcome)
            manifest["status"] = "stopped_after_failure"
            manifest_path = _persist_manifest(backup, run_id, manifest)
            break
        manifest["outcome"] = list(outcome)
        manifest["status"] = "migrating"
        manifest_path = _persist_manifest(backup, run_id, manifest)
    result = {
        "schema": "tenant-fleet-migration-result/v1",
        "run_id": run_id,
        "preflight": plan,
        "backups": backups,
        "outcome": outcome,
        "manifest_path": manifest_path,
        "stopped_after_failure": any(item["status"] == "failed" for item in outcome),
        "all_targets_migrated": len(outcome) == len(plan["targets"]) and all(
            item["status"] in {"migrated", "up_to_date"} for item in outcome
        ),
    }
    manifest.update(result)
    manifest["status"] = "failed" if result["stopped_after_failure"] else "completed"
    result["manifest_path"] = _persist_manifest(backup, run_id, manifest)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-db", required=True)
    parser.add_argument("--tenant-root", required=True)
    parser.add_argument("--migrations-root", default=str(Path(__file__).resolve().parents[1] / "migrations"))
    parser.add_argument("--backup-dir")
    parser.add_argument("--apply", action="store_true", help="Apply migrations; default is read-only plan mode")
    parser.add_argument("--confirm-workers-stopped", action="store_true",
                        help="Confirm web and background workers are stopped before schema changes")
    args = parser.parse_args(argv)
    try:
        if args.apply:
            if not args.backup_dir:
                raise FleetMigrationError("--backup-dir is required with --apply")
            result = apply_fleet(args.control_db, args.tenant_root, args.migrations_root,
                                 args.backup_dir, confirm_workers_stopped=args.confirm_workers_stopped)
        else:
            result = build_plan(args.control_db, args.tenant_root, args.migrations_root)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0 if not result.get("stopped_after_failure") else 2
    except (FleetMigrationError, OSError, sqlite3.Error, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
