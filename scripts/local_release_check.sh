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
  bandit_report=$(mktemp)
  if bandit -r app.py database_runtime.py tenant_catalog.py tools -ll -ii -f json -o "$bandit_report"; then
    names+=("Bandit security scan")
    statuses+=("PASS")
    details+=("no findings at configured severity/confidence")
  else
    bandit_rc=$?
    if python - "$bandit_report" <<'PY'
import json
import sys
with open(sys.argv[1], encoding="utf-8") as handle:
    report = json.load(handle)
high = [item for item in report.get("results", []) if item.get("issue_severity") == "HIGH"]
print("Bandit findings:", len(report.get("results", [])))
for item in report.get("results", []):
    print(item.get("issue_severity"), item.get("issue_confidence"), item.get("test_id"), item.get("filename"), item.get("line_number"))
raise SystemExit(1 if high else 0)
PY
    then
      names+=("Bandit security scan")
      statuses+=("PASS")
      details+=("no HIGH severity findings (lower findings reported)")
    else
      names+=("Bandit security scan")
      statuses+=("FAIL")
      details+=("HIGH severity finding(s); Bandit exit $bandit_rc")
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
