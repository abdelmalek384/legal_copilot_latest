from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "start_mac.command"


class MacLauncherPortContractTests(unittest.TestCase):
    def test_launcher_keeps_localhost_binding_and_default_port(self):
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn('COPILOT_PORT="${COPILOT_PORT:-8000}"', text)
        self.assertIn('--host 127.0.0.1 --port "${COPILOT_PORT}"', text)
        self.assertIn('http://127.0.0.1:${COPILOT_PORT}', text)

    def test_launcher_validates_port_range_before_server_start(self):
        text = LAUNCHER.read_text(encoding="utf-8")
        validation = '(( COPILOT_PORT < 1 || COPILOT_PORT > 65535 ))'
        self.assertIn(validation, text)
        self.assertIn('COPILOT_PORT must be a number between 1 and 65535.', text)
        self.assertLess(text.index(validation), text.index('python -m uvicorn app:app'))


if __name__ == "__main__":
    unittest.main()
