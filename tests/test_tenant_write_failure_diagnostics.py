"""Preserve root-cause diagnostics while keeping tenant write errors generic to clients."""
import sqlite3
import unittest
from unittest.mock import patch

from fastapi import HTTPException

import app


class _RollbackProbe:
    def __init__(self):
        self.called = False

    def rollback(self):
        self.called = True


class TenantWriteFailureDiagnosticTests(unittest.TestCase):
    def test_sqlite_failure_is_logged_and_client_response_stays_generic(self):
        probe = _RollbackProbe()

        @app.rollback_tenant_transaction_on_error
        def fail_write():
            raise sqlite3.OperationalError("database is locked")

        with patch.object(app, "conn", return_value=probe):
            with self.assertLogs(app.logger, level="ERROR") as captured:
                with self.assertRaises(HTTPException) as raised:
                    fail_write()

        self.assertEqual(raised.exception.status_code, 503)
        self.assertEqual(raised.exception.detail, "database write unavailable")
        self.assertTrue(probe.called)
        output = "\n".join(captured.output)
        self.assertIn("Tenant database write failed", output)
        self.assertIn("OperationalError", output)
        self.assertIn("database is locked", output)


if __name__ == "__main__":
    unittest.main()
