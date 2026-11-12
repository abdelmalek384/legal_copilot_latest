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
    names+=("Bandit security scan")
    statuses+=("FAIL")
    details+=("Bandit reported findings or could not complete (exit $bandit_rc); inspect the JSON report before rerunning")
    if [[ -s "$bandit_report" ]]; then
      echo "Bandit JSON report (nonzero exit is not downgraded to PASS):"
      cat "$bandit_report"
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
