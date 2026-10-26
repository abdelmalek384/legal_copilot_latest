#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Legal Copilot — إعداد وتشغيل محلي على هذا الجهاز"
if ! command -v python3 >/dev/null 2>&1; then
  echo "لم يتم العثور على Python 3. ثبّته من python.org ثم أعد المحاولة."
  read -r -p "اضغط Enter للإغلاق..."
  exit 1
fi
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Fresh-install architecture: control plane, per-firm databases, and shared corpus
# must have distinct paths. Do not set COPILOT_DB here; that is legacy compatibility mode.
mkdir -p "data/tenants"
export COPILOT_CONTROL_DB="${COPILOT_CONTROL_DB:-$PWD/data/control_plane.sqlite3}"
export COPILOT_TENANT_DB_ROOT="${COPILOT_TENANT_DB_ROOT:-$PWD/data/tenants}"
export COPILOT_CORPUS_DB="${COPILOT_CORPUS_DB:-$PWD/data/legal_corpus.sqlite3}"
python -c "from database_runtime import DatabaseRuntime; DatabaseRuntime.from_env().initialize()"

if ! python -c "from database_runtime import DatabaseRuntime; r=DatabaseRuntime.from_env(); c=r.control_connection(); n=c.execute(\"SELECT COUNT(*) FROM users u JOIN firm_memberships fm ON fm.user_id=u.id JOIN firms f ON f.id=fm.firm_id WHERE u.status='active' AND fm.status='active' AND f.status='active'\").fetchone()[0]; raise SystemExit(0 if n else 1)" >/dev/null 2>&1; then
  echo "لا يوجد حساب مرتبط بمكتب نشط. أنشئ المكتب ومديره الأول."
  read -r -p "اسم المكتب: " firm_name
  read -r -p "اسم المدير الأول: " user_name
  read -r -p "البريد الإلكتروني: " user_email
  python manage.py init-tenancy --firm-name "$firm_name" --owner-name "$user_name" --owner-email "$user_email"
fi
echo "سيفتح Legal Copilot على http://127.0.0.1:8000"
echo "لإيقافه، ارجع إلى هذه النافذة واضغط Control+C."
python -m uvicorn app:app --host 127.0.0.1 --port 8000
