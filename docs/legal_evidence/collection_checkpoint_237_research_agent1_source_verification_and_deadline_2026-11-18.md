# Collection checkpoint 237 — Research Agent 1 continuation: source verification and acquisition blockers

**Date:** 18 November 2026  
**Repository:** `abdelmalek384/legal_copilot_latest` (default branch `main`)  
**Scope:** continuation of the ten assigned Research Agent 1 priorities. This checkpoint records source verification, deadline analysis and register/count reconciliation. It does not claim that restricted files were acquired.

## 1. Repository and register audit

Rechecked the current master index, the Research Agent 1 checkpoint 203 handoff, checkpoint 235's four historical Gazette scan-copy findings, checkpoint 227's Decision 480 deadline analysis, checkpoint 231's handoff, checkpoint 234's Law 114 text recovery, the 250-row acquisition CSV and the source-permission JSON.

Live register counts:
- Canonical acquisition register: **250 records / 250 unique instrument IDs** (251 CSV lines including header).
- Source-permission register: **97 records / 97 unique source IDs**.
- Provisional instrument classes: **66 base laws; 48 amending laws; 13 executive regulations; 35 executive-regulation amendments; 21 judicial decisions; 54 other decisions/circulars/advisory records; 13 other/unclassified records**.
- Priority full-text inventory: **27 unique instruments**; 26 have searchable/full-text source status, with completeness varying.
- Core unique article provisions: **1,370** (Civil Code 1,093; Evidence Law 163; Building Law 114).
- Historical article-version events: **86**.
- Seven pending rent-law dockets remain separately recorded and are not counted as final judicial decisions.

The task's 172-record description is a stale snapshot, not the current register. No historical 172-row register was substituted. No canonical instrument, article text or judicial decision was added in this checkpoint; all counts above remain unchanged. The 250 instrument classifications are provisional title/domain-based classes, not a legal ontology validated by counsel.

## 2. Older Gazette PDFs: four requested statutes

The direct scan-copy URLs and issue identities in checkpoint 235 were rechecked against the acquisition/source registers:

| Instrument | Gazette issue and date | Available scan-copy | Status |
|---|---|---|---|
| Law 114/1946 | Egyptian Proceedings issue 85, 24 Aug 1946 | https://manshurat.org/file/83333/download?token=Kv0YfwAI | 6-page secondary-hosted scan |
| Law 142/1964 | Official Gazette issue 69, 24 Mar 1964 | https://manshurat.org/file/44021/download?token=5Zwo9ziS | 7-page secondary-hosted scan |
| Law 68/1947 | Egyptian Proceedings issue 58, 3 Jul 1947 | https://manshurat.org/file/82270/download?token=fuDVQjIu | 2-page secondary-hosted scan |
| Law 70/1964 | Official Gazette issue 67, 22 Mar 1964 | https://manshurat.org/file/43842/download?token=z-q7csZN | 11-page secondary-hosted scan |

These are scans of printed Gazette pages and support issue/date/page-image inspection. They are **not Amiri Press-hosted original digital binaries**. No original Amiri Press PDF bytes, publisher-certified copy or SHA-256 hash has been acquired for any of the four. The corresponding source-permission records remain unknown for collection and commercial reuse; public access is not a licence.

The official Amiri Press portal exposes an archive-print service for obtaining certified copies, but no authenticated download route for these four historical issues was located in this pass. Next step is a formal archive-copy request identifying each issue/date and law, then archive and hash the delivered files.

## 3. Law 168/2025, PM Decision 200/2026 and Presidential Decision 480/2026

### Law 168/2025
- Amiri Press DSpace metadata identifies Official Gazette issue 32 bis (و), 13 Aug 2025, publisher مطابع الأميرية, and an original-bundle PDF of approximately 294.4 KB.
- The DSpace download is request-a-copy restricted. The SIS-hosted 295.3 KB lead previously returned 502/inaccessible. A VetoGate scan and several searchable transcriptions are secondary-source alternatives, not original Amiri Press binaries.
- Text capture remains 18/18 provisions; original Gazette bytes/hash remain outstanding.

### PM Decision 200/2026
- Official Gazette issue 3 bis (أ), 18 Jan 2026. The official Amiri Press text portal directly serves the full Arabic decision and executive regulation: https://www.alamiria.com/Sec/TashTxt?id=cEpwOo6BfmY%3D
- The issuing text states in Article 4: **يعمل به من اليوم التالى لتاريخ نشره**. Accordingly, the regulation commenced **19 Jan 2026**.
- The official SIS full-issue Gazette PDF is separately linked in acquisition record EG-0174 and was previously opened/text-extracted. The original Amiri Press DSpace bundle remains request-copy restricted; no local PDF bytes/hash are archived.
- Text capture remains 24/24 issuing/regulation provisions plus Forms 1 (two variants), 2 and 3. Article 20's text-layer annual-report wording conflicts with quarterly wording in Form 3 and Law 168 Article 14; page-image verification/correction remains necessary.

### Presidential Decision 480/2026
- Official Gazette DSpace collection metadata identifies the item as **الجريدة الرسمية - العدد 45 مكرر (ج)**, dated **10 Nov 2026**, publisher Amiri Press, and attributes it to the President. The item identifies Decision 480/2026 as extending the Law 168/2025 Article 3(1) period for another equivalent period: https://dspace.id.com.eg/collections/bb4a4122-9215-48e2-a8a5-b622ffa5eeb6
- Direct item metadata / original-bundle record: https://dspace.id.com.eg/items/03b3721d-4847-4be0-8130-5d4bf38da540/full. The original bundle is listed as 178.37 KB but remains request-copy restricted. No original PDF bytes or hash were acquired.
- The two operative articles remain text-captured from independent secondary reproductions (2/2); this is not original-Gazette authentication.

## 4. Decision 480 commencement and final deadline — conclusion

The following facts are supportable:
1. PM Decision 200/2026 was published on 18 Jan 2026 and expressly commenced on 19 Jan 2026.
2. Law 168/2025 Article 3(1) measures the first application period from commencement of the executive regulation.
3. Cairo Governorate's official notice publicly treated **18 July 2026** as the last day of the first application period.
4. Presidential Decision 480/2026 was published in Official Gazette issue 45 bis (ج) on **10 Nov 2026**. Its Article 1 says only that the period is extended for “another equivalent period”; Article 2 orders publication. Neither article states an express commencement date, a new period start date, a calendar expiry date, or the treatment of applications in the 19 July–10 November 2026 interval.

Two calculations therefore remain conditional, not certified:
- **Consecutive-extension construction:** 19 Jul 2026–18 Jan 2027, producing 18 Jan 2027 as the candidate final day.
- **Publication-based construction:** if the new six-month period starts on the day after publication (11 Nov 2026), the candidate final day is 10 May 2027; if it starts on publication day, it is 9 May 2027.

**Finding:** the precise commencement and final application deadline cannot be established from Decision 480's published operative wording alone. Neither 18 Jan 2027 nor 9/10 May 2027 is printed in the decision or independently confirmed by a competent authority. The decision's commencement default and the status of applications during the apparent gap require a written official interpretation/circular from the competent state-land regularization authority (and, if necessary, the Presidency/Cabinet or State Council). Do not encode any candidate as a verified deadline or advise applicants to rely on it.

## 5. Constitutional Court judgments and rent-law cases

The existing evidence remains:
- **Case 10/35:** secondary-hosted ten-page Gazette reproduction, issue 22 bis (ط), 6 Jun 2018, visually inspected; official signed SCC original and Amiri Press original remain outstanding. Later official SCC material corroborates the holding invalidating Articles 21 and 24 of Law 142/1964, with consequential fall of Article 23.
- **Case 42/17:** full secondary judgment text available; official later SCC and Court of Cassation materials corroborate the partial invalidity of Article 37(2) and consequential fall of Article 38. The Article 37 evidentiary-force limb must not be marked invalid. Gazette publication is identified as issue 35 تابع, 18 Jun 1998; original signed judgment/page remains outstanding.
- **Case 101/26:** full judgment is available on the official SCC site at https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3204_26_101_1_2.html, dated 1 Feb 2009 and identified as Gazette issue 7 bis (أ), 15 Feb 2009. Original printed Gazette page-image validation remains outstanding.
- **Rent-law cases:** searchable full texts and later SCC corroboration are recorded for Cases 4/23, 14/23, 47/21, 116/27, 144/20 and 6/20; Case 11/23 has a secondary-hosted Gazette-issue reproduction (issue 19 bis (ب), 13 May 2018). Original signed SCC judgment files and exact original Gazette scans remain outstanding for the identified cases. Pending dockets remain separately classified.

No new judicial decision is counted in this checkpoint. Do not equate an official SCC HTML judgment with an original signed PDF or original Gazette page image.

## 6. Amendment chains and article extraction

- **Law 143/1981:** 29 substantive articles have consolidated Arabic text; six statutory amendment laws and seven executive-regulation decisions are mapped. Article 21 repeal and Article 22(1) constitutional invalidity are separately flagged. Law 55/1988 standalone text, original amendment Gazette scans and complete historical redlines remain outstanding.
- **Law 114/1946:** checkpoint 234 raises searchable provision coverage to 66/70 IDs, including Article 19 bis; the four absent former bodies are repealed Articles 3, 24, 26 and 29. Twelve statutory/transitional amendment events are identified. Full historical versions, original amendment Gazettes and reconciliation of Law 9/2022 remain incomplete.
- **Law 142/1964:** 66/66 substantive article-body/status entries are represented in the later master-index state; Law 83/2006 expressly replaced Article 30, and a 1964 corrigendum affects Articles 62/65. Constitutional effects of Cases 10/35 and 42/17 must remain provision-specific. Full historical redlines and original amendment Gazette scans remain outstanding.
- **Civil Code Law 131/1948:** 1,093 unique non-repealed provisions are already in the core set. Do not duplicate them. Historical wording for repealed Articles 54–80 and 389–417 is incomplete; full 1–1149 historical/current version reconciliation remains open.
- **Evidence Law 25/1968:** Articles 1–117 are fully transcribed in checkpoints 112–113; total statute representation is 163 provision units including Article 148 bis. Ministry of Finance Gazette reproduction is visually inspected for 11/12 pages; printed page 315 remains a rendering blocker. No duplicate transcription is added here.
- **Building Law 119/2008:** base Articles 1–114 are already transcribed (114/114). The eight Articles 2 and 4–10 from a 2020 secondary consolidation are alternate-source snapshots, not new unique provisions. Decision 144/2009 has 184/185 base article bodies; Article 127 is repealed. Nine inserted bis provisions have varying capture completeness; forms/schedules, page-image verification and full amendment/currentness redline remain outstanding.

## 7. Counts, provenance and rights

No new legal instruments, amendments, executive regulations, judicial decisions, full texts or unique article provisions are counted in checkpoint 237. No register rows are added, deleted or merged. Existing source records retain their source-specific permission states. Keep base laws, amending laws, executive regulations, executive-regulation amendments, judicial decisions, other decisions/circulars, full texts, unique article provisions and historical version events as separate measures.

**No lawyer verification, commercial reuse permission, bulk retrieval permission, redistribution permission or publisher authentication is claimed.** Labels must remain `source-matched, not lawyer-reviewed` where applicable.
