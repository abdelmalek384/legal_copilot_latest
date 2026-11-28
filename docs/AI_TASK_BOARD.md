# AI Task Board — Legal for Today

Checkpoint: 2026-11-28. This board restores a concise handoff; it is not a substitute for issue/PR status or verified test results.

| Priority | Task | Status | Acceptance / next action |
|---|---|---|---|
| P0 | #1903 exact-version source-match evidence retrieval integration | Blocked/in progress | Schema, version-bound adapter package, isolated dedicated test-firm search scope, synthetic fail-closed tests, Python 3.12 exact-head tests and isolation acceptance |
| P0 | #1902 classifier prerequisite | Draft / not integrated | Review exact head and CI; classifier alone is not retrieval implementation |
| P0 | Tenant isolation and secure original-file storage acceptance | Outstanding | Supported-runtime regression and live adapter/recovery acceptance; no claims based on source read-back alone |
| P0 | Lawyer review, source authenticity/currentness and reuse rights | Outstanding | Qualified reviewer evidence and explicit permission records; lawyer verification remains 0 |
| P1 | MFA, SMTP/reminder and release acceptance | Outstanding | Staging acceptance evidence |
| P1 | UI/browser accessibility and manual usability acceptance | Outstanding | Exact-head browser suite and manual firm acceptance |
| P1 | Corpus coverage/provenance reporting | Outstanding | Reconcile coverage and provenance against agreed pilot scope |

## Working rules
- Avoid duplicating existing tests or running expensive suites without a concrete reason.
- Record command, commit SHA, runtime, and outcome for executed tests; source inspection is not test execution.
- Fail closed. Do not relax verified-corpus or tenant-isolation gates to make candidate retrieval work.
- Work on branches and PRs; avoid direct writes to shared main.
