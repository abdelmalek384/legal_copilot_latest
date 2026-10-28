"""Profile-separated runtime for the approved firm-per-database architecture.

When explicit control-plane, tenant-root, and legal-corpus paths are configured,
app.py routes authentication through the control plane, matter operations through
the active firm's database, and legal-registry/search operations through the
central corpus. Firm connections require a server-validated FirmContext.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import stat
import threading
import time
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from db_migrations import MigrationError, _migration_files
from schema_profiles import apply_profile_migrations
from tenant_catalog import TenantCatalogError, initialize_catalog, provision_tenant_database
from tenant_context import (
    FirmContext,
    FirmContextError,
    resolve_firm_context,
    sqlite_membership_lookup,
)
from tenant_storage import TenantConnectionError, TenantSQLiteConnectionRouter


class DatabaseRuntimeError(RuntimeError):
    """Raised when database runtime configuration or initialization is invalid."""


@dataclass(frozen=True)
class DatabasePaths:
    control_plane: Path
    tenant_root: Path
    legal_corpus: Path


class DatabaseRuntime:
    """Own profile-aware connections for one application process.

    No legacy COPILOT_DB fallback is provided: silently using the old shared
    database would undermine the separate-database architecture. The caller
    must explicitly configure all three storage locations.
    """

    def __init__(
        self,
        control_plane_path: str | Path,
        tenant_storage_root: str | Path,
        legal_corpus_path: str | Path,
        *,
        migrations_root: str | Path | None = None,
        timeout: float = 30.0,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        root = Path(tenant_storage_root).expanduser()
        if root.is_symlink():
            raise DatabaseRuntimeError("Tenant storage root must not be a symlink")
        control = Path(control_plane_path).expanduser()
        corpus = Path(legal_corpus_path).expanduser()
        for label, path in (("control-plane", control), ("legal-corpus", corpus)):
            if path.exists() and path.is_symlink():
                raise DatabaseRuntimeError(f"{label} database path must not be a symlink")

        control_resolved = control.resolve()
        corpus_resolved = corpus.resolve()
        root_resolved = root.resolve()
        if control_resolved == corpus_resolved:
            raise DatabaseRuntimeError("Control-plane and legal-corpus databases must be separate")
        if self._is_inside(control_resolved, root_resolved) or self._is_inside(corpus_resolved, root_resolved):
            raise DatabaseRuntimeError("Control-plane and legal-corpus files must be outside tenant storage")
        if control_resolved == root_resolved or corpus_resolved == root_resolved:
            raise DatabaseRuntimeError("A database file cannot be the tenant storage directory")

        self.paths = DatabasePaths(control, root, corpus)
        self.migrations_root = Path(
            migrations_root or (Path(__file__).resolve().parent / "migrations")
        )
        self.timeout = float(timeout)
        self._local = threading.local()
        self._initialize_lock = threading.RLock()
        self._initialized = False
        self._tenant_router = TenantSQLiteConnectionRouter(
            self._new_catalog_connection,
            self.paths.tenant_root,
            timeout=self.timeout,
        )

    @staticmethod
    def _is_inside(path: Path, directory: Path) -> bool:
        try:
            path.relative_to(directory)
            return True
        except ValueError:
            return False

    @staticmethod
    def _validate_profile_storage(path: Path, profile: str) -> None:
        """Revalidate control/corpus file and sidecars before every connection use."""
        if path.is_symlink():
            raise DatabaseRuntimeError(f"{profile} database path must not be a symlink")
        if not path.is_file():
            raise DatabaseRuntimeError(f"{profile} database file is missing or not a regular file")
        if os.name == "posix":
            try:
                mode = stat.S_IMODE(path.stat().st_mode)
            except OSError as exc:
                raise DatabaseRuntimeError(
                    f"{profile} database permissions cannot be verified"
                ) from exc
            if mode & 0o077:
                raise DatabaseRuntimeError(
                    f"{profile} database file permissions allow group/other access"
                )
        for suffix in ("-wal", "-shm", "-journal"):
            sidecar = Path(str(path) + suffix)
            if sidecar.is_symlink():
                raise DatabaseRuntimeError(f"{profile} SQLite sidecar must not be a symlink")
            if not sidecar.exists():
                continue
            if not sidecar.is_file():
                raise DatabaseRuntimeError(f"{profile} SQLite sidecar must be a regular file")
            if os.name == "posix":
                try:
                    sidecar_mode = stat.S_IMODE(sidecar.stat().st_mode)
                except OSError as exc:
                    raise DatabaseRuntimeError(
                        f"{profile} SQLite sidecar permissions cannot be verified"
                    ) from exc
                if sidecar_mode & 0o077:
                    raise DatabaseRuntimeError(
                        f"{profile} SQLite sidecar permissions allow group/other access"
                    )

    @staticmethod
    def _schema_object_inventory(connection: sqlite3.Connection) -> dict[str, object]:
        """Describe schema objects and constraints without reading application rows."""
        # Compare stored DDL as well as PRAGMA inventories. PRAGMA table_info
        # does not expose CHECK constraints, and index metadata alone does not
        # capture partial-index predicates or expression definitions.
        objects = tuple(
            (str(row[0]), str(row[1]), str(row[2]), row[3])
            for row in connection.execute(
                "SELECT type,name,tbl_name,sql FROM sqlite_master "
                "WHERE name NOT GLOB 'sqlite_*' ORDER BY type,name"
            )
        )
        tables = [
            str(row[0]) for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT GLOB 'sqlite_*' ORDER BY name"
            )
        ]
        columns = []
        indexes = []
        foreign_keys = []
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            table_columns = tuple(
                (str(row[1]), str(row[2]), int(row[3]), row[4], int(row[5]))
                for row in connection.execute(f"PRAGMA table_info({quoted})")
            )
            columns.append((table, table_columns))
            for index in connection.execute(f"PRAGMA index_list({quoted})"):
                index_name = str(index[1])
                quoted_index = '"' + index_name.replace('"', '""') + '"'
                index_columns = tuple(
                    (int(row[0]), int(row[1]), row[2], int(row[3]), row[4], int(row[5]))
                    for row in connection.execute(f"PRAGMA index_xinfo({quoted_index})")
                )
                indexes.append((
                    table, index_name, int(index[2]), str(index[3]), int(index[4]), index_columns
                ))
            foreign_keys.append((
                table,
                tuple(
                    (int(row[0]), int(row[1]), str(row[2]), str(row[3]), str(row[4]),
                     str(row[5]), str(row[6]), str(row[7]))
                    for row in connection.execute(f"PRAGMA foreign_key_list({quoted})")
                ),
            ))
        triggers = tuple(
            (str(row[0]), " ".join(str(row[1]).split()))
            for row in connection.execute(
                "SELECT name,sql FROM sqlite_master WHERE type='trigger' "
                "AND name NOT GLOB 'sqlite_*' ORDER BY name"
            )
        )
        return {
            "objects": objects,
            "columns": tuple(columns),
            "indexes": tuple(sorted(indexes)),
            "foreign_keys": tuple(foreign_keys),
            "triggers": triggers,
        }

    def _validate_preprovisioned_profile(self, path: Path, profile: str) -> None:
        """Require an exact, healthy migration state before production startup."""
        directory = self.migrations_root / profile
        if directory.is_symlink() or not directory.is_dir():
            raise DatabaseRuntimeError(
                f"Production {profile} migration directory is missing or unsafe"
            )
        try:
            expected = {
                version: (name, hashlib.sha256(sql.encode("utf-8")).hexdigest())
                for version, name, _migration_path, sql in _migration_files(directory)
            }
        except (MigrationError, OSError) as exc:
            raise DatabaseRuntimeError(
                f"Production {profile} migration inventory is unsafe"
            ) from exc
        if not expected:
            raise DatabaseRuntimeError(
                f"Production {profile} migration inventory must not be empty"
            )

        connection = None
        try:
            uri = path.resolve().as_uri() + "?mode=ro"
            connection = sqlite3.connect(uri, uri=True, timeout=self.timeout)
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            if not {"database_profile", "schema_migrations"}.issubset(tables):
                raise DatabaseRuntimeError(
                    f"Production {profile} database is not pre-provisioned"
                )
            marker = connection.execute(
                "SELECT profile FROM database_profile WHERE singleton=1"
            ).fetchall()
            if len(marker) != 1 or marker[0][0] != profile:
                raise DatabaseRuntimeError(
                    f"Production database is not bound to the {profile} profile"
                )

            triggers = {
                row[0]: row[1] for row in connection.execute(
                    "SELECT name,sql FROM sqlite_master WHERE type='trigger' "
                    "AND name IN ('database_profile_no_update','database_profile_no_delete')"
                )
            }
            for operation in ("update", "delete"):
                sql = triggers.get(f"database_profile_no_{operation}")
                normalized = " ".join(sql.lower().split()) if isinstance(sql, str) else ""
                if (
                    f"before {operation} on database_profile" not in normalized
                    or "raise(abort" not in normalized
                    or "database profile binding is immutable" not in normalized
                ):
                    raise DatabaseRuntimeError(
                        f"Production {profile} database lacks immutable profile guards"
                    )

            recorded = {
                int(row[0]): (str(row[1]), str(row[2]))
                for row in connection.execute(
                    "SELECT version,name,checksum_sha256 FROM schema_migrations"
                )
            }
            if recorded != expected:
                raise DatabaseRuntimeError(
                    f"Production {profile} migration history is pending, missing, or drifted"
                )

            expected_connection = sqlite3.connect(":memory:")
            try:
                apply_profile_migrations(
                    expected_connection, profile, self.migrations_root
                )
                expected_schema = self._schema_object_inventory(expected_connection)
            finally:
                expected_connection.close()
            actual_schema = self._schema_object_inventory(connection)
            if actual_schema != expected_schema:
                raise DatabaseRuntimeError(
                    f"Production {profile} schema objects or constraints differ from trusted migrations"
                )

            journal = connection.execute("PRAGMA journal_mode").fetchone()
            if journal is None or str(journal[0]).lower() != "wal":
                raise DatabaseRuntimeError(
                    f"Production {profile} database must already use WAL mode"
                )
            integrity = connection.execute("PRAGMA quick_check").fetchall()
            if len(integrity) != 1 or integrity[0][0] != "ok":
                raise DatabaseRuntimeError(
                    f"Production {profile} database failed SQLite quick_check"
                )
            if connection.execute("PRAGMA foreign_key_check").fetchall():
                raise DatabaseRuntimeError(
                    f"Production {profile} database has foreign-key violations"
                )
        except DatabaseRuntimeError:
            raise
        except (sqlite3.Error, OSError, ValueError) as exc:
            raise DatabaseRuntimeError(
                f"Production {profile} database could not be validated read-only"
            ) from exc
        finally:
            if connection is not None:
                connection.close()

    @staticmethod
    def _file_identity(path: Path) -> tuple[int, int]:
        """Return the device/inode identity of the database currently at a trusted path."""
        try:
            metadata = path.stat()
        except OSError as exc:
            raise DatabaseRuntimeError("Database file identity cannot be verified") from exc
        if not stat.S_ISREG(metadata.st_mode):
            raise DatabaseRuntimeError("Database path is not a regular file")
        return metadata.st_dev, metadata.st_ino

    def _close_local_connection(self, attribute: str) -> None:
        connection = getattr(self._local, attribute, None)
        try:
            if connection is not None:
                connection.close()
        finally:
            if hasattr(self._local, attribute):
                delattr(self._local, attribute)
            identity_attribute = attribute + "_identity"
            if hasattr(self._local, identity_attribute):
                delattr(self._local, identity_attribute)

    @classmethod
    def from_env(cls) -> "DatabaseRuntime":
        """Build from explicit deployment paths; never silently fall back to COPILOT_DB."""
        required = {
            "COPILOT_CONTROL_DB": os.environ.get("COPILOT_CONTROL_DB", "").strip(),
            "COPILOT_TENANT_DB_ROOT": os.environ.get("COPILOT_TENANT_DB_ROOT", "").strip(),
            "COPILOT_CORPUS_DB": os.environ.get("COPILOT_CORPUS_DB", "").strip(),
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise DatabaseRuntimeError(
                "Separate database configuration is required; missing " + ", ".join(missing)
            )
        return cls(
            required["COPILOT_CONTROL_DB"],
            required["COPILOT_TENANT_DB_ROOT"],
            required["COPILOT_CORPUS_DB"],
        )

    def initialize(self) -> None:
        """Initialize profile schemas and catalog metadata; never migrate legacy rows."""
        with self._initialize_lock:
            if self._initialized:
                return
            production = os.environ.get("COPILOT_ENV", "").strip().lower() in {
                "prod", "production"
            }
            if production:
                # Production startup is not a provisioning command. Validate all
                # persistent storage before touching either database so a missing
                # corpus/control file cannot cause partial startup or silent recreation.
                if self.paths.tenant_root.is_symlink() or not self.paths.tenant_root.is_dir():
                    raise DatabaseRuntimeError(
                        "Production tenant storage root must already exist and must not be a symlink"
                    )
                if os.name == "posix":
                    try:
                        root_mode = stat.S_IMODE(self.paths.tenant_root.stat().st_mode)
                    except OSError as exc:
                        raise DatabaseRuntimeError(
                            "Production tenant storage root permissions cannot be verified"
                        ) from exc
                    if root_mode & 0o077:
                        raise DatabaseRuntimeError(
                            "Production tenant storage root permissions allow group/other access"
                        )
                self._validate_profile_storage(self.paths.control_plane, "control-plane")
                self._validate_profile_storage(self.paths.legal_corpus, "legal-corpus")
                self._validate_preprovisioned_profile(self.paths.control_plane, "control_plane")
                self._validate_preprovisioned_profile(self.paths.legal_corpus, "legal_corpus")
                # The app must not start with tenant databases that still need
                # migrations or catalog lifecycle states that require recovery.
                # Reject orphaned database files too; a tenant-root file not bound
                # by the control-plane catalog must never be silently ignored.
                try:
                    control_uri = self.paths.control_plane.resolve().as_uri() + "?mode=ro"
                    with closing(sqlite3.connect(control_uri, uri=True, timeout=self.timeout)) as control:
                        referenced_files = {
                            row[0] for row in control.execute(
                                "SELECT database_file FROM tenant_database_catalog "
                                "WHERE database_file IS NOT NULL"
                            )
                        }
                except sqlite3.Error as exc:
                    raise DatabaseRuntimeError(
                        "Production tenant catalog could not be inspected read-only"
                    ) from exc
                actual_files = {
                    entry.name for entry in self.paths.tenant_root.iterdir()
                    if entry.name.startswith("tenant-") and entry.name.endswith(".sqlite3")
                }
                if actual_files != referenced_files:
                    raise DatabaseRuntimeError(
                        "Production tenant storage contains missing or unreferenced database files"
                    )

                from tools.migrate_tenant_fleet import FleetMigrationError, build_plan

                try:
                    fleet_plan = build_plan(
                        self.paths.control_plane, self.paths.tenant_root, self.migrations_root
                    )
                except FleetMigrationError as exc:
                    raise DatabaseRuntimeError(
                        "Production tenant database fleet failed read-only preflight"
                    ) from exc
                if fleet_plan["pending_migration_count"] or fleet_plan["skipped"]:
                    raise DatabaseRuntimeError(
                        "Production tenant database fleet has pending migrations or unresolved lifecycle states"
                    )
                for target in fleet_plan["targets"]:
                    tenant_path = self.paths.tenant_root / target["database_file"]
                    self._validate_profile_storage(tenant_path, "firm")
                    try:
                        metadata = tenant_path.stat()
                    except OSError as exc:
                        raise DatabaseRuntimeError(
                            f"Production tenant database for firm {target['firm_id']} cannot be inspected"
                        ) from exc
                    if [metadata.st_dev, metadata.st_ino] != target["file_identity"]:
                        raise DatabaseRuntimeError(
                            f"Production tenant database identity changed during startup preflight"
                        )
                    self._validate_preprovisioned_profile(tenant_path, "firm")
            else:
                self.paths.tenant_root.mkdir(parents=True, exist_ok=True)
                if self.paths.tenant_root.is_symlink():
                    raise DatabaseRuntimeError("Tenant storage root must not be a symlink")

            control = self._open_profile_database(self.paths.control_plane, "control_plane")
            try:
                initialize_catalog(control)
            except (TenantCatalogError, sqlite3.Error) as exc:
                raise DatabaseRuntimeError("Control-plane catalog initialization failed") from exc
            finally:
                control.close()

            corpus = self._open_profile_database(self.paths.legal_corpus, "legal_corpus")
            corpus.close()
            self._initialized = True

    def _open_profile_database(self, path: Path, profile: str) -> sqlite3.Connection:
        if path.exists() and path.is_symlink():
            raise DatabaseRuntimeError(f"{profile} database path must not be a symlink")
        path.parent.mkdir(parents=True, exist_ok=True)
        created = False
        connection = None
        try:
            # Control-plane identities and the shared legal corpus are sensitive
            # stores too. Create new files with restrictive permissions before
            # SQLite opens them, rather than relying on the process umask.
            if not path.exists():
                try:
                    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                except FileExistsError as exc:
                    raise DatabaseRuntimeError(
                        f"{profile} database path appeared during initialization"
                    ) from exc
                os.close(descriptor)
                created = True
                try:
                    os.chmod(path, 0o600)
                except OSError as exc:
                    if os.name == "posix":
                        raise DatabaseRuntimeError(
                            f"Cannot enforce restrictive permissions on new {profile} database"
                        ) from exc
            connection = sqlite3.connect(str(path), timeout=self.timeout)
            connection.row_factory = sqlite3.Row
            # The app serves concurrent requests against the same profile DB.
            # WAL lets readers coexist with the audited writes performed by other
            # request threads; keep this setting established before migrations/use.
            journal_mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()
            if journal_mode is None or str(journal_mode[0]).lower() != "wal":
                raise DatabaseRuntimeError(f"WAL journal mode could not be enabled for {profile}")
            connection.execute("PRAGMA foreign_keys=ON")
            if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
                raise DatabaseRuntimeError(f"Foreign-key enforcement failed for {profile}")
            apply_profile_migrations(connection, profile, self.migrations_root)
            return connection
        except Exception:
            if connection is not None:
                connection.close()
            if created:
                for candidate in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm"), Path(str(path) + "-journal")):
                    try:
                        candidate.unlink(missing_ok=True)
                    except OSError:
                        pass
            raise

    def _require_initialized(self) -> None:
        if not self._initialized:
            self.initialize()

    def _cached_profile_connection(self, attribute: str, path: Path, profile: str) -> sqlite3.Connection:
        """Return a cached connection only while its backing file identity is unchanged.

        Replacing a SQLite file at the same path must not leave a process writing to
        an unlinked old database while operators believe it is using the replacement.
        Fail closed on replacement; a process restart is required after repair.
        """
        try:
            self._validate_profile_storage(path, profile)
            current_identity = self._file_identity(path)
        except Exception:
            self._close_local_connection(attribute)
            raise

        connection = getattr(self._local, attribute, None)
        if connection is not None:
            cached_identity = getattr(self._local, attribute + "_identity", None)
            if cached_identity != current_identity:
                self._close_local_connection(attribute)
                raise DatabaseRuntimeError(
                    f"{profile} database file was replaced while a connection was cached; restart the application"
                )
            return connection

        connection = None
        try:
            connection = sqlite3.connect(str(path), timeout=self.timeout)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
                raise DatabaseRuntimeError(f"Foreign-key enforcement failed for {profile}")
            # Check again to close the validation/open race. Never retain a handle
            # if the path changed while SQLite was opening the file.
            if self._file_identity(path) != current_identity:
                raise DatabaseRuntimeError(
                    f"{profile} database file changed while opening; restart the application"
                )
            self._local.__setattr__(attribute, connection)
            self._local.__setattr__(attribute + "_identity", current_identity)
            return connection
        except Exception:
            if connection is not None:
                connection.close()
            self._close_local_connection(attribute)
            raise

    def control_connection(self) -> sqlite3.Connection:
        """Return the calling thread's control-plane connection."""
        self._require_initialized()
        return self._cached_profile_connection("control", self.paths.control_plane, "control-plane")

    def legal_corpus_connection(self) -> sqlite3.Connection:
        """Return the calling thread's central legal-corpus connection."""
        self._require_initialized()
        return self._cached_profile_connection("corpus", self.paths.legal_corpus, "legal-corpus")

    def _new_catalog_connection(self) -> sqlite3.Connection:
        """Return a fresh connection because the tenant router owns and closes it."""
        self._require_initialized()
        self._validate_profile_storage(self.paths.control_plane, "control-plane")
        connection = sqlite3.connect(str(self.paths.control_plane), timeout=self.timeout)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def provision_firm(self, name: str) -> tuple[int, Path]:
        """Provision an empty firm database; does not import or assign legacy data."""
        self._require_initialized()
        clean_name = name.strip() if isinstance(name, str) else ""
        if not clean_name:
            raise ValueError("firm name must not be blank")
        control = self.control_connection()
        cursor = control.execute(
            "INSERT INTO firms(name,status) VALUES(?,'provisioning')", (clean_name,)
        )
        firm_id = int(cursor.lastrowid)
        control.commit()
        catalog = None
        try:
            # Opening the catalog is part of provisioning too. Keep it inside
            # the guarded block so connection failures cannot strand a firm in
            # the permanent 'provisioning' state.
            catalog = self._new_catalog_connection()
            path = provision_tenant_database(
                catalog,
                firm_id,
                self.paths.tenant_root,
                self._initialize_firm_database,
            )
            updated = control.execute(
                "UPDATE firms SET status='active' WHERE id=? AND status='provisioning'",
                (firm_id,),
            )
            if updated.rowcount != 1:
                raise DatabaseRuntimeError("Firm lifecycle state did not advance after provisioning")
            control.execute(
                "INSERT INTO platform_security_events(actor_user_id,firm_id,event_type,detail_json) "
                "VALUES(NULL,?,'firm_provisioned',?)",
                (firm_id, json.dumps({"database_file": path.name, "status": "active"}, sort_keys=True)),
            )
            control.commit()
            return firm_id, path
        except Exception:
            control.rollback()
            control.execute(
                "UPDATE firms SET status='disabled' WHERE id=? AND status IN ('provisioning','active')",
                (firm_id,),
            )
            # Preserve the catalog's explicit failed state when the tenant
            # initializer rejected its database. Only a still-provisioning or
            # already-provisioned mapping is disabled here; overwriting failed
            # would erase the operator's recovery signal.
            # Preserve a clean failed state after schema initialization fails so a
            # later operator-approved retry remains possible. A provisioned database
            # whose final audit/activation transaction failed is different: retain its
            # trusted filename for maintenance, but disable request-time routing.
            control.execute(
                "UPDATE tenant_database_catalog SET status='failed',database_file=NULL,"
                "updated_at=datetime('now'),last_error_code=COALESCE(last_error_code,"
                "'provisioning_recovery_failed') WHERE firm_id=? AND status='provisioning'",
                (firm_id,),
            )
            control.execute(
                "UPDATE tenant_database_catalog SET status='disabled',updated_at=datetime('now') "
                "WHERE firm_id=? AND status='provisioned'",
                (firm_id,),
            )
            control.commit()
            raise
        finally:
            if catalog is not None:
                catalog.close()

    def retry_failed_firm_provisioning(
        self,
        firm_id: int,
        *,
        reason: str,
        operator_reference: str,
        change_reference: str,
    ) -> Path:
        """Retry only a disabled firm whose catalog explicitly records failed provisioning."""
        if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        audit_fields = {
            "reason": reason,
            "operator_reference": operator_reference,
            "change_reference": change_reference,
        }
        if any(not isinstance(value, str) or not value.strip() for value in audit_fields.values()):
            raise ValueError("reason, operator_reference, and change_reference are required")
        self._require_initialized()
        control = self.control_connection()
        control.execute("BEGIN IMMEDIATE")
        try:
            firm = control.execute(
                "SELECT status FROM firms WHERE id=?", (firm_id,)
            ).fetchone()
            catalog_state = control.execute(
                "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
            ).fetchone()
            if firm is None or firm["status"] != "disabled":
                raise DatabaseRuntimeError("Only a disabled firm can enter provisioning recovery")
            if (
                catalog_state is None
                or catalog_state["status"] != "failed"
                or catalog_state["database_file"] is not None
            ):
                raise DatabaseRuntimeError(
                    "Firm does not have a clean failed provisioning catalog entry; refusing implicit recovery"
                )
            existing_memberships = control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE firm_id=?", (firm_id,)
            ).fetchone()[0]
            existing_invitations = control.execute(
                "SELECT COUNT(*) FROM identity_invitations WHERE firm_id=?", (firm_id,)
            ).fetchone()[0]
            if existing_memberships or existing_invitations:
                raise DatabaseRuntimeError(
                    "Failed provisioning recovery requires no existing memberships or invitations"
                )
            changed = control.execute(
                "UPDATE firms SET status='provisioning' WHERE id=? AND status='disabled'",
                (firm_id,),
            )
            if changed.rowcount != 1:
                raise DatabaseRuntimeError("Firm lifecycle state changed concurrently")
            control.commit()
        except Exception:
            control.rollback()
            raise

        catalog = None
        try:
            catalog = self._new_catalog_connection()
            path = provision_tenant_database(
                catalog,
                firm_id,
                self.paths.tenant_root,
                self._initialize_firm_database,
            )
            control.execute("BEGIN IMMEDIATE")
            changed = control.execute(
                "UPDATE firms SET status='active' WHERE id=? AND status='provisioning'",
                (firm_id,),
            )
            if changed.rowcount != 1:
                raise DatabaseRuntimeError("Firm lifecycle state changed during provisioning recovery")
            control.execute(
                "INSERT INTO platform_security_events(actor_user_id,firm_id,event_type,detail_json) "
                "VALUES(NULL,?,'firm_provisioning_retried',?)",
                (firm_id, json.dumps({
                    "database_file": path.name,
                    "status": "active",
                    **{key: value.strip() for key, value in audit_fields.items()},
                }, sort_keys=True)),
            )
            control.commit()
            return path
        except Exception:
            control.rollback()
            control.execute(
                "UPDATE firms SET status='disabled' WHERE id=? AND status='provisioning'",
                (firm_id,),
            )
            control.execute(
                "UPDATE tenant_database_catalog SET status='disabled',updated_at=datetime('now') "
                "WHERE firm_id=? AND status IN ('provisioning','provisioned')",
                (firm_id,),
            )
            control.commit()
            raise
        finally:
            if catalog is not None:
                catalog.close()

    def reconcile_interrupted_firm_provisioning(
        self,
        firm_id: int,
        *,
        reason: str,
        operator_reference: str,
        change_reference: str,
    ) -> None:
        """Move a confirmed interrupted, file-less provisioning attempt to retryable failure.

        This deliberately refuses to inspect, delete, adopt, or overwrite any existing
        tenant database file. The operator must stop all app/background workers first.
        """
        if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        audit_fields = {
            "reason": reason,
            "operator_reference": operator_reference,
            "change_reference": change_reference,
        }
        if any(not isinstance(value, str) or not value.strip() for value in audit_fields.values()):
            raise ValueError("reason, operator_reference, and change_reference are required")
        self._require_initialized()
        root = self.paths.tenant_root
        if root.is_symlink() or not root.is_dir():
            raise DatabaseRuntimeError("Tenant storage root is unsafe; refusing reconciliation")
        control = self.control_connection()
        control.execute("BEGIN IMMEDIATE")
        try:
            firm = control.execute(
                "SELECT status FROM firms WHERE id=?", (firm_id,)
            ).fetchone()
            catalog_state = control.execute(
                "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
                (firm_id,),
            ).fetchone()
            if firm is None or firm["status"] != "provisioning":
                raise DatabaseRuntimeError(
                    "Only a firm explicitly stuck in provisioning can be reconciled"
                )
            if catalog_state is None or catalog_state["status"] != "provisioning":
                raise DatabaseRuntimeError(
                    "Firm and catalog are not both in provisioning state; refusing reconciliation"
                )
            existing_memberships = control.execute(
                "SELECT COUNT(*) FROM firm_memberships WHERE firm_id=?", (firm_id,)
            ).fetchone()[0]
            existing_invitations = control.execute(
                "SELECT COUNT(*) FROM identity_invitations WHERE firm_id=?", (firm_id,)
            ).fetchone()[0]
            if existing_memberships or existing_invitations:
                raise DatabaseRuntimeError(
                    "Interrupted provisioning has existing memberships or invitations; "
                    "manual lifecycle review required"
                )
            filename = catalog_state["database_file"]
            if filename is not None and (
                not isinstance(filename, str)
                or not re.fullmatch(rf"tenant-{firm_id}-[0-9a-f]{{32}}\.sqlite3", filename)
            ):
                raise DatabaseRuntimeError(
                    "Provisioning catalog contains an invalid filename; manual investigation required"
                )
            # Any tenant file or SQLite sidecar for this firm is ambiguous: it may
            # contain a complete database whose final catalog commit was interrupted.
            # Never delete or adopt it automatically.
            candidates = list(root.glob(f"tenant-{firm_id}-*.sqlite3*"))
            if candidates:
                raise DatabaseRuntimeError(
                    "Tenant database or sidecar exists; manual integrity/binding review required"
                )
            changed = control.execute(
                "UPDATE firms SET status='disabled' WHERE id=? AND status='provisioning'",
                (firm_id,),
            )
            if changed.rowcount != 1:
                raise DatabaseRuntimeError("Firm lifecycle state changed concurrently")
            updated = control.execute(
                "UPDATE tenant_database_catalog SET status='failed',database_file=NULL,"
                "last_error_code='interrupted_provisioning_reconciled',updated_at=datetime('now') "
                "WHERE firm_id=? AND status='provisioning'",
                (firm_id,),
            )
            if updated.rowcount != 1:
                raise DatabaseRuntimeError("Catalog lifecycle state changed concurrently")
            control.execute(
                "INSERT INTO platform_security_events(actor_user_id,firm_id,event_type,detail_json) "
                "VALUES(NULL,?,'firm_provisioning_reconciled_failed',?)",
                (firm_id, json.dumps({
                    "previous_database_file": filename,
                    "status": "failed",
                    **{key: value.strip() for key, value in audit_fields.items()},
                }, sort_keys=True)),
            )
            control.commit()
        except Exception:
            control.rollback()
            raise

    def revoke_disabled_firm_invitations(
        self,
        firm_id: int,
        *,
        reason: str,
        operator_reference: str,
        change_reference: str,
    ) -> int:
        """Revoke active invitations for a disabled firm before offboarding."""
        if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        audit_fields = {
            "reason": reason,
            "operator_reference": operator_reference,
            "change_reference": change_reference,
        }
        if any(not isinstance(value, str) or not value.strip() for value in audit_fields.values()):
            raise ValueError("reason, operator_reference, and change_reference are required")
        self._require_initialized()
        control = self.control_connection()
        now = int(time.time())
        control.execute("BEGIN IMMEDIATE")
        try:
            firm = control.execute(
                "SELECT status FROM firms WHERE id=?", (firm_id,)
            ).fetchone()
            catalog = control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
            ).fetchone()
            if firm is None or firm["status"] != "disabled":
                raise DatabaseRuntimeError(
                    "Invitation offboarding requires a disabled firm"
                )
            if catalog is None or catalog["status"] != "disabled":
                raise DatabaseRuntimeError(
                    "Invitation offboarding requires a disabled tenant catalog entry"
                )
            invitations = control.execute(
                "SELECT id,status FROM identity_invitations "
                "WHERE firm_id=? AND status IN ('pending','sent') ORDER BY id",
                (firm_id,),
            ).fetchall()
            for invitation in invitations:
                updated = control.execute(
                    "UPDATE identity_invitations SET status='revoked',updated_at=? "
                    "WHERE id=? AND status IN ('pending','sent')",
                    (now, invitation["id"]),
                )
                if updated.rowcount != 1:
                    raise DatabaseRuntimeError(
                        "Invitation lifecycle state changed concurrently"
                    )
                control.execute(
                    "INSERT INTO identity_lifecycle_events("
                    "actor_user_id,target_user_id,firm_id,invitation_id,recovery_token_id,"
                    "event_type,detail_json,created_at"
                    ") VALUES(NULL,NULL,?,?,NULL,'invitation_revoked',?,?)",
                    (
                        firm_id,
                        invitation["id"],
                        json.dumps({
                            "reason": reason.strip(),
                            "operator_reference": operator_reference.strip(),
                            "change_reference": change_reference.strip(),
                            "source": "firm_offboarding_cli",
                        }, sort_keys=True),
                        now,
                    ),
                )
            control.commit()
            return len(invitations)
        except Exception:
            control.rollback()
            raise

    def disable_firm(self, firm_id: int) -> bool:
        """Disable a firm without deleting its database or membership history.

        Returns True when an active firm was disabled and False when it was
        already disabled. Provisioning/failed states require explicit recovery.
        """
        if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        self._require_initialized()
        control = self.control_connection()
        control.execute("BEGIN IMMEDIATE")
        try:
            firm = control.execute(
                "SELECT status FROM firms WHERE id=?", (firm_id,)
            ).fetchone()
            if firm is None:
                raise DatabaseRuntimeError("Firm does not exist")
            if firm["status"] not in {"active", "disabled"}:
                raise DatabaseRuntimeError(
                    "Firm is provisioning or failed; use the provisioning recovery procedure"
                )
            catalog = control.execute(
                "SELECT status FROM tenant_database_catalog WHERE firm_id=?", (firm_id,)
            ).fetchone()
            if catalog is None:
                raise DatabaseRuntimeError(
                    "Firm has no trusted tenant catalog entry; refusing lifecycle change"
                )
            changed = firm["status"] == "active"
            if changed:
                updated = control.execute(
                    "UPDATE firms SET status='disabled' WHERE id=? AND status='active'",
                    (firm_id,),
                )
                if updated.rowcount != 1:
                    raise DatabaseRuntimeError("Firm lifecycle state changed concurrently")
            control.execute(
                "UPDATE tenant_database_catalog SET status='disabled',updated_at=datetime('now') "
                "WHERE firm_id=?",
                (firm_id,),
            )
            if changed:
                control.execute(
                    "INSERT INTO platform_security_events(actor_user_id,firm_id,event_type,detail_json) "
                    "VALUES(NULL,?,'firm_disabled',?)",
                    (firm_id, json.dumps({"previous_status": "active", "new_status": "disabled"}, sort_keys=True)),
                )
            control.commit()
            return changed
        except Exception:
            control.rollback()
            raise

    def _initialize_firm_database(self, connection: sqlite3.Connection) -> None:
        # Tenant databases are written by concurrent request threads too. Set
        # WAL once, while the database is being provisioned and before serving it.
        journal_mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()
        if journal_mode is None or str(journal_mode[0]).lower() != "wal":
            raise DatabaseRuntimeError("Tenant WAL journal mode could not be enabled")
        connection.execute("PRAGMA foreign_keys=ON")
        if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            raise DatabaseRuntimeError("Tenant foreign-key enforcement could not be enabled")
        apply_profile_migrations(connection, "firm", self.migrations_root)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            raise DatabaseRuntimeError("New firm database failed SQLite integrity_check")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise DatabaseRuntimeError("New firm database failed foreign_key_check")

    def create_global_identity(self, name: str, email: str, password_hash: str) -> int:
        """Create a global identity with canonical email; does not grant a platform role."""
        from identity import normalize_email

        clean_name = name.strip() if isinstance(name, str) else ""
        display_email = email.strip() if isinstance(email, str) else ""
        if not clean_name or not display_email or not isinstance(password_hash, str) or not password_hash:
            raise ValueError("name, email, and password hash are required")
        normalized = normalize_email(display_email)
        if not normalized:
            raise ValueError("email must normalize to a non-empty value")
        control = self.control_connection()
        cursor = control.execute(
            "INSERT INTO users(name,email_display,email_normalized,password_hash,status) "
            "VALUES(?,?,?,?,'active')",
            (clean_name, display_email, normalized, password_hash),
        )
        control.commit()
        return int(cursor.lastrowid)

    def create_firm_membership(
        self,
        user_id: int,
        firm_id: int,
        role: str,
        *,
        created_by_user_id: int | None = None,
    ) -> None:
        """Create an explicit membership; firm role never grants platform privileges."""
        if role not in {"admin", "lawyer", "junior"}:
            raise ValueError("unsupported firm role")
        control = self.control_connection()
        control.execute("BEGIN IMMEDIATE")
        try:
            identity = control.execute(
                "SELECT status FROM users WHERE id=?", (user_id,)
            ).fetchone()
            firm = control.execute(
                "SELECT status FROM firms WHERE id=?", (firm_id,)
            ).fetchone()
            if identity is None or identity["status"] != "active":
                raise DatabaseRuntimeError("Membership requires an active global identity")
            if firm is None or firm["status"] != "active":
                raise DatabaseRuntimeError("Membership requires an active firm")
            control.execute(
                "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status,created_by_user_id) "
                "VALUES(?,?,?,'active',?)",
                (user_id, firm_id, role, created_by_user_id),
            )
            control.execute(
                "INSERT INTO platform_security_events(actor_user_id,target_user_id,firm_id,event_type,detail_json) "
                "VALUES(?,?,?,'membership_created',?)",
                (created_by_user_id, user_id, firm_id, json.dumps({"firm_role": role}, sort_keys=True)),
            )
            control.commit()
        except Exception:
            control.rollback()
            raise

    def create_initial_firm_owner(
        self, firm_id: int, name: str, email: str, password_hash: str
    ) -> int:
        """Bootstrap the first firm admin without granting platform-wide privileges."""
        from identity import normalize_email

        clean_name = name.strip() if isinstance(name, str) else ""
        display_email = email.strip() if isinstance(email, str) else ""
        normalized = normalize_email(display_email)
        if not clean_name or not display_email or not normalized or not password_hash:
            raise ValueError("name, email, and password hash are required")
        control = self.control_connection()
        control.execute("BEGIN IMMEDIATE")
        try:
            firm = control.execute(
                "SELECT status FROM firms WHERE id=?", (firm_id,)
            ).fetchone()
            if firm is None or firm["status"] != "active":
                raise DatabaseRuntimeError("Initial owner requires a provisioned active firm")
            existing = control.execute(
                "SELECT 1 FROM firm_memberships WHERE firm_id=? LIMIT 1", (firm_id,)
            ).fetchone()
            if existing:
                raise DatabaseRuntimeError("Initial owner bootstrap is only allowed for an empty firm")
            cursor = control.execute(
                "INSERT INTO users(name,email_display,email_normalized,password_hash,status) "
                "VALUES(?,?,?,?,'active')",
                (clean_name, display_email, normalized, password_hash),
            )
            user_id = int(cursor.lastrowid)
            control.execute(
                "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status) "
                "VALUES(?,?,'admin','active')",
                (user_id, firm_id),
            )
            control.execute(
                "INSERT INTO platform_security_events(actor_user_id,target_user_id,firm_id,event_type,detail_json) "
                "VALUES(NULL,?,?,'initial_owner_bootstrapped',?)",
                (user_id, firm_id, json.dumps({"firm_role": "admin", "platform_role_granted": False}, sort_keys=True)),
            )
            control.commit()
            return user_id
        except Exception:
            control.rollback()
            raise

    def resolve_context(self, user_id: int, firm_id: int) -> FirmContext:
        """Resolve the current role from the control plane; callers cannot supply a trusted role."""
        control = self.control_connection()
        identity = control.execute(
            "SELECT id,status FROM users WHERE id=?", (user_id,)
        ).fetchone()
        if identity is None or identity["status"] != "active":
            raise FirmContextError("active global identity is required")
        lookup = sqlite_membership_lookup(control)
        return resolve_firm_context({"id": user_id}, firm_id, lookup)

    def _configure_firm_connection(self, connection: sqlite3.Connection, firm_id: int) -> None:
        """Attach shared profiles and expose views scoped to this connection's firm."""
        # These databases are attached to every matter connection. Validate them
        # even when the tenant connection itself is already cached.
        self._validate_profile_storage(self.paths.control_plane, "control-plane")
        self._validate_profile_storage(self.paths.legal_corpus, "legal-corpus")
        expected = {
            "control": self.paths.control_plane.resolve(),
            "corpus": self.paths.legal_corpus.resolve(),
        }
        attached = {
            row["name"]: Path(row["file"]).resolve()
            for row in connection.execute("PRAGMA database_list")
            if row["name"] not in {"main", "temp"} and row["file"]
        }
        for alias, path in expected.items():
            existing = attached.get(alias)
            if existing is not None and existing != path:
                raise DatabaseRuntimeError(f"Unexpected database attached as {alias}")
            if existing is None:
                connection.execute(f"ATTACH DATABASE ? AS {alias}", (path.as_uri() + "?mode=ro",))

        # Existing matter handlers expect a firm-scoped users table. A temp
        # context table prevents a user with multiple memberships from appearing
        # multiple times or exposing another firm's role in joins.
        connection.execute(
            "CREATE TEMP TABLE IF NOT EXISTS _active_firm_context(firm_id INTEGER NOT NULL)"
        )
        connection.execute("DELETE FROM _active_firm_context")
        connection.execute(
            "INSERT INTO _active_firm_context(firm_id) VALUES(?)", (firm_id,)
        )
        connection.execute("""
            CREATE TEMP VIEW IF NOT EXISTS users AS
            SELECT u.id, u.name, u.email_display AS email, u.email_normalized,
                   u.password_hash AS pw, fm.firm_role AS role, fm.firm_id,
                   CASE WHEN u.status='active' AND fm.status='active' THEN 1 ELSE 0 END AS active
            FROM control.users u
            JOIN control.firm_memberships fm ON fm.user_id=u.id
            JOIN _active_firm_context current_firm ON current_firm.firm_id=fm.firm_id
        """)
        connection.execute("""
            CREATE TEMP VIEW IF NOT EXISTS firms AS
            SELECT f.id, f.name, f.status, f.created_at FROM control.firms f
            JOIN _active_firm_context current_firm ON current_firm.firm_id=f.id
        """)

    def firm_connection(self, context: FirmContext) -> sqlite3.Connection:
        """Return a firm connection only after revalidating membership and current role."""
        if not isinstance(context, FirmContext):
            raise TypeError("a verified FirmContext is required")
        try:
            current = self.resolve_context(context.user_id, context.firm_id)
        except FirmContextError:
            # A stale context must not leave a cached connection usable after
            # membership or firm lifecycle state has been revoked.
            self._tenant_router.revoke_firm_connection(context.firm_id)
            raise
        if current.role != context.role:
            self._tenant_router.revoke_firm_connection(context.firm_id)
            raise FirmContextError("firm role changed; resolve the current context before continuing")
        try:
            connection = self._tenant_router.connection_for_firm(current.firm_id)
            self._configure_firm_connection(connection, current.firm_id)
            return connection
        except (TenantConnectionError, ValueError, sqlite3.Error) as exc:
            raise DatabaseRuntimeError(
                "Firm database is unavailable; no shared fallback is permitted"
            ) from exc

    def close_current_thread(self) -> None:
        """Close all connections owned by the calling thread."""
        errors = []
        try:
            self._tenant_router.close_current_thread()
        except Exception as exc:
            errors.append(exc)
        for attribute in ("control", "corpus"):
            connection = getattr(self._local, attribute, None)
            if connection is not None:
                try:
                    connection.close()
                except sqlite3.Error as exc:
                    errors.append(exc)
                finally:
                    delattr(self._local, attribute)
        if errors:
            raise DatabaseRuntimeError(
                f"Failed to close {len(errors)} database connection(s)"
            ) from errors[0]
