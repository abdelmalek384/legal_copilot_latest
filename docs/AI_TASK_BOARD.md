# AI Task Board — Legal for Today

Checkpoint: 2026-11-28. Continuity baseline merged in #2048 (`2a16454`). Estimates are task-oriented, not release readiness.

| Priority | Task | Status | Next acceptance |
|---|---|---|---|
| P0 | #1903 source-matched corpus adapter/retrieval integration | <escape>0% implementation in this session</escape>; target identified | Exact evidence package bound to version/source; candidate query isolated to gated test-firm; synthetic regressions; Python 3.12 tests |
| P0 | #1902 source-status classifier dependency | Draft/unmerged | Review exact-head tests/CI and earlier blockers before integration |
| P0 | Tenant/storage security acceptance | Outstanding | Supported runtime, exact regression, live adapter/recovery evidence |
| P0 | Legal rights, authenticity, status and lawyer review | Outstanding | Explicit rights and reviewer evidence; lawyer verification 0 |
| P1 | MFA/SMTP/staging acceptance | Outstanding | Real staging acceptance |
| P1 | Browser/accessibility/two-firm acceptance | Outstanding | Exact-head browser suite and manual firm workflow |
| P1 | Corpus coverage/provenance report | Outstanding | Reconcile corpus scope and provenance |

## Operating rules
- Source read-back/static review is not test execution.
- Record SHA, runtime, command, outcome and execution context.
- Do not loosen verified-corpus or tenant-isolation policy.
- Avoid main writes; branch and PR integration.


## 2026-11-28 AI-2 continuation checkpoint

- Re-read continuity files and #1903 issue; source-match adapter, migrations 0005/0006 and integration boundary confirmed.
- Repeated shallow clone attempt failed DNS (`Could not resolve host: github.com`); no code or tests executed.
- Added `docs/ai2_1903_integration_contract.md` on branch `ai2-1903-integration-contract`, documenting exact packet-binding, test-firm isolation, fail-closed retrieval and acceptance requirements. Design documentation only; no implementation/validation claim.
- Candidate serving remains disabled/fail-closed; verified/legal flags unchanged; Law 14/2025 remains rights-blocked.
