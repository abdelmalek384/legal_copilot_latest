# Database operational release acceptance

The database implementation is still under development. A passing unit/integration suite and a successful static SQL audit are necessary, but they do not prove that production object storage, key management, backup recovery, retention policy, identity email, privileged recovery, or operational security review have been accepted.

`tools/database_release_acceptance.py` validates the required operational evidence. `tools/production_release_gate.py` consumes this decision as a mandatory release gate. If the evidence file is missing, malformed, incomplete, pending, or has invalid timestamps, the production release remains blocked.

## Required evidence

| Gate | Required acceptance evidence | Maximum evidence age |
|---|---|---:|
| `original_file_storage` | Live object-storage and KMS/key policy validation, firm-scoped authorization, integrity/reconciliation behavior, and a SHA-256 fingerprint of the exact S3/KMS target configuration | 90 days |
| `purge_writer_quiescence` | Independently witnessed, target-bound evidence that upload/finalize workers were drained, all non-purge principals were denied writes, the purge role was denied writes, bucket/IAM policy changes were frozen, and negative tests/CloudTrail evidence were retained | 90 days |
| `backup_restore_rollback` | Witnessed staging restore, rollback, staged-upload recovery, and deletion-recovery drill; the manifest must list all four in `verified_scenarios` | 90 days |
| `retention_export_deletion_policy` | Approved retention schedule and tenant export/deletion policy; do not substitute an unapproved default | 365 days |
| `production_identity_email` | Production email delivery and recovery-message validation, plus multi-host rate-limit behavior | 90 days |
| `privileged_recovery_bootstrap` | Rehearsed privileged-account recovery and first-platform-admin bootstrap, with a distinct witness | 180 days |
| `independent_security_review` | Independent review evidence and zero unresolved critical/high findings | 90 days |

Each accepted item must have `status: "passed"`, an evidence reference, a timezone-aware ISO-8601 timestamp, and the named approver/verifier. Both `original_file_storage` and `purge_writer_quiescence` items must include the same current `storage_config_sha256`, computed from the active original-object settings (`COPILOT_OBJECT_STORAGE_BACKEND`, `COPILOT_S3_BUCKET`, `COPILOT_S3_REGION`, `COPILOT_S3_KMS_KEY_ID`, `COPILOT_S3_ENDPOINT_URL`) and the separate recovery-archive settings (`COPILOT_S3_RECOVERY_BUCKET`, `COPILOT_S3_RECOVERY_REGION`, `COPILOT_S3_RECOVERY_KMS_KEY_ID`, `COPILOT_S3_RECOVERY_ENDPOINT_URL`). Both buckets and both KMS keys must be distinct; evidence is invalidated if either target changes. The `evidence_ref` for `original_file_storage` must identify both read-only preflight reports and the synthetic original-object round-trip evidence; a configured recovery bucket without successful archive preflight is not accepted. Production startup and every original-file storage access compare this fingerprint to the current configuration; changing the bucket, region, endpoint, backend, or key invalidates the prior storage acceptance until the new target is reviewed and re-accepted. Compute the non-secret fingerprint with `python tools/database_release_acceptance_cli.py --print-storage-config-fingerprint` after loading the approved target configuration. Evidence older than the gate-specific maximum age above is rejected at startup and by the release gate, even if its status remains `passed`; re-run and re-approve the underlying check before refreshing its timestamp. The purge-writer-quiescence, restore drill, and privileged recovery/bootstrap gates additionally require a witness distinct from the verifier. For `purge_writer_quiescence`, `verified_scenarios` must include `upload_finalize_workers_drained`, `non_purge_principals_denied_put_object`, `purge_role_denied_put_object`, `bucket_policy_and_iam_changes_frozen`, and `cloudtrail_negative_tests_retained`; a `--quiesced` CLI assertion is not evidence of these controls. For `backup_restore_rollback`, `verified_scenarios` must include `staging_restore`, `rollback`, `staged_upload_recovery`, and `deletion_recovery`; a generic passed status cannot stand in for one of these required exercises. The independent review must report `unresolved_critical_high: 0`.

## Fresh-install database bootstrap

The first production app process must not create missing database files implicitly. Provision the profile schemas and first firm owner in a restricted maintenance shell before production startup. Use the three separate paths and keep `COPILOT_DB` unset:

```bash
export COPILOT_ENV=development
unset COPILOT_DB
export COPILOT_CONTROL_DB=/secure/persistent/control-plane.sqlite3
export COPILOT_TENANT_DB_ROOT=/secure/persistent/tenants
export COPILOT_CORPUS_DB=/secure/persistent/legal-corpus.sqlite3
python manage.py init-tenancy --firm-name "Firm name" --owner-name "Initial owner" --owner-email "owner@example.invalid"
```

This is a one-time bootstrap command, not permission to run the web application in development mode on production data. Protect the maintenance environment, credentials, and volumes; then run the strict deployment preflight and operational acceptance process. Set `COPILOT_ENV=production` for the actual web service. Production startup requires existing, pre-provisioned control/corpus databases with exact current migration ledgers, an existing non-symlink tenant root, a current tenant-fleet migration state, and a complete fresh acceptance manifest. On POSIX, the tenant root must be private (`0700`) and profile database/sidecar files must be private (`0600`). Missing or empty profile files, pending/drifted migrations, unresolved tenant lifecycle states, or overly broad permissions block startup; do not let startup recreate an empty database in place of missing data.

## Procedure

1. Copy `docs/database_release_acceptance.template.json` into a controlled, access-restricted location outside the repository. The manifest must be a regular file, not a symlink, at most 1 MB, and not writable by group/other users (on POSIX).
2. Complete only after the corresponding real operational check has passed. Do not mark a gate passed based on a planned drill, a mocked test, or a code review.
3. Keep evidence references non-secret. Never put passwords, access tokens, private keys, recovery codes, or cloud credentials in the manifest.
4. Run the read-only validator:

   ```bash
   python tools/database_release_acceptance_cli.py --manifest /secure/path/database-release-acceptance.json
   ```

5. Set `COPILOT_DATABASE_ACCEPTANCE_FILE=/secure/path/database-release-acceptance.json` in the production service environment. The application startup guard validates the manifest and refuses to start when the path is missing or the evidence is incomplete.
6. Supply the same controlled manifest to the overall release gate:

   ```bash
   python tools/production_release_gate.py --database-acceptance /secure/path/database-release-acceptance.json --reviewer-registry /secure/path/reviewer-registry.json
   ```

7. Keep production original-file uploads fail-closed until the live storage and recovery gates are accepted. A successful manifest validates recorded evidence fields; it does not independently witness or authenticate the underlying operational work.

The manifest is deployment evidence, not a migration, and it must not be filled with invented or placeholder approvals. No legacy-data import/reconciliation is required for this fresh-install project.
