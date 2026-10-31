"""Collect sanitized, read-only AWS evidence for original-file S3 acceptance.

This collector never changes AWS resources and never authorizes production purge.
It emits identifiers and policy findings, not policy documents, credentials, or secrets.
"""
from __future__ import annotations

import json
import re
from typing import Any


def _policy_document(raw: Any) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            value = json.loads(raw)
            return value if isinstance(value, dict) else {}
        except (TypeError, ValueError):
            return {}
    return {}


def _statements(document: dict) -> list[dict]:
    statements = document.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]
    return [item for item in statements if isinstance(item, dict)] if isinstance(statements, list) else []


def _values(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value.lower()}
    if isinstance(value, list):
        return {item.lower() for item in value if isinstance(item, str)}
    return set()


def _role_from_caller(arn: str) -> tuple[str | None, str | None]:
    match = re.fullmatch(r"arn:([^:]+):sts::(\d{12}):assumed-role/(.+?)/[^/]+", arn)
    if not match:
        return None, None
    partition, account, role_path = match.groups()
    return account, f"arn:{partition}:iam::{account}:role/{role_path}"


def collect_live_evidence(s3_client, kms_client, sts_client, iam_client, *, bucket: str, key_id: str) -> dict:
    """Inspect caller, bucket policy, KMS key/grants and caller role without mutation."""
    checks: list[dict[str, Any]] = []
    failed: list[str] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed:
            failed.append(name)

    caller: dict[str, str] = {}
    caller_role: dict[str, Any] = {"role_name": None, "role_arn": None, "attached_policy_names": [], "inline_policy_names": []}
    key_arn: str | None = None
    grants: list[dict[str, Any]] = []

    try:
        identity = sts_client.get_caller_identity()
        account = identity.get("Account")
        arn = identity.get("Arn")
        if isinstance(account, str) and re.fullmatch(r"\d{12}", account) and isinstance(arn, str):
            caller = {"account": account, "arn": re.sub(r"/[^/]+$", "/[session]", arn)}
            role_account, role_arn = _role_from_caller(arn)
            record("caller_identity", True, "caller identity is available")
            if role_arn and role_account == account:
                caller_role["role_arn"] = role_arn
                caller_role["role_name"] = role_arn.rsplit("/", 1)[-1]
            else:
                record("caller_assumed_role", False, "caller is not an identifiable assumed role")
        else:
            record("caller_identity", False, "caller identity response is incomplete")
    except Exception:
        record("caller_identity", False, "caller identity could not be inspected")

    try:
        response = s3_client.get_bucket_policy(Bucket=bucket)
        policy = _policy_document(response.get("Policy"))
        statements = _statements(policy)
        public_allow = any(
            item.get("Effect") == "Allow"
            and (item.get("Principal") == "*" or isinstance(item.get("Principal"), dict) and "*" in _values(item["Principal"].get("AWS")))
            for item in statements
        )
        tls_deny = any(
            item.get("Effect") == "Deny"
            and "false" in _values(item.get("Condition", {}).get("Bool", {}).get("aws:SecureTransport"))
            for item in statements if isinstance(item.get("Condition"), dict)
        )
        conditional_delete = any(
            item.get("Effect") == "Deny"
            and bool(_values(item.get("Action")) & {"s3:deleteobject", "s3:*", "s3:delete*"})
            and "true" in _values(item.get("Condition", {}).get("Null", {}).get("s3:if-match"))
            for item in statements if isinstance(item.get("Condition"), dict)
        )
        record("bucket_policy_no_public_allow", not public_allow, "bucket policy has no wildcard public Allow")
        record("bucket_policy_tls_deny", tls_deny, "bucket policy denies insecure transport")
        record("bucket_policy_conditional_delete", conditional_delete, "bucket policy denies deletes without s3:if-match")
    except Exception:
        for name, detail in (
            ("bucket_policy_no_public_allow", "bucket policy could not be inspected"),
            ("bucket_policy_tls_deny", "TLS-deny policy could not be verified"),
            ("bucket_policy_conditional_delete", "conditional-delete policy could not be verified"),
        ):
            record(name, False, detail)

    try:
        response = kms_client.describe_key(KeyId=key_id)
        metadata = response.get("KeyMetadata", {})
        key_arn = metadata.get("Arn") if isinstance(metadata, dict) else None
        key_ok = (
            isinstance(key_arn, str)
            and metadata.get("KeyState") == "Enabled"
            and metadata.get("KeyUsage") == "ENCRYPT_DECRYPT"
            and metadata.get("KeySpec") == "SYMMETRIC_DEFAULT"
            and metadata.get("KeyManager") == "CUSTOMER"
        )
        record("kms_key_enabled_customer_managed", key_ok, "KMS key must be enabled, customer-managed, symmetric, and usable for encryption")
    except Exception:
        record("kms_key_enabled_customer_managed", False, "configured KMS key could not be inspected")

    if caller.get("account") and key_arn:
        key_account = key_arn.split(":")[4] if key_arn.startswith("arn:") and len(key_arn.split(":")) > 4 else None
        record("caller_key_account_match", key_account == caller["account"], "caller and KMS key must belong to the same AWS account")
    else:
        record("caller_key_account_match", False, "caller account or KMS key ARN is unavailable")

    try:
        policy_response = kms_client.get_key_policy(KeyId=key_id, PolicyName="default")
        key_policy = _policy_document(policy_response.get("Policy"))
        record("kms_key_policy_readable", bool(_statements(key_policy)), "KMS key policy is readable")
    except Exception:
        record("kms_key_policy_readable", False, "KMS key policy could not be inspected")

    try:
        grant_response = kms_client.list_grants(KeyId=key_id)
        for grant in grant_response.get("Grants", []):
            if isinstance(grant, dict):
                grants.append({
                    "grantee_principal": grant.get("GranteePrincipal"),
                    "operations": sorted(_values(grant.get("Operations"))),
                })
        record("kms_grants_readable", True, "KMS grants were enumerated")
    except Exception:
        record("kms_grants_readable", False, "KMS grants could not be inspected")

    role_arn = caller_role.get("role_arn")
    if role_arn:
        try:
            role = iam_client.get_role(RoleName=caller_role["role_name"]).get("Role", {})
            caller_role["role_name"] = role.get("RoleName") or caller_role["role_name"]
            caller_role["role_arn"] = role.get("Arn") or role_arn
            attached = iam_client.list_attached_role_policies(RoleName=caller_role["role_name"])
            inline = iam_client.list_role_policies(RoleName=caller_role["role_name"])
            caller_role["attached_policy_names"] = sorted(
                item.get("PolicyArn", "").rsplit("/", 1)[-1]
                for item in attached.get("AttachedPolicies", []) if isinstance(item, dict)
            )
            caller_role["inline_policy_names"] = sorted(
                name for name in inline.get("PolicyNames", []) if isinstance(name, str)
            )
            record("caller_role_inspected", True, "caller IAM role and policy names were inspected")
        except Exception:
            record("caller_role_inspected", False, "caller IAM role policies could not be inspected")
    else:
        record("caller_role_inspected", False, "caller role could not be derived from the STS identity")

    return {
        "bucket": bucket,
        "configured_kms_key": key_id,
        "kms_key_arn": key_arn,
        "caller": caller,
        "caller_role": caller_role,
        "kms_grants": grants,
        "checks": checks,
        "failed_checks": sorted(set(failed)),
        "production_ready": False,
        "manual_review_required": [
            "independent review of effective IAM and bucket policies, including inherited organization controls",
            "verify upload/finalize worker quiescence and enforce the no-writer window with IAM/bucket policy",
            "verify object encryption metadata, bucket ownership, public-access block, logging, and versioning architecture",
            "perform witnessed restore, rollback, staged-upload recovery, and synthetic deletion-recovery drills",
            "obtain approved retention/export/deletion/legal-hold policy and independent security sign-off",
        ],
    }
