import os
import tempfile
import unittest
from pathlib import Path

from original_file_storage import LocalPrivateObjectStore, ObjectStorageError


class LocalPrivateObjectStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "private-objects"
        self.store = LocalPrivateObjectStore(self.root, max_bytes=1024)

    def tearDown(self):
        self.temp.cleanup()

    def test_stage_finalize_and_verify_bytes(self):
        payload = b"confidential matter original\x00bytes"
        staged = self.store.stage(7, payload)
        self.assertEqual(staged.byte_size, len(payload))
        self.assertEqual(len(staged.sha256), 64)
        staged_path = self.root / "firm-7" / (staged.object_id + ".staged")
        final_path = self.root / "firm-7" / (staged.object_id + ".blob")
        self.assertTrue(staged_path.exists())
        self.assertFalse(final_path.exists())
        self.store.finalize(7, staged.object_id)
        self.assertFalse(staged_path.exists())
        with self.store.open(7, staged.object_id) as handle:
            self.assertEqual(handle.read(), payload)
        self.assertTrue(self.store.verify(7, staged.object_id,
                                          expected_sha256=staged.sha256,
                                          expected_size=len(payload)))
        self.assertFalse(self.store.verify(7, staged.object_id,
                                           expected_sha256="0" * 64,
                                           expected_size=len(payload)))

    def test_firm_namespaces_are_isolated(self):
        staged = self.store.stage(7, b"firm seven")
        self.store.finalize(7, staged.object_id)
        with self.assertRaises(ObjectStorageError):
            self.store.open(8, staged.object_id)

    def test_rejects_invalid_firm_and_object_ids(self):
        for firm_id in (0, -1, True, "7"):
            with self.assertRaises(ValueError):
                self.store.stage(firm_id, b"x")
        for object_id in ("../escape", "a" * 31, "A" * 32, ""):
            with self.assertRaises(ValueError):
                self.store.open(7, object_id)

    def test_rejects_oversize_payload_before_writing(self):
        with self.assertRaises(ObjectStorageError):
            self.store.stage(7, b"x" * 1025)
        self.assertEqual(list((self.root / "firm-7").glob("*")) if (self.root / "firm-7").exists() else [], [])

    def test_does_not_overwrite_existing_final_object(self):
        first = self.store.stage(7, b"first")
        self.store.finalize(7, first.object_id)
        staged_path = self.root / "firm-7" / (first.object_id + ".staged")
        staged_path.write_bytes(b"second")
        with self.assertRaises(ObjectStorageError):
            self.store.finalize(7, first.object_id)
        with self.store.open(7, first.object_id) as handle:
            self.assertEqual(handle.read(), b"first")

    def test_rejects_symlinked_firm_namespace(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        other = Path(self.temp.name) / "other"
        other.mkdir()
        namespace = self.root / "firm-9"
        namespace.symlink_to(other, target_is_directory=True)
        with self.assertRaises(ObjectStorageError):
            self.store.stage(9, b"must not escape")

    def test_delete_removes_staged_or_final_object(self):
        staged = self.store.stage(7, b"delete me")
        self.assertTrue(self.store.delete(7, staged.object_id))
        self.assertFalse(self.store.delete(7, staged.object_id))
        final = self.store.stage(7, b"delete me too")
        self.store.finalize(7, final.object_id)
        self.assertTrue(self.store.delete(7, final.object_id))
        self.assertFalse((self.root / "firm-7" / (final.object_id + ".blob")).exists())

    @unittest.skipUnless(os.name == "posix", "POSIX permission check")
    def test_storage_permissions_are_private(self):
        self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
        staged = self.store.stage(7, b"private")
        path = self.root / "firm-7" / (staged.object_id + ".staged")
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.store.finalize(7, staged.object_id)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)


if __name__ == "__main__":
    unittest.main()
