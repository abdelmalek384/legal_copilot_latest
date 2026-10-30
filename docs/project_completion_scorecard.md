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

## Latest merged progress — 2026-10-30

- **PR #931 merged:** registered الذاكرة والمعرفة للدراسات as a public Egyptian legal-document archive discovery lead. Its pages state CC BY 4.0 and expose full-text records across Court of Cassation, Supreme Constitutional Court, Supreme Administrative Court, laws and decisions. Collection/commercial reuse remain **unknown** because licence scope, underlying rights and provenance are not fully established. No legal text was imported.
- **PR #750 merged:** added five provisional Labour Law Articles 237–241 review questions; they remain non-authoritative and require source/counsel review.
- **PR #797 merged:** added the Labour Law implementing-decision verification matrix and restricted-source fallback documentation.
- **PR #926 and #928 remain merged:** metadata-only source discovery and PDF importer resource bounds.
- **CI/security dependency updates merged:** #911 checkout v7, #912 setup-python v7, #913 upload-artifact v7, #915 PyMuPDF 2.0.0, #916 pypdf update, #918 FastAPI 0.162.0, and #919 CodeQL Action v4. Their relevant tests/security checks passed before merge.
- **No percentage increase is claimed:** the legal source additions are discovery/provisional work, not verified or counsel-approved legal content. The verified Egyptian legal corpus remains at 6%.

## Current open implementation items

- **PR #782 — Labour Law evidence inventory:** open, non-DB work. The canonical main file contains 294 cards; manifest and report have been aligned to that actual count. Split snapshots are excluded until duplicate/divergent records are reconciled. The cards remain provisional and search-ineligible. Latest full CI is running; do not merge until Tests, CodeQL and dependency audit pass on the final head.
- **PR #840 — Decisions 248–252 / Table 24:** remains draft/open. Secondary transcription line cross-checks are now recorded for Table 24 rows 34, 61 and 64, but all three discrepancies remain unresolved. Original Gazette issue 225(A) is still request-copy restricted; official matches 0/781, counsel-approved rows 0, retrieval-eligible rows 0.
- **PR #784 — Decision 162 currentness lead:** remains draft/open. Keep signature date, Gazette publication date, commencement and later amendments separate until primary-source reconciliation is complete.
- **PR #922 — Docker build-action update:** open but blocked by a failing cross-firm reminder-healthcheck test. Do not bypass or weaken the tenant-isolation assertion.
- **PR #914 — Boto3 update:** held for review alongside the separate S3/storage workstream.
- **PR #917 — Pillow update:** tests passed on its branch, but it has a merge conflict against current main; synchronize and rerun checks before merging.
- **PR #898 — S3 physical-purge state machine:** separate database/storage workstream. Do not enable destructive purge without independent review, live S3/KMS/IAM evidence, approved retention policy and witnessed recovery.
- **Database/storage workstream:** remains assigned separately. Do not duplicate schema, migration, identity or destructive storage changes here.

## Next highest-value priorities

1. Complete the 294-card canonical Labour Law inventory validation and merge PR #782 only after all required checks pass.
2. Continue obtaining lawful primary Gazette evidence for Decisions 248–252 and other implementing instruments; keep secondary transcriptions and third-party scans quarantined.
3. Assess the new Egyptian case-law archive's CC BY 4.0 scope and Article 141 rights context without bulk scraping or assuming official provenance; use it as discovery/cross-reference material until source and rights gates are clear.
4. Close production operations gaps: real staging configuration, monitoring/alert routing, scheduler ownership/reconciliation, and witnessed backup/restore.
5. Complete manual Arabic RTL/LTR, mobile, desktop, keyboard, screen-reader and lawyer-workflow acceptance.
6. Complete the separate database/storage workstream and validate integration without unsafe cutover.
7. Obtain qualified Egyptian counsel's actual application acceptance after technical completion.

