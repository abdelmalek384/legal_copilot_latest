"""Regression tests for dry-run and apply modes of the restored-original S3 importer."""
import hashlib
import io
import json
import os
import sqlite3
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet

from database_backup import create_backup_bundle, restore_backup_bundle
from database_runtime import DatabaseRuntime
from original_file_storage import StagedObject
from tools import import_restored_originals_to_s3 as importer


class FakeS3Store:
    def __init__(self):
        self.staged = {}
        self.final = {}

    @staticmethod
    def _key(firm_id, object_id):
        return (int(firm_id), object_id)

    def object_presence(self, firm_id, object_id):
        key = self._key(firm_id, object_id)
        return key in self.staged, key in self.final

    def verify_staged(self, firm_id, object_id, *, expected_sha256, expected_size):
        data = self.staged.get(self._key(firm_id, object_id))
        return data is not None and len(data) == expected_size and hashlib.sha256(data).hexdigest() == expected_sha256

    def verify(self, firm_id, object_id, *, expected_sha256, expected_size):
        data = self.final.get(self._key(firm_id, object_id))
        return data is not None and len(data) == expected_size and hashlib.sha256(data).hexdigest() == expected_sha256

    def stage_with_id(self, firm_id, object_id, data):
        key = self._key(firm_id, object_id)
        if key in self.staged or key in self.final:
            raise RuntimeError("duplicate test object")
        self.staged[key] = data
        return StagedObject(object_id, hashlib.sha256(data).hexdigest(), len(data))

    def finalize(self, firm_id, object_id):
        key = self._key(firm_id, object_id)
        if key not in self.staged or key in self.final:
            raise RuntimeError("invalid fake finalization")
        self.final[key] = self.staged.pop(key)

    def delete(self, firm_id, object_id):
        key = self._key(firm_id, object_id)
        self.staged.pop(key, None)
        self.final.pop(key, None)


class RestoredOriginalS3ImporterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = self.root / "source"
        self.runtime = DatabaseRuntime(
            source / "control_plane.sqlite3",
            source / "tenants",
            source / "legal_corpus.sqlite3",
        )
        self.runtime.initialize()
        self.firm_id, _ = self.runtime.provision_firm("Importer test firm")
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_id, "Importer Owner", "importer-owner@example.test", "test-password-hash"
        )

        self.payload = b"verified restored original bytes\x00"
        self.object_id = "a" * 32
        context = self.runtime.resolve_context(self.user_id, self.firm_id)
        firm_db = self.runtime.firm_connection(context)
        case_id = firm_db.execute(
            "INSERT INTO cases(title,created_by,firm_id) VALUES(?,?,?)",
            ("Synthetic importer case", self.user_id, self.firm_id),
        ).lastrowid
        doc_id = firm_db.execute(
            "INSERT INTO docs(case_id,name,firm_id,uploader_user_id,sha256,content_type,byte_size,extraction_status) "
            "VALUES(?,?,?,?,?,?,?,'text_extracted')",
            (case_id, "synthetic.txt", self.firm_id, self.user_id,
             hashlib.sha256(self.payload).hexdigest(), "text/plain", len(self.payload)),
        ).lastrowid
        firm_db.execute(
            "INSERT INTO original_file_objects(object_id,document_id,firm_id,storage_backend,sha256,byte_size,state) "
            "VALUES(?,?,?,'local',?,?,'ready')",
            (self.object_id, doc_id, self.firm_id,
             hashlib.sha256(self.payload).hexdigest(), len(self.payload)),
        )
        firm_db.commit()

        self.object_root = source / "objects"
        namespace = self.object_root / f"firm-{self.firm_id}"
        namespace.mkdir(parents=True, mode=0o700)
        object_path = namespace / f"{self.object_id}.blob"
        object_path.write_bytes(self.payload)
        if os.name == "posix":
            object_path.chmod(0o600)

        self.cipher = Fernet(Fernet.generate_key())
        self.backup_dir = self.root / "backups"
        self.backup_dir.mkdir()
        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir, quiesced=True,
            object_storage_root=self.object_root,
        )
        self.restore_root = self.root / "restored"
        restore_backup_bundle(bundle, self.cipher, self.restore_root)
        self.store = FakeS3Store()

    def tearDown(self):
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        self.temp.cleanup()

    def _run_import(self, *, apply):
        fake_boto3 = types.ModuleType("boto3")
        fake_boto3.client = lambda *args, **kwargs: object()
        argv = [
            "import_restored_originals_to_s3.py",
            "--restore-root", str(self.restore_root),
        ]
        if apply:
            argv.append("--apply")
        env = {
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_S3_BUCKET": "test-private-originals",
            "COPILOT_S3_REGION": "eu-west-1",
            "COPILOT_S3_KMS_KEY_ID": "test-managed-key",
        }
        output = io.StringIO()
        with patch.dict(os.environ, env, clear=False), patch.dict(sys.modules, {"boto3": fake_boto3}), \
             patch.object(DatabaseRuntime, "from_env", return_value=self.runtime), \
             patch.object(importer, "S3PrivateObjectStore", return_value=self.store), \
             patch("sys.argv", argv), redirect_stdout(output):
            code = importer.main()
        return code, json.loads(output.getvalue())

    def _restored_storage_backend(self):
        control = sqlite3.connect(self.restore_root / "control_plane.sqlite3")
        try:
            filename = control.execute(
                "SELECT database_file FROM tenant_database_catalog WHERE firm_id=?", (self.firm_id,)
            ).fetchone()[0]
        finally:
            control.close()
        db = sqlite3.connect(self.restore_root / "tenants" / filename)
        try:
            return db.execute(
                "SELECT storage_backend FROM original_file_objects WHERE object_id=?", (self.object_id,)
            ).fetchone()[0]
        finally:
            db.close()

    def test_dry_run_verifies_restore_without_upload_or_metadata_mutation(self):
        code, report = self._run_import(apply=False)
        self.assertEqual(code, 0)
        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["objects_checked"], 1)
        self.assertEqual(report["actions"][0]["action"], "would_import")
        self.assertEqual(report["mutations_performed"], 0)
        self.assertEqual(self.store.staged, {})
        self.assertEqual(self.store.final, {})
        self.assertEqual(self._restored_storage_backend(), "local")

    def test_apply_uploads_verified_object_and_updates_only_restored_metadata(self):
        code, report = self._run_import(apply=True)
        self.assertEqual(code, 0)
        self.assertEqual(report["mode"], "apply")
        self.assertEqual(report["actions"][0]["action"], "imported")
        self.assertTrue(report["actions"][0]["metadata_updated"])
        self.assertEqual(report["mutations_performed"], 1)
        self.assertEqual(self.store.staged, {})
        self.assertEqual(self.store.final[(self.firm_id, self.object_id)], self.payload)
        self.assertEqual(self._restored_storage_backend(), "s3")
        # The source tenant remains unchanged: this command only migrates the isolated restore.
        source_context = self.runtime.resolve_context(self.user_id, self.firm_id)
        source_db = self.runtime.firm_connection(source_context)
        self.assertEqual(source_db.execute(
            "SELECT storage_backend FROM original_file_objects WHERE object_id=?", (self.object_id,)
        ).fetchone()[0], "local")


if __name__ == "__main__":
    unittest.main()
