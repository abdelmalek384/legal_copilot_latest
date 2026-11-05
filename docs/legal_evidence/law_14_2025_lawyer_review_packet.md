# Law 14/2025 — Egyptian lawyer review packet

**Instrument:** Law No. 14 of 2025 issuing the Labour Law.  
**Publication:** Official Gazette issue 18 (تابع; described in this project as 18 bis), 3 May 2025.  
**Purpose:** qualified Egyptian counsel's article-by-article review. This packet is not legal verification.

## Source and comparison identity

- Candidate transcription: 311 JSONL rows; SHA-256 3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600.
- Gazette reference PDF: 112 pages; recorded SHA-256 b0a47cefe18722d3f23e004ac7e78e6e309010e13124413e7e7018820c9581be.
- Candidate structure: 13 promulgation provisions + 298 provisions in the attached Labour Law.
- Machine comparison: 38 identical after normalization; 221 minor differences; 47 major differences; 5 numeric alerts; 0 missing/extra headings.
- The 273 non-identical machine records and 120 quantitative cue records overlap: 282 unique provisions have prior page-image review records, while 29 provisions have no targeted page-image review recorded. Those checks are evidence aids, not counsel sign-off.

## Official corroborating sources and pagination caution

- Egyptian Tax Authority hosted PDF: https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf — accessed 2026-11-05; indexed as Official Gazette issue 18 (supplement), 3 May 2025; 110 pages. The repository comparison PDF is 112 pages. Byte identity between the two PDFs is unknown, so do not transfer page locators between them without checking.
- Official Printing Authority law text record: https://alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D — corroborates the instrument's identity; it is not the 112-page comparison PDF.
- Ministry of Labour legislation listing: https://www.labour.gov.eg/ar/القوانين-والتشريعات/ — lists Law 14/2025 as a basic law; it does not prove the Gazette PDF's byte identity or currentness.

The page numbers in the tick-sheet refer to the recorded 112-page comparison PDF identified by its SHA-256 above. The original 112-page PDF and 311-row JSONL are not committed in the repository; the reviewer must obtain those exact hash-matching files before signing off. If the reviewer uses the 110-page ETA copy, page locators must be independently remapped.

## Supporting article-by-article comparison records

Use these committed artifacts together with the 311-row lawyer tick-sheet:

- `docs/legal_evidence/README_law_14_2025.md` — complete artifact index and trust boundary.
- `docs/legal_evidence/law_14_2025_comparison_report.md` — comparison method, 311-row structure, 38 identical / 221 minor / 47 major / 5 numeric-alert machine results, and prior visual-check summaries.
- `docs/legal_evidence/law_14_2025_differing_articles_part1.csv`, `part2.csv`, `part3.csv` — all 273 machine-difference records with article, occurrence, machine status, similarity, Gazette PDF page range and review note.
- `docs/legal_evidence/law_14_2025_quantity_tick_sheet_part1.csv` and `part2.csv` — 120 quantitative text cues, page locators and prior visual-check notes.
- `docs/legal_evidence/law_14_2025_numeric_alert_review.csv`, `law_14_2025_major_difference_visual_spot_checks.csv`, `law_14_2025_major_difference_visual_spot_checks_part2.csv`, and the minor-difference spot-check batches — prior page-image checks, not lawyer sign-off.
- `docs/legal_evidence/law_14_2025_discrepancy_article_index.md` and `law_14_2025_quantitative_review_checklist.md` — review navigation aids.

The 273 difference records, 120 quantitative cues and prior page-image checks overlap; they are not additive counts. The tick-sheet contains one row per candidate provision (13 promulgation provisions + 298 attached-law articles). The original candidate JSONL and exact 112-page Gazette PDF are not committed, so the reviewer must obtain those exact hash-matching inputs and compare the full text, not rely only on the machine similarity or prior spot-check note.

## How to use the tick-sheet

Open law_14_2025_lawyer_review_tick_sheet.csv. It has one row for each of the 311 candidate provisions, including the separate numbering blocks for promulgation provisions and the attached law.

For every row, counsel should:
1. Open the exact candidate row in the original law_rows_ar.jsonl and the corresponding printed Gazette page(s).
2. Compare the complete Arabic wording, not just the excerpt or machine similarity: article heading, words, punctuation where material, amounts, dates, periods, percentages, conditions, exceptions, cross-references, provisos, tables and annexes.
3. Tick exactly one of lawyer_tick_match, lawyer_tick_mismatch, or lawyer_tick_unresolved, then mirror that choice in lawyer_decision as match, mismatch, or unresolved.
4. For a mismatch, record the Gazette wording, proposed correction, printed page and the reason. Do not overwrite the source candidate during review.
5. Complete reviewer name, role, review date and a durable signature/review-record reference.

The CSV deliberately leaves every lawyer decision and reviewer field blank. Its verified column is 0 on all 311 rows. Do not change it as part of the review worksheet. A separate authorized approval workflow must record the lawyer's signed decision before any source record can change status.

## Priority checks

- Resolve any mismatch or ambiguity counsel finds in the 311 rows, including all 120 quantitative cues.
- Recheck Article 13 commencement separately from publication: the candidate record notes 1 September 2025 general commencement and 1 October 2025 specialized labour-court commencement; counsel must confirm the text and interpretation.
- Check amendments, repeal/partial repeal, corrigenda and later implementing instruments as of the intended advice date.
- Review collection, storage, display, indexing and commercial-reuse rights. A public URL or manual copy does not establish permission.
- Confirm the exact provenance of the supplied PDF and candidate JSONL. Their recorded hashes identify files but do not prove who published or supplied them.

## Currentness leads requiring counsel review

The targeted official-source snapshot recorded in the comparison manifest (search through 2026-11-05) identified related implementing instruments, not confirmed amendments to Law 14/2025:

- Prime Minister Decision 982/2026 applied remote work on Sundays during April 2026 for specified sectors/administrative functions. The manifest records extensions 1305/2026, 1572/2026, 2033/2026, 2377/2026 and 2590/2026 through September 2026; no October/November extension surfaced in that limited search.
- The Ministry of Labour announced Ministerial Decision 49/2026 concerning seven additional annual-leave days for specified hazardous/difficult work or remote areas, and general workplace-regulation rules for establishments with 10 or more workers. The full signed texts were not captured in the manifest.
- These are leads for currentness and implementation review, not verified amendments and not a complete search.

Counsel should obtain the signed instruments, check publication/effective dates and scope, determine whether they amend, implement or merely supplement the Labour Law, and identify any later decisions or corrigenda before giving current-law advice.

## Sign-off

- Reviewing lawyer: ______________________________
- Egyptian bar / qualification reference (record privately): ______________________________
- Review scope and date: ______________________________
- Outstanding exceptions: ______________________________
- Signed review-record reference: ______________________________

**Current status:** source_matched_not_lawyer_reviewed; lawyer_reviewed=false; authoritative=false; retrieval_eligible=false. All 311 candidate rows remain verified=0.
