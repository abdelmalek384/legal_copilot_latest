# Database operational release acceptance

The database implementation is still under development. A passing unit/integration suite and a successful static SQL audit are necessary, but they do not prove that production object storage, key management, backup recovery, retention policy, identity email, privileged recovery, or operational security review have been accepted.

`tools/database_release_acceptance.py` validates the required operational evidence. `tools/production_release_gate.py` consumes this decision as a mandatory release gate. If the evidence file is missing, malformed, incomplete, pending, or has invalid timestamps, the production release remains blocked.

## Required evidence

| Gate | Required acceptance evidence |
|---|---|
| `original_file_storage` | Live object-storage and KMS/key policy validation, firm-scoped authorization, integrity/reconciliation behavior, and provider configuration |
| `backup_restore_rollback` | Witnessed staging restore, rollback, staged-upload recovery, and deletion-recovery drill |
| `retention_export_deletion_policy` | Approved retention schedule and tenant export/deletion policy; do not substitute an unapproved default |
| `production_identity_email` | Production email delivery and recovery-message validation, plus multi-host rate-limit behavior |
| `privileged_recovery_bootstrap` | Rehearsed privileged-account recovery and first-platform-admin bootstrap, with a distinct witness |
| `independent_security_review` | Independent review evidence and zero unresolved critical/high findings |

Each accepted item must have `status: "passed"`, an evidence reference, a timezone-aware ISO-8601 timestamp, and the named approver/verifier. The restore drill and privileged recovery/bootstrap additionally require a witness distinct from the verifier. The independent review must report `unresolved_critical_high: 0`.

## Procedure

1. Copy `docs/database_release_acceptance.template.json` into a controlled, access-restricted location outside the repository.
2. Complete only after the corresponding real operational check has passed. Do not mark a gate passed based on a planned drill, a mocked test, or a code review.
3. Keep evidence references non-secret. Never put passwords, access tokens, private keys, recovery codes, or cloud credentials in the manifest.
4. Run the read-only validator:

   ```bash
   python tools/database_release_acceptance_cli.py --manifest /secure/path/database-release-acceptance.json
   ```

5. Supply the same controlled manifest to the overall release gate:

   ```bash
   python tools/production_release_gate.py --database-acceptance /secure/path/database-release-acceptance.json --reviewer-registry /secure/path/reviewer-registry.json
   ```

6. Keep production original-file uploads fail-closed until the live storage and recovery gates are accepted. A successful manifest validates recorded evidence fields; it does not independently witness or authenticate the underlying operational work.

The manifest is deployment evidence, not a migration, and it must not be filled with invented or placeholder approvals. No legacy-data import/reconciliation is required for this fresh-install project.
