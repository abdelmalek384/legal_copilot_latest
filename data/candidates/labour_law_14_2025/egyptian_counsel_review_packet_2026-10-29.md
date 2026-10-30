# Egyptian Labour Law 14/2025 — qualified counsel review packet

**Prepared:** 2026-10-29
**Purpose:** A ready-to-use review checklist for a qualified Egyptian employment-law lawyer. This document is not itself legal review, and no lawyer approval is claimed.

## Review scope

1. Law No. 14/2025 promulgation provisions (Articles 1–13), especially commencement, transitional rules, repeals and specialized labour courts.
2. 120 numerical candidate assertions in evidence ledger batches 1–7, with article/page/text-line pinpoints.
3. Implementing instruments and temporal relations, including Decisions 49/2026, 74/2026, 75/2026, 162/2026, 294/2025, Decree 2652/2026, Decree 3165/2026 and the new 248–252/2026 discovery leads.
4. Source-access/reuse scope, including Egyptian IP Law No. 82/2002 Article 141 and the distinction between official legal text, a portal's access terms, scans, editorial content and creative compilations.
5. Retrieval safety: exact citations, effective dates, exceptions, as-of queries, and abstention where a supporting source is absent.

## Required per-rule decision

For every candidate rule, counsel should record:

- Candidate ID and statutory/instrument pinpoint.
- Whether the wording matches the enacted/published official text; if not, quote the exact mismatch and proposed correction.
- Applicable worker/employer categories and exceptions.
- Triggering event, counting method, deadlines, and any special day-count convention.
- Effective interval, transitional application, amendment/repeal/corrigendum history and related implementing instruments.
- Whether the rule is safe to encode as a general rule, needs case-specific qualifications, or must be excluded from automated advice.
- Review outcome: `approved`, `approved_with_conditions`, `rejected`, or `needs_more_evidence`.
- Reviewer name/qualification, review date, notes and signature/reference.

## Hard release gates

- [ ] Actual 311-row candidate JSONL received and its SHA-256 recalculated.
- [ ] Official Gazette source artifact lawfully obtained; original-file SHA-256 recorded; relevant pages visually reviewed.
- [ ] All 311 records compared article-by-article; numeric, major, missing and extra differences resolved or explicitly accepted with reasons.
- [ ] Six spelling outliers (Arts. 66, 103, 124, 134, 141, 278) compared token-by-token; source-layer spelling preserved.
- [ ] 120 numerical candidate assertions reviewed and exceptions/triggers validated.
- [ ] Implementing instruments, later amendments and corrigenda reviewed; unresolved restricted-access notices remain explicitly unknown.
- [ ] Intended source collection/storage/indexing/display/commercial-use scope reviewed and documented.
- [ ] Qualified Egyptian-lawyer decision recorded for each rule or a documented set of rules.
- [ ] Retrieval evaluation passes exact-citation and abstention tests; unreviewed content remains non-authoritative.

## Current status

- Candidate numerical ledger: 120/120 entries by count; **0/120 counsel-approved**.
- Full candidate-to-Gazette comparison: not executed because the actual JSONL is not mounted in this session.
- Official Gazette PDF: browser text and six rendered-page spot checks available; original bytes/hash unavailable after two ordinary download failures.
- Implementing instruments: discovery metadata and selected official searchable texts recorded; several full issue PDFs/corrigenda remain restricted or not located.
- No content is marked lawyer-approved, verified-current, rights-cleared or retrieval-eligible.

## Suggested decision record (copy per rule)

```text
Candidate ID:
Official citation / article / page:
Text match: exact / whitespace-only / uncertain / mismatch
Applicable scope:
Trigger and counting method:
Exceptions / related instruments:
Effective interval and amendment status:
Reuse/access review reference:
Counsel outcome: approved / approved_with_conditions / rejected / needs_more_evidence
Conditions or correction required:
Reviewer qualification/name:
Review date:
Signature / file reference:
```