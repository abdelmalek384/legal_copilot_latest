# Legal Copilot — Whole-project completion scorecard

**As of:** 2026-10-30  
**Purpose:** One consistent, evidence-based percentage for technical project completion. This score is a planning estimate, not a certification or market-readiness claim.

## Current score

<escape>**Technical project completion: 48%** (weighted estimate; rounded from 47.95%).</escape>

**Final Egyptian-counsel acceptance: 0% / not started.** This is a separate post-build acceptance gate, as planned. It must be completed before the product is represented as legally approved or used for client-facing legal reliance.

Open pull requests do not count as completed deliverables. Their changes are treated as pending until merged and validated against the resulting commit. The scorecard is recalculated when a workstream's evidence changes; it is not increased merely because more code or documentation was added.

## Weighted workstreams

| Workstream | Weight | Completion | Weighted points | Current evidence and remaining blockers |
|---|---:|---:|---:|---|
| Core case-management and collaboration workflows | 15% | 75% | 11.25 | Case folders, teams, tasks, sessions, notes, files, fees, activity history and dashboard workflows exist. Remaining: end-to-end workflow acceptance, edge-case QA, and operational polish. |
| Legal research, retrieval and citation quality | 15% | 65% | 9.75 | Arabic/English lexical retrieval, source scoping, citation validation, abstention, provenance display and evaluation tooling exist. Remaining: real lawyer-labelled evaluation, retrieval tuning on reviewed material, and broader practice-area coverage. |
| Verified Egyptian legal knowledge and source rights | 25% | 6% | 1.50 | Candidate catalogues, source registers, permission gates, version metadata, audit tools and review queues exist. The verified corpus remains very small; original primary-source matching, reuse rights, amendment/currentness review and qualified counsel sign-off are still blockers. Candidate counts and secondary copies do not count as verified law. |
| Security, privacy and firm isolation | 15% | 71% | 10.65 | Separate profile architecture, access controls, MFA, audit events, backup tooling and isolation tests exist. The MFA lifecycle audit-failure rollback regression merged in PR #925; CodeQL/Bandit security analysis merged in PR #907. Remaining: complete DB/storage workstream, exhaustive route/job isolation evidence, independent security assessment, and witnessed recovery/rollback. |
| UI, accessibility and device usability | 10% | 45% | 4.50 | Responsive Arabic-first interface, installable privacy-safe PWA shell (PR #903 merged), and current-main Windows/Mac first-run launchers (PR #909 merged) exist. Physical Windows/macOS checks and manual RTL/LTR, keyboard, screen-reader, mobile/tablet and browser acceptance remain incomplete. |
| Automated testing and reliability | 10% | 65% | 6.50 | Broad CI coverage, hash-locked Python dependency baseline (PR #910 merged), CodeQL/Bandit static analysis (PR #907 merged), and current-main legal PDF integrity/OCR regressions (PR #923 merged) exist. Remaining: fresh full-suite evidence for the exact release candidate, operational smoke tests, and resolution of any current failures. |
| Production operations and deployment readiness | 10% | 35% | 3.50 | Strict preflight, release gates, encrypted backup/restore code, storage adapters and reminder outbox/scheduler foundations exist. Remaining: real staging configuration, live provider tests, monitoring/alerting, operator reconciliation, witnessed restore drill, and controlled deployment rehearsal. |
| **Total** | **100%** |  | **47.95 / 100** | **Rounded technical completion: 48%.** |

## Completion rules

1. A feature is complete only when its acceptance criteria are implemented, tests pass on the exact candidate commit, and the change is merged.
2. A draft PR, passing unit test, candidate legal document, source URL, or metadata inventory is not equivalent to a completed release deliverable.
3. Legal material is counted as verified only after original-source authenticity, extraction accuracy, permission/reuse scope, effective/current status, amendment history, and required legal review are evidenced. Unreviewed or secondary material remains quarantined.
4. Security is not complete solely because automated tests pass. Independent assessment, operational access-control tests, and witnessed recovery remain required.
5. Manual QA checklists are procedures, not completed evidence. A run record must identify date, build/commit, environment, tester, result, and defects.
6. The final lawyer acceptance is deliberately separate from engineering progress and is scheduled after technical completion. It remains a mandatory release/approval gate.

## Hard release gates

The product cannot be called production-ready or legally approved until all applicable gates pass:

- [ ] Fresh full CI run passes on the exact release candidate.
- [ ] Database/storage workstream is complete and its owner confirms safe integration; no unapproved schema, migration, or irreversible data action is performed.
- [ ] Independent security review has no unresolved high/critical findings.
- [ ] Two-firm isolation, session revocation, upload/storage, and background-job authorization are evidenced end to end.
- [ ] Encrypted backup, restore, rollback, and original-file recovery are witnessed on a protected staging copy.
- [ ] Production preflight and aggregate release gate pass with the exact deployment configuration.
- [ ] SMTP and reminder scheduling are exercised in a controlled staging environment with monitoring and operator reconciliation.
- [ ] Manual RTL/LTR, mobile, keyboard, screen-reader, and primary lawyer workflows pass and are recorded.
- [ ] A permission-cleared primary legal corpus and lawyer-approved benchmark meet the legal release gate.
- [ ] Qualified Egyptian counsel tests the actual application and records approval or required corrections.

## Current open implementation items

- **PR #840** — Labour Law 14/2025 / Decisions 248–252 evidence ledger; remains draft/open. It is metadata and comparison-workflow work only; original Gazette issue 225(A) copy remains request-copy restricted, so no full Decision 248–252 source verification or verified-law coverage increase is claimed.
- **PR #926** — discovery-only additions for the Ministry of Parliamentary Affairs enacted-laws index, IDSC Gazette repository, and Manshurat Qanuneya. Collection and commercial reuse remain unknown; no legal text was downloaded or made retrieval-eligible. Tests and CodeQL are running; dependency audit passed.
- **PR #928** — current-main PDF importer resource limits (100 MiB PDF, 1,000 pages, 1 MiB metadata sidecars; bounded reads and fail-closed environment configuration). Full Tests, CodeQL and dependency audit are queued; do not merge until all pass.
- **PR #918, #919, #922** — routine FastAPI, CodeQL action and Docker build action dependency updates; review CI and dependency compatibility before merging.
- **PR #898** — S3 physical-purge state machine; separate database/storage workstream. Do not enable destructive purge without independent review, live S3/KMS/IAM evidence, approved retention policy and witnessed recovery.
- **Database/storage workstream** — remains assigned separately; PR #925 merged the MFA lifecycle audit-failure rollback regression. Do not duplicate schema/migration/runtime changes or perform irreversible storage actions here.
- **Superseded PRs** — #900 was replaced by merged #909; #903 merged; #904 was replaced by merged #923; #924 was superseded by current-main PR #928; #906 was superseded by merged #910.

## Next highest-value priorities

1. Complete the product-wide manual QA and release smoke-test evidence, including physical Windows/macOS launcher tests and Arabic-first workflows on phone, tablet and desktop.
2. Close production operations gaps: staging configuration, monitoring, scheduler ownership/reconciliation, and witnessed recovery.
3. Complete the separate database/storage workstream and validate the integration without unsafe cutover.
4. Continue lawful primary-source discovery using public official indexes and item-level metadata; keep text quarantined until source rights, authenticity, currentness and counsel review are evidenced.
5. Finish independent security review and the post-build Egyptian-counsel acceptance.

