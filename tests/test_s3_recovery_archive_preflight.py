import unittest

from tools.validate_s3_recovery_archive import validate_recovery_archive_configuration


class FakeS3:
    def __init__(self, versioning="Enabled", bucket="recovery-archive"):
        self.versioning = versioning
        self.bucket = bucket

    def head_bucket(self, **kwargs):
        return {}

    def get_public_access_block(self, **kwargs):
        return {"PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True, "IgnorePublicAcls": True,
            "BlockPublicPolicy": True, "RestrictPublicBuckets": True,
        }}

    def get_bucket_ownership_controls(self, **kwargs):
        return {"OwnershipControls": {"Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]}}

    def get_bucket_versioning(self, **kwargs):
        return {"Status": self.versioning} if self.versioning else {}

    def get_bucket_encryption(self, **kwargs):
        return {"ServerSideEncryptionConfiguration": {"Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "alias/recovery-archive"
            }
        }]}}


class FakeKMS:
    def describe_key(self, **kwargs):
        key_id = kwargs.get("KeyId")
        arn = (
            "arn:aws:kms:eu-central-1:123456789012:key/wrong"
            if key_id == "alias/wrong"
            else "arn:aws:kms:eu-central-1:123456789012:key/originals"
            if key_id == "alias/originals"
            else "arn:aws:kms:eu-central-1:123456789012:key/recovery"
        )
        return {"KeyMetadata": {
            "Arn": arn, "KeyState": "Enabled", "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT", "KeyManager": "CUSTOMER",
        }}


class RecoveryArchivePreflightTests(unittest.TestCase):
    def test_accepts_separate_versioned_encrypted_archive_but_never_claims_production_ready(self):
        result = validate_recovery_archive_configuration(
            FakeS3(), FakeKMS(), bucket="recovery-archive",
            configured_key="alias/recovery-archive", original_bucket="original-objects", original_key="alias/originals",
        )
        self.assertEqual(result["failed_checks"], [])
        self.assertFalse(result["production_ready"])
        self.assertTrue(next(x["passed"] for x in result["checks"] if x["name"] == "recovery_versioning_enabled"))

    def test_rejects_same_bucket_for_originals_and_recovery_archive(self):
        result = validate_recovery_archive_configuration(
            FakeS3(), FakeKMS(), bucket="original-objects",
            configured_key="alias/recovery-archive", original_bucket="original-objects", original_key="alias/originals",
        )
        self.assertIn("separate_recovery_bucket", result["failed_checks"])

    def test_rejects_suspended_or_missing_recovery_versioning(self):
        for status in ("Suspended", None):
            with self.subTest(status=status):
                result = validate_recovery_archive_configuration(
                    FakeS3(versioning=status), FakeKMS(), bucket="recovery-archive",
                    configured_key="alias/recovery-archive", original_bucket="original-objects", original_key="alias/originals",
                )
                self.assertIn("recovery_versioning_enabled", result["failed_checks"])

    def test_rejects_default_encryption_with_different_kms_key(self):
        class WrongKeyS3(FakeS3):
            def get_bucket_encryption(self, **kwargs):
                return {"ServerSideEncryptionConfiguration": {"Rules": [{
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "alias/wrong"
                    }
                }]}}

        result = validate_recovery_archive_configuration(
            WrongKeyS3(), FakeKMS(), bucket="recovery-archive",
            configured_key="alias/recovery-archive", original_bucket="original-objects", original_key="alias/originals",
        )
        self.assertIn("recovery_default_sse_kms", result["failed_checks"])

    def test_live_acceptance_remains_explicit_after_transport_implementation(self):
        result = validate_recovery_archive_configuration(
            FakeS3(), FakeKMS(), bucket="recovery-archive",
            configured_key="alias/recovery-archive", original_bucket="original-objects",
            original_key="alias/originals",
        )
        self.assertIn(
            "run live staging upload, exact-VersionId download, bundle verification, and isolated restore with protected locator evidence",
            result["manual_review_required"],
        )
        self.assertFalse(result["production_ready"])

    def test_rejects_reusing_original_kms_key_for_recovery_archive(self):
        result = validate_recovery_archive_configuration(
            FakeS3(), FakeKMS(), bucket="recovery-archive",
            configured_key="alias/originals", original_bucket="original-objects",
            original_key="alias/originals",
        )
        self.assertIn("separate_recovery_kms_key", result["failed_checks"])


if __name__ == "__main__":
    unittest.main()
