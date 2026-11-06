"""Read-only reconciliation for tenant original-file metadata and local blobs.

This module intentionally reports anomalies instead of deleting or repairing data.
A reviewer must resolve findings under an application-wide write quiescence window.
"""
from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

_OBJECT_ID = re.compile(r"^[0-9a-f]{32}$")
_FIRM_DIR = re.compile(r"^firm-([1-9][0-9]*)$")


@dataclass(frozen=True)
class TenantDatabase:
    """A trusted firm ID and database path resolved from the control-plane catalog."""

    firm_id: int
    path: Path


@dataclass(frozen=True)
class ReconciliationFinding:
    code: str
    firm_id: int | None
    object_id: str | None
    detail: str


@dataclass(frozen=True)
class ReconciliationReport:
    checked_databases: int
    checked_metadata_rows: int
    checked_objects: int
    findings: tuple[ReconciliationFinding, ...]

    @property
    def clean(self) -> bool:
        return not self.findings


def _read_only_connection(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise ValueError("tenant database must be an existing regular non-symlink file")
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            os.close(fd)
            raise ValueError("object is not a regular file")
        with os.fdopen(fd, "rb", closefd=True) as handle:
            while True:
                block = handle.read(1024 * 1024)
                if not block:
                    break
                size += len(block)
                digest.update(block)
    except OSError as exc:
        raise ValueError("object cannot be safely read") from exc
    return digest.hexdigest(), size


def reconcile_original_file_storage(
    object_root: str | Path,
    tenant_databases: Iterable[TenantDatabase],
) -> ReconciliationReport:
    """Compare firm-scoped metadata with object inventory without changing either.

    The caller must supply database paths resolved through the trusted tenant catalog.
    The report includes missing/corrupt objects, staged crash windows, orphaned files,
    unsafe paths, and unexpected files. No automatic deletion or repair is performed.
    """
    raw_root = Path(object_root).expanduser()
    if raw_root.is_symlink():
        raise ValueError("object storage root must not be a symbolic link")
    root = raw_root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError("object storage root must be an existing directory")

    findings: list[ReconciliationFinding] = []
    expected: dict[tuple[int, str, str], tuple[str, int, str]] = {}
    checked_rows = 0
    checked_objects = 0
    databases = list(tenant_databases)
    seen_firms: set[int] = set()

    for tenant in databases:
        if isinstance(tenant.firm_id, bool) or not isinstance(tenant.firm_id, int) or tenant.firm_id <= 0:
            raise ValueError("tenant firm ID must be a positive integer")
        if tenant.firm_id in seen_firms:
            raise ValueError("duplicate tenant firm ID in reconciliation input")
        seen_firms.add(tenant.firm_id)
        connection = _read_only_connection(Path(tenant.path))
        try:
            binding = connection.execute(
                "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
            ).fetchone()
            if binding is None or int(binding["firm_id"]) != tenant.firm_id:
                findings.append(ReconciliationFinding(
                    "tenant_binding_mismatch", tenant.firm_id, None,
                    "database binding does not match the trusted catalog firm ID",
                ))
                continue
            tables = {row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            if "original_file_objects" not in tables:
                findings.append(ReconciliationFinding(
                    "missing_storage_schema", tenant.firm_id, None,
                    "firm database has no original_file_objects table",
                ))
                continue
            rows = connection.execute(
                "SELECT object_id,storage_backend,sha256,byte_size,state,purged_at,purged_by_user_id,purge_reason "
                "FROM original_file_objects ORDER BY object_id"
            ).fetchall()
            checked_rows += len(rows)
            for row in rows:
                object_id = row["object_id"]
                if row["storage_backend"] != "local":
                    findings.append(ReconciliationFinding(
                        "backend_mismatch", tenant.firm_id,
                        str(object_id) if isinstance(object_id, str) else None,
                        "metadata does not identify the local filesystem backend",
                    ))
                    continue
                if not isinstance(object_id, str) or not _OBJECT_ID.fullmatch(object_id):
                    findings.append(ReconciliationFinding(
                        "invalid_object_id", tenant.firm_id, str(object_id),
                        "metadata contains a non-canonical opaque object ID",
                    ))
                    continue
                if row["purged_at"] is not None:
                    if row["purged_by_user_id"] is None or not str(row["purge_reason"] or "").strip():
                        findings.append(ReconciliationFinding(
                            "invalid_purge_tombstone", tenant.firm_id, object_id,
                            "purged metadata is missing its actor or reason",
                        ))
                    # Tombstones deliberately have no retained binary; any remaining
                    # file will be reported as an orphan during the inventory scan.
                    continue
                state = row["state"]
                if state not in {"staged", "ready", "quarantined"}:
                    findings.append(ReconciliationFinding(
                        "invalid_object_state", tenant.firm_id, object_id,
                        "metadata contains an unsupported storage state",
                    ))
                    continue
                expected[(tenant.firm_id, object_id, "blob")] = (
                    str(row["sha256"]), int(row["byte_size"]), state
                )
                if state == "staged":
                    expected[(tenant.firm_id, object_id, "staged")] = (
                        str(row["sha256"]), int(row["byte_size"]), state
                    )
        finally:
            connection.close()

    observed: set[tuple[int, str, str]] = set()
    for directory in root.iterdir():
        match = _FIRM_DIR.fullmatch(directory.name)
        if not match:
            findings.append(ReconciliationFinding(
                "unexpected_root_entry", None, None,
                f"unexpected entry in object root: {directory.name}",
            ))
            continue
        firm_id = int(match.group(1))
        if directory.is_symlink() or not directory.is_dir():
            findings.append(ReconciliationFinding(
                "unsafe_firm_directory", firm_id, None,
                "firm object namespace is not a regular directory",
            ))
            continue
        if firm_id not in seen_firms:
            findings.append(ReconciliationFinding(
                "unknown_firm_namespace", firm_id, None,
                "object namespace has no supplied trusted tenant database",
            ))
        for path in directory.iterdir():
            if path.is_symlink() or not path.is_file():
                findings.append(ReconciliationFinding(
                    "unsafe_object_entry", firm_id, path.name,
                    "object entry is a symlink or is not a regular file",
                ))
                continue
            suffix = ".blob" if path.name.endswith(".blob") else ".staged" if path.name.endswith(".staged") else None
            object_id = path.name[:-len(suffix)] if suffix else path.name
            if suffix is None or not _OBJECT_ID.fullmatch(object_id):
                findings.append(ReconciliationFinding(
                    "unexpected_object_file", firm_id, path.name,
                    "object filename does not match the opaque storage format",
                ))
                continue
            key = (firm_id, object_id, suffix[1:])
            observed.add(key)
            checked_objects += 1
            metadata = expected.get(key)
            if metadata is None:
                findings.append(ReconciliationFinding(
                    "orphaned_object", firm_id, object_id,
                    "object file has no matching metadata in the firm's database",
                ))
                continue
            digest, size, state = metadata
            try:
                actual_digest, actual_size = _hash_file(path)
            except ValueError:
                findings.append(ReconciliationFinding(
                    "unreadable_object", firm_id, object_id,
                    "object could not be read safely for integrity verification",
                ))
                continue
            if actual_digest != digest or actual_size != size:
                findings.append(ReconciliationFinding(
                    "object_integrity_mismatch", firm_id, object_id,
                    "stored bytes do not match metadata SHA-256 and byte size",
                ))
            if suffix == ".staged" and state != "staged":
                findings.append(ReconciliationFinding(
                    "unexpected_staged_copy", firm_id, object_id,
                    "staged bytes remain although metadata is not in staged state",
                ))
            if suffix == ".staged" and state == "staged":
                findings.append(ReconciliationFinding(
                    "staged_upload_requires_review", firm_id, object_id,
                    "staged bytes and staged metadata remain; verify whether upload finalization was interrupted",
                ))
            if suffix == ".blob" and state == "staged":
                findings.append(ReconciliationFinding(
                    "finalized_object_state_not_committed", firm_id, object_id,
                    "final blob exists but metadata still says staged; inspect upload crash window",
                ))

    for (firm_id, object_id, suffix), (_, _, state) in expected.items():
        if (firm_id, object_id, suffix) in observed:
            continue
        if suffix == "staged":
            # A staged record may already have its final blob after a crash between
            # filesystem finalization and the metadata state transition.
            if (firm_id, object_id, "blob") in observed:
                continue
        if suffix == "blob" and state == "staged" and (firm_id, object_id, "staged") in observed:
            continue
        findings.append(ReconciliationFinding(
            "missing_object", firm_id, object_id,
            f"metadata state '{state}' has no expected {suffix} file",
        ))

    findings.sort(key=lambda item: (
        item.firm_id if item.firm_id is not None else 0,
        item.code, item.object_id or "",
    ))
    return ReconciliationReport(
        checked_databases=len(databases),
        checked_metadata_rows=checked_rows,
        checked_objects=checked_objects,
        findings=tuple(findings),
    )
