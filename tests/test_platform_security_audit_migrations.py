import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from schema_profiles import apply_profile_migrations

ROOT = Path(__file__).resolve().parents[1] / "migrations"


class PlatformSecurityAuditMigrationTests(unittest.TestCase):
    def test_event_vocabulary_migration_preserves_old_events_and_allows_web_password_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "migrations"
            control = root / "control_plane"
            control.mkdir(parents=True)
            for path in sorted((ROOT / "control_plane").glob("000[1-5]_*.sql")):
                shutil.copy(path, control / path.name)
            db = sqlite3.connect(":memory:")
            db.row_factory = sqlite3.Row
            try:
                apply_profile_migrations(db, "control_plane", root)
                db.execute(
                    "INSERT INTO platform_security_events(event_type,detail_json) VALUES('password_reset_cli','{}')"
                )
                db.commit()
                shutil.copy(
                    ROOT / "control_plane" / "0006_platform_security_events_web_password_change.sql",
                    control / "0006_platform_security_events_web_password_change.sql",
                )
                self.assertEqual(apply_profile_migrations(db, "control_plane", root), [6])
                existing = db.execute(
                    "SELECT id,event_type,detail_json FROM platform_security_events"
                ).fetchone()
                self.assertEqual(existing["id"], 1)
                self.assertEqual(existing["event_type"], "password_reset_cli")
                db.execute(
                    "INSERT INTO platform_security_events(event_type,detail_json) VALUES('password_changed_web','{}')"
                )
                db.commit()
                self.assertEqual(db.execute("SELECT COUNT(*) FROM platform_security_events").fetchone()[0], 2)
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
