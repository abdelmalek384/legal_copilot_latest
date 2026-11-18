# Collection checkpoint 190 — additional text extraction for Laws 68/1947, 142/1964 and 70/1964; Gazette scan-copy audit

**Date:** 18 November 2026  
**Agent:** Research Agent 1

## 1. New actual Arabic article text captured

Created:
- `alternate_source_text_capture_law68_142_70_additional_provisions_2026-11-18.md`

This is article text, not a list of references. It adds **41 distinct instrument/article identifiers** not present in the earlier article-text capture file:
- Law 68/1947: six new article bodies (Articles 3, 7, 8, 9, 10 and 11). Existing captures already included Articles 1, 2, 4, 5, 6 and 12–14. Result: all 14 article identifiers now have text; Article 1 is retained as historical original wording and separately marked repealed by Law 5/1964. Article 2, 5, 6, 9 and 12 have 1976 replacement versions; Article 3 has a 1955 amendment.
- Law 142/1964: 15 new article identifiers (Articles 12–21, 23, 24, 37, 38 and 39). Article 23 is only partially transcribed in the supplement and must not be counted as a complete text. Article 38 is historical only because it fell consequentially in SCC Case 42/17. Article 21 and 24 were invalidated in Case 10/35; Article 23 fell consequentially in that case.
- Law 70/1964: 20 new article identifiers/provisions (Articles 18–30, 32, 34 bis(1)–(3), 35 and 39). Article 21 is a partial transcription in this supplement; Article 20 is repealed; Article 30 is unconstitutional; Article 21(1)(9) is unconstitutional. These are consolidated texts through Law 67/2021 and must not be treated as the original 1964 wording or a 2026 fee schedule.

**Text completeness within these 41 new identifiers:** 39 complete article bodies and two partial article bodies (Law 142 Article 23 and Law 70 Article 21). The two partials are explicitly marked. The separate repeated Law 68 Article 1 historical text and Law 142 Article 30 text in the supplement are not counted again.

## 2. Four historical Gazette scan-copy PDFs — direct fallback routes

Checkpoint 94 first identified the four Manshurat download routes. They are now re-opened, and the scan images inspected in this session. All are **secondary-hosted reproductions of Gazette pages**, not authenticated original Amiri Press/GPO binary downloads.

| Instrument | Scan route | Page count | Visible Gazette identity | Current status |
|---|---|---:|---|---|
| Law 114/1946 | https://manshurat.org/file/83333/download?token=Kv0YfwAI | 6 | الوقائع المصرية issue 85, 24 Aug 1946 | scan-copy route public; secondary host |
| Law 142/1964 | https://manshurat.org/file/44021/download?token=5Zwo9ziS | 7 | الجريدة الرسمية issue 69, 24 Mar 1964 | all seven pages opened and visually inspected |
| Law 68/1947 | https://manshurat.org/file/82270/download?token=fuDVQjIu | 2 | الوقائع المصرية issue 58, 3 Jul 1947 | both pages opened and visually inspected |
| Law 70/1964 | https://manshurat.org/file/43842/download?token=z-q7csZN | 11 | الجريدة الرسمية issue 67, 22 Mar 1964 | scan copy public; secondary host |

Total: **four scan-copy PDFs, 26 pages**. This matches the master-index scan count. The files can be used as page-image comparison sources, but not described as original Amiri Press digital binaries. No SHA-256 hashes or repository-local PDF bytes have been recorded.

Additional Court of Cassation Information Centre PDFs:
- Law 68/1947 consolidated 5-page PDF through 6 September 1976: https://alhasswalawfirm.com/uploads/files/law-68-1947-1789187160259-320162837.pdf
- Law 70/1964 consolidated 34-page PDF through 13 June 2021: https://alhasswalawfirm.com/uploads/files/law-70-1964-1789185764215-156631629.pdf

These are secondary-hosted consolidated texts with Gazette masthead and amendment annotations, not the original 1947/1964 issue binaries.

## 3. Source and legal version corrections

### Law 68/1947
- The 2-page Gazette scan displays the original Law 68/1947 publication in الوقائع المصرية issue 58 dated 3 July 1947.
- The 5-page consolidated PDF shows the original Article 1 text, but LAW HUB marks Article 1 repealed by Law 5/1964. The consolidated text page's omission of that repeal marker is a source discrepancy.
- Article 14 says the statute takes effect on 1 January following publication. On the Gazette date above, the apparent commencement is 1 January 1948. Keep this as an article-derived date pending check against Law 5/1964 and any special commencement rule.

### Law 142/1964
- The 7-page scan visibly bears the Gazette issue 69, 24 March 1964 heading.
- The LAW HUB transcription duplicates issuing and substantive article numbers. The repository's normalized schema must keep the issuing provisions separate from the substantive statute.
- Case 10/35 (2 June 2018) invalidated Articles 21 and 24 and caused Article 23 to fall; Case 42/17 (6 June 1998) invalidated only the second limb of Article 37 and caused Article 38 to fall.
- Do not mark all of Article 37 invalid. The register's evidentiary-force limb remains distinct from the prescription prohibition.

### Law 70/1964
- The 11-page scan visibly bears Gazette issue 67, 22 March 1964 and includes the fee statute. It is the scan-copy lead for the original issue, whereas the 34-page Court of Cassation Information Centre PDF is consolidated through 2021.
- The 34-page PDF contains 44 article headings, schedules A/B/C and 16 amendment/judgment footnotes.
- Law 94/1980, 6/1991, 224/1996, 225/1996, 9/2003, 3/2004, 83/2006, 163/2019 and 67/2021 are the identified statutory amendments; 5424/2006 and annual vehicle valuation decisions are separate executive/ministerial decisions.
- SCC Case 2/24 invalidated Article 30; Case 10/16 invalidated Article 21(1)(9). These are judicial invalidity events, not repeal amendments.

## 4. Register and inventory changes

- Updated acquisition records EG-0144, EG-0145, EG-0150 and EG-0151 with direct scan-copy URLs, text source tiers and the distinction between secondary-hosted scan copies and official originals.
- Updated full-text inventory records FT-0004, FT-0005, FT-0006 and FT-0007 with scan-copy page counts and full-text source status.
- Updated four existing source-permission records: EG-MANSHURAT-LAW114-SCAN, EG-MANSHURAT-LAW142-SCAN, EG-MANSHURAT-LAW68-SCAN and EG-MANSHURAT-LAW70-SCAN. Permission and commercial reuse remain unknown.
- No new legal instrument rows were added. No duplicate article text IDs were added to the core 1,370 unique provisions.

## 5. Counts and progress

| Category | Current count / status |
|---|---:|
| Canonical acquisition records | 250 |
| Base laws | 66 |
| Amending laws | 48 |
| Executive regulations | 13 |
| Executive-regulation amendments | 35 |
| Judicial decisions | 21 |
| Other decisions/circulars/advisory authorities | 54 |
| Other/unclassified | 13 |
| Priority full-text inventory | 27 unique instruments |
| Core unique non-repealed article provisions | 1,370 |
| Additional article headings in four older property statutes | 200 |
| Additional text-bearing entries from checkpoints 185–186 | 56 (55 non-repealed text-bearing entries + one repealed Article 1 marker) |
| New distinct article IDs in this checkpoint | 41 (39 complete + 2 partial) |
| Gazette scan-copy reproductions | 4 PDFs / 26 pages |
| Authenticated original Amiri Press/GPO binaries acquired for the four older statutes | 0 |
| Lawyer verification | 0 |
| Commercial reuse permissions established | 0 |

The 41 additional article identifiers are not added to the core 1,370 count; they belong to the separate older property-statute supplement. Historical, repealed and unconstitutional provisions remain in the corpus as versioned historical texts, not current-operative articles.

## 6. Remaining blockers

1. Obtain original Amiri Press/GPO digital binaries for all four older statutes; current Manshurat routes are secondary-hosted scan copies.
2. Archive downloaded PDF bytes and compute SHA-256 only after lawful access and successful local download.
3. Visually compare OCR/transcription against all scan pages, particularly Law 70's tables A/B/C and Law 142 Articles 21–24 and 37–38.
4. Resolve Law 68 Article 1's repeal discrepancy against Law 5/1964 and the 1947 Gazette scan.
5. Finish Law 142 Article 23 complete text and Law 70 Article 21 complete text; preserve the partial flags until complete.
6. Complete article-by-article version redlines for Laws 114, 142, 68 and 70, including inserted bis provisions, repeals, constitutional invalidity and executive regulations.
7. Obtain original SCC Case 42/17 and Case 10/35 judgments and original Gazette judgment pages. Case 101/26 now has its full judgment directly on the official SCC site.
8. No lawyer verification or commercial reuse permission is claimed.
