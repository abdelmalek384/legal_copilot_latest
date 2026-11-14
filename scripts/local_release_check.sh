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

if python -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)' 2>/dev/null; then
  names+=("Supported Python interpreter")
  statuses+=("PASS")
  details+=("Python 3.12")
  run_check "Full CI-invoked Python test suite" python tools/run_local_test_suite.py
  run_check "Focused security regression matrix" bash scripts/security_regression_check.sh
  run_check "Encrypted multi-tenant backup/restore recovery drill" python tests/test_database_recovery_drill.py
else
  names+=("Supported Python interpreter")
  statuses+=("BLOCKED")
  details+=("Python 3.12 is required; Python test gates were not started")
  for label in "Full CI-invoked Python test suite" "Focused security regression matrix" "Encrypted multi-tenant backup/restore recovery drill"; do
    names+=("$label")
    statuses+=("BLOCKED")
    details+=("requires Python 3.12")
  done
fi

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
    # Keep project-relative build and bind-mount paths anchored at the repository,
    # while redirecting the service env_file to the isolated placeholder copy.
    sed "s|      - .env.production|      - $tmpdir/.env.production|" \
      compose.production.yaml > "$tmpdir/compose.production.yaml"
    LEGAL_COPILOT_IMAGE_TAG=compose-contract-check \
      docker compose --project-directory "$PWD" --env-file "$tmpdir/.env.production" \
        -f "$tmpdir/compose.production.yaml" config --quiet
  '
else
  names+=("Placeholder-only production Compose validation")
  statuses+=("BLOCKED")
  details+=("Docker Compose plugin is not installed")
fi

if command -v pip-compile >/dev/null 2>&1; then
  run_check "Python 3.12 dependency lock drift check" bash -c '
    set -eu
    tmpdir=$(mktemp -d)
    trap "rm -rf \"$tmpdir\"" EXIT
    pip-compile --resolver=backtracking --generate-hashes --strip-extras --allow-unsafe \\
      --output-file="$tmpdir/requirements-py312.lock" requirements.txt
    # Ignore pip-compile's generated header because it embeds the differing output path.
    awk "found || /^[[:alnum:]][[:alnum:]_.-]*==/ {found=1; print}" \\
      requirements-py312.lock > "$tmpdir/current-lock.body"
    awk "found || /^[[:alnum:]][[:alnum:]_.-]*==/ {found=1; print}" \\
      "$tmpdir/requirements-py312.lock" > "$tmpdir/regenerated-lock.body"
    diff -u "$tmpdir/current-lock.body" "$tmpdir/regenerated-lock.body"
  '
else
  names+=("Python 3.12 dependency lock drift check")
  statuses+=("BLOCKED")
  details+=("pip-compile is not installed")
fi

if command -v pip-audit >/dev/null 2>&1; then
  run_check "Hash-locked dependency vulnerability audit" pip-audit --strict --progress-spinner off -r requirements-py312.lock
else
  names+=("Hash-locked dependency vulnerability audit")
  statuses+=("BLOCKED")
  details+=("pip-audit is not installed")
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
