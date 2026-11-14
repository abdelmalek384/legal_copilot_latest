#!/usr/bin/env bash
# Local release gate used when hosted CI runners are unavailable.
# Run from the repository root in the supported Python 3.12 environment.
set -uo pipefail

if [[ ! -f "tools/deployment_preflight.py" || ! -d "tests" ]]; then
  echo "Run this script from the repository root." >&2
  exit 2
fi

names=()
statuses=()
details=()

run_check() {
  local label="$1"; shift
  local log rc
  log=$(mktemp)
  names+=("$label")
  echo
  echo "==> $label"
  if "$@" 2>&1 | tee "$log"; then
    statuses+=("PASS")
    details+=("completed")
  else
    rc=$?
    statuses+=("FAIL")
    details+=("exit $rc")
  fi
  rm -f "$log"
}

run_check "Full CI-invoked Python test suite" python tools/run_local_test_suite.py
run_check "Focused security regression matrix" bash scripts/security_regression_check.sh

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  run_check "Placeholder-only production Compose validation" bash -c '
    set -eu
    test ! -e .env.production || {
      echo ".env.production exists; refusing to overwrite it." >&2
      exit 2
    }
    tmpdir=$(mktemp -d)
    trap "rm -rf \"$tmpdir\"" EXIT
    cp .env.production.example "$tmpdir/.env.production"
    LEGAL_COPILOT_IMAGE_TAG=compose-contract-check \
      docker compose --env-file "$tmpdir/.env.production" -f compose.production.yaml config --quiet
  '
else
  names+=("Placeholder-only production Compose validation")
  statuses+=("BLOCKED")
  details+=("Docker Compose plugin is not installed")
fi

if command -v actionlint >/dev/null 2>&1; then
  run_check "GitHub Actions workflow lint" actionlint
else
  names+=("GitHub Actions workflow lint")
  statuses+=("BLOCKED")
  details+=("actionlint is not installed")
fi

if command -v bandit >/dev/null 2>&1; then
  bandit_report=$(mktemp)
  if bandit -r app.py database_runtime.py tenant_catalog.py tools -ll -ii -f json -o "$bandit_report"; then
    names+=("Bandit security scan")
    statuses+=("PASS")
    details+=("no findings at configured severity/confidence")
  else
    bandit_rc=$?
    if [[ -s "$bandit_report" ]]; then
      echo "Bandit JSON report:"
      cat "$bandit_report"
    fi
    if bandit_findings=$(python - "$bandit_report" <<'PY'
import json
import sys
try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        report = json.load(handle)
    results = report.get("results")
    if not isinstance(results, list):
        raise ValueError("Bandit report has no results list")
except (OSError, ValueError, json.JSONDecodeError):
    raise SystemExit(2)
print(len(results))
PY
    ); then
      if [[ "$bandit_findings" =~ ^[0-9]+$ ]] && (( bandit_findings > 0 )); then
        names+=("Bandit security scan")
        statuses+=("FAIL")
        details+=("$bandit_findings finding(s) at configured severity/confidence; Bandit exit $bandit_rc")
      else
        names+=("Bandit security scan")
        statuses+=("BLOCKED")
        details+=("Bandit exited $bandit_rc without reported findings; inspect tool execution")
      fi
    else
      names+=("Bandit security scan")
      statuses+=("BLOCKED")
      details+=("Bandit exited $bandit_rc and produced no valid JSON report")
    fi
  fi
  rm -f "$bandit_report"
else
  names+=("Bandit security scan")
  statuses+=("BLOCKED")
  details+=("install Bandit in the active environment")
fi

if command -v pip-audit >/dev/null 2>&1; then
  if [[ -f requirements-py312.lock ]]; then
    run_check "Dependency audit (hash-locked deployment set)" pip-audit --strict --progress-spinner off -r requirements-py312.lock
  else
    run_check "Dependency audit (requirements)" pip-audit --strict --progress-spinner off -r requirements.txt
  fi
else
  names+=("Dependency audit")
  statuses+=("BLOCKED")
  details+=("install pip-audit in the active environment")
fi

run_check "Strict deployment preflight" python tools/deployment_preflight.py --strict

root_artifacts=$(find . -maxdepth 1 -type f \( -iname '*.patch' -o -iname '*.diff' -o -iname '*.csv' \) -print)
names+=("Repository-root patch/diff/CSV hygiene")
if [[ -z "$root_artifacts" ]]; then
  statuses+=("PASS")
  details+=("no stray patch, diff or CSV files at repository root")
else
  statuses+=("FAIL")
  details+=("remove or relocate: $(printf '%s' "$root_artifacts" | tr '\n' ' ')")
fi

echo
echo "================ LOCAL RELEASE CHECK ================"
printf '%-43s %-10s %s\n' "CHECK" "RESULT" "DETAIL"
printf '%-43s %-10s %s\n' "-------------------------------------------" "----------" "------------------------------"
failed=0
for i in "${!names[@]}"; do
  printf '%-43s %-10s %s\n' "${names[$i]}" "${statuses[$i]}" "${details[$i]}"
  if [[ "${statuses[$i]}" != "PASS" ]]; then failed=1; fi
done
echo "====================================================="
if [[ $failed -eq 0 ]]; then
  echo "All local release checks passed."
else
  echo "Release gate is NOT PASS. Resolve failures and blocked prerequisites; do not treat missing tools or credentials as passes."
fi
exit "$failed"
