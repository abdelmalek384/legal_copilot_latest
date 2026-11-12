#!/usr/bin/env python3
"""Run every one-line Python test invocation registered in GitHub Actions workflows.

This mirrors tests/test_ci_runs_all_tests.py's workflow discovery contract while
running each discovered test module locally with the workflow's leading
NAME=value environment assignments.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
RUN_LINE = re.compile(r"(?m)^\s*run:\s*(?!\|)(.+)$")
TEST_PATH = re.compile(r"^tests/(test_[A-Za-z0-9_]+\.py)$")


def _yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def discover_test_invocations() -> list[tuple[str, tuple[tuple[str, str], ...]]]:
    invocations: set[tuple[str, tuple[tuple[str, str], ...]]] = set()
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        lines = workflow.read_text(encoding="utf-8").splitlines()
        in_jobs = False
        job_environment: dict[str, str] = {}
        reading_job_env = False
        for line in lines:
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            if indent == 0 and stripped == "jobs:":
                in_jobs = True
                continue
            if not in_jobs:
                continue
            if indent == 2 and stripped.endswith(":") and not stripped.startswith("#"):
                job_environment = {}
                reading_job_env = False
                continue
            if indent == 4 and stripped == "env:":
                reading_job_env = True
                continue
            if reading_job_env:
                if not stripped or stripped.startswith("#"):
                    continue
                if indent > 4:
                    if indent == 6 and ":" in stripped:
                        key, value = stripped.split(":", 1)
                        job_environment[key.strip()] = _yaml_scalar(value)
                    continue
                reading_job_env = False

            match_line = RUN_LINE.fullmatch(line)
            if match_line is None:
                continue
            command = match_line.group(1)
            try:
                tokens = shlex.split(command)
            except ValueError as exc:
                raise RuntimeError(
                    f"Cannot parse one-line run command in {workflow.name}: {command}"
                ) from exc
            index = 0
            overrides = dict(job_environment)
            while index < len(tokens) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[index]):
                key, value = tokens[index].split("=", 1)
                overrides[key] = value
                index += 1
            if index + 1 >= len(tokens) or tokens[index] not in {"python", "python3"}:
                continue
            match = TEST_PATH.fullmatch(tokens[index + 1])
            if match is None:
                continue
            invocations.add((match.group(1), tuple(sorted(overrides.items()))))
    return sorted(invocations, key=lambda item: (item[0], item[1]))

def main() -> int:
    invocations = discover_test_invocations()
    if not invocations:
        print("No one-line Python test invocations were discovered in .github/workflows/*.yml.", file=sys.stderr)
        return 2

    results: list[tuple[str, str, int]] = []
    for test_name, overrides in invocations:
        test_path = ROOT / "tests" / test_name
        if not test_path.is_file():
            results.append((test_name, "BLOCKED", 127))
            print(f"BLOCKED: {test_name} is referenced by CI but missing from this checkout.", file=sys.stderr)
            continue

        env = os.environ.copy()
        env.update(dict(overrides))
        # Report only variable names; never echo workflow environment values into logs.
        env_label = ", ".join(key for key, _value in overrides) or "inherited environment"
        print(f"\n==> {test_name} [{env_label}]", flush=True)
        completed = subprocess.run([sys.executable, str(test_path)], cwd=ROOT, env=env)
        status = "PASS" if completed.returncode == 0 else "FAIL"
        results.append((test_name, status, completed.returncode))
        if completed.returncode:
            print(f"FAILED: {test_name} (exit {completed.returncode})", file=sys.stderr)

    print("\n================ CI-INVOKED PYTHON TESTS ================")
    print(f"{'TEST MODULE':48} {'RESULT':10} EXIT")
    print(f"{'-' * 48} {'-' * 10} ----")
    for name, status, code in results:
        print(f"{name:48} {status:10} {code}")
    failed = [row for row in results if row[1] != "PASS"]
    print(f"Result: {len(results) - len(failed)}/{len(results)} passed.")
    if failed:
        print("The local test gate is NOT PASS.")
        return 1
    print("All CI-invoked Python test modules passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
