# Legal knowledge progress report — 2026-10-29

**Scope:** Evidence-backed Egyptian Labour Law 14/2025 workstream and the related OSH implementing Decisions 248–252/2026.  
**Current branch:** `legal-knowledge-evidence-2026-10-29`  
**Draft PR:** [#840](https://github.com/abdelmalek384/legal_copilot_latest/pull/840)

## Headline

**Overall evidence-backed legal-content readiness remains 7%.** The source-discovery and candidate-extraction work has advanced, but no Table 24 exposure limit has passed official Gazette matching, complete currentness review, source-use assessment, and qualified Egyptian OSH counsel approval.

Table 24 candidate extraction now covers **617/745 numbered entries (82.8%)**. This is extraction coverage only, not verified-law coverage. The official Gazette PDF bytes/hash and row-by-row primary-source comparison remain unavailable. No Table 24 row is approved for authoritative retrieval.

## Latest work completed

1. Found the full secondary transcription of Decision 250/2026 at:
   https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html
   It exposes Table 24 and the previously missing printed pages 296–370 at the text-discovery layer, but is not the Official Gazette file.
2. Added **31 structured candidate JSON batches** covering Table 24 numbered entries 1–617. Source-line pinpoints are recorded; parent/child chemical variants are preserved; suspicious CAS strings, formulas, decimal/unit ordering, surface/air limits and text-layer anomalies are flagged rather than silently corrected.
3. Performed structural audits across successive ranges. The checked records cover a continuous row-number sequence through 617, with no gaps or duplicates found in those audits. Each candidate remains `pending_official_match`; this is a structural check, not legal verification.
4. Added `tools/validate_decision250_table24_candidates.py` and a unit test. The validator is fail-closed on missing/duplicate row numbers, invalid JSON, missing source pinpoints, missing names, wrong source metadata, or a row prematurely marked reviewed.
5. Added `tools/build_decision250_table24_review_queue.py` and tests. It creates a triage queue for anomalies, high-risk rows, currentness leads, group-level entries and possible surface/air-unit ambiguity without auto-correcting source data.
6. Added `tools/build_decision250_table24_primary_match_register.py` and tests. It creates a fail-closed row-level register for all 617 extracted candidates; official page/hash, text-match, currentness, source-use and counsel fields start blank/not started, and retrieval eligibility is false.
7. Added CI workflow steps to validate the candidate batches, test the validator and review-queue behavior, and build the review queue. A completed CI result for the latest head has **not** been confirmed; no passing CI claim is made.
8. Prepared `lawyer_in_app_acceptance_plan_2026-10-29.md` for a later hands-on review in the running app. This makes lawyer review a separate release gate; it does not claim any lawyer approval.
9. Decision 250 Table 23 remains at **137/137 candidate labels**. Labels are transcribed from secondary text and still require official page matching.
10. Decision 251 has 17 candidate licensing/experience/fee assertions; Decision 252 has 40 candidate assertions. They remain secondary/unverified pending official comparison.
11. The Decisions 248–252 clause discrepancy checklist and related source-route/currentness notes remain candidate evidence, not verified legal conclusions.

## Current subtask status

| Subtask | Completion estimate | Current status | Remaining gate |
|---|---:|---|---|
| Decision 250 source discovery | 90% | Full secondary transcription located | Official Gazette bytes/hash and complete primary-source match |
| Decision 250 Table 23 candidate labels | 100% candidate-label coverage | 137/137 Arabic labels present | Official page matching, currentness, source-use review, counsel |
| Decision 250 Table 24 candidate extraction | **82.8%** | 617/745 numbered entries structured in 31 batches | Extract remaining entries; primary-source match; currentness and counsel |
| Table 24 official Gazette row matches | 0% | No row-by-row official match completed | Obtain official file/page images and compare every candidate row |
| Table 24 currentness review | 0% complete | Not established by secondary transcription | Confirm applicable amendments, corrigenda and current status |
| Table 24 qualified counsel approval | 0% | No entries approved | Qualified Egyptian OSH lawyer must review source-matched rows |
| Decision 249 implementation circular | 35% search work | Ministry announced periodic circulars; separate public circular not located | Find and verify the circular, or preserve the unresolved gap |
| Decision 251 candidate extraction | 70% extraction work | 17 candidate assertions structured | Official-source comparison, currentness and counsel |
| Decision 252 candidate extraction | 75% extraction work | 40 candidate assertions structured | Official-source comparison, ambiguous table cells, currentness and counsel |
| Original Official Gazette PDF hash | 0% | Original PDF bytes/hash not obtained | Obtain the PDF through ordinary authorized access and hash actual bytes |
| Original 311-row `law_rows_ar.jsonl` reconciliation | 0% in this runtime | File is not available here; historical hash only | User to upload the original file; do not reconstruct it or claim a new hash |
| Source-use/access assessment | Open | No blanket commercial reuse conclusion | Assess official-text status, website terms, compilation rights and intended use |
| Lawyer in-app acceptance | Prepared; review not started | Test plan linked from the corpus README | Run after technical completion, before production release |

## Source and safety boundaries

- The Table 24 candidate source is a secondary transcription. It is useful for discovery, not proof of official wording.
- The Official Gazette catalogue identifies Decisions 248–252/2026 in the supplement to Egyptian Proceedings issue 225(A), dated 2026-10-12:
  https://dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full
- Previous access attempts did not obtain the original Gazette PDF bytes. No original-file SHA-256 is claimed.
- The source text contains apparent transcription anomalies, including reversed or malformed numeric/unit tokens, suspicious formulas/CAS identifiers, mixed surface and air limits, and entries marked as removed. Those remain flagged and must not be presented as current legal/safety guidance.
- The review queue and validator do not authenticate the source, determine currentness, settle reuse rights, or approve a legal rule.
- Lawyer approval must be recorded against the exact app version, corpus version, and tested scope. Reviewing the app is separate from, and does not replace, official-source comparison.

## Next work items, in order

1. Continue candidate extraction from Table 24 row 618 onward, using only source text actually available; do not invent missing entries.
2. Complete the remaining Table 24 numbered entries and validate the continuous row-number sequence.
3. Obtain the official Gazette PDF and record its SHA-256, retrieval date and source URL.
4. Compare each Table 24 row and footnote against the official page image. Resolve all units, limits, CAS/formula tokens, parent-child relationships and surface/air distinctions; leave ambiguous rows quarantined.
5. Build the final row-level currentness and source-use review records.
6. Run the in-app counsel acceptance plan on the actual staging app after technical completion; fix defects and rerun the whole regression set.
7. Keep authoritative retrieval disabled for candidate-only content until the applicable release gates are satisfied.

## Release status

- Official Gazette matched Table 24 rows: **0**
- Currentness-complete Table 24 rows: **0**
- Lawyer-approved Table 24 rows: **0**
- Table 24 rows eligible for authoritative retrieval: **0**
- Overall evidence-backed legal-content readiness: **7%**

These figures intentionally separate extraction progress from legal verification. A nearly complete transcription is not a nearly verified legal corpus.
