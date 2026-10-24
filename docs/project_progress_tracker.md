# Legal Copilot — Project Progress Tracker

**Last updated:** 2026-10-24  
**Tracking method:** deliverable-level checklist, not an estimate of engineering hours. A task is “complete” only when its change is merged and its acceptance criteria are met. Open PRs are in progress, not complete.

## Overall status

- **Completed and merged:** 7 of 19 tracked deliverables (**36.8%**).
- **In progress:** 6 of 19 deliverables (**31.6%**).
- **Not started, blocked, or awaiting validation:** 6 of 19 (**31.6%**).
- **Merged PRs from this workstream:** #88, #89, #90, #91, #92, #94, #96, #97, #98, #99, #100, #101, #102, #103.
- **Open PRs:** none at last check; SEC-01 follow-through is in progress on the current branch.
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
| DATA-03 | Review terms and reuse conditions for every proposed external source | In progress | Merged PR #98 records WIPO/ILO policy limits; Egyptian primary portal terms and item-level rights remain unresolved |
| DATA-04 | Prioritized Egyptian instrument metadata inventory | In progress | Merged PR #97 adds structural/permission-state validation and CI tests for the 69-record inventory; candidates remain metadata-only |
| DATA-05 | Expand the verified starter corpus using permitted acquisition routes | Blocked / ongoing | Depends on lawful source copies, source-specific terms, and lawyer validation; continue metadata discovery meanwhile |
| DATA-06 | Firm-supplied document ingestion with provenance and tenant scoping | Complete | Merged PR #100 adds per-upload SHA-256, uploader/firm metadata, extraction/OCR state and chunk-to-document linkage; binaries are not retained; duplicate uploads remain separate records |
| DATA-07 | OCR/extraction review against original pages | In progress | Merged PR #101 adds audited extraction correction; merged PR #103 adds reviewer-entered page references, stale-correction rejection, and compare-and-swap updates; original binaries/page previews and reviewer UI remain outstanding |
| RSH-01 | Full research result/source inspector with exact passages and pin-cites | In progress | Merged PR #96 adds explicit scopes, status labels, literal Arabic/English term highlighting, passage/citation actions, optional page pin-cites with migration, memo export/save, and metadata-only discovery; existing chunks without page metadata remain unpinned |
| RSH-02 | Arabic retrieval evaluation set and citation-quality metrics | In progress | Merged PR #99 adds Recall@k/MRR, citation source precision, exact reviewed pin-cite scoring, and abstention compliance; unreviewed seeds are excluded from scores, and no quality score is claimed until reviewed labels and real runs exist |
| RSH-03 | Amendment/repeal graph and historical version comparison | Not started | Use only evidence-backed version relations and effective dates |
| UI-04 | Complete responsive browser/RTL/LTR/keyboard/reader QA | Not started | Test mobile, tablet, 200% zoom, forced colors, screen readers, errors and empty states |
| UX-01 | Lawyer usability study for core research and case tasks | Not started | Test with 3–5 Egyptian lawyers; record completion rate, time, errors and trust |
| SEC-01 | Multi-firm isolation verification and independent security review | In progress | Merged PR #102 covers research conversation boundaries; current follow-through adds cross-firm extraction-review read/write denial tests. Shared DB remains; full endpoint/table/job inventory, backup/restore tests, and independent review are outstanding |
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

6. Continue SEC-01 with an endpoint/table/background-job inventory, backup/restore isolation tests, and independent review; the current shared SQLite database is not tenant-separated.\n\n## Known limitations

- The legal corpus is not comprehensive and may lack current amendments.
- Some source permission requests may be declined or unanswered; the roadmap must remain useful without them.
- A practice-area value of `unknown` means unclassified, not absent or covered.
- Automated tests cannot substitute for legal review, manual accessibility checks or security assessment.
