"""Tests for exact-version encrypted S3 recovery archive transport."""
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from database_backup import DatabaseBundleError
from database_backup_archive import (
    download_encrypted_bundle_version,
    upload_encrypted_bundle,
)


class FakeBody(io.BytesIO):
    pass


class FakeS3:
    def __init__(self):
        self.objects = {}
        self.read_versions = []
        self.versioning = "Enabled"
        self.version_id = "archive-version-0001"
        self.force_wrong_get_version = False

    def get_bucket_versioning(self, **kwargs):
        return {"Status": self.versioning} if self.versioning else {}

    def put_object(self, **kwargs):
        data = kwargs["Body"].read()
        self.objects[(kwargs["Bucket"], kwargs["Key"], self.version_id)] = {
            "data": data, "metadata": kwargs["Metadata"],
            "kms": kwargs["SSEKMSKeyId"], "encryption": kwargs["ServerSideEncryption"],
        }
        return {"VersionId": self.version_id}

    def head_object(self, **kwargs):
        item = self.objects[(kwargs["Bucket"], kwargs["Key"], kwargs["VersionId"])]
        return {
            "VersionId": kwargs["VersionId"], "ServerSideEncryption": item["encryption"],
            "SSEKMSKeyId": item["kms"], "ContentLength": len(item["data"]),
            "Metadata": item["metadata"],
        }

    def get_object(self, **kwargs):
        self.read_versions.append(kwargs["VersionId"])
        version = "wrong-version" if self.force_wrong_get_version else kwargs["VersionId"]
        item = self.objects[(kwargs["Bucket"], kwargs["Key"], kwargs["VersionId"])]
        return {"VersionId": version, "Body": FakeBody(item["data"])}


class FakeKMS:
    def describe_key(self, **kwargs):
        return {"KeyMetadata": {
            "Arn": "arn:aws:kms:eu-west-1:123456789012:key/recovery-key",
            "KeyState": "Enabled", "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT", "KeyManager": "CUSTOMER",
        }}


class RecoveryArchiveTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bundle = self.root / "backup.dbundle.enc"
        self.bundle.write_bytes(b"opaque-application-encrypted-backup-bytes")
        self.s3 = FakeS3()
        self.kms = FakeKMS()
        self.config = {
            "bucket": "separate-recovery-archive",
            "kms_key_id": "alias/recovery-key",
        }

    def tearDown(self):
        self.temp.cleanup()

    def upload(self):
        return upload_encrypted_bundle(
            self.s3, self.kms, self.bundle, **self.config
        )

    def test_upload_records_exact_version_checksum_size_and_kms(self):
        locator = self.upload()
        self.assertEqual(locator["version_id"], self.s3.version_id)
        self.assertEqual(locator["sha256"], hashlib.sha256(self.bundle.read_bytes()).hexdigest())
        self.assertEqual(locator["size_bytes"], self.bundle.stat().st_size)
        self.assertEqual(locator["kms_key_arn"], self.kms.describe_key(KeyId="x")["KeyMetadata"]["Arn"])

    def test_download_reads_exact_version_and_verifies_bytes(self):
        locator = self.upload()
        target = self.root / "downloaded.dbundle.enc"
        result = download_encrypted_bundle_version(
            self.s3, self.kms, locator, target, **self.config
        )
        self.assertEqual(result.read_bytes(), self.bundle.read_bytes())
        self.assertEqual(self.s3.read_versions, [locator["version_id"]])

    def test_missing_versioning_fails_closed(self):
        self.s3.versioning = "Suspended"
        with self.assertRaises(DatabaseBundleError):
            self.upload()

    def test_wrong_version_returned_by_get_is_rejected(self):
        locator = self.upload()
        self.s3.force_wrong_get_version = True
        with self.assertRaises(DatabaseBundleError):
            download_encrypted_bundle_version(
                self.s3, self.kms, locator, self.root / "wrong.dbundle.enc", **self.config
            )

    def test_manifest_checksum_tampering_is_rejected(self):
        locator = self.upload()
        locator["sha256"] = "0" * 64
        with self.assertRaises(DatabaseBundleError):
            download_encrypted_bundle_version(
                self.s3, self.kms, locator, self.root / "tampered.dbundle.enc", **self.config
            )

    def test_existing_destination_is_never_overwritten(self):
        locator = self.upload()
        target = self.root / "existing.dbundle.enc"
        target.write_bytes(b"preserve-me")
        with self.assertRaises(DatabaseBundleError):
            download_encrypted_bundle_version(
                self.s3, self.kms, locator, target, **self.config
            )
        self.assertEqual(target.read_bytes(), b"preserve-me")


if __name__ == "__main__":
    unittest.main()
