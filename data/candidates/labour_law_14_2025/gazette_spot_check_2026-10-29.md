# Labour Law No. 14 of 2025 — Gazette spot-check log

**Checked:** 2026-10-29  
**Scope:** Source locator verification for six articles previously flagged for spelling/text comparison: 66, 103, 124, 134, 141 and 278. This is a targeted spot-check, not a 311-row reconciliation or lawyer approval.  
**Retrieval eligibility:** No change. All evidence cards remain `search_eligible: false`.

## Sources used

1. **Primary source:** Government-hosted Official Gazette PDF, *الجريدة الرسمية، العدد 18 (تابع)، 3 مايو 2025*, Law No. 14 of 2025. URL: https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf
2. **Independent official-publisher text page:** Amiri Press, Law No. 14 of 2025. URL: https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D (the page was indexed by search, but direct open returned HTTP 502 during this check).
3. **Public secondary transcription for fallback comparison:** Wikisource, “قانون العمل 14 لسنة 2025 - مصر”. URL: https://ar.wikisource.org/wiki/قانون_العمل_14_لسنة_2025_-_مصر
4. **Additional secondary transcription:** Law Hub, Law No. 14 of 2025. URL: https://lawhub.info/eg/?p=11848

## Official Gazette locator checks

The Gazette PDF text layer was opened around each article heading. These checks confirm the article heading and its printed-page locator in the PDF text extraction; they do **not** certify that the local 311-row JSONL text matches every character.

| Article | Gazette printed page | PDF zero-based page index | Evidence seen in extracted text | Status |
|---:|---:|---:|---|---|
| 66 | 35 | 33 | Heading “مادة (٦٦)” and the employer duties concerning employed children appear at PDF text lines around 803–813. | Locator confirmed; character-level comparison to JSONL blocked because that file is not in this branch. |
| 103 | 49 | 46 | Heading “مادة (١٠٣)” and the National Council for Wages meeting/quorum provision appear around lines 1141–1145. | Locator confirmed; character-level comparison to JSONL blocked. |
| 124 | 54 | 52 | Heading “مادة (١٢٤)” and annual-leave entitlements, including the seven-day increase for specified hazardous/unhealthy/remote work, appear around lines 1292–1304. | Locator confirmed; related Decree 49/2026 still requires full-text review before eligibility decisions are made. |
| 134 | 58 | 56 | Heading “مادة (١٣٤)” and worker duties appear around lines 1371–1391. | Locator confirmed; character-level comparison to JSONL blocked. |
| 141 | 62 | 60 | Heading “مادة (١٤١)” and disciplinary investigation/time-limit language appear around lines 1468–1478. | Locator confirmed; character-level comparison to JSONL blocked. |
| 278 | 107 | 104 | Heading “مادة (٢٧٨)” and attendance-request compliance provision appear around lines 2597–2600. | Locator confirmed; character-level comparison to JSONL blocked. |

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
