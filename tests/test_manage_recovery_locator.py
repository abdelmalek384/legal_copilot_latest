import json
import tempfile
import unittest
from pathlib import Path

from manage import _read_recovery_locator


class RecoveryLocatorReadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_reads_valid_bounded_locator_json(self):
        path = self.root / "locator.json"
        path.write_text(json.dumps({"bucket": "recovery", "version_id": "v1"}), encoding="utf-8")
        self.assertEqual(
            _read_recovery_locator(path),
            {"bucket": "recovery", "version_id": "v1"},
        )

    def test_rejects_oversized_locator(self):
        path = self.root / "large.json"
        path.write_bytes(b" " * 16385)
        with self.assertRaisesRegex(SystemExit, "could not be read safely"):
            _read_recovery_locator(path)

    def test_rejects_non_object_locator(self):
        path = self.root / "array.json"
        path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "could not be read safely"):
            _read_recovery_locator(path)

    @unittest.skipUnless(hasattr(Path, "symlink_to"), "symlinks are unavailable")
    def test_rejects_symlinked_locator(self):
        target = self.root / "target.json"
        target.write_text('{"bucket":"recovery"}', encoding="utf-8")
        link = self.root / "locator-link.json"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")
        with self.assertRaisesRegex(SystemExit, "could not be read safely"):
            _read_recovery_locator(link)


if __name__ == "__main__":
    unittest.main()
