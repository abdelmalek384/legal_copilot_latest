#!/usr/bin/env bash
# Focused security regression matrix. Run from the repository root.
# This executes existing test modules; it does not replace independent review.
set -uo pipefail

if [[ ! -d tests || ! -f app.py ]]; then
  echo "Run this script from the repository root." >&2
  exit 2
fi

if ! python - <<'PY'
import sys
if sys.version_info[:2] != (3, 12):
    print(
        f"BLOCKED: security regression validation requires Python 3.12; "
        f"current interpreter is {sys.version_info.major}.{sys.version_info.minor}.",
        file=sys.stderr,
    )
    raise SystemExit(2)
PY
then
  exit 2
fi

tests=(
  test_backup_restore_drill_paths.py
  test_backup_restore_safety.py
  test_app_separate_database_runtime.py
  test_database_runtime.py
  test_dependency_lock_workflow_contract.py
  test_tenant_catalog.py
  test_trusted_proxy_client_ip.py
  test_tenant_storage.py
  test_auth_rate_limits_separate_runtime.py
  test_identity_lifecycle.py
  test_platform_security_audit_migrations.py
  test_mfa_account_security.py
  test_mfa_primitives.py
  test_mfa_break_glass_cli.py
  test_platform_admin_bootstrap_cli.py
  test_tenant_context.py
  test_tenant_context_transaction_boundary.py
  test_tenant_database_preflight.py
  test_tenant_fleet_migration.py
  test_tenant_ownership_preflight.py
  test_tenant_write_failure_diagnostics.py
  test_s3_storage_preflight.py
  test_s3_recovery_archive_preflight.py
  test_document_classifications.py
  test_document_intelligence.py
  test_document_review_workflow.py
  test_invoice_schema_migration.py
  test_security_audit_export.py
  test_reminder_email.py
  test_reminder_outbox.py
  test_reminder_service.py
  test_security_transport_config.py
  test_trusted_host_middleware.py
  test_uploaded_filename_sanitization.py

  test_database_migration_rehearsal.py

  test_recover_staged_original_files.py

  test_bounded_original_file_audit_history.py

  test_security_audit_read_separate_runtime.py

  test_firm_security_policy.py

  test_auth_cookie_expiry_middleware.py
  test_original_file_storage.py
  test_original_file_reconciliation.py
  test_import_restored_originals_to_s3.py
  test_s3_original_file_storage.py
  test_firm_offboarding_preflight.py
  test_database_backup_bundle.py
  test_manage_recovery_locator.py
  test_database_backup_archive.py
  test_database_release_acceptance.py
  test_device_browser_acceptance.py
  test_device_acceptance_release_integration.py
  test_production_release_gate.py
  test_database_recovery_drill.py
  test_purge_approved_original_files.py
  test_document_extraction_budget.py
  test_pdf_ocr_fallback.py
  test_import_laws_bundle.py
  test_research_prompt_injection_boundary.py
  test_score_arabic_retrieval.py
  test_import_gazette_text.py
  test_legal_source_review_queue.py
  test_legal_eval_runner.py
  test_legal_answer_review_evaluation.py
  test_review_evidence_url_validation.py
  test_labour_law_provisional_review_questions.py
  test_legal_data_foundation_validator.py
  test_legal_release_readiness.py
  test_legal_candidate_catalog.py
  test_legal_corpus_audit.py
  test_source_permission_register.py
  test_legal_versioned_registry.py
  test_amendment_relationship_validator.py
  test_first_official_batch_manifest.py
  test_decision250_candidate_quarantine.py
  test_answer_citation_coverage.py
  test_citation_quantity_binding.py
  test_answer_source_polarity.py
  test_answer_actor_role_binding.py
  test_answer_conditional_scope_binding.py
  test_synthetic_retrieval.py
  test_retrieval_evaluation.py
  test_multi_area_eval_draft.py
  test_output_path_safety.py
  test_case_csv_import.py
  test_client_csv_import.py
  test_invoice_csv_export.py
  test_answer_rating_routes.py
  test_frontend_ux_contract.py
  test_research_copy_initialization.py
  test_security_matrix_registration.py
  test_invoice_payment_routes.py
  test_subscription_billing_routes.py
  test_firm_data_export.py
  test_first_run_wizard_api.py
  test_demo_firm_cli.py
  test_platform_access.py
  test_deployment_preflight.py
  test_tenant_route_inventory_coverage.py
  test_route_auth_audit.py
  test_route_sql_access_audit.py
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

for audit in "tools/audit_route_sql_access.py" "tools/audit_route_auth.py"; do
  labels+=("$audit --strict")
  if [[ ! -f "$audit" ]]; then
    results+=("BLOCKED")
    details+=("static audit tool is absent from this checkout")
    failed=1
  else
    echo
    echo "==> $audit --strict"
    if PYTHONPATH=. python "$audit" --strict; then
      results+=("PASS")
      details+=("completed")
    else
      rc=$?
      results+=("FAIL")
      details+=("exit $rc")
      failed=1
    fi
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
