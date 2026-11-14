import json
import os
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


def write_evidence_files(root, records):
    for item in records:
        for relative in item.get("evidence_paths", []):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"synthetic evidence fixture")


class DeviceBrowserAcceptanceTests(unittest.TestCase):
    def test_structural_record_is_valid_but_not_a_release_pass(self):
        result = validate_record(record())
        self.assertFalse(result["complete"])
        self.assertEqual(result["passed_checks"], 0)

    def test_malformed_untrusted_enum_values_are_reported_not_crashed(self):
        cases = (
            {"environment": []},
            {"device_class": {}},
            {"locale": []},
            {"results": {REQUIRED_RESULTS[0]: []}},
        )
        for overrides in cases:
            with self.subTest(overrides=overrides):
                value = record(**overrides)
                with self.assertRaises(EvidenceError):
                    validate_record(value)

    def test_unhashable_result_values_do_not_crash_defect_detection(self):
        value = record(results={key: "NOT_TESTED" for key in REQUIRED_RESULTS})
        value["results"][REQUIRED_RESULTS[0]] = []
        with self.assertRaisesRegex(EvidenceError, "results.installation must be PASS"):
            validate_record(value)

    def test_release_gate_requires_every_check_to_pass(self):
        value = record(results={key: "PASS" for key in REQUIRED_RESULTS},
                       evidence_paths=["artifacts/run-001/summary.json"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence_files(root, [value])
            result = validate_record(value, expected_commit=COMMIT, require_pass=True, evidence_root=root)
        self.assertTrue(result["complete"])

    def test_release_gate_rejects_not_tested_and_blocked_states(self):
        value = record(results={key: "PASS" for key in REQUIRED_RESULTS},
                       evidence_paths=["artifacts/run-001/summary.json"])
        value["results"]["keyboard_and_screen_reader"] = "BLOCKED"
        value["defect_ids"] = ["QA-123"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence_files(root, [value])
            with self.assertRaisesRegex(EvidenceError, "requires PASS"):
                validate_record(value, require_pass=True, evidence_root=root)

    def test_release_gate_requires_existing_nonempty_evidence_file(self):
        value = record(results={key: "PASS" for key in REQUIRED_RESULTS},
                       evidence_paths=["artifacts/run.json"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(EvidenceError, "evidence file is missing"):
                validate_record(value, require_pass=True, evidence_root=root)
            target = root / "artifacts/run.json"
            target.parent.mkdir()
            target.write_bytes(b"")
            with self.assertRaisesRegex(EvidenceError, "non-empty regular file"):
                validate_record(value, require_pass=True, evidence_root=root)
            target.write_bytes(b"synthetic evidence")
            self.assertTrue(validate_record(value, require_pass=True, evidence_root=root)["complete"])

    def test_release_gate_rejects_traversal_and_symlink_evidence_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            root.mkdir()
            outside = Path(directory) / "outside.txt"
            outside.write_text("outside", encoding="utf-8")
            value = record(results={key: "PASS" for key in REQUIRED_RESULTS},
                           evidence_paths=["../outside.txt"])
            with self.assertRaisesRegex(EvidenceError, "stay inside"):
                validate_record(value, require_pass=True, evidence_root=root)
            link = root / "linked.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable on this platform")
            value["evidence_paths"] = ["linked.txt"]
            with self.assertRaisesRegex(EvidenceError, "symlinks"):
                validate_record(value, require_pass=True, evidence_root=root)

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
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence_files(root, values)
            summaries = [validate_record(item, expected_commit=COMMIT, require_pass=True, evidence_root=root)
                         for item in values]
        with self.assertRaisesRegex(EvidenceError, "phone/en-US"):
            validate_release_matrix(values, summaries)

    def test_release_matrix_rejects_duplicate_device_evidence(self):
        values = [
            passing_record("desktop", "ar-EG", "130"),
            passing_record("desktop", "en-US", "131"),
            passing_record("phone", "ar-EG", "132"),
            passing_record("phone", "en-US", "133"),
        ]
        values.append(dict(values[0]))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence_files(root, values)
            summaries = [validate_record(item, expected_commit=COMMIT, require_pass=True, evidence_root=root)
                         for item in values]
        with self.assertRaisesRegex(EvidenceError, "duplicate evidence records"):
            validate_release_matrix(values, summaries)

    def test_release_matrix_rejects_reused_evidence_files(self):
        values = [
            passing_record("desktop", "ar-EG", "130"),
            passing_record("desktop", "en-US", "131"),
            passing_record("phone", "ar-EG", "132"),
            passing_record("phone", "en-US", "133"),
        ]
        values[1]["evidence_paths"] = list(values[0]["evidence_paths"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence_files(root, values)
            summaries = [validate_record(item, expected_commit=COMMIT, require_pass=True, evidence_root=root)
                         for item in values]
        with self.assertRaisesRegex(EvidenceError, "evidence paths must be unique"):
            validate_release_matrix(values, summaries)

    def test_release_matrix_rejects_mixed_commits_and_environments(self):
        values = [
            passing_record("desktop", "ar-EG", "130"),
            passing_record("desktop", "en-US", "131"),
            passing_record("phone", "ar-EG", "132"),
            passing_record("phone", "en-US", "133"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence_files(root, values)
            summaries = [validate_record(item, require_pass=True, evidence_root=root) for item in values]
            validate_release_matrix(values, summaries)
            values[3]["application_commit"] = "b" * 40
            mixed = [validate_record(item, require_pass=True, evidence_root=root) for item in values]
            with self.assertRaisesRegex(EvidenceError, "exactly one application commit"):
                validate_release_matrix(values, mixed)
            values[3]["application_commit"] = COMMIT
            values[3]["environment"] = "local"
            mixed = [validate_record(item, require_pass=True, evidence_root=root) for item in values]
            with self.assertRaisesRegex(EvidenceError, "exactly one environment"):
                validate_release_matrix(values, mixed)

    def test_cli_require_pass_rejects_one_device_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "one.json"
            value = passing_record("desktop", "ar-EG", "130")
            write_evidence_files(Path(directory), [value])
            path.write_text(json.dumps(value), encoding="utf-8")
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
            write_evidence_files(Path(directory), values)
            path.write_text(json.dumps(values), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/validate_device_browser_acceptance.py"),
                 "--input", str(path), "--expected-commit", COMMIT, "--require-pass"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"release_gate": "PASS"', result.stdout)

    def test_evidence_loader_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text(json.dumps(record()), encoding="utf-8")
            link = root / "evidence.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaisesRegex(EvidenceError, "must not be a symlink"):
                load_records(link)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_evidence_loader_rejects_fifo_without_blocking(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.fifo"
            os.mkfifo(path)
            with self.assertRaisesRegex(EvidenceError, "regular file"):
                load_records(path)

    def test_evidence_loader_rejects_oversized_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized.json"
            path.write_bytes(b" " * 5_000_001)
            with self.assertRaisesRegex(EvidenceError, "5 MB limit"):
                load_records(path)

    def test_evidence_loader_rejects_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_bytes(b'{"record_version":1,"label":"\\xff"}')
            with self.assertRaisesRegex(EvidenceError, "valid UTF-8"):
                load_records(path)

    def test_json_loader_rejects_excessive_nesting(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested.json"
            path.write_text("[" * 1100 + "0" + "]" * 1100, encoding="utf-8")
            with self.assertRaisesRegex(EvidenceError, "nesting exceeds parser limits"):
                load_records(path)

    def test_jsonl_loader_rejects_excessive_nesting(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested.jsonl"
            path.write_text("[" * 1100 + "0" + "]" * 1100 + "\\n", encoding="utf-8")
            with self.assertRaisesRegex(EvidenceError, "nesting exceeds parser limits"):
                load_records(path)

    def test_json_loader_rejects_duplicate_object_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(
                '{"record_version":1,"record_version":1}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(EvidenceError, "duplicate JSON object key"):
                load_records(path)

    def test_jsonl_loader_rejects_duplicate_object_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.jsonl"
            path.write_text(
                '{"record_version":1,"record_version":1}\\n{"record_version":1}\\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(EvidenceError, "duplicate JSON object key"):
                load_records(path)

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
