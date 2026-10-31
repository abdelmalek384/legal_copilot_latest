import unittest

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
        return {"Role": {
            "Arn": "arn:aws:iam::123456789012:role/legal-runtime",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Principal": {"Service": "ecs-tasks.amazonaws.com"}, "Action": "sts:AssumeRole"}],
            },
        }}

    def list_attached_role_policies(self, **kwargs):
        return {"AttachedPolicies": [{"PolicyArn": "arn:aws:iam::aws:policy/ReadOnlyAccess"}]}

    def list_role_policies(self, **kwargs):
        return {"PolicyNames": ["runtime-inline"]}

    def get_policy(self, **kwargs):
        return {"Policy": {"DefaultVersionId": "v1"}}

    def get_policy_version(self, **kwargs):
        return {"PolicyVersion": {"Document": {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": ["s3:GetObject"], "Resource": "arn:aws:s3:::private-originals/*"}],
        }}}

    def get_role_policy(self, **kwargs):
        return {"PolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": ["kms:Decrypt"], "Resource": "arn:aws:kms:eu-central-1:123456789012:key/test-key"}],
        }}


class S3LiveEvidenceTests(unittest.TestCase):
    def test_collects_sanitized_caller_bucket_kms_and_role_evidence(self):
        report = collect_live_evidence(
            FakeS3(), FakeKMS(), FakeSTS(), FakeIAM(),
            bucket="private-originals", key_id="alias/legal-originals",
        )
        self.assertFalse(report["production_ready"])
        self.assertEqual(report["caller"]["account"], "123456789012")
        self.assertEqual(report["caller_role"]["role_name"], "legal-runtime")
        self.assertEqual(report["caller_role"]["inline_policies"][0]["name"], "runtime-inline")
        self.assertEqual(report["caller_role"]["attached_policies"][0]["default_version_id"], "v1")
        self.assertEqual(report["caller_role"]["trust_policy"]["statement_count"], 1)
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


if __name__ == "__main__":
    unittest.main()
