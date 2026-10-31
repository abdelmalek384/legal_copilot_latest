# AWS S3 recovery archive IAM baseline

**Status:** Deployment template only — not approved, deployed, or live-tested. This is separate from the original-object bucket policy. Replace placeholders, inspect the complete effective policies (including permission boundaries, session policies, SCPs, resource policies, and KMS key policy), and obtain independent review before deployment.

## Required trust boundaries

| Principal | Archive access | Must not have |
|---|---|---|
| Backup writer | Put encrypted bundle objects; abort its incomplete multipart uploads; read back the exact version it just created for checksum verification | Delete objects/versions; change bucket policy/versioning/lifecycle; administer KMS |
| Restore reader | Read exact object versions; inspect bucket versioning | Put, overwrite, delete, or administer bucket/KMS |
| Application runtime | None | All recovery-archive S3 and KMS permissions |
| Original-object purge role | None | All recovery-archive S3 and KMS permissions |
| Retention administrator | Separately controlled lifecycle/legal-hold operations only, under approved policy | Routine backup/restore credentials; application runtime access |
| Infrastructure administrator | Change bucket/IAM/KMS configuration under change control | Routine application or purge execution |

Use separate role sessions and short-lived credentials for backup and restore. A shared operator role is not acceptable evidence of separation. The application Fernet `BACKUP_KEY` is independent of the archive SSE-KMS key and must be stored in a separate secret-management boundary.

## Required bucket controls

- Dedicated bucket, distinct from the never-versioned original-object bucket.
- S3 versioning `Enabled`; reject `Suspended`, absent, or unreadable status.
- S3 Block Public Access: all four controls enabled.
- Object Ownership: `BucketOwnerEnforced`.
- Default encryption: SSE-KMS with the dedicated customer-managed symmetric archive key.
- Bucket policy denies non-TLS requests, unencrypted puts, and puts using any KMS key other than the configured archive key.
- Enable CloudTrail S3 data events for the archive prefix and KMS audit events; retain them in the separately approved security evidence store.
- Do not configure lifecycle expiry, noncurrent-version expiry, or KMS key deletion until retention/legal-hold policy is approved.

## Identity-policy templates

Substitute exact account, region, bucket, prefix, role names, and key ARN. Do not add wildcard resources beyond the documented archive prefix.

### Backup writer role

Required S3 actions:
- `s3:GetBucketVersioning` on the exact bucket.
- `s3:PutObject`, `s3:GetObjectVersion`, and `s3:AbortMultipartUpload` on `arn:aws:s3:::<RECOVERY_BUCKET>/database-recovery/v1/*`.

Both the post-upload verification and the restore flow explicitly supply `VersionId`; their `HeadObject`/`GetObject` requests therefore require `s3:GetObjectVersion`, not unversioned `s3:GetObject`. The role does not need `s3:ListBucket`, `s3:ListBucketVersions`, `s3:DeleteObject`, or `s3:DeleteObjectVersion`.

Required KMS actions on the one archive key:
- `kms:GenerateDataKey` for SSE-KMS uploads.
- `kms:Decrypt` for multipart upload and exact-version readback.

### Restore reader role

Required S3 actions:
- `s3:GetBucketVersioning` on the exact bucket.
- `s3:GetObjectVersion` on `arn:aws:s3:::<RECOVERY_BUCKET>/database-recovery/v1/*` for version-pinned `HeadObject`/`GetObject` calls.

Required KMS action:
- `kms:Decrypt` on the one archive key.

No archive write, object-delete, version-delete, lifecycle, bucket-policy, or versioning-administration action is required by the implemented download path.

### KMS key policy

The archive key policy must name the backup-writer and restore-reader role ARNs for only the actions above. Do not grant the application runtime or original-object purge role access. Keep key administrators separate from routine backup/restore operators. Key disablement, scheduled deletion, rotation, grant creation, and policy changes require controlled change approval and must not invalidate the approved backup retention window.

## Bucket-policy deny template

This is an additive baseline, not a replacement bucket policy. Preserve the required public-access, ownership, logging, and TLS controls. Replace every placeholder.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::<RECOVERY_BUCKET>",
        "arn:aws:s3:::<RECOVERY_BUCKET>/*"
      ],
      "Condition": {"Bool": {"aws:SecureTransport": "false"}}
    },
    {
      "Sid": "DenyArchivePutWithoutKms",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::<RECOVERY_BUCKET>/database-recovery/v1/*",
      "Condition": {"StringNotEquals": {"s3:x-amz-server-side-encryption": "aws:kms"}}
    },
    {
      "Sid": "DenyArchivePutWithWrongKmsKey",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::<RECOVERY_BUCKET>/database-recovery/v1/*",
      "Condition": {"StringNotEquals": {"s3:x-amz-server-side-encryption-aws-kms-key-id": "<ARCHIVE_KMS_KEY_ARN>"}}
    },
    {
      "Sid": "DenyApplicationAndPurgeRolesArchiveAccess",
      "Effect": "Deny",
      "Principal": {
        "AWS": [
          "arn:aws:iam::<AWS_ACCOUNT_ID>:role/<APPLICATION_ROLE>",
          "arn:aws:iam::<AWS_ACCOUNT_ID>:role/<ORIGINAL_OBJECT_PURGE_ROLE>"
        ]
      },
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::<RECOVERY_BUCKET>",
        "arn:aws:s3:::<RECOVERY_BUCKET>/*"
      ]
    },
    {
      "Sid": "DenyBackupAndRestoreRolesDeletingArchiveVersions",
      "Effect": "Deny",
      "Principal": {
        "AWS": [
          "arn:aws:iam::<AWS_ACCOUNT_ID>:role/<BACKUP_WRITER_ROLE>",
          "arn:aws:iam::<AWS_ACCOUNT_ID>:role/<RESTORE_READER_ROLE>"
        ]
      },
      "Action": ["s3:DeleteObject", "s3:DeleteObjectVersion"],
      "Resource": "arn:aws:s3:::<RECOVERY_BUCKET>/database-recovery/v1/*"
    }
  ]
}
```

S3 bucket-policy condition-key support and exact IAM action semantics must be checked against the target AWS partition/account before deployment. The bucket default SSE-KMS configuration is a second control; it does not replace explicit identity and resource policy review. Do not assume this policy prevents an authorized infrastructure administrator from changing the policy itself.

## Mandatory live acceptance

1. Capture the exact bucket ARN, region, versioning state, public-access block, ownership controls, encryption configuration, archive KMS key ARN, backup/restore role ARNs, and policy-document hashes.
2. Prove backup writer can upload an encrypted synthetic bundle, abort a controlled incomplete multipart upload, and read back only the exact returned version.
3. Prove restore reader can read that exact version and cannot put, overwrite, delete, or list unrelated objects.
4. Prove application runtime and original-object purge role are denied all archive S3 access and archive KMS use, including via inherited policies and role chaining.
5. Prove backup writer and restore reader cannot delete current or noncurrent versions or alter bucket controls.
6. Prove wrong-key and non-TLS puts are denied by the bucket policy, not merely rejected by application code.
7. Verify CloudTrail records the expected role/session, bucket, key, version ID, and KMS key without logging object content or secrets.
8. Run the witnessed restore, rollback, staged-upload recovery, and deletion-recovery exercises. Measure and approve RPO/RTO.
9. Obtain independent security sign-off and approve retention, export, legal-hold, expiry, and key-retention semantics before any lifecycle rule is enabled.

A JSON policy review, IAM simulator result, unit test, or read-only preflight is not live acceptance. No AWS policy is deployed by this repository change.
