import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from original_file_storage import LocalPrivateObjectStore
from tools.recover_staged_original_files import _process_tenant


class RecoverStagedOriginalFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.object_root = self.root / "objects"
        self.object_root.mkdir()
        self.store = LocalPrivateObjectStore(self.object_root)
        self.db = self.root / "tenant.sqlite3"
        connection = sqlite3.connect(self.db)
        connection.executescript("""
            CREATE TABLE tenant_database_binding(singleton INTEGER PRIMARY KEY, firm_id INTEGER NOT NULL);
            CREATE TABLE original_file_objects(
                object_id TEXT PRIMARY KEY,
                firm_id INTEGER NOT NULL,
                storage_backend TEXT NOT NULL DEFAULT 'local',
                sha256 TEXT NOT NULL,
                byte_size INTEGER NOT NULL,
                state TEXT NOT NULL,
                updated_at TEXT
            );
            INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,7);
        """)
        connection.commit()
        connection.close()

    def tearDown(self):
        self.temp.cleanup()

    def _add_staged_metadata(self, payload):
        staged = self.store.stage(7, payload)
        connection = sqlite3.connect(self.db)
        connection.execute(
            "INSERT INTO original_file_objects(object_id,firm_id,sha256,byte_size,state) "
            "VALUES(?,?,?,?, 'staged')",
            (staged.object_id, 7, staged.sha256, staged.byte_size),
        )
        connection.commit()
        connection.close()
        return staged

    def _state(self, object_id):
        connection = sqlite3.connect(self.db)
        try:
            return connection.execute(
                "SELECT state FROM original_file_objects WHERE object_id=?", (object_id,)
            ).fetchone()[0]
        finally:
            connection.close()

    def test_dry_run_reports_recoverable_staging_without_mutation(self):
        staged = self._add_staged_metadata(b"recovery candidate")

        recovered, findings = _process_tenant(self.db, 7, self.store, apply=False)

        self.assertEqual(recovered, 0)
        self.assertEqual(findings[0]["status"], "recoverable_candidate")
        self.assertEqual(findings[0]["action"], "finalize_staged_object")
        self.assertEqual(self._state(staged.object_id), "staged")
        self.assertEqual(self.store.object_presence(7, staged.object_id), (True, False))

    def test_apply_finalizes_verified_staged_object_and_marks_ready(self):
        staged = self._add_staged_metadata(b"recover safely")

        recovered, findings = _process_tenant(self.db, 7, self.store, apply=True)

        self.assertEqual(recovered, 1)
        self.assertEqual(findings[0]["status"], "recovered")
        self.assertEqual(self._state(staged.object_id), "ready")
        self.assertEqual(self.store.object_presence(7, staged.object_id), (False, True))
        self.assertTrue(self.store.verify(
            7, staged.object_id, expected_sha256=staged.sha256, expected_size=staged.byte_size
        ))

    def test_apply_repairs_metadata_when_finalization_preceded_crash(self):
        staged = self._add_staged_metadata(b"already finalized")
        self.store.finalize(7, staged.object_id)

        recovered, findings = _process_tenant(self.db, 7, self.store, apply=True)

        self.assertEqual(recovered, 1)
        self.assertEqual(findings[0]["action"], "mark_verified_final_object_ready")
        self.assertEqual(self._state(staged.object_id), "ready")

    def test_corrupt_staged_object_is_preserved_for_manual_review(self):
        staged = self._add_staged_metadata(b"expected bytes")
        staged_path = self.object_root / "firm-7" / f"{staged.object_id}.staged"
        staged_path.write_bytes(b"tampered")

        recovered, findings = _process_tenant(self.db, 7, self.store, apply=True)

        self.assertEqual(recovered, 0)
        self.assertEqual(findings[0]["status"], "manual_review_required")
        self.assertEqual(self._state(staged.object_id), "staged")
        self.assertTrue(staged_path.exists())

    def test_both_staged_and_finalized_files_are_preserved_for_review(self):
        staged = self._add_staged_metadata(b"duplicate files")
        staged_path = self.object_root / "firm-7" / f"{staged.object_id}.staged"
        final_path = self.object_root / "firm-7" / f"{staged.object_id}.blob"
        final_path.write_bytes(b"duplicate files")

        recovered, findings = _process_tenant(self.db, 7, self.store, apply=True)

        self.assertEqual(recovered, 0)
        self.assertEqual(findings[0]["status"], "manual_review_required")
        self.assertEqual(self._state(staged.object_id), "staged")
        self.assertTrue(staged_path.exists())
        self.assertTrue(final_path.exists())


    def test_finalization_failure_rolls_back_metadata_and_preserves_staged_bytes(self):
        staged = self._add_staged_metadata(b"keep recovery bytes")
        staged_path = self.object_root / "firm-7" / f"{staged.object_id}.staged"

        with patch.object(self.store, "finalize", side_effect=OSError("injected storage failure")):
            with self.assertRaisesRegex(OSError, "injected storage failure"):
                _process_tenant(self.db, 7, self.store, apply=True)

        self.assertEqual(self._state(staged.object_id), "staged")
        self.assertTrue(staged_path.is_file())
        self.assertEqual(staged_path.read_bytes(), b"keep recovery bytes")
        self.assertEqual(self.store.object_presence(7, staged.object_id), (True, False))


if __name__ == "__main__":
    unittest.main()
