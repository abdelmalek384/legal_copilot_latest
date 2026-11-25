# Manual pilot execution progress — 25 November 2026

**Scope:** AI-1 integration and release-verification checkpoint for Legal for Today. This is an engineering progress record, not a test report, legal certification, or pilot approval.

## Current completion estimates

| AI-1 workstream | Previous | Current | Change | Evidence boundary |
|---|---:|---:|---:|---|
| Legal Research reliability | 47% | 53% | +6 pp | Exact-statute retrieval guard merged; runtime retrieval tests not executed |
| Arabic retrieval and matching | 47% | 51% | +4 pp | Arabic/Persian digit normalization and exact case-number matching merged; benchmark performance unmeasured |
| Citation and trust safeguards | 60% | 67% | +7 pp | Extraction-page provenance preserved; reviewer page references remain unverified |
| Existing evaluation and tests | 26% | 40% | +14 pp | Focused regression coverage expanded; supported-runtime execution remains outstanding |
| PR review and integration | 20% | 55% | +35 pp | Ten PR integrations recorded in docs/STATUS.md; stale duplicates closed |
| **Overall AI-1 assignment** | **39%** | **47%** | **+8 pp** | Implementation estimate only; not runtime readiness |

Percentages measure implementation/evidence authoring against the assigned workstreams. They are not percentages of passing tests, legal accuracy, or production readiness.

## Confirmed manual integration

- #2010 — exact article lookup requires explicit statute number/year and registry-title match; Arabic/Persian digits normalized; exact boost limited to legal corpus.
- #2012 — direct text-document titles reject invisible/control characters while preserving Arabic shaping joiners.
- #2001 — outbound LLM/public-origin URL authority validation rejects malformed authorities, including empty user-information.
- #2016 — reminder date suffixes are strict and duplicate JSON keys fail closed at every nesting depth.
- #2018 — conflict-name substring false positives removed; case numbers require exact normalized numeric sequences; deadline unit and firm-holiday validation tightened.
- #2019 — dashboard/calendar/finance/invoice/research date defaults use Africa/Cairo; one as_of date is frozen per answer.
- #2020 — session fixation, MFA recovery, private download, forwarded-protocol, firm-switch CSRF/Origin, and CSV formula-injection regressions added.
- #2021 — tenant database and SQLite sidecar hard-link checks, post-open revalidation, and connection revocation added.
- #2022 — read-only tenant preflight reports/rejects hard-linked catalog databases, tenant databases, and sidecars.
- #2023 — reviewer-entered page references no longer overwrite extraction-time page provenance; MFA assurance reflects the active factor and destination firm.

## Validation actually performed

- Source and patch reviews were performed for the merged changes.
- Isolated helper assertions were reported by selected PRs; these are not substitutes for repository test execution.
- **Official repository test modules executed in this work session: 0.**
- Python 3.12 is not available in the current runtime and a local repository checkout could not be established.
- GitHub Actions were not used because runner billing is unavailable.
- Browser acceptance, two-firm route acceptance, deployment preflight, and backup/restore rehearsal were not performed.

## Legal evidence and trust restrictions

- No Egyptian legal source was newly lawyer-verified.
- The product trust labels remain conservative: source-matched is not lawyer-reviewed.
- Labour Law 14/2025 candidate rows remain unverified; verified=0 remains unchanged.
- No new law, decision, legal corpus row, or external source dataset was added during this stabilization pass.
- Actual retrieval quality remains unmeasured until the evaluation set has counsel-approved expected articles/answers and real retrieval exports.

## Remaining release gates

1. Supported Python 3.12 environment: clean install from the checked-in hash lock, run focused legal/security suites, then full suite and local release checker.
2. Legal retrieval: run synthetic article-selection and negation regressions; measure top-3 hit rate, wrong-article rate, and abstention rate on approved labels.
3. Tenant isolation: run the two-firm direct-ID/search/download/export denial matrix and filesystem race tests on the intended host.
4. Document workflow: verify upload, extraction, reviewer audit, original download, provenance, and retention in a disposable firm.
5. Operations: perform a witnessed encrypted backup/restore and verify restored tenant data and original binaries.
6. Legal approval: qualified Egyptian lawyer reviews any legal source and page reference before any verified label is applied.
7. Pilot sign-off: only after all applicable gates have recorded evidence; current decision remains NOT READY.

## Next unblocked engineering work

Continue reviewing the remaining legal-research and release-integration surface, without adding corpus data or new product features. Do not merge dependency updates until the Python 3.12 hash lock is regenerated and a clean install/audit can be run. Do not repeat unavailable CI or clone attempts.
