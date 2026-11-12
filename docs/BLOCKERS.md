# Delivery blockers and closure register

Last reviewed: 2026-11-13
Scope: Legal Copilot release work. This register separates work that can be closed by repository changes from work that requires external execution, licensed/legal review, operational access, or real users.

## Closure policy

A task is 100% only when its acceptance criteria are met and the evidence is recorded. A code change or passing unit test alone does not establish production readiness. Do not mark legal content verified without qualified Egyptian-lawyer sign-off. Do not mark tests passed unless they were executed in the stated environment.

## Highest-priority work that can reach 100% in-repository

| Work item | Owner | Closure evidence | Current disposition |
|---|---|---|---|
| DEL/control-character rejection in Gazette source URLs | AI-1 | Validator rejects C0 and DEL; focused regression test exists | C0/DEL, fragment delimiters and backslashes rejected; importer changes merged in #1556/#1563; focused tests still unexecuted |
| Gazette text importer input contract and deterministic output | AI-1 | Input/schema/provenance/duplicate/error-path tests; documented CLI | Importer and operator contract merged in #1563/#1567; source-reviewed, full focused tests still unexecuted |
| Retrieval scorer safety-status ordering | AI-1 | Known wrong/uncited/unverified/non-abstention failures always report below-target; focused tests executed | Fix merged in #1560 and carried with URL hardening in #1566; focused tests still unexecuted |
| Arabic obligation-negation unit coverage | AI-1 | English and Arabic polarity variants tested, including unrelated clauses and whitespace | Additional Arabic polarity/whitespace cases merged in #1559; tests still unexecuted; live answer-path integration remains open under #1561 |
| Benchmark evaluator data-integrity contract | AI-1 | Unlabeled data excluded, reviewer registry required, stable fingerprint, malformed input rejected | Implemented in repository; execution and integration remain unverified |
| Arabic evaluation question inventory | AI-1 | At least 100 unique formal/colloquial Egyptian Arabic drafts, uniform schema, all unreviewed and answer fields empty | 120 drafts (59 general + 61 labour) merged in #1570; static JSONL/schema check complete; lawyer answer-key approval and scoring remain external |
| Documentation and ownership handoff | AI-1 / AI-2 | Each known blocker has owner, acceptance evidence, and no false completion claim | Register merged in #1562 and refreshed in this update; operational blockers remain open |

## External blockers: do not spend repeated effort looping

### Test execution / CI runner availability
- Current limitation: GitHub Actions runner allocation/billing has previously failed before test steps start.
- Owner: Codex / repository administrator.
- Exit criteria: execute focused tests and full suite in a clean Python 3.12 hash-locked environment; preserve command, interpreter, dependency-lock hash, exit status and test counts.
- Exact-head recheck for reviewer-URL/scorer change head `ef90b56ed489be214150f1b86dac0930d814e7b8` on 2026-11-12: Tests run `43252117918`, dependency audit `43252117654`, CodeQL `43252117717`, and browser acceptance `43252117642` all failed before any job step. The inspected jobs returned empty step lists (0 executed steps); this is runner/service allocation evidence, not a code-test failure or pass.
- Until then: PR source review is not a test pass.

### Python 3.12 dependency lock
- Related PR: #1490 (recheck current PR diff before acting; title alone does not establish that the lockfile is correct).
- Owner: Codex.
- Exit criteria: regenerate lock using pinned pip-tools, include authentic hashes, install successfully from lock in a clean environment, and run import/startup plus tests. Never invent hashes.

### Live negated-obligation answer guard
- Related issue: #1561.
- Owner: AI-2 (answer-serving path); Codex for executable integration tests.
- Finding: helper and unit tests exist, but no call site in the default-branch answer path was found during the 2026-11-12 source search.
- Exit criteria: invoke narrow guard at final answer boundary; block/regenerate/abstain on polarity conflict; API-level tests cover English and Arabic negative/positive reversals, faithful negatives, and unrelated clauses.

### Billing / payment provider
- Owner: AI-2 / account owner.
- Exit criteria: sandbox success/failure, duplicate webhook idempotency, invalid signature rejection, cancellation, expired subscription, invoice creation, firm isolation, and audit evidence. Do not infer billing readiness from UI implementation.

### Tenant isolation / production data safety
- Owner: AI-2 and Codex.
- Exit criteria: adversarial cross-firm access tests across cases, documents, sessions, exports, search, background jobs and audit logs; backup/restore drill; deployment secrets and persistent storage review.

### Egyptian legal authority and counsel validation
- Owner: qualified Egyptian lawyer / legal content owner.
- Exit criteria: compare against authenticated Official Gazette source, record amendments/currentness/corrigenda, validate article text and citations, sign off each source/article scope.
- Labour Law No. 14/2025 comparison remains provisional. Preserve `verified=0`; machine comparison is not legal verification.

### Real lawyer pilot
- Owner: product owner / AI-2.
- Exit criteria: three firms complete unaided onboarding in under 15 minutes, use on mobile, and demonstrate owner-visible usage; later gate remains five firms using weekly and two willing to pre-pay.
- This cannot be completed by repository edits alone.

## Current AI-1 pull requests

- Open AI-1 PRs: #1576 (fixture corrections), #1577 (cloud signed-URL query filtering), and #1578 (provenance metadata validation; depends on #1577). All three remain unmerged and require Python 3.12 focused test execution before validation can be claimed.
- #1559 — merged Arabic negated-obligation regression coverage; tests unexecuted.
- #1560 — merged retrieval scorer safety-status ordering fix; tests unexecuted.
- #1562 — merged delivery blocker/closure register.
- #1563 — merged Gazette source URL rejection for empty fragment delimiters and backslashes; tests unexecuted.
- #1566 — merged strict reviewer-evidence URL validation, including backslash rejection; tests unexecuted.
- #1567 — merged Gazette text importer operator contract and status linkage.
- #1556 and #1554 — previously merged; test execution remains unverified.
- #1561 remains an open AI-2 integration issue: the negation helper must be invoked at the live final-answer boundary.

## Next execution order
1. Finish static audits and close deterministic importer/scorer defects that have bounded acceptance criteria.
2. Complete focused unit tests and docs for those changes; keep PRs small and isolated.
3. Hand off any live answer-path, billing, database, tenant, UI or deployment change to AI-2.
4. Reserve Codex for Python 3.12 execution, dependency lock verification, adversarial security tests and production acceptance.
5. Do not tune `MIN_SCORE`, publish retrieval quality scores, or mark legal sources verified until approved labels/source evidence exist.


## Release-gate benchmark inventory follow-up — 2026-11-13

- The default `tools/production_release_gate.py` benchmark is `tests/legal_eval/multi_area_questions.draft.jsonl`. Its draft inventory previously contained 94 questions, below the gate's configured minimum of 100 even before counsel review.
- The inventory and lawyer worksheet have been expanded to 100 questions across the same ten practice areas. This removes the structural count shortfall only; all 100 remain unreviewed and cannot satisfy the release gate until counsel supplies approved answers, dates, source/pin citations and reviewer evidence.
- Codex must execute the focused inventory/retrieval tests and full suite in the clean Python 3.12 locked environment. This branch has not been runtime-tested.


## Evaluation inventory distinction — 2026-11-13

- The production release gate consumes the separate 100-row `multi_area_questions.draft.jsonl` queue (PR #1573), not the 120-row general-plus-labour inventory.
- The 120 rows are 59 general seed questions plus 61 Labour Law draft questions. The 58-row `labour_law_14_2025_provisional_review_questions.draft.jsonl` is another separate provisional review queue. File counts can overlap; they are not a deduplicated unique-question total.
- The release-gate queue now meets its structural 100-row minimum, but still has zero lawyer-approved questions. The 100-approved-question release criterion, 10-practice-area coverage from reviewed rows, answer keys, source/pin-cite checks and approved reviewer evidence remain external counsel-dependent blockers.


## Current AI-1 PR validation checkpoint — 2026-11-13

- #1576 head `81f90fc13b9843df7f4af5e1ebb7b5441153927f`: Tests workflow run `43325788669` failed before exposing any job steps (`steps: null`).
- #1577 head `a745b35913e155c3608c86ebab4e763dac285500`: Tests workflow run `43326626506` failed before exposing any job steps (`steps: null`).
- #1578 head `89e5bdac8fa1f11571bf70b1087b7a6ae56b89ad`: Tests workflow run `43327265469` failed before exposing any job steps (`steps: null`).
- These are runner/service execution failures, not code-test failures or passes. Local Python 3.12 hash-locked validation is the next usable path.
- During static review of #1578, explicit `source_reference: null` was found to bypass the stated non-empty-string rule. The PR branch was corrected and a regression case added; the revised head has not been runtime-tested.
- Merge order remains #1577 before #1578. #1576 is independent. Do not merge these as validated until the focused Python 3.12 tests execute successfully.
