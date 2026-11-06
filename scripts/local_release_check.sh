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
  local output rc
  names+=("$label")
  echo
  echo "==> $label"
  if output=$("$@" 2>&1); then
    statuses+=("PASS")
    details+=("completed")
    printf '%s\n' "$output"
  else
    rc=$?
    statuses+=("FAIL")
    details+=("exit $rc")
    printf '%s\n' "$output"
  fi
}

run_check "Python test suite (unittest discovery)" python -m unittest discover -s tests -p 'test_*.py' -v

if command -v actionlint >/dev/null 2>&1; then
  run_check "GitHub Actions workflow lint" actionlint
else
  names+=("GitHub Actions workflow lint")
  statuses+=("BLOCKED")
  details+=("actionlint is not installed")
fi

if command -v bandit >/dev/null 2>&1; then
  run_check "Bandit security scan" bandit -r app.py database_runtime.py tenant_catalog.py tools -ll -ii
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
