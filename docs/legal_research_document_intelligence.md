# Legal Research document-intelligence foundation

**Status:** Matter-scoped and permission-filtered cross-matter UI/API integration is merged into main via PR #1582. Repository tests and live bilingual browser acceptance remain pending.

## Existing repository capabilities

The application already accepts bounded PDF and DOCX uploads, extracts PDF text with \`[[PDF_PAGE:n]]\` markers, extracts DOCX body paragraphs and tables, enforces upload/page/expanded-archive/text budgets, links extracted chunks to matter document IDs, and has tenant-scoped original-file storage/recovery code. See:

- \`docs/document_extraction_limits.md\`
- \`docs/firm_document_ingestion_provenance.md\`
- \`docs/tenant_file_storage_design.md\`

## New foundation in \`tools/document_intelligence.py\`

- Transparent keyword-based document-type candidates with explicit matched terms and non-probabilistic signal labels.
- Exact-byte SHA-256 and whitespace-normalized extracted-text digests (separate purposes).
- Possible-duplicate grouping constrained to identical firm and matter IDs; byte-identical and text-identical matches are distinguished and still require human review.
- Literal candidate extraction for dates, case references, amounts and explicitly labelled parties.
- A date-mention review timeline that retains document/page provenance, parses valid four-digit-year dates using explicit day-first or ISO rules, and refuses to guess two-digit years or invalid dates.
- Structured candidate records for labelled parties, case/legal references, amounts and date mentions; sentence-scoped event triggers linked only to dates/labelled parties in that same sentence; and explicit Arabic/English relationship phrases. Every record retains character offsets and available page/chunk provenance and remains unverified.
- Matter-wide date/event mention index over authorized documents, sorted parseable dates and unparsed mentions, with chunk/page provenance and strict document/character/result caps.
- PDF page provenance where a page marker exists; no invented page number for DOCX.
- Text comparison that reports literal changed spans and requires lawyer review.

## Safety boundaries

- Every classification and extracted item is a candidate requiring human review.
- No authenticity, legal validity, fraud, contradiction, deadline, or legal conclusion is inferred.
- No original file is modified.
- No OCR is performed.
- Signal extraction is bounded to the existing one-million-character extraction budget; pairwise text comparison is separately limited to 100,000 characters per version and 200 reported change segments.
- The Documents workspace uses authenticated, paginated matter selection and permission-filtered `/documents/search` and `/documents/search-text` endpoints. Metadata and extracted-text search are firm-scoped and restricted to administrator-visible matters or matters where the current user is a member. Results preserve document/chunk/page provenance.
- Extraction review supports accept, correction and recheck decisions with a server-issued text digest, reviewer identity, note and timestamp in the audit trail.
- Saved document categories are matter workflow metadata. Only firm administrators and matter leads can change them; optimistic version checks prevent stale overwrites and each change creates an audit event.
- These workflows do not establish authenticity, legal validity or correctness. A saved category is not a legal conclusion.

## Current implementation and next stages

### Merged in PR #1582

1. Figma-aligned responsive Legal Research shell, source inspector and explicit source-verification warnings.
2. Documents workspace with permission-filtered accessible library, paginated metadata search, Arabic/English extracted-text search, file/status/classification filters, and matter context.
3. Multi-file PDF/DOCX upload with per-file progress, CSRF protection, file-size/type checks, keyboard-accessible drop zone, and original-file availability/download handling.
4. Persistent document classification with lead/admin-only writes, optimistic version checks, reviewer identity, immutable audit events, and tenant/matter scope triggers.
5. Extracted-text review with accept, recheck and correction outcomes, SHA-256 compare-and-swap, reviewer notes, bounded history, and separate original/corrected text display.
6. Original-file legal-hold and deletion-request APIs were already present in the application; the workspace exposes original availability without claiming a binary is retained when the private-storage record does not confirm it.

### Remaining repository work

1. PR #1591 exposes bounded multi-hunk comparisons between original and corrected extraction passages in the chunk-review workflow. PR #1592 adds cross-document version comparison: `GET /documents/compare` accepts two document IDs only within one authorized matter, assembles extracted text in stored chunk order, returns bounded literal hunks plus chunk/page provenance for both versions, and records a coarse security audit event. The Documents workspace now calls this API instead of generating a local first/last-difference approximation. API and frontend contract regressions are merged; runtime execution and browser acceptance remain pending.
2. Expand structured extraction beyond the new conservative rule-based candidates with reviewed bilingual entity-resolution, aliases, cross-document identity linking, event argument roles and explicit relationship normalization. Do not infer a relation from co-occurrence; retain provenance and human-review state.
3. Evaluate Arabic/English PDF and DOCX fixtures, including scanned PDFs, malformed documents, large files, duplicate documents and mixed-language content. OCR remains disabled in this helper foundation.
4. Add end-to-end tests for upload, download, classification concurrency/role enforcement, extraction review, search pagination, firm switching and cross-firm denial.
5. Perform manual Arabic RTL, English LTR, keyboard-only, screen-reader, mobile and desktop browser acceptance against a synthetic staging dataset.
6. Consider richer page-linked original-document previews only where original retention, legal-hold state and authorization are verified. Do not infer original-file availability from extracted text.
7. Evaluate multi-document synthesis only after evidence provenance, conflict handling, source verification and counsel review criteria are defined; summaries must not turn candidate facts into verified legal conclusions.

## Validation

Run: \`python -m unittest tests.test_document_intelligence -v\`

A passing unit suite validates helper behavior only; it does not validate the new API/UI, tenant isolation, production storage, or legal accuracy. The new contract tests have been added but were not run in this implementation session.

## Structured candidate extraction implementation — 2026-11-13 (merged #1594)

- Added `extract_structured_candidates` to `tools/document_intelligence.py`. It emits labelled-party and literal identifier/amount/date entities, event-trigger records with same-sentence date/party mentions, and relationships only when an explicit Arabic or English relation phrase is present.
- Integrated the structured records into the existing authorized `GET /cases/{cid}/docs/{document_id}/chunks` response. Each record receives document ID, chunk ID/reference and page where available; per-kind output is bounded to 250 records.
- Added an Arabic/English structured-candidate section to the Legal Research workspace, displaying source metadata and unverified status.
- Added helper tests, separate-database API provenance assertions, and frontend contract coverage. PR #1594 merged at `600dea925d95f8bccdec79dad9157a4aec78a1e0`; tests remain unexecuted because the Actions runner/billing problem remains.
- This is rule-based candidate structuring, not general NER, event verification, entity resolution or legal relationship analysis. OCR/extraction mistakes may propagate into every candidate.

## Matter-wide date and event index — 2026-11-13 (branch pending merge)

- Added `GET /cases/{cid}/documents/timeline`, which first authorizes the matter and then reads only documents matching that case and active firm.
- The endpoint processes at most 200 documents and one million extracted characters, returns at most 1,000 date mentions and 500 event candidates, and records a security audit event.
- Date records preserve document, chunk, reference, page and character offsets; event candidates retain the trigger, same-sentence date/party mentions and source chunk/page.
- The Documents workspace adds a server-backed matter-wide timeline control, separating parseable dates, unparsed dates and event mentions. The warning states that this is not a verified chronology and does not create deadlines.
- Added helper/API/frontend contract tests. Tests and browser acceptance are not executed; branch `feature/matter-document-timeline-20261113` is pending merge.
