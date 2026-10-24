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
    if len(pw) < 12:
        raise SystemExit("كلمة المرور يجب أن تكون 12 حرفا على الأقل.")
    return pw


def adduser(a):
    pw = read_password("كلمة المرور (12 حرفا على الأقل): ")
    c = app.conn()
    try:
        c.execute("INSERT INTO users(name,email,pw,role) VALUES(?,?,?,?)",
                  (a.name.strip(), a.email.strip().lower(), app.hash_pw(pw), a.role))
        c.commit()
    except Exception as e:
        c.rollback()
        raise SystemExit("تعذر إنشاء الحساب. تحقق من أن البريد الإلكتروني غير مستخدم بالفعل. التفاصيل: " + str(e))
    print("تم إنشاء الحساب. افتح التطبيق وسجّل الدخول بالبريد وكلمة المرور.")


def resetpw(a):
    pw = read_password("كلمة المرور الجديدة: ")
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
    print("imported", sum(app.import_law(app.conn(), rows[i:i + 500]) for i in range(0, len(rows), 500)))


def restore(a):
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
x = sp.add_parser("adduser"); x.add_argument("name"); x.add_argument("email"); x.add_argument("role", choices=["admin", "lawyer", "junior"]); x.set_defaults(f=adduser)
x = sp.add_parser("resetpw"); x.add_argument("email"); x.set_defaults(f=resetpw)
sp.add_parser("genkey").set_defaults(f=lambda a: print(Fernet.generate_key().decode()))
x = sp.add_parser("backup"); x.add_argument("dir"); x.add_argument("--keep", type=int, default=14); x.set_defaults(f=backup)
x = sp.add_parser("importlaws"); x.add_argument("file"); x.set_defaults(f=importlaws)
x = sp.add_parser("restore"); x.add_argument("file"); x.add_argument("out"); x.set_defaults(f=restore)
a = p.parse_args(); a.f(a)
