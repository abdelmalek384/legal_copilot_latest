import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.validate_device_browser_acceptance import (
    EvidenceError, REQUIRED_RESULTS, load_records, validate_record, validate_release_matrix,
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
        "device_class": "desktop",
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


def passing_record(device_class, locale, suffix):
    return record(
        device_class=device_class,
        locale=locale,
        device=f"Synthetic {device_class} {suffix}",
        browser_and_version=f"Chromium {suffix}",
        viewport=f"{1440 if device_class == 'desktop' else 390}x900",
        results={key: "PASS" for key in REQUIRED_RESULTS},
        evidence_paths=[f"artifacts/{device_class}-{locale}.json"],
    )


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

    def test_release_matrix_requires_desktop_and_phone_in_both_locales(self):
        values = [
            passing_record("desktop", "ar-EG", "130"),
            passing_record("desktop", "en-US", "131"),
            passing_record("phone", "ar-EG", "132"),
        ]
        summaries = [validate_record(item, expected_commit=COMMIT, require_pass=True) for item in values]
        with self.assertRaisesRegex(EvidenceError, "phone/en-US"):
            validate_release_matrix(values, summaries)

    def test_release_matrix_rejects_mixed_commits_and_environments(self):
        values = [
            passing_record("desktop", "ar-EG", "130"),
            passing_record("desktop", "en-US", "131"),
            passing_record("phone", "ar-EG", "132"),
            passing_record("phone", "en-US", "133"),
        ]
        summaries = [validate_record(item, require_pass=True) for item in values]
        validate_release_matrix(values, summaries)
        values[3]["application_commit"] = "b" * 40
        mixed = [validate_record(item, require_pass=True) for item in values]
        with self.assertRaisesRegex(EvidenceError, "exactly one application commit"):
            validate_release_matrix(values, mixed)
        values[3]["application_commit"] = COMMIT
        values[3]["environment"] = "local"
        mixed = [validate_record(item, require_pass=True) for item in values]
        with self.assertRaisesRegex(EvidenceError, "exactly one environment"):
            validate_release_matrix(values, mixed)

    def test_cli_require_pass_rejects_one_device_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "one.json"
            path.write_text(json.dumps(passing_record("desktop", "ar-EG", "130")), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/validate_device_browser_acceptance.py"),
                 "--input", str(path), "--expected-commit", COMMIT, "--require-pass"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("release device matrix is incomplete", result.stderr)

    def test_cli_require_pass_accepts_complete_four_cell_matrix(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix.json"
            values = [
                passing_record("desktop", "ar-EG", "130"),
                passing_record("desktop", "en-US", "131"),
                passing_record("phone", "ar-EG", "132"),
                passing_record("phone", "en-US", "133"),
            ]
            path.write_text(json.dumps(values), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/validate_device_browser_acceptance.py"),
                 "--input", str(path), "--expected-commit", COMMIT, "--require-pass"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"release_gate": "PASS"', result.stdout)

    def test_jsonl_and_duplicate_identity_handling(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            path.write_text(json.dumps(record()) + "\n", encoding="utf-8")
            self.assertEqual(len(load_records(path)), 1)
            path.write_text(json.dumps(record()) + "\n" + json.dumps(record()) + "\n", encoding="utf-8")
            rows = load_records(path)
            identities = [(x["application_commit"], x["environment"], x["locale"],
                           x["device_class"], x["device"], x["browser_and_version"], x["viewport"])
                          for x in rows]
            self.assertNotEqual(len(identities), len(set(identities)))


if __name__ == "__main__":
    unittest.main()
