"""Fail when a test file is neither explicitly invoked by CI nor tracked as blocked."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / ".github" / "known_unrun_tests.txt"
WORKFLOWS = ROOT / ".github" / "workflows"


def workflow_invocations():
    commands = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        # Test steps in this repository use one-line "run:" commands. Do not
        # count a filename appearing only in a step title or YAML comment.
        commands.extend(re.findall(r"(?m)^\s*run:\s*(?!\|)(.+)$", text))
    return set(re.findall(
        r"\bpython\s+tests/(test_[A-Za-z0-9_]+\.py)\b",
        "\n".join(commands),
    ))


def known_unrun():
    entries = {}
    for line in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, reason = line.partition(":")
        if not separator:
            raise AssertionError(f"Malformed known-unrun entry: {line}")
        name, reason = name.strip(), reason.strip()
        if not name.startswith("test_") or not name.endswith(".py") or Path(name).name != name:
            raise AssertionError(f"Invalid test filename in known-unrun list: {name}")
        if name in entries:
            raise AssertionError(f"Duplicate known-unrun entry: {name}")
        entries[name] = reason
    return entries


class CiCoverageTests(unittest.TestCase):
    def test_every_test_file_runs_in_ci_or_is_tracked(self):
        invoked = workflow_invocations()
        known = known_unrun()
        orphans = []
        for path in sorted((ROOT / "tests").glob("test_*.py")):
            if path.name not in invoked and path.name not in known:
                orphans.append(path.name)
        self.assertEqual(
            orphans, [],
            "Add these to a workflow or to .github/known_unrun_tests.txt with a reason",
        )

    def test_known_unrun_list_has_no_stale_or_unexplained_entries(self):
        invoked = workflow_invocations()
        for name, reason in known_unrun().items():
            self.assertTrue(
                (ROOT / "tests" / name).is_file(),
                f"{name} no longer exists; remove it from the list",
            )
            self.assertNotIn(
                name, invoked,
                f"{name} now runs in CI; remove it from the list",
            )
            self.assertTrue(reason, f"{name} needs a reason")


if __name__ == "__main__":
    unittest.main()
