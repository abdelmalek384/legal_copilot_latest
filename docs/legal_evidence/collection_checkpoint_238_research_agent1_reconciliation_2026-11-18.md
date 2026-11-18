# Research Agent 1 — continuation checkpoint 238 (18 November 2026)

## Scope and audit method

Reopened the live `main` branch, the master index, checkpoints 85–99, the latest Research Agent 1 checkpoint 237, the deadline-computation note, the property/registration/judicial supplements, the canonical acquisition CSV, the instrument-classification ledger, the priority full-text inventory and the source-permission JSON. The 172-record figure in the task is a stale snapshot; the live canonical CSV is now 273 records. No historical 172-row snapshot was substituted.

## Live register and count reconciliation

Counts read directly from the live repository files:

| Measure | Current count | Counting rule / qualification |
|---|---:|---|
| Canonical acquisition records | 273 | 273 rows, 273 unique instrument IDs in `egypt_initial_statute_acquisition_register_2026-11-17.csv` |
| Base laws | 71 | Provisional title/domain classification |
| Amending laws | 54 | Provisional title/domain classification |
| Executive regulations | 18 | Separate from amendments to regulations |
| Executive-regulation amendments | 38 | Provisional title/domain classification |
| Judicial decisions | 21 | Separate from pending dockets |
| Other decisions/circulars/advisory records | 58 | Includes heterogeneous subordinate/administrative material |
| Other/unclassified | 13 | Requires manual ontology normalization |
| Source-permission records | 102 | 102 unique source IDs; assessments only, not permissions |
| Priority full-text inventory | 56 | 50/56 have a searchable/full-text source; source presence is not full extraction/authentication |
| Core unique operative article provisions | 1,370 | Civil Code 1,093 + Evidence Law 163 + Building Law 114 |
| Civil Code article/status coverage | 1,149/1,149 | 1,093 non-repealed bodies + 56 repealed historical article bodies/status entries; historical bodies are not current law |
| Additional property-statute headings | 200 | Laws 114/1946, 142/1964, 68/1947 and 70/1964; not yet normalized as unique operative provisions |
| Historical article-version events | 127 | Master-index figure; article-level pre/post text normalization remains incomplete |
| Lawyer verification | 0 | No lawyer sign-off recorded |
| Commercial reuse permissions established | 0 | Public access is not permission |

**Reconciliation note:** checkpoint 237 and checkpoint 203 report earlier snapshots of 250 acquisition records and 97/86 permission sources. The live acquisition CSV and source-permission JSON now contain 273 and 102 respectively. The current type ledger also contains 273 rows. The master index's 273/102 figures are consistent with those live files; older checkpoint counts are retained as historical snapshots and must not be repeated as current.

## Priority 1 — Original Gazette PDFs for Laws 114/1946, 142/1964, 68/1947 and 70/1964

No original Amiri Press digital binary was obtained. The following 26 pages are visually inspected secondary-hosted reproductions only:

- Law 114/1946 — Egyptian Proceedings issue 85, 24 August 1946; 6-page scan: https://manshurat.org/file/83333/download?token=Kv0YfwAI
- Law 142/1964 — Official Gazette issue 69, 24 March 1964; 7-page scan: https://manshurat.org/file/44021/download?token=5Zwo9ziS
- Law 68/1947 — Egyptian Proceedings issue 58, 3 July 1947; 2-page scan: https://manshurat.org/file/82270/download?token=fuDVQjIu
- Law 70/1964 — Official Gazette issue 67, 22 March 1964; 11-page scan: https://manshurat.org/file/43842/download?token=z-q7csZN

No original publisher binary, certified archive copy or SHA-256 is recorded. Keep these as scan reproductions, not originals. Next acquisition route: formal Amiri Press archive-copy/certified-copy request identifying issue/date and instrument; do not bypass request-only access.

## Priority 2 — Law 168/2025, PM Decision 200/2026, Presidential Decision 480/2026

- Law 168/2025: Gazette issue 32 bis (و), 13 August 2025. Official DSpace metadata identifies Amiri Press and an approximately 294.4 KB original bundle, but download is request-copy restricted. SIS direct PDF previously returned 502. Secondary 20-page reproduction and searchable text exist; no original bytes/hash.
- PM Decision 200/2026: Gazette issue 3 bis (أ), 18 January 2026. Official Amiri Press text portal: https://www.alamiria.com/Sec/TashTxt?id=cEpwOo6BfmY%3D . Article 4 expressly provides commencement the day after publication: **19 January 2026**. Official SIS-hosted full-issue PDF was opened and text-extracted, but bytes/hash were not archived. Text capture: 24/24 issuing/regulation provisions plus Forms 1 (two variants), 2 and 3. Article 20 text-layer annual/quarterly discrepancy remains pending page-image inspection.
- Presidential Decision 480/2026: official DSpace record https://dspace.id.com.eg/items/03b3721d-4847-4be0-8130-5d4bf38da540/full identifies Gazette issue 45 bis (ج), 10 November 2026, Amiri Press, 178.37 KB original bundle. Download remains request-copy restricted. Two operative articles are transcribed from secondary reproductions; no original bytes/hash.

## Priority 3 — Decision 480/2026 commencement and final application deadline

**No single final calendar date is established by the operative text.** Decision 480 Article 1 says the Article 3(1) period under Law 168/2025 is extended for “another equivalent period”; Article 2 orders publication. The reproduced text contains no express commencement date, calendar expiry date or express rule for the apparent gap between the initial deadline and the decision's 10 November 2026 publication.

Relevant competing inputs:
1. PM Decision 200/2026 commenced on 19 January 2026.
2. Law 168/2025 Article 3(1) provides a six-month period from commencement of the Executive Regulation.
3. Cairo Governorate/local-government notices treated 18 July 2026 as the last filing date (example official notice: https://www.cairo.gov.eg/ar/governorate-entities/neighborhoods/north-area/hay-alamiriya/news/2026/june/09c8646b18c94561a1985b0a83aa38ef).
4. A procedural-month calculation applying Civil and Commercial Procedure Law Article 15 (exclude the triggering day) produces **19 July 2026** from a 19 January trigger. This conflicts by one day with the official local-government notice. The exact legal effect of the relevant administrative filing rule needs official clarification.
5. If an extension is treated as a consecutive six-month continuation, candidate dates are **18 January 2027** (if the initial expiry was 18 July) or **19 January 2027** (if it was 19 July).
6. If the additional period is treated as a fresh period triggered by Decision 480's publication/effectiveness on 10 November 2026, candidate dates are **10 or 11 May 2027**, depending on whether the publication day is excluded under the applicable commencement/time-computation rule.

The decision was issued/published after the locally announced initial filing date, so the treatment of the intervening period is material. Do not represent any of the four candidate endpoints as verified. Obtain a written official circular/interpretation from the competent state-land regularization authority, Cabinet/Presidency or State Council; obtain the original Gazette pages to confirm whether the request-only PDF contains any additional operative detail. Distinguish Article 3 application deadline from Article 11's separate legal consequences.

## Priority 4 — Constitutional Court judgments

- **Case 10/35 (2 June 2018):** 10-page secondary Gazette scan reproduction (issue 22 bis (ط), 6 June 2018) visually inspected. Official later SCC judgment corroborates invalidity of Law 142/1964 Articles 21 and 24, consequential fall of Article 23 and Justice Minister Decision 553/1976. Official later SCC explanation: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/12158_41_14_3_2.html . Direct original signed judgment/Gazette original remains outstanding.
- **Case 42/17 (6 June 1998):** full searchable secondary transcription; later SCC page corroborates its holding. It invalidated Law 142/1964 Article 37(2) (prohibition on acquisitive prescription contrary to register) and Article 38 fell consequentially. Article 37(1)'s evidentiary limb is not invalidated. Gazette metadata: issue 35 تابع, 18 June 1998. Direct official original judgment/Gazette scan remains outstanding. Secondary text: https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/15553 ; official later reference: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/14996_32_39_1_2.html .
- **Case 101/26 (1 February 2009):** full judgment available on official SCC page https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3204_26_101_1_2.html ; Gazette issue 7 bis (أ), 15 February 2009. Article 22(1) of Law 143/1981 invalidated; jurisdictional effect is divided between ordinary courts for civil possession/ownership and administrative courts for administrative disputes. Original Gazette page-image authentication remains outstanding.
- **Rent cases:** repository records full secondary texts for Cases 4/23, 14/23, 47/21 and 116/27 and later official SCC corroboration for Cases 144/20 and 6/20; Case 11/23 has secondary Gazette reproduction (issue 19 bis (ب), 13 May 2018). Original signed SCC judgment files and exact original Gazette scans remain outstanding for identified cases. Seven pending dockets are separately maintained; they are not final judgments. Docket register: `data/research/egypt_constitutional_rent_case_docket_register_2026-11-18.csv`.

## Priority 5 — amendment chains

- **Law 143/1981:** 29 substantive articles have a consolidated Arabic text. Six statutory amendment events and seven executive-regulation decisions are mapped. Article 21 is repealed (Law 12/1984); Article 22(1) is unconstitutional (Case 101/26). Full original amendment Gazette scans and historical redlines remain outstanding. Key identified statutory events include Laws 12/1984, 55/1988, 205/1991, 96/1995, 72/1996 and 11/2024.
- **Law 114/1946:** 12 statutory/transitional amendment events identified; searchable body/status coverage 66/70 IDs. Four absent historical bodies are repealed Articles 3, 24, 26 and 29. Law 9/2022 is a major amendment. Full historical text versions, original amendment Gazette scans and reconciliation of the current consolidation remain incomplete.
- **Law 142/1964:** 72/72 provision IDs represented in the master index (including issuing provisions); Law 83/2006 expressly replaced Article 30; 1964 corrigendum affects Articles 62 and 65. Case 10/35 and Case 42/17 invalidities must be recorded provision-by-provision. Original amendment Gazette scans and full historical redlines remain outstanding.
- Related Laws 68/1947 and 70/1964: Law 68 amendment events include Laws 629/1955, 5/1964 and 103/1976; Decision 1532/1976 is a regulation amendment, not a statutory amendment. Law 70/1964 has at least seven identified amending laws (629/1955, 5/1964, 103/1976, 94/1980, 6/1991, 83/2006 and 67/2021); standalone amendment texts and historical redlines remain incomplete.

## Priority 6 — Civil Code Law 131/1948 Articles 1–1149

Current representation is 1,149/1,149 numbered article text/status entries: 1,093 non-repealed bodies plus 56 repealed historical article entries. The 1,093 operative provisions are already included in the 1,370 core unique-provision count; do not duplicate. Historical text for repealed Articles 54–80 and 389–417 is incomplete, and full amendment-by-amendment historical version normalization is not complete. Checkpoints 94–99 extend selected ranges (including 216–264 and 602–800) but do not imply the entire amendment chain is closed.

## Priority 7 — Evidence Law 25/1968 Articles 1–117

Articles 1–117 are fully transcribed in checkpoints 112–113. Overall representation is 163 provision units (Articles 1–162 plus inserted Article 148 bis). The Ministry of Finance Gazette reproduction is 11/12 pages visually inspected; printed page 315 remains a rendering blocker. Secondary LAW HUB/Notaries Union text bridges that page; WIPO Lex OCR is materially defective. Amendments and historical versions remain to be normalized. No new article bodies are counted in this checkpoint.

## Priority 8 — Building Law 119/2008 and Decision 144/2009

- Law 119/2008: all 114 substantive base articles are transcribed (114/114) from the government-hosted MHUC Gazette reproduction; eight secondary 2020 consolidated snapshots are alternate-source evidence, not additional provisions. Original Amiri Press binary/hash, page-image comparison and full amendment/currentness graph remain outstanding.
- Decision 144/2009: 184/185 extant base article bodies captured; Article 127 is repealed. Nine inserted bis provisions are tracked separately with varying text completeness. Forms/schedules, page-image verification and complete amendment/currentness redline remain outstanding.

## Provenance, versioning, rights and next acquisition actions

Every item must preserve: canonical instrument ID; issuing authority; instrument date; Gazette type/issue/supplement/date/page; source URL and host; source tier; retrieval/access date; binary SHA-256 when lawfully acquired; text extraction method; page-image inspection state; article/version identifiers; amendment/repeal/constitutional invalidity effect; permission status; lawyer-review status.

Immediate next actions:
1. Request the four historic Gazette issue binaries/certified copies from Amiri Press and archive/hash only after lawful delivery.
2. Request the original DSpace bundles for Law 168/2025 and Decision 480/2026; archive Decision 200/2026 SIS PDF bytes/hash and visually inspect Article 20/Form 3.
3. Obtain a written official interpretation of Decision 480 commencement, initial expiry (18 vs 19 July), treatment of the gap and final date.
4. Request direct SCC originals and Gazette pages for Cases 10/35 and 42/17; continue originals for rent cases.
5. Collect amendment Gazette copies and build version-by-version Arabic diffs for Laws 143/1981, 114/1946 and 142/1964 (and related 68/1947 and 70/1964).
6. Continue Civil Code historical/repealed-body extraction and Evidence Law page315 recovery.
7. Complete Decision 144/2009 inserted provisions, annexes/forms and amendment graph; visually verify Law119/2008 Gazette PDF.
8. Keep the canonical acquisition CSV at 273 rows and permission register at 102 unique sources unless an actual new instrument/source is acquired; do not add duplicate legal instruments or duplicate provision texts.

**Status:** no new legal instrument, final judgment, full-text inventory record or unique article provision is added in this checkpoint. This is a reconciliation and handoff checkpoint. Lawyer verification remains 0; commercial reuse permission established remains 0; publisher-authenticated original Gazette binaries for the four historical laws remain 0.
