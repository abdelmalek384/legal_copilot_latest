# Research Agent 1 — continuation checkpoint 239 (18 November 2026)

## 1. Scope and repository audit

Inspected the live master index; collection checkpoints 85–92 and their substantive/supplemental sections; checkpoint 93; and later relevant records covering the four property statutes, amendment chains, source acquisition, deadline analysis, SCC judgments, rent-law dockets, Civil Code/Evidence extraction, Building Law/Decision 144 and article deduplication. The current source files were read directly:
- `data/research/egypt_initial_statute_acquisition_register_2026-11-17.csv`
- `data/research/egypt_instrument_type_classification_2026-11-18.csv`
- `data/research/egypt_acquisition_register_aliases_2026-11-18.csv`
- `data/research/egypt_full_text_inventory_priority_2026-11-18.csv`
- `data/research/egypt_historical_article_version_events_2026-11-18.csv`
- `docs/source_permission_register.json`

The user-supplied 172-record / 40-source figures are historical snapshots, not the live files. No historical snapshot was substituted for the current registers.

## 2. Live register audit and count reconciliation

Counts were parsed from the actual CSV/JSON files, including quoted fields and duplicate IDs.

| Measure | Live count | Rule / qualification |
|---|---:|---|
| Canonical acquisition records | **355** | 355 CSV data rows; 355 distinct EG IDs; zero duplicate IDs |
| Base laws | **76** | Provisional title/domain classification |
| Amending laws | **69** | Provisional title/domain classification |
| Executive regulations | **19** | Original regulation instruments |
| Executive-regulation amendments | **44** | Subordinate instruments amending regulations |
| Judicial decisions | **21** | Acquired judgment records; pending dockets are not included |
| Other decisions | **112** | Other/circular/administrative decision records |
| Other / unclassified | **14** | Provisional classification |
| Source-permission register | **111** | Unique source assessments, not permissions granted |
| Full-text inventory | **131 rows / 127 unique instruments** | Four additional rows are duplicate instrument/source-version entries |
| Historical article-version event register | **127** | Unique event IDs; 58 linked instrument IDs |
| Core unique operative article provisions | **1,370** | Civil Code 1,093 + Evidence Law 163 + Building Law 114 |
| Civil Code article/status coverage | **1,149** | 1,093 operative article bodies + 56 historical/repealed article body/status entries; some historical bodies remain incomplete |
| Additional property-statute headings | **200** | Laws 114/1946 (70), 142/1964 (72), 68/1947 (14), 70/1964 (44); headings are not automatically unique operative provisions |
| Lawyer verification | **0** | No lawyer sign-off recorded |
| Commercial reuse permission established | **0** | Public access and source discovery do not establish reuse permission |

The current acquisition CSV and classification ledger agree at 355 rows/IDs. This supersedes the older master-index dashboard count of 336 and checkpoint 238's 273-row snapshot. The alias map preserves 11 historical duplicate IDs as aliases; these are not extra canonical instruments. Numeric gaps EG-0076–EG-0079 remain unresolved and were not fabricated or filled.

The master-index full-text inventory count of 108 rows/104 instruments is also stale: the live inventory has 131 rows/127 distinct instrument IDs. Individual inventory status varies between complete, partial, source-only and external-only; the row count must not be described as 131 complete local texts. The earlier 85-instrument full/complete-source tally is retained only as a legacy metric pending a field-by-field status recode.

## 3. Priority Gazette acquisition results

### Laws 114/1946, 142/1964, 68/1947 and 70/1964

No original Amiri Press digital PDF binary was acquired. Existing public scan routes are secondary-hosted reproductions only; 26 pages have been visually inspected:
- Law 114/1946 — Egyptian Proceedings issue 85, 24 August 1946; 6-page secondary scan: https://manshurat.org/file/83333/download?token=Kv0YfwAI
- Law 142/1964 — Official Gazette issue 69, 24 March 1964; 7-page secondary scan: https://manshurat.org/file/44021/download?token=5Zwo9ziS
- Law 68/1947 — Egyptian Proceedings issue 58, 3 July 1947; 2-page secondary scan: https://manshurat.org/file/82270/download?token=fuDVQjIu
- Law 70/1964 — Official Gazette issue 67, 22 March 1964; 11-page secondary scan: https://manshurat.org/file/43842/download?token=z-q7csZN

These are not certified copies or authenticated original publisher binaries. No local PDF bytes or SHA-256 hashes are recorded. The Amiri Press website exposes an archive service for obtaining true copies of laws/decisions; the proper next step is a formal archive-copy/certified-copy request identifying each issue and date. Do not bypass DSpace or request-copy restrictions.

### Law 168/2025, PM Decision 200/2026 and Presidential Decision 480/2026

- **Law 168/2025:** Amiri Press DSpace metadata identifies Gazette issue 32 bis (و), 13 August 2025, original bundle 294.4 KB, item UUID 8255632b-a2d4-44c3-9888-d4e2801e8d32. Download remains request-copy restricted. A secondary searchable text and scan reproduction exist. No original bytes/hash.
- **PM Decision 200/2026:** Gazette issue 3 bis (أ), 18 January 2026, original DSpace bundle 1.89 MB, item UUID c8ee628f-2d7b-4f33-ab68-a68db8c99eb1; request-copy route. Official Amiri Press searchable text is available at https://www.alamiria.com/Sec/TashTxt?id=cEpwOo6BfmY%3D. An official SIS-hosted full-issue PDF was opened and text-extracted, but its bytes/hash were not archived. All 24 issuing/regulation provisions and Forms 1 (two variants), 2 and 3 are represented in text. The Article 20 annual/quarterly reporting discrepancy remains unresolved by page-image inspection.
- **Presidential Decision 480/2026:** Gazette issue 45 bis (ج), 10 November 2026, original DSpace bundle 178.37 KB, item UUID 03b3721d-4847-4be0-8130-5d4bf38da540. Download remains request-copy restricted. Both operative articles are transcribed from secondary reproductions; no original bytes/hash.

No original Amiri Press PDF bytes or hashes were archived in this continuation.

## 4. Decision 480/2026 — commencement and final application deadline

PM Decision 200/2026 was published on 18 January 2026 and its issuing Article 4 makes it effective the following day: **19 January 2026**. Law 168/2025 Article 3(1) starts the six-month filing period from commencement of the Executive Regulation. The competent local-government notice and subsequent State Land Recovery Committee statements identify **18 July 2026** as the initial final filing day. The general corresponding-date calculation produces a one-day alternative of 19 July; preserve the discrepancy.

Decision 480/2026 was signed and published on **10 November 2026**. Article 1 extends the Article 3(1) period for “another equivalent period”; Article 2 directs publication. It does not print a commencement date or calendar endpoint and does not expressly address the July–November interval.

**Best-supported administrative planning calculation:** if the extension is consecutive to the officially announced 18 July expiry, the further six-month period ends **18 January 2027**. A one-day alternative of **19 January 2027** follows if the general time-computation rule is applied to the 19 July alternative. A fresh six-month period from publication could point to May 2027, but is less consistent with the reported committee explanation that the extension follows the original July period.

Neither 18 nor 19 January 2027 is an express date in Decision 480 or a formally confirmed official deadline. The treatment of the July–November gap and any applications filed in it remain unresolved. Do not encode either date as a certified legal deadline. Obtain written clarification from the competent State Land Recovery Committee / land authority. For operational risk control only, plan filing before the earlier candidate, 18 January 2027.

Key sources:
- Official DSpace Decision 480 metadata: https://dspace.id.com.eg/items/03b3721d-4847-4be0-8130-5d4bf38da540/full
- Official DSpace PM Decision 200 metadata: https://dspace.id.com.eg/items/c8ee628f-2d7b-4f33-ab68-a68db8c99eb1/full
- Official DSpace Law 168 metadata: https://dspace.id.com.eg/items/8255632b-a2d4-44c3-9888-d4e2801e8d32/full
- Cairo Governorate notice: https://www.cairo.gov.eg/ar/governorate-entities/neighborhoods/north-area/hay-alamiriya/news/2026/june/09c8646b18c94561a1985b0a83aa38ef
- Official Amiri Press Decision 200 text: https://www.alamiria.com/Sec/TashTxt?id=cEpwOo6BfmY%3D

## 5. Constitutional Court judgments and rent-law dockets

- **Case 10/35 (2 June 2018):** 10-page secondary-hosted Gazette scan reproduction (issue 22 bis (ط), 6 June 2018) visually inspected. It records invalidity of Law 142/1964 Articles 21 and 24, consequential fall of Article 23 and Justice Minister Decision 553/1976. Later official SCC judgment corroborates the holding. Original signed judgment / Amiri Press binary remains outstanding.
- **Case 42/17 (6 June 1998):** complete searchable secondary judgment text and later official SCC corroboration. Article 37(2) of Law 142/1964 was invalidated and Article 38 fell consequentially; Article 37(1)'s evidentiary limb remains. Gazette issue metadata conflicts between issue 35 تابع and issue 25 تابع (ب), both reported for 18 June 1998. Original printed page and signed judgment remain outstanding.
- **Case 101/26 (1 February 2009):** full official SCC judgment HTML exists; it invalidates Article 22(1) of Law 143/1981 to the extent of the ordinary-court exclusive-jurisdiction rule. Gazette issue 7 bis (أ), 15 February 2009. Original Gazette page image / hash remains outstanding.
- **Case 11/23 (5 May 2018; Law 136/1981 non-residential leases to legal persons):** complete secondary text and official SCC subject-page corroboration; original signed judgment and Gazette issue 19 bis (ب), 13 May 2018 scan remain outstanding.
- The rent-law docket tracker lists seven pending challenges (Cases 33/47, 34/47, 37/47, 38/47, 18/48, 19/48 and 21/48). These are pending proceedings, not judgments or invalidation events. No final judgment was identified in the latest docket refresh; hearing reports in November 2026 describe adjournments, not suspension or invalidation of Law 164/2025.

No new final judgment or original SCC/Gazette judgment binary was acquired in this continuation.

## 6. Amendment-chain and article extraction status

### Laws 143/1981, 114/1946 and 142/1964

- **Law 143/1981:** identified statutory chain includes Laws 12/1984 (repeal of Article 21), 55/1988 (Article 12(2)), 205/1991 (Article 11(2)), 96/1995 and 72/1996 (successive Article 4(1) replacements), and 11/2024 (Articles 11(2) and 12(2)). SCC Case 101/26 is a separate constitutional invalidation of Article 22(1). Executive Regulation Decision 198/1982 has seven identified amendments: Decisions 305/1983, 105/1986, 139/1990, 305/1990, 1230/1990, 1057/1995 and 1012/2009. Full primary Gazette amendment scans and pre/post Arabic redlines remain incomplete.
- **Law 114/1946:** the event register identifies successive statutory events including Laws 157/1947, 69/1950, 222/1956, 82/1957, 136/1957, 181/1957, 5/1964, 25/1976, 223/1996, 186/2020, 5/2021 and 9/2022; selected regulation events include Decisions 948/1976, 9310/2020 and 2332/2022. Current text coverage is substantial, but four repealed base bodies (Articles 3, 24, 26 and 29) remain historical-text gaps. Do not call the amendment graph closed.
- **Law 142/1964:** identified statutory replacement includes Law 83/2006 (Article 30); Decision 11264/2016 amended the Executive Regulation. SCC Cases 42/17 and 10/35 impose separate invalidity/consequential-fall effects. All 66 substantive article headings have text or an explicit legal-effect status in the repository, but original Gazette amendment scans and full version-by-version pre/post redlines remain outstanding.

### Civil Code Law 131/1948

The live inventory records 1,149 article/status entries: 1,093 operative article bodies plus 56 historical/repealed bodies or status entries. The core 1,093 count is already included in the 1,370 core unique provision count. The historical text for repealed Articles 54–80 and 389–417 remains incomplete, and amendment-by-amendment historical versions are not normalized for every event. Checkpoints 94–99 contain selected supplemental ranges, not proof that every historical version is complete. Continue by filling those historical gaps and linking each version to its amendment/repeal event; do not duplicate already captured operative article bodies.

### Evidence Law 25/1968

Articles 1–117 are already fully transcribed in checkpoints 112–113. The full statute is represented as 163 provision units (Articles 1–162 plus inserted Article 148 bis). The official Ministry of Finance Gazette reproduction has 11 of 12 pages visually inspected; page index 4 (printed page 315) repeatedly fails to render. LAW HUB / Egypt Notaries Union text bridges the missing page but remains secondary. Amendments and historical versions remain to be normalized; no new article bodies were added here.

### Buildings Law 119/2008 and Decision 144/2009

- Law 119/2008: all 114 substantive base article bodies are transcribed from the Ministry of Housing government-hosted Gazette reproduction. Original Amiri Press binary/hash and complete amendment/currentness graph remain outstanding.
- Decision 144/2009: 184/185 extant base article bodies are captured; Article 127 is repealed. Nine inserted bis provisions are tracked separately with varying text completeness. Forms/schedules, full amendment redline and page-image verification remain outstanding. The searchable 185-article source is secondary; the government-bank PDF lead is not an original Amiri Press binary.

## 7. Provenance, status and rights rules reaffirmed

Preserve separately: instrument identity; issuing authority; enactment date; Gazette type/issue/supplement/date/page; commencement; source URL/host/tier; retrieval date; whether PDF bytes were actually acquired; SHA-256 only when bytes are lawfully obtained; page-image inspection; article/version IDs; amendment/repeal/constitutional invalidity/consequential fall; source permission; lawyer review.

Do not equate a government-hosted reproduction with an original Amiri Press binary. Do not equate a searchable text page or DSpace catalogue record with downloaded PDF bytes. Keep express repeal, partial repeal, deferred commencement, constitutional invalidity and consequential fall as distinct status events. Never infer collection, commercial reuse or redistribution permission from public access.

## 8. Changes in this continuation

- New legal instruments: **0**.
- New amendments added to acquisition register: **0**.
- New executive regulations: **0**.
- New final judicial decisions: **0**.
- New full-text inventory records: **0**.
- New unique article provisions: **0**.
- Register rows changed: **0**; no duplicate legal instrument or article text was added.
- New original Gazette PDF bytes / hashes: **0**.
- Lawyer verification: **0**.
- Commercial reuse permission established: **0**.

This checkpoint is a repository audit, source/provenance update and continuation handoff. It does not certify current law, source authenticity beyond the stated source tier, or legal advice.
