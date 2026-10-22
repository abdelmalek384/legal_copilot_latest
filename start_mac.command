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
if ! python -c "import app; raise SystemExit(0 if app.conn().execute('SELECT COUNT(*) FROM users').fetchone()[0] else 1)" >/dev/null 2>&1; then
  echo "لا يوجد حساب مستخدم بعد. أنشئ حساب المدير الأول."
  read -r -p "الاسم: " user_name
  read -r -p "البريد الإلكتروني: " user_email
  python manage.py adduser "$user_name" "$user_email" admin
fi
echo "سيفتح Legal Copilot على http://127.0.0.1:8000"
echo "لإيقافه، ارجع إلى هذه النافذة واضغط Control+C."
python -m uvicorn app:app --host 127.0.0.1 --port 8000
