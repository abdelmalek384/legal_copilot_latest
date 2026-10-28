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

Use this only when the application or host stopped during provisioning and both the firm and its catalog row remain in `provisioning`. First stop **all** web workers, scheduled jobs, and background workers and confirm no provisioning process is active. This command never opens, adopts, deletes, or overwrites a tenant database. It refuses to proceed if any tenant database file or SQLite sidecar for the firm exists, if the filename is invalid, or if the firm/catalog states do not match exactly.

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

## Restore into an isolated destination

**Never restore over the configured live database paths.** Restore creates a new destination directory and validates the encrypted bundle, manifest/checksums, database profiles, firm bindings, catalog consistency, and SQLite integrity before reporting success.

1. Keep the current application instance running against its existing paths, or stop it if the recovery exercise requires a full outage. Do not point it at the restore target yet.
2. Set the correct BACKUP_KEY in the protected operator environment.
3. Restore into a new, empty directory:

       python manage.py restore-tenancy /protected/backup-directory/backup-file.bundle.enc --target-root /protected/restore-rehearsal-unique

   Use the exact encrypted bundle filename emitted by the backup command. The target must be a new location; do not use the current control-plane path, corpus path, or tenant root.
4. Capture all restored paths (control plane, tenant root, legal corpus, and original-object directory) in the restricted recovery record. Configure a separate staging process to use those restored paths.
5. If the deployment uses the S3/KMS original-file backend, first run the local-object recovery smoke test above while the restored metadata still references its bundled local originals. Then, with the operator environment still pointing at the current live database paths for overlap protection, run the read-only S3/KMS preflight:

       python tools/validate_s3_original_file_storage.py --json

   This command always reports `production_ready: false`; passing its structural checks is not production approval. Confirm the dedicated bucket, customer-managed key, public-access-block settings, ownership controls, versioning, and default SSE-KMS encryption. Bucket/IAM policy, KMS grants, and live behavior still require independent review.
6. Run the restored-original importer in dry-run mode against the isolated restore root:

       python tools/import_restored_originals_to_s3.py --restore-root /protected/restore-rehearsal-unique

   Set `COPILOT_OBJECT_STORAGE_BACKEND=s3`, `COPILOT_S3_BUCKET`, `COPILOT_S3_REGION`, and `COPILOT_S3_KMS_KEY_ID` from the approved secret/configuration source. Review the report for every object and confirm zero integrity or conflict errors. Only under a separately approved change, rerun with `--apply`; the command must continue to use the current live database paths for overlap protection and will mutate only the isolated restore directory and configured S3 bucket.
7. After import, point the operator environment's three database paths at the restored staging control-plane, tenant root, and legal-corpus paths, then run the read-only S3 reconciliation against those restored databases:

       python tools/reconcile_s3_original_file_storage.py --json

   Require `clean: true` and zero findings before starting the restored staging application. Restore/import/reconciliation commands do not themselves authorize cutover.
8. Before considering a cutover, run deployment preflight in strict mode against the staging configuration:

       python tools/deployment_preflight.py --strict

   The environment must contain all three separate database paths, must not contain the legacy shared COPILOT_DB path, and must point to the restored staging locations.
9. Start only a staging instance. Verify that migration startup succeeds, the catalog resolves each expected firm, active memberships still work, disabled/revoked memberships remain denied, and a synthetic case created in one firm cannot be read from another.
10. Verify corpus lookup and FTS behavior against known test records. Check that a firm's case/document/chunk sentinels are present only in that firm's database and absent from other firm databases.
11. Record the tested bundle, application revision, restore duration, checks performed, discrepancies, and pass/fail result. Delete or quarantine the rehearsal copy according to the approved retention policy after the exercise.

## Automated isolated restore smoke test

Before scheduling the witnessed staging exercise, run the automated restore smoke test against a known encrypted bundle from a protected maintenance host. It restores into a private temporary directory, validates SQLite/profile/catalog bindings, reconciles restored original-file metadata against the restored local object store, checks runtime routing for each active firm, and verifies that identities without active membership are denied. It reports only bounded findings and removes its temporary directory when it exits; cleanup is not guaranteed secure erasure.

Set the key through the protected environment, never as a command-line argument:

    COPILOT_BACKUP_FERNET_KEY="$BACKUP_KEY" python tools/run_database_recovery_drill.py --bundle /protected/backup-directory/backup-file.bundle.enc --temp-parent /protected/recovery-temp --json

The temporary parent must already exist, must not be a symlink, and must be protected for plaintext database staging. Do not run this command inside the production application process. A nonzero exit, any reported finding, or missing output is a **NO-GO** for the next stage. A passing smoke test is useful automated evidence only: it does not prove reverse-proxy behavior, real application startup, HTTP cross-firm denial, live rollback, key recovery, retention controls, or reviewer sign-off. Continue with the full witnessed staging drill below.

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
