# AWS S3 purge policy baseline (deployment template)

**Status:** Engineering template only — not approved or deployed. Replace every placeholder, merge these statements into the existing bucket policy, validate the resulting policy in the target AWS account, and obtain an independent review before use. This document does not authorize uploads or deletion.

## Scope and invariants

This baseline is for an S3 **general purpose bucket** dedicated to original matter files. The application currently requires a confirmed never-versioned bucket for physical purge; both `Enabled` and `Suspended` versioning block purge. Keep the application and purge roles separate.

- Application role: stage uploads, finalize staged objects into `.blob`, read/verify originals, and remove only its temporary `.staged` objects. It must not physically delete finalized `.blob` objects.
- Purge role: read and verify finalized originals, inspect bucket versioning, and perform a conditional `DeleteObject` on a finalized object only. It must not upload or overwrite objects.
- During the purge window, no principal may create, overwrite, copy into, or delete finalized `.blob` keys except the purge role's conditional delete. Stop and drain upload/finalize workers before enabling this window.
- A CLI `--quiesced` flag is an operator assertion, not an AWS lock. The temporary bucket-policy deny below is the enforceable write freeze; also freeze changes to bucket policy, versioning, lifecycle configuration, KMS key policy/state, and role attachments for the window.
- The ETag is a concurrency validator, not a substitute for the application's SHA-256 and byte-size verification.

## Required substitutions

| Placeholder | Required value |
|---|---|
| `<BUCKET_NAME>` | Exact dedicated bucket name |
| `<AWS_ACCOUNT_ID>` | 12-digit owning account |
| `<REGION>` | Bucket region |
| `<APPLICATION_ROLE_NAME>` | Exact runtime IAM role |
| `<PURGE_ROLE_NAME>` | Separate, human-operated purge role |
| `<INFRASTRUCTURE_ADMIN_ROLE_NAME>` | Restricted role allowed to change bucket controls |

Do not commit real account-specific ARNs, credentials, or environment secrets to this repository.

## 1. Persistent bucket-policy controls

Merge the following statements into the existing bucket policy after substituting the placeholders. Preserve existing TLS, public-access, encryption, logging, and ownership controls; do not replace the complete policy blindly.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyFinalizedObjectDeleteWithoutIfMatch",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:DeleteObject",
      "Resource": "arn:aws:s3:::<BUCKET_NAME>/firms/*/originals/*.blob",
      "Condition": {
        "Null": {
          "s3:if-match": "true"
        }
      }
    },
    {
      "Sid": "DenyApplicationRoleDeletingFinalizedObjects",
      "Effect": "Deny",
      "Principal": {
        "AWS": "arn:aws:iam::<AWS_ACCOUNT_ID>:role/<APPLICATION_ROLE_NAME>"
      },
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteObjectVersion"
      ],
      "Resource": "arn:aws:s3:::<BUCKET_NAME>/firms/*/originals/*.blob"
    },
    {
      "Sid": "DenyFinalizedObjectVersionDeletion",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:DeleteObjectVersion",
      "Resource": "arn:aws:s3:::<BUCKET_NAME>/firms/*/originals/*.blob"
    }
  ]
}
```

The first statement denies a finalized-object delete request if the `If-Match` condition key is absent. Conditional deletes with a specific ETag require both `s3:DeleteObject` and `s3:GetObject`; grant those only to the purge role for the finalized-object prefix. The application role must not receive `s3:DeleteObject` on the finalized-object prefix. It still needs narrowly scoped `s3:DeleteObject` on the `.staged` prefix because successful finalization removes its staged copy.

The bucket policy is not a complete identity policy. Explicitly scope identity policies for the two roles, and inspect inherited group, permission-set, session, boundary, organization, and resource policies for broader grants.

## 2. Temporary no-writer freeze for a purge window

After uploads and finalization workers have been stopped and drained, add the following temporary statement to the bucket policy. It denies creation/overwrite (including `CopyObject`, authorized through `s3:PutObject`) and deletion of finalized objects to every principal other than the dedicated purge role. The purge role must have no `s3:PutObject` permission, so the exception permits only its separately granted conditional delete.

```json
{
  "Sid": "PurgeWindowFreezeFinalizedObjectWriters",
  "Effect": "Deny",
  "Principal": "*",
  "Action": [
    "s3:PutObject",
    "s3:DeleteObject"
  ],
  "Resource": "arn:aws:s3:::<BUCKET_NAME>/firms/*/originals/*.blob",
  "Condition": {
    "ArnNotEquals": {
      "aws:PrincipalArn": "arn:aws:iam::<AWS_ACCOUNT_ID>:role/<PURGE_ROLE_NAME>"
    }
  }
}
```

This is a temporary operational control, not a permanent policy statement. Confirm in the target account that the policy is accepted and that the runtime role, every other writer, and any relevant service principal are denied writes during the freeze. The purge role remains unable to write because it has no allow for `s3:PutObject`. Do not begin the purge if the policy simulator or live negative tests do not demonstrate the expected denials.

While the freeze is active, block changes to the bucket's versioning, lifecycle configuration, bucket policy, KMS key policy/state, and the relevant IAM role policies/attachments. Use a separately controlled infrastructure-admin path for the temporary policy change and its removal. Record policy document hashes and CloudTrail evidence before and after the window. Remove the temporary statement only after post-purge inventory, tenant metadata, and audit reconciliation are complete.

## 3. Role permission boundaries

Use these as minimum-scope design requirements when reviewing identity policies:

### Application runtime role

- Allow `s3:PutObject` for `firms/*/originals/*.staged` and the required destination write/copy operation for `firms/*/originals/*.blob`.
- Allow `s3:GetObject` for the firm's staged/finalized object paths needed for readback and integrity verification.
- Allow `s3:DeleteObject` only for `firms/*/originals/*.staged`.
- Explicitly deny (or ensure no allow exists for) `s3:DeleteObject` and `s3:DeleteObjectVersion` on `firms/*/originals/*.blob`.
- Do not grant bucket-policy, versioning, lifecycle, IAM, or KMS-administration permissions.

### Purge operator role

- Allow `s3:GetBucketVersioning` on the exact bucket and `s3:ListBucket` only if required by the reviewed preflight.
- Allow `s3:GetObject` and `s3:DeleteObject` only on `firms/*/originals/*.blob`; conditional ETag deletion requires both.
- Do not grant `s3:PutObject`, `s3:DeleteObjectVersion`, bucket-policy, versioning, lifecycle, or KMS-administration permissions.
- Grant only the required KMS `DescribeKey` and decrypt permissions on the exact customer-managed key, subject to the key policy. The runtime upload path separately needs only the key operations required for its tested SSE-KMS write/read flow.
- Require a human operator, separate from requester and approver, with short-lived credentials and recorded change approval.

These are review requirements, not a substitute for evaluating the complete effective permissions in the target AWS account.

## 4. Acceptance sequence

1. Record account, region, bucket, exact KMS key ARN, application role ARN, purge role ARN, and a non-secret storage-configuration fingerprint in the protected acceptance record.
2. Confirm the bucket is general purpose, dedicated to this storage namespace, private, owned by the expected account, and has never had versioning enabled. Unknown or suspended versioning blocks physical purge.
3. Validate the persistent policy and both role policies. Prove the application role cannot delete a `.blob`; prove an unconditioned delete is denied; prove the purge role's ETag-matched delete succeeds only in an explicitly allowlisted synthetic staging bucket/firm.
4. Prove a wrong ETag returns a precondition failure and preserves the replacement object. Prove missing `If-Match` is denied by the bucket policy, not merely by application code.
5. In staging, stop/drain writers, enable the temporary freeze, and demonstrate that the application role and every other writer cannot `PutObject`/copy or delete finalized keys. Verify the purge role cannot write.
6. Run the synthetic staging purge only after the approved retention/legal-hold and recovery evidence gates pass. Reconcile object inventory, metadata, immutable audit events, and deletion request states.
7. Remove the temporary freeze under change control, verify normal staged upload/finalize/readback behavior, and retain policy hashes, CloudTrail records, test outputs, and reviewer sign-off.

A fake-S3 unit test or a successful policy JSON parse is not live-provider acceptance. Production purge remains blocked until the live bucket, KMS, IAM, no-writer, retention, recovery, and independent-review evidence is accepted.

## References

- AWS, [Enforce conditional deletes on Amazon S3 buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-delete-enforce.html).
- AWS, [How to perform conditional deletes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-deletes.html).
- AWS, [DeleteObject API](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html).

