# Collection checkpoint 193 — Decision 200/2026 official Gazette PDF, attached forms and Article 20 discrepancy

**Date:** 18 November 2026  
**Agent:** Research Agent 1

## 1. Official government-hosted Gazette PDF located and opened

The full Gazette issue PDF is directly accessible from the Egyptian State Information Service (SIS) digital repository:

https://mediadr.sis.gov.eg/xmlui/bitstream/handle/123456789/118973/OG3_20260118_2885.pdf?isAllowed=y&sequence=2

- PDF title: الجريدة الرسمية — العدد ٣ مكرر (أ) في ١٨ يناير سنة ٢٠٢٦.
- PDF text extraction: 562 lines.
- The opening page identifies the Republic of Egypt, Presidency, Official Gazette, issue 3 bis (أ), dated 18 January 2026.
- It contains the full issuing decision, all 20 Executive Regulation articles and attached Forms 1, 2 and 3.
- This is an **official government-hosted full-issue Gazette PDF** and materially upgrades the source evidence beyond a DSpace metadata record or a secondary transcription.
- The Amiri Press DSpace item separately identifies a 1.89 MB original issue bundle but remains request-copy only.
- Attempts to download the SIS PDF bytes into the research environment failed. The PDF was opened and text-extracted, but no local binary or SHA-256 hash has been archived. Do not claim a local download or hash.

## 2. Attached forms captured as actual text

Created:
`pm_decision_200_2026_forms_1_2_3_full_text_capture_2026-11-18.md`

The official Gazette PDF contains:
- **Form 1:** two variants — application for regularization of possession of reclaimed/cultivated land and application for built-up land. Both forms include applicant identity, address/notification, land location/area/use/boundaries, WGS84 coordinate tables, supporting attachments, declaration and signature fields.
- **Form 2:** inspection report, including committee member details, land description, WGS84 coordinates, conformity findings and committee signatures.
- **Form 3:** quarterly report ("تقرير ربع سنوي") with 25 reporting fields, including application volumes, fees, inspections, approvals/rejections, grievances, contracts, removals, recovered parcels, criminal reports and amounts collected.

The forms are transcribed structurally with blank fields and tables preserved as templates. No new numbered legal article is added to the 44-provision count.

## 3. Critical discrepancy — Executive Regulation Article 20 versus Form 3 and Law 168 Article 14

The official SIS PDF's text layer at lines 263–268 renders Executive Regulation Article 20 as:

"تلتزم الجهة الإدارية المختصة بإعداد تقارير سنوية عن موقف طلبات التقنين المقدمة إليها..."

This says **annual reports** ("سنوية").

However:
- Form 3 in the same official Gazette PDF is explicitly titled **"تقرير ربع سنوي"** (quarterly report).
- Law 168/2025 substantive Article 14 says the competent authority prepares **quarterly reports** ("تقارير ربع سنوية").
- LAW HUB's secondary transcription of Decision 200/2026 also says Article 20 is quarterly, not annual.

The official PDF's page-image screenshot endpoint failed with a restricted-URL error for the page containing Article 20, so the word "سنوية" has not been visually verified against the page image. This may be an OCR omission of "ربع", a Gazette drafting inconsistency, or a secondary transcription correction. **Do not silently harmonize the texts.**

Repository treatment:
1. Preserve the official SIS PDF text-layer wording "سنوية" as the extracted Gazette source string.
2. Preserve the LAW HUB alternative wording "ربع سنوية" as a separate secondary-source variant.
3. Preserve Form 3's quarterly title.
4. Preserve Law 168 Article 14's quarterly requirement.
5. Add an unresolved internal inconsistency flag; obtain a visual page image or official Amiri Press clarification/corrigendum before deciding the operative reporting cadence.

## 4. Forms and original Gazette acquisition status

- Decision 200/2026: official SIS-hosted full-issue Gazette PDF opened; full text and forms captured. Local PDF bytes/hash not archived. Separate Amiri Press DSpace original bundle remains request-copy only.
- Law 168/2025: VetoGate-hosted 20-page Gazette scan reproduction opened. It identifies issue 32 bis (و), 13 August 2025; Law 168/2025 appears on printed pages 3–10, followed by Law 169/2025. The scan carries a notice that the electronic copy is not valid for circulation. It is not the authenticated Amiri Press digital binary. DSpace original bundle remains request-copy only; Diwan Al-Omran Google Drive original-PDF preview shows a loading/sign-in placeholder.
- Presidential Decision 480/2026: DSpace official bundle is 178.37 KB by metadata, but Download redirects to request-a-copy; no local bytes/hash. Two operative articles are captured from independent media reproductions.

## 5. Register updates

- Source-permission record EG-SIS-GAZETTE-2026-01-18 remains collection_permission=unknown and commercial_reuse_permission=unknown; access status records official SIS PDF opened, 562 lines, no local bytes/hash.
- Source-permission record EG-VETOGATE-GAZETTE-168-2025 remains rights unknown; scan notice and secondary-host status retained.
- Full-text inventory FT-0010 now records the official SIS full-issue PDF and all three forms as text-captured; only local bytes/hash, page-image visual verification and Article20 discrepancy resolution remain.
- Acquisition record EG-0174 now distinguishes official SIS PDF text access from the separate DSpace Amiri Press request-copy bundle.
- No new instrument or numbered article provision is added. The total remains 44/44 full-text provisions for Law 168/2025, Decision 200/2026 and Decision 480/2026.

## 6. Remaining actions

1. Obtain a locally archivable SIS PDF through an authorized route and calculate SHA-256; preserve the URL and access timestamp.
2. Obtain the Amiri Press DSpace bundle through request-copy if an authenticated publisher binary is required.
3. Obtain a visual page image for Article 20 to determine whether the Gazette page itself says "سنوية" or "ربع سنوية".
4. Seek an official correction/circular from the competent authority if the discrepancy is real.
5. Preserve the annual/quarterly source variants in the legal database until resolved.
6. No lawyer verification, commercial reuse permission or redistribution permission is claimed.
