"""Read-only reconciliation of S3 original-object inventory and firm metadata."""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Iterable

from original_file_reconciliation import ReconciliationFinding, ReconciliationReport, TenantDatabase
from original_file_storage import ObjectStorageError
from s3_original_file_storage import S3PrivateObjectStore

_OBJECT_ID = re.compile(r"^[0-9a-f]{32}$")
_KEY = re.compile(r"^firms/([1-9][0-9]*)/originals/([0-9a-f]{32})\.(staged|blob)$")


def _readonly(path: Path) -> sqlite3.Connection:
    if path.is_symlink() or not path.is_file():
        raise ValueError("tenant database must be an existing regular non-symlink file")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def reconcile_s3_original_file_storage(
    store: S3PrivateObjectStore, tenant_databases: Iterable[TenantDatabase]
) -> ReconciliationReport:
    """Compare every S3 object under firms/ with trusted firm DB metadata; never mutate."""
    findings: list[ReconciliationFinding] = []
    expected: dict[tuple[int, str], tuple[str, int, str, str | None]] = {}
    checked_rows = 0
    checked_objects = 0
    databases = list(tenant_databases)
    seen_firms: set[int] = set()

    for tenant in databases:
        if isinstance(tenant.firm_id, bool) or not isinstance(tenant.firm_id, int) or tenant.firm_id <= 0:
            raise ValueError("tenant firm ID must be a positive integer")
        if tenant.firm_id in seen_firms:
            raise ValueError("duplicate tenant firm ID")
        seen_firms.add(tenant.firm_id)
        db = _readonly(tenant.path)
        try:
            binding = db.execute(
                "SELECT firm_id FROM tenant_database_binding WHERE singleton=1"
            ).fetchone()
            if binding is None or int(binding["firm_id"]) != tenant.firm_id:
                raise ValueError("tenant database binding does not match trusted catalog")
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "original_file_objects" not in tables:
                continue
            rows = db.execute(
                "SELECT object_id,firm_id,storage_backend,sha256,byte_size,state,purged_at "
                "FROM original_file_objects ORDER BY object_id"
            ).fetchall()
            for row in rows:
                checked_rows += 1
                object_id = row["object_id"]
                if int(row["firm_id"]) != tenant.firm_id or not isinstance(object_id, str) or not _OBJECT_ID.fullmatch(object_id):
                    findings.append(ReconciliationFinding("invalid_metadata_binding", tenant.firm_id, str(object_id), "object metadata does not match trusted firm context"))
                    continue
                if row["storage_backend"] != "s3":
                    findings.append(ReconciliationFinding("backend_mismatch", tenant.firm_id, object_id, "metadata does not identify the S3 backend"))
                    continue
                if not re.fullmatch(r"[0-9a-f]{64}", str(row["sha256"])) or int(row["byte_size"]) < 0:
                    findings.append(ReconciliationFinding("invalid_integrity_metadata", tenant.firm_id, object_id, "digest or size metadata is invalid"))
                    continue
                expected[(tenant.firm_id, object_id)] = (
                    row["sha256"], int(row["byte_size"]), row["state"], row["purged_at"]
                )
        finally:
            db.close()

    inventory = store.list_object_keys()
    observed: set[tuple[int, str, str]] = set()
    for key in inventory:
        match = _KEY.fullmatch(key)
        if not match:
            findings.append(ReconciliationFinding("unexpected_object_key", None, None, "unexpected key exists under the reserved firms/ namespace"))
            continue
        firm_id, object_id, state = int(match.group(1)), match.group(2), match.group(3)
        observed.add((firm_id, object_id, state))
        record = expected.get((firm_id, object_id))
        if record is None or record[3] is not None:
            findings.append(ReconciliationFinding("orphaned_object", firm_id, object_id, "S3 object has no live metadata row"))
            continue
        digest, size, metadata_state, _ = record
        if state == "staged":
            # A staged key is always a crash-window finding, even when its bytes are valid.
            try:
                valid = store.verify_staged(firm_id, object_id, expected_sha256=digest, expected_size=size)
            except (ObjectStorageError, ValueError):
                valid = False
            findings.append(ReconciliationFinding(
                "staged_object_present", firm_id, object_id,
                "staged bytes match metadata and require operator recovery" if valid else "staged object is missing or fails digest/size verification",
            ))
        else:
            checked_objects += 1
            try:
                valid = store.verify(firm_id, object_id, expected_sha256=digest, expected_size=size)
            except (ObjectStorageError, ValueError):
                valid = False
            if not valid:
                findings.append(ReconciliationFinding("object_integrity_mismatch", firm_id, object_id, "finalized object is missing or fails digest/size verification"))
            elif metadata_state not in {"ready", "quarantined"}:
                findings.append(ReconciliationFinding("state_mismatch", firm_id, object_id, "finalized object exists while metadata is not ready or quarantined"))

    for (firm_id, object_id), (_, _, state, purged_at) in expected.items():
        staged = (firm_id, object_id, "staged") in observed
        final = (firm_id, object_id, "blob") in observed
        if purged_at is not None:
            if staged or final:
                continue
            continue
        if state in {"ready", "quarantined"} and not final:
            findings.append(ReconciliationFinding("missing_object", firm_id, object_id, "metadata references a finalized object that is absent from S3 inventory"))
        elif state == "staged" and not staged and not final:
            findings.append(ReconciliationFinding("missing_staged_object", firm_id, object_id, "staged metadata has no staged or finalized S3 object"))
    return ReconciliationReport(len(databases), checked_rows, checked_objects, tuple(findings))
