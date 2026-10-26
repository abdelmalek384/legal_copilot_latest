# Separate-database backup and recovery runbook

**Status:** Operational procedure to rehearse before any production use. A successful backup command is not evidence that recovery has been accepted.

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
4. Capture the three paths printed by the restore command in the restricted recovery record. Configure a separate staging process to use those restored paths.
5. Before considering a cutover, run deployment preflight in strict mode against the staging configuration:

       python tools/deployment_preflight.py --strict

   The environment must contain all three separate database paths, must not contain the legacy shared COPILOT_DB path, and must point to the restored staging locations.
6. Start only a staging instance. Verify that migration startup succeeds, the catalog resolves each expected firm, active memberships still work, disabled/revoked memberships remain denied, and a synthetic case created in one firm cannot be read from another.
7. Verify corpus lookup and FTS behavior against known test records. Check that a firm's case/document/chunk sentinels are present only in that firm's database and absent from other firm databases.
8. Record the tested bundle, application revision, restore duration, checks performed, discrepancies, and pass/fail result. Delete or quarantine the rehearsal copy according to the approved retention policy after the exercise.

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
