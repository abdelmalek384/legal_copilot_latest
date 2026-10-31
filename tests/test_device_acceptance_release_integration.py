import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from tools.production_release_gate import _evaluate_device_acceptance
from tools.validate_device_browser_acceptance import REQUIRED_RESULTS


COMMIT = "a" * 40


def evidence_record(device_class, locale, suffix):
    return {
        "record_version": 1,
        "tested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "application_commit": COMMIT,
        "environment": "staging",
        "os_and_build": "Synthetic OS build",
        "device": f"Synthetic {device_class} {suffix}",
        "device_class": device_class,
        "browser_and_version": f"Chromium {suffix}",
        "locale": locale,
        "viewport": "1440x900" if device_class == "desktop" else "390x844",
        "network": "online and offline",
        "tester_role": "synthetic acceptance tester",
        "results": {key: "PASS" for key in REQUIRED_RESULTS},
        "defect_ids": [],
        "evidence_paths": [f"restricted-evidence/{device_class}-{locale}.json"],
        "notes": "Synthetic fixture only; no manual device test was performed.",
    }


def complete_matrix():
    return [
        evidence_record("desktop", "ar-EG", "130"),
        evidence_record("desktop", "en-US", "131"),
        evidence_record("phone", "ar-EG", "132"),
        evidence_record("phone", "en-US", "133"),
    ]


def write_manifest(path, records):
    for record in records:
        for relative in record.get("evidence_paths", []):
            evidence = path.parent / relative
            evidence.parent.mkdir(parents=True, exist_ok=True)
            evidence.write_bytes(b"synthetic evidence fixture")
    path.write_text(json.dumps(records), encoding="utf-8")


class DeviceAcceptanceReleaseIntegrationTests(unittest.TestCase):
    def test_missing_evidence_blocks(self):
        result = _evaluate_device_acceptance(None, COMMIT)
        self.assertFalse(result["ready"])
        self.assertIn("not configured", result["error"])

    def test_missing_or_invalid_release_commit_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            write_manifest(path, complete_matrix())
            result = _evaluate_device_acceptance(path, "short-sha")
        self.assertFalse(result["ready"])
        self.assertIn("full 40-character", result["error"])

    def test_wrong_commit_blocks(self):
        records = complete_matrix()
        for record in records:
            record["application_commit"] = "b" * 40
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            write_manifest(path, records)
            result = _evaluate_device_acceptance(path, COMMIT)
        self.assertFalse(result["ready"])
        self.assertIn("does not match expected commit", result["error"])

    def test_incomplete_matrix_blocks(self):
        records = complete_matrix()[:-1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            write_manifest(path, records)
            result = _evaluate_device_acceptance(path, COMMIT)
        self.assertFalse(result["ready"])
        self.assertIn("matrix is incomplete", result["error"])

    def test_non_pass_result_blocks(self):
        records = complete_matrix()
        records[0]["results"]["keyboard_and_screen_reader"] = "BLOCKED"
        records[0]["defect_ids"] = ["QA-101"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            write_manifest(path, records)
            result = _evaluate_device_acceptance(path, COMMIT)
        self.assertFalse(result["ready"])
        self.assertIn("requires PASS", result["error"])

    def test_complete_matrix_for_exact_commit_passes_structural_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            write_manifest(path, complete_matrix())
            result = _evaluate_device_acceptance(path, COMMIT)
        self.assertTrue(result["ready"], result["error"])
        self.assertEqual(result["records_validated"], 4)
        self.assertEqual(result["application_commit"], COMMIT)
        self.assertEqual(result["environment"], "staging")


if __name__ == "__main__":
    unittest.main()
