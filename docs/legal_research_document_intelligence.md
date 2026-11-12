# Legal Research document-intelligence foundation

**Status:** Initial pure-Python analysis helpers added; not yet wired into the lawyer-facing UI or upload route.

## Existing repository capabilities

The application already accepts bounded PDF and DOCX uploads, extracts PDF text with \`[[PDF_PAGE:n]]\` markers, extracts DOCX body paragraphs and tables, enforces upload/page/expanded-archive/text budgets, links extracted chunks to matter document IDs, and has tenant-scoped original-file storage/recovery code. See:

- \`docs/document_extraction_limits.md\`
- \`docs/firm_document_ingestion_provenance.md\`
- \`docs/tenant_file_storage_design.md\`

## New foundation in \`tools/document_intelligence.py\`

- Transparent keyword-based document-type candidates.
- Exact-byte SHA-256 and whitespace-normalized extracted-text digests (separate purposes).
- Literal candidate extraction for dates, case references, amounts and explicitly labelled parties.
- PDF page provenance where a page marker exists; no invented page number for DOCX.
- Text comparison that reports literal changed spans and requires lawyer review.

## Safety boundaries

- Every classification and extracted item is a candidate requiring human review.
- No authenticity, legal validity, fraud, contradiction, deadline, or legal conclusion is inferred.
- No original file is modified.
- No OCR is performed.
- Inputs are bounded to the existing one-million-character extraction budget.
- These helpers do not bypass firm/case authorization and are not yet exposed as a user-facing feature.

## Next integration stages

1. Add authenticated matter-scoped API endpoints that call the helpers only after existing authorization checks.
2. Persist user-approved classifications and reviewer corrections with audit events.
3. Add searchable UI filters and page-linked document previews.
4. Add duplicate grouping within the same firm/matter only; never deduplicate across firms.
5. Add robust version comparison and chronological event review.
6. Evaluate with synthetic Arabic/English PDFs and DOCX fixtures before enabling for pilot users.

## Validation

Run: \`python -m unittest tests.test_document_intelligence -v\`

A passing unit suite validates helper behavior only; it does not validate upload integration, UI, tenant isolation, production storage, or legal accuracy.
