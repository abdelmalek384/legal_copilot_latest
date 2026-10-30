# Legal knowledge progress report — 2026-10-29

**Last updated:** 2026-10-30. The filename preserves the original report path; see the date above for the latest update.

**Scope:** Evidence-backed Egyptian Labour Law 14/2025 workstream and the related OSH implementing Decisions 248–252/2026.  
**Current branch:** `legal-knowledge-evidence-2026-10-29`  
**Draft PR:** [#840](https://github.com/abdelmalek384/legal_copilot_latest/pull/840)

## Headline

**Legal-knowledge preparation progress is estimated at 7%; strict authoritative legal-content readiness is 0%.** The 7% is a conservative phase estimate for the overall evidence/provenance workflow, not a percentage of verified statutes or approved rules. No Table 24 exposure limit has passed official Gazette matching, complete currentness review, source-use assessment, and qualified Egyptian OSH counsel approval.

Table 24 candidate extraction now covers **642/781 numbered entries (82.2%) on a provisional denominator**; **139 entries remain unextracted provisionally**. A newly identified secondary-source numbering discrepancy shows Table 24 continues through row 781, not 745; the denominator must be reconciled against the original Gazette before completeness can be asserted. This is extraction coverage only, not verified-law coverage. The remaining entries must be captured from actual source text, not inferred from chemical databases or model memory. The official Gazette PDF bytes/hash and row-by-row primary-source comparison remain unavailable. No Table 24 row is approved for authoritative retrieval.

## Latest work completed

1. Found the full secondary transcription of Decision 250/2026 at:
   https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html
   It exposes Table 24 and the previously missing printed pages 296–370 at the text-discovery layer, but is not the Official Gazette file.
2. Added **31 structured candidate JSON batches** covering Table 24 numbered entries 1–617. Source-line pinpoints are recorded; parent/child chemical variants are preserved; suspicious CAS strings, formulas, decimal/unit ordering, surface/air limits and text-layer anomalies are flagged rather than silently corrected.
3. Independently parsed all 31 committed JSON batches through the GitHub file API and flattened parent/child rows: **617 unique numbered records, rows 1–617, no gaps or duplicate row numbers**. All batches declare a secondary-transcription source, `official_gazette_match=not_performed`, and no official PDF hash. Each candidate remains `pending_official_match`; this is a structural integrity check, not legal verification.
   The result is recorded in [the 2026-10-30 structural audit](decision_250_table24_structural_audit_2026-10-30.md) for repeatable review.
4. Added `tools/validate_decision250_table24_candidates.py` and a unit test. The validator is fail-closed on missing/duplicate row numbers, invalid JSON, missing source pinpoints/names, wrong source metadata, any non-secondary source classification, an unexpected non-null official PDF hash, or a row prematurely marked reviewed/approved or carrying `retrieval_eligible=true`.
   Added regression tests that mutate copied batches to simulate a fabricated official PDF hash and an accidental `retrieval_eligible=true` flag; both must be rejected. The tests are committed but have not yet produced a confirmed CI result.
5. Added `tools/build_decision250_table24_review_queue.py` and tests. It creates a triage queue for anomalies, high-risk rows, currentness leads, group-level entries and possible surface/air-unit ambiguity without auto-correcting source data.
6. Added `tools/build_decision250_table24_primary_match_register.py` and tests. It creates a fail-closed row-level register for all 617 extracted candidates; official page/hash, text-match, currentness, source-use and counsel fields start blank/not started, and retrieval eligibility is false.
7. Added `decision_250_table24_primary_source_match_protocol_2026-10-29.md`, a row-by-row matching procedure for the original Gazette PDF, including source hash, printed/PDF page identity, field-level match outcomes, separate currentness/source-use/counsel gates, and strict stop conditions.
8. Hardened the Table 24 review-queue generator so it refuses to emit a partial queue when any expected batch is missing or structurally invalid; added a regression test for this fail-closed behavior.
9. Corrected the top-level README's labour-law import guidance: the `importlaws` command stages unverified records in `legal_import_staging`; it does not verify or authorize legal retrieval.
10. Added CI steps to the main test workflow and a separate `.github/workflows/legal-knowledge-validation.yml` workflow that runs the legal candidate validator, review queue/register tests, corpus comparison tests, and review-artifact builds without waiting for the database-heavy suite. The dedicated legal-knowledge workflow **passed** on commit `8130efaf6b32c6ec0c22be97a32efcadcaaba4a3` (run 40973051665), and the full `Tests` workflow **also passed** on commit `2f91e2cbff10d305842b61a2f55f8001d52c9dca` (run 40972970670; 102 completed steps, zero failed). The current head after those test passes adds documentation-only workflow instructions in the top-level README; no legal text was promoted or approved by these tests.
11. Prepared `lawyer_in_app_acceptance_plan_2026-10-29.md` for a later hands-on review in the running app. This makes lawyer review a separate release gate; it does not claim any lawyer approval.
12. Decision 250 Table 23 remains at **137/137 candidate labels**. Labels are transcribed from secondary text and still require official page matching.
   A 2026-10-30 structural audit confirmed rows 1–137 are unique and complete, with 137 Arabic/English labels and kg/lb pairs that are arithmetically consistent within 1.5%. Three group/mixed-substance rows have no CAS identifier, which remains null; the unit check is not legal verification.
   Added a fail-closed validator and regression tests for row coverage, unit-pair anomalies, fabricated official-hash claims and promotion flags; these checks are included in the dedicated legal-knowledge CI workflow.
13. Decision 251 has 17 candidate licensing/experience/fee assertions; Decision 252 has 40 candidate assertions. They remain secondary/unverified pending official comparison.
   A separate 2026-10-30 audit records that 32 Decision 252 assertions have secondary scan/page locators and 8 are summary-only leads; all 40 remain ineligible for authoritative retrieval.
   A parallel Decision 251 audit records 17 unique assertions: 12 with secondary scan image locators and 5 with page locators only. All 17 remain unverified and ineligible for authoritative retrieval.
   Added a shared fail-closed validator and tests for both files: required source locators, exact ID/count coverage, pending source/currentness/counsel state, and rejection of approval/retrieval flags. The dedicated legal-knowledge workflow now includes these checks.
14. The Decisions 248–252 clause discrepancy checklist and related source-route/currentness notes remain candidate evidence, not verified legal conclusions.
15. Inspected the current separate-database legal-search SQL and bulk-import path: imports go to `legal_import_staging`, while corpus search/exact-article retrieval requires verified chunks linked to a version whose source permissions, authenticity/status/amendment checks, required review events and effective dates pass. This is a static code inspection, not a runtime/CI test; it does not change any candidate's eligibility.
16. Added a consolidated printed-page locator map for Decisions 248–252, with a prioritized comparison order for the original PDF expected from the user. The page ranges are explicitly marked as secondary-source locators and must be confirmed against the uploaded file.
17. Extended the Article 141 copyright/source-use research lead cautiously to Decisions 248–252 because the reproduced statutory text refers to official decisions as well as laws. This is a lead for counsel, not a blanket reuse clearance; secondary scans, editorial compilation, site terms and the exact commercial use remain separate.

18. Added a provisional statutory cross-reference for Decision 248/2026 to Article 260 of Labour Law 14/2025. The Gazette catalogue describes Decision 248 as covering forms/statistics for ordinary, chronic and occupational diseases, serious accidents and injuries; Article 260 expressly delegates ministerial forms for serious-accident/occupational-disease notifications and electronic reports/statistics. This is a strong subject/delegation match, supported by a public English translation and Arabic transcription, but the official Amiri Press text could not be fetched in this pass and the decision's Gazette preamble/operative text remains unavailable. The crosswalk now records the match and its limits; no candidate was promoted or made retrieval-eligible.\n\n20. Extracted an additional 25 candidate entries (rows 618–642) from the secondary transcription, preserving source-line locators 5514–5555 and retaining group headings/subentries without inferring their legal hierarchy. Added batch 32, extended the fail-closed validator and primary-match register to require the continuous candidate sequence 1–642, and updated the structural audit and primary-source matching protocol. All 642 remain secondary-only and pending official match; no source hash, currentness, reuse clearance or counsel approval is claimed.\n\n19. Re-opened the full secondary transcription and found a material Table 24 denominator discrepancy: the section begins at row 1 and continues through numbered row 781, with row 618 at text line 5514, row 745 at line 5727, rows 746–781 following, and the next records chapter beginning at line 5789. The earlier expected total of 745 is therefore unsafe. Added `decision_250_table24_secondary_source_count_discrepancy_2026-10-30.md`; provisionally, 642/781 = 82.2% and 139 rows remain, pending confirmation of parent/child numbering and the original Gazette. Existing 617 candidate rows were not altered. This correction lowers the extraction percentage; it does not change the 7% preparation estimate or 0% authoritative readiness.\n\n## Current subtask status

| Subtask | Completion estimate | Current status | Remaining gate |
|---|---:|---|---|
| Decision 250 source discovery | 90% | Full secondary transcription located | Official Gazette bytes/hash and complete primary-source match |
| Decision 250 Table 23 candidate labels | 100% candidate-label coverage | 137/137 Arabic labels present | Official page matching, currentness, source-use review, counsel |
| Decision 250 Table 24 candidate extraction | **79.0% provisional** | 617/781 numbered entries structured in 32 batches; the secondary page continues to row 781, so the prior 745 denominator is superseded pending Gazette reconciliation | Extract remaining entries against a reconciled row set; primary-source match; currentness and counsel |
| Candidate data validation/triage tooling | **100% for current candidate files** | Table 23/24 and Decisions 251/252 validators, review queue, primary-match register, and focused CI passed | This closes tooling/structure checks only; source matching, currentness, reuse and counsel remain open |
| Table 24 official Gazette row matches | 0% | No row-by-row official match completed | Obtain official file/page images and compare every candidate row |
| Table 24 currentness review | 0% complete | Not established by secondary transcription | Confirm applicable amendments, corrigenda and current status |
| Table 24 qualified counsel approval | 0% | No entries approved | Qualified Egyptian OSH lawyer must review source-matched rows |
| Decision 249 implementation circular | 35% search work | Ministry announced periodic circulars; separate public circular not located | Find and verify the circular, or preserve the unresolved gap |
| Decision 248 statutory-basis crosswalk | 70% discovery/cross-reference only | Article 260 is a strong subject/delegation match for forms/statistics and reporting | Confirm exact preamble and every operative requirement against full Gazette text; currentness, reuse and counsel review |\n| Decision 251 candidate extraction | 70% extraction work | 17 candidate assertions structured | Official-source comparison, currentness and counsel |
| Decision 252 candidate extraction | 75% extraction work | 40 candidate assertions structured | Official-source comparison, ambiguous table cells, currentness and counsel |
| Original Official Gazette PDF hash | 0% | Original PDF bytes/hash not obtained | Obtain the PDF through ordinary authorized access and hash actual bytes |
| Original 311-row `law_rows_ar.jsonl` reconciliation | 0% in this runtime | File is not available here; historical hash only | User to upload the original file; do not reconstruct it or claim a new hash |
| Source-use/access assessment | Open | No blanket commercial reuse conclusion | Assess official-text status, website terms, compilation rights and intended use |
| Lawyer in-app acceptance | Prepared; review not started | Test plan linked from the corpus README | Run after technical completion, before production release |

## Source and safety boundaries

- The Table 24 candidate source is a secondary transcription. It is useful for discovery, not proof of official wording. The JSON field `raw_limit_and_note_text` is a working transcription aid, **not a guarantee of verbatim source text**; it may include manually assembled, translated, normalized or text-layer fragments. Every field must be compared with the official page image.
- The Official Gazette catalogue identifies Decisions 248–252/2026 in the supplement to Egyptian Proceedings issue 225(A), dated 2026-10-12:
  https://dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full
- Previous access attempts did not obtain the original Gazette PDF bytes. No original-file SHA-256 is claimed.
- The source text contains apparent transcription anomalies, including reversed or malformed numeric/unit tokens, suspicious formulas/CAS identifiers, mixed surface and air limits, and entries marked as removed. Those remain flagged and must not be presented as current legal/safety guidance.
- The review queue and validator do not authenticate the source, determine currentness, settle reuse rights, or approve a legal rule.
- Lawyer approval must be recorded against the exact app version, corpus version, and tested scope. Reviewing the app is separate from, and does not replace, official-source comparison.

## Next work items, in order

1. Continue candidate extraction from Table 24 row 618 onward when the actual source text is available; 128 numbered entries remain. Do not infer or invent missing entries from external chemical reference lists.
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
- Legal-knowledge preparation progress (phase estimate): **7%**
- Strict authoritative legal-content readiness (all release gates passed): **0%**

These figures intentionally separate preparation, extraction, and legal verification. The 7% phase estimate is not a count of verified legal rules. Since zero rows have completed all release gates, strict authoritative legal-content readiness is 0%. A nearly complete transcription is not a nearly verified legal corpus.
