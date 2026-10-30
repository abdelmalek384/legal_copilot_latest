#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Legal Copilot — إعداد وتشغيل محلي على هذا الجهاز"
if ! command -v python3 >/dev/null 2>&1; then
  echo "لم يتم العثور على Python 3. ثبّته من python.org ثم أعد المحاولة."
  read -r -p "اضغط Enter للإغلاق..."
  exit 1
fi
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)'; then
  echo "يلزم Python 3.12 أو أحدث. / Python 3.12 or newer is required."
  read -r -p "اضغط Enter للإغلاق..."
  exit 1
fi
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
if [ ! -x ".venv/bin/python" ] || ! ".venv/bin/python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)'; then
  echo "بيئة .venv الحالية لا تستخدم Python 3.12 أو أحدث. أعد تسميتها يدوياً بعد حفظ أي تغييرات؛ لن يحذفها هذا المشغل. / Existing .venv must use Python 3.12 or newer. Rename it manually after preserving any changes; this launcher will not delete it."
  read -r -p "اضغط Enter للإغلاق..."
  exit 1
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

python tools/bootstrap_first_firm.py
echo "سيفتح Legal Copilot على http://127.0.0.1:8000"
echo "لإيقافه، ارجع إلى هذه النافذة واضغط Control+C."
python -m uvicorn app:app --host 127.0.0.1 --port 8000
