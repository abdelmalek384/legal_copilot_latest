import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from original_file_reconciliation import (
    TenantDatabase,
    reconcile_original_file_storage,
)


class OriginalFileReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.objects = self.root / "objects"
        self.objects.mkdir()
        self.db = self.root / "tenant.sqlite3"
        self.firm_id = 7
        self.object_id = "a" * 32
        self.payload = b"reconciliation fixture bytes"
        self._create_database()

    def tearDown(self):
        self.temp.cleanup()

    def _create_database(self, *, firm_id=7, rows=None):
        connection = sqlite3.connect(self.db)
        connection.executescript("""
            CREATE TABLE tenant_database_binding(singleton INTEGER PRIMARY KEY, firm_id INTEGER NOT NULL);
            CREATE TABLE original_file_objects(
                object_id TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                byte_size INTEGER NOT NULL,
                state TEXT NOT NULL
            );
        """)
        connection.execute(
            "INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,?)", (firm_id,)
        )
        for object_id, payload, state in rows or []:
            connection.execute(
                "INSERT INTO original_file_objects(object_id,sha256,byte_size,state) VALUES(?,?,?,?)",
                (object_id, hashlib.sha256(payload).hexdigest(), len(payload), state),
            )
        connection.commit()
        connection.close()

    def _reconcile(self, *, firm_id=7):
        return reconcile_original_file_storage(
            self.objects, [TenantDatabase(firm_id=firm_id, path=self.db)]
        )

    def test_clean_ready_object_passes_integrity_check(self):
        self._create_database(rows=[(self.object_id, self.payload, "ready")])
        directory = self.objects / "firm-7"
        directory.mkdir()
        (directory / f"{self.object_id}.blob").write_bytes(self.payload)

        report = self._reconcile()

        self.assertTrue(report.clean, report.findings)
        self.assertEqual(report.checked_databases, 1)
        self.assertEqual(report.checked_metadata_rows, 1)
        self.assertEqual(report.checked_objects, 1)

    def test_detects_corrupt_bytes_and_missing_ready_object(self):
        self._create_database(rows=[
            (self.object_id, self.payload, "ready"),
            ("b" * 32, self.payload, "ready"),
        ])
        directory = self.objects / "firm-7"
        directory.mkdir()
        (directory / f"{self.object_id}.blob").write_bytes(b"tampered bytes")

        report = self._reconcile()
        codes = {finding.code for finding in report.findings}

        self.assertIn("object_integrity_mismatch", codes)
        self.assertIn("missing_object", codes)

    def test_reports_orphaned_file_without_deleting_it(self):
        directory = self.objects / "firm-7"
        directory.mkdir()
        orphan = directory / f"{self.object_id}.blob"
        orphan.write_bytes(self.payload)

        report = self._reconcile()

        self.assertIn("orphaned_object", {finding.code for finding in report.findings})
        self.assertTrue(orphan.exists(), "reconciliation must be read-only")

    def test_reports_finalized_blob_with_staged_metadata_as_crash_window(self):
        self._create_database(rows=[(self.object_id, self.payload, "staged")])
        directory = self.objects / "firm-7"
        directory.mkdir()
        (directory / f"{self.object_id}.blob").write_bytes(self.payload)

        report = self._reconcile()

        self.assertIn(
            "finalized_object_state_not_committed",
            {finding.code for finding in report.findings},
        )
        self.assertFalse(any(f.code == "missing_object" for f in report.findings))

    def test_refuses_database_firm_binding_mismatch(self):
        self._create_database(firm_id=99)

        report = self._reconcile(firm_id=7)

        self.assertIn("tenant_binding_mismatch", {finding.code for finding in report.findings})

    def test_refuses_duplicate_firm_database_inputs(self):
        with self.assertRaises(ValueError):
            reconcile_original_file_storage(
                self.objects,
                [
                    TenantDatabase(firm_id=7, path=self.db),
                    TenantDatabase(firm_id=7, path=self.db),
                ],
            )

    def test_does_not_follow_symlinked_object(self):
        self._create_database(rows=[(self.object_id, self.payload, "ready")])
        directory = self.objects / "firm-7"
        directory.mkdir()
        outside = self.root / "outside.blob"
        outside.write_bytes(self.payload)
        (directory / f"{self.object_id}.blob").symlink_to(outside)

        report = self._reconcile()

        self.assertIn("unsafe_object_entry", {finding.code for finding in report.findings})
        self.assertEqual(outside.read_bytes(), self.payload)


if __name__ == "__main__":
    unittest.main()
