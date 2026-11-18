# Collection checkpoint 192 — complete searchable Arabic texts for Law 168/2025, PM Decision 200/2026 and Presidential Decision 480/2026

**Date:** 18 November 2026  
**Agent:** Research Agent 1

## 1. Text extraction completion

A full searchable Law 168/2025 page was opened on Diwan Al-Omran:
https://diwanalomran.com/fr/legal/2025-168/

A full searchable PM Decision 200/2026 page was opened on LAW HUB:
https://lawhub.info/eg/?p=17395

An official Amiri Press searchable-text endpoint for Decision 200 was attempted but returned HTTP 502. The alternate full text is therefore the LAW HUB transcription, with the original Gazette metadata independently corroborated by DSpace/Diwan and the earlier Amiri Press result.

### Complete provision coverage

| Instrument | Issuing provisions | Substantive / regulation provisions | Total full-text provisions | Text status |
|---|---:|---:|---:|---|
| Law 168/2025 | 4 | 14 | **18/18** | Complete searchable Arabic text captured |
| PM Decision 200/2026 | 4 | 20 | **24/24** | Complete searchable Arabic text captured |
| Presidential Decision 480/2026 | — | 2 operative articles | **2/2** | Both operative articles captured from independent reproductions |
| **Total** | | | **44/44** | Full text captured; original Gazette binaries still outstanding |

The new addendum in `alternate_source_text_recovery_law168_decision200_decision480_2026-11-18.md` adds 29 provisions not previously captured (12 Law 168 provisions and 17 Decision 200 provisions), and completes the previously partial Law 168 Article 5. Existing provisions were not repeated:
- Law 168/2025 existing capture: issuing Article 4 and substantive Articles 2, 3, 4, 6, 8.
- Decision 200/2026 existing capture: issuing Article 4 and Regulation Articles 3–7 and 9.
- Presidential Decision 480/2026: Articles 1 and 2 were already fully captured.
- The addendum now completes all 18 Law 168 and all 24 Decision 200 provision texts.

## 2. Gazette metadata and commencement

### Law 168/2025
- Gazette issue 32 bis (و), 13 August 2025.
- Issuing Article 4 states that the law operates after 30 days from publication.
- The corresponding date is **12 September 2025** (30 days after 13 August, excluding the publication date). This is an article-derived commencement calculation; final authentication should be made against the Gazette page and general statutory time-counting rule.
- Issuing Article 3 required the Prime Minister to issue the Executive Regulation within 30 days of publication. Decision 200 was not published until 18 January 2026, so the regulation was issued later than the 30-day target. The law's commencement and the regulation's commencement are separate events.

### PM Decision 200/2026
- Signed 18 January 2026; Gazette issue 3 bis (أ), 18 January 2026.
- Issuing Article 4 says it operates from the day after publication.
- Regulation commencement is therefore **19 January 2026**.
- Law 168 substantive Article 3 starts the six-month filing period from the date the Executive Regulation comes into force. The six-month period therefore starts from the 19 January 2026 commencement event.

### Presidential Decision 480/2026
- Signed 10 November 2026; Gazette issue 45 bis (ج), 10 November 2026.
- Article 1: "تمد المدة المشار إليها بالفقرة الأولى من المادة (3) من قانون بعض قواعد وإجراءات التصرف فى أملاك الدولة الخاصة الصادر بالقانون رقم 168 لسنة 2025، لمدة أخرى مماثلة."
- Article 2 directs publication.
- It does not state a new calendar start date or final deadline.

## 3. Final application deadline — remains legally unresolved

The following evidence is now cross-referenced against the full texts:
1. Law 168 Article 3: six months from commencement of the Executive Regulation.
2. Decision 200 issuing Article 4: commencement on 19 January 2026.
3. Cairo Governorate's official page, published 21 June 2026, says the initial final date was **18 July 2026**:
   https://www.cairo.gov.eg/ar/more/more/taqnen/
4. State Land Recovery Committee coordinator's Shorouk interview, 21 August 2026, says the initial period expired on 18 July 2026 and an additional six-month extension had been decided:
   https://www.shorouknews.com/news/view.aspx?cdate=21082026&id=1e7b4599-2221-4d95-b9b6-6a6c66e8866e
5. Presidential Decision 480 Article 1 extends the period for "another similar period", but does not specify the calendar endpoint.

**Two principal appended-period candidates:**
- If the operational administrative date 18 July 2026 is treated as the end of the first period, six further months would end **18 January 2027**.
- If the general corresponding-date calculation is applied to the 19 January 2026 regulation commencement, the first six-month period may end 19 July 2026 and the appended period may end **19 January 2027**.

The alternative interpretation that the six-month period starts afresh from Decision 480 publication (10 November 2026) would point to May 2027, but the committee-coordinator interview supports an appended extension after the July initial period. No official post-publication circular located in this pass fixes a new calendar deadline.

**Conclusion:** the most defensible administrative planning window is **18–19 January 2027**, but neither date is certified as the final legal deadline. The May 2027 interpretation should not be relied upon absent an authoritative written clarification. Request written clarification from the State Land Recovery Committee / competent land authority. For operational risk control, file before the earlier candidate, 18 January 2027.

## 4. Original PDF acquisition — additional routes tested

### Law 168/2025
- DSpace official bundle metadata: https://dspace.id.com.eg/items/8255632b-a2d4-44c3-9888-d4e2801e8d32/full — request-copy route; no bytes/hash.
- Diwan Al-Omran "original document PDF" link resolves to Google Drive file:
  https://drive.google.com/file/d/1zXxR0YWpJN_UcncUcO2Y8bmea-yQJF7p/view
- Google Drive preview returned a loading placeholder/sign-in page; no PDF bytes or pages obtained.

### PM Decision 200/2026
- DSpace official bundle metadata: https://dspace.id.com.eg/items/c8ee628f-2d7b-4f33-ab68-a68db8c99eb1/full — 1.89 MB original issue bundle identified; no bytes/hash archived.
- Diwan Al-Omran "original document PDF" link resolves to Google Drive:
  https://drive.google.com/file/d/10F3Jyb_I-QPFe3JZiqI1dm6tyviwagFo/view
- Google Drive preview returned a loading placeholder/sign-in page; no PDF bytes or pages obtained.
- Amiri Press text endpoint returned HTTP 502 in this pass.

### Presidential Decision 480/2026
- DSpace official bundle metadata: https://dspace.id.com.eg/items/03b3721d-4847-4be0-8130-5d4bf38da540/full — 178.37 KB original bundle identified; Download redirects to request-a-copy.
- Secondary reproductions from Al-Masry Al-Youm and other outlets contain both operative articles. No original PDF bytes/hash.

No access-control bypass was attempted. The Google Drive routes and DSpace request-copy paths are acquisition leads, not proof of permission or successful acquisition.

## 5. Register and inventory changes

- Updated FT-0009: Law 168/2025 now records all 18/18 provisions as searchable text captured.
- Updated FT-0010: Decision 200/2026 now records all 24/24 provisions as searchable text captured.
- Updated FT-0011: Decision 480/2026 records 2/2 operative articles captured.
- Updated acquisition records EG-0173, EG-0174 and EG-0175 with complete text coverage and exact outstanding original-PDF blockers.
- No new instrument records were added; no duplicate article text records were created.
- Permission fields remain unknown for all third-party mirrors and Google Drive file routes; commercial reuse permission remains unestablished.

## 6. Counts

| Metric | Count |
|---|---:|
| New provision texts added in this checkpoint's addendum | 29 |
| Existing partial provision completed | 1 (Law 168 Article 5) |
| Total full-text provisions now captured across these three instruments | **44** |
| Law 168/2025 full text | 18/18 |
| PM Decision 200/2026 full text | 24/24 |
| Presidential Decision 480/2026 operative text | 2/2 |
| Original Gazette PDF bytes locally archived in this checkpoint | 0 |
| SHA-256 hashes generated in this checkpoint | 0 |
| Lawyer verification | 0 |
| Commercial reuse permissions established | 0 |

## 7. Remaining work

1. Obtain the Law 168 and Decision 200 Google Drive PDFs through authorized access; compare all 44 provisions to Gazette page images and hash local files.
2. Obtain Decision 480 DSpace copy through request-copy and hash it.
3. Extract all attached forms and schedules to Decision 200; Article 6 refers to Form 1, Article 11 to Form 2, and Article 20 to Form 3.
4. Obtain written clarification of the Decision 480 extension endpoint, resolving 18/19 January 2027.
5. Check subsequent amendments to Law 168 and Decision 200 before deploying any live deadline or fee logic.
6. Do not claim lawyer verification or commercial reuse permission.
