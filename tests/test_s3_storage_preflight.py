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
                "SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "arn:aws:kms:eu-west-1:123456789012:key/abc"
            }
        }]}}


class FakeKMS:
    def describe_key(self, **kwargs):
        return {"KeyMetadata": {
            "Arn": "arn:aws:kms:eu-west-1:123456789012:key/abc",
            "KeyState": "Enabled", "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT", "KeyManager": "CUSTOMER",
        }}


class S3StoragePreflightTests(unittest.TestCase):
    def test_passes_required_bucket_and_kms_controls_but_never_claims_production_ready(self):
        result = validate_s3_configuration(
            FakeS3(), FakeKMS(), bucket="private-originals", configured_key="alias/legal-originals"
        )
        self.assertEqual(result["failed_checks"], [])
        self.assertFalse(result["production_ready"])
        self.assertTrue(result["manual_review_required"])
        self.assertTrue(all(check["passed"] for check in result["checks"]))

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
        self.assertIn("versioning", result["failed_checks"])
        self.assertFalse(result["production_ready"])


if __name__ == "__main__":
    unittest.main()
