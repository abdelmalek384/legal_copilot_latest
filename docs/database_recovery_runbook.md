# Separate-database backup and recovery runbook

**Status:** Operational procedure to rehearse before any production use. A successful backup command is not evidence that recovery has been accepted. Use the [recovery drill evidence record template](database_recovery_drill_record_template.md) to capture the bundle identity, verification, isolated restore, tenant checks, rollback rehearsal, measurements, and independent sign-off. Store detailed logs in the approved restricted evidence store; do not put keys, tokens, client names, or matter contents in the record.

## Scope and prerequisites

The approved runtime uses three storage locations:

- Control plane: global identities, firm memberships, platform roles, sessions, and the trusted firm catalog.
- Tenant root: one database file per firm.
- Shared legal corpus: centrally maintained legal-reference data.

The encrypted bundle must include all three components and every firm database cataloged by the control plane. A backup made while application writes continue is not an approved coordinated recovery point.

Before starting:

1. Confirm the operator is authorized to handle every included firm's data.
2. Confirm there is sufficient protected storage for the encrypted bundle and temporary staging files.
3. Confirm BACKUP_KEY is available from the approved secret store. Generate a key with python manage.py genkey only when creating a new key. Keep the key separate from the backup directory and database storage. Losing the key makes encrypted backups unrecoverable; do not paste it into tickets, logs, source control, or chat.
4. Confirm the retention window and destination capacity before using --keep; pruning old bundles is destructive to those backup files.

## Recover a failed firm-provisioning attempt

Provisioning failures are deliberately not auto-retried by request handlers. The runtime preserves a failed catalog state only when tenant schema initialization failed and the partial database was removed. Recovery is permitted only when the firm is disabled and its catalog entry is explicitly `failed`; active firms, intentionally disabled firms, missing catalog entries, and provisioned databases are not eligible for this retry command.

After reviewing the control-plane and catalog state on a trusted operator host, retry with an auditable reason and change references:

```bash
python manage.py retry-failed-provisioning \
  --firm-id 123 \
  --reason "Retry after reviewed transient schema initialization failure" \
  --operator-reference "incident-or-ticket-reference" \
  --change-reference "approved-change-reference" \
  --confirm-retry
```

The command creates a new uniquely named tenant database, reruns the firm-profile migrations and immutable firm binding checks, validates SQLite integrity/foreign keys, then activates the firm only after the catalog is provisioned and the recovery audit event commits. If schema initialization fails, the partial database is removed and the catalog remains `failed`, allowing a later reviewed retry. If provisioning succeeds but the final recovery audit/activation transaction fails, the firm remains disabled and the valid database is retained with catalog status `disabled` for maintenance; this is not retryable through this command and requires a separate reviewed repair. Missing catalog rows, stale filename mappings, memberships, and invitations are refused. Do not manually set lifecycle status values or reuse a database file from another firm.

## Reconcile interrupted, file-less firm provisioning

Use this only when the application or host stopped during provisioning and both the firm and its catalog row remain in `provisioning`. First stop **all** web workers, scheduled jobs, and background workers and confirm no provisioning process is active. This command never opens, adopts, deletes, or overwrites a tenant database. It refuses to proceed if any tenant database file or SQLite sidecar for the firm exists, if the filename is invalid, if any membership or invitation history exists, or if the firm/catalog states do not match exactly.

For the file-less case, record the incident and approved change, then run:

```bash
python manage.py reconcile-interrupted-provisioning \
  --firm-id 123 \
  --reason "Host restarted during tenant provisioning; no tenant file or sidecar exists" \
  --operator-reference "incident-or-ticket-reference" \
  --change-reference "approved-change-reference" \
  --confirm-workers-stopped \
  --confirm-reconcile
```

The command atomically changes the firm to `disabled`, changes the catalog to `failed` with no database filename, and appends an immutable audit event. It does not activate the firm. Once the failure is reviewed, the separate `retry-failed-provisioning` command can perform a fresh, audited attempt. If any database file or sidecar exists, stop and investigate integrity, firm binding, and catalog history manually; do not force the state or delete the file as part of reconciliation.

## Run the read-only tenant offboarding preflight

Before any tenant-level export, retention action, or deletion proposal, disable the firm through the lifecycle command and suspend/revoke its active memberships according to the approved offboarding plan. Then run the read-only preflight using the intended database/object-storage paths:

```bash
python tools/firm_offboarding_preflight.py --firm-id 123 --json
```

The command never deletes or modifies data. A clear report is not legal authorization to purge. Resolve every finding first, including active memberships, active/pending invitations, active legal holds, staged or quarantined originals, pending second-admin deletion approvals, in-flight purges, integrity/binding failures, and object-store reconciliation discrepancies. Active invitations are a blocker even when the firm is disabled. After confirming the firm and catalog are disabled, revoke pending/sent invitations atomically with per-invitation audit events:

```bash
python manage.py revoke-firm-invitations \\
  --firm-id 123 \\
  --reason "Revoke outstanding invitations before approved tenant offboarding" \\
  --operator-reference "incident-or-ticket-reference" \\
  --change-reference "approved-change-reference" \\
  --confirm-revoke
```

The command refuses active firms, requires explicit confirmation and operator/change references, and rolls back all status changes if any audit write fails. Do not delete invitation rows. Retain the report and policy/legal approval evidence in the restricted operations record.

## Recover staged original-file uploads before backup

A backup bundle must not be created while any tenant original-file metadata remains in the staged state. Resolve interrupted uploads first, while all application and background writers are stopped.

1. Keep all application, scheduler, and worker writes paused. Confirm the configured object backend and the intended staging bucket/root.
2. Run the recovery command in dry-run mode:

       python tools/recover_staged_original_files.py --json

   For the local development backend, ensure COPILOT_OBJECT_STORAGE_ROOT points to the private object directory. For S3, set COPILOT_OBJECT_STORAGE_BACKEND=s3 and the approved bucket, region, KMS key, and AWS credentials from the protected environment. The command never prints credentials.
3. Review every finding. recoverable_candidate means the staged bytes match the recorded SHA-256 and size; it is not permission to mutate. Any manual_review_required, missing bytes, digest mismatch, or concurrent-change finding is a NO-GO. Investigate it manually; do not delete the staged object or rewrite metadata to make the report clean.
4. Only after the operator confirms quiescence and approves the recovery change, run:

       python tools/recover_staged_original_files.py --apply --quiesced --json

   The command requires both flags together. It finalizes verified staged bytes and updates tenant metadata transactionally. If storage finalization fails, the metadata transaction rolls back and the staged bytes must remain available for another reviewed attempt.
5. Re-run the command without --apply. Require recovered_count to be zero, manual_review_required to be false, and no remaining recovery candidates. Then run the backend-appropriate read-only reconciliation:
   - Local staging: python tools/reconcile_original_file_storage.py --json
   - S3 staging: python tools/reconcile_s3_original_file_storage.py --json

   Require a clean report with zero findings before creating the coordinated backup bundle.
6. Record the dry-run report, apply report, post-recovery reconciliation report, operator, witness, and staging commit in the restricted evidence store. Redact object IDs if they are treated as sensitive by the deployment.

This recovery command is not a substitute for the backup/restore drill. Production local-filesystem recovery is disabled; use the configured S3 backend for a production deployment. Never use direct SQL updates or manual object copies to bypass the recovery checks.

## Create a coordinated encrypted bundle

1. Put the application into maintenance mode or stop all application/background workers that can write to any of the three database areas. Wait for active requests and jobs to finish. Keep writes paused for the full bundle snapshot window.
2. Set BACKUP_KEY in the operator's protected environment.
3. Run:

       python manage.py backup-tenancy /protected/backup-directory --quiesced --keep 14

4. Confirm the command reports the bundle path and completes successfully. Record the bundle filename, timestamp, operator, application revision, and result in the restricted operations log; never record the key.
5. Confirm the new bundle exists, has non-zero size, and is readable only by the intended backup operators. Preserve the prior known-good bundle until the new one has passed a restore rehearsal.
6. Resume writes only after the backup command has exited successfully or its failure has been investigated. A failed bundle must not be treated as a valid recovery point.

The --quiesced flag is an operator assertion, not an automated lock on all application writers. It does not stop the service for you.

## Verify an encrypted bundle before restore

1. Run verification on a trusted operator host with protected temporary storage and the correct `BACKUP_KEY` configured.
2. Execute:

       python manage.py verify-backup-tenancy /protected/backup-directory/backup-file.bundle.enc

3. Confirm the command reports `"verified": true` and the expected tenant database count. Keep the encrypted bundle and its key separate.
4. Verification temporarily materializes plaintext SQLite databases in a restricted temporary directory and removes them on exit. Deletion is **not guaranteed secure erasure**, especially on SSDs or copy-on-write filesystems. This command does not replace a witnessed restore into staging, startup, isolation checks, or rollback rehearsal.

## Store and retrieve the encrypted bundle in the separate S3 recovery archive

The recovery archive is not the original-object bucket. Configure the separate `COPILOT_S3_RECOVERY_BUCKET`, `COPILOT_S3_RECOVERY_REGION`, `COPILOT_S3_RECOVERY_KMS_KEY_ID`, and optional `COPILOT_S3_RECOVERY_ENDPOINT_URL` values. The AWS identity used for backup must have only the reviewed archive write permissions; restore operators need exact-version read permissions. The application runtime and original-object purge role must have no recovery-archive access. These IAM boundaries must be independently verified before production use.

After creating the local encrypted bundle and while preserving the approved operator evidence, upload it:

```bash
python manage.py archive-upload-tenancy /protected/backup-directory/backup-file.bundle.enc \
  > /protected/recovery-evidence/archive-locator.json
```

The command requires S3 bucket versioning to be `Enabled`, and an enabled customer-managed symmetric KMS key. It uploads the already-Fernet-encrypted bytes with S3 SSE-KMS. The JSON locator records the exact S3 `VersionId`, object key, SHA-256, byte size, and canonical archive KMS key ARN. Store this locator in the restricted recovery evidence store, separately from the archive object and BACKUP_KEY. Do not edit it, infer a version from the latest object, or treat a key without a VersionId as a recovery point. Keep the output file protected; it identifies a recovery object.

To retrieve a specific recovery point, provide the exact locator and a new local destination:

```bash
python manage.py archive-download-tenancy \
  /protected/recovery-evidence/archive-locator.json \
  --out /protected/restore-input/backup-file.bundle.enc
```

The command pins both S3 read operations to the locator's `VersionId`, checks the returned version, server-side encryption and KMS key identity, metadata, size, and independently computed SHA-256. It refuses to overwrite an existing file. Then run `verify-backup-tenancy` on the downloaded encrypted file and `restore-tenancy` to a new isolated directory. Download success alone is not bundle verification or a completed recovery drill. Multipart uploads are aborted on detected upload failure; investigate any ambiguous network failure and reconcile incomplete multipart uploads through the approved archive operations process.

## Restore into an isolated destination

**Never restore over the configured live database paths.** Restore creates a new destination directory and validates the encrypted bundle, manifest/checksums, database profiles, firm bindings, catalog consistency, and SQLite integrity before reporting success.

1. Keep the current application instance running against its existing paths, or stop it if the recovery exercise requires a full outage. Do not point it at the restore target yet.
2. Set the correct BACKUP_KEY in the protected operator environment.
3. Restore into a new, empty directory:

       python manage.py restore-tenancy /protected/backup-directory/backup-file.bundle.enc --target-root /protected/restore-rehearsal-unique

   Use the exact encrypted bundle filename emitted by the backup command. The target must be a new location; do not use the current control-plane path, corpus path, or tenant root.
4. Capture all restored paths (control plane, tenant root, legal corpus, and original-object directory) in the restricted recovery record. Configure a separate staging process to use those restored paths.
5. If the deployment uses the S3/KMS original-file backend, first run the local-object recovery smoke test above while the restored metadata still references its bundled local originals. Then, with the operator environment still pointing at the current live database paths for overlap protection, run both read-only S3/KMS preflights:

       python tools/validate_s3_original_file_storage.py --json
       python tools/validate_s3_recovery_archive.py --json

   The original-object bucket must be confirmed never-versioned; the separate recovery-archive bucket must have versioning `Enabled`, a different bucket name, and a different canonical customer-managed KMS key. Both commands always report `production_ready: false`; passing structural checks is not production approval. Bucket/IAM policies, backup/restore role separation, KMS grants, retention, legal holds, and live behavior still require independent review.
6. After the read-only preflight passes, run the live synthetic-object round trip against a dedicated, active, empty firm whose name begins `SYNTHETIC-ACCEPTANCE-`. Do not use a firm with client matters. With the operator environment configured for staging or production and the approved S3/KMS values, run:

       python tools/verify_s3_original_file_roundtrip.py --firm-id 123 --confirm-synthetic-firm --json

   The command verifies the firm is a dedicated empty acceptance tenant, then stages synthetic bytes, checks staged integrity/KMS identity, finalizes and verifies the destination, reads the bytes back, and deletes the active probe keys. Its JSON report includes `storage_config_sha256`, a SHA-256 fingerprint of both non-secret S3 targets (original-object and recovery-archive buckets, regions, KMS identifiers, and endpoints). Preserve that fingerprint with the evidence and confirm it matches the target fingerprint recorded in the operational acceptance manifest; evidence from a different target is not reusable. The report never includes secret credentials and never sets production approval to true. Require every configuration and round-trip check to pass and `cleanup_pending: false`. If cleanup is pending, stop and reconcile the reported opaque object ID before retrying. Deletion from the never-versioned original-object bucket does not erase copies held in encrypted recovery archives; retention and legal-hold policy governs archive expiry.
7. Run the restored-original importer in dry-run mode against the isolated restore root:

       python tools/import_restored_originals_to_s3.py --restore-root /protected/restore-rehearsal-unique

   Set `COPILOT_OBJECT_STORAGE_BACKEND=s3`, `COPILOT_S3_BUCKET`, `COPILOT_S3_REGION`, and `COPILOT_S3_KMS_KEY_ID` from the approved secret/configuration source. Review the report for every object and confirm zero integrity or conflict errors. Only under a separately approved change, rerun with `--apply`; the command must continue to use the current live database paths for overlap protection and will mutate only the isolated restore directory and configured S3 bucket.
8. After import, point the operator environment's three database paths at the restored staging control-plane, tenant root, and legal-corpus paths, then run the read-only S3 reconciliation against those restored databases:

       python tools/reconcile_s3_original_file_storage.py --json

   Require `clean: true` and zero findings before starting the restored staging application. Restore/import/reconciliation commands do not themselves authorize cutover.
9. Before considering a cutover, run deployment preflight in strict mode against the staging configuration:

       python tools/deployment_preflight.py --strict

   The environment must contain all three separate database paths, must not contain the legacy shared COPILOT_DB path, and must point to the restored staging locations.
10. Start only a staging instance. Verify that migration startup succeeds, the catalog resolves each expected firm, active memberships still work, disabled/revoked memberships remain denied, and a synthetic case created in one firm cannot be read from another.
11. Verify corpus lookup and FTS behavior against known test records. Check that a firm's case/document/chunk sentinels are present only in that firm's database and absent from other firm databases.
12. Record the tested bundle, application revision, restore duration, checks performed, discrepancies, and pass/fail result. Delete or quarantine the rehearsal copy according to the approved retention policy after the exercise.

## Automated isolated restore smoke test

Before scheduling the witnessed staging exercise, run the automated restore smoke test against a known encrypted bundle from a protected maintenance host. It restores into a private temporary directory, validates SQLite/profile/catalog bindings, reconciles restored original-file metadata against the restored local object store, checks runtime routing for each active firm, and verifies that identities without active membership are denied. It reports only bounded findings and removes its temporary directory when it exits; cleanup is not guaranteed secure erasure.

Set the key through the protected environment, never as a command-line argument:

    COPILOT_BACKUP_FERNET_KEY="$BACKUP_KEY" python tools/run_database_recovery_drill.py --bundle /protected/backup-directory/backup-file.bundle.enc --temp-parent /protected/recovery-temp --json

The temporary parent must already exist, must not be a symlink, and must be protected for plaintext database staging. Do not run this command inside the production application process. A nonzero exit, any reported finding, or missing output is a **NO-GO** for the next stage. A passing smoke test is useful automated evidence only: it does not prove reverse-proxy behavior, real application startup, HTTP cross-firm denial, live rollback, key recovery, retention controls, or reviewer sign-off. Continue with the full witnessed staging drill below.

## Deletion-recovery exercise and production S3 limitation

Perform deletion-recovery rehearsal only in an isolated staging environment with a dedicated synthetic firm and synthetic matter/original file. Never use a client matter or a production firm for this exercise.

1. Create a known-good encrypted bundle while the synthetic original is finalized and its tenant metadata is ready. Record the original object's SHA-256 and byte size in the restricted evidence record.
2. Exercise the supported deletion request and distinct second-admin approval workflow in staging. Record the request ID, requester, approver, and reasons. Confirm an active legal hold blocks the request/purge path.
3. The S3-aware offboarding preflight and physical-purge implementation are now present on `main` in `tools/firm_offboarding_s3_preflight.py`, `tools/purge_approved_s3_original_files.py`, and `s3_original_file_storage.py`. The S3 purge path is guarded by the acceptance manifest, exact storage-target fingerprint, disabled-firm/catalog checks, distinct requester/approver/operator roles, legal-hold checks, byte-integrity/KMS verification, ETag-conditional deletion, and post-delete verification. **Implementation is not live-provider acceptance or authorization to delete.** Do not manually delete S3 objects or mark the production deletion-recovery scenario passed based on fake-S3 tests.
4. For a local staging rehearsal, use the approved two-admin workflow and local purge CLI with all preflight requirements met, then verify the tombstone and immutable deletion/hold history. Restore the known-good bundle into a separate new destination and verify the pre-deletion synthetic case, original metadata, and original bytes against the recorded SHA-256/size. Never restore over active staging paths.
5. For S3 staging, the deletion-recovery scenario remains BLOCKED pending live bucket/KMS/IAM validation, independent review of conditional deletion and the IAM-enforced no-writer window, approved retention/lifecycle controls, and a witnessed synthetic-firm rehearsal. There is also an unresolved architecture conflict: the storage validator requires bucket versioning `Enabled` for recovery, while physical purge requires a confirmed never-versioned bucket. One bucket cannot meet both. Resolve this through separately accepted recovery/purge buckets or a reviewed version-aware purge implementation before attempting the S3 deletion drill.
6. Preserve before/after reports, bundle identity, synthetic object digest/size, request/approval evidence, tombstone/history checks, restore result, and witness sign-off in the restricted evidence store.

A local staging rehearsal does not satisfy production S3 deletion acceptance. The retention_export_deletion_policy and backup_restore_rollback gates remain blocked until the approved production deletion workflow and the witnessed recovery scenarios are actually accepted.

## Cutover and rollback gates

Do not change live environment paths merely because the restore command succeeded. Require all of the following:

- A named operator and reviewer approve the recovery point and intended cutover.
- Strict deployment preflight passes on the proposed paths.
- Startup and tenant-isolation acceptance checks pass on the restored copy.
- Data owners accept any known recovery-point loss and the incident owner records the decision.
- The original database files and previous known-good encrypted bundle remain preserved until the new instance passes its agreed smoke-test window.

For rollback, stop writes to the candidate instance first. Restore the prior approved configuration paths; do not copy individual SQLite files into a live set and do not mix control-plane, tenant, and corpus files from different backup generations. Preserve the failed candidate for investigation under the retention policy.

## Scheduled recovery acceptance checklist

- [ ] Confirm backup completed while all writers were quiesced.
- [ ] Confirm encrypted bundle is stored separately from BACKUP_KEY.
- [ ] Run `python manage.py verify-backup-tenancy` and confirm the bundle validates without persistent restore artifacts.
- [ ] Restore a representative bundle into a new isolated destination.
- [ ] Confirm all profile, firm-binding, manifest, and SQLite integrity validations pass.
- [ ] Run strict deployment preflight and staging startup.
- [ ] Test cross-firm denial and active/revoked membership behavior.
- [ ] Test representative firm search and shared corpus lookup.
- [ ] Record restore duration, recovery point, results, and reviewer sign-off.
- [ ] Verify backup retention and key-access controls.

Until this drill is completed and approved for the target deployment, backup/restore implementation must not be described as proven operational recovery.
