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
        self.multipart_uploads = {}
        self.multipart_completed = False
        self.multipart_aborted = False
        self.fail_upload_part = False

    def get_bucket_versioning(self, **kwargs):
        return {"Status": self.versioning} if self.versioning else {}

    def put_object(self, **kwargs):
        data = kwargs["Body"].read()
        self.objects[(kwargs["Bucket"], kwargs["Key"], self.version_id)] = {
            "data": data, "metadata": kwargs["Metadata"],
            "kms": kwargs["SSEKMSKeyId"], "encryption": kwargs["ServerSideEncryption"],
        }
        return {"VersionId": self.version_id}

    def create_multipart_upload(self, **kwargs):
        upload_id = "multipart-upload-1"
        self.multipart_uploads[(kwargs["Bucket"], kwargs["Key"], upload_id)] = {
            "parts": {}, "metadata": kwargs["Metadata"],
            "kms": kwargs["SSEKMSKeyId"], "encryption": kwargs["ServerSideEncryption"],
        }
        return {"UploadId": upload_id}

    def upload_part(self, **kwargs):
        if self.fail_upload_part:
            raise RuntimeError("injected multipart part failure")
        item = self.multipart_uploads[(kwargs["Bucket"], kwargs["Key"], kwargs["UploadId"])]
        item["parts"][kwargs["PartNumber"]] = kwargs["Body"]
        return {"ETag": '"part-etag"'}

    def complete_multipart_upload(self, **kwargs):
        upload_id = kwargs["UploadId"]
        item = self.multipart_uploads[(kwargs["Bucket"], kwargs["Key"], upload_id)]
        data = b"".join(item["parts"][number] for number in sorted(item["parts"]))
        self.objects[(kwargs["Bucket"], kwargs["Key"], self.version_id)] = {
            "data": data, "metadata": item["metadata"],
            "kms": item["kms"], "encryption": item["encryption"],
        }
        self.multipart_completed = True
        return {"VersionId": self.version_id}

    def abort_multipart_upload(self, **kwargs):
        self.multipart_aborted = True
        self.multipart_uploads.pop((kwargs["Bucket"], kwargs["Key"], kwargs["UploadId"]), None)
        return {}

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

    def test_large_bundle_uses_multipart_upload(self):
        from unittest.mock import patch

        with patch("database_backup_archive._SINGLE_PUT_MAX_BYTES", 1):
            locator = self.upload()
        self.assertEqual(locator["version_id"], self.s3.version_id)
        self.assertTrue(self.s3.multipart_completed)
        self.assertFalse(self.s3.multipart_aborted)

    def test_multipart_failure_aborts_incomplete_upload(self):
        from unittest.mock import patch

        self.s3.fail_upload_part = True
        with patch("database_backup_archive._SINGLE_PUT_MAX_BYTES", 1):
            with self.assertRaises(DatabaseBundleError):
                self.upload()
        self.assertTrue(self.s3.multipart_aborted)
        self.assertEqual(self.s3.multipart_uploads, {})

    def test_download_reads_exact_version_and_verifies_bytes(self):
        locator = self.upload()
        target = self.root / "downloaded.dbundle.enc"
        result = download_encrypted_bundle_version(
            self.s3, self.kms, locator, target, **self.config
        )
        self.assertEqual(result.read_bytes(), self.bundle.read_bytes())
        self.assertEqual(self.s3.read_versions, [locator["version_id"], locator["version_id"]])

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

    def test_object_bytes_changed_after_upload_are_rejected(self):
        locator = self.upload()
        item = self.s3.objects[(locator["bucket"], locator["key"], locator["version_id"])]
        item["data"] = item["data"] + b"tampered"
        with self.assertRaises(DatabaseBundleError):
            download_encrypted_bundle_version(
                self.s3, self.kms, locator, self.root / "corrupt.dbundle.enc", **self.config
            )
        self.assertFalse((self.root / "corrupt.dbundle.enc").exists())

    def test_wrong_kms_key_on_exact_version_is_rejected(self):
        locator = self.upload()
        item = self.s3.objects[(locator["bucket"], locator["key"], locator["version_id"])]
        item["kms"] = "arn:aws:kms:eu-west-1:123456789012:key/other-key"
        with self.assertRaises(DatabaseBundleError):
            download_encrypted_bundle_version(
                self.s3, self.kms, locator, self.root / "wrong-key.dbundle.enc", **self.config
            )

    def test_archive_upload_cli_verifies_bundle_before_creating_aws_clients(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        import manage

        args = SimpleNamespace(file=str(self.bundle))
        with (
            patch.object(manage, "_backup_fernet", return_value=object()),
            patch.object(manage, "verify_backup_bundle", return_value={"verified": True}) as verify,
            patch.object(manage, "_recovery_archive_clients", return_value=(self.s3, self.kms, self.config["bucket"], self.config["kms_key_id"])) as clients,
            patch.object(manage, "upload_encrypted_bundle", return_value={"version_id": "v1"}) as upload,
            patch("builtins.print"),
        ):
            manage.archive_upload_tenancy(args)
        verify.assert_called_once()
        clients.assert_called_once()
        upload.assert_called_once()

    def test_archive_upload_cli_refuses_unverified_bundle_before_aws_access(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        import manage

        args = SimpleNamespace(file=str(self.bundle))
        with (
            patch.object(manage, "_backup_fernet", return_value=object()),
            patch.object(manage, "verify_backup_bundle", return_value={"verified": False}),
            patch.object(manage, "_recovery_archive_clients") as clients,
        ):
            with self.assertRaises(SystemExit):
                manage.archive_upload_tenancy(args)
        clients.assert_not_called()

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
