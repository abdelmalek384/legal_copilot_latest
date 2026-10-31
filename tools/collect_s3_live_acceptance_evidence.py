#!/usr/bin/env python3
"""Collect sanitized, read-only S3/KMS/IAM evidence for a deployment acceptance review.

This tool never changes cloud configuration and never claims production readiness.
Run it separately under each real workload/operator role; a single caller identity
does not prove the permissions of other roles.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from typing import Any


def _policy_document(raw: object) -> dict[str, Any] | None:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            value = json.loads(raw)
        except (TypeError, ValueError):
            return None
        return value if isinstance(value, dict) else None
    return None


def _statements(policy: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(policy, dict):
        return []
    value = policy.get("Statement", [])
    if isinstance(value, dict):
        value = [value]
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _items(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def _wildcard_principal(value: object) -> bool:
    if value == "*":
        return True
    if isinstance(value, dict):
        return any("*" in _items(item) for item in value.values())
    return False


def _secure_transport_deny(statements: list[dict[str, Any]]) -> bool:
    for statement in statements:
        if str(statement.get("Effect", "")).lower() != "deny":
            continue
        actions = {item.lower() for item in _items(statement.get("Action"))}
        if not any(action in {"s3:*", "s3:getobject", "s3:putobject", "s3:deleteobject"} for action in actions):
            continue
        condition = statement.get("Condition", {})
        if not isinstance(condition, dict):
            continue
        for operator, values in condition.items():
            if not isinstance(values, dict):
                continue
            for key, value in values.items():
                if key.lower() == "aws:securetransport" and operator.lower() in {"bool", "boolifexists"}:
                    if str(value).lower() == "false":
                        return True
    return False


def _conditional_delete_deny(statements: list[dict[str, Any]]) -> bool:
    for statement in statements:
        if str(statement.get("Effect", "")).lower() != "deny":
            continue
        actions = {item.lower() for item in _items(statement.get("Action"))}
        if not ({"s3:*", "s3:deleteobject"} & actions):
            continue
        condition = statement.get("Condition", {})
        if not isinstance(condition, dict):
            continue
        for operator, values in condition.items():
            if operator.lower() != "null" or not isinstance(values, dict):
                continue
            for key, value in values.items():
                if key.lower() == "s3:if-match" and str(value).lower() == "true":
                    return True
    return False


def _policy_fingerprint(document: dict[str, Any] | None) -> str | None:
    if document is None:
        return None
    payload = json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _assumed_role_name(arn: object) -> str | None:
    if not isinstance(arn, str):
        return None
    match = re.fullmatch(r"arn:[^:]+:sts::[0-9]{12}:assumed-role/(.+?)/[^/]+", arn)
    # IAM GetRole expects the friendly role name, not the path-bearing ARN segment.
    # Preserve path separately in the role ARN returned by GetRole.
    return match.group(1).rsplit("/", 1)[-1] if match else None


def _policy_summary(document: object) -> dict[str, Any]:
    policy = _policy_document(document)
    statements = _statements(policy)
    broad = []
    for item in statements:
        if str(item.get("Effect", "")).lower() != "allow":
            continue
        actions = _items(item.get("Action"))
        resources = _items(item.get("Resource"))
        if "*" in actions or "iam:*" in actions or "s3:*" in actions or "kms:*" in actions:
            broad.append("wildcard_action")
        if "*" in resources:
            broad.append("wildcard_resource")
    return {
        "sha256": _policy_fingerprint(policy),
        "statement_count": len(statements),
        "broad_allow_flags": sorted(set(broad)),
    }


def _list_all(iam_client, method: str, *, RoleName: str, result_key: str) -> list[Any]:
    function = getattr(iam_client, method)
    items: list[Any] = []
    marker = None
    while True:
        args = {"RoleName": RoleName}
        if marker:
            args["Marker"] = marker
        response = function(**args)
        items.extend(response.get(result_key, []))
        if not response.get("IsTruncated"):
            break
        marker = response.get("Marker")
        if not marker:
            raise RuntimeError("IAM policy listing was truncated without a continuation marker")
    return items


def _managed_policy_evidence(iam_client, policy_arn: str) -> dict[str, Any]:
    metadata = iam_client.get_policy(PolicyArn=policy_arn).get("Policy", {})
    version_id = metadata.get("DefaultVersionId")
    if not isinstance(version_id, str) or not version_id:
        raise RuntimeError("managed IAM policy has no default version")
    version = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=version_id)
    summary = _policy_summary(version.get("PolicyVersion", {}).get("Document"))
    return {
        "arn": policy_arn,
        "default_version_id": version_id,
        **summary,
    }


def collect_live_evidence(s3_client, kms_client, sts_client, iam_client, *, bucket: str, key_id: str) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: str):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    caller: dict[str, Any] = {}
    try:
        identity = sts_client.get_caller_identity()
        caller = {
            "account": identity.get("Account"),
            "arn": identity.get("Arn"),
            "user_id": identity.get("UserId"),
        }
        check("caller_identity", bool(caller["account"] and caller["arn"]), "current AWS principal identified")
    except Exception:
        check("caller_identity", False, "STS caller identity could not be read")

    bucket_policy = None
    try:
        raw = s3_client.get_bucket_policy(Bucket=bucket).get("Policy")
        bucket_policy = _policy_document(raw)
        statements = _statements(bucket_policy)
        check("bucket_policy_readable", bucket_policy is not None, "bucket policy was read and parsed")
        check(
            "bucket_policy_no_public_allow",
            not any(
                str(item.get("Effect", "")).lower() == "allow" and _wildcard_principal(item.get("Principal"))
                for item in statements
            ),
            "no wildcard-principal Allow statement was found; confirm account and access-point policies separately",
        )
        check(
            "bucket_policy_tls_deny",
            _secure_transport_deny(statements),
            "bucket policy must explicitly deny insecure transport",
        )
        check(
            "bucket_policy_conditional_delete",
            _conditional_delete_deny(statements),
            "bucket policy must deny DeleteObject when s3:if-match is absent",
        )
    except Exception:
        check("bucket_policy_readable", False, "bucket policy is absent or could not be read")
        check("bucket_policy_no_public_allow", False, "bucket policy could not be inspected")
        check("bucket_policy_tls_deny", False, "bucket policy could not be inspected")
        check("bucket_policy_conditional_delete", False, "bucket policy could not be inspected")

    key_metadata: dict[str, Any] = {}
    key_arn = None
    try:
        metadata = kms_client.describe_key(KeyId=key_id).get("KeyMetadata", {})
        key_arn = metadata.get("Arn")
        key_metadata = {
            "arn": key_arn,
            "state": metadata.get("KeyState"),
            "usage": metadata.get("KeyUsage"),
            "spec": metadata.get("KeySpec"),
            "manager": metadata.get("KeyManager"),
        }
        check(
            "kms_key_identity",
            bool(key_arn and metadata.get("KeyState") == "Enabled"
                 and metadata.get("KeyUsage") == "ENCRYPT_DECRYPT"
                 and metadata.get("KeySpec") == "SYMMETRIC_DEFAULT"
                 and metadata.get("KeyManager") == "CUSTOMER"),
            "configured key must resolve to an enabled customer-managed symmetric encryption key",
        )
    except Exception:
        check("kms_key_identity", False, "configured KMS key could not be inspected")

    kms_policy = None
    try:
        raw = kms_client.get_key_policy(KeyId=key_arn or key_id, PolicyName="default").get("Policy")
        kms_policy = _policy_document(raw)
        statements = _statements(kms_policy)
        broad = any(
            str(item.get("Effect", "")).lower() == "allow" and _wildcard_principal(item.get("Principal"))
            for item in statements
        )
        check("kms_key_policy_readable", kms_policy is not None, "KMS key policy was read and parsed")
        check(
            "kms_key_policy_no_wildcard_allow",
            not broad,
            "no wildcard-principal Allow statement was found; validate all grants and conditions independently",
        )
    except Exception:
        check("kms_key_policy_readable", False, "KMS key policy is absent or could not be read")
        check("kms_key_policy_no_wildcard_allow", False, "KMS key policy could not be inspected")

    grants: list[dict[str, Any]] = []
    try:
        marker = None
        while True:
            args = {"KeyId": key_arn or key_id, "Limit": 100}
            if marker:
                args["Marker"] = marker
            result = kms_client.list_grants(**args)
            for grant in result.get("Grants", []):
                grants.append({
                    "grantee_principal": grant.get("GranteePrincipal"),
                    "operations": sorted(_items(grant.get("Operations"))),
                    "retiring_principal": grant.get("RetiringPrincipal"),
                })
            if not result.get("NextMarker"):
                break
            marker = result["NextMarker"]
        check("kms_grants_readable", True, "KMS grants were enumerated")
    except Exception:
        check("kms_grants_readable", False, "KMS grants could not be enumerated")

    role_name = _assumed_role_name(caller.get("arn"))
    role_evidence: dict[str, Any] = {"role_name": role_name}
    if role_name:
        try:
            role = iam_client.get_role(RoleName=role_name).get("Role", {})
            attached = _list_all(
                iam_client, "list_attached_role_policies",
                RoleName=role_name, result_key="AttachedPolicies",
            )
            inline = _list_all(
                iam_client, "list_role_policies",
                RoleName=role_name, result_key="PolicyNames",
            )
            attached_evidence = [
                _managed_policy_evidence(iam_client, item["PolicyArn"])
                for item in attached if isinstance(item.get("PolicyArn"), str)
            ]
            inline_evidence = []
            for name in inline:
                # IAM ListRolePolicies returns policy names as strings, unlike
                # ListAttachedRolePolicies which returns objects.
                if not isinstance(name, str):
                    continue
                document = iam_client.get_role_policy(RoleName=role_name, PolicyName=name).get("PolicyDocument")
                inline_evidence.append({"name": name, **_policy_summary(document)})
            trust_evidence = _policy_summary(role.get("AssumeRolePolicyDocument"))
            boundary_arn = (
                role.get("PermissionsBoundary", {}).get("PermissionsBoundaryArn")
                if isinstance(role.get("PermissionsBoundary"), dict) else None
            )
            boundary_evidence = (
                _managed_policy_evidence(iam_client, boundary_arn) if boundary_arn else None
            )
            role_evidence.update({
                "role_arn": role.get("Arn"),
                "trust_policy": trust_evidence,
                "permissions_boundary": boundary_evidence,
                "attached_policies": sorted(attached_evidence, key=lambda item: item["arn"]),
                "inline_policies": sorted(inline_evidence, key=lambda item: item["name"]),
            })
            check(
                "caller_role_inventory",
                bool(role.get("Arn") and all(item["sha256"] for item in attached_evidence + inline_evidence)
                     and trust_evidence["sha256"]),
                "current assumed role, trust policy, managed policy documents, inline policy documents, and boundary were inventoried",
            )
        except Exception:
            check("caller_role_inventory", False, "current assumed role policies could not be inventoried")
    else:
        check("caller_role_inventory", False, "current caller is not an identifiable assumed IAM role")

    key_account = key_arn.split(":")[4] if isinstance(key_arn, str) and key_arn.startswith("arn:") else None
    check(
        "caller_key_account_match",
        bool(caller.get("account") and key_account and caller.get("account") == key_account),
        "current caller account must match the configured KMS key account; cross-account use requires separate review",
    )

    return {
        "production_ready": False,
        "bucket": bucket,
        "caller": caller,
        "caller_role": role_evidence,
        "kms_key": key_metadata,
        "bucket_policy_sha256": _policy_fingerprint(bucket_policy),
        "bucket_policy_statement_count": len(_statements(bucket_policy)),
        "kms_key_policy_sha256": _policy_fingerprint(kms_policy),
        "kms_key_policy_statement_count": len(_statements(kms_policy)),
        "kms_grants": grants,
        "checks": checks,
        "failed_checks": [item["name"] for item in checks if not item["passed"]],
        "manual_review_required": [
            "run under and compare each application, backup, recovery, and purge workload identity; this report describes only the current caller",
            "inspect bucket policy, account-level controls, access-point policies, SCPs, permission boundaries, session policies, and effective permissions",
            "verify application runtime cannot physically delete; verify purge role is least privilege and separately authorized",
            "verify KMS grants, key rotation, key administrators, recovery principals, and key-retention dependencies",
            "resolve versioning/recovery versus physical-purge architecture and run witnessed staging drills",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit sanitized JSON evidence")
    args = parser.parse_args()
    bucket = os.environ.get("COPILOT_S3_BUCKET", "").strip()
    region = os.environ.get("COPILOT_S3_REGION", "").strip()
    key_id = os.environ.get("COPILOT_S3_KMS_KEY_ID", "").strip()
    if not bucket or not region or not key_id:
        parser.error("COPILOT_S3_BUCKET, COPILOT_S3_REGION, and COPILOT_S3_KMS_KEY_ID are required")
    try:
        import boto3
        result = collect_live_evidence(
            boto3.client("s3", region_name=region),
            boto3.client("kms", region_name=region),
            boto3.client("sts"),
            boto3.client("iam"),
            bucket=bucket,
            key_id=key_id,
        )
    except ImportError:
        print("AWS SDK is not installed", file=sys.stderr)
        return 2
    except Exception:
        print("AWS live evidence collection failed; no configuration was changed", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"Read-only S3/KMS/IAM evidence for bucket {bucket}")
        print(f"Caller ARN: {result['caller'].get('arn') or 'unknown'}")
        for item in result["checks"]:
            print(f"- {'PASS' if item['passed'] else 'FAIL'} {item['name']}: {item['detail']}")
        print("Production ready: NO")
        print("Manual review is mandatory; the report describes only the current caller role.")
    return 0 if not result["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
