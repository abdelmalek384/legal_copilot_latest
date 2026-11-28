import json
import os
import tempfile
import unittest
from pathlib import Path

from tools.seed_legal_candidates import _MAX_JSON_INPUT_BYTES, _read_json_input


class SeedLegalCandidatesInputTests(unittest.TestCase):
    def test_loads_json_object_and_array(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text('{"items":[1,2]}', encoding="utf-8")
            self.assertEqual(_read_json_input(path, "input"), {"items": [1, 2]})

    def test_rejects_duplicate_keys_at_nested_depth(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text('{"nested":{"key":1,"key":2}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                _read_json_input(path, "input")

    def test_rejects_invalid_utf8_and_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(b"\xff")
            with self.assertRaisesRegex(ValueError, "UTF-8"):
                _read_json_input(path, "input")
            path.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "valid JSON"):
                _read_json_input(path, "input")

    def test_rejects_oversized_regular_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(b"x" * (_MAX_JSON_INPUT_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "4 MiB"):
                _read_json_input(path, "input")

    def test_rejects_symlink(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "unreadable or unsafe"):
                _read_json_input(link, "input")

    def test_rejects_non_regular_file_without_blocking(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO unavailable")
        with tempfile.TemporaryDirectory() as directory:
            fifo = Path(directory) / "input.fifo"
            os.mkfifo(fifo)
            with self.assertRaisesRegex(ValueError, "regular file"):
                _read_json_input(fifo, "input")


if __name__ == "__main__":
    unittest.main()
