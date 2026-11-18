# Research Agent 1 — checkpoint 170: source acquisition, deadline, judicial and register reconciliation
**Date:** 18 November 2026

## 1. Scope and method

Rechecked the master index, checkpoints 85–93 and supplemental sections, later amendment-chain checkpoints 149–169, the acquisition register, source-permission register, priority full-text inventory and historical article-version event register. Rechecked official publisher, DSpace, government-hosted source locators for the priority Gazette instruments and Constitutional Court judgments.

No restricted DSpace request-copy process was bypassed. No PDF is represented as locally acquired unless its bytes were actually obtained. No legal instrument or article text was added in this checkpoint; work is source reconciliation, register deduplication, type classification and blocker clarification.

## 2. Register deduplication and normalized category counts

### Acquisition register

The pre-cleanup CSV contained 242 rows and 242 unique IDs, but title/number cross-checking exposed 11 duplicate legal-instrument records. These were duplicate source/acquisition entries for the same legal act, not 11 additional instruments. The duplicates were consolidated into canonical rows, preserving source URLs and observations in the canonical record.

- Canonical register: data/research/egypt_initial_statute_acquisition_register_2026-11-17.csv
- Alias map: data/research/egypt_acquisition_register_aliases_2026-11-18.csv
- Provisional type ledger: data/research/egypt_instrument_type_classification_2026-11-18.csv

The 11 merged pairs:
- EG-0063 → EG-0004 (Companies Law 159/1981)
- EG-0050 → EG-0012 (Customs Law 207/2020)
- EG-0027 → EG-0013 (Social Insurance Law 148/2019)
- EG-0028 → EG-0021 (Penal Code 58/1937)
- EG-0068 → EG-0023 (Investment Law 72/2017)
- EG-0026 → EG-0025 (Consumer Protection Law 181/2018)
- EG-0066 → EG-0059 (Bankruptcy/Insolvency Law 11/2018)
- EG-0209 → EG-0168 (Law 629/1955 amending Law 68/1947)
- EG-0210 → EG-0169 (Law 103/1976 amending Law 68/1947)
- EG-0214 → EG-0171 (Decision 1532/1976 amending Law 68/1947 Executive Regulation)
- EG-0236 → EG-0153 (Law 12/1984; the same act is the Irrigation and Drainage Law and also repeals Article 21 of Law 143/1981)

The historical article-version event register and priority full-text inventory now point to canonical IDs where affected. Earlier checkpoints retain their historical acquisition IDs; use the alias map when resolving those references. Numeric gaps EG-0076–EG-0079 remain unresolved and were not filled.

### Separate current counts

| Measure | Count | Qualification |
|---|---:|---|
| Canonical acquisition records | **246** | Unique legal instruments after 11 duplicate-row consolidations |
| Source-permission records | **64** | Unique source assessments; not permissions granted |
| Base-law records | **66** | Provisional title/domain classification |
| Amending-law records | **48** | Provisional title/domain classification; includes transitional/deferral effects where identified |
| Executive regulations | **13** | Original regulation instruments |
| Executive-regulation amendment records | **35** | Subordinate instruments changing regulation text |
| Judicial decisions | **19** | SCC judgment records currently represented in the acquisition register |
| Other decisions/circulars | **52** | Ministerial, Cabinet, presidential and other subordinate decisions |
| Other/unclassified instrument records | **13** | Requires manual type normalization |
| Priority full-text inventory records | **33** | Mixed completeness; not all authenticated or complete |
| Historical article-version events | **44** | Events, not instruments or article texts |
| Core unique article provisions | **1,370** | Civil Code 1,093 + Evidence Law 163 + Building Law 114 |
| Additional searchable article headings | **200** | Laws 114/142/68/70; not fully extracted/versioned |

The type counts are provisional classifications from title/domain labels, stored row-by-row in the type ledger. They are not a lawyer-certified taxonomy. The acquisition count is not the sum of article provisions or full-text files.

### Source-permission audit

The JSON register contains 64 unique source IDs, no duplicates. Permission-state distribution:
- 58: collection unknown / commercial reuse unknown;
- 5: collection not allowed without explicit exception or licence / commercial reuse requires prior written permission;
- 1: collection unknown / commercial reuse not allowed without explicit exception or licence.

No permission state was upgraded. All 246 canonical acquisition records retain lawyer_reviewed=false and rights_cleared=false.

## 3. Original Gazette PDF acquisition status

### Laws 114/1946, 142/1964, 68/1947 and 70/1964

The previously inspected 26 printed Gazette pages remain secondary-hosted scan reproductions, not Amiri Press original digital binaries:
- Law 114/1946: Egyptian Proceedings issue 85, 24 August 1946, 6 pages.
- Law 142/1964: Official Gazette issue 69, 24 March 1964, 7 pages.
- Law 68/1947: Egyptian Proceedings issue 58, 3 July 1947, 2 pages.
- Law 70/1964: Official Gazette issue 67, 22 March 1964, 11 pages.

Manshurat catalogue records and direct scan-PDF routes:
- Law 114/1946: catalogue https://manshurat.org/node/69796 ; PDF https://manshurat.org/file/81500/download?token=G8bK0_YZ (6 pages).
- Law 142/1964: catalogue https://manshurat.org/node/33844 ; PDF https://manshurat.org/file/44021/download?token=5Zwo9ziS (7 pages).
- Law 68/1947: catalogue https://manshurat.org/node/70547 ; PDF https://manshurat.org/file/82270/download?token=fuDVQjIu (2 pages).
- Law 70/1964: catalogue https://manshurat.org/node/33668 ; PDF https://manshurat.org/file/43842/download?token=z-q7csZN (11 pages).

All four PDF objects were opened in the research session; their page counts and first-page masthead, issue/date and instrument headings were visually checked. The first-page images show the relevant printed Gazette issue and instrument. These are secondary-hosted scans of printed Gazette pages, not authenticated Amiri Press digital binaries. Law 114 also has a government-hosted Ministry of Justice PDF, but it is a base-law reproduction, not an authenticated Amiri Press Gazette binary. Original Amiri Press files for all four statutes remain not obtained. No certified publisher hash/authentication or commercial reuse right is claimed.

### Law 168/2025, PM Decision 200/2026, Presidential Decision 480/2026

- **Law 168/2025:** Official DSpace identifies Official Gazette issue 32 bis (و), 13 August 2025, Amiri Press publisher, original bundle 294.4 KB. Download opens a request-a-copy form. No original bytes/hash obtained. Official catalogue: https://dspace.id.com.eg/items/8255632b-a2d4-44c3-9888-d4e2801e8d32/full . Court of Cassation-hosted reproduction and secondary Gazette scan/text are alternatives, not the original Amiri Press binary.
- **PM Decision 200/2026:** Official Gazette issue 3 bis (A), 18 January 2026. SIS identifies a public full-issue PDF, 1.893 MB, containing Decision 200/2026: https://mediadr.sis.gov.eg/xmlui/handle/123456789/118973 . Amiri Press searchable text: https://www.alamiria.com/Sec/TashTxt?id=cEpwOo6BfmY%3D . The separate DSpace original bundle (1.89 MB) opens a request-a-copy form: https://dspace.id.com.eg/items/c8ee628f-2d7b-4f33-ab68-a68db8c99eb1/full . The SIS PDF is an official government-hosted Gazette issue reproduction; no local binary/hash was archived in this pass.
- **Presidential Decision 480/2026:** Official Gazette issue 45 bis (ج), 10 November 2026; DSpace metadata names the President and Amiri Press and lists a 178.37 KB original bundle. Download opens a request-a-copy form: https://dspace.id.com.eg/items/03b3721d-4847-4be0-8130-5d4bf38da540/full . Original PDF bytes not obtained.

No restricted DSpace download was bypassed. The public SIS issue page for Decision 200 is the only one of these three with an identified public PDF route; the DSpace original bundle remains restricted.

## 4. Decision 480/2026 — commencement and application deadline

### Commencement of the Executive Regulation

PM Decision 200/2026 was published in Official Gazette issue 3 bis (A) on 18 January 2026. Issuing Article 4 says it takes effect on the day after publication. Therefore the Executive Regulation commenced on **19 January 2026**. This is the trigger stated in Law 168/2025 Article 3 for the initial six-month application period.

### Initial period

- Applying Civil and Commercial Procedure Law Article 15 (exclude the event day; expire at the end of the corresponding date) gives a working initial deadline of **19 July 2026**.
- The official Cairo Governorate portal publicly stated **18 July 2026** as the last day (notice dated 21 June 2026): https://www.cairo.gov.eg/ar/more/more/taqnen/
- The one-day discrepancy is not resolved by Decision 480's text. The authority's public notice must be preserved as an official administrative statement, not treated as a statutory amendment. No definitive initial filing day is certified without an official interpretation of the special administrative filing rule and portal operation.

### Additional period under Presidential Decision 480/2026

Article 1 says the Article 3(1) application period is extended “for another equivalent period” (لمدة أخرى مماثلة). The decision contains no express calendar end date and does not identify the new period's start date.

Conditional constructions:
- If the additional six months run consecutively after 18 July 2026: **18 January 2027**.
- If they run consecutively after 19 July 2026: **19 January 2027**.
- If a new six-month period begins on publication/effectiveness of Decision 480 on 10 November 2026: **10 or 11 May 2027**, depending on the applicable event-day rule.

No official circular, platform reopening notice or binding judgment was located in this pass selecting one construction. Therefore **the final application deadline remains uncertified**. Do not encode any candidate date as definitive. Decision 480 expressly refers to Article 3(1); it does not expressly extend the separate Article 11 period.

## 5. Constitutional Court judgments

- **Case 10/35 (2 June 2018):** Articles 21 and 24 of Law 142/1964 were invalidated; Article 23 and Justice Decision 553/1976 fell consequentially. The original judgment's printed Gazette scan reproduction was visually inspected in the earlier judgment note (Official Gazette issue 22 bis (ط), 6 June 2018, pp. 16–25). No direct official SCC URL for Case 10/35 itself or Amiri Press digital original was found. A later official SCC judgment reproduces and explains the holding: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/12158_41_14_3_2.html .
- **Case 42/17 (6 June 1998):** Article 37(2) of Law 142/1964 was invalidated and Article 38 fell consequentially; Article 37(1) was not invalidated. Full text remains secondary. Gazette issue/date is conflicted: issue 35 supplement vs issue 25 supplement, both reported for 18 June 1998. No direct official SCC judgment page or original Gazette scan obtained. Secondary text: https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/15553 .
- **Case 101/26 (1 February 2009):** official SCC-hosted full judgment: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3204_26_101_1_2.html . It invalidated Article 22(1) of Law 143/1981; Gazette issue 7 bis (A), 15 February 2009. Original Gazette scan remains outstanding.
- **Rent Case 81/19 (6 February 1999):** official SCC full judgment: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/637_19_81_1_2.html . It invalidated only the final phrase of Article 18(b) of Law 136/1981 requiring execution of the urgent eviction judgment in the tenant's presence. Original Gazette scan remains outstanding.
- **Rent Case 108/19 (19 December 2004):** official SCC full judgment: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1617_19_108_1_2.html . It rejected the challenge as inadmissible, relying on Case 203/20 (14 April 2002); it is not a merits invalidation. Original Gazette scan remains outstanding.
- **Rent Case 24/20 (9 November 2024):** official SCC full judgment page now located at https://www.sccourt.gov.eg/SCC/faces/Rules_Html/15196_20_24_1_2.html. It invalidated the first paragraph of each of Law 136/1981 Articles 1 and 2 insofar as they fixed annual residential rent; effect is deferred to the day after the end of the then-current ordinary parliamentary session. The printed Gazette scan reproduction (issue 45 bis (A), 10 November 2024, pp. 17–30) was also visually inspected. Do not describe it as blanket invalidation.
- **Rent Case 81/19 (6 February 1999):** official SCC full judgment page is now recorded in EG-0247. It invalidates only the final phrase of Article 18(b) requiring execution in the tenant's presence. Original Gazette judgment page remains outstanding.
- **Rent Case 108/19 (19 December 2004):** official SCC full judgment page is now recorded in EG-0248. The challenge was inadmissible because Case 203/20 had already resolved the issue; it is not a merits invalidation. Original Gazette judgment page remains outstanding.
- **Additional rent-law judgment backlog from checkpoint 88:** Cases 6/9 (1995), 4/15 (1996), 3/18 (1997), 44/17 (1997), 116/18 (1997), 70/18 (2002), 144/20 (2000), 6/20 (2002), 4/23 (2003), 14/23 and 47/21 (2004), 116/27 (2008), and 11/23 (2018) are now separately registered as EG-0249–EG-0261. Case 70/18 and Case 144/20 have later official SCC judgments confirming their holdings; Case 11/23 has a secondary full-text transcription and an SCC principles-page cross-reference. The original direct judgment pages and Gazette publication scans remain outstanding for these 13 records.

Judicial decisions remain a distinct category from statutory amendments. The acquisition register now contains six explicit SCC case records: Cases 10/35, 42/17, 101/26, 24/20, 81/19 and 108/19. Other rent-law judgment authorities remain indexed in the judicial research layer and are not double-counted as separate statutory instruments.

## 6. Amendment-chain reconciliation

### Law 143/1981

Statutory chain identified:
- Law 12/1984 — repeals Article 21 (same Law 12/1984 instrument as the Irrigation and Drainage Law; now consolidated under EG-0153).
- Law 55/1988 — replaces Article 12(2).
- Law 205/1991 — replaces Article 11(2).
- Law 96/1995 and Law 72/1996 — successive replacements of Article 4(1).
- Law 11/2024 — replaces Article 11(2) and Article 12(2), effective 25 February 2024.
- Case 101/26 separately invalidates Article 22(1).

Executive Regulation Decision 198/1982: seven identified amendment decisions — 305/1983 (repeals Articles 27–30), 105/1986 and 1230/1990 (successive Article 45 versions), 139/1990 (Article 50), 305/1990 (Article 41), 1057/1995 (Article 42; published 5 June 1996), and 1012/2009 (Article 15). Original Gazette amendment scans remain outstanding.

### Law 114/1946

Identified statutory chain:
- Laws 69/1950, 222/1956, 136/1957, 82/1957, 181/1957, 5/1964, 25/1976, 223/1996, 186/2020, 5/2021 and 9/2022.
- Law 5/2021 is a commencement deferral for Law 186/2020, not a substantive replacement.
- Law 82/1957, Law 222/1956 and Law 181/1957 still require original Gazette verification; Law 25/1976 commencement metadata is disputed.
- Executive Regulation Decree 2/1946 and its amendment chain include Decisions 948/1976, 3003/1979, 9310/2020 and 2332/2022. Decision 825/1975 is the separate Executive Regulation under Law 142/1964; its amendment chain is handled under the Law 142 section and includes Decision 11264/2016. Full pre/post article versions and original issue scans remain incomplete.

### Law 142/1964

- Law 83/2006 replaced Article 30; it also amended Law 70/1964 Article 19.
- Case 42/17 invalidated Article 37(2), with Article 38 consequentially falling.
- Case 10/35 invalidated Articles 21 and 24, with Article 23 and Decision 553/1976 consequentially falling.
- Executive Regulation Decision 825/1975 and amendment Decision 11264/2016 require a full article redline.
- Territorial commencement/postponement decisions are section-specific; they do not amend the substantive statute. Decision 5208/2026's third-party mirror mismatch remains a source-image issue.

### Laws 68/1947 and 70/1964

- Law 68/1947: Law 629/1955 replaced Article 3; Law 103/1976 replaced Articles 2, 5, 6, 9 and 12; Law 5/1964 repealed Article 1. Executive-regulation changes include Presidential Decision 820/1963, Justice Decision 1532/1976 and Decision 4730/2020.
- Law 70/1964: Laws 94/1980, 6/1991, 224/1996, 225/1996, 9/2003, 3/2004, 83/2006, 163/2019 and 67/2021. SCC Cases 2/24 and 10/16 are separate constitutional-effect records, not amendments.

The 44-event historical article-version register currently records effects but lacks exact pre/post Arabic text for many events. No article version is to be overwritten; add successive snapshots and separate repeal, invalidation, consequential fall and deferral event types.

## 7. Civil Code, Evidence Law and Building Law extraction status

- **Civil Code Law 131/1948:** Article-number extraction is complete through Article 1149. Current unique non-repealed base provisions count is **1,093**; the 56-number difference is the repealed ranges Articles 54–80 and 389–417. Article 766(2) has been recovered. This is a complete base-text extraction set, not a current consolidated code; amendment/version/currentness review remains incomplete.
- **Evidence Law 25/1968:** requested Articles 1–117 are already extracted (checkpoints 112–113). The wider enacted statute is treated as Articles 1–162 plus inserted Article 148 bis, for **163 unique article provisions**. WIPO's apparent Article 163 line duplicates Article 153 and is an OCR anomaly. The official Ministry of Finance 12-page Gazette reproduction is located; 11/12 pages were visually inspected and PDF index 4 remains unverified. Amendment laws 54/1974, 23/1992, 18/1999 and 76/2007 are identified; original amendment Gazette scans and historical text diffs remain outstanding.
- **Building Law 119/2008:** official Ministry of Housing Gazette reproduction contains 114 substantive articles. Law 23/2015 is the principal statutory amendment identified. Decision 144/2009 has 185 base numbered regulation articles in a secondary full-text reproduction; the secondary claim of 198 current provisions is unverified. Later regulation changes include Decisions 200/2010, 109/2013, 67/2014, 774/2014, 954/2022, 120/2025 and 1505/2025; original issue images, forms/schedules and article redlines remain open. OCR-corrupted Law 119 Articles 89, 102 and 114 must remain quarantined until page-image correction.

## 8. Provenance, repeal and version-status rules

- Store Gazette publication date/issue separately from enactment date, commencement date and any later effective date.
- Store source tier per file: original Amiri Press PDF; official publisher searchable text; official government-hosted Gazette reproduction; official court judgment page; secondary Gazette scan; secondary consolidated transcription.
- Store retrieval state separately from source metadata: listed/request-only, public PDF locator, PDF bytes acquired, hash generated, page images checked.
- Do not treat a secondary scan as an original Amiri Press binary.
- Distinguish express statutory repeal, partial repeal, commencement deferral, constitutional invalidation, consequential fall and replacement by a later text.
- Preserve each article's prior and subsequent wording with exact effective date and source, not one overwritten current string.
- Do not infer rights_cleared=true from a public portal, Gazette access or a DSpace catalogue record.

## 9. No new instrument or article text in this checkpoint

- New base laws: 0.
- New amending laws: 0.
- New executive regulations: 0.
- New judicial acquisition records: 15 (Cases 81/19 and 108/19 plus 13 rent-law judgment records EG-0249–EG-0261; Case 24/20 source provenance upgraded, not a new instrument).
- New full-text records: 0.
- New unique article provisions: 0.
- Changes are deduplication, source-status reconciliation, normalized type classification and corrected index metrics.

## 10. Outstanding blockers and next actions

1. Obtain authorized original Amiri Press PDFs for Laws 114/1946, 142/1964, 68/1947 and 70/1964; compare all 26 inspected pages against publisher originals.
2. Submit/obtain authorized access for Law 168/2025 and Presidential Decision 480/2026 DSpace bundles; archive Decision 200/2026's public SIS full-issue PDF with hash if permitted.
3. Ask the competent State-land regularization authority for a written interpretation identifying the start and final day of the Decision 480 extension and whether the period revives/bridges the July–November gap.
4. Obtain original SCC Gazette scans for Cases 42/17, 101/26, 81/19 and 108/19; retain official SCC HTML for Cases 101/26, 81/19 and 108/19 and the later official explanation of Case 10/35.
5. Resolve Case 42/17 issue-number conflict from the actual printed Gazette page.
6. Complete Law 143/1981, 114/1946 and 142/1964 article-level amendment graphs with pre/post Arabic text and commencement/repeal effects.
7. Recover Evidence Law PDF page index 4 and acquire amendment Gazette scans; visually validate Civil Code and Building Law OCR.
8. Complete Decision 144/2009 form/schedule review and regulation amendment graph.
9. Reconcile the 44 version events with canonical instrument IDs and add historical article snapshots.
10. Preserve source permissions and lawyer-review flags as false/unknown unless documentary evidence changes them.

## 11. Verification and rights

No lawyer verification, commercial reuse permission, certified Amiri Press authentication, or general bulk collection permission is claimed. No restricted download was bypassed. All 246 canonical acquisition records remain lawyer_reviewed=false and rights_cleared=false.
