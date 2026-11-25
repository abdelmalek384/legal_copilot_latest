# AI-2 manual stabilization checkpoint — 25 November 2026

**Status:** initial inspection and source review only. No runtime, browser, or repository tests executed by this checkpoint. This is not pilot approval.

## Access and baseline
- Repository: `abdelmalek384/legal_copilot_latest`; mainline inspected through authenticated GitHub file operations.
- Latest commit search result: `d20da92b38960b80516f86cd2daf5dd73904f718` (search result snapshot, not a locally checked-out HEAD).
- Open PR search returned no open PRs.
- Local checkout is unavailable: clone attempt failed resolving `github.com`. The local environment has Python 3.13.5, not the documented Python 3.12 test runtime.
- GitHub Actions intentionally not used because runner billing is unavailable.

## Static source review
- Reviewed portions of `tenant_catalog.py`, `tenant_storage.py`, `tests/test_tenant_catalog.py`, `tests/test_tenant_storage.py`, and `tests/test_tenant_database_preflight.py`.
- Existing safeguards include catalog/firm binding checks, strict database filename mapping, symlink and hard-link checks, SQLite sidecar checks, restrictive file mode checks, post-open revalidation, and revocation of cached connections on validation failure.
- Existing tests cover several synthetic path replacement, symlink, hard-link, permission, and firm-binding scenarios; they are not executed here.
- The pathname-to-SQLite-open race remains a documented residual risk. This review does not establish exploitability or closure. Restrict tenant storage write access to the application service account and administrators.
- No source changes or test results are claimed from this checkpoint.

## AI-2 progress (conservative implementation/evidence estimates)
| Workstream | Current | Evidence and outstanding |
|---|---:|---|
| Backend and existing workflows | 25% | Status and code source review only; CRUD journeys and persistence not run |
| Frontend and usability | 20% | Existing accessibility source contracts; browser acceptance not run |
| Mobile and Arabic/English UI | 15% | No RTL/LTR viewport acceptance |
| Security and tenant isolation | 30% | Existing hardening inspected; adversarial execution and two-firm acceptance outstanding |
| Documents and file handling | 30% | Existing safeguards documented; full upload/review/download journey not run |
| Deployment, backup and recovery | 15% | Operational documents exist; restore rehearsal outstanding |
| Local testing and regression | 5% | No tests run in this checkpoint |
| **Overall AI-2 assignment** | **20%** | Initial inspection; no runtime acceptance |

No completion percentage is increased merely because code or documentation exists.

## Evidence produced
- Repository status and blockers files inspected.
- Static code/test inspection of tenant catalog and tenant storage routing.
- No files changed; no commits or PRs created by AI-2 in this checkpoint.

## Next practical execution requirement
A repository checkout and supported runtime are required to execute the existing test modules, modify application code safely, verify focused regressions, and perform browser/two-firm/restore acceptance. Do not repeatedly retry the blocked clone or CI. Continue source inspection only where it can identify a concrete, reviewable issue; do not make untested security-sensitive edits or claim runtime validation.


## Follow-up static review (same date)
- Reviewed README local-validation instructions, `scripts/security_regression_check.sh`, `scripts/local_release_check.sh`, `tools/run_local_test_suite.py`, `tests/test_ci_runs_all_tests.py`, `docs/STATUS.md`, and `docs/BLOCKERS.md` through repository file access.
- The local runner is explicitly gated to Python 3.12 and mirrors one-line test invocations with job-level environment assignments. The security matrix is a curated list and includes missing-file reporting; the release check distinguishes BLOCKED from PASS and includes restore-drill, dependency, static-analysis, and compose checks.
- This confirms the intended manual test pathway, but cannot validate its execution, coverage completeness, or whether current modules all pass. No attempt was made to run it without a checkout or compatible environment.
- Reconfirmed the release remains NOT READY, with actual two-firm authorization acceptance, browser/RTL checks, and witnessed restore evidence still open. These require an execution environment/operational witness and are not closed by source review.
- This follow-up produced review evidence only; no implementation/test percentages are raised.


## Follow-up continuation — identity and firm-boundary review (25 November 2026)

- Continued with a source-only review rather than retrying the unavailable checkout or GitHub Actions. Inspected the separate-runtime authentication path, CSRF/Origin checks, firm-context resolution and switching, MFA policy gating, case authorization helper, and the existing focused regression suites.
- Confirmed that `tests/test_app_separate_database_runtime.py` currently defines 123 separate-runtime regression test methods, including synthetic cross-firm denial, stale-membership revocation, case-child/task isolation, document/original-file isolation, export boundaries, audit rollback, and firm lifecycle coverage. This is an inventory count only; none of those tests were executed in this continuation.
- Inspected `tests/test_firm_security_policy.py` coverage for per-firm MFA, multi-firm policy switching, and CSRF/Origin rejection. Existing test source is not runtime evidence.
- Found a documentation drift in `docs/identity_firm_membership_contract.md`: its closing text still described a shared-database runtime and unimplemented tenant routing, contradicting the current separate control-plane / per-firm tenant / shared-corpus architecture. Updated the document to preserve its historical design rationale, point to current implementation entry points, and distinguish ongoing operational acceptance from pre-implementation design decisions.
- Documentation correction committed directly to `main`: `1e7e4f0fffbdf721804aaa1a3dc6e5de3e7a45f8`. GitHub read-back verified the updated blob `595ec23ea276dc1a7bc8c9141be748dd90064dc3`.
- No application code, schema, migration, tenant data, or AI-1 retrieval/evidence logic changed. No test, runtime, browser, mobile, deployment, backup/restore, or security acceptance pass is claimed.

### Progress accounting

| Workstream | Previous | Current | Change | Basis |
|---|---:|---:|---:|---|
| Backend and existing workflows | 25% | 25% | 0 pp | Source review only; no workflow execution |
| Frontend and usability | 20% | 20% | 0 pp | No browser execution |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport execution |
| Security and tenant isolation | 30% | 30% | 0 pp | Source/test inventory only; adversarial execution outstanding |
| Documents and file handling | 30% | 30% | 0 pp | No upload/review/download runtime journey |
| Deployment, backup and recovery | 15% | 15% | 0 pp | No deployment or restore rehearsal |
| Local testing and regression | 5% | 5% | 0 pp | No repository tests executed |
| **Overall AI-2 assignment** | **20%** | **20%** | **0 pp** | One stale architecture document corrected; no runtime acceptance evidence added |

The narrow documentation correction is complete, but it does not justify raising the overall assignment estimate. The checkout/network and Python 3.12 runtime constraints remain; no further attempt was made to repeat those blocked operations.
