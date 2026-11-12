# Delivery blockers and closure register

Last reviewed: 2026-11-12
Scope: Legal Copilot release work. This register separates work that can be closed by repository changes from work that requires external execution, licensed/legal review, operational access, or real users.

## Closure policy

A task is 100% only when its acceptance criteria are met and the evidence is recorded. A code change or passing unit test alone does not establish production readiness. Do not mark legal content verified without qualified Egyptian-lawyer sign-off. Do not mark tests passed unless they were executed in the stated environment.

## Highest-priority work that can reach 100% in-repository

| Work item | Owner | Closure evidence | Current disposition |
|---|---|---|---|
| DEL/control-character rejection in Gazette source URLs | AI-1 | Validator rejects C0 and DEL; focused regression test exists | Code change merged in PR #1556; execution still unverified |
| Gazette text importer input contract and deterministic output | AI-1 | Input/schema/provenance/duplicate/error-path tests; documented CLI | Partially complete; needs full source/test audit |
| Retrieval scorer safety-status ordering | AI-1 | Known wrong/uncited/unverified/non-abstention failures always report below-target; focused tests executed | Fix proposed in PR #1560; tests not executed |
| Arabic obligation-negation unit coverage | AI-1 | English and Arabic polarity variants tested, including unrelated clauses and whitespace | Additional cases proposed in PR #1559; tests not executed |
| Benchmark evaluator data-integrity contract | AI-1 | Unlabeled data excluded, reviewer registry required, stable fingerprint, malformed input rejected | Implemented in repository; execution and integration remain unverified |
| Documentation and ownership handoff | AI-1 / AI-2 | Each known blocker has owner, acceptance evidence, and no false completion claim | This register created; update as work closes |

## External blockers: do not spend repeated effort looping

### Test execution / CI runner availability
- Current limitation: GitHub Actions runner allocation/billing has previously failed before test steps start.
- Owner: Codex / repository administrator.
- Exit criteria: execute focused tests and full suite in a clean Python 3.12 hash-locked environment; preserve command, interpreter, dependency-lock hash, exit status and test counts.
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
- #1559: Arabic negated-obligation regression cases. Test-only; not executed.
- #1560: retrieval scorer reports known safety failures as below-target even when other cohort metrics are incomplete. Tests not executed.
- #1562: delivery blocker/closure register and status linkage. Documentation-only; not tests run.
- #1563: reject empty URL fragment delimiters in Gazette source URLs. Tests not executed.
- #1565: Gazette importer operator contract. Documentation-only; source-cross-checked, no tests run.
- #1566: strict reviewer evidence URL validation. Tests not executed.
- #1556: DEL rejection in Gazette source URL; merged previously, test execution unverified.
- #1554: control-character fixture corrections; merged previously, test execution unverified.

## Next execution order
1. Finish static audits and close deterministic importer/scorer defects that have bounded acceptance criteria.
2. Complete focused unit tests and docs for those changes; keep PRs small and isolated.
3. Hand off any live answer-path, billing, database, tenant, UI or deployment change to AI-2.
4. Reserve Codex for Python 3.12 execution, dependency lock verification, adversarial security tests and production acceptance.
5. Do not tune `MIN_SCORE`, publish retrieval quality scores, or mark legal sources verified until approved labels/source evidence exist.
