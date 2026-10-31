import unittest

from tools.validate_s3_original_file_storage import validate_s3_configuration


class FakeS3:
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
        return {"Status": "Enabled"}

    def get_bucket_encryption(self, **kwargs):
        return {"ServerSideEncryptionConfiguration": {"Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "alias/legal-originals"
            }
        }]}}


class FakeKMS:
    def __init__(self):
        self.lookups = []

    def describe_key(self, **kwargs):
        key_id = kwargs.get("KeyId")
        self.lookups.append(key_id)
        arn = (
            "arn:aws:kms:eu-west-1:123456789012:key/other"
            if key_id == "alias/other"
            else "arn:aws:kms:eu-west-1:123456789012:key/abc"
        )
        return {"KeyMetadata": {
            "Arn": arn, "KeyId": "abc" if arn.endswith("/abc") else "other",
            "KeyState": "Enabled", "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT", "KeyManager": "CUSTOMER",
        }}


class S3StoragePreflightTests(unittest.TestCase):
    def test_passes_required_bucket_and_kms_controls_but_never_claims_production_ready(self):
        result = validate_s3_configuration(
            FakeS3(), FakeKMS(), bucket="private-originals", configured_key="alias/legal-originals"
        )
        self.assertEqual(result["bucket_versioning_status"], "Enabled")
        self.assertEqual(result["failed_checks"], ["original_bucket_never_versioned"])
        self.assertFalse(result["production_ready"])
        self.assertTrue(result["manual_review_required"])
        self.assertFalse(next(item["passed"] for item in result["checks"] if item["name"] == "original_bucket_never_versioned"))

    def test_never_versioned_original_bucket_passes_its_versioning_gate(self):
        class NeverVersionedS3(FakeS3):
            def get_bucket_versioning(self, **kwargs):
                return {}

        result = validate_s3_configuration(
            NeverVersionedS3(), FakeKMS(), bucket="private-originals", configured_key="alias/legal-originals"
        )
        self.assertIsNone(result["bucket_versioning_status"])
        self.assertNotIn("original_bucket_never_versioned", result["failed_checks"])
        self.assertFalse(result["production_ready"])

    def test_resolves_bucket_default_encryption_alias_to_canonical_key_arn(self):
        kms = FakeKMS()
        result = validate_s3_configuration(
            FakeS3(), kms, bucket="private-originals", configured_key="alias/legal-originals"
        )
        self.assertNotIn("default_sse_kms", result["failed_checks"])
        self.assertIn("alias/legal-originals", kms.lookups)
        self.assertTrue(next(
            item["passed"] for item in result["checks"] if item["name"] == "default_sse_kms"
        ))

    def test_rejects_bucket_default_encryption_using_a_different_kms_key(self):
        class WrongKeyS3(FakeS3):
            def get_bucket_encryption(self, **kwargs):
                return {"ServerSideEncryptionConfiguration": {"Rules": [{
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "alias/other"
                    }
                }]}}

        result = validate_s3_configuration(
            WrongKeyS3(), FakeKMS(), bucket="private-originals", configured_key="alias/legal-originals"
        )
        self.assertIn("default_sse_kms", result["failed_checks"])

    def test_missing_public_access_and_versioning_controls_fail(self):
        class UnsafeS3(FakeS3):
            def get_public_access_block(self, **kwargs):
                return {"PublicAccessBlockConfiguration": {"BlockPublicAcls": True}}

            def get_bucket_versioning(self, **kwargs):
                return {"Status": "Suspended"}

        result = validate_s3_configuration(
            UnsafeS3(), FakeKMS(), bucket="private-originals", configured_key="alias/legal-originals"
        )
        self.assertIn("public_access_block", result["failed_checks"])
        self.assertIn("original_bucket_never_versioned", result["failed_checks"])
        self.assertFalse(result["production_ready"])


if __name__ == "__main__":
    unittest.main()
