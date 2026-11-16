import os
import tempfile
import unittest
from unittest.mock import patch
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
        self.assertEqual(self.store.object_presence(7, staged.object_id), (True, False))
        self.assertTrue(self.store.verify_staged(
            7, staged.object_id, expected_sha256=staged.sha256, expected_size=len(payload)
        ))
        self.assertFalse(self.store.verify_staged(
            7, staged.object_id, expected_sha256="0" * 64, expected_size=len(payload)
        ))
        self.store.finalize(7, staged.object_id)
        self.assertEqual(self.store.object_presence(7, staged.object_id), (False, True))
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

    @unittest.skipUnless(os.name == "posix", "POSIX symlinks are required")
    def test_finalize_rejects_staged_path_replaced_by_symlink(self):
        staged = self.store.stage(7, b"trusted original")
        namespace = self.root / "firm-7"
        staged_path = namespace / (staged.object_id + ".staged")
        final_path = namespace / (staged.object_id + ".blob")
        outside = Path(self.temp.name) / "outside-secret"
        outside.write_bytes(b"outside data")
        real_link = os.link

        def replace_before_link(source, destination, **kwargs):
            staged_path.unlink()
            staged_path.symlink_to(outside)
            return real_link(source, destination, **kwargs)

        with patch("original_file_storage.os.link", side_effect=replace_before_link):
            with self.assertRaisesRegex(ObjectStorageError, "not a regular file|changed while finalizing"):
                self.store.finalize(7, staged.object_id)

        self.assertFalse(final_path.exists())
        self.assertFalse(final_path.is_symlink())
        self.assertEqual(outside.read_bytes(), b"outside data")

    @unittest.skipUnless(os.name == "posix", "POSIX directory symlinks are required")
    def test_stage_is_not_redirected_by_firm_directory_symlink_swap(self):
        existing = self.store.stage(7, b"preserve staged object")
        namespace = self.root / "firm-7"
        parked = self.root / "firm-7-parked"
        outside = Path(self.temp.name) / "outside-namespace"
        outside.mkdir()
        sentinel = outside / "sentinel"
        sentinel.write_bytes(b"outside data")
        real_open = os.open
        swapped = False

        def swap_before_namespace_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if path == "firm-7" and kwargs.get("dir_fd") is not None and not swapped:
                namespace.rename(parked)
                namespace.symlink_to(outside, target_is_directory=True)
                swapped = True
            return real_open(path, flags, *args, **kwargs)

        try:
            with patch("original_file_storage.os.open", side_effect=swap_before_namespace_open):
                with self.assertRaises(ObjectStorageError):
                    self.store.stage(7, b"must not escape")
        finally:
            if namespace.is_symlink():
                namespace.unlink()
            if parked.exists():
                parked.rename(namespace)

        self.assertTrue(swapped)
        self.assertEqual(sentinel.read_bytes(), b"outside data")
        self.assertEqual(
            (namespace / (existing.object_id + ".staged")).read_bytes(),
            b"preserve staged object",
        )
        self.assertEqual(
            sorted(path.name for path in namespace.iterdir()),
            [existing.object_id + ".staged"],
        )

    @unittest.skipUnless(os.name == "posix", "POSIX hard links are required")
    def test_finalize_rejects_staged_object_with_external_hardlink(self):
        staged = self.store.stage(7, b"trusted original")
        staged_path = self.root / "firm-7" / (staged.object_id + ".staged")
        final_path = self.root / "firm-7" / (staged.object_id + ".blob")
        outside = Path(self.temp.name) / "outside-hardlink"
        os.link(staged_path, outside)

        with self.assertRaisesRegex(ObjectStorageError, "regular file"):
            self.store.finalize(7, staged.object_id)

        self.assertFalse(final_path.exists())
        self.assertEqual(outside.read_bytes(), b"trusted original")
        self.assertEqual(staged_path.read_bytes(), b"trusted original")

    @unittest.skipUnless(os.name == "posix", "POSIX hard links are required")
    def test_open_and_verify_reject_final_object_with_external_hardlink(self):
        staged = self.store.stage(7, b"private original")
        self.store.finalize(7, staged.object_id)
        final_path = self.root / "firm-7" / (staged.object_id + ".blob")
        outside = Path(self.temp.name) / "outside-final-hardlink"
        os.link(final_path, outside)

        with self.assertRaisesRegex(ObjectStorageError, "single-link"):
            self.store.open(7, staged.object_id)
        self.assertFalse(self.store.verify(
            7, staged.object_id,
            expected_sha256=staged.sha256,
            expected_size=staged.byte_size,
        ))
        self.assertEqual(outside.read_bytes(), b"private original")

    def test_store_rejects_replaced_root_directory(self):
        staged = self.store.stage(7, b"pinned-root data")
        parked = self.root.with_name("private-objects-parked")
        self.root.rename(parked)
        self.root.mkdir(mode=0o700)

        with self.assertRaisesRegex(ObjectStorageError, "root directory changed"):
            self.store.stage(7, b"must not enter replacement root")

        self.assertEqual(
            (parked / "firm-7" / (staged.object_id + ".staged")).read_bytes(),
            b"pinned-root data",
        )
        self.assertEqual(list(self.root.iterdir()), [])

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
