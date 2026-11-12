#!/usr/bin/env bash
# Focused security regression matrix. Run from the repository root.
# This executes existing test modules; it does not replace independent review.
set -uo pipefail

if [[ ! -d tests || ! -f app.py ]]; then
  echo "Run this script from the repository root." >&2
  exit 2
fi

tests=(
  test_app_separate_database_runtime.py
  test_auth_rate_limits_separate_runtime.py
  test_mfa_account_security.py
  test_security_transport_config.py
  test_trusted_proxy_client_ip.py
  test_trusted_host_middleware.py
  test_original_file_storage.py
  test_document_extraction_budget.py
  test_pdf_ocr_fallback.py
  test_research_prompt_injection_boundary.py
  test_case_csv_import.py
  test_client_csv_import.py
  test_invoice_payment_routes.py
  test_subscription_billing_routes.py
  test_firm_data_export.py
  test_first_run_wizard_api.py
  test_demo_firm_cli.py
  test_platform_access.py
  test_deployment_preflight.py
  test_tenant_route_inventory_coverage.py
)

labels=()
results=()
details=()
failed=0

for test_file in "${tests[@]}"; do
  labels+=("$test_file")
  if [[ ! -f "tests/$test_file" ]]; then
    results+=("BLOCKED")
    details+=("test module is absent from this checkout")
    failed=1
    continue
  fi

  echo
  echo "==> $test_file"
  if [[ "$test_file" == "test_trusted_proxy_client_ip.py" ]]; then
    if COPILOT_ENV=development PYTHONPATH=. python "tests/$test_file"; then
      results+=("PASS")
      details+=("completed")
    else
      rc=$?
      results+=("FAIL")
      details+=("exit $rc")
      failed=1
    fi
  elif PYTHONPATH=. python "tests/$test_file"; then
    results+=("PASS")
    details+=("completed")
  else
    rc=$?
    results+=("FAIL")
    details+=("exit $rc")
    failed=1
  fi
done

echo
echo "================ SECURITY REGRESSION MATRIX ================"
printf '%-47s %-10s %s\n' "TEST MODULE" "RESULT" "DETAIL"
printf '%-47s %-10s %s\n' "-----------------------------------------------" "----------" "------------------------------"
for i in "${!labels[@]}"; do
  printf '%-47s %-10s %s\n' "${labels[$i]}" "${results[$i]}" "${details[$i]}"
done
echo "============================================================"
if [[ $failed -eq 0 ]]; then
  echo "All focused security regression modules passed."
else
  echo "Security regression gate is NOT PASS. Resolve failures and missing modules."
fi
exit "$failed"
