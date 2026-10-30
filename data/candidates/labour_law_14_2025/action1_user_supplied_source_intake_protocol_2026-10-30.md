# Action 1 — user-supplied primary-source intake protocol

**Prepared:** 2026-10-30  
**Expected user input:** original Official Gazette PDF for Decisions 248–252/2026 (especially Decision 250), and law_rows_ar.jsonl if available.  
**Purpose:** Be ready to process the files when the user supplies them; do not wait for third-party permission correspondence and do not bypass restricted repositories.

## 1. Expected inputs

1. Original Official Gazette / Egyptian Proceedings Supplement 225(A), dated 12 October 2026, containing Ministry of Labour Decisions 248, 249, 250, 251 and 252 of 2026. Expected catalog identity:
   - DSpace record: https://dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full
   - Publisher: المطابع الأميرية
   - Original bundle metadata: العدد 225 تابع أ - مؤمن.pdf, 6.13 MB
2. The user's original law_rows_ar.jsonl, if available. Historical identity from the user's earlier local audit:
   - SHA-256: 3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600
   - Size: 393,861 bytes
   - Expected records: 311 (13 promulgation provisions + 298 articles)
   - The historical hash/size/count are comparison targets only; re-hash the actual supplied bytes.

## 2. Intake safety

- Preserve every supplied file byte-for-byte as the immutable original.
- Do not overwrite, rename internally, normalize, OCR-correct, or edit the original.
- Record the actual filename, MIME/type, byte size, supplied timestamp, and SHA-256.
- Confirm the PDF's printed Gazette issue/date and that all five expected decisions are present before relying on any page map.
- Record both PDF zero-based page index and printed Gazette page number; do not assume the secondary page map is correct.
- If the supplied PDF differs from the catalog bundle, treat it as a distinct source version and preserve both identities.
- Do not upload private client material or secrets into this public legal corpus branch.
- Do not treat the user's provision of a file as a blanket commercial reuse opinion. The underlying official-document Article 141 route, scan/compilation distinctions, source-use review and counsel gate remain separate.

## 3. Gazette PDF execution order

1. Verify identity and hash.
2. Extract PDF metadata/page count and build a printed-page-to-PDF-index map.
3. Locate exact start/end pages for Decisions 248–252 and all annexes, tables, forms, footnotes and transition clauses.
4. Compare Decision 248 Articles/forms against the Article 260 parent-law cross-reference, including inside/outside accident and symptom/diagnosis triggers.
5. Compare Decision 249 Articles 1–22 and Tables 1–3; prioritize Table 2 staffing cells and Table 3 pollutant combinations.
6. Compare Decision 250 Table 23 (137 candidates) and Table 24 (781 flattened candidates, including nested child rows); prioritize known CAS/formula/decimal/unit anomalies, high-risk substances, surface limits, footnotes and removed/blank entries.
7. Compare Decision 251 licensing conditions, qualifications, exceptions, fees and transition clauses.
8. Compare Decision 252 training-provider licensing, programme hours, facilities, fees, pass/attendance rules, exemptions and transition clauses.
9. Populate per-row/per-clause official match outcomes and exact page pinpoints; preserve raw candidate data and record mismatches separately.
10. Run all legal-knowledge and full Tests workflows. A successful test does not itself approve a legal rule.

## 4. law_rows_ar.jsonl execution order

1. Re-hash supplied bytes and compare with the historical SHA-256 above.
2. Parse every JSONL line; record malformed lines and schema drift without silently repairing the original.
3. Confirm the expected 311 records / 13 issuance provisions / 298 law articles.
4. Compare each candidate article against the government-hosted ETA Official Gazette PDF and the official Amiri Press searchable text route, recording exact source pinpoints and field-level diffs.
5. Prioritize numeric, missing, extra, major-text and known spelling outliers.
6. Preserve Gazette spelling in the source text; keep Arabic search normalization in a separate derived field.
7. Do not replace the user's original file with a regenerated or secondary-source substitute.

## 5. Release boundaries

- Official-source match, currentness, source-use, qualified counsel approval and retrieval eligibility remain separate gates.
- A page match does not prove currentness.
- A file hash proves file identity, not legal accuracy.
- A complete 781-row Table 24 transcription does not prove any exposure value.
- Do not activate a decision or numerical rule in authoritative retrieval until its exact evidence and release gates pass.

## 6. Lawyer acceptance timing

The in-app lawyer review is a separate acceptance gate **after technical completion**, not a prerequisite to continuing source ingestion and engineering. The lawyer should test the actual app build and corpus version, with exact prompts from lawyer_in_app_acceptance_plan_2026-10-29.md; record only the scope actually examined and approved. No legal approval is assumed in this intake protocol.
