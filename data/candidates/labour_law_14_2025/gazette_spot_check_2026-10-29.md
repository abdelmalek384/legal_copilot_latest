# Labour Law No. 14 of 2025 — Gazette spot-check log

**Checked:** 2026-10-29  
**Scope:** Source locator verification for six articles previously flagged for spelling/text comparison: 66, 103, 124, 134, 141 and 278. This is a targeted spot-check, not a 311-row reconciliation or lawyer approval.  
**Retrieval eligibility:** No change. All evidence cards remain `search_eligible: false`.

## Sources used

1. **Primary source:** Government-hosted Official Gazette PDF, *الجريدة الرسمية، العدد 18 (تابع)، 3 مايو 2025*, Law No. 14 of 2025. URL: https://eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf
2. **Independent official-publisher text page:** Amiri Press, Law No. 14 of 2025. URL: https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D (the page was indexed by search, but direct open returned HTTP 502 during this check).
3. **Public secondary transcription for fallback comparison:** Wikisource, “قانون العمل 14 لسنة 2025 - مصر”. URL: https://ar.wikisource.org/wiki/قانون_العمل_14_لسنة_2025_-_مصر
4. **Additional secondary transcription:** Law Hub, Law No. 14 of 2025. URL: https://lawhub.info/eg/?p=11848

## Official Gazette locator checks

The Gazette PDF text layer was opened around each article heading. These checks confirm the article heading and its printed-page locator in the PDF text extraction; they do **not** certify that the local 311-row JSONL text matches every character.

| Article | Gazette printed page | PDF zero-based page index | Evidence seen in extracted text | Status |
|---:|---:|---:|---|---|
| 66 | 35 | 33 | Heading “مادة (٦٦)” and the employer duties concerning employed children appear at PDF text lines around 803–813. | Locator confirmed; character-level comparison to JSONL blocked because that file is not in this branch. |
| 103 | 48 | 46 | Heading “مادة (١٠٣)” and the National Council for Wages meeting/quorum provision appear around lines 1141–1145. | Locator confirmed; character-level comparison to JSONL blocked. |
| 124 | 54 | 52 | Heading “مادة (١٢٤)” and annual-leave entitlements, including the seven-day increase for specified hazardous/unhealthy/remote work, appear around lines 1292–1304. | Locator confirmed; related Decree 49/2026 still requires full-text review before eligibility decisions are made. |
| 134 | 57 | 55 | Heading “مادة (١٣٤)” and worker duties appear around lines 1371–1391. | Locator confirmed; character-level comparison to JSONL blocked. |
| 141 | 61 | 59 | Heading “مادة (١٤١)” and disciplinary investigation/time-limit language appear around lines 1468–1478. | Locator confirmed; character-level comparison to JSONL blocked. |
| 278 | 106 | 104 | Heading “مادة (٢٧٨)” and attendance-request compliance provision appear around lines 2597–2600. | Locator confirmed; character-level comparison to JSONL blocked. |

**Important page-numbering note:** The PDF index is zero-based; the printed Gazette page is the number shown in the document. Do not treat the PDF index as the printed page.

## What this resolves — and what it does not

- Resolves the immediate risk that the six flagged article pinpoints were merely guessed: the article headings are present at the listed Gazette printed pages in the official PDF text extraction.
- Does **not** resolve whether the six spelling outliers are transcription errors. The actual outlier strings and their corresponding rows from `law_rows_ar.jsonl` are not in this public branch, so a true side-by-side comparison cannot be made from this checkout.
- Does **not** establish a binary SHA-256 for the Gazette PDF. A web text extraction is not the original PDF byte stream; no PDF hash is claimed.
- Does **not** constitute visual inspection of every page, full article-by-article comparison, legal currentness certification, reuse permission, or Egyptian-lawyer review.
- The PDF text extraction itself can normalize/reorder Arabic glyphs and digits. Any exact spelling judgment must use the rendered Gazette page or a locally downloaded, hashed original file.

## Next comparison procedure — no source-access bypass required

1. Obtain the 311-row JSONL from the existing local artifact (or rebuild a fresh comparison copy from a source whose reuse terms permit it); do not publish the original JSONL until redistribution/commercial rights are cleared.
2. Download the government-hosted PDF through its ordinary public link, retain the unmodified original, and record retrieval timestamp, byte size, and SHA-256 locally.
3. Compare each record's article identifier and text against the corresponding Gazette page; record each difference as `exact_match`, `whitespace_only`, `OCR_or_extraction_uncertain`, `substantive_mismatch`, or `not_checked`.
4. For the six spelling outliers (Arts. 66, 103, 124, 134, 141, 278), record the exact source string and proposed JSONL string side by side. Preserve Gazette orthography in the source layer; put normalized search text in a separate derived field.
5. Review all 120 numeric provisions against the rendered Gazette pages, with a separate row for each amount, percentage, duration, threshold, age, deadline, or cross-reference. Do not mark a row complete based only on a secondary transcription or an OCR string.
6. Keep `verified`, `in_force`, and `search_eligible` false until the source match, currentness/reuse review, and qualified Egyptian-lawyer review gates are met.

## Current blocker and lawful fallback

The missing `law_rows_ar.jsonl` is deliberately not distributed in the repository while its source storage, redistribution and commercial reuse terms remain unresolved. Do not bypass website access controls or copy restricted material. Use the publicly accessible official Gazette PDF as the primary comparison source, the Amiri Press text page as a second official-source lead when reachable, and Wikisource/Law Hub only as secondary cross-checks. If a full official implementing decision is not publicly available, record it as unresolved rather than infer its operative text from a press announcement.

## Status

**Partial progress:** six article/page locators now have official-PDF text-layer support.  
**Still blocked:** the six exact spelling comparisons, all 311 JSONL-to-Gazette comparisons, the 120-item numeric checklist, original-PDF SHA-256, full currentness/reuse review, and qualified lawyer sign-off.  
**Safety:** no card is activated by this log.


## Additional official-hosted PDF cross-check — 2026-11-02

A second official-hosted copy was located through the Egyptian Tax Authority legislation index. The index links directly to the 110-page PDF:

- Egyptian Tax Authority: https://eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf
- State Information Service: https://sis.gov.eg/media/760267/القانون-رقم-14-لسنة-2025-بإصدار-قانون-العمل.pdf

Both are government-hosted copies of the Official Gazette issue 18 (تابع), 3 May 2025. Their web PDF text layers expose the six targeted article locations. This is an additional official-hosted source cross-check, not proof that either PDF's bytes are identical to the other.

### Article 103 — text-layer discrepancy and ETA page-image check

The ETA-hosted PDF page image (PDF index 46; printed Gazette page 48) was visually inspected in the public PDF viewer. It visibly reads **"كل ستة أشهر على الأقل"**, with no intervening word "سنة". This confirms the wording shown in the ETA rendered page and supports the provisional Article 103 summary in the card inventory.

However, the SIS-hosted PDF text layer around the same provision includes **"كل سنة ستة أشهر على الأقل"**. One search-indexed extraction of the ETA PDF also returns the extra word "سنة", even though the rendered ETA page image does not show it. This points to an extraction/OCR-layer discrepancy; the SIS page image remains unavailable for visual inspection. Do not treat the extracted extra word as definitive statutory wording.

**Disposition:** The ETA page-image wording is visually confirmed. Keep the text-layer discrepancy documented until the SIS page image can be checked. This does not establish an amendment or change the legal status of the Law.

### Cross-check scope and limitations

- The ETA-hosted PDF page images were visually inspected for all six target provisions: Article 66 at printed page 35 / PDF index 33; Article 103 at page 48 / index 46; Article 124 at page 54 / index 52; Article 134 at page 57 / index 55; Article 141 at page 61 / index 59; and Article 278 at page 106 / index 104.
- The SIS PDF text layer independently exposes the same six article locators, but its rendered page images were not visually checked in this session.
- The ETA and SIS URLs are public viewing links. This check does not establish binary equality, original-file SHA-256, systematic reuse permission, amendment completeness, or qualified-counsel approval.
- The missing 311-row `law_rows_ar.jsonl` and 120-item numeric checklist are still not present in the Library or repository checkout inspected. No full candidate-to-Gazette comparison is claimed.
- All Labour Law cards remain `search_eligible: false`; no verification or release gate is changed.

### Immediate next action

Obtain or open the SIS-hosted page image corresponding to printed page 48 / PDF index 46 through the ordinary public viewer or an authorized local copy. Compare the visible Article 103 wording with the ETA page image, record each PDF's SHA-256 only after obtaining its actual bytes, and then compare the resolved wording with the candidate article row when that row is available. Keep the cross-copy discrepancy open if the SIS image remains inaccessible.
