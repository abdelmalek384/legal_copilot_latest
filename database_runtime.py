"""Profile-separated runtime for the approved firm-per-database architecture.

When explicit control-plane, tenant-root, and legal-corpus paths are configured,
app.py routes authentication through the control plane, matter operations through
the active firm's database, and legal-registry/search operations through the
central corpus. Firm connections require a server-validated FirmContext.
"""
from __future__ import annotations

import json
import os
import sqlite3
import stat
import threading
from dataclasses import dataclass
from pathlib import Path

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

    def _close_local_connection(self, attribute: str) -> None:
        connection = getattr(self._local, attribute, None)
        if connection is not None:
            try:
                connection.close()
            finally:
                delattr(self._local, attribute)

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

    def control_connection(self) -> sqlite3.Connection:
        """Return the calling thread's control-plane connection."""
        self._require_initialized()
        try:
            self._validate_profile_storage(self.paths.control_plane, "control-plane")
        except Exception:
            self._close_local_connection("control")
            raise
        connection = getattr(self._local, "control", None)
        if connection is None:
            connection = sqlite3.connect(str(self.paths.control_plane), timeout=self.timeout)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            self._local.control = connection
        return connection

    def legal_corpus_connection(self) -> sqlite3.Connection:
        """Return the calling thread's central legal-corpus connection."""
        self._require_initialized()
        try:
            self._validate_profile_storage(self.paths.legal_corpus, "legal-corpus")
        except Exception:
            self._close_local_connection("corpus")
            raise
        connection = getattr(self._local, "corpus", None)
        if connection is None:
            connection = sqlite3.connect(str(self.paths.legal_corpus), timeout=self.timeout)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            self._local.corpus = connection
        return connection

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
            control.execute(
                "UPDATE tenant_database_catalog SET status='disabled',updated_at=datetime('now') "
                "WHERE firm_id=?",
                (firm_id,),
            )
            control.commit()
            raise
        finally:
            if catalog is not None:
                catalog.close()

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
                connection.execute(f"ATTACH DATABASE ? AS {alias}", (str(path),))

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
