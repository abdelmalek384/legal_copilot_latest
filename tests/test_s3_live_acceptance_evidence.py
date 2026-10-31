import io
import json
import os
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from tools.collect_s3_live_acceptance_evidence import collect_live_evidence


class FakeS3:
    def get_bucket_policy(self, **kwargs):
        return {"Policy": '{"Version":"2012-10-17","Statement":['
            '{"Effect":"Deny","Principal":"*","Action":"s3:*","Resource":"*","Condition":{"Bool":{"aws:SecureTransport":"false"}}},'
            '{"Effect":"Deny","Principal":"*","Action":"s3:DeleteObject","Resource":"*","Condition":{"Null":{"s3:if-match":"true"}}}'
            ']}'}


class FakeKMS:
    def describe_key(self, **kwargs):
        return {"KeyMetadata": {
            "Arn": "arn:aws:kms:eu-central-1:123456789012:key/test-key",
            "KeyState": "Enabled", "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT", "KeyManager": "CUSTOMER",
        }}

    def get_key_policy(self, **kwargs):
        return {"Policy": '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":"arn:aws:iam::123456789012:root"},"Action":"kms:*","Resource":"*"}]}'}

    def list_grants(self, **kwargs):
        return {"Grants": [{"GranteePrincipal": "arn:aws:iam::123456789012:role/legal-runtime",
                            "Operations": ["Encrypt", "Decrypt"]}]}


class FakeSTS:
    def get_caller_identity(self):
        return {"Account": "123456789012",
                "Arn": "arn:aws:sts::123456789012:assumed-role/legal-runtime/session",
                "UserId": "AROAX:session"}


class FakeIAM:
    def get_role(self, **kwargs):
        return {"Role": {"Arn": "arn:aws:iam::123456789012:role/legal-runtime"}}

    def list_attached_role_policies(self, **kwargs):
        return {"AttachedPolicies": [{"PolicyArn": "arn:aws:iam::aws:policy/ReadOnlyAccess"}]}

    def list_role_policies(self, **kwargs):
        return {"PolicyNames": ["runtime-inline"]}


class S3LiveEvidenceTests(unittest.TestCase):
    def test_collects_sanitized_caller_bucket_kms_and_role_evidence(self):
        report = collect_live_evidence(
            FakeS3(), FakeKMS(), FakeSTS(), FakeIAM(),
            bucket="private-originals", key_id="alias/legal-originals",
        )
        self.assertFalse(report["production_ready"])
        self.assertEqual(report["caller"]["account"], "123456789012")
        self.assertEqual(report["caller_role"]["role_name"], "legal-runtime")
        self.assertEqual(report["caller_role"]["inline_policy_names"], ["runtime-inline"])
        self.assertEqual(len(report["kms_grants"]), 1)
        self.assertEqual(report["failed_checks"], [])

    def test_public_bucket_policy_allow_fails_closed(self):
        class PublicS3(FakeS3):
            def get_bucket_policy(self, **kwargs):
                return {"Policy": '{"Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"*"}]}'}

        report = collect_live_evidence(
            PublicS3(), FakeKMS(), FakeSTS(), FakeIAM(),
            bucket="private-originals", key_id="alias/legal-originals",
        )
        self.assertIn("bucket_policy_no_public_allow", report["failed_checks"])
        self.assertIn("bucket_policy_tls_deny", report["failed_checks"])
        self.assertIn("bucket_policy_conditional_delete", report["failed_checks"])

    def test_caller_and_key_account_mismatch_fails(self):
        class OtherAccountSTS(FakeSTS):
            def get_caller_identity(self):
                return {"Account": "999999999999",
                        "Arn": "arn:aws:sts::999999999999:assumed-role/legal-runtime/session",
                        "UserId": "AROAX:session"}

        report = collect_live_evidence(
            FakeS3(), FakeKMS(), OtherAccountSTS(), FakeIAM(),
            bucket="private-originals", key_id="alias/legal-originals",
        )
        self.assertIn("caller_key_account_match", report["failed_checks"])



    def test_cli_requires_explicit_storage_target_configuration(self):
        from tools.collect_s3_live_acceptance_evidence import main

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as error:
                main(["--json"])
        self.assertEqual(error.exception.code, 2)

    def test_cli_emits_sanitized_json_and_never_claims_production_ready(self):
        from tools.collect_s3_live_acceptance_evidence import main

        fake_boto3 = SimpleNamespace(client=lambda service, **kwargs: {
            "s3": FakeS3(), "kms": FakeKMS(), "sts": FakeSTS(), "iam": FakeIAM()
        }[service])
        output = io.StringIO()
        environment = {
            "COPILOT_S3_BUCKET": "private-originals",
            "COPILOT_S3_REGION": "eu-central-1",
            "COPILOT_S3_KMS_KEY_ID": "alias/legal-originals",
            "COPILOT_S3_ENDPOINT_URL": "",
            "AWS_SECRET_ACCESS_KEY": "never-print-this-secret",
        }
        with patch.dict(os.environ, environment, clear=True), patch.dict("sys.modules", {"boto3": fake_boto3}):
            with redirect_stdout(output):
                result = main(["--json"])
        rendered = output.getvalue()
        report = json.loads(rendered)
        self.assertEqual(result, 0)
        self.assertFalse(report["production_ready"])
        self.assertNotIn("never-print-this-secret", rendered)
        self.assertNotIn("Version", rendered)


if __name__ == "__main__":
    unittest.main()
