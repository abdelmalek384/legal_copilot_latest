# Storage architecture decision — separate original objects from recovery archives

**Status:** Proposed engineering decision; not approved for deployment.  
**Scope:** Greenfield first deployment. No legacy database or legacy-object migration is assumed.  
**Decision owner:** Deployment/storage owner, with security review and qualified counsel approval for retention semantics.

## Decision required

The current design has an impossible single-bucket requirement:

- `tools/validate_s3_original_file_storage.py` requires S3 bucket versioning to be `Enabled` for recovery/version-history protection.
- `S3PrivateObjectStore.purge_unversioned()` requires the original-object bucket to be confirmed never-versioned and rejects both `Enabled` and `Suspended`.

One bucket cannot satisfy both. Neither check should be weakened to make the other pass.

## Recommended target: two independent buckets

### A. Original-object bucket

Purpose: active, firm-namespaced original uploads.

- Dedicated private general-purpose S3 bucket; no unrelated workloads.
- Versioning must never have been enabled. An absent `Status` from a successful `GetBucketVersioning` response is required; `Enabled`, `Suspended`, errors, and unexpected response fields fail closed.
- Bucket-owner-enforced ownership; all four S3 public-access-block controls enabled.
- Default SSE-KMS with a customer-managed key dedicated to original objects.
- Firm-namespaced opaque object keys; no public URLs and no caller-controlled key components.
- Runtime role may stage, finalize, read, and reconcile objects, but may not delete finalized originals.
- Separate purge role may perform only the approved conditional physical-delete workflow. Bucket policy must deny deletes missing `s3:if-match`.
- During purge, a controlled policy freeze and worker drain must prevent every non-purge principal from writing, overwriting, or recreating finalized keys. A CLI `--quiesced` flag is only an assertion and is not a lock.

### B. Recovery-archive bucket

Purpose: encrypted multi-database backup bundles, including original-file bytes, used for restore and deletion recovery.

- Separate bucket and separate access boundary; never use the original-object bucket as the backup archive.
- Versioning must be `Enabled`; a suspended or unreadable state fails closed.
- Bucket-owner-enforced ownership and all four public-access-block controls enabled.
- Default SSE-KMS with a separate customer-managed archive key. Keep the application backup encryption key (`BACKUP_KEY`) separate from both KMS keys.
- Only backup/restore principals may write/read archive objects. The application runtime and original-object purge role receive no archive access.
- Retention, lifecycle expiry, legal hold, backup deletion, and key-retention semantics must be approved before lifecycle policies are deployed. Versioning alone is not a retention policy or proof of recoverability.

## Recovery and deletion semantics

1. Create a coordinated encrypted backup bundle while all relevant writers are stopped and tenant/object state is reconciled.
2. Upload the encrypted bundle to the recovery-archive bucket using a dedicated backup principal; record the archive object version ID, checksum, bundle identity, application revision, and archive-target fingerprint in protected evidence.
3. Restore only from a verified archive object version into a new isolated destination. Verify all database profile/firm bindings, SQLite integrity, original-file hashes/sizes, and KMS access before staging activation.
4. Physical purge operates only on the never-versioned original-object bucket and uses the existing ETag-conditional delete plus independently enforced no-writer controls.
5. A purge does not imply immediate erasure from encrypted backup archives. The approved policy must define backup retention and the point at which all recoverable copies expire or are cryptographically rendered inaccessible. Legal holds override routine expiry/deletion.

## Required implementation before this decision can be marked accepted

- Add explicit, non-overlapping configuration for original-object and recovery-archive bucket, region, and KMS key identifiers.
- Include both targets in non-secret configuration fingerprints; evidence for one target must not be reused for the other.
- Change the original-object preflight to require never-versioned state only; add a separate recovery-archive preflight requiring versioning enabled.
- Add an encrypted backup-archive upload operation and exact-version restore retrieval. Keep local encrypted bundle creation available for development and controlled offline workflows.
- Enforce separate IAM roles and bucket policies; verify effective policies and organization-level controls, not only role policy names.
- Add tests for same-bucket misconfiguration, missing/ambiguous versioning state, wrong KMS key, cross-role access denial, archive object-version selection, tamper detection, and restore integrity.
- Update deployment configuration examples, recovery runbook, purge checklist, and operational acceptance manifest.
- Complete live staging acceptance with synthetic tenant data, independent witness, measured RPO/RTO, and independent security review.

## Explicitly not approved by this proposal

- No AWS resource is created or modified.
- No bucket versioning is enabled, suspended, or disabled.
- No retention period or lifecycle expiration is selected.
- No production upload or purge is authorized.
- No claim is made that backup archives currently live in S3; the repository's encrypted bundle workflow must be integrated with the archive bucket before this architecture is implemented.

## Implementation status (2026-10-31)

PR #1024 implements the two independent read-only preflights, requires distinct bucket and KMS configuration in production preflight, changes the original-object validator to require never-versioned state, and binds the acceptance fingerprint to both targets. It also updates the runbook and deployment example. These are configuration and validation controls only. Encrypted backup-bundle upload, exact-version retrieval, backup/restore IAM separation, lifecycle/retention approval, and witnessed live recovery remain unimplemented and block acceptance of this architecture.

## Acceptance criteria

This decision is accepted only when the accountable deployment/storage owner approves the two-bucket design, qualified counsel/security approve the retention and legal-hold semantics, the required implementation and tests are merged, and the exact staging buckets/keys/IAM policies pass witnessed live acceptance.
