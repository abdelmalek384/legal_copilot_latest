# Collection checkpoint 164 — alternate Arabic text recovery for core property/notarial statutes and Building Regulation 144/2009
**Date:** 18 November 2026  
**Repository:** abdelmalek384/legal_copilot_latest

## What changed

This checkpoint records a substantive move from metadata-only acquisition leads to alternate searchable Arabic legal text. Original Gazette binaries remain separate from these text sources.

### New source acquisitions and text capture

1. **Law 68/1947 — Notarial Law**
   - Alternate source: LAW HUB searchable Arabic transcription, with amendment annotations.
   - Captured all 14 article headings and the substantive text of Articles 2–14; Article 1 marked repealed by Law 5/1964.
   - Amendment markers include Law 629/1955 (Article 3) and Law 103/1976 (Articles 2, 5, 6, 9, 12).
   - This is the first near-complete text capture of this law in the working corpus, but still requires Gazette image validation.

2. **Law 142/1964 — Real Estate Registry System Law**
   - Alternate source: LAW HUB full searchable page; cross-source leads at Al-Hasswa and Manshurat.
   - Page exposes 6 issuing provisions plus 66 substantive article sequence. Transcribed selected substantive text: Articles 1, 2, 4, 8, 11, 13, 26–28, 45–49, 55–59.
   - Important version note preserved: SCC Case 10/35 invalidated Articles 21 and 24, with consequential lapse of Article 23 and Decision 553/1976; Case 42/17 invalidated Article 37(2), with Article 38 consequentially falling. Do not mark all of Article 37 invalid.
   - Full extraction remains incomplete; LAW HUB page flattens/repeats some article numbering, so map each provision against the Gazette PDF before treating numbering as authoritative.

3. **Law 114/1946 — Real Estate Publicity Law**
   - Alternate source: Court of Cassation Information Centre PDF reproduction, hosted by a secondary domain and labelled amended through 6 March 2022.
   - Captured substantive text excerpts for Articles 5–13, 20–22, 30–35, 41–49, including registration effects, registrable leases, electronic applications, priority, mortgage particulars, renewal and inheritance registration.
   - OCR overlap/duplicate wording in Article 9 is explicitly flagged; original Gazette page image comparison and footnote resolution remain outstanding.

4. **Law 70/1964 — Notarization and Registration Fees Law**
   - Alternate source: Al-Hasswa legal library transcription said to reproduce the Court of Cassation portal; 44 articles and annex references; stated amendment state through 13 June 2021.
   - Captured text/structured text for Articles 1–19 and 24–34, including fixed fees, preservation fees, proportional fees, judicial deposit, collection, refunds, exemptions and reductions.
   - Article 2 list numbering anomalies are flagged rather than silently corrected. Schedules A/B/C remain to be captured and checked against Gazette images. Article 30 is marked unconstitutional in the source; judgment must be attached to the version graph.

5. **Decision 144/2009 — Executive Regulation of Building Law 119/2008**
   - Alternate source: LAW HUB full searchable Arabic regulation page; official Ministry of Housing/Manshurat Gazette source links identified as cross-check targets.
   - Captured all 4 issuing provisions, preliminary definitions, and selected substantive text from Articles 36–38, 59–63 and 144.
   - Page contains historical/current text and amendment annotations; it is not yet a date-effective consolidated redline. Annexes/forms and all amendments remain to be extracted.

## Repository updates

- Added docs/legal_evidence/alternate_source_arabic_text_capture_laws_114_142_68_70_and_building_reg_144_2009_2026-11-18.md.
- Added five records FT-0026 through FT-0030 to data/research/egypt_full_text_inventory_priority_2026-11-18.csv.
- Priority full-text inventory is now **30 records** (previously 25).
- Acquisition register remains **241 unique instrument records**; source-permission register remains **64 unique source records**; historical version-event register remains **44 events**. This checkpoint did not add instrument records or amendment events.
- Core article extraction remains **1,370 completed provisions** (Civil Code 1,093; Evidence Law 163; Building Law 114). These alternate-source excerpts are not added to the 1,370 count because the additional statutes have not yet been fully normalized and versioned.
- The existing Law 143/1981 article extraction remains separate; this checkpoint does not change its 28 article texts and one repealed marker.

## Updated progress estimate

| Workstream | Estimate |
|---|---:|
| Defined core article sets (Civil Code, Evidence, Building Law) | **100% text extraction**; historical/current version verification remains separate |
| Law 143/1981 | **28 articles transcribed + one repealed marker** |
| Law 68/1947 | **Near-complete base text captured (Articles 2–14; Article 1 repealed)** |
| Laws 114/1946, 142/1964, 70/1964 | **Selected article text captured; complete extraction still in progress** |
| Decision 144/2009 | **Searchable full-text source acquired; selected article text captured; full normalized extraction/redline pending** |
| Priority full-text inventory | **30 records** |
| Broader civil/property/contract corpus | **16% provisional** (up from 15%; scope estimate, not a document count) |
| Whole Egyptian legal corpus | **2% provisional** |
| Lawyer verification | **0%** |
| Commercial reuse permission confirmed | **0%** |

## Remaining blockers and alternate route

- **Original Gazette scans unavailable/request-only:** continue using official government-hosted copies where present, Court of Cassation reproductions, LAW HUB, EastLaws, Manshurat, and Ministry of Housing repositories as secondary text acquisition paths, while preserving source-tier labels.
- **Image/OCR problems:** use searchable HTML/PDF transcriptions as fallback; retain page-image comparison flags for punctuation, tables, schedules, and disputed article numbering.
- **Decision 480/2026 deadline:** remains unresolved. The original Gazette bundle, commencement clause and any post-decision administrative circular are still required; no final deadline is certified.
- **No rights inference:** public accessibility does not establish permission for commercial reuse.

## Next collection sequence

1. Finish all remaining Law 142 articles and map exact issuing/substantive article numbering to the Gazette.
2. Complete Law 114 remaining articles and resolve Article 9 OCR plus every amendment footnote.
3. Complete Law 70 Articles 20–44 and transcribe Schedules A/B/C; attach SCC Case 2/24.
4. Extract all 185 base articles of Decision 144/2009 from the searchable page, preserving old/new text blocks and decision annotations.
5. Convert each amendment instrument into article-level before/after events; then recalculate the percentage from normalized text counts rather than source-page availability.
