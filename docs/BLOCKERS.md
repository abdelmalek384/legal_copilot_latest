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
| Legal evaluation report evidence-path integrity | AI-1 | Scorer, release-gate and legal-readiness report outputs cannot overwrite candidate/run/reviewer/acceptance inputs, including hard links | 100% merged (#1593); regression tests committed but not executed |
| Legal report output-path integrity | AI-1 | JSON/Markdown report destinations cannot alias their database/register inputs or each other through direct paths, symlinks or hard links | 100% merged for legal-source review queue, corpus inventory, acquisition readiness, amendment relationships and Arabic OCR report paths (#1599); tests not run |
| Remaining legal audit output-path integrity | AI-1 | Canonical OCR evaluator, article-row audit and corpus database audit cannot overwrite their inputs through direct paths, symlinks or hard links | This branch adds guards and CLI regressions; tests committed but not executed |
| Additional legal CLI report-path integrity | AI-1 | Corpus/reference comparison, Labour Law evidence-card report, and structured legal-draft output cannot overwrite source inputs or inventory manifests | This branch adds direct-path, symlink and hard-link guards plus CLI regressions; tests not run |

## External blockers: do not spend repeated effort looping

### Test execution / CI runner availability
- Current limitation: GitHub Actions runner allocation/billing has previously failed before test steps start.
- Owner: Codex / repository administrator.
- Exit criteria: execute focused tests and full suite in a clean Python 3.12 hash-locked environment; preserve command, interpreter, dependency-lock hash, exit status and test counts.
- Exact-head recheck for reviewer-URL/scorer change head `ef90b56ed489be214150f1b86dac0930d814e7b8` on 2026-11-12: Tests run `43252117918`, dependency audit `43252117654`, CodeQL `43252117717`, and browser acceptance `43252117642` all failed before any job step. The inspected jobs returned empty step lists (0 executed steps); this is runner/service allocation evidence, not a code-test failure or pass.
- Until then: PR source review is not a test pass.

### Python 3.12 dependency lock
- Related PR #1490 was inspected on 2026-11-13: it changes only `requirements.txt` (`boto3>=1.43.123` to `>=1.43.125`) and does not update `requirements-py312.lock`. Do not merge it as a completed dependency update until the lock is regenerated with authentic hashes and installed successfully in a clean Python 3.12 environment.
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

## Recent AI-1 and Legal Research integration

- #1576 — merged fixture corrections for the Gazette importer and Arabic retrieval scorer.
- #1577 — merged AWS/GCP signed-URL companion-parameter rejection.
- #1578 — superseded by current-main PR #1584 and closed; the replacement adds provenance control-character rejection and requires any explicitly supplied `source_reference` to be a non-empty string.
- #1580 — merged retrieval-evaluator malformed-enum and ambiguous evidence-URL validation.
- #1581 — merged fail-closed device-acceptance metadata validation.
- #1582 — merged the Figma-aligned Legal Research/Document Intelligence workspace onto current `main`, preserving the 18 newer main commits by carrying only the 16 changed files. The older #1564 branch was closed as superseded.
- #1583 — merged retrieval scorer rejection of non-object question/run rows.
- #1584 — merged Gazette provenance metadata hardening on current `main`.
- #1558 and #1543 — closed as superseded by #1582; their relevant classification/document-intelligence work is included in the integrated workspace.
- #1561 is closed after confirming the narrow guard is called in `app.ask` and merging #1588 service-path regressions for Arabic polarity reversal, faithful negative wording, and unrelated obligation clauses. Runtime tests remain unexecuted.

All of these merges are source-reviewed code integration only. Their tests remain unexecuted unless an explicit runtime result is recorded; do not infer passing tests from a successful merge.

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


## Retrieval evaluator malformed-enum follow-up — 2026-11-13

- PR #1580 guards untrusted `review_status` and `reviewer_role` JSON values before set membership. Malformed list/object values now enter the evaluator's invalid-question report rather than raising `TypeError`. It also rejects raw backslashes and empty query/fragment delimiters in reviewer evidence URLs.
- Regression tests cover unhashable list values for both fields. Static source/diff review only; runtime tests remain unexecuted.
- Latest exact-head Tests workflow run `43328429442` (head `53eed6cfa7ab6601f6cdd13b4c362a25c6095f7f`) failed before exposing job steps (`steps: null`), consistent with the current runner-allocation blocker. An earlier head's run `43328171760` had the same result.


## Merge checkpoint — 2026-11-13 (current main)

- Merged #1577, #1576, #1580, #1582, #1584, #1583 and #1581. The large Legal Research redesign was rebased at file level onto current main: its old branch was 306 commits ahead and 18 behind; the replacement branch had 0 commits behind and retained newer main-side evaluation/importer work.
- Closed superseded drafts #1578, #1564, #1558 and #1543. #1578's remaining provenance hardening was recreated as #1584 and merged.
- No GitHub Actions test execution or browser acceptance is claimed. The Actions runner/billing issue still prevents jobs from exposing executable steps. Run focused importer, retrieval scorer/evaluator, device acceptance, document classification, app runtime, export and frontend contract tests in the clean Python 3.12 hash-locked environment when available.
- Legal Research implementation is merged, but browser acceptance (Arabic RTL, English LTR, keyboard-only, mobile/desktop), end-to-end PDF/DOCX upload/download/review, and adversarial tenant-isolation checks remain open.


## Current-main implementation progress — 2026-11-13

| Workstream | Repository implementation | Validation / acceptance | Overall status |
|---|---:|---:|---:|
| Figma-aligned Legal Research UI and application shell | 100% merged (#1582) | Browser/RTL/LTR/accessibility QA not run | 80% |
| PDF/DOCX upload, accessible document library, metadata and Arabic/English text search | 100% merged (#1582) | End-to-end upload/download and adversarial tenant checks not run | 80% |
| Persistent classification, audit history, extraction review and literal multi-hunk correction comparison | 100% merged (#1582/#1591) | Python 3.12 integration tests and browser review flow not run | 85% |
| Cross-document version comparison API and Documents workspace integration | 100% merged (#1592) | Matter-scope/page-provenance runtime tests and browser acceptance not run | 80% |
| Gazette importer and provenance hardening | 100% merged (#1576/#1577/#1584) | Focused Python 3.12 tests not run | 80% |
| Retrieval scorer/evaluator and device-evidence input hardening | 100% merged (#1580/#1581/#1583) | Focused Python 3.12 tests not run | 80% |
| Live Arabic/English negated-obligation guard | Runtime call site confirmed; Arabic service-path tests merged (#1588) | Tests not run | 85% |
| Structured candidate extraction (labelled entities, bilingual case/legal references, event mentions, explicit relationships, date and amount candidates) | 100% merged (#1594/#1600/#1602/#1603/#1604/#1606/#1608) | Helper/API/browser tests not run; limited deterministic rules; official-law verification remains external | 88% |
| Matter-wide date/event mention timeline | 100% merged (#1596) | API/browser acceptance and tenant-scope runtime checks not run | 80% |
| Cross-document exact repeated-mention grouping | 100% merged (#1598) | Exact-match groups require human review; no identity resolution; tests/browser not run | 70% |
| Advanced multi-document synthesis and cross-document entity resolution | Not implemented | Requires evidence conflict model, provenance policy and counsel evaluation | 20% |
| Full Arabic RTL/LTR, keyboard, mobile/desktop acceptance | Not complete | Requires browser/device execution | 0% |
| CI / clean Python 3.12 suite | Not complete | Runner/billing allocation prevents hosted jobs; local execution not available in this session | 0% |
| Adversarial tenant-isolation and backup/restore acceptance | Foundations and targeted tests exist | Full cross-firm route/job/export/search and witnessed restore remain | 40% |
| Payment-provider and paid-pilot acceptance | Existing billing UI/API foundations | Provider sandbox, webhook, real-firm and revenue evidence remain | 30% |
| Egyptian-law source verification and counsel sign-off | Review inventories and tooling exist | Qualified counsel and authenticated Gazette evidence required | 0% |

Percentages distinguish repository implementation from validation and operational acceptance. A merged PR is not a test pass or production-readiness certification.


## Follow-up hardening — 2026-11-13

- #1588 merged Arabic service-path tests for the live negated-obligation guard; issue #1561 is closed. The tests are committed but not executed.
- #1589 merged an additional explicit-source-reference validation check; #1590 then removed a duplicate earlier check, retaining one fail-closed validation point. The importer still rejects explicitly supplied null/empty/non-string references even when a valid source URL exists.
- Neither merge establishes a passing test result. Focused Python 3.12 execution remains blocked by unavailable hosted runners and was not run locally in this session.


## Document review comparison integration — 2026-11-13

- PR #1591 exposes bounded multi-hunk literal comparison for corrected extraction passages in the authorized chunk API and review UI. Each hunk shows before/after text and an explicit lawyer-review requirement; oversized comparisons fail closed with a warning.
- The uploaded original remains unchanged. This is a transcription-difference view, not semantic legal analysis or a finding that the correction is accurate.
- Runtime and frontend contract tests were added but not executed because hosted runner/billing allocation remains blocked.

## Cross-document version comparison — 2026-11-13 (merged #1592)

- Added `GET /documents/compare` for two document IDs within one authorized matter. It verifies both document records against the selected case and active firm; cross-matter/missing IDs return the same 404 response.
- Text is assembled in stored chunk order with source chunk IDs, references, page numbers and character offsets. Each version is bounded to 100,000 characters; the shared helper caps output at 200 literal change hunks.
- The Documents workspace now uses the server comparison endpoint and renders each before/after hunk, both versions' source-chunk/page references, and an explicit lawyer-review warning. It no longer presents a local first/last-difference approximation as the comparison result.
- Added separate-database runtime coverage for a real two-document comparison, page provenance, cross-matter denial and same-document rejection, plus frontend contract assertions.
- PR #1592 merged at `531315955078fb01febfc6f36c61a0fa09edd6e9`. Static source/diff review only; no Python tests or browser execution has run. Merge is code integration, not a passing test or production acceptance.

## Structured entity, event and relationship candidates — 2026-11-13 (merged #1594)

- Added bounded bilingual rule-based structuring for labelled-party and literal identifier/amount/date entities, event triggers with same-sentence date/party mentions, and explicit Arabic/English relationship phrases.
- Integrated results into the authorized document-chunk API with document/chunk/page provenance and per-kind caps; the Legal Research UI now renders separate candidate cards and warnings.
- Added helper, separate-database API and frontend contract regressions. PR #1594 merged at `600dea925d95f8bccdec79dad9157a4aec78a1e0`. No tests or browser runs were executed because hosted runner/billing allocation remains blocked.
- This is not general NER, entity resolution, event verification, or a legal relationship conclusion. All records remain unverified candidates; OCR/extraction errors may propagate.

## Matter-wide date and event mention timeline — 2026-11-13 (merged #1596)

- Added an authorized case-scoped endpoint that aggregates date and event mentions across documents in the selected matter only, preserving document/chunk/page provenance and source offsets.
- Caps: 200 documents, one million extracted characters, 1,000 date mentions and 500 event candidates. Every view records a security audit event.
- The Documents workspace can request the matter-wide index and displays parseable dates, unparsed dates and same-sentence event mentions. It explicitly warns that this is not a verified chronology and creates no deadlines.
- Added helper, separate-database runtime and frontend contract tests. PR #1596 merged at `27409eedaa042c3b54abdb4fe547ce396751c5b4`. No tests or browser execution were run because hosted runner/billing allocation remains blocked.

## Cross-document repeated-mention index — 2026-11-13 (merged #1598)

- Added exact normalized mention grouping for labelled parties and case/legal references within one authorized matter. Matching is limited to Unicode NFKC, case-folding and whitespace collapse; no fuzzy or semantic identity resolution is attempted.
- Added a matter-authorized API and UI action, with member-level document/chunk/page provenance, 200-document/one-million-character/1,000-candidate/500-group bounds and audit logging.
- Same-firm nonmembers are denied by the matter authorization gate. Added helper, API, authorization and frontend contract tests; PR #1598 merged at `5d4b9516cfdebe13d5c99053a50145e968e39ea0`. None were executed because hosted runners remain unavailable.
- All groups are possible repeated mentions only, not proof of identity, common ownership or legal relationship.

## Arabic/English named-month date extraction — 2026-11-13 (branch pending merge)

- Added named Gregorian month recognition for Arabic and English day-first/month-first date mentions, including Arabic-Indic digits, to the shared extraction and matter timeline helper.
- Valid four-digit-year dates are normalized; ambiguous two-digit years and invalid calendar dates remain unparsed. Hijri conversion is explicitly unsupported.
- Added helper regression coverage. Tests/browser acceptance remain unexecuted; branch `feature/arabic-named-month-dates-20261113` is pending merge.
