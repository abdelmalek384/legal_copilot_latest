"""Admin commands. adduser: create an account. genkey: make a backup key. backup/restore: encrypted database backups.
Examples: python manage.py adduser "Ahmed" ahmed@firm.eg lawyer | BACKUP_KEY=... python manage.py backup backups --keep 14"""
import argparse, getpass, glob, json, os, sqlite3, tempfile, time
from cryptography.fernet import Fernet
import app


def read_password(prompt):
    print("ملاحظة: لن تظهر أحرف كلمة المرور أثناء الكتابة في الطرفية؛ هذا طبيعي.")
    pw = getpass.getpass(prompt)
    if len(pw) < 12: raise SystemExit("كلمة المرور يجب أن تكون 12 حرفا على الأقل.")
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
    os.makedirs(a.dir, exist_ok=True); tmp = os.path.join(a.dir, "tmp.db"); dst = sqlite3.connect(tmp)
    app.conn().backup(dst); dst.close()
    out = os.path.join(a.dir, time.strftime("backup-%Y%m%d-%H%M%S.db.enc"))
    with open(tmp, "rb") as f, open(out, "wb") as o: o.write(Fernet(os.environ["BACKUP_KEY"]).encrypt(f.read()))
    os.remove(tmp)
    for old in sorted(glob.glob(os.path.join(a.dir, "backup-*.enc")))[:-a.keep]: os.remove(old)
    print("saved", out)


def importlaws(a):
    rows = [json.loads(l) for l in open(a.file, encoding="utf-8") if l.strip()]
    print("imported", sum(app.import_law(app.conn(), rows[i:i + 500]) for i in range(0, len(rows), 500)))


def restore(a):
    # Authenticate and decrypt completely before touching the destination.
    with open(a.file, "rb") as source:
        plaintext = Fernet(os.environ["BACKUP_KEY"]).decrypt(source.read())
    destination = os.path.abspath(a.out)
    parent = os.path.dirname(destination) or "."
    fd, staged = tempfile.mkstemp(prefix=".restore-", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(plaintext)
            output.flush()
            os.fsync(output.fileno())
        os.replace(staged, destination)
    finally:
        if os.path.exists(staged):
            os.remove(staged)


p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
x = sp.add_parser("adduser"); x.add_argument("name"); x.add_argument("email"); x.add_argument("role", choices=["admin", "lawyer", "junior"]); x.set_defaults(f=adduser)
x = sp.add_parser("resetpw"); x.add_argument("email"); x.set_defaults(f=resetpw)
sp.add_parser("genkey").set_defaults(f=lambda a: print(Fernet.generate_key().decode()))
x = sp.add_parser("backup"); x.add_argument("dir"); x.add_argument("--keep", type=int, default=14); x.set_defaults(f=backup)
x = sp.add_parser("importlaws"); x.add_argument("file"); x.set_defaults(f=importlaws)
x = sp.add_parser("restore"); x.add_argument("file"); x.add_argument("out"); x.set_defaults(f=restore)
a = p.parse_args(); a.f(a)
