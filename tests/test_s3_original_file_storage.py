import hashlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path

from original_file_storage import ObjectStorageError
from s3_original_file_storage import S3PrivateObjectStore
from original_file_reconciliation import TenantDatabase
from original_file_s3_reconciliation import reconcile_s3_original_file_storage
from database_backup import _copy_s3_original_objects, _scan_s3_original_object_inventory


class FakeS3Error(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.response = {"Error": {"Code": code}, "ResponseMetadata": {"HTTPStatusCode": 404 if code == "NoSuchKey" else 500}}


class FakeS3Client:
    def __init__(self):
        self.objects = {}
        self.calls = []

    def _read(self, bucket, key):
        try:
            return self.objects[(bucket, key)]
        except KeyError as exc:
            raise FakeS3Error("NoSuchKey") from exc

    def put_object(self, **kwargs):
        self.calls.append(("put_object", kwargs.copy()))
        key = (kwargs["Bucket"], kwargs["Key"])
        if kwargs.get("IfNoneMatch") == "*" and key in self.objects:
            raise RuntimeError("conditional create failed")
        data = kwargs["Body"]
        self.objects[key] = {
            "Body": bytes(data),
            "Metadata": dict(kwargs.get("Metadata", {})),
            "ETag": '"' + hashlib.md5(data).hexdigest() + '"',
            "ServerSideEncryption": kwargs.get("ServerSideEncryption"),
            "SSEKMSKeyId": kwargs.get("SSEKMSKeyId"),
        }
        return {}

    def head_object(self, **kwargs):
        value = self._read(kwargs["Bucket"], kwargs["Key"])
        return {
            "ETag": value["ETag"],
            "ContentLength": len(value["Body"]),
            "Metadata": value["Metadata"],
            "ServerSideEncryption": value.get("ServerSideEncryption"),
            "SSEKMSKeyId": value.get("SSEKMSKeyId"),
        }

    def copy_object(self, **kwargs):
        self.calls.append(("copy_object", kwargs.copy()))
        destination = (kwargs["Bucket"], kwargs["Key"])
        source = (kwargs["CopySource"]["Bucket"], kwargs["CopySource"]["Key"])
        if kwargs.get("IfNoneMatch") == "*" and destination in self.objects:
            raise RuntimeError("conditional copy failed")
        value = self._read(*source)
        if value["ETag"] != kwargs.get("CopySourceIfMatch"):
            raise RuntimeError("source changed")
        self.objects[destination] = {
            **value,
            "ServerSideEncryption": kwargs.get("ServerSideEncryption"),
            "SSEKMSKeyId": kwargs.get("SSEKMSKeyId"),
        }
        return {}

    def get_object(self, **kwargs):
        value = self._read(kwargs["Bucket"], kwargs["Key"])
        return {
            "Body": io.BytesIO(value["Body"]),
            "ServerSideEncryption": value.get("ServerSideEncryption"),
            "SSEKMSKeyId": value.get("SSEKMSKeyId"),
        }

    def delete_object(self, **kwargs):
        self.objects.pop((kwargs["Bucket"], kwargs["Key"]), None)
        return {}

    def list_objects_v2(self, **kwargs):
        keys = sorted(key for (bucket, key) in self.objects if bucket == kwargs["Bucket"] and key.startswith(kwargs["Prefix"]))
        return {"Contents": [{"Key": key} for key in keys], "IsTruncated": False}


class S3PrivateObjectStoreTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeS3Client()
        self.store = S3PrivateObjectStore(self.client, "private-matter-files", "alias/legal-files", max_bytes=1024)

    def test_stage_uses_firm_namespace_and_kms_encryption(self):
        payload = b"confidential original\x00bytes"
        staged = self.store.stage(12, payload)
        self.assertEqual(staged.sha256, hashlib.sha256(payload).hexdigest())
        self.assertEqual(staged.byte_size, len(payload))
        key = ("private-matter-files", f"firms/12/originals/{staged.object_id}.staged")
        value = self.client.objects[key]
        self.assertEqual(value["Body"], payload)
        self.assertEqual(value["ServerSideEncryption"], "aws:kms")
        self.assertEqual(value["SSEKMSKeyId"], "alias/legal-files")
        call = next(kwargs for name, kwargs in self.client.calls if name == "put_object")
        self.assertEqual(call["IfNoneMatch"], "*")
        self.assertEqual(call["Metadata"]["firm-id"], "12")
        self.assertEqual(self.store.object_presence(12, staged.object_id), (True, False))

    def test_stage_with_id_preserves_restored_object_id_and_refuses_overwrite(self):
        object_id = "d" * 32
        staged = self.store.stage_with_id(12, object_id, b"restored bytes")
        self.assertEqual(staged.object_id, object_id)
        with self.assertRaises(ObjectStorageError):
            self.store.stage_with_id(12, object_id, b"replacement bytes")
        self.store.finalize(12, object_id)
        with self.store.open(12, object_id) as handle:
            self.assertEqual(handle.read(), b"restored bytes")

    def test_finalize_open_and_verify(self):
        payload = b"private original bytes"
        staged = self.store.stage(12, payload)
        self.assertTrue(self.store.verify_staged(12, staged.object_id, expected_sha256=staged.sha256, expected_size=len(payload)))
        self.store.finalize(12, staged.object_id)
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, True))
        with self.store.open(12, staged.object_id) as handle:
            self.assertEqual(handle.read(), payload)
        self.assertTrue(self.store.verify(12, staged.object_id, expected_sha256=staged.sha256, expected_size=len(payload)))
        self.assertFalse(self.store.verify(12, staged.object_id, expected_sha256="0" * 64, expected_size=len(payload)))
        copy_call = next(kwargs for name, kwargs in self.client.calls if name == "copy_object")
        self.assertEqual(copy_call["ServerSideEncryption"], "aws:kms")
        self.assertEqual(copy_call["SSEKMSKeyId"], "alias/legal-files")
        self.assertEqual(copy_call["IfNoneMatch"], "*")

    def test_rejects_unencrypted_or_non_kms_objects_on_read_and_verify(self):
        staged = self.store.stage(12, b"confidential")
        self.store.finalize(12, staged.object_id)
        key = ("private-matter-files", f"firms/12/originals/{staged.object_id}.blob")
        self.client.objects[key]["ServerSideEncryption"] = "AES256"
        with self.assertRaises(ObjectStorageError):
            self.store.open(12, staged.object_id)
        self.assertFalse(self.store.verify(
            12, staged.object_id, expected_sha256=staged.sha256,
            expected_size=staged.byte_size,
        ))
        with self.assertRaises(ObjectStorageError):
            self.store.object_presence(12, staged.object_id)

    def test_firm_namespace_and_object_id_validation(self):
        staged = self.store.stage(12, b"firm twelve")
        self.store.finalize(12, staged.object_id)
        with self.assertRaises(ObjectStorageError):
            self.store.open(13, staged.object_id)
        for value in (0, -1, True, "12"):
            with self.assertRaises(ValueError):
                self.store.stage(value, b"x")
        for value in ("../escape", "A" * 32, "f" * 31):
            with self.assertRaises(ValueError):
                self.store.open(12, value)

    def test_oversized_payload_rejected_before_remote_write(self):
        with self.assertRaises(ObjectStorageError):
            self.store.stage(12, b"x" * 1025)
        self.assertEqual(self.client.objects, {})

    def test_delete_removes_staged_and_final_objects(self):
        staged = self.store.stage(12, b"delete me")
        self.assertTrue(self.store.delete(12, staged.object_id))
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, False))
        final = self.store.stage(12, b"delete me too")
        self.store.finalize(12, final.object_id)
        self.assertTrue(self.store.delete(12, final.object_id))
        self.assertFalse(self.store.delete(12, final.object_id))

    def test_inventory_lists_only_keys_in_originals_namespace(self):
        one = self.store.stage(12, b"one")
        self.store.finalize(12, one.object_id)
        other = self.store.stage(13, b"other")
        keys = self.store.list_object_keys()
        self.assertIn(f"firms/12/originals/{one.object_id}.blob", keys)
        self.assertIn(f"firms/13/originals/{other.object_id}.staged", keys)
        self.assertTrue(all(key.startswith("firms/") for key in keys))

    def test_s3_reconciliation_checks_metadata_integrity_and_orphans_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "firm.sqlite3"
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE tenant_database_binding(singleton INTEGER PRIMARY KEY, firm_id INTEGER NOT NULL);
                CREATE TABLE original_file_objects(
                    object_id TEXT PRIMARY KEY, firm_id INTEGER NOT NULL, storage_backend TEXT NOT NULL,
                    sha256 TEXT NOT NULL, byte_size INTEGER NOT NULL, state TEXT NOT NULL, purged_at TEXT
                );
                INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,12);
            """)
            payload = b"verified object"
            staged = self.store.stage(12, payload)
            self.store.finalize(12, staged.object_id)
            db.execute(
                "INSERT INTO original_file_objects VALUES(?,?,?,?,?,'ready',NULL)",
                (staged.object_id, 12, "s3", staged.sha256, staged.byte_size),
            )
            db.commit()
            db.close()

            report = reconcile_s3_original_file_storage(
                self.store, [TenantDatabase(firm_id=12, path=path)]
            )
            self.assertTrue(report.clean, report.findings)
            self.assertEqual(report.checked_metadata_rows, 1)
            self.assertEqual(report.checked_objects, 1)

    def test_s3_reconciliation_reports_missing_object(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "firm.sqlite3"
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE tenant_database_binding(singleton INTEGER PRIMARY KEY, firm_id INTEGER NOT NULL);
                CREATE TABLE original_file_objects(
                    object_id TEXT PRIMARY KEY, firm_id INTEGER NOT NULL, storage_backend TEXT NOT NULL,
                    sha256 TEXT NOT NULL, byte_size INTEGER NOT NULL, state TEXT NOT NULL, purged_at TEXT
                );
                INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,12);
            """)
            db.execute(
                "INSERT INTO original_file_objects VALUES(?,?,?,?,?,'ready',NULL)",
                ("a" * 32, 12, "s3", hashlib.sha256(b"missing").hexdigest(), 7),
            )
            db.commit()
            db.close()

            report = reconcile_s3_original_file_storage(
                self.store, [TenantDatabase(firm_id=12, path=path)]
            )
            self.assertIn("missing_object", {item.code for item in report.findings})

    def test_encrypted_backup_staging_copies_verified_s3_originals(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "tenant.sqlite3"
            payload_dir = root / "payload"
            payload_dir.mkdir()
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE original_file_objects(
                    object_id TEXT PRIMARY KEY, firm_id INTEGER NOT NULL, storage_backend TEXT NOT NULL,
                    sha256 TEXT NOT NULL, byte_size INTEGER NOT NULL, state TEXT NOT NULL, purged_at TEXT
                );
            """)
            payload = b"backup source bytes"
            staged = self.store.stage(12, payload)
            self.store.finalize(12, staged.object_id)
            db.execute(
                "INSERT INTO original_file_objects VALUES(?,?,?,?,?,'ready',NULL)",
                (staged.object_id, 12, "s3", staged.sha256, staged.byte_size),
            )
            db.commit()
            db.close()

            expected = _copy_s3_original_objects(path, 12, self.store, payload_dir)
            backup_copy = payload_dir / "objects" / "firm-12" / f"{staged.object_id}.blob"
            self.assertEqual(expected, {f"firm-12/{staged.object_id}.blob"})
            self.assertEqual(backup_copy.read_bytes(), payload)
            self.assertEqual(_scan_s3_original_object_inventory(self.store), expected)

    def test_missing_kms_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            S3PrivateObjectStore(self.client, "private-matter-files", "")


if __name__ == "__main__":
    unittest.main()
