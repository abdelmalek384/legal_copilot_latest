# Legal Copilot — Whole-project completion scorecard

**As of:** 2026-11-01  
**Purpose:** One consistent, evidence-based percentage for technical project completion. This score is a planning estimate, not a certification or market-readiness claim.

## Current score

<escape>**Technical project completion: 50.01/100** (weighted estimate; up 0.02 points from 49.99; rounds to 50%).</escape>

**Final Egyptian-counsel acceptance: 0% / not started.** This is a separate post-build acceptance gate, as planned. It must be completed before the product is represented as legally approved or used for client-facing legal reliance.

Open pull requests do not count as completed deliverables. Their changes are treated as pending until merged and validated against the resulting commit. The scorecard is recalculated when a workstream's evidence changes; it is not increased merely because more code or documentation was added.

## Weighted workstreams

| Workstream | Weight | Completion | Weighted points | Current evidence and remaining blockers |
|---|---:|---:|---:|---|
| Core case-management and collaboration workflows | 15% | 76% | 11.40 | Case folders, teams, tasks, sessions, notes, files, fees, activity history, dashboard workflows, and the case-screen deadline calculator preview exist. The calculator remains explicitly non-authoritative because its rule and holiday data are unverified. Remaining: end-to-end workflow acceptance, edge-case QA, and operational polish. |
| Legal research, retrieval and citation quality | 15% | 68.3% | 10.245 | Arabic/English retrieval, expanded Egyptian colloquial phrase hints, source scoping, citation validation, a fail-closed lexical citation-relevance guard, abstention, provenance display and evaluation tooling exist. PR #1121 adds a versioned human-reviewed defect taxonomy (including source/polarity, actor/role, conditional scope, pinpoint, currentness, authenticity and privacy categories) while preserving uncategorized v1 legacy findings without inferred labels. This improves review traceability, not legal correctness or lawyer-labelled benchmark coverage. PR #1128 preserves recorded article/page locators and abstains on conflicting numeric pinpoints; PR #1130 adds narrow explicit Arabic predicate-polarity contradiction checks; PR #1131 adds cited actor-role and conditional-scope overgeneralization checks. These deterministic safeguards and the lexical relevance guard are not semantic entailment or counsel review. PR #1133 adds stable opaque answer IDs to evaluation reports, with legacy compatibility and explicit coverage reporting. PR #1134 compares independent reviews only when both case_id and answer_id match, and reports exact agreement, conflicts and adjudication needs without selecting a correct reviewer. These improve evaluation traceability, not legal correctness or actual lawyer-reviewed benchmark coverage. Remaining: real lawyer-labelled evaluation, retrieval tuning on reviewed material, and broader practice-area coverage. |
| Verified Egyptian legal knowledge and source rights | 25% | 9.8% | 2.45 | Candidate catalogues, source registers, permission gates, version metadata, audit tools and review queues exist. PR #1066 enforces the operator-attested counsel allowlist; #1067 aligns offline release validation; #1075 applies latest-event semantics to the review queue; #1077 aligns coverage metrics with runtime; #1083 consolidates strict current-event validation across runtime, queue and dashboard; #1087 prevents candidate seeding from drifting from the canonical permission register. PRs #1073–#1074 and #1080 improve Constitution provenance; #1081 reconciles Court of Cassation use terms and Article 141 context, retaining manual lookup/link-out only absent written commercial approval. PR #1089 adds strict URL parsing across legal evidence URL paths; #1090 aligns the read-only corpus audit with latest-event semantics; #1092 enforces exact permission-state parity at final release readiness; #1093 aligns strict HTTPS validation in the offline release validator. PR #1118 adds a bilingual candidate-inventory health panel and validation-issue count, with explicit language that the planning denominator is not legal-text availability, currentness, verified corpus coverage or counsel acceptance. This is dashboard transparency only, not independent credential verification or new primary-source-verified law. Original Gazette matching, reuse rights and amendment/currentness review remain blockers. |
| Security, privacy and firm isolation | 15% | 72.5% | 10.875 | Separate profile architecture, access controls, MFA, audit events, backup tooling and isolation tests exist. PR #1088 scopes prior research context to completed turns in the same search scope and matter ID, and explicitly persists those boundaries in assistant metadata; its Tests, CodeQL, dependency audit and non-database safety regression passed. The MFA lifecycle audit-failure rollback regression merged in PR #925; PR #1120 adds fault-injection proof that recovery-code consumption and session verification roll back if the verification audit write fails, and verifies audit-event immutability. CodeQL/Bandit security analysis merged in PR #907. Remaining: complete DB/storage workstream, exhaustive route/job isolation evidence, independent security assessment, and witnessed recovery/rollback. |
| UI, accessibility and device usability | 10% | 45.3% | 4.53 | Responsive Arabic-first interface, installable privacy-safe PWA shell (PR #903 merged), and current-main Windows/Mac first-run launchers (PR #909 merged) exist. Automated Chromium acceptance is merged and passed 6/6 tests in PR #1078. PR #1118 adds Arabic/English candidate-inventory dashboard acceptance for the planning-denominator caveat; it does not increase verified corpus volume. Physical Windows/macOS checks and manual RTL/LTR, keyboard, screen-reader, mobile/tablet and lawyer-workflow acceptance remain incomplete. |
| Automated testing and reliability | 10% | 69.9% | 6.99 | Broad CI coverage, hash-locked Python dependency baseline (PR #910 merged), CodeQL/Bandit static analysis (PR #907 merged), legal PDF integrity/OCR regressions (PR #923 merged), exact-head counsel-attestation and release-marker regressions, and merged 6/6 Chromium acceptance (PR #1078) exist. PR #1095 adds no-clobber output protection with real-CLI exit-code regression coverage; PR #1098 binds generated reports to exact input SHA-256/size metadata and a UTC host-clock timestamp. Both PRs passed their exact-head Tests, CodeQL, dependency and browser workflows. PR #1120 adds fault-injection coverage proving recovery-code consumption, session MFA verification and audit-event insertion roll back together when audit persistence fails; it also verifies audit-event update/delete are rejected. Exact-head Tests, Browser acceptance, dependency audit and Python/JavaScript CodeQL all passed. PRs #1128, #1130 and #1131 add exact-head regressions for article/page pinpoints, Arabic source-polarity reversals, actor-role substitutions and conditional-scope overgeneralization; each test module is explicitly invoked by CI. All three passed exact-head Tests, Browser acceptance, dependency audit, non-database safety regression, Bandit and Python/JavaScript CodeQL. PR #1133 adds validation and CI coverage for stable answer-ID propagation; PR #1134 adds independent-review agreement regressions for same-answer grouping, duplicate reviewer exclusion, legacy records and insufficient-evidence conflicts. Both passed exact-head Tests, Browser acceptance, dependency audit and Python/JavaScript CodeQL/Bandit. Remaining: manual device/accessibility acceptance, operational smoke tests and witnessed production recovery. |
| Production operations and deployment readiness | 10% | 35.2% | 3.52 | Strict preflight, release gates, encrypted backup/restore code, storage adapters and reminder outbox/scheduler foundations exist. PR #1102 adds post-submission SMTP ambiguity quarantine, no automatic retry after a possible acceptance, and no duplicate resend after confirmed SMTP acceptance; its exact-head tests and safety regression passed. Remaining: real staging configuration, live provider tests, monitoring/alerting, operator reconciliation, witnessed restore drill, and controlled deployment rehearsal. |
| **Total** | **100%** |  | **50.01 / 100** | **Rounded technical completion: 50%.** |

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

## Latest merged progress — 2026-10-31 (deadline workflow and AI quality)

- **PR #1052 merged:** integrated the existing deadline calculator into the case Legal Deadlines screen, with authenticated, case-scoped read-only preview, trigger-date validation, raw and adjusted dates, and explicit draft warnings. Full Tests, CodeQL, dependency audit and non-database safety regression passed. The calculator's legal rules and holiday calendar remain unverified; this is not a legally reliable deadline engine.
- **PR #1053 merged:** expanded retrieval-only Egyptian colloquial phrase hints across labour, tenancy, family, civil, commercial, procedural and accident-related questions. Original query wording and negation remain preserved. Full Tests, CodeQL, dependency audit and non-database safety regression passed. No lawyer-labelled top-k accuracy claim is made.
- **PR #1054 merged:** added a fail-closed lexical citation-relevance check that rejects cited claim sentences with no meaningful lexical anchor in their cited passages. Full Tests, CodeQL, dependency audit and non-database safety regression passed. This is not semantic entailment or legal review.
- **Score recalculation:** case-management workflow completion moves from 75% to 76%; research/retrieval/citation quality moves from 65% to 68%. Weighted technical completion is 48.50/100, rounded to 49%. Verified Egyptian legal knowledge remains 6%; qualified Egyptian-counsel acceptance remains 0%.

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
- **PR #995 merged:** aligned the five Labour Decision 248–252 Arabic title fields to the exact IDSC/Amiri Press catalogue abstract and added a regression assertion for each instrument-number/year prefix. The full 139-step Tests workflow, CodeQL and dependency audit passed; no legal-status or retrieval-eligibility flags changed.
- **PR #993 merged:** added a same-firm nonmember guessed-ID regression for `POST /deadlines/{did}/done`; the request must return 404 and leave the deadline open. The full 139-step Tests workflow, CodeQL and dependency audit passed. This is test coverage only, with no runtime/schema change.
- **Superseded branches closed:** PR #971 was closed as a duplicate of #963. PR #782 was closed after confirming its 294 canonical card IDs and its supplementary coverage are represented in current main; seven differently named Articles 258–265 cards were semantic duplicates of cards already in the canonical inventory.
- **No completion-percentage increase is claimed:** these changes improve inventory integrity, evidence traceability, tests and release controls. They do not add lawyer-approved or fully primary-source-verified legal content. Verified Egyptian legal knowledge remains 6%; technical completion remains 48%.

## Latest merged progress — 2026-10-31 (qualified-counsel retrieval gate)

- **PR #1066 merged:** passing `lawyer_approval` events now require an authenticated platform-reviewer account ID in the operator-managed `LEGAL_QUALIFIED_EGYPTIAN_COUNSEL_USER_IDS` allowlist. The API appends a machine-readable counsel-attestation marker; normal and exact-article retrieval require it; provenance, the read-only corpus audit and review queue flag missing markers. The allowlist parser rejects malformed, zero, non-ASCII, oversized and out-of-range IDs without crashing. The branch passed the full Tests workflow, CodeQL (Python and JavaScript), dependency audit, non-database safety regression, and both amd64 and arm64 container builds before merge.
- **Control limitation:** the allowlist is an operator attestation, not independent identity, bar-membership, credential, standing or review-truth verification. The allowlist must be populated and maintained through protected deployment configuration by an authorized operator. Empty configuration blocks passing lawyer-approval writes. Existing unmarked approval events do not qualify for retrieval and require controlled re-review; no existing event was automatically promoted.
- **Score recalculation:** verified Egyptian legal knowledge/source-rights workflow moves from 6% to 7% because the counsel-review gate is now enforced end to end; automated testing/reliability moves from 66% to 67% because the new regression and exact-head CI acceptance passed. Weighted technical completion moves from 48.50 to **48.85/100** (up 0.35 points; rounded display remains 49%). Verified primary-source corpus volume does not increase; final Egyptian-counsel acceptance remains 0%.

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

**Technical completion is 49.20/100** (rounded to 49%) after the merged counsel-attestation release-gate work. Final Egyptian-counsel acceptance remains **0% / not started**. Verified primary-source corpus volume remains unchanged; provisional records and secondary-source cross-checks do not count as verified law or market readiness.

## Latest merged progress — 2026-10-31 (candidate release-validator alignment)

- **PR #1067 merged:** the metadata-only legal source-to-release validator now requires each passing `lawyer_approval` record to contain the runtime counsel-allowlist marker and requires the marker's positive platform account ID to match `reviewer_id`. Regressions cover missing markers and mismatched account IDs. Tests, CodeQL, dependency audit and non-database safety regression passed on the exact PR head before merge.
- **Score recalculation:** source-to-release governance moves from 7% to 8%, and automated testing/reliability from 67% to 68%. Weighted technical completion moves from 48.85 to **49.20/100** (up 0.35 points; rounded display remains 49%). No primary-source legal text was newly verified or promoted; verified corpus volume remains unchanged at 6%, and final Egyptian-counsel acceptance remains 0%.

## Additional merged hardening — 2026-10-31

- **PR #1071 merged:** the offline counsel-marker validator now applies the runtime allowlist's positive signed-64-bit account-ID boundary. It rejects values above the maximum and arbitrarily long marker strings; tests cover the maximum valid ID, the first invalid ID, and a 5,000-digit token. This is additional validator hardening and does not change the weighted score or verified-corpus volume.
- **PR #1070 merged:** corrected the bilingual Settings warning. It no longer says multi-firm isolation is unimplemented; it accurately states that public registration and production confidential-matter use remain disabled pending production tenant-isolation tests, storage/recovery controls, retention policy, and independent security review. Copy-only; no access-control setting was changed.

## Latest merged progress — 2026-10-31 (current review-event and source-provenance consistency)

- **PR #1073 merged:** recorded the Presidency-hosted 2019 Constitution PDF locator and the page's all-rights-reserved notice. Collection and commercial reuse remain unknown; no original bytes/hash, full Gazette comparison, or post-2019 currentness review was completed. The candidate remains discovery-only.
- **PR #1074 merged:** corrected the Constitution publication crosswalk: the Presidency PDF's Gazette issue 16 repeated (w) reference belongs to an embedded referendum-results notice, while secondary metadata points to issue 15 repeated (c) for the amendment instrument. The secondary issue lead remains unverified against the original Gazette; no legal text was promoted.
- **PR #1075 merged:** the read-only legal-source review queue now lets only the latest event per review type control current eligibility; historical passes cannot override later failures or corrections, and counsel attestation is checked only on the latest lawyer-approval pass. Exact-head Tests, CodeQL and dependency audit passed.
- **PR #1077 merged:** the corpus-coverage dashboard's missing-review-evidence metric now applies the same latest-event, evidence, reviewer, notes and counsel-attestation requirements as runtime retrieval. Regression tests prove later failures/unattested approvals are counted and later valid passes restore the metric. Tests, CodeQL, dependency audit and non-database safety regression passed.
- **Score recalculation:** legal-source governance/review workflow completion moves from 8% to 8.5% because the latest-event rule is now consistent across the review queue, dashboard and runtime eligibility gate. Weighted technical completion moves from 49.20 to **49.33/100** (up 0.13; rounded display remains 49%). No legal source became verified or retrieval-eligible; final Egyptian-counsel acceptance remains 0%.

## Latest merged progress — 2026-10-31 (strict review-evidence consistency)

- **PR #1083 merged:** the runtime source-status gate, offline legal-source review queue and coverage dashboard now use one shared current-review-evidence validator. It requires the latest event per review type, a valid parsed/non-future timestamp, non-empty reviewer and notes, a credential-free HTTPS evidence URL, and the exact positive account-ID counsel marker on the latest lawyer-approval pass. Regressions cover blank notes, malformed zero-ID counsel markers, credential-bearing HTTPS URLs and future-dated events. Tests, CodeQL, dependency audit and non-database safety regression passed.
- **Score recalculation:** the legal-source governance workstream rises from 8.5% to 9.0% because current-event validation is now consistent across runtime, reviewer queue and dashboard. Weighted technical completion moves from 49.33 to **49.45/100** (up 0.12; rounded display remains 49%). This is governance progress only: no additional legal instrument was verified or made retrieval-eligible; final Egyptian-counsel acceptance remains 0%.

## Latest merged progress — 2026-10-31 (scope isolation and canonical source permissions)

- **PR #1087 merged:** candidate-source seeding now requires exactly one canonical permission-register match, matching collection/commercial-reuse states and source host. This prevents stale candidate metadata from making a source appear more permissively licensed than the canonical register. Tests, CodeQL and dependency audit passed. No legal content was imported or promoted.
- **PR #1088 merged:** research retrieval context is now limited to completed turns in the same scope and matter ID; legacy assistant messages without scope metadata fail closed. The route persists the request's scope and matter ID explicitly in assistant metadata. Tests, CodeQL, dependency audit and non-database safety regression passed. This closes a cross-scope/cross-matter context-contamination path; it does not establish production tenant-isolation acceptance.
- **PR #1081 merged:** Court of Cassation source-use record now reflects the Court's May 2026 terms and Article 141 context. It remains manual lookup/link-out only for this commercial product absent prior written approval; no ingestion, bulk extraction or commercial republication is authorized.
- **Score recalculation:** legal-source governance rises from 9.0% to 9.3% for canonical permission parity and strict evidence URL validation; security/privacy/firm isolation rises from 72% to 72.5% for tested research-context boundary enforcement. Weighted technical completion moves from 49.58 to **49.60/100** (up 0.02; rounded display 50%). This is code/governance progress only. Verified primary-source corpus volume is unchanged; final Egyptian-counsel acceptance remains 0%.

## Latest merged progress — 2026-11-01 (current-main browser acceptance and release validation)

- **PR #1093 merged:** the offline legal release validator now applies the same strict HTTPS URL-shape checks as the runtime/review evidence paths. The exact PR head passed Tests (1,392 tests across 128 scripts), CodeQL, dependency security audit and non-database safety regression.
- **PR #1078 merged:** the synthetic Playwright/Chromium acceptance harness passed **6/6 browser tests** on its exact head. The full Tests workflow passed **1,391 tests across 128 scripts**; CodeQL, Bandit, dependency audit and non-database safety regression also passed. Coverage includes platform-reviewer authorization, metadata-only corpus drill-down, firm-document versus verified-corpus separation, cross-firm case isolation, expired sessions, Arabic RTL/English LTR, mobile overflow, keyboard focus, loading/error states, citation copy, passage copy, memo export and case-note save.
- **Browser follow-up cleanup:** #1057 and #1068 were closed as superseded by #1078. Manual lawyer, physical-device, screen-reader and accessibility acceptance remain separate outstanding gates.
- **Score recalculation:** legal-source governance/review moves from 9.3% to 9.6% after #1090, #1092 and #1093 complete latest-event audit, exact canonical permission parity and strict release-validator URL checks. Automated testing/reliability moves from 68% to 69% after the merged 6/6 Chromium acceptance and exact-head full-suite/security checks. Weighted technical completion moves from **49.60 to 49.78/100**. This is engineering-control progress only: verified primary-source Egyptian legal corpus remains 6%, and final Egyptian-counsel acceptance remains 0%.

## Additional merged progress — 2026-11-01 (evaluation evidence integrity)

- **PR #1095 merged:** legal-answer evaluation and qualified-human review summary CLIs refuse to overwrite existing report files. A collision returns exit code 2 and leaves the original bytes unchanged; the human-review CLI's process exit status is verified through a subprocess regression.
- **PR #1098 merged:** both report types now record SHA-256 and byte size for the exact input artifacts parsed, plus a UTC host-clock generation timestamp. Local paths and raw input contents are omitted. The report explicitly disclaims cryptographic authenticity, reviewer qualification and trusted timestamp guarantees.
- **Initial assessment:** the first evidence-integrity checkpoint did not recalculate the score; the subsequent 69.5% reliability recalculation is recorded below and supersedes that provisional assessment.

## Score recalculation — 2026-11-01 (evaluation evidence integrity)

- **PR #1095 merged:** no-clobber report writing prevents reruns from silently replacing existing legal-answer evaluation or human-review summary evidence. The actual human-review CLI exit status is covered by a subprocess regression.
- **PR #1098 merged:** report provenance now identifies exact question, result, review-record and reviewer-registry input bytes by SHA-256 and size, while omitting local paths and contents and disclaiming trusted timestamp/authenticity claims.
- **Automated testing and reliability** moves from 69% to 69.5% for the additional evidence-preservation and reproducibility controls and their exact-head regression coverage. Weighted technical completion moves from **49.78 to 49.83/100** (up 0.05).
- This remains engineering/evidence-integrity progress only. Verified Egyptian legal corpus remains 6%; final Egyptian-counsel acceptance remains 0%.

## Score recalculation — 2026-11-01 (SMTP ambiguous-submission safety)

- **PR #1102 merged:** the reminder adapter now quarantines transport failures after SMTP submission starts as `smtp_submission_ambiguous` and does not automatically retry. Explicit SMTP 4xx rejections remain retryable; confirmed SMTP acceptance followed by close/QUIT failure does not trigger a resend.
- **Production operations and deployment readiness** moves from 35.0% to 35.2% for this code-level duplicate-risk control and its regression coverage. Weighted technical completion moves from **49.83 to 49.85/100** (up 0.02).
- This is not production-delivery acceptance. Live SMTP provider staging, credentials, external scheduler monitoring, provider reconciliation and independent operational recovery review remain outstanding.

## Pending review candidates — 2026-11-01

- **PR #1105:** explicit Arabic answer/source polarity conflict guard. Exact-head Tests (151/151), browser acceptance, non-database safety regression, dependency audit, Bandit and CodeQL passed. Product-owner approval remains pending; the change is not included in the weighted score.
- **PR #1106:** ten additional synthetic Egyptian colloquial retrieval scenarios across practice areas. Exact-head Tests (150/150), browser acceptance, dependency audit and CodeQL passed. Product-owner approval remains pending; the test-only change is not included in the weighted score.
- **PR #1099:** closed as superseded by current-main PR #1106. No unique implementation was discarded.


## Latest merged progress — 2026-11-01 (candidate catalogue denominator integrity)

- **PR #1108 merged:** the corpus-coverage dashboard now requires each candidate catalogue record to have a non-empty stable instrument ID, normalizes whitespace before duplicate detection, rejects duplicate/missing IDs from the candidate denominator, and validates the plural practice_areas field as a list while preserving the legacy singular practice_area string form.
- Regression coverage verifies duplicate IDs, whitespace variants, missing/blank IDs, malformed plural area values, non-object entries, and the distinction between invalid identity (excluded from denominator) and a valid instrument with unknown practice-area classification (included under unknown).
- Exact-head CI passed Tests (150/150 workflow steps), Browser acceptance, non-database safety regression (24/24), dependency security audit, Bandit, Python CodeQL and JavaScript CodeQL.
- **Score recalculation:** verified Egyptian legal knowledge/source-governance workflow moves from 9.6% to 9.7% for improved integrity of candidate-inventory denominators and diagnostics. Weighted technical completion moves from **49.85 to 49.88/100**. This is a metadata-governance improvement only; verified Egyptian legal corpus remains 6%, and final Egyptian-counsel acceptance remains 0%.


## Latest merged progress — 2026-11-01 (Research Source Inspector keyboard acceptance)

- **PR #1111 merged:** Chromium acceptance now exercises the Research Source Inspector using keyboard-only navigation: Tab traversal from search scope and matter selectors through the conversation list to the composer and submit control, followed by Enter-key submission and the metadata-only empty-result state.
- **PR #1115 merged:** the keyboard traversal bound is derived from the page's actual focusable controls, avoiding a fixed conversation-list size assumption in the shared synthetic browser fixture.
- Exact-head validation for #1115 passed Browser acceptance (10/10), Tests (150/150 workflow steps), dependency audit, Bandit, Python CodeQL and JavaScript CodeQL.
- **Score recalculation:** UI/accessibility automated acceptance moves from 45.0% to 45.2% for the additional end-to-end keyboard workflow. Weighted technical completion moves from **49.88 to 49.90/100**. This is automated keyboard coverage only; screen-reader, physical-device, manual RTL/LTR and lawyer workflow acceptance remain outstanding.
- Verified Egyptian legal corpus remains 6%; final Egyptian-counsel acceptance remains 0%.


## Latest merged progress — 2026-11-01 (MFA audit integrity)

- **PR #1120 merged:** added fault-injection coverage for MFA verification audit failure. The test proves a recovery code remains unused, the session remains unverified, and no partial audit event is persisted when the audit insert fails.
- Added regression coverage for append-only MFA security events: UPDATE and DELETE attempts raise SQLite integrity errors and leave the original event intact.
- Exact-head CI passed Tests (149 workflow steps), Browser acceptance (10/10), dependency security audit, Bandit, Python CodeQL and JavaScript CodeQL.
- Automated testing and reliability increases from 69.5% to 69.6%; weighted technical completion increases from **49.90 to 49.91/100**. No Egyptian-law verification, rights clearance or counsel acceptance is claimed by this engineering test work.
- Verified Egyptian legal corpus remains 6%; final Egyptian-counsel acceptance remains 0%.
