# Test Ledger — Legal for Today

This ledger is a restored evidence log. It does not retroactively certify prior tests.

| Date | Commit / scope | Command or evidence | Outcome | Classification |
|---|---|---|---|---|
| 2026-11-28 | Main baseline `60b2ebd0d2a0940c904a6ac6afb54a4ac221fcec` | GitHub source read-back: `tools/source_match_evidence.py`, `docs/STATUS.md`, issue #1903, draft PR #1902 | Source-level inspection only; tests not executed during this session | Not a test run |

## Evidence requirements
For each test execution record: exact commit SHA, supported Python/runtime, command, exit status, test count/output summary, and whether run locally or in CI. Separate static inspection, synthetic harnesses, CI results, staging acceptance, and live-provider acceptance. Never record an unexecuted test as passed.
