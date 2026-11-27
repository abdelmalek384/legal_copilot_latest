import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from schema_profiles import apply_profile_migrations

ROOT = Path(__file__).resolve().parents[1] / "migrations"


class PlatformSecurityAuditMigrationTests(unittest.TestCase):
    def test_membership_suspension_event_migration_preserves_existing_audit_history(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "migrations"
            control = root / "control_plane"
            control.mkdir(parents=True)
            for path in sorted((ROOT / "control_plane").glob("000[1-7]_*.sql")):
                shutil.copy(path, control / path.name)
            db = sqlite3.connect(":memory:")
            db.row_factory = sqlite3.Row
            try:
                apply_profile_migrations(db, "control_plane", root)
                db.execute(
                    "INSERT INTO platform_security_events(event_type,detail_json) VALUES('password_changed_web','{}')"
                )
                db.execute(
                    "INSERT INTO platform_security_events(event_type,detail_json) VALUES('membership_created','{}')"
                )
                db.commit()
                shutil.copy(
                    ROOT / "control_plane" / "0008_platform_security_events_membership_suspension.sql",
                    control / "0008_platform_security_events_membership_suspension.sql",
                )
                self.assertEqual(apply_profile_migrations(db, "control_plane", root), [8])
                self.assertEqual(
                    [row["event_type"] for row in db.execute("SELECT event_type FROM platform_security_events ORDER BY id")],
                    ["password_changed_web", "membership_created"],
                )
                db.execute(
                    "INSERT INTO platform_security_events(event_type,detail_json) VALUES('membership_suspended','{}')"
                )
                db.commit()
                self.assertEqual(db.execute("SELECT COUNT(*) FROM platform_security_events").fetchone()[0], 3)
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            finally:
                db.close()

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
                    ROOT / "control_plane" / "0007_platform_security_events_web_password_change.sql",
                    control / "0007_platform_security_events_web_password_change.sql",
                )
                self.assertEqual(apply_profile_migrations(db, "control_plane", root), [7])
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

    def test_logout_event_migration_0027_preserves_current_audit_history_and_vocabulary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "migrations"
            control = root / "control_plane"
            control.mkdir(parents=True)
            source = ROOT / "control_plane"
            for path in sorted(source.glob("*.sql")):
                if int(path.name[:4]) <= 26:
                    shutil.copy(path, control / path.name)

            db = sqlite3.connect(":memory:")
            db.row_factory = sqlite3.Row
            try:
                applied = apply_profile_migrations(db, "control_plane", root)
                self.assertEqual(applied, list(range(1, 27)))
                db.execute(
                    "INSERT INTO platform_security_events(event_type,detail_json) "
                    "VALUES('membership_reactivated','{\"existing\":true}')"
                )
                db.commit()

                shutil.copy(
                    source / "0027_platform_security_events_logout.sql",
                    control / "0027_platform_security_events_logout.sql",
                )
                self.assertEqual(
                    apply_profile_migrations(db, "control_plane", root),
                    [27],
                )

                existing = db.execute(
                    "SELECT id,event_type,detail_json FROM platform_security_events"
                ).fetchone()
                self.assertEqual(
                    (existing["id"], existing["event_type"], existing["detail_json"]),
                    (1, "membership_reactivated", '{"existing":true}'),
                )

                db.execute(
                    "INSERT INTO platform_security_events(event_type,detail_json) "
                    "VALUES('logout','{\"method\":\"web\",\"session_revoked\":true}')"
                )
                db.commit()
                self.assertEqual(
                    [row["event_type"] for row in db.execute(
                        "SELECT event_type FROM platform_security_events ORDER BY id"
                    )],
                    ["membership_reactivated", "logout"],
                )
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute("UPDATE platform_security_events SET detail_json='{}' WHERE id=1")
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute("DELETE FROM platform_security_events WHERE id=1")
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
