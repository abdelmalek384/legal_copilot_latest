#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Legal Copilot — إعداد وتشغيل محلي على هذا الجهاز"
# The dependency lock and supported release runtime target Python 3.12 exactly.
# Reuse an existing 3.12 venv; never replace or delete an existing environment.
if [ ! -d ".venv" ]; then
  if command -v python3.12 >/dev/null 2>&1; then
    PYTHON_BIN="python3.12"
  elif command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)'; then
    PYTHON_BIN="python3"
  else
    echo "يلزم Python 3.12 تحديداً. ثبّت Python 3.12 ثم أعد المحاولة. / Python 3.12 is required; newer versions are not assumed compatible."
    read -r -p "اضغط Enter للإغلاق..."
    exit 1
  fi
  "$PYTHON_BIN" -m venv .venv
fi
if [ ! -x ".venv/bin/python" ] || ! ".venv/bin/python" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)'; then
  echo "بيئة .venv الحالية لا تستخدم Python 3.12. احفظها ثم أعد تسميتها يدوياً؛ لن يحذفها هذا المشغل. / Existing .venv must use Python 3.12 exactly. Preserve or rename it manually; this launcher will not delete it."
  read -r -p "اضغط Enter للإغلاق..."
  exit 1
fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Fresh-install architecture: control plane, per-firm databases, and shared corpus
# must have distinct paths. Do not set COPILOT_DB; the application rejects it in every environment.
mkdir -p "data/tenants"
export COPILOT_CONTROL_DB="${COPILOT_CONTROL_DB:-$PWD/data/control_plane.sqlite3}"
export COPILOT_TENANT_DB_ROOT="${COPILOT_TENANT_DB_ROOT:-$PWD/data/tenants}"
export COPILOT_CORPUS_DB="${COPILOT_CORPUS_DB:-$PWD/data/legal_corpus.sqlite3}"
python -c "from database_runtime import DatabaseRuntime; DatabaseRuntime.from_env().initialize()"

python tools/bootstrap_first_firm.py
echo "سيفتح Legal Copilot على http://127.0.0.1:8000"
echo "لإيقافه، ارجع إلى هذه النافذة واضغط Control+C."
python -m uvicorn app:app --host 127.0.0.1 --port 8000
