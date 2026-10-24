# Legal Copilot — Project Progress Tracker

**Last updated:** 2026-10-24  
**Tracking method:** deliverable-level checklist, not an estimate of engineering hours. A task is “complete” only when its change is merged and its acceptance criteria are met. Open PRs are in progress, not complete.

## Overall status

- **Completed and merged:** 4 of 20 tracked deliverables (**20%**).
- **In progress:** 2 of 20 deliverables (**10%**).
- **Not started, blocked, or awaiting validation:** 14 of 20 (**70%**).
- **Merged PRs from this workstream:** #88, #89, #90, #91.
- **Open PRs:** #92 (corpus/UX roadmap documentation), #94 (coverage dashboard implementation; CI was running at last check).
- **External permission requests:** not sent by this project workflow. Claude is expected to handle outreach; approval is not assumed.
- **Manual UI QA:** not yet completed.

Percentages count deliverables equally; they are not a claim that 20% of all coding hours or all product capability is complete.

## Task register

| ID | Deliverable | Status | Evidence / next action |
|---|---|---|---|
| UI-01 | Responsive workspace baseline and dashboard shortcuts | Complete | Merged PR #88 |
| UI-02 | Keyboard navigation, skip link, language-switch and modal accessibility | Complete | Merged PR #89; manual assistive-technology QA remains a separate task |
| UI-03 | Saved research search/rename and safer source-link handling | Complete | Merged PR #91; this is not the complete source-inspector workflow |
| SRC-01 | Permission outreach tracker, official contact verification and permission-gate tests | Complete | Merged PR #90; verified contact does not mean permission granted |
| DATA-01 | Document permission-aware corpus strategy and alternatives | In progress | PR #92; review and merge the strategy documents |
| DATA-02 | Corpus coverage/provenance dashboard and admin-only metrics API | In progress | PR #94; wait for CI, fix failures, review and merge |
| DATA-03 | Review terms and reuse conditions for every proposed external source | Not started | Record item-specific terms, allowed purpose, attribution and evidence before ingestion |
| DATA-04 | Prioritized Egyptian instrument metadata inventory | Not started | Seed metadata-only candidates with source URL and unknown states; never fabricate legal text |
| DATA-05 | Expand the verified starter corpus using permitted acquisition routes | Blocked / ongoing | Depends on lawful source copies, source-specific terms, and lawyer validation; continue metadata discovery meanwhile |
| DATA-06 | Firm-supplied document ingestion with provenance and tenant scoping | Not started | Build upload, hashing, ownership, retention and access-control workflow |
| DATA-07 | OCR/extraction review against original pages | Not started | Add page preview, OCR confidence, corrections and reviewer audit trail |
| RSH-01 | Full research result/source inspector with exact passages and pin-cites | Partial | Source links and saved-research UX improved in #91; exact passage/version inspection and no-source states remain |
| RSH-02 | Arabic retrieval evaluation set and citation-quality metrics | Not started | Lawyer-reviewed questions; measure retrieval recall, pin-cite accuracy, stale-law and answerability failures |
| RSH-03 | Amendment/repeal graph and historical version comparison | Not started | Use only evidence-backed version relations and effective dates |
| UI-04 | Complete responsive browser/RTL/LTR/keyboard/reader QA | Not started | Test mobile, tablet, 200% zoom, forced colors, screen readers, errors and empty states |
| UX-01 | Lawyer usability study for core research and case tasks | Not started | Test with 3–5 Egyptian lawyers; record completion rate, time, errors and trust |
| SEC-01 | Multi-firm isolation verification and independent security review | Not started | Follow the existing multi-firm isolation plan; test guessed IDs, uploads, search, exports and backups |
| SEC-02 | Production account recovery, MFA/session/device controls and retention policies | Not started | Complete threat model and release checklist before public/production launch |
| OPS-01 | Production observability, backup/restore rehearsal and deployment release gates | Not started | Add structured logs, alerts, backup restore test and documented rollback |

## Progress rules

1. A merged PR with passing CI can complete code work, but it does not complete manual QA unless manual evidence is recorded.
2. Permission status must be supported by written evidence. Public visibility, HTTPS, a successful download, or an official contact email does not establish bulk or commercial reuse permission.
3. Keep these states separate: source discovered, metadata recorded, text acquired, extraction reviewed, authenticity verified, legal status verified, amendment history verified, and reuse permission approved.
4. Exclude fictional test corpus data from real-law coverage metrics.
5. Report coverage as registered candidates and verified operative versions, not as an unqualified “percentage of Egyptian law covered.”

## Immediate next actions

1. Check CI for PR #94; fix any API or frontend regression before merge.
2. Review and merge PR #92 once its documentation is approved.
3. After #94 is merged, implement the full Research Results & Source Inspector (RSH-01).
4. In parallel, build the metadata-only instrument inventory and document source-specific terms.
5. Record Claude's outreach status and any written replies in the permission tracker; do not change permissions until written terms are reviewed.

## Known limitations

- The legal corpus is not comprehensive and may lack current amendments.
- Some source permission requests may be declined or unanswered; the roadmap must remain useful without them.
- A practice-area value of `unknown` means unclassified, not absent or covered.
- Automated tests cannot substitute for legal review, manual accessibility checks or security assessment.
