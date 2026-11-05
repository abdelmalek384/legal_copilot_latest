# Labour Law 14/2025 — source comparison run (evidence only)

**Run date:** 2026-11-05  
**Scope:** candidate JSONL vs the user-supplied Gazette-copy PDF; no legal certification.

## Recovered source files

Both files were recovered from the user-provided root-level `untitled folder.zip` (the similarly named ZIP under `/legal/` remains inaccessible):

- Candidate: `law_rows_ar.jsonl` — SHA-256 `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600`.
- Reference: `العدد-18-تابع-مومن-1.pdf` — 112 pages; SHA-256 `b0a47cefe18722d3f23e004ac7e78e6e309010e13124413e7e7018820c9581be`.

The PDF cover identifies Official Gazette issue 18 (supplement), 3 May 2025. Its metadata reports encryption/owner copy restrictions, and the page images carry the watermark `صورة إلكترونية لا يعتد بها`. Treat it as a watermarked Gazette copy for comparison, not as proof of byte authenticity or permission to reproduce/reuse it.

Independent public locators found:
- Government-hosted PDF: https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf
- Amiri Press text page: https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D
- DSpace catalogue item, publisher listed as Amiri Press: https://dspace.id.com.eg/items/75a95151-8a93-45c0-a607-9320863881df

These locators corroborate the Gazette issue/title/date. They do not prove that the supplied PDF bytes came from those URLs or grant collection/commercial-reuse rights.

## Structural audit

Ran the repository's `tools/audit_article_rows.py` logic against the recovered JSONL:

- Rows: **311**; malformed JSON lines: **0**.
- Issuance provisions: **13**, numbered 1–13 with no gaps or duplicates.
- Attached law: **298**, numbered 1–298 with no gaps or duplicates.
- Exact duplicate article texts: **0**.
- Numeric cross-references beyond the highest article in each group: **0**.
- Text-quality findings: 4 rows without terminal punctuation.
- Orthography outliers: 6 (Arts. 66, 103, 124, 134, 141, 278).
- Quantity-bearing articles: **120**.
- Embedded flags: `verified=0` for all 311; `in_force=1` and `as_of=2025-05-03` for all 311. Those latter flags are not evidence of commencement/currentness; 3 May is the publication date.

## Automated text comparison

Ran the repository's `tools/compare_corpus_to_reference.py` against the 112-page PDF using `pdftotext -layout`:

| Result | Count |
|---|---:|
| Identical after normalization | 38 |
| Minor text difference | 221 |
| Major text difference | 47 |
| Numeric-token difference | 5 |
| Missing candidate rows | 0 |
| Extra candidate rows | 0 |
| Reference article headings detected | 311 |

The comparison aligned all 311 article labels, but the PDF text layer is disrupted by RTL layout and the repeated watermark. The tool itself warns that text extraction is not visual page review. Therefore the 268 minor/major flags are **unresolved extraction/comparison flags**, not confirmed legal-text discrepancies and not proof of a full 311-row match.

The five numeric-token flags (Arts. 21, 82, 124, 146, 298) were checked against rendered page images (PDF pages 18, 40, 54–55, 63, 111). The apparent differences are consistent with text-extraction/segmentation artifacts; no actual numeric mismatch was confirmed in those spot checks.

The six orthography-outlier locations were also visually inspected on the relevant page images (PDF pages 35, 48, 54–55, 57–58, 61–62, 106). No mismatch was confirmed in those spot checks. This does not replace a complete page-by-page review of all article text.

## Existing quantitative checklist

The Library file `quantity_checklist_partial_checked.csv` and its accompanying comparison report record **120/120** quantitative provisions visually checked, **0/120** pending, and no discrepancies among those checked provisions. This is an existing user-provided review record; this run did not independently repeat all 120 checks. It is source comparison only, not lawyer review.

## Disposition and remaining work

- Keep every JSONL `verified` flag at **0**.
- Keep the document's registry status at **discovery_only**; do not enable authoritative retrieval.
- Do not treat `in_force=1` or `as_of=2025-05-03` as legal-currentness evidence.
- No amendments/corrigenda/currentness review, reuse-rights determination, or Egyptian lawyer review has been completed.
- `tools/record_manual_capture.py` was not used to create a provenance record: the exact original download URL and individual who saved the PDF are not recorded in the supplied archive. Do not invent them. The government/Amiri Press URLs above are source locators, not asserted download origins.
- The remaining 268 text-comparison flags need targeted visual resolution against a clean, authorized source copy before anyone can claim all 311 article texts are source-matched.

**Conclusion:** the candidate's structure is clean and all 311 article labels align with the supplied Gazette-copy scan. The existing 120-item quantitative checklist is marked complete in the supplied review record. Full article-by-article textual matching, legal currentness, reuse permission, and lawyer approval remain incomplete. This result is **not verified and not lawyer-reviewed**.
