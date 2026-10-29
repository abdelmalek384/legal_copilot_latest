# Law 14/2025 — 311-row reconciliation execution record

**Updated:** 2026-10-29
**Current status:** Not executed against the actual candidate rows. The row-by-row comparison remains blocked by missing runtime artifact access, not by absence of a public reference text.

## Candidate artifact identity

- Filename: `law_rows_ar.jsonl`
- Previously inspected local path from the user's environment: `/Users/abdelmalekmohamed/Downloads/copilot/law_rows_ar.jsonl` (the same file was previously located under `/Users/abdelmalekmohamed/Downloads/law_rows_ar.jsonl`).
- Recorded SHA-256 of the supplied JSONL: `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600`.
- Recorded size: 393,861 bytes; 311 valid records; 13 promulgation provisions and 298 law articles; 0 malformed lines.
- Access state for this work session: that path is on the user's Mac and is not mounted in this execution environment; the file is intentionally absent from the public repository while source-use scope remains under review. The hash is a historical identifier, not proof that the current unavailable bytes were re-hashed in this session.

## Official reference route

- Government-hosted Official Gazette PDF: https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf
- Official Amiri Press searchable text: https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D
- Official Gazette issue metadata: https://dspace.id.com.eg/items/75a95151-8a93-45c0-a607-9320863881df
- Browser PDF text extraction: 110 pages / 2,728 text lines; selected articles have line ranges in numerical ledger batches 1–7.
- Targeted rendered-page visual checks completed for PDF indices 33, 46, 52, 56, 59 and 104 (printed Gazette pages 35, 48, 54, 58, 61 and 106).
- Two ordinary public download attempts (ETA portal and SIS-hosted URL) failed. No original PDF bytes or SHA-256 were obtained; no request-a-copy workflow was bypassed.

## What is complete

- Candidate JSONL was previously audited locally for structure and count; this session did not re-read its rows.
- 120/120 numerical candidate slots now have article/page/text-line evidence entries across seven batches. This is 100% checklist coverage by count, not source matching.
- Six flagged articles have official PDF page locators and targeted rendered-page visual checks.
- Implementing-instrument discovery now includes 19 Gazette-indexed or official-text leads, including Prime Minister's Decree 3165/2026 and Labour Ministry Decisions 248–252/2026.

## What remains blocked or incomplete

1. **311-row comparison:** cannot execute without the actual JSONL bytes. Do not regenerate a substitute from a secondary webpage and call it the original file.
2. **Six exact spelling outliers:** official pages are located and rendered; the six candidate row strings are unavailable, so no exact side-by-side result is claimed.
3. **Original PDF hash / full visual inspection:** no downloaded official PDF bytes; only browser text extraction and six rendered page spot-checks.
4. **Currentness/corrigenda:** targeted discovery only. Issue 108's archive includes a file named `تنويه 108.pdf`, but it is restricted to a request-a-copy workflow; its content and relevance to Decisions 74/75 are unknown. Newer instruments 248–252/2026 are archive metadata leads, not fully reviewed texts.
5. **Rights and lawyer review:** Article 141 of Egyptian IP Law No. 82/2002 is a promising official-document exclusion lead, but current law/source-access terms and intended commercial use need qualified Egyptian-counsel confirmation.
6. **Authoritative retrieval:** remains disabled. No candidate is marked lawyer-approved or verified-current.

## Next exact execution step when the candidate file is available in the session

1. Hash the supplied JSONL bytes and compare to the recorded SHA-256 above.
2. Run `python tools/compare_corpus_to_reference.py --candidate law_rows_ar.jsonl --reference official_reference.txt --out-dir comparison_report` against an independently captured official-text reference whose acquisition route and intended use are documented.
3. Save comparison JSON/Markdown, reference hash, candidate hash, and per-article status. Manually resolve numeric/major/missing/extra differences first.
4. Compare Arts. 66, 103, 124, 134, 141 and 278 character-by-character against rendered official pages; preserve Gazette spellings in source text and place search-normalized forms in a separate derived field.
5. Keep all rows pending source match/currentness/reuse/counsel review until the corresponding evidence gates pass.