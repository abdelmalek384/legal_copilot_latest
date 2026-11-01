# Legal Copilot — Project Progress Tracker

**Last updated:** 2026-11-01 (current whole-product checkpoint; historical snapshots retained; workstream percentages are not additive)
**Tracking method:** deliverable-level checklist, not an estimate of engineering hours. A task is “complete” only when its change is merged and its acceptance criteria are met. Open PRs are in progress, not complete.

## Overall status

See [the weighted whole-project completion scorecard](project_completion_scorecard.md): **49.90/100 technical completion** (up 0.02 points from 49.88; rounds to 50%) as of 2026-11-01. Final Egyptian-counsel acceptance is **0% / not started** and remains a separate mandatory post-build release gate. Open PRs are not counted as completed work.


## Previous whole-product checkpoint — 2026-10-31

At that checkpoint the weighted scorecard recorded **49.33/100 technical completion** (up 0.13 points from 49.20; rounds to 49%). The current score is shown in the overall status above. Qualified Egyptian-counsel acceptance remains **0% / not started** and is still a mandatory post-build release gate.

### Merged since the 30 October checkpoint and 31 October follow-up

- **#945:** patched pypdf to 6.21.4 and refreshed the hash-locked Python 3.12 deployment lock. Tests, dependency audit, CodeQL and container build passed.
- **#946:** identified Ministerial Decision 162/2026 and added a secondary-text crosswalk to Labour Law 14/2025. The original Gazette PDF remains unhashed/uninspected; the record remains discovery-only.
- **#944:** recorded the Supreme Constitutional Court public recent-judgments page and a third-party-described API lead. No API calls or bulk collection were made; rights remain unknown.
- **#931:** registered الذاكرة والمعرفة للدراسات as a legal-document discovery source. Its stated CC BY 4.0 scope over underlying texts and database compilation remains unresolved; no text was imported.
- **#784:** closed as superseded by #946.
- **#963:** merged the reconciled 360-card Labour Law No. 14/2025 candidate inventory and manifest. Full 138-step Tests, CodeQL and dependency audit passed on the final head. All 360 cards remain search_eligible=false; no verified-corpus percentage increase is claimed.
- **#967:** merged additional visual checks of Labour Law Article 13 and printed Gazette pages 94–111, correcting 90 pinpoints for Articles 250–298. Original PDF bytes/hash, reuse rights, currentness and counsel review remain outstanding.
- **#834 and #983:** merged the updated SEC-01 storage attack-surface inventory and S3 purge acceptance checklist. Live S3/KMS/IAM evidence, retention approval, and witnessed recovery/deletion remain open.
- **#987:** merged Decision 250 Table 24 source-rights metadata for Riwaq and Law Hub. The secondary transcription remains link-out only; no row-level content was imported. Law Hub's terms restrict profiting by republishing its free site materials.
- **#989:** merged metadata-only inventory entries for Labour Decisions 248–252/2026, source-rights records and a secondary-source matrix. Both the 6.13 MB Gazette PDF and 55-byte item-specific license.txt are request-copy restricted; no original bytes, licence text or hash were obtained. All five instruments remain discovery-only.
- **#990:** merged same-firm nonmember task-claim/task-completion authorization regression coverage; unauthorized actions return 404 and leave task state unchanged. Full Tests, CodeQL and dependency audit passed.
- **#995:** aligned Decisions 248–252 Arabic title fields to the exact IDSC/Amiri Press catalogue abstract and added regression assertions for the instrument-number/year prefixes. Full 139-step Tests, CodeQL and dependency audit passed.
- **#993:** added same-firm nonmember guessed-deadline-ID completion coverage; unauthorized completion returns 404 and the deadline remains open. Full 139-step Tests, CodeQL and dependency audit passed; no runtime/schema changes.
- **#782 and #971:** closed as superseded after card-ID reconciliation; no unique canonical card IDs were discarded. #782's remaining seven differently named Articles 258–265 cards were semantic duplicates already represented in main.
- **#1044 and #1047:** merged the Law 14/2025 accompanying-law Articles 1–120 Gazette checklist and populated all 120 article-heading page locators from the ETA-hosted Official Gazette PDF. The corresponding page images for printed pages 6–52 / PDF indexes 4–50 were inspected for locator confirmation. This is not a full article-text/OCR comparison; all verification, currentness, rights and counsel gates remain open, and every card remains `search_eligible=false`.
- **#1048:** merged the invoice-module implementation contract covering invoice lifecycle, line items, exact EGP amounts, append-only payments, derived payment states, firm/case authorization, print/export and required regression tests. This is a schema-review proposal, not invoice implementation; table/API/UI work remains gated on database-owner approval.
- **#1049:** corrected the Law 14/2025 Gazette source-evidence register to record the IDSC item-specific Gazette PDF and license file as request-a-copy/restricted, and added a regression test for the restricted collection-permission state. No restricted files were obtained; commercial reuse remains unapproved.

- **#1052:** integrated the existing deadline calculator into the case Legal Deadlines screen as an authenticated, read-only preview; rules and holiday data remain unverified, so no legal reliance is permitted.
- **#1053:** expanded Egyptian colloquial retrieval hints across major practice areas; this is retrieval-only and has no lawyer-labelled accuracy benchmark yet.
- **#1054:** added a fail-closed lexical citation-relevance guard; this checks textual anchors, not semantic entailment or legal correctness.
- **#1066:** merged the qualified-counsel approval gate. Passing lawyer-approval events require an authenticated account ID from the operator-managed allowlist; the marker gates normal/exact retrieval and is checked by provenance, corpus audit and reviewer queue. Full Tests, CodeQL, dependency audit, non-database safety regression, and amd64/arm64 container builds passed. This is operator attestation, not independent credential verification; no primary-source legal material was promoted.
- **#1067:** merged the matching offline source-to-release validator gate. A passing candidate lawyer-approval record must carry the same runtime marker and its positive account ID must match `reviewer_id`. Missing/mismatched marker regressions passed Tests, CodeQL, dependency audit and non-database safety regression. No legal source was promoted.
- **#1065:** merged the refreshed project progress tracker and active release-gate record.
- **#1070:** corrected the Settings release warning in Arabic and English to describe the remaining production acceptance gates without falsely stating that tenant isolation is unimplemented.
- **#1071:** aligned offline counsel-marker ID validation with the runtime positive signed-64-bit allowlist boundary; malformed/out-of-range marker regressions passed all required CI.
- **#1072:** refreshed the scorecard/tracker after merged UI and validator hardening.
- **#1073:** recorded the Presidency-hosted 2019 Constitution PDF locator and all-rights-reserved notice; rights, original bytes/hash, Gazette comparison and post-2019 currentness remain unresolved.
- **#1074:** distinguished the referendum-results Gazette reference from the amendment-instrument publication lead; the latter remains secondary and unverified.
- **#1075:** made the legal-source review queue honor the latest review event per type; stale passes no longer override later failures or unattested counsel approvals.
- **#1077:** aligned corpus-coverage missing-review metrics with the runtime latest-event eligibility gate; regression tests cover failure, unattested approval and restoration by a later valid pass.
- **#1079:** refreshed the weighted scorecard and progress tracker after the latest-event governance improvements.
- **#1080:** added the National Elections Authority's official 2014/2019 Constitution PDF locator and its all-rights-reserved notice; permissions remain unknown and the candidate remains discovery-only.
- **#1083:** consolidated strict current-review-event validation across runtime, offline queue and coverage dashboard; all required CI and safety checks passed.
- **#1087:** made candidate source seeding fail closed unless exactly one canonical permission-register entry matches source host and both permission states; all required CI passed.
- **#1088:** restricted retrieval context to completed turns in the same search scope and matter ID, persisted explicit scope/matter metadata, and failed closed for legacy metadata-less turns; all required CI and safety checks passed.
- **#1089:** tightened the shared evidence URL parser to reject whitespace/control characters, credentials, malformed ports and empty port suffixes across source, review and permission evidence URLs; Tests, CodeQL and dependency audit passed.
- **#1081:** merged Court of Cassation use-policy reconciliation; commercial product remains manual lookup/link-out only absent prior written approval.


### 31 October live follow-up — additional merged work and active gates

The weighted scorecard has now been recalculated to **49.45/100** after #1066 and #1067 met their merged acceptance criteria. This is a technical-governance increase; verified primary-source corpus volume remains 6%, and counsel acceptance remains 0%.

**Merged after the preceding checkpoint:**

- **#1037:** bounded model-response reads in the application and evaluation CLI. Tests, CodeQL, dependency audit and non-database safety regression passed.
- **#1058:** integrated deadline-calculation assumptions and explanatory source-basis details, and expanded Egyptian Arabic retrieval hints. All four required checks passed. This remains a calculation/retrieval aid, not verified legal deadline advice.
- **#1060:** added production-path synthetic retrieval regression tests using fictional fixtures. These validate isolation/citation plumbing, not real-world legal accuracy.
- **#1061:** added the Ministry-hosted Decision 294/2025 text copy and source-rights safeguards. Decision 294 remains discovery-only; Gazette comparison and reuse rights remain open.
- **#1056:** added an AI case brief with bounded matter context, citation validation, common-identifier redaction, a separate deployment gate, explicit firm/client authorization attestations, and an activity-log record committed before model transmission. All four required checks passed. The attestations are user assertions, not independent proof of consent; no provider/live data-processing acceptance is claimed.
- **#1062:** updated Decision 290/2025's intermittent-work crosswalk using secondary full-text corroboration and third-party repository metadata. The MELES PDFs were not obtained; the Gazette PDF remains request-a-copy restricted. Decision 290 remains G3/discovery-only, not G4.
- **#1064:** recorded the Ministry's 2026-10-27 clarification lead for Decision 249/2026. The indexed result is not the full decision or a Gazette amendment; direct page retrieval failed, rights remain unknown, and the instrument stays discovery-only.

**Open PRs — not complete until merged and all required checks pass:**

- **#1105:** Arabic answer/source polarity guard; all exact-head checks passed, but explicit product-owner approval remains pending.
- **#1106:** ten additional synthetic Egyptian colloquial retrieval scenarios; all exact-head checks passed, but explicit product-owner approval remains pending.
- **#840:** remains draft/open; Decisions 248–252 and Table 24 source comparison remain discovery-only pending lawful original Gazette access, item-specific rights evidence and primary-source comparison.

**Superseded PR:**

- **#1063:** closed as superseded by rebased PR #1064 after Decision 290's merge changed shared evidence-register files.

**Operational issue updates:**

- **#473 MFA:** implementation primitives and recovery CLI are present; actual secret-manager provisioning, authenticator/lost-device rehearsal, two-admin recovery rehearsal and independent security review remain open.
- **#474 reminders:** planner, durable outbox, dry-run scheduler and monitoring/runbook are present; real SMTP acceptance, host scheduling, provider timeout/rotation rehearsal and operator reconciliation remain open.
- **Invoices:** PR #1048 remains an implementation contract only. No invoice schema/API/UI work is authorized without explicit database-owner approval.
- **AWS/storage:** live bucket, KMS, IAM, conditional-delete, writer-quiescence and witnessed restore/deletion acceptance still require the actual staging account and named operator evidence.
- **Legal authority:** none of the six 2025 Labour working-time/holiday decisions is promoted to authoritative status by these changes. All dependent cards remain search_eligible=false pending original-source comparison, source-specific rights, currentness and qualified Egyptian-lawyer review.


### Current open PRs and acceptance

- **#1078 merged:** synthetic browser acceptance passed 6/6 tests on the exact head; the full 1,391-test workflow, CodeQL, Bandit, dependency audit and non-database safety regression passed. This is automated acceptance only; manual lawyer/device/screen-reader/accessibility acceptance remains open.
- **#1057 and #1068:** closed as superseded by #1078; no unique implementation was discarded.
- **#1093 merged:** strict HTTPS URL validation is now aligned in the offline release validator and the runtime/review evidence validators.
- **#1095 merged:** evaluation and human-review report writers now refuse to overwrite existing evidence files; the human-review CLI propagates exit code 2 and is covered by a subprocess regression.
- **#1098 merged:** both evaluation report types now include exact-input SHA-256 hashes, byte counts and a UTC host-clock timestamp without exposing input paths or contents.
- **#1102 merged:** post-submission SMTP timeouts/disconnects are quarantined as ambiguous and are not automatically retried; explicit 4xx rejections remain retryable.
- **#1104 merged:** manual UI, accessibility, device and counsel-acceptance runbook prepared; it does not claim manual acceptance.
- **#1105 and #1106:** exact-head checks passed; both await explicit product-owner approval and are not counted as merged progress.
- **#1099 closed:** superseded by current-main #1106.
- **#1034 closed as completed:** its automated browser-acceptance scope is delivered by #1078; manual lawyer/device/screen-reader acceptance remains separate.
- **#840:** remains draft/open; Decisions 248–252 and Table 24 source comparison remain discovery-only pending lawful original Gazette access and rights review.

### Current non-database priorities

1. Keep #840 in draft. Continue lawful primary-source comparison for Decisions 248–252; original Gazette matches remain 0/5 and Table 24 matches remain 0/781. Do not merge its row-level secondary transcription while original bytes, item-specific licence text and reuse rights are unresolved.
2. Complete exact Gazette-text and OCR discrepancy comparison for the 120 checklist articles against the canonical candidate data when the approved source artifact is available; do not infer matches from page locators. Obtain original PDF bytes/hash through authorized access and resolve collection/reuse rights, later-instrument currentness and qualified Egyptian-lawyer review.
3. Obtain database-owner approval for the invoice logical model and tenant boundary before implementing invoice schema, API or UI. Existing `fees` rows remain recorded-fee summaries, not invoices.
4. Continue primary-source discovery and provenance checks for Egyptian legislation and Court of Cassation / Constitutional Court decisions. Keep secondary sources out of authoritative retrieval and preserve source-specific reuse restrictions.
5. Complete real lawyer-labelled retrieval/citation evaluation against exact reviewed source versions and pinpoint citations; no qualified-counsel benchmark run has been completed.
6. Complete manual Arabic RTL/LTR, accessibility, mobile/browser and lawyer-workflow QA.
7. Complete staging operations, monitoring, operator reconciliation and witnessed backup/restore after the separate DB/storage workstream is ready.

Database/tenant schema, migration, identity and destructive storage changes remain assigned to the separate DB workstream and are not duplicated here.

## Current workstream snapshot — 2026-10-27

**Important:** These percentages are rough, reviewable workstream estimates—not a claim that the product is market-ready. They measure visible engineering/evidence progress and are not directly additive. The legacy 7/20 tally below is not refreshed to include every recent workstream and must not be quoted as the current overall project completion percentage.

| Workstream | Estimate | Status | Evidence / next gate |
|---|---:|---|---|
| Verified Egyptian legal knowledge | 15% | **Blocked / lagging** | Source registry and permission gates exist; PR #684 documents the staged verification roadmap. Still requires permission-cleared primary texts, provenance/hash records, amendment/currentness review, and qualified Egyptian-lawyer sign-off. |
| Research retrieval, citations, evaluation | 65% | **Progressing** | Open PRs #668, #670, #675, #677, #678, and #680 address citation parsing/report preservation, future-effective retrieval, retrieved-source citation scoring, abstention metrics, and source-status consistency. They remain incomplete until merged and reviewed; real lawyer-labelled runs are still needed. |
| Legal corpus auditability | 70% | **Progressing** | Open PRs #681–#683 add read-only checks for evidence behind verification flags, review-event integrity, and chunk/version consistency. These audits report contradictions; they do not authenticate sources or repair records. |
| Security and tenant isolation | 70% | **Progressing; release-gated** | Multiple security/control-plane safeguards have merged; open PR #671 concerns private tenant-namespaced original-file storage and belongs to the database/storage workstream. Independent security review, full route/job isolation validation, and witnessed recovery testing remain release gates. |
| Test stability and release readiness | 60% | **At risk / validation needed** | The supplied handoff reported 85/88 scripts passing and three failures (Arabic matching, tenant-storage test, and separate-database dashboard HTTP 500). Those results came from a user-supplied report and have not been independently reproduced here; rerun against the current commit before treating them as current. |
| UI, accessibility, manual QA | 40% | **Lagging / unverified** | Existing checklists and prior UI fixes exist, but full manual RTL/LTR, keyboard, screen-reader, browser and lawyer-workflow evidence is still outstanding. |
| Production / paid pilot readiness | 35% | **Blocked by prerequisites** | Do not launch or market legal verification, deadline correctness, paid workflows, or broad coverage until corpus rights/review, evaluation, security, recovery, and manual QA gates pass. |

### Current open work requiring review

- **#684** — phased roadmap for verified Egyptian legal knowledge; test check passed.
- **#682** — read-only review-event integrity audit; its test check passed.
- **#683** — read-only chunk-to-version consistency audit; its test check passed.
- **#681** — evidence-backed verification flags audit; recheck latest CI before review.
- **#680, #678, #677, #675, #670, #668** — research/evaluation improvements; check current CI and merge status before counting as complete.
- **#667** — earlier tracker refresh PR; verify whether it is still useful after this snapshot and avoid conflicting tracker edits.
- **#671** — original-file storage adapter; separate database/storage workstream, not modified by this snapshot.
- **#685** — this tracker refresh; test check passed after the snapshot was authored.
- **#686** — Markdown renderer now displays review-event and chunk/version audit metrics; test check passed.
- **#687** — Arabic hamza test assertions aligned with canonical token normalization; test check passed. This is test-only and does not change runtime normalization.
- **#688** — local manual-capture provenance validator and operator guide; CI is in progress. It never marks content retrieval-eligible.

### Immediate priority order

1. Review/merge only after CI and diff review; do not treat open PRs as completed.
2. Finish the non-DB legal-source roadmap and instrument-level checklists; keep actual legal content blocked until source rights and qualified review are evidenced.
3. Run the current test suite and record exact command, commit SHA, pass/fail totals, and each failure.
4. Complete real lawyer-labelled retrieval evaluation and manual UI/accessibility QA.
5. Keep DB/storage migrations and irreversible tenant-data actions with the database workstream owner; require explicit approval for risky production actions.
- **Completed and merged:** 7 of 20 tracked deliverables (**35.0%**).
- **In progress:** 8 of 20 deliverables (**40.0%**).
- **Not started, blocked, or awaiting validation:** 5 of 20 (**25.0%**).
- **Merged PRs from this workstream:** #88, #89, #90, #91, #92, #94, #96, #97, #98, #99, #100, #101, #102, #103, #104, #105, #106, #107, #108, #109, #110, #112, #114, #115, #116, #117, #119, #120, #121, #123, #126, #130, #131, #133, #135, #172, #180, #182, #183, #184, #186, #187, #188, #189, #190, #191, #192, #193, #194, #195, #196, #198, #199, #200, #201, #202, #203, #204, #205, #206, #208, #216, #218, #221, #223, #227, #232, #234, #237, #239, #241, #245, #246, #247, #248, #249, #250, #251, #252, #253, #254, #255, #256, #257, #258, #259, #260, #261, #262, #263, #264, #265, #266, #267, #268, #269, #270, #271, #272, #273, #274, #275, #276, #278, #279, #280, #281, #282, #283, #285, #286, #289, #290, #291, #292, #293, #294, #295, #296, #297, #298, #299, #300, #302, #304, #305, #306, #307, #308, #309, #310, #311, #312, #313, #314, #315, #316, #317, #318, #319, #320, #321, #322, #323, #324, #325, #326, #327, #328, #329, #330, #331, #332, #333, #334, #335, #336, #337, #338, #339, #340, #341, #342, #343, #344, #345, #346, #347, #348, #349, #350, #351, #352, #353, #354, #355, #356, #357, #358, #359, #360, #361, #362, #363, #365, #366, #367, #368, #369, #370, #497, #499, #500, #504, #513, #516, #518, #538, #540, #544, #561, #564, #568, #569, #570, #571, #572, #574, #575.
- **Recent merged work and remaining boundary:** PR #183 hardens research-inspector date/provenance validation; #184 makes database profile binding immutable; #186–#192 refresh progress tracking and harden migration/tenant-catalog safeguards; #193 requires structured review evidence for confirmed amendment relationships; #194 prevents incomplete extracted text from being misclassified in legal-version comparisons; #195 adds a catalog-backed tenant connection-routing foundation; #196 adds citation coverage and expected pin-cite recall; #327–#330 further harden corpus review and source-link workflows; #345 and #351 add metadata-discovery regression tests, #348 counts unknown permission states as blocked, #353 rejects whitespace-only discovery queries, and #356 hardens memo provenance by preserving recorded scope/date, rejecting malformed passage quotes, and making empty states scope-specific; #367 adds a lawyer opinion checklist for source/data rights; #368 keeps export filenames faithful to valid recorded dates; #369 adds manual QA cases for memo provenance; #362/#363/#366/#370 harden and document tenant SQLite sidecar safety. PR #497 rejects future-dated source-terms review evidence; #499 requires an explicit minimum lawyer-reviewed sample for legal-answer quality gates and validates practice-area labels; #500 rejects malformed source-manifest/question-seed structures; #504 measures preservation of annotated legal-critical OCR tokens; and #513 adds a read-only source-to-release gate requiring explicit rights scope, original-file hash integrity, verified legal status, and passed source/extraction/amendment/licensing/lawyer review records. #516 refreshes the tracker; #518 strengthens benchmark practice-area coverage; #538 adds protected-temporary-restore backup verification (not a witnessed recovery drill); and #540 adds a standalone deadline arithmetic prototype that remains unverified and is not wired into matter deadlines. PR #544 adds the append-only control-plane audit schema and transactional CLI password-reset logging; PR #561 adds lifecycle audit events and a bounded read-only audit CLI; PR #564 tightens membership/audit transaction atomicity and is pending CI. PR #568 adds transactional web password-change audit logging with a forward migration that preserves event history; PR #569 adds transactional audit events for web membership creation and suspension. PR #570 adds audited operator-only platform-role grant/revoke commands with last-admin protection. PR #571 blocks production startup with legacy shared-database configuration; PR #572 enforces trusted-host, secure-cookie, HTTPS-origin, admin-token, and backup-key requirements at startup. PR #574 fixes firm switching after membership suspension for existing sessions and adds an integration regression test; route-wide lifecycle verification remains open. PR #575 prevents direct deadline arithmetic callers from marking an unreviewed period as legally verified; CI passed. These changes are merged, but they do not establish legal correctness or production readiness. PR #195 and #198 were early foundations; PR #372 subsequently wired authenticated session/membership checks into the separate-runtime request path for fresh installs. This is not production release approval: exhaustive route/query/background-job isolation, operational recovery, retention/monitoring, and independent security review remain outstanding. PR #200 revokes a cached connection on the current thread after catalog validation fails; #201 adds a regression test that same-firm connections are distinct across threads and are closed by their owning thread. These are foundations, not a substitute for request authorization or global revocation of already-running work. PRs #202–#205 contain follow-on tracker and tenant-connection lifecycle work; the database workstream remains with its assigned contributor. PR #206 adds bounded query-side Arabic variants for reported case-file search misses and token-order-insensitive preliminary conflict matching; it changes neither stored source text nor database/index contents. PR #216 adds 61 draft Arabic labour-law evaluation questions and a lawyer worksheet; #221 adds structural checks while keeping the answer key blank until legal review. PR #218 hardens login lockout, bounds concurrent password hashing, moves scrypt outside SQLite write transactions, and rejects common predictable passwords; production still needs MFA, shared/edge rate limiting, independent security review, and load testing. PR #223 improves responsive layout and selected text sizes, but manual RTL/LTR/accessibility QA remains outstanding. PR #227 adds a firm- and case-scoped recorded-fee overview; it is not invoicing, accounting, payment processing, or a currency-aware ledger. PR #232 exposes unassigned tasks only within cases the user may access and adds an atomic single-claim action with regression tests for outsider denial and duplicate claims. PR #234 displays calendar days remaining or overdue age on due-date pills; it is date arithmetic, not statutory-deadline calculation. PR #239 exports accessible tasks, hearings, and open deadlines for the next 90 days as iCalendar; users can import it into a calendar app, but this is not an automatic notification service or a statutory-deadline calculator. PR #241 adds the export action to the agenda screen. PR #245 normalizes standalone carriage returns before escaping iCalendar text fields and adds regression coverage for CR/LF, backslashes, commas, and semicolons; this prevents raw carriage returns in user-controlled text from becoming injected calendar content lines. DB-03 (#131) catalog/provisioning, DB-04 (#133) schema-boundary contract, and DB-05 (#135) profile-aware migration harness remain foundations rather than end-to-end isolation. The checksum-verified migration runner exists, but legacy startup schema/ALTER statements still need incremental conversion. PR #119's data-ownership/migration map remains a draft. PR #251 records the approved identity/membership direction; #252 adds Unicode-normalized email handling to login/reviewer checks and a read-only normalized-email collision audit; #253 adds fresh control-plane global identities, many-to-many firm memberships and separate platform roles; #255 reconciles the storage audit with the approved target; #259 adds a tested control-plane membership lookup helper but does not wire authenticated requests or sessions into tenant routing. These are foundations only: no legacy identities are merged, and runtime request/session integration, legacy reconciliation, per-firm backup/restore, and end-to-end sentinel isolation remain outstanding. PR #256 prevents missing or unknown research scopes from receiving a verified label; #260 prevents malformed non-string passages from being presented as exact legal quotations and keeps missing memo scope explicitly unknown; #258 and #265 improve memo-download and clipboard failure handling. PR #275 adds a manual QA checklist but is not a completed QA record; #279 makes source hosts visible and rejects credential-bearing HTTPS URLs; #281 fixes actual DOM application of ARIA/data/role attributes and announces research loading/result/error states; #285 returns exact source-word forms matched by expanded Arabic retrieval for highlighting without rewriting passages or changing ranking; #296 preserves diacritic-bearing surface forms; #293 verifies the matched-terms API contract; and #300 explains source-status labels and displays the original source host in the main result panel. These changes do not replace manual browser/screen-reader review or lawyer validation.  PR #305 makes research-memo empty states match the recorded scope; #309 adds coverage-workspace language-switch regression coverage; #310 aligns UI empty states with verified-corpus, firm-document, metadata-only, and unknown scopes; #315 protects Arabic diacritic/tatweel normalization and negation-token retrieval; #316 protects the private matter-evidence status boundary; #318 adds admin-only shared-registry drill-downs from coverage metrics, with bounded parameterized queries and no matter-passage output. PR #320 adds search controls to registry drill-downs so reviewers can find records beyond the default first 100; #322 supports Enter-key submission. PR #321 adds a repeatable manual QA checklist for the coverage dashboard and aligns memo QA expectations with scope-aware empty states. PR #324 adds permission-state filters and keyboard-accessible drill-downs from permission summaries; #325 reads persisted research scope from the stored result and uses the correct historical question when launching metadata discovery. These changes are automated-test-backed; browser/RTL manual review remains outstanding. PR #123's read-only ownership preflight detects selected anomalies but does not migrate data. PR #126 quarantines unclassified ownership and denies unclassified logins but does not undo historical misassignment or route databases by tenant. Schema parity, legacy-data migration, per-firm backup/restore, and end-to-end sentinel isolation remain outstanding.
- **External permission requests:** not sent by this project workflow. Claude is expected to handle outreach; approval is not assumed.
- **Manual UI QA:** not yet completed.

Percentages count the 20 deliverables actually listed in this register equally; they are not a claim about engineering hours or total product capability.

## Task register

| ID | Deliverable | Status | Evidence / next action |
|---|---|---|---|
| UI-01 | Responsive workspace baseline and dashboard shortcuts | Complete | Merged PR #88 |
| UI-02 | Keyboard navigation, skip link, language-switch and modal accessibility | Complete | Merged PR #89; manual assistive-technology QA remains a separate task |
| UI-03 | Saved research search/rename and safer source-link handling | Complete | Merged PR #91; this is not the complete source-inspector workflow |
| SRC-01 | Permission outreach tracker, official contact verification and permission-gate tests | Complete | Merged PR #90; verified contact does not mean permission granted |
| DATA-01 | Document permission-aware corpus strategy and alternatives | Complete | Merged PR #92; alternatives remain useful if permissions are declined |
| DATA-02 | Corpus coverage/provenance dashboard and admin-only metrics API | Complete | Merged PR #94; coverage remains a registry metric, not total-law coverage |
| DATA-03 | Review terms and reuse conditions for every proposed external source | In progress | Merged PR #98 records WIPO/ILO policy limits; PR #105 adds Labour Law 14/2025 source review metadata; #497 rejects future-dated review evidence and #513 enforces source/document permission scope before release; Egyptian primary portal terms and item-level rights remain unresolved |
| DATA-04 | Prioritized Egyptian instrument metadata inventory | In progress | Merged PR #97 adds structural/permission-state validation and CI tests for the 69-record inventory; PR #105 adds Labour Law 14/2025 review metadata; #500 hardens malformed-input handling and #513 adds a source-to-release evidence gate; candidates remain metadata-only until original texts, reuse scope, and review approvals are complete |
| DATA-05 | Expand the verified starter corpus using permitted acquisition routes | Blocked / ongoing | Depends on lawful source copies, source-specific terms, and lawyer validation; continue metadata discovery meanwhile |
| DATA-06 | Firm-supplied document ingestion with provenance and tenant scoping | Complete | Merged PR #100 adds per-upload SHA-256, uploader/firm metadata, extraction/OCR state and chunk-to-document linkage; binaries are not retained; duplicate uploads remain separate records |
| DATA-07 | OCR/extraction review against original pages | In progress | Merged PR #101 adds audited extraction correction; merged PR #103 adds reviewer-entered page references, stale-correction rejection, and compare-and-swap updates; #504 adds critical-token recall for article numbers, dates, amounts, and negation/proviso phrases; representative permission-cleared court scans and reviewer UI remain outstanding |
| RSH-01 | Full research result/source inspector with exact passages and pin-cites | In progress | Merged PR #96 adds explicit scopes, status labels, passage/citation actions, optional page pin-cites with migration, memo export/save, and metadata-only discovery; #256/#260 add fail-closed source-scope and malformed-passage safeguards; #275 provides a manual QA checklist (not evidence of completed QA); #279/#300 show source hosts; #285/#296 highlight actual matched source-word forms including diacritic-bearing Arabic; #300 adds plain-language status explanations. Existing chunks without page metadata remain unpinned; browser and lawyer review remain outstanding |
| RSH-02 | Arabic retrieval evaluation set and citation-quality metrics | In progress | Merged PR #99 adds Recall@k/MRR and citation metrics; PR #196 adds answerable-case citation coverage and expected pin-cite recall; PR #206 improves targeted Arabic query matching; #285/#296 expose matched surface terms and preserve diacritics for highlighting; #293 verifies the API contract but none of these is a retrieval-quality benchmark. PR #216 adds 61 draft labour-law questions and a lawyer worksheet; #221 checks structure and blank answer/source fields; #499 adds a minimum lawyer-reviewed sample-size gate. No legal quality score is valid until an Egyptian lawyer approves the answer key and real evaluation runs exist |
| RSH-03 | Amendment/repeal graph and historical version comparison | In progress | PR #182 adds read-only extracted-text comparison; PR #193 requires a structured Gazette/reviewer evidence record, real review dates, provision mapping, and known effective date for `reviewed_confirmed` relationships; PR #194 marks article comparisons uncomparable when extraction text is incomplete; PR #199 excludes all occurrences of duplicate chunk IDs and marks affected article labels uncomparable. These are structural safeguards, not proof of legal effect. Evidence-backed relationship review, source authentication, and effective-date reasoning remain outstanding |
| UI-04 | Complete responsive browser/RTL/LTR/keyboard/reader QA | In progress | PR #223 improves login labels, small-screen navigation, long-value wrapping, and selected text sizes; PR #234 makes remaining/overdue days visible; PR #241 exposes calendar export in the agenda UI; PR #258 improves memo download cleanup; PR #265 fixes clipboard failure reporting; PR #275 provides a manual QA checklist; #279/#300 display source hosts; #281 fixes ARIA/data/role attribute application and announces asynchronous research states. Manual mobile/tablet, 200% zoom, forced-colors, screen-reader, keyboard, copy/download, error and empty-state checks remain outstanding |
| UX-01 | Lawyer usability study for core research and case tasks | Not started | Test with 3–5 Egyptian lawyers; record completion rate, time, errors and trust |
| SEC-01 | Multi-firm isolation verification and independent security review | In progress | Merged PR #102 covers research conversation boundaries, #104 adds extraction-review read/write denial tests, #107 adds tenant-boundary inventory and cross-firm audit regression tests, and #108 adds runtime route/schema inventory drift checks. PR #109 hardens encrypted restore to authenticate before replacing a destination and stage writes atomically. Global legal-review endpoints now require a deployment-configured platform reviewer allowlist in addition to admin role. Proposed target architecture is documented in docs/database_tenancy_architecture.md: shared app, trusted tenant catalog, database per firm, and separately controlled shared legal corpus. PR #112 is merged, but this is a design proposal only; current shared SQLite remains. docs/database_boundary_phase0_review.md records an initial static review of storage entry points, table classifications, mixed legal/matter search, identity/session questions, and migration exit criteria (PR #114). PR #115 extracts SQLite connection lifecycle behind a testable provider without changing the single configured database path; its CI passed and it is merged, but it does not select tenant databases or provide isolation. docs/repository_storage_entrypoint_inventory.md records the non-route CLI, corpus tooling, file outputs, backup/restore, deployment-preflight, and external job-inventory gaps (PR #116 merged; CI passed). PR #251 records approved global-identity and many-to-many membership semantics; PR #253 adds fresh control-plane identity, membership, and separate platform-role tables; PR #259 adds a tested SQLite membership lookup helper but does not wire it into authenticated request routing or session handling. PR #261 adds canonical Unicode email-normalization tests; #263 rejects unsupported firm roles in context resolution; #264 adds an explicit platform-role lookup helper separate from firm roles; #266 rejects provisioning without a firm schema profile; #267 corrects the storage audit's account of legacy firm defaults; and #268 tracks role-hardening progress. PR #269 tracks identity tests; #271/#282/#283 strengthen tenant preflight and control-plane authority checks; #272 validates platform-role inputs; #273/#276 reject inactive firms or disabled identities in membership resolution; #274 documents a session/bootstrap policy proposal; #278 tracks lifecycle/binding checks; and #280 validates trusted membership lookup; #286/#289/#294/#297/#299 track further preflight/profile validation; #291 hardens platform-role checks against stale/wrong-profile access; #292 audits migration history; #295 tests identity/platform-role schema separation; and #298 verifies the control-plane profile during catalog preflight. PR #301 remains open for catalog migration-history audit. These remain preflight/control-plane foundations and do not establish production tenant isolation. docs/data_ownership_migration_map.md maps declared tables/resources to candidate firm, control-plane, and shared-corpus ownership, with unresolved rows and migration gates (PR #119 merged; draft only, not an exhaustive audit). PR #121 adds an initial static query/resource audit (documentation only; merged). PR #123 adds a read-only SQLite ownership preflight script and unit tests; it reports anomalies but does not repair or migrate records. PR #126 stops startup from assigning NULL legacy user/case ownership to firm 1, preserves ambiguous rows in a quarantine ledger, and denies login and invalidates sessions where firm ownership remains NULL; this does not undo historical defaulted values. PR #195 adds a catalog-backed tenant connection router with per-firm connection reuse and fail-closed behavior; PR #198 adds a fail-closed active-firm context resolver backed by a caller-supplied trusted membership lookup; PR #200 closes the current thread's cached tenant connection when catalog validation fails; PR #201 tests thread-local connection separation and cleanup. None is a production routing cutover: the resolver is not wired into routes, the caller must supply a verified session identity and authoritative membership lookup, and current routes still use shared SQLite. Obtain product/deployment-owner approval, complete the real deployment inventory and exhaustive query/file review, reconcile legacy ownership, then build approved request integration, firm-specific backup/restore, and independent review. |
| REV-01 | Revenue-ready paid pilot: verified labour-law workflow, billing/entitlements, OCR quality, drafting and commercial release gates | In progress | PR #227 adds a scoped overview of recorded, paid, outstanding and overdue fees using existing records; it is not invoicing or payments. No payment integration or subscription lifecycle is implemented. Provider access, product-owner decisions, lawyer-reviewed corpus/evaluation, and SEC-01 remain prerequisites. |
| SEC-02 | Production account recovery, MFA/session/device controls and retention policies | In progress | PR #218 hardens login lockout and password policy; add MFA and complete threat model, shared/edge rate limiting, and release review before production |
| OPS-01 | Production observability, backup/restore rehearsal and deployment release gates | Not started | Add structured logs, alerts, backup restore test and documented rollback |

## Progress rules

1. A merged PR with passing CI can complete code work, but it does not complete manual QA unless manual evidence is recorded.
2. Permission status must be supported by written evidence. Public visibility, HTTPS, a successful download, or an official contact email does not establish bulk or commercial reuse permission.
3. Keep these states separate: source discovered, metadata recorded, text acquired, extraction reviewed, authenticity verified, legal status verified, amendment history verified, and reuse permission approved.
4. Exclude fictional test corpus data from real-law coverage metrics.
5. Report coverage as registered candidates and verified operative versions, not as an unqualified “percentage of Egyptian law covered.”

## Immediate next actions

1. Continue DATA-07: approve secure original-file retention and implement reviewer UI/page previews; merged PR #103 adds only reviewer-entered page references and concurrency protection.
2. Do not claim retrieval evaluation quality until RSH-02 has lawyer-labelled questions and real runs; PR #180 hardens malformed/duplicate record handling and PR #196 adds coverage metrics, but neither supplies reviewed labels or real run data.
3. Complete manual RTL/LTR/keyboard/screen-reader and lawyer review for the merged source inspector (RSH-01). PR #183's fail-closed date/provenance checks and #256's explicit verified-corpus scope gate are merged; #260 also rejects malformed passage values and missing memo scope no longer defaults to verified_corpus. PR #275 provides a repeatable checklist, but actual browser/build results must still be recorded; #281 adds live status announcements, #285/#296 improve matched-word highlighting, and #300 explains status labels and displays the original-source host. Manual review remains outstanding.
4. Continue item-level terms and reuse review for Egyptian sources under DATA-03; retain unknown permission states unless evidence supports a change.
5. Continue the 69-candidate metadata inventory under DATA-04, adding only verified metadata and source references.

6. SEC-01 safe legacy migration: remove implicit reassignment of NULL user/case firm IDs, add a durable quarantine ledger, fail closed for unassigned identities, and test repeatable startup migration. Then build a dry-run/reconciliation tool for a protected DB copy; do not classify quarantined rows without evidence. This is a partial safeguard, not database-per-firm isolation.

7. Revenue readiness: review docs/revenue_readiness_roadmap.md with the product owner. Confirm labour law as the first paid scope, the pilot customer, trial/plan rules, payment provider eligibility, and responsible legal reviewer. Treat the document as a proposal until decisions are approved; do not market unimplemented payments, drafting, deadline calculation, verification badges, or WhatsApp delivery.

8. Continue SEC-01: PR #251 records the approved identity/membership contract, and PR #253 adds fresh control-plane schemas; PR #259 supplies a membership lookup helper but does not complete runtime request/session integration. PR #261 adds Unicode normalization tests, #263 validates allowed firm roles, and #264 adds an explicit platform-role lookup helper; #269 tracks those tests; #271/#282/#283 strengthen preflight checks; #272/#273/#276/#280 harden role, lifecycle, disabled-identity and membership lookups. PR #274 is a policy proposal, not a completed session/bootstrap implementation. PR #286/#289/#294/#297/#299 track further preflight/profile validation; #291 hardens platform-role checks, #292 audits migration history, #295 tests schema separation, and #298 validates the control-plane profile during preflight. These are primitives, not a completed request/session integration. Review docs/data_ownership_migration_map.md (PR #119 merged) with data/deployment owners; confirm table ownership, mixed FTS partitioning, identity/audit treatment, and orphan-row quarantine. Obtain the actual deployment/job inventory and finish exhaustive query/file review. PR #121 documents the initial static query/resource audit; PR #123 adds a read-only ownership preflight, neither proving isolation. DB-03 catalog/provisioning (#131), DB-04 schema contract (#133), and DB-05 profile-aware migration harness (#135) are merged. The profile-migration harness and profile-separated runtime are foundations; validate schema parity, backup/restore, and request-path integration before any production cutover. PR #361's runtime foundation was superseded by PR #372, which wires the configured fresh-install request path through the control plane, firm databases, and shared corpus. Remaining release work includes exhaustive route/query/background-job review, lifecycle acceptance, witnessed backup/restore and rollback drills, retention/monitoring, and independent security review. The database tracker says no legacy database is deployed, so legacy import reconciliation is conditional rather than a first-deployment task.

## Known limitations

- The legal corpus is not comprehensive and may lack current amendments.
- Some source permission requests may be declined or unanswered; the roadmap must remain useful without them.
- A practice-area value of `unknown` means unclassified, not absent or covered.
- Automated tests cannot substitute for legal review, manual accessibility checks or security assessment.


## Current checkpoint update — 2026-10-28

This section supersedes the dated open-PR list above where the status has changed. It is a snapshot, not a fresh full-repository test or legal review.

### Workstream estimates (rough, non-additive)

| Workstream | Estimate | Current state |
|---|---:|---|
| Overall product readiness | 42% ± 8 percentage points | Estimate carried forward from the prior review; not recalculated from a full acceptance run. |
| Legal corpus verification | 6% | Still the largest product gap: no comprehensive lawyer-reviewed corpus; source artifacts, reuse scope, effective dates, and qualified review remain blockers. |
| Research evaluation and citation integrity | 72% | Several scoring safeguards merged; source-status consistency and runner/scorer changes remain open/conflicted. Real lawyer-labelled benchmark runs are still missing. |
| Legal corpus audit safeguards | 55% | Evidence-flag audit and Markdown metric display merged; review-event integrity and chunk/version consistency PRs remain open with conflicts. |
| Database/tenant isolation | 65% estimate | Separate workstream owned by the other AI. Do not treat this percentage as release approval; independent security review and deployment-level validation remain. |
| UI/UX and manual QA | 45% | Fresh browser, RTL/LTR, keyboard, screen-reader and lawyer workflow evidence remains outstanding. |

### Merged since the 2026-10-27 snapshot

- #666: hardened evaluation-runner API base URL validation.
- #670: evaluation reports refuse to overwrite existing evidence files.
- #672: stabilized the MFA replay regression test across TOTP time boundaries (test-only; not a security certification).
- #673: expanded official Egyptian legal-source discovery metadata; new sources remain discovery-only and reuse permission remains unknown.
- #675: added exact-article future-effective-law regression coverage (test-only).
- #676: gates case-scoped prompts and follow-up context on the separate firm-data processing approval flag.
- #677 and #678: evaluator now penalizes citations to sources not retrieved and reports false abstentions/strict decision metrics.
- #681: requires supporting review/evidence records for legal verification flags.
- #686: renders the new audit metrics in Markdown as well as JSON.

The above merges improve tooling and safety controls; they do not prove the corpus is authentic/current, establish commercial reuse permission, or certify product readiness.

### Current blockers and next actions

1. **#682 — review-event integrity audit:** recorded PR Tests workflow passed, but GitHub reports merge conflicts. Reconcile against current main and rerun tests; do not force-merge.
2. **#683 — chunk/version consistency audit:** recorded PR Tests workflow passed, but GitHub reports merge conflicts. Reconcile after #682 to avoid overlapping edits to the same audit files.
3. **#680 — citation source-status evidence:** recorded PR Tests workflow passed, but GitHub reports merge conflicts with newer evaluator changes. Port/reconcile changes and rerun tests.
4. **#668 — runner/scorer schema and citation parsing:** recorded PR Tests workflow passed, but merge is rejected due conflicts. Reconcile with the now-merged #677/#678 work before merging.
5. **Legal content:** continue metadata discovery and source-specific rights analysis only. Do not bulk-download or commercially reuse material where rights remain unknown. Labour Law 14/2025 remains blocked pending independently sourced artifacts, amendment/effective-date comparison, and Egyptian-lawyer sign-off.
6. **Current test evidence:** PR-specific workflows passed before their merges, but the complete test suite has not yet been independently confirmed on the latest combined main commit.
7. **Database work:** PR #690 is the other AI's identity/invitation/recovery lifecycle workstream. This tracker update does not alter or approve that code. Avoid overlapping changes to migrations, tenant storage, identity lifecycle, or production data.

### Completion accounting rule

Count a deliverable as complete only when its code is merged and acceptance criteria are met. CI success on an individual PR is not the same as a passing full suite on current main. A validator or metadata catalog is not a verified legal corpus, and no percentage here should be interpreted as a legal accuracy guarantee.

## Latest checkpoint update — 2026-10-28 (after PRs #693–#696)

This update supersedes the earlier 2026-10-28 checkpoint above where PR state has changed. Percentages remain rough, non-additive estimates; they are not a full acceptance test or legal accuracy score.

| Workstream | Estimate | Current status |
|---|---:|---|
| Overall product readiness | 42% ± 8 percentage points | Carried forward; no increase claimed without a fresh full acceptance run. |
| Verified Egyptian legal corpus | 6% | Critical blocker remains: source artifacts, rights scope, amendment/currentness verification, and qualified Egyptian-lawyer review. |
| Research evaluation and citation integrity | 78% | PRs #694 and #696 merged after successful PR CI. Still needs lawyer-labelled benchmark runs and fresh full-suite confirmation on latest main. |
| Legal corpus audit safeguards | 75% | PRs #693 and #695 merged after successful PR CI. Audits expose inconsistencies but do not authenticate source material or repair records. |
| Database/tenant isolation | 65% estimate | Owned by the other AI. PR #690 remains separate and unapproved by this non-DB workstream. |
| UI/UX and manual QA | 45% | Manual RTL/LTR, keyboard, screen-reader, responsive, and lawyer workflow QA remain outstanding. |

### Newly merged since the previous checkpoint

- **#693:** review-event integrity audit (reviewer, type/outcome, timestamp, evidence URL shape, and version references).
- **#694:** fail-closed source-status evidence checks in legal evaluation.
- **#695:** consistency audit between global chunk flags and linked legal versions.
- **#696:** runner/scorer integration; citation-like markers in code/comments are ignored, unstable source IDs are invalid, and missing/non-verified status is treated conservatively.
- **#668, #680, #682, #683, #667, and #685:** stale/conflicted PR branches were closed as superseded by the merged replacements or current tracker.

Each new code PR passed its recorded PR Tests workflow before merge. The full Tests workflow also passed on combined main commit dbada2e06f5f917c6ff5ee2de1d6d2ed35ad5e40 after PR #696 merged. This confirms the suite on that exact code snapshot; any later code changes require their own validation.

### Remaining blockers / next task order

1. **Confirm current main CI after #696.** Record exact commit and outcome; investigate any failures instead of relying on earlier PR-only passes.
2. **Legal corpus:** preserve discovery-only and unknown permission states until source-specific evidence supports promotion. Labour Law 14/2025 remains blocked pending independently sourced original artifacts, effective-date/amendment reconciliation, and lawyer sign-off.
3. **Research quality:** run the evaluator only against a lawyer-reviewed benchmark. The scoring tools validate evidence consistency; they do not create ground truth or prove legal correctness.
4. **UI/UX:** collect real browser/accessibility/manual QA evidence.
5. **Database work:** leave migrations, tenant storage, identity lifecycle, and production data actions with the assigned DB workstream. Do not overlap or take irreversible actions without approval.

The overall completion estimate is intentionally unchanged: engineering safeguards have improved, but verified legal content, external review, manual QA, and release acceptance remain major gaps.


## Latest checkpoint — 2026-10-28 (after PRs #699–#704)

This supersedes earlier checkpoint estimates where status has changed. Percentages are rough workstream estimates, not legal-accuracy scores.

| Workstream | Estimate | Status |
|---|---:|---|
| Overall product readiness | 42% ± 8 percentage points | Unchanged; no product-readiness increase claimed from code-only safeguards and UI localization. |
| Verified Egyptian legal corpus | 6% | Still the critical blocker: original source artifacts, reuse scope, effective-date/amendment reconciliation, and qualified Egyptian-lawyer review are missing. |
| Research evaluation and citation integrity | 78% | Evidence/status scoring and runner/scorer integration are merged. A lawyer-labelled benchmark is still needed to measure actual legal correctness. |
| Legal corpus audit safeguards | 75% | Review-event integrity and chunk/version consistency audits are merged. They flag inconsistencies but do not authenticate legal texts. |
| UI/UX implementation | 55% | Bilingual forms and document review, case-tab labels, and modal keyboard-focus handling improved. Manual browser/accessibility QA is still outstanding. |
| Database/tenant isolation | 65% estimate | Remains the other AI's workstream. Do not overlap migrations, tenant storage, identity lifecycle, or production data operations. |

### Newly merged UI and onboarding work

- **#699:** corrected README installation, first-owner bootstrap, and separate-database backup/restore instructions; the full Tests workflow passed before merge.
- **#700:** localized case creation and client/conflict-check workflows for Arabic/English.
- **#701:** localized case-detail inputs, validation feedback, and fee formatting.
- **#702:** localized document-review actions, OCR warnings, status labels, and reviewer prompts.
- **#703:** localized case tabs, team roles, summary labels, and activity timestamps.
- **#704:** added modal focus trapping and focus restoration on dismissal.

PR-specific Tests and non-database safety workflows passed for the UI changes before merge. The full Tests workflow also passed on combined main commit e923be526fa9fe3ba25f52a7a7231112850d2694 after PR #704. Manual browser testing has not been performed and must not be inferred from CI.

### Remaining blockers / next order

1. **Manual UI acceptance:** test Arabic RTL and English LTR at 360, 768, 1024, and 1440 px; verify keyboard-only navigation, modal focus return, screen-reader labels, zoom/reflow, long Arabic/Latin citations, and document-review flows. Capture screenshots/results before calling UI/UX release-ready.
2. **Legal corpus:** continue metadata-only discovery unless source-specific acquisition/reuse permission is established. Labour Law 14/2025 remains blocked pending independent source artifacts, effective-date/amendment reconciliation, and lawyer sign-off.
3. **Research quality:** use the evaluation tools with lawyer-reviewed expected sources and pin-cites; tooling success is not a substitute for ground truth.
4. **Database work:** keep the assigned database/identity PRs separate. No irreversible database changes were made by this workstream.

Overall readiness remains 42% ± 8% because the largest unresolved product gap is still the absence of a comprehensive verified Egyptian legal corpus and qualified legal review.


## Latest checkpoint — 2026-10-28 (after PR #706)

This update supersedes prior checkpoints where statuses have changed. Percentages remain estimates, not a legal accuracy score or a full product acceptance decision.

| Workstream | Estimate | Status |
|---|---:|---|
| Overall product readiness | 42% ± 8 percentage points | Unchanged; verified legal content and real-world acceptance remain major gaps. |
| Verified Egyptian legal corpus | 6% | Blocked on source artifacts, rights scope, amendment/effective-date reconciliation, and qualified Egyptian-lawyer review. |
| Research evaluation and citation integrity | 78% | Citation-status evidence, runner/scorer integration, and strict scoring safeguards are merged. A lawyer-labelled benchmark is still required. |
| Legal corpus audit safeguards | 75% | Review-event and chunk/version consistency audits are merged. These flag metadata conflicts but do not authenticate legal texts. |
| Source provenance / permission metadata checks | 80% | Manual capture integrity validation now also blocks permission-readiness flags when terms review is older than the internal 180-day freshness policy. This is not a legal rule and does not grant permission. |
| UI/UX implementation | 55% | Case/client/document workflows are more consistently bilingual; modal keyboard focus trapping/restoration is implemented. Manual browser/accessibility QA remains open. |
| Database/tenant isolation | 65% estimate | Other AI's workstream; avoid overlapping migrations, tenant storage, identity lifecycle, and production data operations. |

### Newly merged since the previous checkpoint

- **#699:** corrected README setup, first-owner bootstrap, and separate-database backup/restore instructions.
- **#700–#703:** localized case creation, client/conflict checks, case-detail fields, document review, case tabs/team roles, and activity timestamps.
- **#704:** modal keyboard focus trap and focus restoration.
- **#706:** stale source-terms review now blocks collection/commercial-readiness flags until terms are rechecked.

The full Tests workflow passed on combined main commit 9f7392e9f7a22e4743ad00ef57891ea5d38ce68b after PR #706. PR-level and main-level CI are tied to exact commits; future code changes require fresh validation.

### Remaining blockers / next order

1. **Manual UI acceptance:** test Arabic RTL and English LTR at 360, 768, 1024, and 1440 px; keyboard-only navigation; modal focus return; screen-reader labels; zoom/reflow; long Arabic/Latin citations; and document-review workflows. Record screenshots and results.
2. **Legal corpus:** keep source permissions unknown unless supported by source-specific evidence. Labour Law 14/2025 remains blocked pending independently sourced original artifacts, amendment/effective-date reconciliation, and lawyer sign-off.
3. **Research quality:** run evaluation against lawyer-reviewed expected sources and pin-cites; CI success does not create legal ground truth.
4. **Database work:** leave the assigned database/identity workstream separate. No irreversible database actions were taken here.

Overall readiness remains 42% ± 8%. Engineering safeguards have improved, but a comprehensive verified Egyptian legal corpus and qualified legal review are still missing.


## Latest checkpoint — 2026-10-28 (after PRs #709–#710)

This checkpoint supersedes earlier status estimates where they differ. Percentages are rough workstream estimates, not additive and not measures of legal accuracy.

| Workstream | Estimate | Status / next gate |
|---|---:|---|
| Overall product readiness | 42% ± 8 percentage points | Unchanged. New safety tooling does not resolve the verified-law corpus, independent review, or manual acceptance gates. |
| Verified Egyptian legal corpus | 6% | Critical blocker: original legal artifacts, rights scope, effective-date/amendment reconciliation, and qualified Egyptian-lawyer review are still missing. |
| Research evaluation and citation integrity | 78% | Evaluation now requires reviewer-registry approval before assessments count. Actual lawyer-reviewed benchmark records and runs are still absent. |
| Legal corpus audit safeguards | 75% | Audits flag contradictions; they do not authenticate law or prove completeness/currentness. |
| Source provenance and acquisition readiness | 85% | Fresh terms reviews and explicit HTTPS terms URLs are required for readiness. Source-specific permissions remain unknown unless backed by evidence. |
| UI/UX implementation | 55% | Bilingual workflow changes and modal keyboard focus safeguards are merged; manual RTL/LTR, responsive, screen-reader, and lawyer-workflow QA remains open. |
| Database/tenant isolation | 65% estimate | Separate workstream owned by the other AI. Do not overlap migrations, tenant storage, identity lifecycle, or production data actions. |

### Newly merged

- **#709 — explicit source-terms URLs:** the acquisition-readiness audit now requires valid HTTPS terms URLs in both the source register and document manifest, rejecting missing or credential-bearing URLs. The first CI run exposed four older CLI fixtures without terms URLs; the fixtures were updated and the corrected PR Tests and non-database safety workflows passed. The full Tests workflow passed on main commit 4144673b6f18a2cd0a5b89ca9eb1eb1213b9d5b9.
- **#710 — approved reviewer registry:** human-answer evaluation records must match a unique approved reviewer ID and name, with qualification basis, evidence reference, verifier, and a valid non-future verification date. The full Tests workflow passed on the final PR commit a7171896102e3d1a15d6bd2b625e8fb0b689a2f7; post-merge Tests are running on main commit aae7fad31d901c67bd1e7094fd65fb95fdb57a64.

### Current blockers and next actions

1. **Current-main validation:** await the post-merge full Tests workflow on aae7fad31d901c67bd1e7094fd65fb95fdb57a64; record any failure rather than relying on PR-only CI.
2. **Reviewer governance:** the registry is an auditable administrative assertion, not independent proof of a professional license. Keep real credential evidence in private controlled storage; a trusted operator must verify it before approving a reviewer.
3. **Legal corpus:** keep candidates blocked until source-specific rights evidence and original text/version checks exist. Labour Law 14/2025 still needs independent source comparison, effective-date/amendment reconciliation, and Egyptian-lawyer sign-off.
4. **Human evaluation:** do not claim legal-answer accuracy until approved reviewers score a sufficiently balanced benchmark with exact source versions and pin-cites.
5. **UI/UX:** manual browser, keyboard, screen-reader, RTL/LTR, and lawyer-workflow acceptance is not yet recorded.
6. **Database work:** keep assigned identity, tenant storage, migrations, and production data operations separate. No irreversible database changes were made in this non-DB workstream.

The overall readiness estimate remains 42% ± 8%. The recent work makes permission and reviewer claims more accountable, but it does not itself establish reuse rights, legal authenticity, currentness, or product readiness.


## Latest checkpoint — 2026-10-28 (after PR #712)

This update supersedes previous checkpoints where statuses have changed. Percentages remain rough, non-additive estimates—not legal-accuracy scores.

| Workstream | Estimate | Status |
|---|---:|---|
| Overall product readiness | 42% ± 8 percentage points | Unchanged; no verified corpus or manual acceptance completion claimed. |
| Verified Egyptian legal corpus | 6% | Blocked on original source artifacts, source-specific rights, effective-date/amendment reconciliation, and Egyptian-lawyer sign-off. |
| Research evaluation and citation integrity | 78% | Both human-review scoring and benchmark scoring now require a private approved reviewer registry. Actual lawyer-reviewed benchmark runs remain missing. |
| Legal corpus audit safeguards | 75% | Audits identify evidence/status/version inconsistencies; they do not authenticate legal texts. |
| Source provenance/acquisition safeguards | 85% | Stale terms reviews and missing/credential-bearing HTTPS terms URLs block acquisition readiness. Rights remain unknown until evidenced. |
| UI/UX implementation | 55% | Bilingual workflows and modal keyboard focus handling are implemented; manual RTL/LTR, screen-reader, responsive, and lawyer-workflow QA remains outstanding. |
| Database/tenant isolation | 65% estimate | Separate workstream owned by the other AI; no overlap with migrations, tenant storage, or identity lifecycle. |

### Newly merged — #712

The benchmark scorer and production release gate now require reviewer IDs/names to match a valid approved reviewer registry. The release gate blocks when the registry is missing or invalid. The PR's full Tests workflow passed on commit 2a122e83cce33bf1caa47f9c1cd828bbf34d9479. Post-merge full Tests are queued on main commit 990a664d149ae753248e4faf767ddb95333e0af6; do not call current main validated until that run completes.

### Immediate next actions

1. Confirm the post-merge full Tests result on 990a664d149ae753248e4faf767ddb95333e0af6.
2. Keep actual reviewer credential evidence private and require trusted manual verification before setting registry status to approved. The registry gate checks consistency; it does not independently verify a license.
3. Obtain and compare permitted primary legal texts, beginning with Labour Law 14/2025; preserve source bytes/hashes, dates, amendments, and review notes, and keep retrieval blocked until release checks pass.
4. Populate the benchmark only with qualified reviewer-approved questions, exact source versions, and pinpoint citations; no legal-accuracy claims before real reviewed runs.
5. Perform and record manual browser/accessibility QA.
6. Leave DB/tenant/storage and production data actions to the assigned database workstream.
Overall readiness stays at 42% ± 8%. Reviewer/source controls are more accountable, but source permissions, verified legal content, lawyer-labelled evidence, manual QA, and independent release review remain unresolved.


## Latest checkpoint — 2026-10-28 (after PRs #715–#716)

Percentages are rough, non-additive estimates; they are not measures of legal accuracy.

| Workstream | Estimate | Current state |
|---|---:|---|
| Overall product readiness | 42% ± 8 percentage points | Unchanged. Still not market-ready. |
| Verified Egyptian legal corpus | 6% | Critical blocker: primary artifacts, rights scope, effective dates/amendments, and Egyptian-lawyer sign-off remain incomplete. |
| Research evaluation and citation integrity | 82% | Reviewer scope is checked against declared practice areas in human assessment and benchmark scoring; real counsel-reviewed benchmark runs are still absent. |
| Amendment/repeal provenance safeguards | 80% | Confirmed edges require traceable HTTPS evidence, SHA-256 metadata, reviewer ID/role, and non-future chronology. Validator does not authenticate evidence or legal effect. |
| Source provenance/acquisition safeguards | 85% | Terms freshness and source-terms URLs are checked; source-specific reuse rights remain unknown without evidence. |
| UI/UX implementation | 55% | Bilingual workflows and keyboard focus handling implemented; manual RTL/LTR, screen-reader, responsive, and lawyer-workflow QA remains outstanding. |
| Database/tenant isolation | 65% estimate | Remains assigned to the other AI; no database or tenant-storage changes made in this workstream. |

### Newly merged

- **#715 — reviewer practice-area scope:** reviewer registry entries must identify Egyptian legal counsel, Egypt jurisdiction, and explicit practice-area scope. Out-of-scope human assessments and benchmark questions are rejected. Full Tests passed on the PR head and post-merge main commit 741fa46f540bc204a32e8f720ae9518e02da8271.
- **#716 — traceable amendment confirmation:** a reviewed-confirmed relationship requires an HTTPS evidence URL, a 64-character SHA-256 digest, reviewer ID, the explicit qualified Egyptian lawyer role, and valid publication/review chronology. Full Tests passed on the PR head; the post-merge full Tests workflow on 27e4b9ceb7a887c9e0e8a407bcec8359464dca78 was still running at the time of this checkpoint.

### Next gates

1. Confirm post-merge full Tests on 27e4b9ceb7a887c9e0e8a407bcec8359464dca78.
2. Keep confirmed legal relationships blocked unless a trusted human verifies the referenced official evidence and reviewer credentials. URL/hash format checks do not verify content.
3. Acquire permitted primary texts for priority laws, reconcile official Gazette text and amendments/effective dates, and obtain qualified Egyptian-lawyer review. Do not infer permission from public access or unanswered emails.
4. Produce actual reviewed benchmark runs with source-version pin-cites before making legal-accuracy claims.
5. Record manual accessibility and bilingual browser acceptance.
6. Leave tenant DB, migrations, storage adapters, and identity lifecycle to the assigned database workstream.

Overall readiness remains 42% ± 8%; recent changes strengthen accountability but do not substitute for verified law content, permission evidence, real human review, or product acceptance.


## Latest checkpoint — 2026-10-28 (after PRs #718–#720)

Percentages are rough, non-additive estimates, not measures of legal accuracy.

| Workstream | Estimate | Current state |
|---|---:|---|
| Overall product readiness | 42% ± 8 percentage points | Unchanged; not market-ready. |
| Verified Egyptian legal corpus | 6% | Still blocked on original official text, source-specific rights, Gazette/page evidence, effective dates/amendment reconciliation, and Egyptian-lawyer sign-off. |
| Metadata discovery inventory | 71 instrument candidates | Discovery coverage only; candidates are not verified laws or permission to copy. |
| Research evaluation and citation integrity | 82% | Reviewer registry and practice-area scope enforced; actual qualified-counsel benchmark runs still absent. |
| Amendment/repeal provenance safeguards | 80% | Confirmed relationships require traceable HTTPS evidence URL, SHA-256 metadata, reviewer ID/role, and valid publication/review chronology. Human verification remains required. |
| Source provenance/acquisition safeguards | 85% | Source-terms URLs and freshness checks exist; reuse rights remain unknown unless backed by evidence. |
| UI/UX implementation | 55% | Bilingual workflows and modal keyboard-focus handling implemented; manual accessibility and lawyer-workflow QA remains open. |
| Database/tenant isolation | 65% estimate | Assigned to the other AI. No database/tenant-storage changes made in this workstream. |

### Newly merged legal-discovery updates

- **#718 — 2026 general work-regulation rules:** added an official Ministry of Labour announcement as a discovery-only candidate linked to Labour Law 14/2025. Exact instrument number, Gazette text/pages, commencement, currentness, and reuse rights remain unknown.
- **#719 — follow-up to Decision 264/2025:** added a State Information Service report that the Ministry approved 2026 training-centre standards under Labour Law 14/2025 and Decision 264/2025. The standards text and whether there is a separate instrument remain unverified.
- **#720 — Ministerial Decision 49/2026:** added an official Ministry announcement describing the decision on hazardous/difficult work and remote areas for additional annual leave. The full decision and Gazette evidence remain outstanding.

The Phase 2 metadata-only inventory now contains 71 candidates across 13 source records. No legal text was downloaded, no permission or legal-status flag was promoted, and no candidate was marked verified by these PRs.

### Next gates

1. Confirm the post-merge full Tests run on main commit 32f42ddadd435dde22fb14783b588471fd393722.
2. Obtain official Gazette issue/page references and permitted original text for Labour Law 14/2025 and its implementing instruments; reconcile the exact effective date, transitional provisions, amendments, and repeal history.
3. Verify the exact text and legal form of the 2026 work-regulation rules and the standards linked to Decision 264/2025; keep them discovery-only until the primary instrument is located.
4. Review collection, storage, extraction, indexing, excerpt display, commercial use, and redistribution rights separately for each source and document.
5. Run a real benchmark with qualified Egyptian counsel, exact source versions and pinpoint citations before making legal-accuracy claims.
6. Record manual RTL/LTR, keyboard, screen-reader, responsive and lawyer-workflow acceptance.
7. Leave tenant database, migrations, storage adapters and identity lifecycle to the assigned database workstream.

Overall readiness remains 42% ± 8%. The recent work improves traceability and identifies current implementation leads; it does not establish verified legal content or production readiness.


## Latest checkpoint — 2026-10-30 (whole-product and database workstream reconciliation)

This checkpoint separates the product-wide readiness estimate from the database workstream estimate. The percentages are rough, reviewable workstream estimates, not additive scores or legal-accuracy claims.

| Workstream | Estimate | Status / next gate |
|---|---:|---|
| **Overall product readiness** | **42% ± 8 percentage points** | Unchanged from the latest project-wide checkpoint. Database progress does not close the verified-law corpus, human legal evaluation, manual QA, or release-acceptance blockers. |
| Verified Egyptian legal corpus | 6% | Still the critical product blocker: original primary texts, source-specific reuse rights, effective-date/amendment reconciliation, and qualified Egyptian-lawyer sign-off remain outstanding. |
| Research evaluation and citation integrity | 78% | Evaluation and citation safeguards are implemented, but actual qualified-counsel benchmark runs against exact source versions and pinpoint citations remain outstanding. |
| Legal corpus audit safeguards | 75% | Read-only audits and review-integrity checks are implemented; they do not authenticate law or prove completeness/currentness. |
| Source provenance and acquisition safeguards | 85% | Terms freshness, provenance and permission gates are implemented; source-specific rights remain unknown unless supported by evidence. |
| UI/UX implementation | 55% | Bilingual workflows and keyboard-focus safeguards are implemented; manual RTL/LTR, responsive, keyboard, screen-reader and lawyer-workflow acceptance remains outstanding. |
| **Database / tenant isolation** | **87%** | Separate database tracker estimate. PR #901 merged as `733b11b` after Full Tests run #41052146895 passed 123/123, including the explicit purge-and-backup regression and CI coverage guard. The local-backup tombstone fix is now in main. PR #898 adds fake-S3 state-machine tests for legal-hold refusal, wrong-firm database binding, tenant commit failure after object deletion, and a retry that remains blocked for manual review. Full Tests run #41053584222 passed 123/123 on head `64ff4c7b696ac00e8f0d79f95cce7333e666eae8`, after synchronization with current main and merged PRs #901 and #902. PR #898 remains open and has no independent destructive-operation review. Live S3/KMS/IAM verification, approved retention/deletion policy, witnessed recovery, and independent security review remain release blockers. |
| Production / paid-pilot readiness | 35% | Blocked by verified legal content, counsel-reviewed evaluation, security review, live infrastructure acceptance, witnessed recovery, and manual product QA. |

### Fresh-install and legacy-data scope

The deployment target remains a fresh install. No production customer database has been deployed or supplied for legacy import, so legacy customer-data reconciliation/migration is not a first-deployment task. This does not waive the need to validate fresh schema creation, versioned migrations, tenant isolation, backup/restore, or removal of unsafe runtime compatibility paths.

### Current priority order

1. Complete and independently review the S3 purge state machine; keep destructive production execution disabled until live S3/KMS/IAM evidence, retention-policy approval, and witnessed staging recovery/deletion evidence exist.
2. Complete the lawful, source-backed Egyptian legal corpus and obtain qualified counsel sign-off. Keep unverified candidates out of verified retrieval.
3. Run a real lawyer-labelled retrieval/citation benchmark against exact source versions and pin-cites.
4. Complete manual Arabic RTL / English LTR, responsive, keyboard, screen-reader and lawyer-workflow acceptance.
5. Finish route/query/background-job tenant-isolation acceptance, production identity delivery/recovery, and independent security review.

The **47% weighted technical completion score** supersedes the older non-additive 42% ± 8% estimate. It remains a planning estimate, not production readiness or legal approval. The verified legal corpus remains at 6%; Law 174/2025's commencement is intentionally unassigned pending reconciliation of Law 160/2026's published wording with official explanatory material and qualified Egyptian-counsel review. The database workstream has advanced, but it cannot compensate for the product's still-limited verified legal corpus or missing human and operational acceptance evidence.


## Latest checkpoint — 2026-10-30 (post-launcher, PWA, importer and security-baseline merges)

This checkpoint supersedes the prior whole-product estimate where noted. It is a technical planning estimate, not a legal-accuracy or production-readiness claim. Open PRs do not count as completed work.

| Workstream | Estimate | Evidence / remaining gate |
|---|---:|---|
| Core case management | 75% | Existing workflows remain implemented; full end-to-end lawyer acceptance and edge-case QA remain. |
| Legal research/retrieval | 65% | Arabic/English retrieval, citation validation, provenance and abstention foundations exist; qualified-counsel benchmark runs against exact source versions remain absent. |
| Verified Egyptian legal corpus and rights | 6% | Labour Law 14/2025 remains quarantined; exact Gazette comparison, item-level rights, amendment/currentness reconciliation and Egyptian counsel review remain outstanding. |
| Security and firm isolation | 71% | PR #907 CodeQL/Bandit analysis and PR #925 MFA lifecycle rollback regression merged; route/job isolation, separate DB/storage completion, independent security review and witnessed recovery remain. |
| UI/device usability | 45% | PR #903 privacy-safe PWA shell and PR #909 Windows/Mac launchers merged; physical device/browser/accessibility acceptance remains. |
| Automated testing/reliability | 65% | PR #910 hash-locked dependency baseline, PR #907 static analysis, and PR #923 legal PDF integrity/OCR hardening merged; fresh full release-candidate validation remains. |
| Production operations | 38% | PR #905 read-only reminder outbox monitor and PR #903 deployment HTTP smoke probe merged; real staging, alert routing/on-call, SMTP rehearsal and witnessed restore remain. |

**Weighted technical completion: 47.95/100, rounded to 48%.** Final Egyptian-counsel acceptance remains 0% / not started and is a separate mandatory post-build gate.

### Newly merged since the previous scorecard
- **#928:** fail-closed PDF importer size/page limits, bounded reads, and regression coverage; Full Tests, CodeQL and dependency audit passed.
- **#926:** metadata-only discovery records for MPA enacted-laws index, IDSC Gazette repository and Manshurat legal archive. Reuse rights remain unknown; no legal text was downloaded or promoted.
- **#903:** privacy-safe installable PWA shell and read-only deployment HTTP smoke probe. Offline matter data remains deliberately unsupported.
- **#907:** CodeQL security-extended analysis and Bandit scan; static analysis does not replace independent security assessment.
- **#909:** current-main Windows/Mac first-run launchers and shared bootstrap; physical device smoke tests remain.
- **#910:** hash-locked Python dependency security baseline.
- **#923:** legal PDF/sidecar integrity, hash-bound OCR cache and Arabic-first OCR/importer improvements.
- **#925:** MFA lifecycle transaction rollback regression; database work remains owned by its separate workstream.
- **#905:** read-only reminder outbox health monitor and operator runbook.

### Current non-database work in progress
- **#926 merged:** metadata-only discovery of MPA enacted-law index, IDSC Gazette repository and Manshurat legal archive; all reuse rights remain unknown. Full Tests, CodeQL and dependency audit passed.
- **#928 merged:** current-main PDF importer resource bounds (100 MiB PDF, 1,000 pages, 1 MiB sidecars, bounded reads); Full Tests, CodeQL and dependency audit passed.
- **#840:** Labour Law/Decision 248–252 evidence ledger; original Gazette copy remains restricted and unverified.
- **#918, #919, #922:** dependency/action updates pending compatibility and CI review.

### Immediate gates
1. Finish PR #926 and #928 only after their full CI and security checks pass.
2. Continue multi-practice-area legal-source discovery without scraping restricted repositories or treating open access as a commercial licence.
3. Keep unverified texts out of authoritative retrieval; the supplied 311 Labour Law rows remain unverified.
4. Complete manual Arabic RTL/LTR, mobile, desktop, keyboard and screen-reader acceptance.
5. Complete staging deployment, SMTP/scheduler monitoring, operator reconciliation and witnessed backup/restore.
6. Leave tenant database, migrations, identity and destructive storage actions to the assigned database workstream.
7. Obtain qualified Egyptian counsel's actual application acceptance after technical completion.

## Latest checkpoint — 2026-10-30 (legal archive discovery, evidence inventory reconciliation, and CI hardening)

This checkpoint supersedes the earlier 47%/42% estimates recorded above. The whole-project technical score remains **48%** (47.95/100 weighted estimate). Final Egyptian-counsel acceptance remains **0% / not started** and is still a mandatory post-build gate.

### Completed and merged since the prior checkpoint

- **#931 — public legal archive discovery:** added الذاكرة والمعرفة للدراسات to the source permission register. Its public pages state CC BY 4.0 and provide full text in three court sections, laws and decisions. The register keeps collection and commercial reuse as unknown. WIPO Lex's consolidated Egyptian IP Law 82/2002 Article 141 is recorded as a rights-context lead: official documents are excluded from copyright, but creative collections/selection/arrangement may be protected. This does not authorize bulk extraction or override portal access terms. No legal text was imported.
- **#750 — Labour Law review questions:** merged five provisional review questions for Articles 237–241. These are not verified legal answers.
- **#797 — source verification matrix:** merged the Labour Law implementing-decision verification matrix and Decision 162 access-fallback documentation.
- **#926 and #928 — source discovery and PDF limits:** remain merged. Discovery records do not promote legal text; PDF limits remain 100 MiB, 1,000 pages and 1 MiB sidecars with bounded reads.
- **CI/dependency baseline:** merged #911, #912, #913, #915, #916, #918 and #919 after relevant checks passed. These improve build/security/dependency maintenance but do not materially change the legal corpus or market-readiness score.

### Current non-database legal-knowledge work

- **#782 — long-lived Labour Law branch:** the branch contains a larger 294-card expansion but is 198 commits ahead and 234 behind current main; it is not safe to merge as a whole. The unique Articles 256–298 and Articles 1–39/promulgation 2–11 material was selectively ported through #937 and #939. Current main now has 127 canonical cards, not 294. The remaining branch material still requires selective reconciliation. All 127 cards are search_eligible=false; 43 OSH/inspection cards and 15 coverage-gap page pinpoints are inferred/not visually verified, and 10 promulgation cards have no established Gazette page pinpoint.
- **#840 — Decisions 248–252 / Table 24:** secondary transcription cross-checks are recorded for rows 34, 61 and 64. The raw CAS/value discrepancies remain unresolved, the original Gazette issue 225(A) is still request-copy restricted, and official Gazette matches remain 0/781. No values are approved for occupational exposure or compliance use.
- **#784 — Decision 162:** currentness and publication-date reconciliation remains draft/open.
- **#931 — case-law source lead:** catalogue snapshot reports 1,135 Court of Cassation judgments, 983 Supreme Constitutional Court judgments, 2,456 Supreme Administrative Court judgments, 10,259 decisions and 1,090 laws. Five representative full-text pages were sampled. These counts and pages are discovery evidence, not proof of completeness, official provenance or licence scope. PR #935 separately registered the official Court of Cassation Legal Heritage Library as a browse-only primary verification route; its scans are watermarked against republication and reuse permissions remain unknown.

### Remaining release gates

1. Complete and merge #782 only after Tests, CodeQL and dependency audit pass on the final head.
2. Obtain authorized original Gazette copies or official text for Labour Law instruments and Decisions 248–252; no request-copy bypass.
3. Resolve item-level rights, source authenticity, currentness, amendment history and counsel review before any candidate becomes authoritative retrieval material.
4. Complete manual RTL/LTR, mobile, desktop, keyboard, screen-reader and lawyer-workflow acceptance.
5. Complete staging configuration, monitoring, scheduler reconciliation and witnessed backup/restore.
6. Leave tenant database, identity, migrations and destructive storage actions to the assigned database workstream.
7. Obtain qualified Egyptian counsel's actual application acceptance after technical completion.

**Completion remains 48%, not 49%:** recent work improves discovery, data integrity and CI, but the verified Egyptian legal corpus remains at 6% and counsel acceptance remains 0%. More candidate records or secondary-source cross-checks do not count as verified law.



## Latest checkpoint — 2026-10-30 (127 Labour Law cards and official-source discovery)

**Whole-project technical completion remains 48%** (47.95/100 weighted estimate). This does not increase from provisional cards or source-discovery records. The verified Egyptian legal corpus remains **6%** and final Egyptian-counsel acceptance remains **0% / not started**.

### Completed and merged

- **#935 — official Court of Cassation heritage library:** registered the Court's historical legal-document library and direct record routes. The announcement reports 27 scanned volumes, 13,275 pages, 3,533 indexed documents and 12,577 index entries for the core 1899–1933 series. Sample 1899, 1933, 1936 and 1937 record pages were located. The scans carry a watermark intended to prevent republication; collection and commercial reuse remain unknown. The current judgments/principles search portal is recorded separately with its published restrictions. No scans were ingested.
- **#937 — Labour Law occupational-safety/inspection expansion:** added 43 non-duplicate cards for selected Articles 256–298; canonical inventory grew from 59 to 102. Full Tests, CodeQL and dependency audit passed before merge.
- **#939 — Labour Law coverage and promulgation expansion:** added 15 coverage-gap cards for accompanying-law Articles 1–39 and 10 promulgation cards for Articles 2–11; canonical inventory is now 127. The report renderer explicitly says “not established” when Gazette page pinpoints are unavailable. Full Tests, CodeQL and dependency audit passed before merge.
- **#940 — Dataflare Egyptian Legal Corpus source audit:** registered a public 2,434-row/25M-token dataset whose card claims MIT licensing. Its schema lacks record-level source URLs, dates, Gazette pinpoints and currentness; the underlying source/rights chain is not established. Full Tests, CodeQL, dependency audit and non-database safety regression passed before merge. No Parquet or legal text was downloaded or imported.
- **#914 and #917 — dependency updates:** Boto3 and Pillow updates merged after Tests, CodeQL and dependency audit passed.

### Current legal-knowledge boundaries

- The 127 Labour Law cards are **provisional research leads only**. Every card has search_eligible=false; the instrument authenticity, currentness, amendment history, reuse rights and Egyptian-lawyer review gates remain pending.
- The 43 occupational-safety/inspection cards and 15 coverage-gap cards contain inferred page pinpoints that were not visually compared with the original Gazette. The 10 promulgation cards for Articles 2–11 have no established Gazette page pinpoints. Do not use them to calculate transitional deadlines, determine pending-case treatment, set exposure thresholds, or decide penalties.
- The original Gazette issue 225(A) for Decisions 248–252 remains request-copy restricted. Table 24 discrepancies in rows 34, 61 and 64 remain unresolved; official Gazette matches remain 0/781. Do not bypass access restrictions or use tentative values for compliance advice.
- The Dataflare MIT claim is not treated as blanket permission for underlying texts or embedded compilations. The dataset remains a provenance/quality candidate only.
- The MKSEgypt archive's CC BY 4.0 statement remains subject to rights-scope and provenance review; no bulk collection or ingestion is authorized by the register.

### Open work and blockers

- **#782:** remains open but diverged 198 commits ahead / 234 behind current main; do not merge as a whole. Continue selective reconciliation only.
- **#840:** draft/open; Decisions 248–252 and Table 24 evidence ledger remains secondary-only until original Gazette comparison and legal review.
- **#784:** draft/open; Decision 162 publication/currentness reconciliation remains unresolved.
- **#922:** open; Tests failed in test_scans_multiple_firms_and_aggregates_without_cross_firm_data because the health report was unexpectedly healthy. Do not weaken the cross-firm isolation assertion; diagnose and rerun before merging the Docker build-action update.
- **#898:** S3 physical-purge state machine remains with the separate database/storage workstream. No destructive purge without independent review, live S3/KMS/IAM evidence, approved retention policy and witnessed recovery.
- **Database/tenant architecture:** remains assigned to the other AI. No duplicate schema, migration, identity or destructive storage work was performed here.

### Next highest-value priorities

1. Continue primary-source comparison and provenance work for Labour Law 14/2025 and its implementing decisions; keep all unverified cards out of authoritative retrieval.
2. Continue selectively reconciling the remaining #782 branch material onto current main; do not merge the stale branch wholesale.
3. Diagnose #922's cross-firm reminder-healthcheck failure without weakening isolation guarantees.
4. Resolve the official Gazette access gap lawfully; no user input is currently required and no request-copy bypass will be attempted.
5. Complete real lawyer-labelled retrieval/citation evaluation, manual Arabic RTL/LTR/accessibility/browser QA, staging operations, and witnessed backup/restore.
6. Obtain qualified Egyptian counsel's actual application acceptance after technical completion.

**No completion-percentage increase is claimed:** more provisional cards and source leads improve research preparation, but they do not establish a verified Egyptian legal corpus or counsel-approved answers.


## Latest checkpoint — 2026-10-31 (implementing-decision crosswalk and source-rights review)

**Whole-project technical completion remains 48%** (the existing weighted estimate); the verified Egyptian legal corpus remains **6%** and final Egyptian-counsel acceptance remains **0% / not started**. This source-discovery work does not justify a percentage increase.

### Completed and merged

- **#1044 and #1047 — Law 14/2025 accompanying-law checklist and page locators:** the Articles 1–120 Gazette comparison checklist is merged, and article-heading locators were populated from the ETA-hosted Gazette PDF for the full 298-article law. Selected page images were inspected to confirm locators. This is not a full article-text comparison; verification, currentness, rights and counsel gates remain open.
- **#1048 — invoice implementation contract:** merged a database-owner review proposal covering invoice lifecycle, EGP exact-money handling, line items, append-only payments, derived payment states, firm/case authorization, immutable issued snapshots, print/export and regression tests. No invoice tables, migrations, API or UI were implemented. Implementation remains gated on explicit database-owner approval of the logical model, migration target and tenant strategy; accountant/tax-counsel confirmation is separately required before calling any output a tax invoice.
- **#1049 — Gazette issue 295 source rights:** recorded the Amiri Press/DSpace issue metadata, request-a-copy restrictions for the issue PDF and item-specific license file, and repository terms. No restricted bytes were obtained and no rights were inferred from a license filename.
- **#1051 — Decisions 288/2025, 289/2025, 290/2025, 291/2025, 292/2025 and 294/2025:** added decision-level secondary-text crosswalks, official issue metadata, parent-Law 14/2025 article anchors, currentness leads and regression tests. Decision 289 Articles 1–2 were reviewed in a Ministry of Labour PDF hosted by SIS; this is a government-hosted text copy, not the Official Gazette scan, and reuse terms remain unreviewed. Decision 291 was visually cross-checked against a third-party page-image reproduction of Gazette pages 21–22; the original DSpace PDF remains request-copy restricted and the reproduction's provenance/reuse rights remain unresolved. A separate MELES DSpace item for Decision 288 lists two restricted PDFs and a restricted item-specific license file; repository terms require written permission for commercial reuse and systematic database compilation. All six decisions remain discovery-only, legal status unknown and search_eligible=false. PR #1051 passed Tests, CodeQL, dependency security audit and non-database safety regression before merge.

### Open work and blockers

- Complete page-by-page exact text comparison for all 298 Law 14/2025 articles and the 13 promulgation provisions against lawfully acquired Gazette bytes; existing article locators and selected visual checks are not full verification.
- Obtain lawful primary-text access and compare Decisions 288, 290, 292 and 294 with their Gazette pages; obtain the original Gazette issue 295 for Decision 291 comparison. Do not submit request-copy forms or bypass restrictions under the current acquisition constraint.
- Verify later amendments, commencement and currentness for all six decisions; in particular, locate an authoritative instrument for the Decision 291 Article 4 annual overtime maximum. The candidate 2026-03-31 deadline is a date calculation, not proof of compliance or non-compliance.
- Resolve collection and commercial reuse permissions and obtain qualified Egyptian-lawyer review before any statutory card becomes authoritative or search-eligible.
- Invoice implementation remains blocked pending database-owner approval. Do not overload the existing fees table or alter tenant isolation to simulate invoices.

**No verified-corpus percentage increase is claimed:** the new crosswalks improve source discovery and rights traceability, not legal verification or counsel acceptance.

### Latest checkpoint — 2026-10-31 (counsel marker and source-release gate)

- #1066 and #1067 are merged. The runtime review API, normal/exact retrieval, provenance, read-only corpus audit, reviewer queue, and offline candidate release validator now share the counsel-allowlist marker contract. The offline validator additionally requires the marker account ID to match the candidate review's reviewer_id.
- The verified-corpus volume remains unchanged at 6%; no new Gazette original was obtained, no source-specific rights were cleared, and no legal content was promoted. Final Egyptian-counsel acceptance remains 0% / not started.
- #1057's synthetic browser corpus fixture was corrected for the new marker requirement. The corrected head's browser CI result is pending; the browser acceptance gate is not complete.
- The weighted engineering score is **49.20/100** (up 0.70 from 48.50; rounded to 49%). This increase reflects merged release-governance and regression coverage, not new verified legal material.

### Latest checkpoint — 2026-11-01 (browser acceptance and release-validator alignment)

- **#1093 merged:** strict HTTPS URL validation now rejects malformed/out-of-range ports, empty port suffixes, URL credentials, whitespace and control characters in the offline legal release validator. Tests (1,392 across 128 scripts), CodeQL, dependency audit and non-database safety regression passed.
- **#1078 merged:** the synthetic Chromium acceptance harness passed 6/6 browser tests. The full Tests workflow passed 1,391 tests across 128 scripts; CodeQL, Bandit, dependency audit and non-database safety regression passed.
- **#1057 and #1068 closed:** superseded by #1078. The old failed browser branch's ambiguous Arabic locators and invalid text/plain upload fixture were corrected in the merged harness; application PDF/DOCX-only validation was preserved.
- **Current technical completion: 49.78/100**, up 0.18 from 49.60. This reflects the latest-event audit/permission/release-gate consistency and merged automated browser acceptance.
- **Verified Egyptian legal corpus remains 6%; final Egyptian-counsel acceptance remains 0%.** No legal instrument was newly verified, no restricted source was acquired, and no reuse permission was inferred.
- Manual physical-device, screen-reader, accessibility and lawyer-workflow acceptance remain outstanding. PR #840 remains discovery-only pending lawful source access and rights review.

### Latest checkpoint — 2026-11-01 (evaluation evidence integrity)

- **#1095 merged:** legal-answer evaluation and qualified-human review summaries now use exclusive file creation. Existing report paths are refused with exit code 2; regression coverage verifies the existing evidence remains unchanged. The human-review evaluator's command-line entry point now propagates that exit status.
- **#1098 merged:** evaluation reports bind themselves to the exact input bytes used by recording SHA-256 and byte size for question seeds, model results, review records and reviewer registries. Reports include a UTC generation timestamp, omit local paths and raw inputs, and explicitly state that hashes are not proof of authorship/qualification/correctness and that the timestamp is not a trusted timestamp.
- **#1034 closed as completed:** merged #1078 satisfies the automated browser-test scope. Manual lawyer, screen-reader, physical-device and visual accessibility acceptance remain separate and outstanding.
- **Initial assessment:** the first evidence-integrity checkpoint did not recalculate the score; the subsequent 69.5% reliability recalculation is recorded below. No legal correctness, corpus-volume or counsel-acceptance credit is claimed.

### Latest checkpoint — 2026-11-01 (evaluation evidence integrity score recalculation)

- **#1095 and #1098 merged:** evaluator outputs now refuse to overwrite existing evidence and include hashes/byte counts for exact input artifacts, with no raw paths or contents disclosed.
- Automated testing/reliability is **69.5%**; weighted technical completion is **49.83/100**. The 0.05-point increase reflects evidence-preservation and reproducibility controls with exact-head regression coverage.
- **Verified Egyptian legal corpus remains 6%; final Egyptian-counsel acceptance remains 0%.** No legal source was promoted or reuse permission inferred.

### Latest checkpoint — 2026-11-01 (reminder SMTP ambiguity safety)

- **PR #1102 merged:** post-submission SMTP timeout/disconnect is recorded as `smtp_submission_ambiguous` and not automatically retried. Explicit SMTP 4xx rejection remains retryable. A close/QUIT error after confirmed acceptance does not trigger another send.
- Exact-head validation passed Tests (150/150 steps), non-database safety regression, Chromium acceptance, dependency security audit, Bandit and CodeQL.
- **Issue #474 remains open:** live provider staging/credentials, external scheduler monitoring, provider reconciliation and independent operational review remain outstanding. No production reminder delivery is claimed.
- Production operations/deployment readiness is now 35.2%; weighted technical completion is 49.85/100. Verified Egyptian legal corpus remains 6%; final Egyptian-counsel acceptance remains 0%.

### Latest checkpoint — 2026-11-01 (pending review and manual acceptance preparation)

- **PR #1105:** exact-head Tests (151/151), Browser acceptance, non-database safety regression, dependency audit, Bandit and CodeQL passed. It remains open pending explicit product-owner approval.
- **PR #1106:** exact-head Tests (150/150), Browser acceptance, dependency audit and CodeQL passed. All ten fictional colloquial retrieval scenarios passed. It remains open pending explicit product-owner approval.
- **PR #1104 merged:** manual acceptance runbook now provides the device/browser/screen-reader matrix, evidence record, firm-isolation checks and separate Egyptian-counsel sign-off procedure. Actual manual acceptance remains unperformed.
- **PR #1099 closed:** superseded by current-main #1106.
- **#840 remains discovery-only** pending lawful original Gazette access and rights review. #474 remains open for live SMTP/provider staging and operational review. #93/#95 remain open for human manual acceptance. #473/#886 remain open for independent security review and live storage/operations acceptance.


### Latest checkpoint — 2026-11-01 (candidate catalogue denominator integrity)

- **PR #1108 merged:** candidate catalogue denominator now excludes rows without a stable non-empty instrument ID and duplicate IDs after whitespace normalization. The plural practice_areas field must be a list; malformed values are diagnosed and valid identified instruments without a usable classification remain visible under unknown.
- Exact-head validation passed Tests (150/150 workflow steps), Browser acceptance (10/10), non-database safety regression (24/24), dependency audit, Bandit, Python CodeQL and JavaScript CodeQL.
- The weighted scorecard is now **49.88/100**. This is an engineering metadata-integrity improvement only; verified Egyptian legal corpus remains 6%, and final Egyptian-counsel acceptance remains 0%.


### Latest checkpoint — 2026-11-01 (Research Source Inspector keyboard acceptance)

- **PR #1111 merged:** added a keyboard-only Chromium workflow for scope selection, matter selection, conversation-list traversal, query composer focus, Enter submission and metadata-only empty-state behavior.
- Exact-head validation passed Browser acceptance (10/10), Tests (150/150), dependency audit, Bandit and both CodeQL analyses.
- UI/accessibility automated acceptance is now 45.2%; weighted technical completion is **49.90/100**. Manual screen-reader, device, RTL/LTR and lawyer acceptance remain unperformed. Verified Egyptian legal corpus remains 6%; Egyptian-counsel acceptance remains 0%.
