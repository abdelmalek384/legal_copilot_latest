"""Admin commands for account maintenance and encrypted database backups."""
import argparse
import getpass
import json
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet
import app
from database_runtime import DatabaseRuntime, DatabaseRuntimeError
from database_backup import DatabaseBundleError, create_backup_bundle, restore_backup_bundle, verify_backup_bundle
from database_backup_archive import upload_encrypted_bundle, download_encrypted_bundle_version


def _require_profile_separated_runtime(operation: str) -> None:
    """Forbid CLI writes through the shared compatibility database."""
    required = ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if os.environ.get("COPILOT_DB", "").strip() or missing:
        details = []
        if os.environ.get("COPILOT_DB", "").strip():
            details.append("COPILOT_DB must be unset")
        if missing:
            details.append("missing " + ", ".join(missing))
        raise SystemExit(
            f"{operation} requires the profile-separated database runtime: " + "; ".join(details)
        )


def _backup_fernet():
    key = os.environ.get("BACKUP_KEY")
    if not key:
        raise SystemExit("BACKUP_KEY is required; generate one with: python manage.py genkey")
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except (ValueError, TypeError) as exc:
        raise SystemExit("BACKUP_KEY is invalid; generate a Fernet key with: python manage.py genkey") from exc




def read_password(prompt):
    print("ملاحظة: لن تظهر أحرف كلمة المرور أثناء الكتابة في الطرفية؛ هذا طبيعي.")
    pw = getpass.getpass(prompt)
    try:
        return app.validate_password_strength(pw)
    except ValueError as exc:
        raise SystemExit("كلمة المرور ضعيفة: " + str(exc)) from exc


def adduser(a):
    _require_profile_separated_runtime("adduser")
    if not a.firm_id:
        raise SystemExit("Separate-database mode requires --firm-id; firm roles do not grant platform roles.")
    pw = read_password("كلمة المرور (12 حرفا على الأقل): ")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        c = runtime.control_connection()
        c.execute("BEGIN IMMEDIATE")
        firm = c.execute("SELECT status FROM firms WHERE id=?", (a.firm_id,)).fetchone()
        if firm is None or firm["status"] != "active":
            c.rollback()
            raise SystemExit("Cannot create a user membership for a missing or inactive firm.")
        cur = c.execute(
            "INSERT INTO users(name,email_display,email_normalized,password_hash,status) "
            "VALUES(?,?,?,?,'active')",
            (a.name.strip(), a.email.strip(), app.normalize_email(a.email), app.hash_pw(pw)),
        )
        c.execute(
            "INSERT INTO platform_security_events(actor_user_id,target_user_id,firm_id,event_type,detail_json) "
            "VALUES(NULL,?,?,'identity_created_cli',?)",
            (cur.lastrowid, a.firm_id, json.dumps({"method": "manage.py adduser"}, sort_keys=True)),
        )
        c.execute(
            "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status) VALUES(?,?,?,'active')",
            (cur.lastrowid, a.firm_id, a.role),
        )
        c.execute(
            "INSERT INTO platform_security_events(actor_user_id,target_user_id,firm_id,event_type,detail_json) "
            "VALUES(NULL,?,?,'membership_created',?)",
            (cur.lastrowid, a.firm_id, json.dumps({"firm_role": a.role, "method": "manage.py adduser"}, sort_keys=True)),
        )
        c.commit()
        print("تم إنشاء الحساب وربطه بالمكتب المحدد. صلاحيات المنصة مستقلة عن دور المكتب.")
    except SystemExit:
        raise
    except Exception as e:
        try:
            runtime.control_connection().rollback()
        except Exception:
            pass
        raise SystemExit("تعذر إنشاء الحساب أو عضوية المكتب. تحقق من البريد ورقم المكتب. التفاصيل: " + str(e))
    finally:
        runtime.close_current_thread()


def init_tenancy(a):
    """Initialize fresh profile databases and bootstrap the first firm administrator."""
    pw = read_password("كلمة مرور مدير المكتب الأول: ")
    runtime = DatabaseRuntime.from_env()
    runtime.initialize()
    control = runtime.control_connection()
    active_memberships = control.execute(
        "SELECT COUNT(*) FROM firm_memberships fm JOIN users u ON u.id=fm.user_id "
        "JOIN firms f ON f.id=fm.firm_id WHERE fm.status='active' AND u.status='active' AND f.status='active'"
    ).fetchone()[0]
    if active_memberships:
        raise SystemExit("An active firm membership already exists; refusing to replace the initial owner.")
    firms = control.execute("SELECT id,name,status FROM firms WHERE status='active' ORDER BY id").fetchall()
    if len(firms) == 0:
        existing_users = control.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        existing_firms = control.execute("SELECT COUNT(*) FROM firms").fetchone()[0]
        if existing_users or existing_firms:
            raise SystemExit("Existing identities or firm records need explicit recovery review before bootstrap.")
        firm_id, database_path = runtime.provision_firm(a.firm_name)
    elif len(firms) == 1:
        firm_id, database_path = int(firms[0]["id"]), None
        memberships = control.execute(
            "SELECT COUNT(*) FROM firm_memberships WHERE firm_id=?", (firm_id,)
        ).fetchone()[0]
        existing_users = control.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if memberships or existing_users:
            raise SystemExit("Existing identities or membership records need explicit recovery review before bootstrap.")
    else:
        raise SystemExit("Multiple firms already exist; choose and bootstrap an owner through a reviewed recovery procedure.")
    try:
        user_id = runtime.create_initial_firm_owner(
            firm_id, a.owner_name, a.owner_email, app.hash_pw(pw)
        )
    except Exception as exc:
        raise SystemExit("Firm database was prepared but initial owner creation failed; inspect the control plane before retrying: " + str(exc))
    print("تم تهيئة قاعدة المكتب المنفصلة.")
    print("firm_id:", firm_id)
    print("owner_user_id:", user_id)
    if database_path:
        print("firm_database:", database_path)
    print("لم يتم منح دور إداري على مستوى المنصة.")


def provision_firm_cli(a):
    """Provision a new firm database through the trusted runtime catalog."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Set the three separate database paths before provisioning a firm.")
    runtime = DatabaseRuntime.from_env()
    try:
        firm_id, database_path = runtime.provision_firm(a.name)
        print(json.dumps({
            "status": "provisioned",
            "firm_id": firm_id,
            "firm_name": a.name.strip(),
            "database_path": str(database_path),
            "next_step": "Create a new owner with adduser --firm-id or attach an existing identity with addmembership.",
        }, ensure_ascii=False, sort_keys=True))
    except (DatabaseRuntimeError, ValueError, sqlite3.Error) as exc:
        raise SystemExit("Firm provisioning failed: " + str(exc)) from exc
    finally:
        runtime.close_current_thread()


def retry_failed_provisioning_cli(a):
    """Retry a failed tenant initializer only with explicit operator/change evidence."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Provisioning recovery requires the separate database architecture.")
    if not a.confirm_retry:
        raise SystemExit("Refusing provisioning retry without --confirm-retry.")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        database_path = runtime.retry_failed_firm_provisioning(
            a.firm_id,
            reason=a.reason,
            operator_reference=a.operator_reference,
            change_reference=a.change_reference,
        )
        print(json.dumps({
            "status": "provisioned",
            "firm_id": a.firm_id,
            "database_file": database_path.name,
            "recovery": "retried_failed_provisioning",
        }, ensure_ascii=False, sort_keys=True))
    except (RuntimeError, ValueError, OSError, sqlite3.Error) as exc:
        raise SystemExit("Failed-firm provisioning recovery refused or failed: " + str(exc)) from exc
    finally:
        runtime.close_current_thread()


def reconcile_interrupted_provisioning_cli(a):
    """Mark only a file-less interrupted provisioning attempt as retryable failure."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Provisioning reconciliation requires the separate database architecture.")
    if not a.confirm_workers_stopped:
        raise SystemExit("Refusing reconciliation without --confirm-workers-stopped.")
    if not a.confirm_reconcile:
        raise SystemExit("Refusing reconciliation without --confirm-reconcile.")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        runtime.reconcile_interrupted_firm_provisioning(
            a.firm_id,
            reason=a.reason,
            operator_reference=a.operator_reference,
            change_reference=a.change_reference,
        )
        print(json.dumps({
            "status": "failed",
            "firm_id": a.firm_id,
            "recovery": "reconciled_interrupted_provisioning",
            "retry_allowed": True,
        }, ensure_ascii=False, sort_keys=True))
    except (DatabaseRuntimeError, ValueError, OSError, sqlite3.Error) as exc:
        raise SystemExit("Interrupted provisioning reconciliation refused or failed: " + str(exc)) from exc
    finally:
        runtime.close_current_thread()


def revoke_firm_invitations_cli(a):
    """Revoke pending/sent invitations for a disabled firm before offboarding."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Invitation offboarding requires the separate database architecture.")
    if not a.confirm_revoke:
        raise SystemExit("Refusing invitation revocation without --confirm-revoke.")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        revoked = runtime.revoke_disabled_firm_invitations(
            a.firm_id,
            reason=a.reason,
            operator_reference=a.operator_reference,
            change_reference=a.change_reference,
        )
        print(json.dumps({
            "firm_id": a.firm_id,
            "revoked_invitation_count": revoked,
            "status": "completed",
            "operation": "revoke_disabled_firm_invitations",
        }, ensure_ascii=False, sort_keys=True))
    except (DatabaseRuntimeError, ValueError, OSError, sqlite3.Error) as exc:
        raise SystemExit("Firm invitation offboarding refused or failed: " + str(exc)) from exc
    finally:
        runtime.close_current_thread()


def disable_firm_cli(a):
    """Disable firm access while retaining its database and historical data."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Firm lifecycle commands require the separate database architecture.")
    runtime = DatabaseRuntime.from_env()
    try:
        changed = runtime.disable_firm(a.firm_id)
        print(json.dumps({
            "status": "disabled",
            "firm_id": a.firm_id,
            "changed": changed,
            "data_deleted": False,
        }, ensure_ascii=False, sort_keys=True))
    except (DatabaseRuntimeError, ValueError, sqlite3.Error) as exc:
        raise SystemExit("Firm disable failed: " + str(exc)) from exc
    finally:
        runtime.close_current_thread()


def addmembership_cli(a):
    """Attach an existing active global identity to a provisioned firm."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Cross-firm memberships require the separate database architecture.")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        normalized = app.normalize_email(a.email)
        control = runtime.control_connection()
        identity = control.execute(
            "SELECT id,name,status FROM users WHERE email_normalized=?", (normalized,)
        ).fetchone()
        if identity is None:
            raise SystemExit("No global identity exists for that normalized email.")
        if identity["status"] != "active":
            raise SystemExit("Disabled global identities cannot receive new memberships.")
        existing = control.execute(
            "SELECT status FROM firm_memberships WHERE user_id=? AND firm_id=?",
            (identity["id"], a.firm_id),
        ).fetchone()
        if existing is not None:
            raise SystemExit("Membership already exists; reactivation requires a reviewed workflow.")
        try:
            runtime.create_firm_membership(int(identity["id"]), a.firm_id, a.role)
        except (DatabaseRuntimeError, ValueError, sqlite3.Error) as exc:
            raise SystemExit("Membership creation failed: " + str(exc)) from exc
        print(json.dumps({
            "status": "membership_created",
            "user_id": int(identity["id"]),
            "name": identity["name"],
            "email": normalized,
            "firm_id": a.firm_id,
            "role": a.role,
        }, ensure_ascii=False, sort_keys=True))
    finally:
        runtime.close_current_thread()


def _is_privileged_identity(control, user_id: int) -> bool:
    return control.execute(
        "SELECT 1 FROM user_platform_roles WHERE user_id=? "
        "UNION ALL SELECT 1 FROM firm_memberships WHERE user_id=? AND firm_role='admin' LIMIT 1",
        (user_id, user_id),
    ).fetchone() is not None


def resetpw(a):
    _require_profile_separated_runtime("resetpw")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        c = runtime.control_connection()
        email = app.normalize_email(a.email)
        account = c.execute(
            "SELECT id,status FROM users WHERE email_normalized=?", (email,)
        ).fetchone()
        if not account:
            raise SystemExit("لا يوجد حساب بهذا البريد الإلكتروني.")
        if _is_privileged_identity(c, int(account["id"])):
            raise SystemExit(
                "Privileged identities require the MFA-authorized resetpw-assisted procedure."
            )
        pw = read_password("كلمة المرور الجديدة: ")
        c.execute("BEGIN IMMEDIATE")
        current = c.execute(
            "SELECT id,status FROM users WHERE id=?", (account["id"],)
        ).fetchone()
        if current is None or current["status"] != "active" or _is_privileged_identity(c, int(account["id"])):
            c.rollback()
            raise SystemExit("Identity state changed; no password reset was performed.")
        c.execute(
            "UPDATE users SET password_hash=?,updated_at=datetime('now') WHERE id=? AND status='active'",
            (app.hash_pw(pw), account["id"]),
        )
        revoked = c.execute("DELETE FROM auth_sessions WHERE user_id=?", (account["id"],)).rowcount
        c.execute(
            "INSERT INTO platform_security_events(actor_user_id,target_user_id,event_type,detail_json) "
            "VALUES(NULL,?,'password_reset_cli',?)",
            (account["id"], json.dumps({"method": "manage.py resetpw", "sessions_revoked": revoked}, sort_keys=True)),
        )
        c.commit()
        print("تم تحديث كلمة المرور وإبطال جميع الجلسات؛ سجّل الدخول من جديد.")
    except SystemExit:
        raise
    except Exception as exc:
        try:
            runtime.control_connection().rollback()
        except Exception:
            pass
        raise SystemExit("Password reset failed; no success is reported.") from exc
    finally:
        runtime.close_current_thread()


def resetpw_assisted_cli(a):
    """Reset a privileged identity only after a distinct active MFA-enabled platform admin authorizes it."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Assisted privileged password recovery requires separate-database mode.")
    if not getattr(a, "confirm_reset", False):
        raise SystemExit("Explicit --confirm-reset is required.")
    if isinstance(a.target_user_id, bool) or a.target_user_id <= 0:
        raise SystemExit("--target-user-id must be a positive integer.")
    reason = a.reason.strip() if isinstance(a.reason, str) else ""
    if len(reason) < 8 or len(reason) > 500:
        raise SystemExit("--reason must contain 8 to 500 characters; do not include secrets.")
    reference_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{2,63}$")
    operator_reference = a.operator_reference.strip() if isinstance(a.operator_reference, str) else ""
    change_reference = a.change_reference.strip() if isinstance(a.change_reference, str) else ""
    if not reference_pattern.fullmatch(operator_reference):
        raise SystemExit("--operator-reference must be a 3-64 character restricted identifier.")
    if not reference_pattern.fullmatch(change_reference):
        raise SystemExit("--change-reference must be a 3-64 character restricted identifier.")
    actor_email = app.normalize_email(a.actor_email)
    if not actor_email:
        raise SystemExit("--actor-email must identify an existing global identity.")

    actor_password = getpass.getpass("Authorizing platform administrator password: ")
    actor_code = getpass.getpass("Authorizing platform administrator TOTP code: ")
    new_password = read_password("New password for privileged account: ")
    new_password_hash = app.hash_pw(new_password)
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        control = runtime.control_connection()
        now = int(time.time())
        control.execute("BEGIN IMMEDIATE")

        def abort(message):
            if control.in_transaction:
                control.rollback()
            raise SystemExit(message)

        actor = control.execute(
            "SELECT id,password_hash,status FROM users WHERE email_normalized=?",
            (actor_email,),
        ).fetchone()
        if (
            actor is None or actor["status"] != "active"
            or not app.check_pw(actor_password, actor["password_hash"])
        ):
            abort("Assisted recovery actor authentication failed.")
        actor_id = int(actor["id"])
        if actor_id == a.target_user_id:
            abort("The authorizing platform administrator must differ from the target.")
        authorized = control.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (actor_id,),
        ).fetchone()
        if authorized is None:
            abort("Only an active platform_admin may authorize privileged password recovery.")
        actor_mfa = control.execute(
            "SELECT status,locked_until FROM mfa_credentials WHERE user_id=?",
            (actor_id,),
        ).fetchone()
        if actor_mfa is None or actor_mfa["status"] != "enabled":
            abort("The authorizing platform administrator must have enabled MFA.")
        if int(actor_mfa["locked_until"] or 0) > now:
            abort("The authorizing administrator's MFA is temporarily locked.")
        try:
            factor = app._mfa_verify_factor_in_transaction(
                control, actor_id, code=actor_code, recovery_code=None, now=now,
            )
        except app.MFAConfigurationError as exc:
            abort("MFA encryption key is unavailable or invalid.")
        if factor != "totp":
            app._mfa_record_failure(control, actor_id, now)
            control.commit()
            raise SystemExit("Assisted recovery actor MFA verification failed.")

        target = control.execute(
            "SELECT id,status,password_hash FROM users WHERE id=?",
            (a.target_user_id,),
        ).fetchone()
        if target is None or target["status"] != "active":
            abort("Target must be an existing active global identity.")
        if not _is_privileged_identity(control, int(target["id"])):
            abort("This command is restricted to firm-admin or platform-role identities.")
        active_access = control.execute(
            "SELECT 1 FROM firm_memberships fm JOIN firms f ON f.id=fm.firm_id "
            "WHERE fm.user_id=? AND fm.status='active' AND f.status='active' "
            "UNION ALL SELECT 1 FROM user_platform_roles WHERE user_id=? LIMIT 1",
            (target["id"], target["id"]),
        ).fetchone()
        if active_access is None:
            abort("Target has no active firm membership or platform role; no reset was performed.")
        if app.check_pw(new_password, target["password_hash"]):
            abort("Choose a new password different from the current password.")
        if control.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (target["id"],),
        ).fetchone():
            active_admins = control.execute(
                "SELECT COUNT(DISTINCT u.id) FROM users u JOIN user_platform_roles r ON r.user_id=u.id "
                "WHERE u.status='active' AND r.role_name='platform_admin'"
            ).fetchone()[0]
            if active_admins <= 1:
                abort("Cannot reset the last active platform administrator through this command.")

        revoked = control.execute(
            "DELETE FROM auth_sessions WHERE user_id=?", (target["id"],)
        ).rowcount
        control.execute(
            "UPDATE users SET password_hash=?,updated_at=datetime('now') "
            "WHERE id=? AND status='active'",
            (new_password_hash, target["id"]),
        )
        firm = control.execute(
            "SELECT fm.firm_id FROM firm_memberships fm JOIN firms f ON f.id=fm.firm_id "
            "WHERE fm.user_id=? AND fm.firm_role='admin' AND fm.status='active' AND f.status='active' "
            "ORDER BY fm.firm_id LIMIT 1",
            (target["id"],),
        ).fetchone()
        control.execute(
            "INSERT INTO platform_security_events("
            "actor_user_id,target_user_id,firm_id,event_type,detail_json) "
            "VALUES(?,?,?,'password_reset_assisted_cli',?)",
            (
                actor_id, target["id"], int(firm["firm_id"]) if firm else None,
                json.dumps({
                    "method": "manage.py resetpw-assisted",
                    "reason": reason,
                    "operator_reference": operator_reference,
                    "change_reference": change_reference,
                    "sessions_revoked": revoked,
                }, sort_keys=True, separators=(",", ":")),
            ),
        )
        control.execute(
            "INSERT INTO mfa_security_events(actor_user_id,target_user_id,event_type,detail_json) "
            "VALUES(?,?,'administrator_reset',?)",
            (
                actor_id, target["id"],
                json.dumps({
                    "reason": "assisted_privileged_password_recovery",
                    "method": "manage.py resetpw-assisted",
                    "sessions_revoked": revoked,
                }, sort_keys=True, separators=(",", ":")),
            ),
        )
        control.commit()
        print(json.dumps({
            "status": "password_reset_assisted",
            "actor_user_id": actor_id,
            "target_user_id": int(target["id"]),
            "sessions_revoked": revoked,
            "event_type": "password_reset_assisted_cli",
        }, sort_keys=True))
    except SystemExit:
        raise
    except (DatabaseRuntimeError, sqlite3.Error, ValueError) as exc:
        try:
            runtime.control_connection().rollback()
        except Exception:
            pass
        raise SystemExit("Assisted privileged password recovery failed; no success is reported.") from exc
    finally:
        runtime.close_current_thread()


def backup(a):
    raise SystemExit(
        "Single-file backups are disabled. Use 'python manage.py backup-tenancy "
        "<directory> --quiesced' with the three profile-separated databases."
    )


def importlaws(a):
    _require_profile_separated_runtime("importlaws")
    with open(a.file, encoding="utf-8") as source:
        rows = [json.loads(line) for line in source if line.strip()]
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        c = runtime.legal_corpus_connection()
        total = 0
        for i in range(0, len(rows), 500):
            batch = rows[i:i + 500]
            c.executemany(
                "INSERT INTO legal_import_staging(law,article,text,norm,source) VALUES(?,?,?,?,?)",
                [(str(row["law"]), str(row["article"]), str(row["text"]), app.norm(str(row["text"])), row.get("source")) for row in batch],
            )
            total += len(batch)
        c.commit()
        print("staged for legal review:", total)
    except Exception as exc:
        try:
            runtime.legal_corpus_connection().rollback()
        except Exception:
            pass
        raise SystemExit("Legal import staging failed; no success is reported.") from exc
    finally:
        runtime.close_current_thread()


def backup_tenancy(a):
    if not app._separate_runtime_enabled():
        raise SystemExit("Set the three separate database paths before creating a tenancy bundle.")
    try:
        runtime = DatabaseRuntime.from_env()
        path = create_backup_bundle(
            runtime, _backup_fernet(), a.dir, keep=a.keep, quiesced=a.quiesced
        )
    except (DatabaseBundleError, DatabaseRuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print("Encrypted database bundle created:", path)
    print("The application must remain quiesced for the entire snapshot window.")


def verify_tenancy_backup(a):
    """Verify an encrypted tenancy bundle without changing configured database paths."""
    try:
        report = verify_backup_bundle(a.file, _backup_fernet())
    except (DatabaseBundleError, ValueError, OSError) as exc:
        raise SystemExit("Backup verification failed: " + str(exc)) from exc
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


def _recovery_archive_clients():
    bucket = os.environ.get("COPILOT_S3_RECOVERY_BUCKET", "").strip()
    region = os.environ.get("COPILOT_S3_RECOVERY_REGION", "").strip()
    key_id = os.environ.get("COPILOT_S3_RECOVERY_KMS_KEY_ID", "").strip()
    endpoint = os.environ.get("COPILOT_S3_RECOVERY_ENDPOINT_URL", "").strip() or None
    original_bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
    if not bucket or not region or not key_id or not original_bucket:
        raise SystemExit(
            "COPILOT_S3_RECOVERY_BUCKET, COPILOT_S3_RECOVERY_REGION, "
            "COPILOT_S3_RECOVERY_KMS_KEY_ID, and COPILOT_S3_BUCKET are required."
        )
    if bucket == original_bucket:
        raise SystemExit("Recovery archive bucket must be distinct from original-object storage.")
    try:
        import boto3
    except ImportError as exc:
        raise SystemExit("AWS SDK is not installed; install the locked requirements.") from exc
    return (
        boto3.client("s3", region_name=region, endpoint_url=endpoint),
        boto3.client("kms", region_name=region),
        bucket,
        key_id,
    )


def archive_upload_tenancy(a):
    """Upload an already-encrypted bundle and print its exact-version locator."""
    s3, kms, bucket, key_id = _recovery_archive_clients()
    try:
        locator = upload_encrypted_bundle(
            s3, kms, a.file, bucket=bucket, kms_key_id=key_id
        )
    except (DatabaseBundleError, OSError, ValueError) as exc:
        raise SystemExit("Recovery archive upload failed: " + str(exc)) from exc
    print(json.dumps(locator, sort_keys=True))


def archive_download_tenancy(a):
    """Download the exact version described by a protected locator JSON file."""
    locator_path = Path(a.locator).expanduser()
    if locator_path.is_symlink() or not locator_path.is_file():
        raise SystemExit("Recovery locator must be a regular non-symlink JSON file.")
    try:
        if locator_path.stat().st_size > 16384:
            raise ValueError("locator file is too large")
        locator = json.loads(locator_path.read_text(encoding="utf-8"))
        if not isinstance(locator, dict):
            raise ValueError("locator must be a JSON object")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit("Recovery locator could not be read safely.") from exc
    s3, kms, bucket, key_id = _recovery_archive_clients()
    try:
        downloaded = download_encrypted_bundle_version(
            s3, kms, locator, a.out, bucket=bucket, kms_key_id=key_id
        )
    except (DatabaseBundleError, OSError, ValueError) as exc:
        raise SystemExit("Recovery archive download failed: " + str(exc)) from exc
    print("Exact encrypted archive version downloaded:", downloaded)
    print("Next: verify with verify-backup-tenancy, then restore-tenancy to a new isolated directory.")


def _change_platform_role(a, *, grant: bool):
    """Change a platform role only when an active platform admin authorizes it."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Platform-role changes require separate-database mode.")
    role = getattr(a, "role", "")
    if role not in {"platform_admin", "platform_reviewer"}:
        raise SystemExit("Role must be platform_admin or platform_reviewer.")
    reason = a.reason.strip() if isinstance(a.reason, str) else ""
    if len(reason) < 8 or len(reason) > 500:
        raise SystemExit("--reason must contain 8 to 500 characters; do not include secrets.")
    actor_email = app.normalize_email(a.actor_email)
    target_email = app.normalize_email(a.target_email)
    if not actor_email or not target_email:
        raise SystemExit("Actor and target email addresses are required.")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        c = runtime.control_connection()
        c.execute("BEGIN IMMEDIATE")
        try:
            actor = c.execute(
                "SELECT id,status FROM users WHERE email_normalized=?", (actor_email,)
            ).fetchone()
            if actor is None or actor["status"] != "active":
                raise SystemExit("Actor must be an active global identity.")
            authorized = c.execute(
                "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
                (actor["id"],),
            ).fetchone()
            if not authorized:
                raise SystemExit("Only an active platform_admin can change platform roles.")
            target = c.execute(
                "SELECT id,status FROM users WHERE email_normalized=?", (target_email,)
            ).fetchone()
            if target is None:
                raise SystemExit("Target global identity was not found.")
            existing = c.execute(
                "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name=?",
                (target["id"], role),
            ).fetchone()
            if grant:
                if target["status"] != "active":
                    raise SystemExit("Disabled identities cannot receive platform roles.")
                if existing:
                    raise SystemExit("Target already has this platform role.")
                c.execute(
                    "INSERT INTO user_platform_roles(user_id,role_name,granted_by_user_id) VALUES(?,?,?)",
                    (target["id"], role, actor["id"]),
                )
                event_type = "platform_role_granted"
                action = "Granted"
            else:
                if not existing:
                    raise SystemExit("Target does not have this platform role.")
                if role == "platform_admin" and target["status"] == "active":
                    active_admins = c.execute(
                        "SELECT COUNT(DISTINCT u.id) FROM users u JOIN user_platform_roles r ON r.user_id=u.id "
                        "WHERE u.status='active' AND r.role_name='platform_admin'"
                    ).fetchone()[0]
                    if active_admins <= 1:
                        raise SystemExit("Cannot revoke the last active platform_admin.")
                c.execute(
                    "DELETE FROM user_platform_roles WHERE user_id=? AND role_name=?",
                    (target["id"], role),
                )
                event_type = "platform_role_revoked"
                action = "Revoked"
            c.execute(
                "INSERT INTO platform_security_events(actor_user_id,target_user_id,event_type,detail_json) "
                "VALUES(?,?,?,?)",
                (actor["id"], target["id"], event_type,
                 json.dumps({"role": role, "reason": reason, "method": "manage.py"}, sort_keys=True)),
            )
            c.commit()
        except SystemExit:
            if c.in_transaction:
                c.rollback()
            raise
        except sqlite3.Error as exc:
            if c.in_transaction:
                c.rollback()
            raise SystemExit("Platform-role change was not committed; database or audit write failed.") from exc
        print(f"{action} {role} for user_id={target['id']}; audit event recorded.")
    finally:
        runtime.close_current_thread()


def grant_platform_role(a):
    _change_platform_role(a, grant=True)


def revoke_platform_role(a):
    _change_platform_role(a, grant=False)


def bootstrap_platform_admin_cli(a):
    """One-time operator-controlled bootstrap for the first platform administrator."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Platform-admin bootstrap requires separate-database mode.")
    if not a.confirm_bootstrap:
        raise SystemExit("Explicit --confirm-bootstrap is required.")
    if isinstance(a.target_user_id, bool) or a.target_user_id <= 0:
        raise SystemExit("--target-user-id must be a positive integer.")
    reason = a.reason.strip() if isinstance(a.reason, str) else ""
    if len(reason) < 8 or len(reason) > 500:
        raise SystemExit("--reason must contain 8 to 500 characters; do not include secrets.")
    reference_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{2,63}$")
    operator_reference = a.operator_reference.strip() if isinstance(a.operator_reference, str) else ""
    change_reference = a.change_reference.strip() if isinstance(a.change_reference, str) else ""
    if not reference_pattern.fullmatch(operator_reference):
        raise SystemExit("--operator-reference must be a 3-64 character restricted identifier.")
    if not reference_pattern.fullmatch(change_reference):
        raise SystemExit("--change-reference must be a 3-64 character restricted identifier.")

    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        control = runtime.control_connection()
        control.execute("BEGIN IMMEDIATE")
        try:
            prior_bootstrap = control.execute(
                "SELECT 1 FROM platform_security_events "
                "WHERE event_type='platform_admin_bootstrap_cli' LIMIT 1"
            ).fetchone()
            if prior_bootstrap is not None:
                raise SystemExit("A successful platform-admin bootstrap is already recorded; use the reviewed break-glass process.")
            active_admin = control.execute(
                "SELECT 1 FROM users u JOIN user_platform_roles r ON r.user_id=u.id "
                "WHERE u.status='active' AND r.role_name='platform_admin' LIMIT 1"
            ).fetchone()
            if active_admin is not None:
                raise SystemExit("An active platform administrator already exists.")
            target = control.execute(
                "SELECT id,status FROM users WHERE id=?", (a.target_user_id,)
            ).fetchone()
            if target is None or target["status"] != "active":
                raise SystemExit("Target must be an existing active global identity.")
            membership = control.execute(
                "SELECT fm.firm_id FROM firm_memberships fm JOIN firms f ON f.id=fm.firm_id "
                "WHERE fm.user_id=? AND fm.firm_role='admin' AND fm.status='active' "
                "AND f.status='active' ORDER BY fm.firm_id LIMIT 1",
                (a.target_user_id,),
            ).fetchone()
            if membership is None:
                raise SystemExit("Target must have an active admin membership in an active firm.")
            control.execute(
                "INSERT INTO user_platform_roles(user_id,role_name,granted_by_user_id) "
                "VALUES(?,'platform_admin',NULL)",
                (a.target_user_id,),
            )
            control.execute(
                "INSERT INTO platform_security_events("
                "actor_user_id,target_user_id,firm_id,event_type,detail_json) "
                "VALUES(NULL,?,?,'platform_admin_bootstrap_cli',?)",
                (
                    a.target_user_id,
                    membership["firm_id"],
                    json.dumps({
                        "method": "manage.py bootstrap-platform-admin",
                        "reason": reason,
                        "operator_reference": operator_reference,
                        "change_reference": change_reference,
                    }, sort_keys=True),
                ),
            )
            control.commit()
        except SystemExit:
            if control.in_transaction:
                control.rollback()
            raise
        except sqlite3.Error as exc:
            if control.in_transaction:
                control.rollback()
            raise SystemExit(
                "Platform-admin bootstrap was not committed; role and audit event were rolled back."
            ) from exc
        print(json.dumps({
            "status": "bootstrapped",
            "target_user_id": int(a.target_user_id),
            "firm_id": int(membership["firm_id"]),
            "event_type": "platform_admin_bootstrap_cli",
        }, sort_keys=True))
    except (DatabaseRuntimeError, sqlite3.Error, ValueError) as exc:
        raise SystemExit("Platform-admin bootstrap could not safely complete.") from exc
    finally:
        runtime.close_current_thread()


def mfa_reset_cli(a):
    """Operator break-glass reset, authorized by a second active MFA-enabled platform admin."""
    if not app._separate_runtime_enabled():
        raise SystemExit("MFA recovery requires separate-database mode.")
    reason = a.reason
    if reason not in {"lost_device", "lost_recovery_codes", "suspected_compromise", "other"}:
        raise SystemExit("Choose a supported non-sensitive recovery reason.")
    actor_email = app.normalize_email(a.actor_email)
    target_email = app.normalize_email(a.target_email)
    if not actor_email or not target_email or actor_email == target_email:
        raise SystemExit("Actor and target must be different valid global identities.")
    actor_password = getpass.getpass("Platform administrator password: ")
    actor_code = getpass.getpass("Platform administrator TOTP code: ")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        c = runtime.control_connection()
        now = int(time.time())
        c.execute("BEGIN IMMEDIATE")

        def abort(message):
            c.rollback()
            raise SystemExit(message)

        actor = c.execute(
            "SELECT id,password_hash,status FROM users WHERE email_normalized=?", (actor_email,)
        ).fetchone()
        if actor is None or actor["status"] != "active" or not app.check_pw(actor_password, actor["password_hash"]):
            abort("Break-glass actor authentication failed.")
        authorized = c.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (actor["id"],),
        ).fetchone()
        if not authorized:
            abort("Only an active platform_admin can authorize an MFA reset.")
        target = c.execute(
            "SELECT id,status FROM users WHERE email_normalized=?", (target_email,)
        ).fetchone()
        if target is None or target["status"] != "active":
            abort("Target must be an active global identity.")
        target_credential = c.execute(
            "SELECT status FROM mfa_credentials WHERE user_id=?", (target["id"],)
        ).fetchone()
        if target_credential is None:
            abort("Target has no MFA credential to reset.")
        actor_credential = c.execute(
            "SELECT status,locked_until FROM mfa_credentials WHERE user_id=?", (actor["id"],)
        ).fetchone()
        if actor_credential is None or actor_credential["status"] != "enabled":
            abort("Break-glass actor must have enabled MFA.")
        if int(actor_credential["locked_until"]) > now:
            abort("Break-glass actor MFA is temporarily locked.")
        try:
            factor = app._mfa_verify_factor_in_transaction(
                c, int(actor["id"]), code=actor_code, recovery_code=None, now=now,
            )
        except app.MFAConfigurationError as exc:
            abort("MFA encryption key is unavailable or invalid.")
        if factor != "totp":
            app._mfa_record_failure(c, int(actor["id"]), now)
            c.commit()
            raise SystemExit("Break-glass actor MFA verification failed.")
        if c.execute(
            "SELECT 1 FROM user_platform_roles WHERE user_id=? AND role_name='platform_admin'",
            (target["id"],),
        ).fetchone():
            active_admins = c.execute(
                "SELECT COUNT(DISTINCT u.id) FROM users u JOIN user_platform_roles r ON r.user_id=u.id "
                "WHERE u.status='active' AND r.role_name='platform_admin'"
            ).fetchone()[0]
            if active_admins <= 1:
                abort("Cannot reset the last active platform administrator through this command.")
        used_at = datetime.fromtimestamp(now, timezone.utc).isoformat(timespec="seconds")
        c.execute(
            "UPDATE mfa_recovery_codes SET used_at=? WHERE user_id=? AND used_at IS NULL",
            (used_at, target["id"]),
        )
        c.execute("DELETE FROM mfa_credentials WHERE user_id=?", (target["id"],))
        revoked = c.execute("DELETE FROM auth_sessions WHERE user_id=?", (target["id"],)).rowcount
        c.execute(
            "INSERT INTO mfa_security_events(actor_user_id,target_user_id,event_type,detail_json) VALUES(?,?,?,?)",
            (actor["id"], target["id"], "administrator_reset",
             json.dumps({"reason": reason, "method": "manage.py mfa-reset", "sessions_revoked": revoked},
                        sort_keys=True, separators=(",", ":"))),
        )
        c.commit()
        print(json.dumps({
            "status": "mfa_reset",
            "actor_user_id": int(actor["id"]),
            "target_user_id": int(target["id"]),
            "sessions_revoked": revoked,
            "reason": reason,
            "next_step": "Target must sign in and complete MFA enrollment again under the active policy.",
        }, ensure_ascii=False, sort_keys=True))
    except SystemExit:
        raise
    except (DatabaseRuntimeError, sqlite3.Error, ValueError) as exc:
        raise SystemExit("MFA reset failed; no success is reported. Inspect the control-plane audit and database state.") from exc
    finally:
        runtime.close_current_thread()


def platform_audit(a):
    """Print a bounded read-only view of the control-plane security audit ledger."""
    if not app._separate_runtime_enabled():
        raise SystemExit("Platform audit is available only in separate-database mode.")
    if isinstance(a.limit, bool) or not isinstance(a.limit, int) or a.limit < 1 or a.limit > 500:
        raise SystemExit("--limit must be an integer between 1 and 500")
    for label in ("firm_id", "target_user_id"):
        value = getattr(a, label, None)
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
            raise SystemExit(f"--{label.replace('_', '-')} must be a positive integer")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        c = runtime.control_connection()
        clauses, params = [], []
        if a.event_type:
            clauses.append("event_type=?")
            params.append(a.event_type)
        if a.firm_id is not None:
            clauses.append("firm_id=?")
            params.append(a.firm_id)
        if a.target_user_id is not None:
            clauses.append("target_user_id=?")
            params.append(a.target_user_id)
        sql = "SELECT id,actor_user_id,target_user_id,firm_id,event_type,detail_json,created_at FROM platform_security_events"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(a.limit)
        items = []
        for row in c.execute(sql, params).fetchall():
            item = dict(row)
            try:
                item["detail"] = json.loads(item.pop("detail_json"))
            except (ValueError, TypeError):
                item["detail"] = {"unparsed": True}
                item.pop("detail_json", None)
            items.append(item)
        print(json.dumps({"items": items, "limit": a.limit}, ensure_ascii=False, sort_keys=True))
    finally:
        runtime.close_current_thread()


def mfa_audit(a):
    """Read a bounded, sanitized view of append-only MFA security events."""
    if not app._separate_runtime_enabled():
        raise SystemExit("MFA audit is available only in separate-database mode.")
    if isinstance(a.limit, bool) or not isinstance(a.limit, int) or not 1 <= a.limit <= 500:
        raise SystemExit("--limit must be an integer between 1 and 500")
    if a.target_user_id is not None and (
        isinstance(a.target_user_id, bool) or not isinstance(a.target_user_id, int) or a.target_user_id <= 0
    ):
        raise SystemExit("--target-user-id must be a positive integer")
    runtime = DatabaseRuntime.from_env()
    try:
        runtime.initialize()
        control = runtime.control_connection()
        clauses, params = [], []
        if a.target_user_id is not None:
            clauses.append("target_user_id=?")
            params.append(a.target_user_id)
        if a.event_type:
            clauses.append("event_type=?")
            params.append(a.event_type)
        query = (
            "SELECT id,actor_user_id,target_user_id,event_type,detail_json,created_at "
            "FROM mfa_security_events"
        )
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(a.limit)
        items = []
        for row in control.execute(query, params).fetchall():
            item = dict(row)
            try:
                item["detail"] = json.loads(item.pop("detail_json"))
            except (ValueError, TypeError):
                item.pop("detail_json", None)
                item["detail"] = {"unparsed": True}
            items.append(item)
        print(json.dumps({"items": items, "limit": a.limit}, ensure_ascii=False, sort_keys=True))
    finally:
        runtime.close_current_thread()


def restore_tenancy(a):
    try:
        restored = restore_backup_bundle(a.file, _backup_fernet(), a.target_root)
    except DatabaseBundleError as exc:
        raise SystemExit(str(exc)) from exc
    print("Verified bundle restored to a new directory.")
    print("COPILOT_CONTROL_DB=" + str(restored["control_plane"]))
    print("COPILOT_TENANT_DB_ROOT=" + str(restored["tenant_root"]))
    print("COPILOT_CORPUS_DB=" + str(restored["legal_corpus"]))
    print("Review the restored databases and rehearse application startup before switching paths.")


def restore(a):
    raise SystemExit(
        "Single-file restores are disabled. Use 'python manage.py restore-tenancy "
        "<bundle> --target-root <new-empty-directory>' after verifying the encrypted bundle."
    )


p = argparse.ArgumentParser()
sp = p.add_subparsers(dest="cmd", required=True)
x = sp.add_parser("adduser"); x.add_argument("name"); x.add_argument("email"); x.add_argument("role", choices=["admin", "lawyer", "junior"]); x.add_argument("--firm-id", type=int); x.set_defaults(f=adduser)
x = sp.add_parser("init-tenancy"); x.add_argument("--firm-name", required=True); x.add_argument("--owner-name", required=True); x.add_argument("--owner-email", required=True); x.set_defaults(f=init_tenancy)
x = sp.add_parser("provision-firm"); x.add_argument("name"); x.set_defaults(f=provision_firm_cli)
x = sp.add_parser("retry-failed-provisioning", help="Retry only a disabled firm with a failed tenant catalog entry")
x.add_argument("--firm-id", type=int, required=True)
x.add_argument("--reason", required=True)
x.add_argument("--operator-reference", required=True)
x.add_argument("--change-reference", required=True)
x.add_argument("--confirm-retry", action="store_true", help="Explicitly confirm this audited provisioning retry")
x.set_defaults(f=retry_failed_provisioning_cli)
x = sp.add_parser("reconcile-interrupted-provisioning", help="Reconcile a file-less interrupted firm provisioning attempt")
x.add_argument("--firm-id", type=int, required=True)
x.add_argument("--reason", required=True)
x.add_argument("--operator-reference", required=True)
x.add_argument("--change-reference", required=True)
x.add_argument("--confirm-workers-stopped", action="store_true", help="Confirm all app and background workers are stopped")
x.add_argument("--confirm-reconcile", action="store_true", help="Explicitly confirm this audited lifecycle reconciliation")
x.set_defaults(f=reconcile_interrupted_provisioning_cli)
x = sp.add_parser("addmembership"); x.add_argument("email"); x.add_argument("--firm-id", type=int, required=True); x.add_argument("--role", choices=["lawyer", "junior"], required=True); x.set_defaults(f=addmembership_cli)
x = sp.add_parser("disable-firm"); x.add_argument("firm_id", type=int); x.set_defaults(f=disable_firm_cli)
x = sp.add_parser("revoke-firm-invitations", help="Revoke pending/sent invitations for a disabled firm before offboarding")
x.add_argument("--firm-id", type=int, required=True)
x.add_argument("--reason", required=True)
x.add_argument("--operator-reference", required=True)
x.add_argument("--change-reference", required=True)
x.add_argument("--confirm-revoke", action="store_true", help="Explicitly confirm audited revocation of active invitations")
x.set_defaults(f=revoke_firm_invitations_cli)
x = sp.add_parser("resetpw"); x.add_argument("email"); x.set_defaults(f=resetpw)
sp.add_parser("genkey").set_defaults(f=lambda a: print(Fernet.generate_key().decode()))
sp.add_parser("gen-mfa-key", help="Generate a dedicated MFA secret-encryption key; never reuse BACKUP_KEY").set_defaults(
    f=lambda a: print(Fernet.generate_key().decode())
)
x = sp.add_parser("backup"); x.add_argument("dir"); x.add_argument("--keep", type=int, default=14); x.set_defaults(f=backup)
x = sp.add_parser("backup-tenancy"); x.add_argument("dir"); x.add_argument("--keep", type=int, default=14); x.add_argument("--quiesced", action="store_true", help="Assert application writes are paused for the full bundle snapshot"); x.set_defaults(f=backup_tenancy)
x = sp.add_parser("bootstrap-platform-admin", help="One-time CLI bootstrap of the first platform administrator")
x.add_argument("--target-user-id", type=int, required=True)
x.add_argument("--reason", required=True)
x.add_argument("--operator-reference", required=True)
x.add_argument("--change-reference", required=True)
x.add_argument("--confirm-bootstrap", action="store_true", help="Explicitly confirm this irreversible first-admin bootstrap")
x.set_defaults(f=bootstrap_platform_admin_cli)
x = sp.add_parser("grant-platform-role", help="Grant a platform role; requires an active platform_admin actor")
x.add_argument("--actor-email", required=True)
x.add_argument("--target-email", required=True)
x.add_argument("--role", required=True, choices=["platform_admin", "platform_reviewer"])
x.add_argument("--reason", required=True)
x.set_defaults(f=grant_platform_role)
x = sp.add_parser("revoke-platform-role", help="Revoke a platform role; cannot remove the last active platform_admin")
x.add_argument("--actor-email", required=True)
x.add_argument("--target-email", required=True)
x.add_argument("--role", required=True, choices=["platform_admin", "platform_reviewer"])
x.add_argument("--reason", required=True)
x.set_defaults(f=revoke_platform_role)
x = sp.add_parser("resetpw-assisted", help="MFA-authorized password reset for a privileged identity")
x.add_argument("--actor-email", required=True)
x.add_argument("--target-user-id", type=int, required=True)
x.add_argument("--reason", required=True)
x.add_argument("--operator-reference", required=True)
x.add_argument("--change-reference", required=True)
x.add_argument("--confirm-reset", action="store_true", help="Explicitly confirm this privileged password reset")
x.set_defaults(f=resetpw_assisted_cli)
x = sp.add_parser("mfa-reset", help="Reset a lost authenticator using a second active MFA-enabled platform administrator")
x.add_argument("--actor-email", required=True)
x.add_argument("--target-email", required=True)
x.add_argument("--reason", required=True, choices=["lost_device", "lost_recovery_codes", "suspected_compromise", "other"])
x.set_defaults(f=mfa_reset_cli)
x = sp.add_parser("mfa-audit", help="Read sanitized MFA security events on a trusted operator host")
x.add_argument("--limit", type=int, default=50)
x.add_argument("--target-user-id", type=int)
x.add_argument("--event-type", choices=["enrollment_started", "enrollment_completed", "login_verified", "recovery_code_used", "recovery_codes_rotated", "mfa_disabled", "administrator_reset", "verification_failed", "enrollment_failed"])
x.set_defaults(f=mfa_audit)
x = sp.add_parser("platform-audit", help="Read recent platform security events on a trusted operator host")
x.add_argument("--limit", type=int, default=50)
x.add_argument("--firm-id", type=int)
x.add_argument("--target-user-id", type=int)
x.add_argument("--event-type", choices=["password_reset_cli", "identity_created_cli", "password_changed_web", "firm_provisioned", "firm_provisioning_retried", "firm_provisioning_reconciled_failed", "firm_disabled", "membership_created", "membership_suspended", "initial_owner_bootstrapped", "platform_role_granted", "platform_role_revoked", "platform_admin_bootstrap_cli", "password_reset_assisted_cli"])
x.set_defaults(f=platform_audit)
x = sp.add_parser("restore-tenancy"); x.add_argument("file"); x.add_argument("--target-root", required=True); x.set_defaults(f=restore_tenancy)
x = sp.add_parser("verify-backup-tenancy", help="Verify an encrypted tenancy bundle using temporary protected storage"); x.add_argument("file"); x.set_defaults(f=verify_tenancy_backup)
x = sp.add_parser("archive-upload-tenancy", help="Upload an encrypted bundle to the separate versioned S3 recovery archive"); x.add_argument("file"); x.set_defaults(f=archive_upload_tenancy)
x = sp.add_parser("archive-download-tenancy", help="Download one exact S3 recovery archive version from a protected locator JSON file"); x.add_argument("locator"); x.add_argument("--out", required=True); x.set_defaults(f=archive_download_tenancy)
x = sp.add_parser("importlaws"); x.add_argument("file"); x.set_defaults(f=importlaws)
x = sp.add_parser("restore"); x.add_argument("file"); x.add_argument("out"); x.set_defaults(f=restore)
def main(argv=None):
    args = p.parse_args(argv)
    args.f(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
