import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.validate_device_browser_acceptance import (
    EvidenceError, REQUIRED_RESULTS, load_records, validate_record,
)

COMMIT = "a" * 40


def record(**overrides):
    value = {
        "record_version": 1,
        "tested_at": "2026-10-31T12:00:00+02:00",
        "application_commit": COMMIT,
        "environment": "staging",
        "os_and_build": "Ubuntu 24.04",
        "device": "Synthetic browser runner",
        "browser_and_version": "Chromium 130",
        "locale": "ar-EG",
        "viewport": "1440x900",
        "network": "online and offline",
        "tester_role": "synthetic firm administrator",
        "results": {key: "NOT_TESTED" for key in REQUIRED_RESULTS},
        "defect_ids": [],
        "evidence_paths": [],
        "notes": "Synthetic fixture; no tests were performed.",
    }
    value.update(overrides)
    return value


class DeviceBrowserAcceptanceTests(unittest.TestCase):
    def test_structural_record_is_valid_but_not_a_release_pass(self):
        result = validate_record(record())
        self.assertFalse(result["complete"])
        self.assertEqual(result["passed_checks"], 0)

    def test_release_gate_requires_every_check_to_pass(self):
        value = record(results={key: "PASS" for key in REQUIRED_RESULTS},
                       evidence_paths=["artifacts/run-001/summary.json"])
        self.assertTrue(validate_record(value, expected_commit=COMMIT, require_pass=True)["complete"])

    def test_release_gate_rejects_not_tested_and_blocked_states(self):
        value = record(results={key: "PASS" for key in REQUIRED_RESULTS},
                       evidence_paths=["artifacts/run-001/summary.json"])
        value["results"]["keyboard_and_screen_reader"] = "BLOCKED"
        value["defect_ids"] = ["QA-123"]
        with self.assertRaisesRegex(EvidenceError, "requires PASS"):
            validate_record(value, require_pass=True)

    def test_rejects_naive_timestamp_and_short_commit(self):
        value = record(tested_at="2026-10-31T12:00:00", application_commit="abc")
        with self.assertRaises(EvidenceError):
            validate_record(value)

    def test_rejects_wrong_commit(self):
        with self.assertRaisesRegex(EvidenceError, "does not match"):
            validate_record(record(), expected_commit="b" * 40)

    def test_pass_requires_evidence_and_failure_requires_defect_reference(self):
        value = record(results={key: "PASS" for key in REQUIRED_RESULTS})
        with self.assertRaisesRegex(EvidenceError, "evidence path"):
            validate_record(value)
        value["evidence_paths"] = ["artifacts/run.json"]
        value["results"]["installation"] = "FAIL"
        with self.assertRaisesRegex(EvidenceError, "defect_ids"):
            validate_record(value)

    def test_jsonl_and_duplicate_identity_handling(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            path.write_text(json.dumps(record()) + "\n", encoding="utf-8")
            self.assertEqual(len(load_records(path)), 1)
            path.write_text(json.dumps(record()) + "\n" + json.dumps(record()) + "\n", encoding="utf-8")
            rows = load_records(path)
            identities = [(x["application_commit"], x["environment"], x["locale"]) for x in rows]
            self.assertNotEqual(len(identities), len(set(identities)))


if __name__ == "__main__":
    unittest.main()
