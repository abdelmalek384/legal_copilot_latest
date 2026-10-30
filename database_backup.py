"""Encrypted, checksummed backup/restore bundles for the separate database architecture.

The caller must quiesce application writes before taking a multi-file snapshot.
Restore always targets a new directory; it never overwrites configured live paths.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from database_runtime import DatabaseRuntime
from original_file_storage import ObjectStorageError
from s3_original_file_storage import S3PrivateObjectStore


class DatabaseBundleError(RuntimeError):
    """Raised when a database bundle cannot be safely created or restored."""


_FORMAT_VERSION = 2
_TENANT_FILENAME = re.compile(r"tenant-(?P<firm_id>[1-9][0-9]*)-(?P<nonce>[0-9a-f]{32})\.sqlite3\Z")
_OBJECT_ID = re.compile(r"^[0-9a-f]{32}\.blob$")
_FIRM_OBJECT_DIR = re.compile(r"^firm-[1-9][0-9]*$")
_MAX_ARCHIVE_BYTES = 8 * 1024 * 1024 * 1024
_MAX_ENTRIES = 2048
# Fernet adds a 57-byte envelope and up to 16 bytes of block padding before base64 encoding.
_MAX_ENCRYPTED_BUNDLE_BYTES = ((_MAX_ARCHIVE_BYTES + 73 + 2) // 3) * 4


def _readonly(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise DatabaseBundleError(f"Required database is missing or is a symlink: {path.name}")
    uri = path.resolve().as_uri() + "?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection
    except sqlite3.Error as exc:
        raise DatabaseBundleError(f"Cannot open database read-only: {path.name}") from exc


def _integrity(connection: sqlite3.Connection, label: str) -> None:
    rows = connection.execute("PRAGMA quick_check").fetchall()
    if len(rows) != 1 or rows[0][0] != "ok":
        raise DatabaseBundleError(f"{label} failed SQLite quick_check")
    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise DatabaseBundleError(f"{label} failed foreign_key_check")


def _has_immutable_trigger(connection: sqlite3.Connection, name: str, table: str, operation: str, message: str) -> bool:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type='trigger' AND name=?", (name,)
    ).fetchone()
    if row is None or not isinstance(row[0], str):
        return False
    sql = " ".join(row[0].lower().split())
    return (
        f"before {operation} on {table}" in sql
        and "raise(abort" in sql
        and message in sql
    )


def _validate_profile(path: Path, expected: str, firm_id: int | None = None) -> None:
    connection = _readonly(path)
    try:
        try:
            row = connection.execute(
                "SELECT profile FROM database_profile WHERE singleton=1"
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseBundleError(f"{path.name} has no database profile marker") from exc
        if row is None or row["profile"] != expected:
            raise DatabaseBundleError(f"{path.name} is not bound to the {expected} profile")
        for operation in ("update", "delete"):
            if not _has_immutable_trigger(
                connection, f"database_profile_no_{operation}", "database_profile",
                operation, "database profile binding is immutable",
            ):
                raise DatabaseBundleError(f"{path.name} has no immutable profile guard for {operation}")
        _integrity(connection, path.name)
        if expected == "control_plane":
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            if not {"firms", "tenant_database_catalog", "users", "firm_memberships"}.issubset(tables):
                raise DatabaseBundleError("Control plane is missing required identity/catalog tables")
        if expected == "firm":
            rows = connection.execute(
                "SELECT singleton,firm_id FROM tenant_database_binding"
            ).fetchall()
            if len(rows) != 1 or rows[0]["singleton"] != 1 or rows[0]["firm_id"] != firm_id:
                raise DatabaseBundleError(f"{path.name} is not immutably bound to firm {firm_id}")
            for operation in ("update", "delete"):
                if not _has_immutable_trigger(
                    connection, f"tenant_database_binding_no_{operation}",
                    "tenant_database_binding", operation,
                    "tenant database firm binding is immutable",
                ):
                    raise DatabaseBundleError(f"{path.name} has no immutable firm binding guard for {operation}")
    finally:
        connection.close()


def _safe_tenant_path(root: Path, firm_id: int, filename: str) -> Path:
    match = _TENANT_FILENAME.fullmatch(filename or "")
    if not match or int(match.group("firm_id")) != firm_id:
        raise DatabaseBundleError(f"Invalid tenant catalog filename for firm {firm_id}")
    if root.is_symlink() or not root.is_dir():
        raise DatabaseBundleError("Tenant storage root must be a real directory")
    resolved_root = root.resolve()
    candidate = resolved_root / filename
    if candidate.is_symlink() or not candidate.is_file():
        raise DatabaseBundleError(f"Tenant database is missing or is a symlink for firm {firm_id}")
    resolved = candidate.resolve()
    if resolved.parent != resolved_root:
        raise DatabaseBundleError("Tenant database path escapes the configured storage root")
    return resolved


def _snapshot(source_path: Path, destination: Path, profile: str, firm_id: int | None = None) -> None:
    _validate_profile(source_path, profile, firm_id)
    source = _readonly(source_path)
    target = None
    try:
        target = sqlite3.connect(str(destination), timeout=30)
        source.backup(target, pages=256, sleep=0.05)
        target.commit()
        # SQLite backup copies the database header, including WAL mode. Backup
        # archives must contain a single self-contained DB file, not transient
        # -wal/-shm sidecars whose contents could be omitted or inconsistent.
        journal_mode = target.execute("PRAGMA journal_mode=DELETE").fetchone()
        if journal_mode is None or str(journal_mode[0]).lower() != "delete":
            raise DatabaseBundleError("Could not finalize a standalone database snapshot")
    except sqlite3.Error as exc:
        raise DatabaseBundleError(f"Could not snapshot {source_path.name}") from exc
    finally:
        source.close()
        if target is not None:
            target.close()
    _validate_profile(destination, profile, firm_id)
    try:
        os.chmod(destination, 0o600)
    except OSError:
        if os.name == "posix":
            raise DatabaseBundleError(f"Could not restrict permissions on {destination.name}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _object_root_path(value: str | Path, tenant_root: Path, control_path: Path, corpus_path: Path) -> Path:
    raw = Path(value).expanduser()
    if raw.is_symlink():
        raise DatabaseBundleError("Original-object storage root must not be a symlink")
    resolved = raw.resolve()
    protected = [tenant_root.resolve(), control_path.resolve(), corpus_path.resolve()]
    for path in protected:
        if resolved == path or resolved in path.parents or path in resolved.parents:
            raise DatabaseBundleError("Original-object storage must be separate from database storage")
    if raw.exists() and (not raw.is_dir() or raw.is_symlink()):
        raise DatabaseBundleError("Original-object storage root must be a real directory")
    return resolved


def _copy_original_objects(
    tenant_snapshot: Path, firm_id: int, object_root: Path, payload: Path
) -> set[str]:
    db = _readonly(tenant_snapshot)
    try:
        tables = {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "original_file_objects" not in tables:
            return set()
        columns = {
            row[1] for row in db.execute("PRAGMA table_info(original_file_objects)")
        }
        has_purged_at = "purged_at" in columns
        select = "object_id,firm_id,storage_backend,sha256,byte_size,state"
        if has_purged_at:
            select += ",purged_at"
        rows = db.execute(
            f"SELECT {select} FROM original_file_objects ORDER BY object_id"
        ).fetchall()
    finally:
        db.close()

    # A purged row is an intentional database tombstone, not a live object.
    # Keep the metadata in the database snapshot but never require or archive
    # the physically erased original bytes.
    active_rows = [
        row for row in rows
        if not (has_purged_at and row["purged_at"] is not None)
    ]
    expected: set[str] = set()
    namespace = object_root / ("firm-" + str(firm_id))
    if namespace.is_symlink():
        raise DatabaseBundleError(f"Original-object namespace is a symlink for firm {firm_id}")
    if active_rows and (not object_root.is_dir() or not namespace.is_dir()):
        raise DatabaseBundleError(f"Original-object storage is missing for firm {firm_id}")
    for row in active_rows:
        object_id = row["object_id"]
        if row["firm_id"] != firm_id or row["storage_backend"] != "local" or not isinstance(object_id, str) or not re.fullmatch(r"[0-9a-f]{32}", object_id):
            raise DatabaseBundleError(f"Original-object metadata is invalid for local storage in firm {firm_id}")
        if row["state"] not in {"ready", "quarantined"}:
            raise DatabaseBundleError(f"Firm {firm_id} has unfinished original-object metadata; reconcile before backup")
        source = namespace / (object_id + ".blob")
        if source.is_symlink() or not source.is_file():
            raise DatabaseBundleError(f"Original object is missing for firm {firm_id}")
        if source.stat().st_size != int(row["byte_size"]) or _sha256(source) != row["sha256"]:
            raise DatabaseBundleError(f"Original-object integrity check failed for firm {firm_id}")
        relative = f"objects/firm-{firm_id}/{object_id}.blob"
        target = payload / relative
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(source, target)
        try:
            os.chmod(target, 0o600)
        except OSError:
            if os.name == "posix":
                raise DatabaseBundleError("Could not restrict permissions on backed-up original object")
        expected.add(f"firm-{firm_id}/{object_id}.blob")
    return expected


def _copy_s3_original_objects(
    tenant_snapshot: Path, firm_id: int, store: S3PrivateObjectStore, payload: Path
) -> set[str]:
    db = _readonly(tenant_snapshot)
    try:
        tables = {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "original_file_objects" not in tables:
            return set()
        columns = {row[1] for row in db.execute("PRAGMA table_info(original_file_objects)")}
        required = {"object_id", "firm_id", "storage_backend", "sha256", "byte_size", "state"}
        if not required.issubset(columns):
            raise DatabaseBundleError(f"Tenant {firm_id} has incomplete original-object metadata")
        has_purged_at = "purged_at" in columns
        select = "object_id,firm_id,storage_backend,sha256,byte_size,state"
        if has_purged_at:
            select += ",purged_at"
        rows = db.execute(f"SELECT {select} FROM original_file_objects ORDER BY object_id").fetchall()
    finally:
        db.close()

    expected: set[str] = set()
    for row in rows:
        object_id = row["object_id"]
        if row["firm_id"] != firm_id or row["storage_backend"] != "s3" or not isinstance(object_id, str) or not re.fullmatch(r"[0-9a-f]{32}", object_id):
            raise DatabaseBundleError(f"Original-object metadata is invalid for firm {firm_id}")
        if has_purged_at and row["purged_at"] is not None:
            continue
        if row["state"] not in {"ready", "quarantined"}:
            raise DatabaseBundleError(f"Firm {firm_id} has unfinished original-object metadata; reconcile before backup")
        digest, size = row["sha256"], int(row["byte_size"])
        try:
            staged, finalized = store.object_presence(firm_id, object_id)
            valid = not staged and finalized and store.verify(
                firm_id, object_id, expected_sha256=digest, expected_size=size
            )
            if not valid:
                raise DatabaseBundleError(f"S3 original-object integrity check failed for firm {firm_id}")
            with store.open(firm_id, object_id) as source:
                relative = f"objects/firm-{firm_id}/{object_id}.blob"
                target = payload / relative
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                digest_check = hashlib.sha256()
                size_check = 0
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                fd = os.open(target, flags, 0o600)
                try:
                    with os.fdopen(fd, "wb", closefd=True) as output:
                        while True:
                            block = source.read(1024 * 1024)
                            if not block:
                                break
                            output.write(block)
                            digest_check.update(block)
                            size_check += len(block)
                except Exception:
                    target.unlink(missing_ok=True)
                    raise
                if size_check != size or digest_check.hexdigest() != digest:
                    target.unlink(missing_ok=True)
                    raise DatabaseBundleError(f"S3 original-object changed during backup for firm {firm_id}")
        except (ObjectStorageError, ValueError) as exc:
            raise DatabaseBundleError(f"S3 original-object could not be safely backed up for firm {firm_id}") from exc
        expected.add(f"firm-{firm_id}/{object_id}.blob")
    return expected


def _scan_s3_original_object_inventory(store: S3PrivateObjectStore) -> set[str]:
    found: set[str] = set()
    for key in store.list_object_keys():
        match = re.fullmatch(r"firms/([1-9][0-9]*)/originals/([0-9a-f]{32})\.(staged|blob)", key)
        if not match or match.group(3) != "blob":
            raise DatabaseBundleError("S3 original-object storage contains staged or unexpected objects")
        found.add(f"firm-{match.group(1)}/{match.group(2)}.blob")
    return found


def _scan_original_object_root(object_root: Path) -> set[str]:
    if not object_root.exists():
        return set()
    if object_root.is_symlink() or not object_root.is_dir():
        raise DatabaseBundleError("Original-object storage root must be a real directory")
    found: set[str] = set()
    for namespace in object_root.iterdir():
        if namespace.is_symlink() or not namespace.is_dir() or not _FIRM_OBJECT_DIR.fullmatch(namespace.name):
            raise DatabaseBundleError("Original-object storage contains an unexpected entry")
        for item in namespace.iterdir():
            if item.is_symlink() or not item.is_file() or not _OBJECT_ID.fullmatch(item.name):
                raise DatabaseBundleError("Original-object storage contains an unfinished or unexpected object")
            found.add(f"{namespace.name}/{item.name}")
    return found


def _validate_original_object_inventory(
    extracted: Path, files: dict, tenant_records: list[dict]
) -> set[str]:
    expected: set[str] = set()
    for record in tenant_records:
        relative = record.get("archive_path")
        if not relative:
            continue
        firm_id = int(record["firm_id"])
        db = _readonly(extracted / relative)
        try:
            tables = {row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            if "original_file_objects" not in tables:
                continue
            rows = db.execute(
                "SELECT object_id,firm_id,sha256,byte_size,state,purged_at,"
                "purged_by_user_id,purge_reason FROM original_file_objects"
            ).fetchall()
            for row in rows:
                object_id = row["object_id"]
                if row["firm_id"] != firm_id or not isinstance(object_id, str) or not re.fullmatch(r"[0-9a-f]{32}", object_id):
                    raise DatabaseBundleError(f"Original-object metadata is invalid for firm {firm_id}")
                if row["state"] not in {"ready", "quarantined"}:
                    raise DatabaseBundleError(f"Firm {firm_id} has unfinished original-object metadata")
                if row["purged_at"] is not None:
                    if row["purged_by_user_id"] is None or not str(row["purge_reason"] or "").strip():
                        raise DatabaseBundleError(f"Firm {firm_id} has an invalid purge tombstone")
                    continue
                object_relative = f"objects/firm-{firm_id}/{object_id}.blob"
                if files.get(object_relative) is None:
                    raise DatabaseBundleError(f"Backup omits original object for firm {firm_id}")
                object_path = extracted / object_relative
                if object_path.is_symlink() or not object_path.is_file():
                    raise DatabaseBundleError("Backup original-object path is unsafe")
                if object_path.stat().st_size != int(row["byte_size"]) or _sha256(object_path) != row["sha256"]:
                    raise DatabaseBundleError(f"Backup original-object integrity check failed for firm {firm_id}")
                expected.add(object_relative)
        finally:
            db.close()
    actual = {name for name in files if name.startswith("objects/")}
    if actual != expected:
        raise DatabaseBundleError("Backup original-object inventory does not match tenant metadata")
    return expected


def create_backup_bundle(
    runtime: DatabaseRuntime,
    cipher: Fernet,
    output_dir: str | Path,
    *,
    keep: int = 14,
    quiesced: bool = False,
    object_storage_root: str | Path | None = None,
    object_store: S3PrivateObjectStore | None = None,
) -> Path:
    """Create an encrypted bundle from consistent per-file SQLite snapshots.

    quiesced=True is an operator assertion that application writes are paused.
    SQLite snapshots are consistent per file, not a cross-file atomic transaction,
    so a live multi-file backup is rejected by default.
    """
    if not quiesced:
        raise DatabaseBundleError("Pause application writes and pass quiesced=True before bundling databases")
    if keep < 1:
        raise ValueError("keep must be at least 1")
    control_path = runtime.paths.control_plane
    corpus_path = runtime.paths.legal_corpus
    tenant_root = runtime.paths.tenant_root
    if tenant_root.is_symlink() or not tenant_root.is_dir():
        raise DatabaseBundleError("Tenant storage root must be a real directory")
    backend = os.environ.get("COPILOT_OBJECT_STORAGE_BACKEND", "local").strip().lower()
    production = os.environ.get("COPILOT_ENV", "").strip().lower() in {"prod", "production"}
    object_root: Path | None = None
    if backend == "s3":
        if object_storage_root is not None:
            raise DatabaseBundleError("object_storage_root cannot be used with the S3 backend")
        if object_store is None:
            bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
            region = os.environ.get("COPILOT_S3_REGION", "").strip()
            kms_key_id = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
            endpoint = os.environ.get("COPILOT_S3_ENDPOINT_URL", "").strip() or None
            if not bucket or not region or not kms_key_id:
                raise DatabaseBundleError("S3 bucket, region, and KMS key ID are required for backup")
            try:
                import boto3
                object_store = S3PrivateObjectStore(
                    boto3.client("s3", region_name=region, endpoint_url=endpoint),
                    bucket=bucket, kms_key_id=kms_key_id,
                    kms_client=boto3.client("kms", region_name=region),
                )
            except ImportError as exc:
                raise DatabaseBundleError("AWS SDK is not installed") from exc
        if not isinstance(object_store, S3PrivateObjectStore):
            raise DatabaseBundleError("S3 backup requires the reviewed S3 object-store adapter")
    elif backend == "local":
        if production:
            raise DatabaseBundleError("production backup requires S3 original-object storage")
        if object_store is not None:
            raise DatabaseBundleError("object_store is only supported with the S3 backend")
        configured_object_root = object_storage_root
        if configured_object_root is None:
            configured_object_root = os.environ.get("COPILOT_OBJECT_STORAGE_ROOT", "").strip() or (tenant_root.parent / "objects")
        object_root = _object_root_path(configured_object_root, tenant_root, control_path, corpus_path)
    else:
        raise DatabaseBundleError("COPILOT_OBJECT_STORAGE_BACKEND must be local or s3")
    destination = Path(output_dir).expanduser()
    if destination.is_symlink():
        raise DatabaseBundleError("Backup destination must not be a symlink")
    destination.mkdir(parents=True, exist_ok=True)
    destination = destination.resolve()
    if not destination.is_dir():
        raise DatabaseBundleError("Backup destination must be a directory")
    resolved_tenant_root = tenant_root.resolve()
    protected_roots = [(resolved_tenant_root, "tenant storage")]
    if object_root is not None:
        protected_roots.append((object_root, "original-object storage"))
    for protected_root, label in protected_roots:
        try:
            destination.relative_to(protected_root)
            raise DatabaseBundleError(f"Backup output must be outside {label}")
        except ValueError:
            pass
        try:
            protected_root.relative_to(destination)
            raise DatabaseBundleError(f"Backup output must not contain {label}")
        except ValueError:
            pass

    with tempfile.TemporaryDirectory(prefix=".dbbundle-stage-", dir=destination) as tmp:
        stage = Path(tmp)
        payload = stage / "payload"
        payload.mkdir()
        control_snapshot = payload / "control_plane.sqlite3"
        corpus_snapshot = payload / "legal_corpus.sqlite3"
        _snapshot(control_path, control_snapshot, "control_plane")
        _snapshot(corpus_path, corpus_snapshot, "legal_corpus")
        expected_objects: set[str] = set()

        control = _readonly(control_snapshot)
        try:
            catalog_rows = control.execute(
                "SELECT firm_id,database_file,status FROM tenant_database_catalog ORDER BY firm_id"
            ).fetchall()
            firms = {
                row["id"]: row["status"] for row in control.execute("SELECT id,status FROM firms")
            }
            if control.execute("PRAGMA foreign_key_check(tenant_database_catalog)").fetchall():
                raise DatabaseBundleError("Tenant catalog has invalid firm ownership references")
            catalog_by_firm = {int(row["firm_id"]): row for row in catalog_rows}
            for firm_id, firm_status in firms.items():
                if firm_status == "active":
                    catalog_row = catalog_by_firm.get(int(firm_id))
                    if catalog_row is None or catalog_row["status"] != "provisioned" or not catalog_row["database_file"]:
                        raise DatabaseBundleError(f"Active firm {firm_id} has no provisioned database")
            referenced_files = {
                row["database_file"] for row in catalog_rows if row["database_file"]
            }
            actual_files = {
                path.name for path in tenant_root.iterdir()
                if path.name.startswith("tenant-") and path.name.endswith(".sqlite3")
            }
            if actual_files != referenced_files:
                raise DatabaseBundleError("Tenant storage contains missing or unreferenced database files")
            tenant_records = []
            for row in catalog_rows:
                firm_id = int(row["firm_id"])
                filename = row["database_file"]
                status = row["status"]
                if status == "provisioning":
                    raise DatabaseBundleError(f"Firm {firm_id} is mid-provisioning; retry after recovery")
                if firm_id not in firms:
                    raise DatabaseBundleError(f"Tenant catalog references missing firm {firm_id}")
                record: dict[str, Any] = {
                    "firm_id": firm_id, "database_file": filename, "status": status,
                    "firm_status": firms[firm_id], "archive_path": None,
                }
                if filename:
                    source_path = _safe_tenant_path(tenant_root, firm_id, filename)
                    relative = f"tenants/{filename}"
                    target_path = payload / relative
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    _snapshot(source_path, target_path, "firm", firm_id)
                    if backend == "s3":
                        expected_objects.update(_copy_s3_original_objects(target_path, firm_id, object_store, payload))
                    else:
                        expected_objects.update(_copy_original_objects(target_path, firm_id, object_root, payload))
                    record["archive_path"] = relative
                elif status == "provisioned":
                    raise DatabaseBundleError(f"Provisioned firm {firm_id} has no database file")
                tenant_records.append(record)
        finally:
            control.close()

        actual_objects = (
            _scan_s3_original_object_inventory(object_store)
            if backend == "s3"
            else _scan_original_object_root(object_root)
        )
        if actual_objects != expected_objects:
            raise DatabaseBundleError("Original-object storage contains missing or unreferenced objects; reconcile before backup")

        file_hashes = {}
        for path in sorted(p for p in payload.rglob("*") if p.is_file()):
            file_hashes[path.relative_to(payload).as_posix()] = _sha256(path)
        manifest = {
            "format_version": _FORMAT_VERSION,
            "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "profiles": {
                "control_plane": "control_plane.sqlite3",
                "legal_corpus": "legal_corpus.sqlite3",
                "tenant_root": "tenants/",
                "object_storage": "objects/",
            },
            "tenants": tenant_records,
            "files": file_hashes,
        }
        archive_path = stage / "bundle.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode("utf-8"))
            for relative in sorted(file_hashes):
                archive.write(payload / relative, arcname=relative)

        if archive_path.stat().st_size > _MAX_ARCHIVE_BYTES:
            raise DatabaseBundleError("Backup bundle exceeds the supported expanded size")
        encrypted = cipher.encrypt(archive_path.read_bytes())
        final_path = destination / f"tenancy-{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns()}.dbbundle.enc"
        fd, temp_path = tempfile.mkstemp(prefix=".dbbundle-", suffix=".tmp", dir=destination)
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(encrypted)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp_path, final_path)
            try:
                os.chmod(final_path, 0o600)
            except OSError:
                if os.name == "posix":
                    raise DatabaseBundleError("Could not restrict permissions on encrypted backup")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    old = sorted(
        destination.glob("tenancy-*.dbbundle.enc"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    for obsolete in old[keep:]:
        obsolete.unlink()
    return final_path


def _safe_archive_members(archive: zipfile.ZipFile) -> set[str]:
    infos = archive.infolist()
    if len(infos) > _MAX_ENTRIES:
        raise DatabaseBundleError("Backup bundle contains too many entries")
    total = 0
    names = set()
    for info in infos:
        name = PurePosixPath(info.filename)
        if name.is_absolute() or ".." in name.parts or not info.filename or "\\" in info.filename:
            raise DatabaseBundleError("Backup bundle contains an unsafe path")
        mode = (info.external_attr >> 16) & 0o170000
        if mode == 0o120000:
            raise DatabaseBundleError("Backup bundle may not contain symbolic links")
        if info.filename in names:
            raise DatabaseBundleError("Backup bundle contains duplicate paths")
        names.add(info.filename)
        total += info.file_size
        if total > _MAX_ARCHIVE_BYTES:
            raise DatabaseBundleError("Backup bundle exceeds the supported expanded size")
    return names


def verify_backup_bundle(bundle_path: str | Path, cipher: Fernet) -> dict[str, Any]:
    """Verify an encrypted bundle in protected temporary storage, without changing live paths.

    This temporarily creates plaintext SQLite files. Run only on a trusted host with
    protected temporary storage; deletion is not guaranteed secure erasure on SSDs
    or copy-on-write filesystems.
    """
    import tempfile

    with tempfile.TemporaryDirectory(prefix="legal-copilot-bundle-verify-") as temp_dir:
        temp_root = Path(temp_dir)
        if os.name == "posix":
            try:
                os.chmod(temp_root, 0o700)
            except OSError as exc:
                raise DatabaseBundleError("Could not restrict temporary verification directory permissions") from exc
        destination = temp_root / "verified"
        restored = restore_backup_bundle(bundle_path, cipher, destination)
        for label, path in (("control-plane", restored["control_plane"]),
                             ("legal-corpus", restored["legal_corpus"])):
            connection = _readonly(path)
            try:
                _integrity(connection, label)
            finally:
                connection.close()
        tenant_paths = sorted(restored["tenant_root"].glob("tenant-*.sqlite3"))
        for path in tenant_paths:
            connection = _readonly(path)
            try:
                _integrity(connection, path.name)
            finally:
                connection.close()
        return {
            "verified": True,
            "format_version": _FORMAT_VERSION,
            "tenant_database_count": len(tenant_paths),
            "tenant_firm_ids": sorted(
                int(_TENANT_FILENAME.fullmatch(path.name).group("firm_id"))
                for path in tenant_paths
                if _TENANT_FILENAME.fullmatch(path.name) is not None
            ),
            "original_object_count": len(list(restored["object_storage"].rglob("*.blob"))),
            "original_objects_verified": True,
            "plaintext_retained": False,
            "warning": "Verification used temporary plaintext database files; deletion is not guaranteed secure erasure.",
        }


def _read_encrypted_backup(path_value: str | Path) -> bytes:
    """Read a bounded regular backup file without following links or blocking on FIFOs."""
    path = Path(path_value).expanduser()
    if path.is_symlink():
        raise DatabaseBundleError("Backup input must not be a symlink")
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(path, flags)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise DatabaseBundleError("Backup input must be a regular file")
        if metadata.st_size > _MAX_ENCRYPTED_BUNDLE_BYTES:
            raise DatabaseBundleError("Encrypted backup exceeds the supported size limit")
        stream = os.fdopen(descriptor, "rb")
        descriptor = None
        with stream:
            data = stream.read(_MAX_ENCRYPTED_BUNDLE_BYTES + 1)
        if len(data) > _MAX_ENCRYPTED_BUNDLE_BYTES:
            raise DatabaseBundleError("Encrypted backup exceeds the supported size limit")
        return data
    except DatabaseBundleError:
        raise
    except OSError as exc:
        raise DatabaseBundleError("Backup input could not be read safely") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def restore_backup_bundle(
    backup_file: str | Path,
    cipher: Fernet,
    target_root: str | Path,
) -> dict[str, Path]:
    """Restore a verified bundle into a new directory without overwriting live files."""
    destination = Path(target_root).expanduser()
    if destination.is_symlink() or destination.exists():
        raise DatabaseBundleError("Restore target must not exist; choose a new destination path")
    parent = destination.parent
    if parent.is_symlink() or not parent.is_dir():
        raise DatabaseBundleError("Restore target's parent directory must already exist")
    destination = destination.resolve()
    try:
        encrypted = _read_encrypted_backup(backup_file)
        plaintext = cipher.decrypt(encrypted)
    except DatabaseBundleError:
        raise
    except (OSError, InvalidToken, ValueError) as exc:
        raise DatabaseBundleError("Backup bundle could not be authenticated or decrypted") from exc

    with tempfile.TemporaryDirectory(prefix=".dbbundle-restore-", dir=parent) as tmp:
        stage = Path(tmp)
        if len(plaintext) > _MAX_ARCHIVE_BYTES:
            raise DatabaseBundleError("Backup bundle exceeds the supported expanded size")
        archive_path = stage / "bundle.zip"
        archive_path.write_bytes(plaintext)
        extracted = stage / "extracted"
        extracted.mkdir()
        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                _safe_archive_members(archive)
                names = set(archive.namelist())
                if "manifest.json" not in names:
                    raise DatabaseBundleError("Backup bundle is missing its manifest")
                archive.extractall(extracted)
        except (zipfile.BadZipFile, OSError) as exc:
            raise DatabaseBundleError("Backup bundle is not a valid archive") from exc

        try:
            manifest = json.loads((extracted / "manifest.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DatabaseBundleError("Backup bundle manifest is invalid") from exc
        if not isinstance(manifest, dict) or manifest.get("format_version") != _FORMAT_VERSION:
            raise DatabaseBundleError("Unsupported or malformed backup bundle format")
        if manifest.get("profiles") != {
            "control_plane": "control_plane.sqlite3",
            "legal_corpus": "legal_corpus.sqlite3",
            "tenant_root": "tenants/",
            "object_storage": "objects/",
        }:
            raise DatabaseBundleError("Backup bundle profile inventory is invalid")
        files = manifest.get("files")
        if not isinstance(files, dict) or not files:
            raise DatabaseBundleError("Backup bundle manifest has no file checksums")
        expected_names = set(files) | {"manifest.json"}
        archive_names = {p.relative_to(extracted).as_posix() for p in extracted.rglob("*") if p.is_file()}
        if archive_names != expected_names:
            raise DatabaseBundleError("Backup bundle file inventory does not match its manifest")
        for relative in files:
            if relative in {"control_plane.sqlite3", "legal_corpus.sqlite3"}:
                continue
            parts = PurePosixPath(relative).parts
            if len(parts) == 2 and parts[0] == "tenants" and _TENANT_FILENAME.fullmatch(parts[1]):
                continue
            if (len(parts) == 3 and parts[0] == "objects"
                    and _FIRM_OBJECT_DIR.fullmatch(parts[1]) and _OBJECT_ID.fullmatch(parts[2])):
                continue
            raise DatabaseBundleError("Backup bundle contains an unexpected database or object path")
        for relative, expected_hash in files.items():
            if not isinstance(relative, str) or not isinstance(expected_hash, str):
                raise DatabaseBundleError("Backup bundle checksum entry is malformed")
            candidate = extracted / relative
            if candidate.is_symlink() or not candidate.is_file() or _sha256(candidate) != expected_hash:
                raise DatabaseBundleError(f"Backup bundle checksum failed for {relative}")

        control_file = extracted / "control_plane.sqlite3"
        corpus_file = extracted / "legal_corpus.sqlite3"
        if files.get("control_plane.sqlite3") is None or files.get("legal_corpus.sqlite3") is None:
            raise DatabaseBundleError("Backup bundle must contain control-plane and legal-corpus databases")
        _validate_profile(control_file, "control_plane")
        _validate_profile(corpus_file, "legal_corpus")

        tenant_records = manifest.get("tenants")
        if not isinstance(tenant_records, list):
            raise DatabaseBundleError("Backup bundle tenant inventory is invalid")
        control = _readonly(control_file)
        try:
            catalog = {
                (int(row["firm_id"]), row["database_file"], row["status"])
                for row in control.execute(
                    "SELECT firm_id,database_file,status FROM tenant_database_catalog"
                ).fetchall()
            }
            listed = {
                (int(row["firm_id"]), row.get("database_file"), row.get("status"))
                for row in tenant_records
            }
            if catalog != listed:
                raise DatabaseBundleError("Manifest tenant catalog does not match the control-plane database")
            firm_statuses = {
                int(row["id"]): row["status"]
                for row in control.execute("SELECT id,status FROM firms").fetchall()
            }
            for firm_id, status in firm_statuses.items():
                if status == "active":
                    catalog_row = next((item for item in tenant_records if int(item["firm_id"]) == firm_id), None)
                    if catalog_row is None or catalog_row.get("status") != "provisioned" or not catalog_row.get("database_file"):
                        raise DatabaseBundleError(f"Active firm {firm_id} has no provisioned database in the bundle")
            if control.execute("PRAGMA foreign_key_check").fetchall():
                raise DatabaseBundleError("Restored control-plane database has foreign-key violations")
            if control.execute("PRAGMA foreign_key_check(tenant_database_catalog)").fetchall():
                raise DatabaseBundleError("Restored control-plane tenant catalog has invalid ownership references")
        finally:
            control.close()

        for record in tenant_records:
            firm_id = int(record["firm_id"])
            relative = record.get("archive_path")
            filename = record.get("database_file")
            if relative is None:
                if filename and record.get("status") == "provisioned":
                    raise DatabaseBundleError(f"Manifest omits provisioned database for firm {firm_id}")
                continue
            if relative != f"tenants/{filename}" or files.get(relative) is None:
                raise DatabaseBundleError(f"Manifest has an invalid database path for firm {firm_id}")
            _validate_profile(extracted / relative, "firm", firm_id)

        _validate_original_object_inventory(extracted, files, tenant_records)

        staged_root = stage / "restored"
        staged_root.mkdir(mode=0o700)
        (staged_root / "tenants").mkdir(mode=0o700)
        (staged_root / "objects").mkdir(mode=0o700)
        shutil.copyfile(control_file, staged_root / "control_plane.sqlite3")
        shutil.copyfile(corpus_file, staged_root / "legal_corpus.sqlite3")
        for record in tenant_records:
            relative = record.get("archive_path")
            if relative:
                shutil.copyfile(extracted / relative, staged_root / relative)
        for relative in files:
            if relative.startswith("objects/"):
                target = staged_root / relative
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                shutil.copyfile(extracted / relative, target)
        # Restored tenant files must satisfy the runtime's concurrency
        # contract before they are made available to the application.
        for database_path in staged_root.rglob("*.sqlite3"):
            connection = None
            try:
                connection = sqlite3.connect(str(database_path), timeout=30)
                mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()
                if mode is None or str(mode[0]).lower() != "wal":
                    raise DatabaseBundleError(
                        f"Could not enable WAL on restored database {database_path.name}"
                    )
            except sqlite3.Error as exc:
                raise DatabaseBundleError(
                    f"Could not initialize restored database {database_path.name}"
                ) from exc
            finally:
                if connection is not None:
                    connection.close()

        for path in staged_root.rglob("*"):
            if not path.is_file():
                continue
            try:
                os.chmod(path, 0o600)
            except OSError:
                if os.name == "posix":
                    raise DatabaseBundleError(f"Could not restrict permissions on restored file {path.name}")
        for directory in [staged_root / "objects", *[p for p in (staged_root / "objects").rglob("*") if p.is_dir()]]:
            try:
                os.chmod(directory, 0o700)
            except OSError:
                if os.name == "posix":
                    raise DatabaseBundleError("Could not restrict permissions on restored object directory")
        os.replace(staged_root, destination)

    return {
        "root": destination,
        "control_plane": destination / "control_plane.sqlite3",
        "tenant_root": destination / "tenants",
        "legal_corpus": destination / "legal_corpus.sqlite3",
        "object_storage": destination / "objects",
    }
