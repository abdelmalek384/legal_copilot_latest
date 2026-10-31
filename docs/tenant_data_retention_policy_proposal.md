# Tenant data retention, export, legal-hold and deletion policy — approval draft

**Status:** DRAFT — NOT APPROVED FOR PRODUCTION. This document proposes conservative operational defaults for owner, privacy/legal counsel, and security review. It does not determine statutory retention periods, waive client duties, or authorize deletion. No automated expiry or permanent deletion may be enabled on the strength of this draft.

## 1. Scope and data classes

This policy applies to tenant-controlled and operational data held by the legal application:

| Data class | Examples | Proposed owner / scope | Retention decision |
|---|---|---|---|
| Matter records | Cases, clients, tasks, notes, deadlines, fees, sessions | Firm / matter | Set by the firm's engagement terms and applicable professional, court, regulatory and limitation duties; exact schedule requires counsel approval |
| Matter documents | Original uploads, extracted text, chunks, annotations, review corrections, previews | Firm / matter | Same matter schedule; preserve originals and provenance while the matter is retained or a hold applies |
| Tenant audit evidence | Access, export, hold, deletion request/approval, purge tombstones | Firm-scoped, with restricted platform operations access | Separate immutable-audit schedule required; do not delete with ordinary matter content by default |
| Identity and membership | Global identity, firm memberships, invitations, recovery tokens, sessions | Control plane | Separate identity/security schedule; expired token/session cleanup must preserve required security audit evidence |
| Backups and recovery copies | Encrypted control-plane, tenant and corpus bundles; original-object copies | Restricted operations | Defined backup rotation and legal-hold exception required; deletion from primary storage does not imply immediate deletion from retained backups |
| Shared legal corpus | Legal source/version/review records and licensed content | Platform / source-rights scope | Govern under source licence, provenance and review policy; never mix tenant matter content into the corpus |
| Operational telemetry | Security logs, job results, health checks, SMTP delivery metadata | Operations | Minimize content and identifiers; set a separate approved security-log schedule |

## 2. Conservative interim controls (effective only as engineering defaults)

Until this policy is approved:
- No automatic permanent deletion, age-based purge, or lifecycle expiry of tenant originals or matter databases.
- A legal hold blocks deletion and remains effective until an authorized release with a reason is recorded. Hold events and deletion-approval events remain immutable.
- A clear offboarding preflight is not legal authorization. Export, contractual obligations, backup retention and legal holds must be reviewed before deletion is proposed.
- A deletion request requires a distinct second firm administrator to approve; execution requires a distinct active platform operator after firm/catalog disablement, membership/invitation revocation, integrity checks and storage reconciliation.
- Any ambiguous object, missing byte, digest mismatch, staged copy, versioning ambiguity, failed conditional delete, or database commit failure blocks completion and enters manual review.
- Never promise secure erasure of temporary plaintext or SSD/copy-on-write storage. Record cleanup as best-effort and use restricted encrypted staging.
- Production S3 deletion remains blocked until the versioning architecture conflict and live AWS/IAM/KMS controls are resolved and independently accepted.

These defaults are safeguards, not a retention schedule and not a substitute for a contract or legal review.

## 3. Tenant export requirements

A tenant export should be an authenticated, audited, firm-scoped operation that:
1. Resolves the firm only from trusted server-side membership context; never accepts a caller-supplied database path or storage key.
2. Includes a manifest describing export time, application/schema revision, tenant identifier in the protected export metadata, record counts by approved category, and per-file SHA-256/byte size.
3. Includes matter records, document metadata, original bytes where retained, extracted text and provenance, user annotations/review history, and the tenant audit records that the approved export policy requires.
4. Excludes other firms, global credentials, session tokens, platform secrets, unrelated shared-corpus internals, and operational credentials.
5. Applies legal holds and export restrictions; a hold preserves material but does not automatically grant a user authority to export it.
6. Uses encryption in transit and at rest, short-lived access, least-privilege operator access, and an approved delivery channel. Never deliver an export through a public object URL.
7. Records requester, approver where required, scope, manifest digest, destination class, completion/failure and expiry/deletion of the export copy without logging matter contents.
8. Supports integrity verification and a documented process for partial/failed exports; do not mark an incomplete export as complete.

**Implementation status:** the repository has tenant-aware backup/restore and security-audit export capabilities, but a complete client-facing tenant data export package and its approval/expiry workflow are not yet accepted. Do not describe a database backup as a complete client export.

## 4. Legal holds and preservation

- Holds must be matter/document scoped, set by an authorized firm administrator with a reason, actor and timestamp.
- Releasing a hold requires an authorized actor, a non-empty reason, and an immutable event. Confirm no other hold or preservation duty applies before release.
- A hold blocks deletion-request approval and purge. Re-check the hold immediately before destructive execution.
- Holds must cover primary originals, extracted/derived matter content, relevant metadata and backup copies to the extent required by the approved legal process.
- Preserve a record of the hold's authority, scope, start, changes, release, and affected data classes in a restricted evidence store.
- Do not infer that a firm closure, contract end, account suspension, or deletion request releases a hold.

## 5. Offboarding and deletion workflow

Proposed sequence:
1. Receive and authenticate the firm's authorized request; identify the exact firm and scope.
2. Review engagement terms, applicable law, professional duties, litigation/regulatory holds, third-party processor obligations and any pending matter.
3. Produce and verify the approved tenant export before any irreversible deletion, unless a documented legal restriction prevents export.
4. Disable the firm and catalog binding; revoke active memberships and outstanding invitations using audited lifecycle operations.
5. Run the read-only offboarding preflight and S3 reconciliation. Resolve every orphan, mismatch, staged/quarantined object, pending request, hold, and integrity finding.
6. Require distinct requester, second firm-admin approver and platform purge operator. Verify each actor's live role and status at execution.
7. Execute only the exact approved object/database scope under the reviewed storage architecture, maintenance window and IAM-enforced write freeze. The CLI `--quiesced` flag is an operator assertion, not a lock.
8. Reconcile object inventory, tenant metadata, deletion tombstones and immutable audit events. Ambiguous results remain blocked/manual-review; never infer success.
9. Retain only the minimum tombstone/audit evidence required by the separately approved schedule. Tombstones must not retain matter content or original storage paths.
10. Verify expiry/removal of retained backup copies only according to the approved backup schedule and hold exceptions. Do not claim complete erasure while recoverable backup copies remain.

## 6. Backup and derived-copy treatment

- Approve separate retention windows for primary data, encrypted backups, export packages, restore staging, temporary plaintext, logs, and synthetic acceptance artifacts.
- Define how legal holds suspend backup expiry and how release resumes it.
- Record backup bundle identity, encryption-key identifier/version, creation time, covered profiles/tenants, checksum and expiry schedule.
- A restore must preserve firm binding and legal-hold/deletion history. A restored copy must not silently reactivate a disabled firm.
- Key deletion/rotation is not a shortcut for deleting individual tenant data unless cryptographic erasure is specifically designed, legally approved, and independently verified.
- Temporary plaintext cleanup is not guaranteed secure erasure on SSD or copy-on-write filesystems; use encrypted restricted staging and document residual risk.

## 7. Decisions requiring named approval

The accountable owner, privacy/legal counsel and security reviewer must record decisions for:
- Applicable jurisdictions, professional duties, client-contract terms and any mandatory retention/preservation periods.
- Exact duration and trigger for each data class in Section 1, including audit evidence and identity lifecycle records.
- Export format, included categories, delivery mechanism, approver and export-copy expiry.
- Legal-hold authority, scope, conflict resolution, release authority and backup treatment.
- Deletion eligibility, notice period, second-person approval, tombstone fields and final purge authority.
- Backup rotation, restore-staging cleanup, processor copies and post-deletion backup expiry.
- S3 versioning architecture: separate versioned recovery and never-versioned purge buckets, or a reviewed version-aware purge that deletes every retained version/delete marker subject to policy.
- Evidence store, signatories, review cadence and policy-change process.

No retention duration is filled in by engineering because the correct values depend on law, contract, jurisdiction and professional obligations.

## 8. Required acceptance evidence

The `retention_export_deletion_policy` release gate must remain blocked until the approved policy version, named approver, approval timestamp and evidence reference are recorded in the controlled acceptance manifest. Separate witnessed evidence is still required for live storage acceptance and the four recovery scenarios: staging restore, rollback, staged-upload recovery and deletion recovery.

**Approval record (complete only after review):**
- Policy version:
- Accountable data owner:
- Privacy/legal counsel:
- Security reviewer:
- Jurisdictions and client-contract scope:
- Approved on (timezone-aware timestamp):
- Evidence reference:
- Exceptions and expiry:
- Next review date:

**Until this record is completed and the release gate accepts the evidence, this proposal is not an approved policy and production retention/deletion remains blocked.**
