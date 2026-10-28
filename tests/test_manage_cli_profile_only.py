"""CLI write commands must never silently target the shared compatibility database."""
import os
import unittest
from argparse import Namespace
from unittest.mock import patch
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import manage


class ProfileSeparatedCLITests(unittest.TestCase):
    def test_adduser_refuses_shared_database_before_password_prompt(self):
        with patch.dict(os.environ, {"COPILOT_DB": "/tmp/legacy.sqlite3"}, clear=True):
            with patch("manage.read_password") as prompt:
                with self.assertRaisesRegex(SystemExit, "profile-separated database runtime"):
                    manage.adduser(Namespace(name="User", email="user@example.test", role="lawyer", firm_id=1))
            prompt.assert_not_called()

    def test_resetpw_refuses_shared_database_before_password_prompt(self):
        with patch.dict(os.environ, {"COPILOT_DB": "/tmp/legacy.sqlite3"}, clear=True):
            with patch("manage.read_password") as prompt:
                with self.assertRaisesRegex(SystemExit, "profile-separated database runtime"):
                    manage.resetpw(Namespace(email="user@example.test"))
            prompt.assert_not_called()

    def test_importlaws_refuses_shared_database_before_opening_input(self):
        with patch.dict(os.environ, {"COPILOT_DB": "/tmp/legacy.sqlite3"}, clear=True):
            with self.assertRaisesRegex(SystemExit, "profile-separated database runtime"):
                manage.importlaws(Namespace(file="/path/that/must/not/be/opened.jsonl"))


if __name__ == "__main__":
    unittest.main()
