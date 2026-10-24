"""Tests for the connection-lifecycle boundary (not tenant isolation)."""
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from storage import SQLiteConnectionProvider


class SQLiteConnectionProviderTests(unittest.TestCase):
    def test_same_thread_reuses_connection_and_returns_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = SQLiteConnectionProvider(Path(directory) / "firm.db")
            try:
                first = provider.connection()
                second = provider.connection()
                self.assertIs(first, second)
                first.execute("CREATE TABLE example (value TEXT)")
                first.execute("INSERT INTO example(value) VALUES ('ok')")
                first.commit()
                row = second.execute("SELECT value FROM example").fetchone()
                self.assertIsInstance(row, sqlite3.Row)
                self.assertEqual(row["value"], "ok")
            finally:
                provider.close_current_thread()

    def test_each_thread_gets_its_own_connection(self):
        with tempfile.TemporaryDirectory() as directory:
            provider = SQLiteConnectionProvider(Path(directory) / "threaded.db")
            main_connection = provider.connection()
            worker_connections = []
            failures = []

            def worker():
                try:
                    connection = provider.connection()
                    worker_connections.append(connection)
                    connection.execute("SELECT 1").fetchone()
                except Exception as exc:  # surfaced in the test thread
                    failures.append(exc)
                finally:
                    provider.close_current_thread()

            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()
            try:
                self.assertEqual(failures, [])
                self.assertEqual(len(worker_connections), 1)
                self.assertIsNot(main_connection, worker_connections[0])
            finally:
                provider.close_current_thread()

    def test_providers_keep_configured_databases_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            first = SQLiteConnectionProvider(Path(directory) / "first.db")
            second = SQLiteConnectionProvider(Path(directory) / "second.db")
            try:
                first.connection().execute("CREATE TABLE marker (value TEXT)")
                first.connection().execute("INSERT INTO marker VALUES ('first')")
                first.connection().commit()
                second.connection().execute("CREATE TABLE marker (value TEXT)")
                second.connection().execute("INSERT INTO marker VALUES ('second')")
                second.connection().commit()

                first_value = first.connection().execute("SELECT value FROM marker").fetchone()[0]
                second_value = second.connection().execute("SELECT value FROM marker").fetchone()[0]
                self.assertEqual(first_value, "first")
                self.assertEqual(second_value, "second")
            finally:
                first.close_current_thread()
                second.close_current_thread()

    def test_rejects_empty_path_and_nonpositive_timeout(self):
        with self.assertRaises(ValueError):
            SQLiteConnectionProvider("")
        with self.assertRaises(ValueError):
            SQLiteConnectionProvider("copilot.db", timeout=0)


if __name__ == "__main__":
    unittest.main()
