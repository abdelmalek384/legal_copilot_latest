# Legal Copilot — Project Progress Tracker

**Last updated:** 2026-10-28 (historical 2026-10-27 snapshot retained; current checkpoint appended; legacy 20-deliverable tally retained for historical continuity but is not a current overall project percentage)  
**Tracking method:** deliverable-level checklist, not an estimate of engineering hours. A task is “complete” only when its change is merged and its acceptance criteria are met. Open PRs are in progress, not complete.

## Overall status

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


## Latest checkpoint — 2026-10-30 (PR #840 legal-knowledge evidence work)

This checkpoint records discovery and engineering safeguards, not verified-law coverage. Percentages remain conservative and are not additive.

| Workstream | Estimate / count | Current state |
|---|---:|---|
| Overall product readiness | 42% ± 8 pp (last recorded estimate; not recalculated by this evidence-only work) | Not market-ready. DB/tenant, deployment, security acceptance and manual UX review remain separate gates. |
| Verified Egyptian legal corpus | 6% (unchanged) | No new legal rule was promoted to verified or retrieval-eligible. Original Gazette bytes, item-specific reuse evidence and qualified counsel review remain missing. |
| Legal-knowledge preparation | 15% (planning/evidence preparation estimate only) | More source relationships, candidate inventories, discrepancy controls and reproducible checks are prepared; this is not verified-law coverage. |
| Phase 2 metadata inventory | 79 instrument candidates / 14 source records | Seven new 2026 Prime Minister decision candidates (982, 1305, 1572, 2033, 2377, 2590, 3165) linked to Labour Law 14/2025. All remain discovery-only. |
| Decision 250 Table 24 | 781 secondary candidate rows | Structural inventory is complete (781/781); original Gazette row matches remain 0/781. Rows 34, 61 and 64 remain explicitly unresolved/high-priority. |
| Decisions 248–252 | 0/5 fully compared with original Gazette | Supplement 225(A) original PDF remains request-copy restricted in the checked DSpace record; Action 1 user-supplied intake is pending. |
| Lawyer in-app review | Not started | Separate post-technical-completion release gate. The review plan now includes OSH-23–27 for later implementing-decision/currentness behavior, including the April Sunday scope and whether monthly extensions carried it forward. |

### New evidence work completed

- Identified official Amiri Press searchable-text leads and Gazette metadata for Prime Minister Decisions 982, 1305, 1572, 2033, 2377, 2590 and 3165/2026. These are distinct implementing/extension candidates, not amendments to Law 14/2025 merely because they cite it.
- Added seven separate instrument records and parent-law relationships to `docs/phase_2_document_inventory.json`; the metadata-only inventory now contains 79 records. Added `EG-DSPACE-OFFICIAL-GAZETTE-CATALOGUE` as a separate third-party catalogue source so repository metadata is not conflated with the Amiri Press issuing authority; permission remains unknown.
- Checked the DSpace download routes for Gazette issues containing Decisions 982, 1305, 1572 and 2033: 982, 1572 and 2033 route to request-copy; 1305 requires DSpace login. The official Gazette collection listing also identifies Decision 2590 in issue 35 (مكرر), but its exact item record is not pinned. Secondary press reports place Decision 3165 in issue 41 (مكرر و), reportedly dated 12 October 2026; its exact official Gazette item is not yet pinned, so this remains a discovery lead. No login was attempted, no access control was bypassed, and no copy request was submitted.
- Recorded that Decision 2590/2026 continues Decision 982/2026 through September 2026. A targeted search did not locate an October extension; this is not proof that no October instrument exists and does not establish expiry/currentness.
- Added an explicit currentness discovery log and five future in-app lawyer prompts (OSH-23–27) to test October status, original Gazette citation, Decision 3165 and the distinction between parent-law amendment and implementing-decision extension.
- Added regression assertions for the seven instrument records, parent relationships, DSpace metadata and access restrictions. A local structural/schema-equivalent check found 79 records, 14 source records, no duplicate IDs, no unsupported states and no invalid URLs.
- Prepared `tools/inspect_action1_labour_intake.py` with tests and CI wiring. It creates a metadata-only receipt for the supplied Gazette PDF and optional `law_rows_ar.jsonl` (hashes, sizes, PDF signature/EOF, JSONL shape, duplicate-key diagnostics and comparison with the historical 311-record SHA/size/count); it never edits, uploads, extracts or embeds source contents and never promotes legal status or retrieval eligibility.
- On code/test head `653d933e892b874d3387c817eec9bbba72a339de`, Legal Knowledge Validation run 41035768710 passed (28/28) and Full Tests run 41035768592 passed (104/104). The full suite explicitly passed the new metadata-only Action 1 intake-inspector regression step. The current PR head has only subsequent progress-documentation changes. The preceding validated branch checkpoint remains 103/103 Full Tests and 28/28 Legal Knowledge Validation.

### Next gates

1. Receive the user's original Official Gazette Supplement 225(A) PDF and optional `law_rows_ar.jsonl`; preserve/hash originals and compare all available candidate records without committing restricted raw files.
2. Continue acquiring official Gazette pages for other Labour Law implementing instruments only through permitted routes; record login/request-copy restrictions rather than bypassing them.
3. Reconcile Decision 250 Table 24 rows 34, 61 and 64 first, then the remaining 781 rows.
4. Verify currentness, amendments, extensions and commencement separately for each instrument; no conclusion from search absence.
5. Complete technical work before scheduling the lawyer's in-app review; obtain sign-off only for the exact app commit, corpus version and legal scope actually tested.
6. Keep all candidate-only and rights-unclear material out of authoritative retrieval. Leave DB/tenant/storage work to the assigned workstream.

**Percentage rule:** the 79-record inventory and seven new source leads improve discovery completeness, not the verified Egyptian legal corpus percentage. Keep the verified-corpus estimate at 6% until the actual release gates pass.
