"""Regression tests for authenticated, validated, atomic encrypted database restores."""
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from cryptography.fernet import Fernet


ROOT = Path(__file__).resolve().parents[1]
MANAGE = ROOT / "manage.py"


def run_restore(source: Path, destination: Path, key: bytes, db_path: Path):
    env = os.environ.copy()
    env["BACKUP_KEY"] = key.decode()
    env["COPILOT_DB"] = str(db_path)
    return subprocess.run(
        [sys.executable, str(MANAGE), "restore", str(source), str(destination)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def sqlite_payload(path: Path) -> bytes:
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE sentinel (value TEXT NOT NULL)")
        connection.execute("INSERT INTO sentinel(value) VALUES('valid')")
        connection.commit()
    finally:
        connection.close()
    return path.read_bytes()


def test_restore_authenticates_before_replacing_existing_destination(tmp_path):
    key = Fernet.generate_key()
    wrong_key = Fernet.generate_key()
    encrypted = tmp_path / "backup.db.enc"
    encrypted.write_bytes(Fernet(key).encrypt(b"not a real database, but authenticated payload"))
    destination = tmp_path / "restored.db"
    original = b"existing destination must survive a wrong key"
    destination.write_bytes(original)

    result = run_restore(encrypted, destination, wrong_key, tmp_path / "app.db")

    assert result.returncode != 0
    assert destination.read_bytes() == original
    assert not list(tmp_path.glob(".restore-*.tmp"))


def test_restore_validates_sqlite_before_atomic_replacement(tmp_path):
    key = Fernet.generate_key()
    payload = tmp_path / "backup.db.enc"
    plaintext = sqlite_payload(tmp_path / "source.db")
    payload.write_bytes(Fernet(key).encrypt(plaintext))
    destination = tmp_path / "restored.db"

    result = run_restore(payload, destination, key, tmp_path / "app.db")

    assert result.returncode == 0, result.stderr
    restored = sqlite3.connect(destination)
    try:
        assert restored.execute("SELECT value FROM sentinel").fetchone() == ("valid",)
        assert restored.execute("PRAGMA quick_check").fetchone() == ("ok",)
    finally:
        restored.close()
    assert not list(tmp_path.glob(".restore-*.tmp"))


def test_restore_does_not_accept_tampered_ciphertext(tmp_path):
    key = Fernet.generate_key()
    payload = tmp_path / "backup.db.enc"
    token = Fernet(key).encrypt(sqlite_payload(tmp_path / "source.db"))
    payload.write_bytes(token[:-2] + (b"AA" if token[-2:] != b"AA" else b"BB"))
    destination = tmp_path / "restored.db"

    result = run_restore(payload, destination, key, tmp_path / "app.db")

    assert result.returncode != 0
    assert not destination.exists()
    assert not list(tmp_path.glob(".restore-*.tmp"))


def test_authenticated_non_sqlite_payload_cannot_replace_existing_database(tmp_path):
    key = Fernet.generate_key()
    payload = tmp_path / "backup.db.enc"
    payload.write_bytes(Fernet(key).encrypt(b"authenticated but not a SQLite database"))
    destination = tmp_path / "restored.db"
    original = sqlite_payload(tmp_path / "existing.db")
    destination.write_bytes(original)

    result = run_restore(payload, destination, key, tmp_path / "app.db")

    assert result.returncode != 0
    assert "not a readable SQLite database" in result.stderr
    assert destination.read_bytes() == original
    assert not list(tmp_path.glob(".restore-*.tmp"))
