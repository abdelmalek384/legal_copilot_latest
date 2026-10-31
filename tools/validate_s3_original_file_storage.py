#!/usr/bin/env python3
"""Read-only preflight for the private S3 bucket and customer-managed KMS key."""
from __future__ import annotations

import argparse
import json
import os
import sys


def validate_s3_configuration(s3_client, kms_client, *, bucket: str, configured_key: str) -> dict:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    try:
        s3_client.head_bucket(Bucket=bucket)
        check("bucket_accessible", True, "configured bucket is accessible to this operator identity")
    except Exception:
        check("bucket_accessible", False, "configured bucket could not be accessed")

    key_arn = None
    try:
        key_response = kms_client.describe_key(KeyId=configured_key)
        key = key_response.get("KeyMetadata", {})
        key_arn = key.get("Arn")
        key_ok = (
            key.get("KeyState") == "Enabled"
            and key.get("KeyUsage") == "ENCRYPT_DECRYPT"
            and key.get("KeySpec") == "SYMMETRIC_DEFAULT"
            and key.get("KeyManager") == "CUSTOMER"
            and isinstance(key_arn, str)
        )
        check("kms_key", key_ok, "configured key must be enabled, customer-managed, symmetric, and usable for encryption")
    except Exception:
        check("kms_key", False, "configured KMS key could not be inspected")

    try:
        response = s3_client.get_public_access_block(Bucket=bucket)
        block = response.get("PublicAccessBlockConfiguration", {})
        keys = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
        passed = all(block.get(key) is True for key in keys)
        check("public_access_block", passed, "all four S3 public-access-block controls must be enabled")
    except Exception:
        check("public_access_block", False, "bucket public-access-block configuration is missing or unreadable")

    try:
        response = s3_client.get_bucket_ownership_controls(Bucket=bucket)
        rules = response.get("OwnershipControls", {}).get("Rules", [])
        passed = any(rule.get("ObjectOwnership") == "BucketOwnerEnforced" for rule in rules)
        check("bucket_owner_enforced", passed, "ACLs must be disabled with BucketOwnerEnforced")
    except Exception:
        check("bucket_owner_enforced", False, "bucket ownership controls are missing or unreadable")

    versioning_status = None
    versioning_read = False
    try:
        response = s3_client.get_bucket_versioning(Bucket=bucket)
        versioning_read = isinstance(response, dict)
        versioning_status = response.get("Status") if versioning_read else None
        check(
            "versioning",
            versioning_status == "Enabled",
            "bucket versioning must be enabled for version-history recovery; this requirement conflicts with the current physical-purge implementation",
        )
        never_versioned = versioning_read and versioning_status is None and set(response) <= {"ResponseMetadata"}
        check(
            "physical_purge_versioning_compatibility",
            never_versioned,
            "current physical purge requires a confirmed never-versioned bucket; Enabled, Suspended, unknown, and unexpected response states block purge",
        )
    except Exception:
        check("versioning", False, "bucket versioning state could not be verified")
        check(
            "physical_purge_versioning_compatibility",
            False,
            "physical purge compatibility cannot be established because bucket versioning state could not be verified",
        )

    try:
        response = s3_client.get_bucket_encryption(Bucket=bucket)
        rules = response.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
        matched = False
        for rule in rules:
            algorithm = rule.get("ApplyServerSideEncryptionByDefault", {})
            key_id = algorithm.get("KMSMasterKeyID")
            if algorithm.get("SSEAlgorithm") != "aws:kms" or not key_arn:
                continue
            # GetBucketEncryption may return the configured alias, key ID, or
            # ARN. Resolve it before comparing; string equality would reject
            # a correctly configured alias and could not prove key identity.
            if not isinstance(key_id, str) or not key_id.strip():
                continue
            try:
                bucket_key = kms_client.describe_key(KeyId=key_id).get("KeyMetadata", {})
                bucket_key_arn = bucket_key.get("Arn")
            except Exception:
                continue
            if isinstance(bucket_key_arn, str) and bucket_key_arn == key_arn:
                matched = True
        check("default_sse_kms", matched, "default bucket encryption must require the configured customer-managed KMS key")
    except Exception:
        check("default_sse_kms", False, "bucket default encryption could not be verified")

    failed = [item["name"] for item in checks if not item["passed"]]
    return {
        "bucket": bucket,
        "bucket_versioning_status": versioning_status if versioning_read else "unknown",
        "configured_kms_key": configured_key,
        "checks": checks,
        "failed_checks": failed,
        "manual_review_required": [
            "independent review of bucket policy and IAM permissions",
            "firm-isolation policy and KMS grants",
            "key rotation and recovery rehearsal",
            "live upload/download/reconciliation/backup/restore/deletion drill",
            "resolve incompatible versioning requirements: recovery preflight requires Enabled while physical purge requires a never-versioned bucket; use separate buckets or implement and review version-aware deletion of every retained version",
        ],
        "production_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only S3/KMS configuration checks; this tool never changes cloud settings."
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
    region = os.environ.get("COPILOT_S3_REGION", "").strip()
    key_id = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
    endpoint = os.environ.get("COPILOT_S3_ENDPOINT_URL", "").strip() or None
    if not bucket or not region or not key_id:
        parser.error("COPILOT_S3_BUCKET, COPILOT_S3_REGION, and COPILOT_S3_KMS_KEY_ID are required")
    try:
        import boto3
        s3_client = boto3.client("s3", region_name=region, endpoint_url=endpoint)
        kms_client = boto3.client("kms", region_name=region)
        result = validate_s3_configuration(s3_client, kms_client, bucket=bucket, configured_key=key_id)
    except ImportError:
        print("S3/KMS preflight unavailable: AWS SDK is not installed", file=sys.stderr)
        return 2
    except Exception:
        print("S3/KMS preflight could not safely complete", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"S3/KMS configuration preflight for bucket {bucket}")
        for check in result["checks"]:
            print(f"- {'PASS' if check['passed'] else 'FAIL'} {check['name']}: {check['detail']}")
        print("Production ready: NO")
        print("Manual review and live recovery drills remain mandatory.")
    return 0 if not result["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
