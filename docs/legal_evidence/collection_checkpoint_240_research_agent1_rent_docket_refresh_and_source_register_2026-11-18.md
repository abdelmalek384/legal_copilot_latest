# Research Agent 1 — continuation checkpoint 240 (18 November 2026)

## Scope

This continuation rechecked the live repository baseline, the priority source leads and the rent-law SCC docket after checkpoint 239. It supplements, and does not replace, checkpoints 85–93 and 227–239. It does not claim access to restricted original Gazette bundles.

## 1. Canonical register reconciliation

The current default-branch acquisition CSV and classification ledger each contain **367 data rows / 367 distinct instrument IDs**. The master-index classification is 366 confirmed instruments plus one provisional candidate (Decision 6199/2007). There are no duplicate canonical IDs in the live CSV. The alias map preserves historical duplicate identifiers separately.

Current instrument classes:
- 77 base laws
- 70 amending laws
- 20 executive regulations
- 51 executive-regulation amendments
- 21 judicial decisions
- 114 other decisions
- 14 other / unclassified records

The source-permission register was updated from 119 to **122 unique source assessments** by adding three public news-report locators for rent-law docket discovery. These records all retain collection_permission = unknown and commercial_reuse_permission = unknown. They are not permissions granted.

The priority full-text inventory has **148 rows / 144 unique instruments**. Four rows are additional source/version entries, not duplicate legal instruments. The historical article-version event register has **127 events**. Core unique operative article provisions remain **1,370**: Civil Code 1,093; Evidence Law 163; Building Law 114. These counts exclude additional article-heading metadata and incomplete/historical placeholders.

No acquisition-register instrument row, instrument classification, full-text inventory row, historical version event or article body was added in this pass. No new legal instrument or unique article provision is counted.

## 2. Rent-law SCC docket refresh

New secondary reporting located:
- **Case 21/48 (Judicial Year 48):** Cairo24 report dated 8 November 2026 says the Commissioners Authority adjourned the matter to **13 December 2026**, reportedly because State Lawsuits Authority had not supplied requested documents. Al-Watan report dated 9 November 2026 independently reports the same next date and procedural posture. These are news reports, not official docket entries or judgments.
- **Case 44/48 (Judicial Year 48):** Al-Aqaria report dated 6 October 2026 reports a newly filed challenge seeking invalidation of Law 164/2025, particularly Articles 2, 3, 4 and 7. The filing and relief remain to be verified against the SCC registry.
- The seven cases already tracked in checkpoint 239 remain separate docket entries: 33/47, 34/47, 37/47, 38/47, 18/48, 19/48 and 21/48. Do not count any pending challenge as a judicial decision or constitutional invalidation.
- The reports do not establish suspension of Law 164/2025 or any final judgment. No original SCC judgment was acquired in this refresh.

Sources:
- https://www.cairo24.com/250742
- https://www.elwatannews.com/news/details/8392899
- https://www.aleqaria.com.eg/post/details/353182/

Three corresponding source-permission entries were added:
- EG-CAIRO24-OLDRENT-CASE21-48-2026
- EG-ELWATAN-OLDRENT-CASE21-48-2026
- EG-ALEQARIA-OLDRENT-CASE44-48-2026

All three remain rights-uncleared; no licence or commercial reuse permission was established.

## 3. Priority Gazette and judgment status — no acquisition upgrade

The four historical Gazette scan copies remain secondary-hosted reproductions of original issue pages, not original Amiri Press digital binaries:
- Law 114/1946 — Egyptian Proceedings issue 85, 24 August 1946; 6-page scan: https://manshurat.org/file/83333/download?token=Kv0YfwAI
- Law 142/1964 — Official Gazette issue 69, 24 March 1964; 7-page scan: https://manshurat.org/file/44021/download?token=5Zwo9ziS
- Law 68/1947 — Egyptian Proceedings issue 58, 3 July 1947; 2-page scan: https://manshurat.org/file/82270/download?token=fuDVQjIu
- Law 70/1964 — Official Gazette issue 67, 22 March 1964; 11-page scan: https://manshurat.org/file/43842/download?token=z-q7csZN

The three 2025–2026 DSpace Amiri Press bundle records remain catalogue metadata/request-copy routes:
- Law 168/2025 — issue 32 bis (و), 13 August 2025; item UUID 8255632b-a2d4-44c3-9888-d4e2801e8d32.
- PM Decision 200/2026 — issue 3 bis (أ), 18 January 2026; item UUID c8ee628f-2d7b-4f33-ab68-a68db8c99eb1. An official SIS-hosted full-issue PDF was previously opened and text-extracted, but local bytes/hash are not archived.
- Presidential Decision 480/2026 — issue 45 bis (ج), 10 November 2026; item UUID 03b3721d-4847-4be0-8130-5d4bf38da540.

Official DSpace records identify the publisher as Amiri Press and show original bundle filenames/sizes. A catalogue entry is not a downloaded PDF. No original Amiri Press PDF bytes or SHA-256 hashes were acquired in this pass.

Judgment status:
- **Case 10/35 (2 June 2018):** a secondary-hosted judgment PDF/scan locator exists and later official SCC material corroborates the holding (invalidity of Law 142/1964 Articles 21 and 24; consequential fall of Article 23 and Decision 553/1976). Original signed SCC file not acquired.
- **Case 42/17 (6 June 1998):** full secondary judgment transcription exists; official later SCC material quotes/corroborates the holding (Article 37(2) invalid; Article 38 consequentially falls). Original signed judgment not acquired. Gazette issue metadata remains inconsistent between issue 35 تابع and issue 25 تابع (ب), both reported on 18 June 1998.
- **Case 101/26 (1 February 2009):** full original judgment text is available on the official SCC website at https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3204_26_101_1_2.html. The original Gazette judgment page image and local hash remain outstanding.
- **Case 11/23 (5 May 2018):** secondary full-text transcription and official SCC subject-page corroboration exist; original signed judgment and Gazette issue 19 bis (ب) scan remain outstanding.

## 4. Decision 480/2026 deadline — preserve unresolved alternatives

PM Decision 200/2026 was published 18 January 2026 and its issuing Article 4 makes it effective 19 January 2026. Cairo Governorate publicly announced 18 July 2026 as the initial six-month filing deadline; the general corresponding-date calculation can produce 19 July. Decision 480/2026 was published 10 November 2026 and extends the Article 3(1) period for “another equivalent period” but states neither a commencement date nor a calendar endpoint.

The best-supported conservative administrative planning date remains **18 January 2027**, with **19 January 2027** as the one-day alternative. A publication-based May 2027 interpretation is less consistent with the available committee explanation but cannot be erased from the interpretive history. None is expressly printed or authoritatively confirmed. Treatment of applications during the July–November interval remains unresolved. Do not encode a certified final deadline; obtain written competent-authority clarification.

## 5. Remaining extraction and amendment work — no duplicate article text

- **Laws 143/1981, 114/1946 and 142/1964:** amendment-event chains remain identified but not fully redlined against original Gazette scans. Law 114 historical bodies for repealed Articles 3, 24, 26 and 29 remain missing. Law 142 has text or legal-effect status for all 66 substantive articles; historical version comparison and original amendment scans remain open. Law 143 chain includes Laws 12/1984, 55/1988, 205/1991, 96/1995, 72/1996 and 11/2024; original amendment scans and full pre/post redlines remain open.
- **Civil Code 131/1948:** 1,093 non-repealed operative article bodies are already complete and deduplicated. The 56 historical/repealed entries are status records, not 56 additional full texts. The government-hosted base PDF marks Articles 54–80 and 389–417 as repealed; original historical wording for these 56 provisions remains to be recovered from an authorized 1948 source. Do not create duplicate operative bodies.
- **Evidence Law 25/1968:** Articles 1–117 are already transcribed. The full statute is represented as 163 provision units (Articles 1–162 plus inserted Article 148 bis). One page of the Ministry of Finance Gazette reproduction remains visually inaccessible; secondary text bridges it. Amendment/version mapping remains open.
- **Buildings Law 119/2008:** 114 substantive base articles are transcribed from a government-hosted Gazette reproduction; original Amiri Press bytes/hash and complete amendment/currentness graph remain outstanding.
- **Decision 144/2009:** 184 of 185 extant base article bodies are captured; Article 127 is repealed. Nine inserted bis provisions and forms/schedules require completion/version checks. The 77–90 subset capture is superseded by the 77–93 full capture and adds no new unique article IDs.

## 6. Counts and verification boundaries

| Measure | Current count | Meaning |
|---|---:|---|
| Acquisition register | 367 | 366 confirmed + 1 provisional candidate |
| Base laws | 77 | Instrument classification |
| Amending laws | 70 | Instrument classification |
| Executive regulations | 20 | Instrument classification |
| Executive-regulation amendments | 51 | Instrument classification |
| Judicial decisions | 21 | Acquired decision records; excludes pending dockets |
| Other decisions | 114 | Instrument classification |
| Other / unclassified | 14 | Provisional classification |
| Source-permission assessments | 122 | 119 prior + 3 docket-report sources; not permissions |
| Full-text inventory | 148 rows / 144 unique instruments | Includes partial/source-only statuses |
| Historical article-version events | 127 | Event records, not article count |
| Core unique operative article provisions | 1,370 | 1,093 Civil Code + 163 Evidence + 114 Building |
| Additional property-statute headings | 200 | 70 + 72 + 14 + 44; not full article bodies |
| New instruments in this pass | 0 | No new legal instrument |
| New full-text inventory records | 0 | No new full-text instrument record |
| New unique article provisions | 0 | No duplicate or new article body |
| New original Gazette PDF bytes / hashes | 0 | No binary acquired |
| Lawyer verification | 0 | No lawyer sign-off |
| Commercial reuse permissions established | 0 | No permission grant |

No access-control bypass was attempted. No lawyer verification, currentness certification or commercial reuse permission is claimed.
