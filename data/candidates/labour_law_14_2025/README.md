# Labour Law No. 14 of 2025 — candidate corpus

**Status: pending full Official Gazette comparison, source-use assessment, and Egyptian-lawyer review. Not approved for authoritative retrieval.**

This directory tracks the supplied Arabic JSONL corpus and its source review. The supplied file is **not** committed to this public repository. Its source-use and redistribution conditions have not been fully assessed; this is an unresolved review item, not a claim that permission is necessarily required.

## Inspected artifact

- Supplied filename: `law_rows_ar.jsonl`
- SHA-256: `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600`
- Size: 393,861 bytes
- Records: 311 valid JSONL records (13 promulgation provisions and 298 articles of the accompanying law)
- All rows had `verified=0`; all rows had `in_force=1`. The latter is untrusted input and must never be used to establish legal status.
- Source: [Manshurat text copy](https://manshurat.org/content/qnwn-lml-ljdyd-rqm-14-lsn-2025)
- Claimed primary publication: Official Gazette issue 18 (supplement), 2025-05-03
- Review result: structural checks and selected text spot checks only; no full article-by-article comparison against the exact Gazette PDF.

## Candidate transcription fidelity warning

Decision 250 Table 24 JSON batches are **secondary-source candidate transcriptions**, not byte-for-byte quotations. The field `raw_limit_and_note_text` is a working transcription aid; it may contain manually assembled, translated, normalized, or text-layer fragments and must not be treated as verbatim official wording. Every label, formula, CAS token, number, unit, footnote and column association requires comparison against the original Gazette page image before any row can be used authoritatively.

## Current review documents

- [Legal-knowledge progress report (2026-10-29)](progress_report_2026-10-29.md): current subtask completion estimates, new scan-based source routes, blockers and release-gate counts.
- [Decision 250 Table 23 structural audit (2026-10-30)](decision_250_table23_structural_audit_2026-10-30.md): 137 unique rows and an arithmetic sanity check of kg/lb pairs; three group/mixed-substance rows retain null CAS identifiers and no official matches are claimed.
- [Table 23 candidate validator](../../../tools/validate_decision250_table23_candidates.py) and [tests](../../../tests/test_decision250_table23_candidate_validation.py): check the 137-row structure, fail closed on fabricated approval/hash flags, and flag kg/lb arithmetic discrepancies without correcting them.
- [Decision 250 Table 24 full structural audit (2026-10-30)](decision_250_table24_structural_audit_2026-10-30.md): independent parse of all 31 batches; 617 unique rows 1–617, no gaps/duplicates, with zero official matches claimed.
- [Decision 252 candidate assertion audit (2026-10-30)](decision_252_candidate_assertion_audit_2026-10-30.md): 40 unique candidates, 32 with secondary scan/page locators and 8 secondary-summary-only leads; no official match or counsel approval.
- [Decision 251 candidate assertion audit (2026-10-30)](decision_251_candidate_assertion_audit_2026-10-30.md): 17 unique licensing/eligibility candidates, 12 with secondary image locators and 5 page-only locators; no official match or counsel approval.
- [Decisions 251/252 candidate validator](../../../tools/validate_decisions_251_252_candidates.py) and [tests](../../../tests/test_decisions_251_252_candidate_validation.py): validate the 17/40 assertion sets, required source locators, pending review states and fail-closed promotion gates.
- [Consolidated original-Gazette page map for Decisions 248–252 (2026-10-30)](decisions_248_252_primary_source_page_map_2026-10-30.md): secondary printed-page locators and a prioritized row-by-row comparison order for the PDF when supplied.

- [Alternative public source routes and instrument inventory (2026-10-29)](alternative_public_source_routes_2026-10-29.md): maps official searchable Amiri Press texts, Ministry of Labour publications, Gazette catalogue metadata and secondary comparison routes; clearly separates full text from metadata-only leads and records currentness limits.
- [Decision 250 full secondary transcription access review (2026-10-29)](decision_250_full_secondary_transcription_access_review_2026-10-29.md): records the newly found full secondary text, Table 23/Table 24 page map and recovery of the previously missing printed pp.296–370; clearly marks official-file comparison, complete table extraction, currentness and counsel review as open.
- [Table 24 extraction progress update (2026-10-29)](progress_update_2026-10-29_table24_batch2.md): records the first 40/745 candidate entries extracted from the full secondary transcription and the unresolved official-source/counsel gates.
- [Decision 250 Table 24 candidate batch 1, rows 1–20](decision_250_table24_candidate_batch1_rows001_020_2026-10-29.json): source-pinned secondary candidate records; raw limit strings retained and not approved for safety/compliance use.
- [Decision 250 Table 24 candidate batch 2, rows 21–40](decision_250_table24_candidate_batch2_rows021_040_2026-10-29.json): source-pinned candidate records; nested rows and CAS anomalies preserved for primary-source review.
- [Decision 250 Table 24 candidate batch 3, rows 41–60](decision_250_table24_candidate_batch3_rows041_060_2026-10-29.json): additional source-pinned candidates; nested isomer rows and apparent transcription anomalies are preserved for primary-source review.
- [Decision 250 Table 24 candidate batch 4, rows 61–80](decision_250_table24_candidate_batch4_rows061_080_2026-10-29.json): source-pinned candidates including nested chemical variants and an extraction anomaly; no exposure limit is approved.
- [Decision 250 Table 24 candidate batch 5, rows 81–99](decision_250_table24_candidate_batch5_rows081_100_2026-10-29.json): source-pinned candidates including nested entries and raw transcription anomalies; JSON parse checked, all rows remain pending official match.
- [Decision 250 Table 24 candidate batch 6, rows 100–120](decision_250_table24_candidate_batch6_rows100_120_2026-10-29.json): additional source-pinned candidates with raw values retained and suspicious source tokens flagged for review.
- [Decision 250 Table 24 candidate batch 7, rows 121–140](decision_250_table24_candidate_batch7_rows121_140_2026-10-29.json): further candidate records; formula/identifier anomalies are explicitly flagged and remain pending official-source matching.
- [Decision 250 Table 24 candidate batch 8, rows 141–160](decision_250_table24_candidate_batch8_rows141_160_2026-10-29.json): further source-pinned candidates; raw values and suspicious formula tokens are retained for page-level verification.
- [Decision 250 Table 24 candidate batch 9, rows 161–180](decision_250_table24_candidate_batch9_rows161_180_2026-10-29.json): further candidate records including the nested chromium section; all entries remain pending official match and specialist review.
- [Decision 250 Table 24 candidate batch 10, rows 181–200](decision_250_table24_candidate_batch10_rows181_200_2026-10-29.json): further source-pinned candidates; complex coal-dust/chromium-related rows and multi-substance entries are flagged for official-page review.
- [Decision 250 Table 24 candidate batch 11, rows 201–220](decision_250_table24_candidate_batch11_rows201_220_2026-10-29.json): further candidates; malformed decimal strings are preserved as anomalies rather than guessed or normalized.
- [Decision 250 Table 24 candidate batch 12, rows 221–240](decision_250_table24_candidate_batch12_rows221_240_2026-10-29.json): further candidates; apparent reversed decimal/unit strings are explicitly flagged for primary-page comparison.
- [Decision 250 Table 24 candidate batch 13, rows 241–260](decision_250_table24_candidate_batch13_rows241_260_2026-10-29.json): additional source-pinned candidates, including combined-substance entries and unresolved numeric-order anomalies.
- [Decision 250 Table 24 candidate batch 14, rows 261–280](decision_250_table24_candidate_batch14_rows261_280_2026-10-29.json): further candidate entries; isomer groups and reversed numeric tokens remain unapproved pending official comparison.
- [Decision 250 Table 24 candidate batch 15, rows 281–300](decision_250_table24_candidate_batch15_rows281_300_2026-10-29.json): additional candidates, including complex multi-CAS entries; raw anomalies remain pending page-level verification.
- [Decision 250 Table 24 candidate batch 16, rows 301–320](decision_250_table24_candidate_batch16_rows301_320_2026-10-29.json): further candidates; multi-value entries and possible column alignment issues remain unverified.
- [Decision 250 Table 24 candidate batch 17, rows 321–340](decision_250_table24_candidate_batch17_rows321_340_2026-10-29.json): further candidates including multi-substance/surface-limit records; all remain pending official-page comparison.
- [Decision 250 Table 24 candidate batch 18, rows 341–360](decision_250_table24_candidate_batch18_rows341_360_2026-10-29.json): additional candidates including dust/group rows and multi-compound entries; all remain pending official-page comparison.
- [Decision 250 Table 24 candidate batch 19, rows 361–380](decision_250_table24_candidate_batch19_rows361_380_2026-10-29.json): additional candidates; the hexane parent/child hierarchy is preserved for official-source verification.
- [Decision 250 Table 24 candidate batch 20, rows 381–403](decision_250_table24_candidate_batch20_rows381_403_2026-10-29.json): additional candidates; cyanide and iodine group hierarchies are preserved, with malformed source tokens flagged.
- [Decision 250 Table 24 candidate batch 21, rows 404–423](decision_250_table24_candidate_batch21_rows404_423_2026-10-29.json): further candidates including group-level iron and petroleum entries; unresolved unit/formula issues remain flagged.
- [Decision 250 Table 24 candidate batch 22, rows 424–443](decision_250_table24_candidate_batch22_rows424_443_2026-10-29.json): further candidates; mercury category hierarchy and group-level entries are preserved for official-source matching.
- [Decision 250 Table 24 candidate batch 23, rows 444–463](decision_250_table24_candidate_batch23_rows444_463_2026-10-29.json): further candidates, including multi-isomer entries and flagged text-layer anomalies.
- [Decision 250 Table 24 candidate batch 24, rows 464–483](decision_250_table24_candidate_batch24_rows464_483_2026-10-29.json): additional candidate entries; potential formula/limit anomalies remain flagged and unapproved.
- [Decision 250 Table 24 candidate batch 25, rows 484–503](decision_250_table24_candidate_batch25_rows484_503_2026-10-29.json): further candidate records; malformed CAS tokens, multi-limit rows, and group hierarchies are flagged.
- [Decision 250 Table 24 candidate batch 26, rows 504–523](decision_250_table24_candidate_batch26_rows504_523_2026-10-29.json): further candidates; nickel group hierarchy, malformed CAS tokens, and high-risk entries remain pending official-source review.
- [Decision 250 Table 24 candidate batch 27, rows 524–543](decision_250_table24_candidate_batch27_rows524_543_2026-10-29.json): additional candidates; the removed oil-mist entry is marked as a currentness lead, not treated as current law.
- [Decision 250 Table 24 candidate batch 28, rows 544–563](decision_250_table24_candidate_batch28_rows544_563_2026-10-29.json): ozone work-intensity subentries and further chemical candidates; all remain pending official-source comparison.
- [Decision 250 Table 24 candidate batch 29, rows 564–583](decision_250_table24_candidate_batch29_rows564_583_2026-10-29.json): additional candidates; suspicious formulas and mixed exposure-limit tokens remain explicitly unapproved.
- [Decision 250 Table 24 candidate batch 30, rows 584–603](decision_250_table24_candidate_batch30_rows584_603_2026-10-29.json): further candidates; the blank numbered slot 599 is preserved explicitly rather than silently renumbered.
- [Decision 250 Table 24 candidate batch 31, rows 604–617](decision_250_table24_candidate_batch31_rows604_617_2026-10-29.json): additional candidates through the visible source segment ending at row 617; later rows still require continued extraction.
- [In-app labour-law counsel acceptance plan](lawyer_in_app_acceptance_plan_2026-10-29.md): prepared test protocol for the lawyer's later hands-on review, with explicit abstention, citation, currentness, high-risk numeric-limit and data-isolation checks.
- [Decisions 248–252 enabling-provision crosswalk](decisions_249_252_enabling_provisions_crosswalk_2026-10-30.md): maps each decision to its parent-law delegation; includes the Article 260 vs Decision 248 reporting-trigger comparison and the unverified 24h/48h and symptom/diagnosis distinctions.
- [Decisions 248–252 clause discrepancy checklist](decisions_248_252_clause_discrepancy_checklist_2026-10-29.md): clause-level secondary-source leads, exact official-text comparisons and counsel questions.
- The counsel acceptance plan now includes exact Arabic app prompts, including OSH-16-A/B for Decision 248's off-site accident and occupational-disease reporting triggers; prompts are test inputs, not approved answers.
- [Table 24 review-queue generator](../../../tools/build_decision250_table24_review_queue.py): builds a human triage queue for anomalies, high-risk entries, currentness leads, missing CAS values and possible surface/air-unit issues without auto-correcting candidates.
- [Table 24 primary-match register generator](../../../tools/build_decision250_table24_primary_match_register.py): creates one fail-closed row-level review record for each of the 617 extracted candidates, with official-page/hash/currentness/counsel fields blank and retrieval eligibility false.
- [Table 24 primary-source match protocol](decision_250_table24_primary_source_match_protocol_2026-10-29.md): step-by-step official PDF identity, row-level matching, currentness, source-use and counsel gates; no official match is claimed yet.
- [Table 24 candidate structure validator](../../../tools/validate_decision250_table24_candidates.py): checks JSON batches, row-number continuity, nested rows, source pinpoints, and the hard pending-review status; it does not validate legal correctness.
- [Decision 250 Table 23 candidate rows](decision_250_table23_first_page_candidate_rows_2026-10-29.json): 137/137 rows now have Arabic labels; the last 74 labels and two CAS entries were added from secondary text and remain pending official-Gazette matching.

- [Source and legal-status review](source_and_legal_review.md)
- [Detailed review report](review_report_2026-10-24.md)
- [Versioned registry candidate metadata](registry_candidate.json)
- [Related implementing-instrument candidates](related_instruments_candidates.json)
- Registration helper: [`tools/register_labour_law_candidate.py`](../../../tools/register_labour_law_candidate.py)

## Commencement and repeal leads

The accessible promulgation text states general commencement from 2025-09-01, specialized labour courts from 2025-10-01, and repeal of Labour Law No. 12/2003 and Law No. 125/2010 in Article 12. Treat these as provisional version metadata until the exact Official Gazette issue is reviewed and qualified Egyptian counsel confirms the commencement, transitional rules, and current legal effect.

Later official-source leads include Prime Minister's Decree 2652/2026 and Labour Ministry Decisions 74/2026 and 75/2026. They are tracked separately as possible implementing/related instruments, not assumed to be formal amendments.

## Evidence-backed knowledge progress (2026-10-29)

The following work is a review aid only. It does not change the 311-row candidate corpus to verified/current status and does not enable authoritative retrieval.

- [Numerical evidence ledger batch 1 — NL-001 to NL-036](numerical_rule_evidence_ledger_batch1_2026-10-29.md): 36 candidate numeric assertions with searchable-PDF text-line pinpoints.
- [Numerical evidence ledger batch 2 — NL-037 to NL-060](numerical_rule_evidence_ledger_batch2_2026-10-29.md): 24 additional candidates with printed-page/article pinpoints from provisional cards.
- [Numerical evidence ledger batch 3 — NL-061 to NL-072](numerical_rule_evidence_ledger_batch3_2026-10-29.md): 12 additional candidates, including recruitment-agency capital/security thresholds and deadlines.
- [Numerical evidence ledger batch 4 — NL-073 to NL-089](numerical_rule_evidence_ledger_batch4_2026-10-29.md): 17 additional candidates on sickness leave, workplace regulations, disciplinary investigations, and procedural deadlines; these now have printed-page and browser-extracted Gazette PDF line ranges.
- [Numerical evidence ledger batch 5 — NL-090 to NL-099](numerical_rule_evidence_ledger_batch5_2026-10-29.md): 10 more candidates covering registration, sickness isolation, resignation, death-related payment, arbitration composition, and economic termination.
- [Numerical evidence ledger batch 6 — NL-100 to NL-106](numerical_rule_evidence_ledger_batch6_2026-10-29.md): 7 more candidates on disciplinary sanctions, investigation exceptions, and the effect of a committee's failure to decide.
- [Six-article Gazette locator spot-check](gazette_spot_check_2026-10-29.md): printed-page/PDF-index locators confirmed for Arts. 66, 103, 124, 134, 141 and 278. The actual six candidate JSONL rows are absent from the public branch, so the spelling outliers themselves remain **uncompared**. The official PDF text view is accessible, but no original PDF bytes were obtained for SHA-256 or visual scan review.
- [Numerical evidence ledger batch 7 — NL-107 to NL-120](numerical_rule_evidence_ledger_batch7_2026-10-29.md): 14 further candidate numeric assertions with searchable official-text/PDF line and page locators.
- Numerical checklist: **120/120 candidate slots (100% by count)**. This is candidate coverage, not source-match or legal verification. Lawyer-approved: **0/120**; complete currentness review: **0/120**; eligible for authoritative retrieval: **0/120**. This is not 100% legal verification.
- [Implementing-instrument currentness register](implementing_instrument_currentness_leads_2026-10-29.md), [structured Decision 162/2026 candidate](decision_162_2026_candidate.json), [Decision 162/2026 detailed secondary-text pinpoints](decision_162_2026_secondary_transcription_review_2026-10-29.md), [Decision 162/2026 implementing-rule evidence ledger](decision_162_2026_numerical_evidence_ledger_2026-10-29.md), [numerical evidence ledger batch 7](numerical_rule_evidence_ledger_batch7_2026-10-29.md), [311-row reconciliation execution record](311_row_reconciliation_execution_record_2026-10-29.md), [qualified Egyptian counsel review packet](egyptian_counsel_review_packet_2026-10-29.md), [19 Gazette-indexed/official-text instrument leads](related_instruments_gazette_discovery_batch_2026-10-29.json), [Decree 3165/2026 National Council for Wages review](pm_decree_3165_2026_national_wages_council_review_2026-10-29.md), [Decision 49/2026 location reconciliation](decision_49_2026_article124_location_reconciliation_2026-10-29.md), and [Decision 294/2025 paid-holiday reconciliation](decision_294_2025_paid_holidays_reconciliation_2026-10-29.md).
- [Official-text copyright and source-access review lead](official_text_copyright_and_access_review_lead_2026-10-29.md): Egyptian IP Law Article 141 appears to exclude official legal documents from copyright protection, subject to Egyptian-counsel confirmation; source-site access terms and bulk-retrieval controls remain separate issues.

**Evidence gaps remain:** the original Official Gazette PDF bytes have not been downloaded or hashed and no end-to-end visual inspection has been completed; the 311-row candidate comparison is incomplete; six reported text outliers remain unresolved; later implementing instruments and possible corrections require full-text review; source-access/reuse questions and Egyptian-lawyer review remain open. The alternative public-source inventory and the newly found full secondary Decision 250 transcription improve discovery and support provisional text comparison but do not close these release gates. Keep every candidate out of authoritative retrieval until the applicable gates pass.

## Permission and import safeguards

The IDSC repository [End User Agreement](https://dspace.id.com.eg/info/end-user-agreement) says commercial exploitation and systematic retrieval to compile a database require express written permission. No permission has been obtained. Public accessibility is not treated as a license.

The registry helper creates metadata and pending review events only. It does not import article chunks, trust incoming `verified`/`in_force` flags, or enable search. It has **not** been run against the user's local SQLite database from this session.

Before activation:
1. Obtain permission for storage, extraction, indexing, embeddings, display, redistribution, and commercial use, or verify another lawful licensed source.
2. Obtain the exact Official Gazette issue through an authorized route and compare every row against it with page-level evidence.
3. Register related instruments separately and determine their exact legal relationship and dates.
4. Obtain qualified Egyptian-lawyer review of authenticity, commencement, transitional rules, repeals, and the amendment/implementation chain.
5. Only then consider approval and search eligibility.

A JSONL hash proves the identity of the supplied data file, not the authenticity of the law or permission to reuse it.

## Source-linked provision evidence cards (2026-10-28)

See [`provision_evidence_cards.json`](provision_evidence_cards.json) for twenty-one concise Arabic research cards with article/page pinpoints, official publisher and government-hosted Gazette-PDF links, secondary cross-checks, explicit limitations, and related-instrument follow-ups.

The cards cover promulgation Articles 1, 12 and 13, and accompanying-law Articles 89–96, 117–120, 124, 125, 128–131, 164 and 165. They are **provisional research leads only**. The Gazette PDF text was inspected through web text extraction for selected pages, but the original file has not been downloaded, hashed, or visually inspected; the full 311-record article-by-article comparison is incomplete. For Decision 49/2026 (annual-leave categories), IDSC-hosted Official Gazette metadata identifies the supplement to issue 64 dated 2026-03-18 as listing the decision. For Decision 294/2025 (paid holidays), IDSC-hosted metadata identifies the supplement to issue 291 dated 2025-12-25 as listing the decision. For both, the full text/page range has not been obtained and reviewed here; neither decision is a verified operative rule in this corpus.

These cards must not be activated as authoritative retrieval, used to calculate individual entitlements, or presented as a lawyer-reviewed current-law answer. Source reuse permission, complete amendment/currentness review, and qualified Egyptian-lawyer review remain outstanding.

A human-readable, source-linked rendering is available in [`provision_evidence_cards_review.md`](provision_evidence_cards_review.md). It is generated from the JSON record by:

```bash
python tools/report_labour_law_evidence_cards.py
```

The report is a review aid only; it does not change any source-permission, legal-status, lawyer-review, or retrieval-eligibility flags. Its regression test requires the checked-in Markdown report to match the JSON cards.



- [Official Gazette supplement catalog and access status](decisions_248_252_primary_source_page_map_2026-10-30.md): exact DSpace record for Gazette Supplement 225(A), 12 October 2026, listing Decisions 248–252 and the original 6.13 MB bundle; the PDF is request-copy restricted, so no primary text has yet been reviewed.


- **Decision 250 Table 24 status (2026-10-30):** 38/38 secondary candidate batches; 781/781 numbered entries structurally present with no gaps/duplicates. The technical table index is corrected to a single Table 24 spanning secondary printed pages 249–360 (no Table 25). Regression coverage: `tests/test_decision_250_table24_inventory.py`. Official Gazette matches remain 0/781 and retrieval eligibility 0/781; the original Gazette PDF is listed in the DSpace catalog but request-copy restricted.


- [Egypt official-document Article 141 source-use route](egypt_official_documents_copyright_route_article141_2026-10-30.md): records the official-document exclusion, the creative-compilation exception, the distinction between underlying legal text and scan/third-party database rights, and the WIPO consolidation's 2020 currentness cutoff.

- [Official Gazette Article 296 penalty cross-reference](official_primary_text_article296_2026-10-30.jsonl): selected official-hosted Gazette PDF text, printed page 111 / PDF index 108; preserves the two enumerated article groups and remains pending original-byte hash, currentness and counsel review.
