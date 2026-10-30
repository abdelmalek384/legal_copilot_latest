#!/usr/bin/env python3
"""Prompt for the first firm only when no active firm owner exists.

The helper delegates account creation to the reviewed init-tenancy CLI. It
passes user input as an argument list (never through a shell) and does not
create, migrate, reset, or delete database files itself.
"""
from __future__ import annotations

import subprocess
import sys

from database_runtime import DatabaseRuntime


ACTIVE_OWNER_SQL = (
    "SELECT COUNT(*) FROM users u "
    "JOIN firm_memberships fm ON fm.user_id=u.id "
    "JOIN firms f ON f.id=fm.firm_id "
    "WHERE u.status='active' AND fm.status='active' AND f.status='active'"
)


def build_init_command(python_executable: str, firm_name: str, owner_name: str, owner_email: str) -> list[str]:
    """Build a shell-free command for the existing tenancy bootstrap CLI."""
    return [
        python_executable,
        "manage.py",
        "init-tenancy",
        "--firm-name",
        firm_name.strip(),
        "--owner-name",
        owner_name.strip(),
        "--owner-email",
        owner_email.strip(),
    ]


def has_active_owner() -> bool:
    runtime = DatabaseRuntime.from_env()
    control = runtime.control_connection()
    row = control.execute(ACTIVE_OWNER_SQL).fetchone()
    return bool(row and int(row[0]) > 0)


def main() -> int:
    try:
        if has_active_owner():
            print("يوجد بالفعل مدير نشط لمكتب؛ لا يلزم إجراء تهيئة. / An active firm owner already exists; no bootstrap action is needed.")
            return 0
    except Exception as exc:
        print(f"تعذر فحص قاعدة التحكم بأمان ({type(exc).__name__}). / Could not safely inspect the control plane ({type(exc).__name__}).", file=sys.stderr)
        return 2

    print("لم يتم العثور على مدير نشط؛ أنشئ المكتب ومديره الأول. / No active firm owner was found; create the first firm administrator.")
    firm_name = input("اسم المكتب / Firm name: ").strip()
    owner_name = input("اسم المدير / Owner name: ").strip()
    owner_email = input("البريد الإلكتروني / Owner email: ").strip()
    if not firm_name or not owner_name or not owner_email:
        print("اسم المكتب واسم المدير والبريد الإلكتروني مطلوبة. / Firm name, owner name, and owner email are all required.", file=sys.stderr)
        return 2

    command = build_init_command(sys.executable, firm_name, owner_name, owner_email)
    result = subprocess.run(command, check=False)
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
