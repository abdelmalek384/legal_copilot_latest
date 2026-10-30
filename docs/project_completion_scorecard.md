# Legal Copilot — Whole-project completion scorecard

**As of:** 2026-10-30 (after merges #907, #905, #909, #910, #920 and #923)  
**Purpose:** One consistent, evidence-based percentage for technical project completion. This score is a planning estimate, not a certification or market-readiness claim.

## Current score

<escape>**Technical project completion: 49%** (weighted estimate; rounded from 49.1%).</escape>

**Final Egyptian-counsel acceptance: 0% / not started.** This is a separate post-build acceptance gate, as planned. It must be completed before the product is represented as legally approved or used for client-facing legal reliance.

Open pull requests do not count as completed deliverables. Their changes are treated as pending until merged and validated against the resulting commit. The scorecard is recalculated when a workstream's evidence changes; it is not increased merely because more code or documentation was added.

## Weighted workstreams

| Workstream | Weight | Completion | Weighted points | Current evidence and remaining blockers |
|---|---:|---:|---:|---|
| Core case-management and collaboration workflows | 15% | 75% | 11.25 | Case folders, teams, tasks, sessions, notes, files, fees, activity history and dashboard workflows exist. Remaining: end-to-end workflow acceptance, edge-case QA, and operational polish. |
| Legal research, retrieval and citation quality | 15% | 65% | 9.75 | Arabic/English lexical retrieval, source scoping, citation validation, abstention, provenance display and evaluation tooling exist. Remaining: real lawyer-labelled evaluation, retrieval tuning on reviewed material, and broader practice-area coverage. |
| Verified Egyptian legal knowledge and source rights | 25% | 6% | 1.50 | Candidate catalogues, source registers, permission gates, version metadata, audit tools and review queues exist. The verified corpus remains very small; original primary-source matching, reuse rights, amendment/currentness review and qualified counsel sign-off are still blockers. Candidate counts and secondary copies do not count as verified law. |
| Security, privacy and firm isolation | 15% | 72% | 10.80 | Separate profile architecture, access controls, MFA, audit events and isolation tests are reinforced by merged CodeQL (Python/JavaScript), Bandit and strict hash-locked dependency auditing. Remaining: review all CodeQL alerts, triage 17 medium B608 findings on the exact release candidate, complete DB/storage workstream, independent security assessment, and witnessed recovery/rollback. |
| UI, accessibility and device usability | 10% | 48% | 4.80 | Responsive Arabic-first interface, installable PWA shell, and safer Mac/Windows first-run launchers are merged. Automated frontend contracts pass. Manual RTL/LTR, keyboard, screen-reader, real Android/iOS/desktop install, offline and browser acceptance remain incomplete. |
| Automated testing and reliability | 10% | 66% | 6.60 | Full CI passed 131/131 on the merged legal-import/Arabic-OCR candidate; the hardened container built for amd64 and arm64, with Compose validation, CodeQL/Bandit and dependency audit passing on their exact PR heads. Remaining: fresh full-suite evidence on the exact release candidate, staging smoke tests, browser/device acceptance and witnessed operational tests. |
| Production operations and deployment readiness | 10% | 44% | 4.40 | Merged hash-locked Python deployment dependencies, hardened non-root/read-only container and Compose template, dual-architecture image builds, read-only reminder health monitoring, strict preflight and release gates. Remaining: actual host/proxy deployment, production secrets and IAM, S3/KMS live acceptance, SMTP staging, external alert routing, operator reconciliation, witnessed restore/recovery drill and controlled deployment rehearsal. |
| **Total** | **100%** |  | **49.10 / 100** | **Rounded technical completion: 49%.** |

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

## Current merged deliverables and open implementation items

### Major deliverables merged into main

- **PR #907 — static application security analysis:** CodeQL for Python and JavaScript/TypeScript plus Bandit. The high-severity gate passed. Seventeen medium B608 SQL-construction findings remain visible for manual review; scan success is not a clean-alert certification.
- **PR #905 — reminder outbox monitoring:** read-only per-firm health probe and operator runbook are merged. Staging scheduler, alert routing, SMTP provider behavior and reconciliation remain untested.
- **PR #903 — installable PWA shell:** merged. Real Android/iOS/desktop installation, offline behavior and accessibility acceptance remain manual gates.
- **PR #909 — Mac/Windows first-run launchers:** merged after 127/127 Full Tests. Physical Windows and macOS smoke tests remain pending.
- **PR #910 — dependency security baseline:** merged. The Python 3.12 hash lock, strict dependency audit, Dependabot and pinned resolver toolchain are in main. The exact lock passed clean --require-hashes installation and strict pip-audit.
- **PR #920 — hardened container deployment:** merged after 130/130 Full Tests, Compose validation, and successful amd64/arm64 image builds. No image was published and no host deployment has occurred.
- **PR #923 — legal PDF import and Arabic OCR:** merged after 131/131 Full Tests, CodeQL/Bandit and dependency audit. The importer validates exact PDF bytes against SHA-256, rejects unsafe file/URL inputs, requires explicit source language, segments Arabic/English article headings, and defaults scanned-document OCR to ara+eng. It creates unverified candidate rows only; it does not establish source rights, authenticity, extraction accuracy, legal force or lawyer approval.
- **PR #901 — purged-original backup tombstones:** already merged. The backup bundle preserves tombstone metadata without expecting physically purged original bytes.

### Still open or externally blocked

- **PR #840 — Labour Law evidence ledger and Gazette candidate inventory:** draft/open and not yet synchronized to current main. The 781 Table 24 rows remain secondary-source candidates; original Gazette byte/page matches remain 0/781. No candidate row is promoted to verified law.
- **PR #898 — S3 physical-purge state machine:** open and assigned to the separate database/storage workstream. Destructive-operation approval, live S3/KMS/IAM acceptance, approved retention/deletion policy and witnessed recovery remain mandatory.
- **Database/storage workstream:** remains assigned separately. Do not duplicate schema, migration, storage-runtime or irreversible deletion work here.
- **Action 1 primary-source intake:** awaiting the user's original Gazette PDF and optional law_rows_ar.jsonl. Keep source bytes local/private; use the intake, hashing and comparison tools without committing the files.
- **Final Egyptian-counsel acceptance:** 0% / not started by design. The lawyer must test the actual application after technical completion; this remains a separate mandatory approval gate.
- **Manual product acceptance:** phone/tablet/desktop RTL/LTR, keyboard, screen-reader, PWA install/offline, Windows/macOS launchers and primary lawyer workflows have not been witnessed or recorded.


## Next highest-value priorities

1. Complete the product-wide manual QA and release smoke-test evidence, including Arabic-first workflows on phone, tablet and desktop.
2. Close production operations gaps: staging configuration, monitoring, scheduler ownership/reconciliation, and witnessed recovery.
3. Complete the separate database/storage workstream and validate the integration without unsafe cutover.
4. On receipt of the original legal files, perform the primary-source matching and provenance review; keep legal status quarantined until counsel review.
5. Finish independent security review and the post-build Egyptian-counsel acceptance.

