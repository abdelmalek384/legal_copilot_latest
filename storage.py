"""Small SQLite connection-provider boundary for Legal Copilot.

This module intentionally provides connection lifecycle only. It does not resolve
firms, authorize users, or select tenant databases. The application currently
uses one configured database path; tenant routing must be implemented separately
only after the identity and shared-corpus model is reviewed.
"""
import sqlite3
import threading
from pathlib import Path
from typing import Union


DatabasePath = Union[str, Path]


class SQLiteConnectionProvider:
    """Return one SQLite connection per thread for one configured database path."""

    def __init__(self, database_path: DatabasePath, timeout: float = 30.0):
        if database_path is None or str(database_path).strip() == "":
            raise ValueError("database_path must be a non-empty path")
        self.database_path = str(database_path)
        self.timeout = float(timeout)
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        self._local = threading.local()

    def connection(self) -> sqlite3.Connection:
        """Get this thread's connection, creating it lazily when needed."""
        connection = getattr(self._local, "c", None)
        if connection is None:
            connection = sqlite3.connect(self.database_path, timeout=self.timeout)
            connection.row_factory = sqlite3.Row
            self._local.c = connection
        return connection

    def close_current_thread(self) -> None:
        """Close and clear the connection owned by the calling thread."""
        connection = getattr(self._local, "c", None)
        if connection is not None:
            try:
                connection.close()
            finally:
                del self._local.c
