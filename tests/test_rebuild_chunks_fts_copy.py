"""Tests for rebuilding FTS only on a newly created copy."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.rebuild_chunks_fts_copy import rebuild_copy
from schema_profiles import apply_profile_migrations

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


class RebuildChunksFtsCopyTests(unittest.TestCase):
    def make_source(self, path: Path, *, existing_fts: bool) -> None:
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, text TEXT, norm TEXT)")
            db.executemany(
                "INSERT INTO chunks(id,text,norm) VALUES(?,?,?)",
                [(1, "hello world", "old token"), (2, "legal rules", "stale")],
            )
            if existing_fts:
                db.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(norm)")
                db.execute("INSERT INTO chunks_fts(rowid,norm) VALUES(1,'wrong index')")
                db.commit()

    def test_missing_index_rebuilds_only_in_new_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.sqlite3"
            output = root / "rebuilt.sqlite3"
            self.make_source(source, existing_fts=False)

            report = rebuild_copy(source, output)

            self.assertEqual(report["status"], "passed")
            self.assertFalse(report["source_modified"])
            self.assertEqual(report["source_chunks"], 2)
            self.assertEqual(report["staged_chunks"], 2)
            self.assertEqual(report["fts_audit"]["finding_count"], 0)
            with sqlite3.connect(source) as db:
                names = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertNotIn("chunks_fts", names)
                self.assertNotIn("schema_migrations", names)
            with sqlite3.connect(output) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0], 2)
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'hello'").fetchone()[0],
                    1,
                )

    def test_stale_index_rebuilt_in_copy_source_remains_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.sqlite3"
            output = root / "rebuilt.sqlite3"
            self.make_source(source, existing_fts=True)

            report = rebuild_copy(source, output)

            self.assertEqual(report["status"], "passed")
            with sqlite3.connect(source) as db:
                self.assertEqual(db.execute("SELECT norm FROM chunks_fts WHERE rowid=1").fetchone()[0], "wrong index")
            with sqlite3.connect(output) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0], 2)
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'hello'").fetchone()[0],
                    1,
                )

    def test_profile_database_rebuild_preserves_external_content_schema_and_triggers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "firm.sqlite3"
            output = root / "firm-rebuilt.sqlite3"
            with sqlite3.connect(source) as db:
                apply_profile_migrations(db, "firm", MIGRATIONS)
                db.execute("INSERT INTO cases(id,title) VALUES(1,'firm matter')")
                db.execute(
                    "INSERT INTO chunks(id,text,norm,case_id) VALUES(1,?,?,1)",
                    ("source text", "canonical_profile_norm"),
                )
                db.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('delete-all')")
                db.commit()

            report = rebuild_copy(source, output)

            self.assertEqual(report["status"], "passed", report)
            self.assertEqual(report["database_profile"], "firm")
            self.assertFalse(report["source_modified"])
            with sqlite3.connect(source) as db:
                self.assertEqual(
                    db.execute(
                        "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'canonical_profile_norm'"
                    ).fetchone()[0],
                    0,
                )
            with sqlite3.connect(output) as db:
                definition = db.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' AND name='chunks_fts'"
                ).fetchone()[0]
                self.assertIn("content='chunks'", definition)
                self.assertEqual(
                    db.execute(
                        "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'canonical_profile_norm'"
                    ).fetchone()[0],
                    1,
                )
                triggers = {
                    row[0] for row in db.execute(
                        "SELECT name FROM sqlite_master WHERE type='trigger'"
                    )
                }
                self.assertTrue({
                    "chunks_fts_insert", "chunks_fts_delete", "chunks_fts_update"
                }.issubset(triggers))
                db.execute("UPDATE chunks SET norm='updated_profile_norm' WHERE id=1")
                db.commit()
                self.assertEqual(
                    db.execute(
                        "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'updated_profile_norm'"
                    ).fetchone()[0],
                    1,
                )

    def test_refuses_to_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.sqlite3"
            output = root / "existing.sqlite3"
            self.make_source(source, existing_fts=False)
            output.write_bytes(b"keep me")
            with self.assertRaises(FileExistsError):
                rebuild_copy(source, output)
            self.assertEqual(output.read_bytes(), b"keep me")

    def test_failure_does_not_leave_partial_output_or_change_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.sqlite3"
            output = root / "rebuilt.sqlite3"
            with sqlite3.connect(source) as db:
                db.execute("CREATE TABLE unrelated(id INTEGER)")
            with self.assertRaisesRegex(ValueError, "no chunks table"):
                rebuild_copy(source, output)
            self.assertFalse(output.exists())
            with sqlite3.connect(source) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM unrelated").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
