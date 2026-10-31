#!/usr/bin/env python3
"""Read-only preflight for the separately versioned encrypted S3 recovery archive."""
from __future__ import annotations

import argparse
import json
import os
import sys


def validate_recovery_archive_configuration(
    s3_client, kms_client, *, bucket: str, configured_key: str, original_bucket: str,
    original_key: str,
) -> dict:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check(
        "separate_recovery_bucket",
        bool(bucket and bucket != original_bucket),
        "recovery archive bucket must be distinct from the original-object bucket",
    )

    try:
        s3_client.head_bucket(Bucket=bucket)
        check("recovery_bucket_accessible", True, "recovery archive bucket is accessible to this operator identity")
    except Exception:
        check("recovery_bucket_accessible", False, "recovery archive bucket could not be accessed")

    try:
        response = s3_client.get_public_access_block(Bucket=bucket)
        block = response.get("PublicAccessBlockConfiguration", {})
        keys = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
        check(
            "recovery_public_access_block",
            all(block.get(key) is True for key in keys),
            "all four S3 public-access-block controls must be enabled",
        )
    except Exception:
        check("recovery_public_access_block", False, "recovery bucket public-access-block configuration is missing or unreadable")

    try:
        response = s3_client.get_bucket_ownership_controls(Bucket=bucket)
        rules = response.get("OwnershipControls", {}).get("Rules", [])
        passed = any(rule.get("ObjectOwnership") == "BucketOwnerEnforced" for rule in rules)
        check("recovery_bucket_owner_enforced", passed, "recovery bucket ACLs must be disabled with BucketOwnerEnforced")
    except Exception:
        check("recovery_bucket_owner_enforced", False, "recovery bucket ownership controls are missing or unreadable")

    try:
        response = s3_client.get_bucket_versioning(Bucket=bucket)
        check(
            "recovery_versioning_enabled",
            isinstance(response, dict) and response.get("Status") == "Enabled",
            "recovery archive bucket versioning must be Enabled; Suspended, absent, unknown, or unreadable state fails closed",
        )
    except Exception:
        check("recovery_versioning_enabled", False, "recovery archive bucket versioning state could not be verified")

    key_arn = None
    original_key_arn = None
    try:
        original_key_arn = kms_client.describe_key(KeyId=original_key).get("KeyMetadata", {}).get("Arn")
    except Exception:
        original_key_arn = None
    try:
        response = kms_client.describe_key(KeyId=configured_key)
        metadata = response.get("KeyMetadata", {})
        key_arn = metadata.get("Arn")
        valid_key = (
            isinstance(key_arn, str)
            and metadata.get("KeyState") == "Enabled"
            and metadata.get("KeyUsage") == "ENCRYPT_DECRYPT"
            and metadata.get("KeySpec") == "SYMMETRIC_DEFAULT"
            and metadata.get("KeyManager") == "CUSTOMER"
        )
        check("recovery_kms_key", valid_key, "archive key must be enabled, customer-managed, symmetric, and usable for encryption")
    except Exception:
        check("recovery_kms_key", False, "configured recovery KMS key could not be inspected")
    check(
        "separate_recovery_kms_key",
        bool(key_arn and original_key_arn and key_arn != original_key_arn),
        "recovery archive must use a different canonical KMS key from original-object storage",
    )

    try:
        response = s3_client.get_bucket_encryption(Bucket=bucket)
        rules = response.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
        matched = False
        for rule in rules:
            default = rule.get("ApplyServerSideEncryptionByDefault", {})
            key_id = default.get("KMSMasterKeyID")
            if default.get("SSEAlgorithm") != "aws:kms" or not isinstance(key_id, str) or not key_id.strip() or not key_arn:
                continue
            try:
                resolved = kms_client.describe_key(KeyId=key_id).get("KeyMetadata", {}).get("Arn")
            except Exception:
                continue
            if resolved == key_arn:
                matched = True
        check("recovery_default_sse_kms", matched, "recovery archive default encryption must resolve to the configured customer-managed KMS key")
    except Exception:
        check("recovery_default_sse_kms", False, "recovery archive default encryption could not be verified")

    failed = [item["name"] for item in checks if not item["passed"]]
    return {
        "recovery_bucket": bucket,
        "original_bucket": original_bucket,
        "configured_recovery_kms_key": configured_key,
        "recovery_kms_key_arn": key_arn,
        "checks": checks,
        "failed_checks": failed,
        "production_ready": False,
        "manual_review_required": [
            "verify effective backup/restore IAM roles and deny archive access to application runtime and purge principals",
            "approve archive retention, legal hold, expiry, and KMS key-retention semantics",
            "implement and test encrypted bundle upload and exact-version restore retrieval",
            "perform witnessed restore/rollback and measure RPO/RTO against an approved target",
            "obtain independent security review and live staging acceptance",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only preflight for a separate versioned S3 recovery archive; never approves production."
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)
    bucket = os.environ.get("COPILOT_S3_RECOVERY_BUCKET", "").strip()
    region = os.environ.get("COPILOT_S3_RECOVERY_REGION", "").strip()
    key_id = os.environ.get("COPILOT_S3_RECOVERY_KMS_KEY_ID", "").strip()
    original_bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
    original_key = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
    endpoint = os.environ.get("COPILOT_S3_RECOVERY_ENDPOINT_URL", "").strip() or None
    if not bucket or not region or not key_id or not original_bucket or not original_key:
        parser.error(
            "COPILOT_S3_RECOVERY_BUCKET, COPILOT_S3_RECOVERY_REGION, "
            "COPILOT_S3_RECOVERY_KMS_KEY_ID, COPILOT_S3_BUCKET, and COPILOT_S3_KMS_KEY_ID are required"
        )
    try:
        import boto3
        s3 = boto3.client("s3", region_name=region, endpoint_url=endpoint)
        kms = boto3.client("kms", region_name=region)
        result = validate_recovery_archive_configuration(
            s3, kms, bucket=bucket, configured_key=key_id,
            original_bucket=original_bucket, original_key=original_key
        )
    except ImportError:
        print("S3/KMS recovery-archive preflight unavailable: AWS SDK is not installed", file=sys.stderr)
        return 2
    except Exception:
        print("S3/KMS recovery-archive preflight could not safely complete", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"Recovery archive preflight for bucket {bucket}")
        for item in result["checks"]:
            print(f"- {'PASS' if item['passed'] else 'FAIL'} {item['name']}: {item['detail']}")
        print("Production ready: NO")
        print("Archive transport, retention approval, and witnessed recovery remain mandatory.")
    return 0 if not result["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
