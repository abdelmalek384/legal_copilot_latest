# Legal Copilot — Whole-project completion scorecard

**As of:** 2026-10-31  
**Purpose:** One consistent, evidence-based percentage for technical project completion. This score is a planning estimate, not a certification or market-readiness claim.

## Current score

<escape>**Technical project completion: 48%** (weighted estimate; rounded from 47.90%).</escape>

**Final Egyptian-counsel acceptance: 0% / not started.** This is a separate post-build acceptance gate, as planned. It must be completed before the product is represented as legally approved or used for client-facing legal reliance.

Open pull requests do not count as completed deliverables. Their changes are treated as pending until merged and validated against the resulting commit. The scorecard is recalculated when a workstream's evidence changes; it is not increased merely because more code or documentation was added.

## Weighted workstreams

| Workstream | Weight | Completion | Weighted points | Current evidence and remaining blockers |
|---|---:|---:|---:|---|
| Core case-management and collaboration workflows | 15% | 75% | 11.25 | Case folders, teams, tasks, sessions, notes, files, fees, activity history and dashboard workflows exist. Remaining: end-to-end workflow acceptance, edge-case QA, and operational polish. |
| Legal research, retrieval and citation quality | 15% | 65% | 9.75 | Arabic/English lexical retrieval, source scoping, citation validation, abstention, provenance display and evaluation tooling exist. Remaining: real lawyer-labelled evaluation, retrieval tuning on reviewed material, and broader practice-area coverage. |
| Verified Egyptian legal knowledge and source rights | 25% | 6% | 1.50 | Candidate catalogues, source registers, permission gates, version metadata, audit tools and review queues exist. The verified corpus remains very small; original primary-source matching, reuse rights, amendment/currentness review and qualified counsel sign-off are still blockers. Candidate counts and secondary copies do not count as verified law. |
| Security, privacy and firm isolation | 15% | 72% | 10.80 | Separate profile architecture, access controls, MFA, audit events, backup tooling and isolation tests exist. The MFA lifecycle audit-failure rollback regression merged in PR #925; CodeQL/Bandit security analysis merged in PR #907. Remaining: complete DB/storage workstream, exhaustive route/job isolation evidence, independent security assessment, and witnessed recovery/rollback. |
| UI, accessibility and device usability | 10% | 45% | 4.50 | Responsive Arabic-first interface, installable privacy-safe PWA shell (PR #903 merged), and current-main Windows/Mac first-run launchers (PR #909 merged) exist. Physical Windows/macOS checks and manual RTL/LTR, keyboard, screen-reader, mobile/tablet and browser acceptance remain incomplete. |
| Automated testing and reliability | 10% | 66% | 6.60 | Broad CI coverage, hash-locked Python dependency baseline (PR #910 merged), CodeQL/Bandit static analysis (PR #907 merged), and current-main legal PDF integrity/OCR regressions (PR #923 merged) exist. Remaining: fresh full-suite evidence for the exact release candidate, operational smoke tests, and resolution of any current failures. |
| Production operations and deployment readiness | 10% | 35% | 3.50 | Strict preflight, release gates, encrypted backup/restore code, storage adapters and reminder outbox/scheduler foundations exist. Remaining: real staging configuration, live provider tests, monitoring/alerting, operator reconciliation, witnessed restore drill, and controlled deployment rehearsal. |
| **Total** | **100%** |  | **47.90 / 100** | **Rounded technical completion: 48%.** |

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

## Latest merged progress — 2026-10-30 (127-card corpus and source discovery)

- **PR #931 merged:** registered الذاكرة والمعرفة للدراسات as a legal-document archive discovery lead. The site states CC BY 4.0 and exposes full text across three court sections, laws and decisions. Collection/commercial reuse remain unknown because the scope of the licence over underlying texts, third-party reproductions, annotations and the database compilation is unresolved. No legal text was imported.
- **PR #935 merged:** registered the official Court of Cassation Legal Heritage Library as a manual primary-source verification route. The Court's announcement reports 27 scanned volumes, 13,275 pages, 3,533 indexed documents and 12,577 index entries for the core 1899–1933 series. Individual 1899, 1933, 1936 and 1937 catalogue records were located. Scans are watermarked to prevent republication; collection and commercial reuse remain unknown. The current judgments/principles search portal is tracked separately with its published restrictions. No scans were ingested.
- **PR #937 merged:** added 43 non-duplicate Labour Law 14/2025 occupational-safety and inspection cards for selected Articles 256–298, expanding the canonical inventory from 59 to 102.
- **PR #939 merged:** added 15 coverage-gap cards for accompanying-law Articles 1–39 and 10 promulgation cards for Articles 2–11, expanding the canonical inventory to 127. The report renderer now displays missing Gazette pinpoints as “not established.” Every card remains search_eligible=false.
- **PR #940 merged:** registered the public Dataflare Egyptian Legal Corpus dataset (2,434 records, 25M+ tokens, dataset card claims MIT) as a provenance-gated candidate. It lacks record-level source URLs, dates, Gazette pinpoints and currentness metadata; underlying provenance and rights scope remain unknown. No Parquet file or legal text was downloaded or imported.
- **PR #914 and #917 merged:** Boto3 and Pillow dependency updates passed Tests, CodeQL and dependency audit before merge.
- **No completion-percentage increase is claimed:** provisional cards and source-discovery metadata improve research preparation, but do not establish verified law or counsel-approved answers. The verified Egyptian legal corpus remains 6%.

## Latest merged progress — 2026-10-31 (security and legal-source discovery)

- **PR #945 merged:** upgraded the Python PDF parser to pypdf 6.21.4 and refreshed the hash-locked Python 3.12 deployment lock. The prior 6.21.2 pin triggered four dependency advisories; the updated branch passed the full Tests workflow, dependency audit, CodeQL and container image build.
- **PR #946 merged:** resolved the identity of Ministerial Decision 162/2026, recorded the Official Gazette Supplement 176 metadata (13 August 2026), and added a secondary-text crosswalk against Labour Law 14/2025 Articles 117–129, 137 and 141. The candidate effective date 14 August 2026 is not verified against original Gazette bytes. Article 46's investigation-extension wording remains a counsel question. The instrument remains discovery-only and retrieval-ineligible.
- **PR #944 merged:** recorded the Supreme Constitutional Court's public recent-judgments page and a third-party-described API lead. The API was not called or independently validated; official terms and collection/commercial reuse remain unknown. No judgments were ingested.
- **PR #931 merged:** registered الذاكرة والمعرفة للدراسات as a discovery-only legal archive. Its site-level CC BY 4.0 statement does not resolve rights over underlying texts, third-party reproductions or database compilation. No legal text was imported.
- **PR #784 closed as superseded by #946:** the exact Decree 162 record and crosswalk now live in current main.
- **No increase is claimed for verified Egyptian legal knowledge:** all these changes improve source discovery, provenance and release safeguards, but no new Gazette original was hashed/visually matched and no lawyer-approved legal text was added. Verified-corpus completion remains 6%.

## Latest merged progress — 2026-10-31 (360-card reconciliation and storage acceptance evidence)

- **PR #963 merged:** reconciled the Labour Law No. 14/2025 candidate inventory to 360 unique card IDs, covering Articles 1–298 with no article-number gaps. The full 138-step Tests workflow, CodeQL and dependency audit passed on the merged candidate commit. All 360 cards remain `search_eligible=false`; the reconciliation is not primary-source verification, currentness review, rights clearance or counsel approval.
- **PR #967 merged:** added a focused Official Gazette visual-check record for Labour Law Article 13 and printed pages 94–111, correcting 90 card pinpoints across Articles 250–298. The local PDF bytes and SHA-256 remain unavailable; reuse rights, amendment/currentness review and counsel approval remain open.
- **PR #834 merged:** updated the SEC-01 attack-surface inventory to reflect tenant-scoped original-file storage, the local development adapter, S3/KMS adapter foundation, staged-upload recovery and encrypted multi-database backup/restore. Live bucket/key-policy validation, approved retention schedules and witnessed recovery/deletion remain open.
- **PR #983 merged:** added the S3 purge acceptance checklist covering live IAM/KMS/bucket evidence, retention, recovery and destructive-action safeguards. This is acceptance documentation, not approval to run a purge or evidence that production controls have passed.
- **PR #987 merged:** recorded Riwaq al-Jamal's public Decision 250 secondary transcription as rights-unknown, and Law Hub's PDF-preview route with its published restriction on profiting by republishing its free site materials. The Google Drive preview was not readable in this review; no PDF bytes or hash are claimed. The note preserves the 781-entry secondary structure, 0/781 Official Gazette matches, and unresolved rows 34, 61 and 64. No row-level transcription was imported. Source-permission tests, the full Tests workflow, non-database safety regression, CodeQL and dependency audit all passed.
- **PR #989 merged:** added metadata-only Phase 2 records for Labour Decisions 248–252/2026, plus source-rights records and a secondary-source matrix. The IDSC/Amiri Press catalogue lists the 6.13 MB Gazette PDF and a 55-byte item-specific `license.txt`; both downloads resolve to request-a-copy forms, so neither the original nor the licence text was obtained. Secondary sources remain link-out leads only; no row-level text was imported. All five instruments remain discovery-only, legal status unknown and retrieval-ineligible. Table 24 remains 0/781 official matches; rows 34, 61 and 64 remain unresolved.
- **PR #990 merged:** added same-firm nonmember regression coverage for task claim and completion routes, asserting 404 and unchanged task state. The full 139-step Tests workflow, CodeQL and dependency audit passed.
- **Superseded branches closed:** PR #971 was closed as a duplicate of #963. PR #782 was closed after confirming its 294 canonical card IDs and its supplementary coverage are represented in current main; seven differently named Articles 258–265 cards were semantic duplicates of cards already in the canonical inventory.
- **No completion-percentage increase is claimed:** these changes improve inventory integrity, evidence traceability, tests and release controls. They do not add lawyer-approved or fully primary-source-verified legal content. Verified Egyptian legal knowledge remains 6%; technical completion remains 48%.

## Current open implementation items

- **PR #840 — Decisions 248–252 / Table 24:** draft/open. The official Gazette catalogue confirms Supplement 225(A), dated 12 October 2026, but the original bundle is request-copy restricted. Secondary full transcriptions are discovery/cross-check leads only. Table 24's secondary transcription has 781 numbered entries; original Gazette matches remain 0/781, counsel-approved rows 0/781 and retrieval-eligible rows 0/781. Rows 34, 61 and 64 retain unresolved discrepancies. Do not merge its row-level secondary transcription into the product corpus without a defensible source-use basis and primary comparison.
- **PR #970 and #974 — database/storage workstream:** open and assigned to the separate AI/workstream. Do not duplicate or alter schema, tenant-runtime, purge, retention or destructive storage changes here. PR #898 was closed unmerged and #974 is the refreshed follow-up; no production purge is authorized by the checklist.
- **PR #922 — Docker build-action update:** closed unmerged. The version bump is not included in main; only revisit if still required and with a passing cross-firm isolation test.
- **Decision 162/2026 and Decision 249/2026:** provenance and quarantined evidence were merged via #961 and #964; original Gazette bytes/hash, full currentness/amendment review, reuse clearance and counsel approval remain outstanding.
- **Database/tenant work:** remains assigned to the separate workstream. No duplicate schema, migration, identity or destructive storage changes were made here.

## Next highest-value priorities

1. Advance Decisions 248–252/2026 through lawful primary-source comparison; keep secondary transcriptions as manual research leads and all unverified content out of retrieval.
2. Resolve the Decision 250 Table 23/24 original-source gap without bypassing the Gazette repository's request-copy restriction; preserve row discrepancies and rights uncertainty.
3. Complete the separate DB/storage workstream under its owner, including live S3/KMS/IAM evidence, retention approval, recovery and purge acceptance; do not duplicate those changes here.
4. Complete real lawyer-labelled retrieval/citation evaluation against reviewed Egyptian legal material.
5. Complete manual Arabic RTL/LTR, accessibility, mobile, browser and lawyer-workflow QA; record build, tester, environment and defects.
6. Complete staging operations, monitoring, operator reconciliation and witnessed backup/restore/rollback.
7. Obtain qualified Egyptian counsel's actual application acceptance after technical completion.

**Technical completion remains 48%** (47.90/100). Final Egyptian-counsel acceptance remains **0% / not started**. More provisional records or secondary-source cross-checks do not count as verified law or market readiness.
