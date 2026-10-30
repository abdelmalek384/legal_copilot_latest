@echo off
setlocal
cd /d "%~dp0"

echo Legal Copilot - Windows local setup

where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher not found. Install Python 3.12 from python.org and enable the Python Launcher.
  pause
  exit /b 1
)
py -3.12 --version >nul 2>nul
if errorlevel 1 (
  echo Python 3.12 is required. Install Python 3.12, then run this file again.
  pause
  exit /b 1
)

if defined COPILOT_DB (
  echo COPILOT_DB is set. This launcher refuses the legacy shared-database mode.
  echo Remove COPILOT_DB from your environment, then try again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto :failed
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto :failed

python -m pip install --upgrade pip
if errorlevel 1 goto :failed
python -m pip install -r requirements.txt
if errorlevel 1 goto :failed

if not exist "data\tenants" mkdir "data\tenants"
if not defined COPILOT_CONTROL_DB set "COPILOT_CONTROL_DB=%CD%\data\control_plane.sqlite3"
if not defined COPILOT_TENANT_DB_ROOT set "COPILOT_TENANT_DB_ROOT=%CD%\data\tenants"
if not defined COPILOT_CORPUS_DB set "COPILOT_CORPUS_DB=%CD%\data\legal_corpus.sqlite3"

python -c "from database_runtime import DatabaseRuntime; DatabaseRuntime.from_env().initialize()"
if errorlevel 1 goto :failed

python tools\bootstrap_first_firm.py
if errorlevel 1 goto :failed

echo.
echo Legal Copilot is starting on http://127.0.0.1:8000
echo Keep this window open. Press Ctrl+C here to stop the server.
python -m uvicorn app:app --host 127.0.0.1 --port 8000
goto :eof

:failed
echo.
echo Setup failed. No database reset or deletion was attempted.
pause
exit /b 1
