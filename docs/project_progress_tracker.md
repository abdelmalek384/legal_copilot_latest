# Legal Copilot — Project Progress Tracker

**Last updated:** 2026-10-24 (PR #119 merged; data-ownership map remains a draft pending owner review)  
**Tracking method:** deliverable-level checklist, not an estimate of engineering hours. A task is “complete” only when its change is merged and its acceptance criteria are met. Open PRs are in progress, not complete.

## Overall status

- **Completed and merged:** 7 of 19 tracked deliverables (**36.8%**).
- **In progress:** 6 of 19 deliverables (**31.6%**).
- **Not started, blocked, or awaiting validation:** 6 of 19 (**31.6%**).
- **Merged PRs from this workstream:** #88, #89, #90, #91, #92, #94, #96, #97, #98, #99, #100, #101, #102, #103, #104, #105, #106, #107, #108, #109, #110, #112, #114, #115, #116, #117.
- **Open PRs:** None found in the repository search at the time of this update. PR #119's data-ownership/migration map is merged as a draft; PR #117's identity/membership contract is merged as an unapproved proposal. PR #116's storage/file/backup/job inventory and PR #115's behavior-preserving SQLite connection-provider interface are merged.
- **External permission requests:** not sent by this project workflow. Claude is expected to handle outreach; approval is not assumed.
- **Manual UI QA:** not yet completed.

Percentages count the 19 deliverables actually listed in this register equally; they are not a claim about engineering hours or total product capability.

## Task register

| ID | Deliverable | Status | Evidence / next action |
|---|---|---|---|
| UI-01 | Responsive workspace baseline and dashboard shortcuts | Complete | Merged PR #88 |
| UI-02 | Keyboard navigation, skip link, language-switch and modal accessibility | Complete | Merged PR #89; manual assistive-technology QA remains a separate task |
| UI-03 | Saved research search/rename and safer source-link handling | Complete | Merged PR #91; this is not the complete source-inspector workflow |
| SRC-01 | Permission outreach tracker, official contact verification and permission-gate tests | Complete | Merged PR #90; verified contact does not mean permission granted |
| DATA-01 | Document permission-aware corpus strategy and alternatives | Complete | Merged PR #92; alternatives remain useful if permissions are declined |
| DATA-02 | Corpus coverage/provenance dashboard and admin-only metrics API | Complete | Merged PR #94; coverage remains a registry metric, not total-law coverage |
| DATA-03 | Review terms and reuse conditions for every proposed external source | In progress | Merged PR #98 records WIPO/ILO policy limits; PR #105 adds Labour Law 14/2025 source review metadata; Egyptian primary portal terms and item-level rights remain unresolved |
| DATA-04 | Prioritized Egyptian instrument metadata inventory | In progress | Merged PR #97 adds structural/permission-state validation and CI tests for the 69-record inventory; PR #105 adds Labour Law 14/2025 review metadata; candidates remain metadata-only |
| DATA-05 | Expand the verified starter corpus using permitted acquisition routes | Blocked / ongoing | Depends on lawful source copies, source-specific terms, and lawyer validation; continue metadata discovery meanwhile |
| DATA-06 | Firm-supplied document ingestion with provenance and tenant scoping | Complete | Merged PR #100 adds per-upload SHA-256, uploader/firm metadata, extraction/OCR state and chunk-to-document linkage; binaries are not retained; duplicate uploads remain separate records |
| DATA-07 | OCR/extraction review against original pages | In progress | Merged PR #101 adds audited extraction correction; merged PR #103 adds reviewer-entered page references, stale-correction rejection, and compare-and-swap updates; original binaries/page previews and reviewer UI remain outstanding |
| RSH-01 | Full research result/source inspector with exact passages and pin-cites | In progress | Merged PR #96 adds explicit scopes, status labels, literal Arabic/English term highlighting, passage/citation actions, optional page pin-cites with migration, memo export/save, and metadata-only discovery; existing chunks without page metadata remain unpinned |
| RSH-02 | Arabic retrieval evaluation set and citation-quality metrics | In progress | Merged PR #99 adds Recall@k/MRR, citation source precision, exact reviewed pin-cite scoring, and abstention compliance; unreviewed seeds are excluded from scores, and no quality score is claimed until reviewed labels and real runs exist |
| RSH-03 | Amendment/repeal graph and historical version comparison | Not started | Use only evidence-backed version relations and effective dates |
| UI-04 | Complete responsive browser/RTL/LTR/keyboard/reader QA | Not started | Test mobile, tablet, 200% zoom, forced colors, screen readers, errors and empty states |
| UX-01 | Lawyer usability study for core research and case tasks | Not started | Test with 3–5 Egyptian lawyers; record completion rate, time, errors and trust |
| SEC-01 | Multi-firm isolation verification and independent security review | In progress | Merged PR #102 covers research conversation boundaries, #104 adds extraction-review read/write denial tests, #107 adds tenant-boundary inventory and cross-firm audit regression tests, and #108 adds runtime route/schema inventory drift checks. PR #109 hardens encrypted restore to authenticate before replacing a destination and stage writes atomically. Global legal-review endpoints now require a deployment-configured platform reviewer allowlist in addition to admin role. Proposed target architecture is documented in docs/database_tenancy_architecture.md: shared app, trusted tenant catalog, database per firm, and separately controlled shared legal corpus. PR #112 is merged, but this is a design proposal only; current shared SQLite remains. docs/database_boundary_phase0_review.md records an initial static review of storage entry points, table classifications, mixed legal/matter search, identity/session questions, and migration exit criteria (PR #114). PR #115 extracts SQLite connection lifecycle behind a testable provider without changing the single configured database path; its CI passed and it is merged, but it does not select tenant databases or provide isolation. docs/repository_storage_entrypoint_inventory.md records the non-route CLI, corpus tooling, file outputs, backup/restore, deployment-preflight, and external job-inventory gaps (PR #116 merged; CI passed). docs/identity_firm_membership_contract.md proposes global identities with explicit many-to-many firm memberships, session/membership revocation rules, and acceptance tests (PR #117 merged as a proposal, not approved or implemented). docs/data_ownership_migration_map.md maps declared tables/resources to candidate firm, control-plane, and shared-corpus ownership, with unresolved rows and migration gates (PR #119 merged; draft only, not an exhaustive audit). Obtain product/deployment-owner approval, complete the real deployment inventory and exhaustive query/file review, then build trusted tenant provisioning, migration tooling, firm-specific backup/restore, and independent review. |
| SEC-02 | Production account recovery, MFA/session/device controls and retention policies | Not started | Complete threat model and release checklist before public/production launch |
| OPS-01 | Production observability, backup/restore rehearsal and deployment release gates | Not started | Add structured logs, alerts, backup restore test and documented rollback |

## Progress rules

1. A merged PR with passing CI can complete code work, but it does not complete manual QA unless manual evidence is recorded.
2. Permission status must be supported by written evidence. Public visibility, HTTPS, a successful download, or an official contact email does not establish bulk or commercial reuse permission.
3. Keep these states separate: source discovered, metadata recorded, text acquired, extraction reviewed, authenticity verified, legal status verified, amendment history verified, and reuse permission approved.
4. Exclude fictional test corpus data from real-law coverage metrics.
5. Report coverage as registered candidates and verified operative versions, not as an unqualified “percentage of Egyptian law covered.”

## Immediate next actions

1. Continue DATA-07: approve secure original-file retention and implement reviewer UI/page previews; merged PR #103 adds only reviewer-entered page references and concurrency protection.
2. Do not claim retrieval evaluation quality until RSH-02 has lawyer-labelled questions and real runs; its harness is merged in PR #99.
3. Complete manual RTL/LTR/keyboard/screen-reader and lawyer review for the merged source inspector (RSH-01).
4. Continue item-level terms and reuse review for Egyptian sources under DATA-03; retain unknown permission states unless evidence supports a change.
5. Continue the 69-candidate metadata inventory under DATA-04, adding only verified metadata and source references.

6. Continue SEC-01: PR #117's identity contract is merged as a proposal only; product-owner approval is still required. Review docs/data_ownership_migration_map.md (PR #119 merged) with the data and deployment owners; confirm table ownership, mixed FTS partitioning, identity/audit treatment, and orphan-row quarantine. Obtain the actual deployment/job inventory and finish the exhaustive query/file review. Only then define trusted tenant catalog/provisioning and test storage routing before migration. Add per-firm backup/restore and migration rehearsal after ownership boundaries are approved. Shared SQLite is not tenant-separated.

## Known limitations

- The legal corpus is not comprehensive and may lack current amendments.
- Some source permission requests may be declined or unanswered; the roadmap must remain useful without them.
- A practice-area value of `unknown` means unclassified, not absent or covered.
- Automated tests cannot substitute for legal review, manual accessibility checks or security assessment.
