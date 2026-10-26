"""Admin commands for account maintenance and encrypted database backups."""
import argparse
import getpass
import glob
import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path

from cryptography.fernet import Fernet
import app
from database_runtime import DatabaseRuntime, DatabaseRuntimeError
from database_backup import DatabaseBundleError, create_backup_bundle, restore_backup_bundle, verify_backup_bundle


def _backup_fernet():
    key = os.environ.get("BACKUP_KEY")
    if not key:
        raise SystemExit("BACKUP_KEY is required; generate one with: python manage.py genkey")
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except (ValueError, TypeError) as exc:
        raise SystemExit("BACKUP_KEY is invalid; generate a Fernet key with: python manage.py genkey") from exc


def _validate_sqlite(path):
    """Reject authenticated but corrupt/non-SQLite payloads before restore."""
    connection = None
    try:
        uri = Path(path).resolve().as_uri() + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True, timeout=5)
        result = connection.execute("PRAGMA quick_check").fetchall()
        if len(result) != 1 or result[0][0] != "ok":
            raise SystemExit("Restore rejected: SQLite quick_check did not pass.")
    except sqlite3.Error as exc:
        raise SystemExit("Restore rejected: decrypted payload is not a readable SQLite database.") from exc
    finally:
        if connection is not None:
            connection.close()


def read_password(prompt):
    print("ملاحظة: لن تظهر أحرف كلمة المرور أثناء الكتابة في الطرفية؛ هذا طبيعي.")
    pw = getpass.getpass(prompt)
    try:
        return app.validate_password_strength(pw)
    except ValueError as exc:
        raise SystemExit("كلمة المرور ضعيفة: " + str(exc)) from exc


def adduser(a):
    pw = read_password("كلمة المرور (12 حرفا على الأقل): ")
    if app._separate_runtime_enabled():
        if not a.firm_id:
            raise SystemExit("Separate-database mode requires --firm-id; firm roles do not grant platform roles.")
        runtime = DatabaseRuntime.from_env()
        runtime.initialize()
        c = runtime.control_connection()
        try:
            c.execute("BEGIN IMMEDIATE")
            firm = c.execute(
                "SELECT status FROM firms WHERE id=?", (a.firm_id,)
            ).fetchone()
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
        except Exception as e:
            c.rollback()
            raise SystemExit("تعذر إنشاء الحساب أو عضوية المكتب. تحقق من البريد ورقم المكتب. التفاصيل: " + str(e))
        print("تم إنشاء الحساب وربطه بالمكتب المحدد. صلاحيات المنصة مستقلة عن دور المكتب.")
        return
    c = app.conn()
    try:
        c.execute("INSERT INTO users(name,email,pw,role) VALUES(?,?,?,?)",
                  (a.name.strip(), a.email.strip().lower(), app.hash_pw(pw), a.role))
        c.commit()
    except Exception as e:
        c.rollback()
        raise SystemExit("تعذر إنشاء الحساب. تحقق من أن البريد الإلكتروني غير مستخدم بالفعل. التفاصيل: " + str(e))
    print("تم إنشاء الحساب. افتح التطبيق وسجّل الدخول بالبريد وكلمة المرور.")


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


def resetpw(a):
    pw = read_password("كلمة المرور الجديدة: ")
    if app._separate_runtime_enabled():
        runtime = DatabaseRuntime.from_env()
        try:
            runtime.initialize()
            c = runtime.control_connection()
            email = app.normalize_email(a.email)
            c.execute("BEGIN IMMEDIATE")
            account = c.execute("SELECT id FROM users WHERE email_normalized=?", (email,)).fetchone()
            if not account:
                c.rollback()
                raise SystemExit("لا يوجد حساب بهذا البريد الإلكتروني.")
            c.execute(
                "UPDATE users SET password_hash=?,updated_at=datetime('now') WHERE id=?",
                (app.hash_pw(pw), account["id"]),
            )
            c.execute("DELETE FROM auth_sessions WHERE user_id=?", (account["id"],))
            c.execute(
                "INSERT INTO platform_security_events(actor_user_id,target_user_id,event_type,detail_json) "
                "VALUES(NULL,?,'password_reset_cli',?)",
                (account["id"], json.dumps({"method": "manage.py resetpw", "sessions_revoked": True}, sort_keys=True)),
            )
            c.commit()
            print("تم تحديث كلمة المرور وإبطال جميع الجلسات؛ سجّل الدخول من جديد.")
            return
        except Exception:
            try:
                runtime.control_connection().rollback()
            except Exception:
                pass
            raise
        finally:
            runtime.close_current_thread()
    c = app.conn()
    email = a.email.strip().lower()
    c.execute("BEGIN IMMEDIATE")
    account = c.execute("SELECT id,firm_id FROM users WHERE email=?", (email,)).fetchone()
    if not account:
        c.rollback()
        raise SystemExit("لا يوجد حساب بهذا البريد الإلكتروني.")
    c.execute("UPDATE users SET pw=? WHERE id=?", (app.hash_pw(pw), account["id"]))
    c.execute("DELETE FROM auth_sessions WHERE user_id=?", (account["id"],))
    c.execute("INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(?,?,?)",
              (account["firm_id"], account["id"], "password_reset_cli_sessions_revoked"))
    c.commit()
    print("تم تحديث كلمة المرور؛ سجّل الدخول من جديد.")


def backup(a):
    if app._separate_runtime_enabled():
        raise SystemExit("Refusing single-file backup in separate-database mode. A verified multi-database backup bundle is required.")
    if a.keep < 1:
        raise SystemExit("--keep must be at least 1")
    cipher = _backup_fernet()
    backup_dir = Path(a.dir).expanduser().resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    if not backup_dir.is_dir():
        raise SystemExit("Backup destination must be a directory")

    db_fd, db_stage = tempfile.mkstemp(prefix=".backup-db-", suffix=".tmp", dir=backup_dir)
    os.close(db_fd)
    encrypted_stage = None
    dst = None
    try:
        dst = sqlite3.connect(db_stage, timeout=30)
        app.conn().backup(dst)
        dst.close()
        dst = None
        _validate_sqlite(db_stage)

        with open(db_stage, "rb") as source:
            token = cipher.encrypt(source.read())
        out = backup_dir / f"backup-{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns()}.db.enc"
        fd, encrypted_stage = tempfile.mkstemp(prefix=".backup-enc-", suffix=".tmp", dir=backup_dir)
        with os.fdopen(fd, "wb") as output:
            output.write(token)
            output.flush()
            os.fsync(output.fileno())
        os.replace(encrypted_stage, out)
        encrypted_stage = None

        old_backups = sorted(
            (Path(name) for name in glob.glob(str(backup_dir / "backup-*.enc")) if Path(name) != out),
            key=lambda item: item.name,
        )
        for old in old_backups[:max(0, len(old_backups) + 1 - a.keep)]:
            old.unlink(missing_ok=True)
        print("saved", out)
    finally:
        if dst is not None:
            dst.close()
        Path(db_stage).unlink(missing_ok=True)
        if encrypted_stage and os.path.exists(encrypted_stage):
            os.remove(encrypted_stage)


def importlaws(a):
    with open(a.file, encoding="utf-8") as source:
        rows = [json.loads(line) for line in source if line.strip()]
    if app._separate_runtime_enabled():
        runtime = DatabaseRuntime.from_env()
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
        return
    print("imported", sum(app.import_law(app.conn(), rows[i:i + 500]) for i in range(0, len(rows), 500)))


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
    if app._separate_runtime_enabled():
        raise SystemExit("Refusing single-file restore in separate-database mode. A verified multi-database restore bundle is required.")
    cipher = _backup_fernet()
    with open(a.file, "rb") as source:
        plaintext = cipher.decrypt(source.read())

    destination = Path(a.out).expanduser().resolve()
    parent = destination.parent
    if not parent.is_dir():
        raise SystemExit("Restore destination directory must already exist.")
    fd, staged = tempfile.mkstemp(prefix=".restore-", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(plaintext)
            output.flush()
            os.fsync(output.fileno())
        _validate_sqlite(staged)
        os.replace(staged, destination)
    finally:
        if os.path.exists(staged):
            os.remove(staged)


p = argparse.ArgumentParser()
sp = p.add_subparsers(dest="cmd", required=True)
x = sp.add_parser("adduser"); x.add_argument("name"); x.add_argument("email"); x.add_argument("role", choices=["admin", "lawyer", "junior"]); x.add_argument("--firm-id", type=int); x.set_defaults(f=adduser)
x = sp.add_parser("init-tenancy"); x.add_argument("--firm-name", required=True); x.add_argument("--owner-name", required=True); x.add_argument("--owner-email", required=True); x.set_defaults(f=init_tenancy)
x = sp.add_parser("provision-firm"); x.add_argument("name"); x.set_defaults(f=provision_firm_cli)
x = sp.add_parser("addmembership"); x.add_argument("email"); x.add_argument("--firm-id", type=int, required=True); x.add_argument("--role", choices=["lawyer", "junior"], required=True); x.set_defaults(f=addmembership_cli)
x = sp.add_parser("disable-firm"); x.add_argument("firm_id", type=int); x.set_defaults(f=disable_firm_cli)
x = sp.add_parser("resetpw"); x.add_argument("email"); x.set_defaults(f=resetpw)
sp.add_parser("genkey").set_defaults(f=lambda a: print(Fernet.generate_key().decode()))
x = sp.add_parser("backup"); x.add_argument("dir"); x.add_argument("--keep", type=int, default=14); x.set_defaults(f=backup)
x = sp.add_parser("backup-tenancy"); x.add_argument("dir"); x.add_argument("--keep", type=int, default=14); x.add_argument("--quiesced", action="store_true", help="Assert application writes are paused for the full bundle snapshot"); x.set_defaults(f=backup_tenancy)
x = sp.add_parser("platform-audit", help="Read recent platform security events on a trusted operator host")
x.add_argument("--limit", type=int, default=50)
x.add_argument("--firm-id", type=int)
x.add_argument("--target-user-id", type=int)
x.add_argument("--event-type", choices=["password_reset_cli", "firm_provisioned", "firm_disabled", "membership_created", "initial_owner_bootstrapped", "platform_role_granted", "platform_role_revoked"])
x.set_defaults(f=platform_audit)
x = sp.add_parser("restore-tenancy"); x.add_argument("file"); x.add_argument("--target-root", required=True); x.set_defaults(f=restore_tenancy)
x = sp.add_parser("verify-backup-tenancy", help="Verify an encrypted tenancy bundle using temporary protected storage"); x.add_argument("file"); x.set_defaults(f=verify_tenancy_backup)
x = sp.add_parser("importlaws"); x.add_argument("file"); x.set_defaults(f=importlaws)
x = sp.add_parser("restore"); x.add_argument("file"); x.add_argument("out"); x.set_defaults(f=restore)
def main(argv=None):
    args = p.parse_args(argv)
    args.f(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
