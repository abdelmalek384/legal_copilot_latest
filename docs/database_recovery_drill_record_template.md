# Database recovery drill evidence record

**Purpose:** capture reviewer-verifiable evidence from a witnessed staging restore/rollback drill. Completing this template does not itself prove recovery; record only what was actually run and observed.

> **Do not record secrets or client content here.** Never include `BACKUP_KEY`, passwords, session cookies, tokens, full database paths containing sensitive identifiers, client names, case names, or document text. Store detailed logs in the approved restricted evidence store and reference them by identifier.

## 1. Drill identity

- Drill record ID:
- Date/time started (UTC):
- Date/time completed (UTC):
- Application commit SHA:
- Environment / staging identifier:
- Operator:
- Independent reviewer / witness:
- Change or incident ticket:
- Outcome: `NOT RUN` / `PASS` / `FAIL` / `BLOCKED`

## 2. Recovery point

- Encrypted bundle filename:
- Bundle SHA-256:
- Bundle creation timestamp (UTC):
- Source application revision:
- Number of cataloged firm databases:
- Backup operator / restricted evidence reference:
- Was the application and all database writers quiesced for the complete snapshot window? `YES` / `NO`
- Evidence that quiescence was verified:
- Was the bundle retained separately from the backup key? `YES` / `NO`
- Key identifier/version only (never the key value):

## 3. Verification and restore

Record each result as `PASS`, `FAIL`, or `N/A`. Attach evidence references; redact secrets from command output.

| Check | Result | Evidence reference / notes |
|---|---|---|
| `python manage.py verify-backup-tenancy` reports verified | | |
| Expected firm-database count matches manifest/catalog | | |
| Restore targets were new, isolated paths and did not overlap live paths | | |
| `python manage.py restore-tenancy` completes successfully | | |
| Manifest checksums, database profiles, firm bindings, catalog consistency, and SQLite integrity pass | | |
| Restricted temporary plaintext is cleaned up after verification | | |
| `python tools/deployment_preflight.py --strict` passes against restored staging paths | | |
| Staging application starts and completes migration checks without fallback to `COPILOT_DB` | | |
| Each expected firm resolves to its catalog-bound database | | |
| A synthetic case in Firm A is not readable from Firm B | | |
| Active membership works; suspended/revoked membership remains denied | | |
| Disabled firm remains denied without deleting its database | | |
| Shared legal corpus lookup and FTS integrity checks pass | | |
| Firm-private document sentinels do not appear in another firm's database or results | | |

## 4. Recovery measurements

- Total restore duration:
- Time until staging startup completed:
- Number of firm databases restored:
- Known recovery point / maximum observed data loss:
- Any missing rows, schema differences, or consistency warnings:
- Any manual intervention required:
- Evidence references for integrity checks:
- Temporary restore copies deleted or quarantined under approved retention policy?:
- Cleanup evidence reference:

## 5. Rollback rehearsal

| Check | Result | Evidence reference / notes |
|---|---|---|
| Candidate staging instance stopped before rollback | | |
| Previous approved configuration and known-good bundle preserved | | |
| No SQLite files from different backup generations were mixed | | |
| Rollback target/configuration restored and smoke-tested | | |
| Failed candidate retained or disposed of according to policy | | |

## 6. Staged-upload recovery

| Check | Result | Evidence reference / notes |
|---|---|---|
| All application, scheduler, and worker writes stopped before recovery | | |
| Dry-run of tools/recover_staged_original_files.py reviewed | | |
| Every recoverable candidate matched recorded SHA-256 and byte size | | |
| No manual-review, missing-object, integrity-mismatch, or concurrent-change findings remain | | |
| Apply mode used only with explicit --apply and --quiesced after approval | | |
| Recovery output reports zero unresolved findings | | |
| Follow-up dry-run reports no remaining recovery candidates | | |
| Backend-specific local/S3 reconciliation reports clean with zero findings | | |

## 7. Deletion-recovery scenario

| Check | Result | Evidence reference / notes |
|---|---|---|
| Dedicated synthetic firm/matter/object used; no client data involved | | |
| Known-good encrypted bundle created before the synthetic deletion | | |
| Distinct firm-admin request and second-admin approval recorded | | |
| Legal-hold behavior checked; held object cannot be purged | | |
| Purge operator is a distinct active platform administrator | | |
| Deletion/tombstone and immutable event history verified | | |
| Known-good bundle restored to a new isolated destination | | |
| Pre-deletion synthetic matter, metadata, and original bytes recovered with matching SHA-256/size | | |
| S3 versioning, delete-marker, KMS, and lifecycle behavior reviewed | | |

**Production S3 limitation:** an S3-aware purge CLI and offboarding preflight now exist on `main`, with fake-S3 state-machine coverage and fail-closed checks for bucket versioning, staged objects, byte integrity, KMS identity, and post-delete absence. This does not prove live AWS behavior. Mark the deletion-recovery scenario BLOCKED until live bucket/KMS/IAM verification, independent review of the IAM-enforced no-writer control during the integrity-check/delete interval, approved retention/export/deletion policy, and a witnessed synthetic-staging deletion-recovery rehearsal are complete. The CLI `--quiesced` flag is an operator assertion, not a distributed lock. Do not manually delete S3 objects or mark this scenario passed based on local-only or fake-S3 tests.

## 8. Findings and approval

- Findings / deviations:
- Severity and owner for each finding:
- Remediation ticket(s):
- Does the drill meet the agreed recovery-time objective? `YES` / `NO` / `NOT DEFINED`
- Does the drill meet the agreed recovery-point objective? `YES` / `NO` / `NOT DEFINED`
- Data owner accepts the recovery point / known loss?:
- Operator decision: `GO` / `NO-GO`
- Operator sign-off and timestamp (UTC):
- Reviewer sign-off and timestamp (UTC):
- Follow-up drill date, if required:

**Acceptance rule:** any failed isolation, integrity, authorization, startup, or rollback check is a `NO-GO`. Missing reviewer sign-off means the drill is not accepted. A successful `verify-backup-tenancy` run alone is not an operational recovery pass.
