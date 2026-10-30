"""Fail when a test file is neither executed by CI nor explicitly tracked as blocked."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / ".github" / "known_unrun_tests.txt"
WORKFLOWS = ROOT / ".github" / "workflows"


def workflow_text():
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(WORKFLOWS.glob("*.yml"))
    )


def known_unrun():
    entries = {}
    for line in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, reason = line.partition(":")
        if not separator:
            raise AssertionError(f"Malformed known-unrun entry: {line}")
        entries[name.strip()] = reason.strip()
    return entries


class CiCoverageTests(unittest.TestCase):
    def test_every_test_file_runs_in_ci_or_is_tracked(self):
        text = workflow_text()
        known = known_unrun()
        orphans = []
        for path in sorted((ROOT / "tests").glob("test_*.py")):
            if path.name not in text and path.name not in known:
                orphans.append(path.name)
        self.assertEqual(
            orphans, [],
            "Add these to a workflow or to .github/known_unrun_tests.txt with a reason",
        )

    def test_known_unrun_list_has_no_stale_or_unexplained_entries(self):
        text = workflow_text()
        for name, reason in known_unrun().items():
            self.assertTrue(
                (ROOT / "tests" / name).is_file(),
                f"{name} no longer exists; remove it from the list",
            )
            self.assertNotIn(
                name, text,
                f"{name} now runs in CI; remove it from the list",
            )
            self.assertTrue(reason, f"{name} needs a reason")


if __name__ == "__main__":
    unittest.main()
