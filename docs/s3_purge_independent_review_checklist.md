# S3 original-file physical-purge — independent review and deployment acceptance

**Status:** Open. This checklist is a review instrument, not evidence that any control has passed. A passing CI run with fake S3 clients does not establish live AWS account, bucket, KMS, IAM, retention, or recovery behavior.

## Review record

- Repository commit / PR:
- Independent reviewer:
- Reviewer role and independence from implementation:
- Review date:
- Deployment environment:
- AWS account ID (record in protected evidence store; do not put secrets here):
- Region:
- Bucket name:
- Storage-target SHA-256 fingerprint:
- KMS key ARN:
- Purge operator identity:
- Change / approval reference:
- Result: Not started / Pass / Fail / Blocked
- Evidence references:

## 1. Destructive authorization and separation of duties

- [ ] Deletion request is scoped to the correct firm, object, document, and tenant database.
- [ ] Requester and approver are distinct active firm administrators.
- [ ] Purge operator is an active platform administrator and is distinct from both requester and approver.
- [ ] Firm and tenant catalog are disabled; all firm memberships are inactive.
- [ ] Legal hold is absent at the final authorization check; hold/release events remain immutable and auditable.
- [ ] The exact approved request reason and approval reason are retained in the purge audit record.
- [ ] A failed or interrupted purge cannot be reported as completed.

## 2. Bucket, object, and concurrency controls
**Architecture decision required before live acceptance:** the current read-only S3 validator requires `GetBucketVersioning=Enabled` for recovery, while the current physical-purge code requires a confirmed never-versioned bucket. These conditions are mutually exclusive for one bucket. Record the approved architecture (separate versioned recovery bucket plus never-versioned purge bucket, or a reviewed version-aware purge implementation) and prove it with separate target fingerprints and drills. Until then, mark both live storage acceptance and physical deletion BLOCKED. Do not change versioning on a live bucket to make a test pass.


- [ ] Live `GetBucketVersioning` confirms the target bucket has never had versioning enabled; `Enabled`, `Suspended`, unknown, or unexpected response states block deletion.
- [ ] The bucket policy and account controls prevent enabling versioning or changing relevant bucket controls during the purge window.
- [ ] The exact bucket, region, endpoint, and storage fingerprint match the signed/current acceptance evidence.
- [ ] Object key namespace is derived from the trusted firm ID and opaque object ID; no user-supplied key or URL is accepted.
- [ ] Staged and finalized object presence is reconciled; staged copies block physical purge.
- [ ] SHA-256, byte size, and KMS metadata are verified against tenant metadata immediately before deletion.
- [ ] `DeleteObject` uses the ETag observed before integrity verification as an `If-Match` precondition; a missing ETag or failed precondition blocks deletion and preserves the current object.
- [ ] The live bucket policy enforces conditional deletes with the `s3:if-match` condition key and denies unconditioned `DeleteObject`/`DeleteObjects` requests; verify the actual provider supports this API behavior.
- [ ] **Time-of-check/time-of-use review:** demonstrate that an external writer cannot overwrite or recreate the object between integrity verification and deletion. Conditional ETag deletion protects against a changed current object, but does not replace the IAM-enforced no-writer control; the CLI `--quiesced` flag is an operator assertion only and does not create a distributed lock or block S3 writes.
- [ ] The IAM policy and operational change freeze enforce the no-writer condition for the entire purge interval.
- [ ] The accepted `purge_writer_quiescence` manifest gate contains target-bound, independently witnessed evidence for worker drain, denial of both PutObject and DeleteObject by every non-purge principal, denial of writes by the purge role, policy-change freeze, and retained CloudTrail/negative-test evidence. A CLI `--quiesced` assertion alone is insufficient.
- [ ] Delete response, post-delete object absence, and post-delete bucket-versioning state are checked; ambiguous outcomes enter manual review.

## 3. KMS and IAM

Run the sanitized, read-only evidence collector separately under each actual application, backup/recovery, and purge workload identity:

```bash
COPILOT_OBJECT_STORAGE_BACKEND=s3 python tools/collect_s3_live_acceptance_evidence.py --json
```

The report fingerprints the bucket and KMS policies and summarizes the current assumed role's trust policy, attached managed policy documents, inline policy documents, permissions boundary, and KMS grants. It does not emit raw policy documents or credentials and never changes cloud configuration. One report describes only the identity that ran it. Independently evaluate SCPs, session policies, access-point/account policies, and effective permissions; retain the sanitized report and exact storage-target fingerprint in the protected evidence store. A successful collector exit code is not production approval and does not authorize purge.


- [ ] Live object metadata identifies the exact expected customer-managed KMS key ARN, not merely an alias or a generic SSE-KMS marker.
- [ ] KMS key policy permits only the intended application and recovery principals; no broad account-wide decrypt grant is present without documented approval.
- [ ] Purge operator role has only the minimum required read/verify/delete and KMS metadata permissions.
- [ ] Application runtime role cannot perform physical deletion.
- [ ] Bucket policy denies public access and unapproved principals; access logging/audit evidence is enabled and retained.
- [ ] KMS key is enabled, not pending deletion, and has a documented recovery/retention dependency.

## 4. Retention, legal holds, and recovery

- [ ] Data-retention schedule and tenant export/deletion policy are formally approved by the accountable owner.
- [ ] Applicable legal hold, litigation hold, and regulatory preservation requirements are checked before approval and again before purge.
- [ ] Backup retention, deletion, and key-retention behavior are consistent with the approved policy.
- [ ] A witnessed staging restore proves original bytes, metadata, firm binding, and KMS access are recoverable before any production purge.
- [ ] Rollback, staged-upload recovery, and deletion-recovery drills are witnessed and recorded.
- [ ] RPO/RTO objectives are approved and measured; no values are inferred from test results.

## 5. Execution evidence

- [ ] Read-only offboarding preflight is clear for the exact firm and deployment.
- [ ] Current production acceptance manifest matches the exact storage fingerprint.
- [ ] Synthetic staging drill has passed with an explicitly allowlisted synthetic firm and bucket.
- [ ] Dry-run report identifies only the expected approved requests and no other objects.
- [ ] Quiescence is enforced by deployment/IAM controls, not solely by the CLI flag.
- [ ] Apply is executed by the authorized operator under the approved change window.
- [ ] Post-run object inventory, tenant metadata, immutable audit events, and request states reconcile.
- [ ] Any mismatch or interrupted operation remains in manual review; no automatic retry or inferred success is allowed.

## 6. Reviewer conclusion

- Findings:
- Required remediations:
- Evidence locations:
- Final decision: Approve / Reject / Blocked
- Reviewer signature or approved review-system reference:
- Change owner acknowledgement:

**No production physical deletion is authorized by completing this document alone.** The release owner must also approve the retention policy, live cloud configuration, recovery evidence, and deployment change.
