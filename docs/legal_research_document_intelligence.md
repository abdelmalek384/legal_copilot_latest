# Legal Research document-intelligence foundation

**Status:** Matter-scoped UI/API integration is implemented on the Figma refresh branch. Repository tests and live bilingual browser acceptance remain pending.

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
- PDF page provenance where a page marker exists; no invented page number for DOCX.
- Text comparison that reports literal changed spans and requires lawyer review.

## Safety boundaries

- Every classification and extracted item is a candidate requiring human review.
- No authenticity, legal validity, fraud, contradiction, deadline, or legal conclusion is inferred.
- No original file is modified.
- No OCR is performed.
- Signal extraction is bounded to the existing one-million-character extraction budget; pairwise text comparison is separately limited to 100,000 characters per version and 200 reported change segments.
- The Documents page lists only matters returned by the authenticated `/cases` endpoint and loads documents through the existing authorized case-detail route.
- Extraction review supports accept, correction and recheck decisions with a server-issued text digest, reviewer identity, note and timestamp in the audit trail.
- Saved document categories are matter workflow metadata. Only firm administrators and matter leads can change them; optimistic version checks prevent stale overwrites and each change creates an audit event.
- These workflows do not establish authenticity, legal validity or correctness. A saved category is not a legal conclusion.

## Next integration stages

1. Complete repository tests and add end-to-end tests for classification concurrency, reviewer roles, export, and cross-matter denial.
2. Perform manual RTL/LTR, keyboard, mobile and upload/review acceptance against a synthetic staging dataset.
3. Add page-linked original-document previews only where original retention and authorization are verified.
4. Implement firm-wide search only after a dedicated tenant-safe backend endpoint and query budgets exist.
5. Extend first-difference comparison to bounded multi-hunk comparison with explicit version provenance.
6. Evaluate with synthetic Arabic/English PDFs and DOCX fixtures before enabling for pilot users.

## Validation

Run: \`python -m unittest tests.test_document_intelligence -v\`

A passing unit suite validates helper behavior only; it does not validate the new API/UI, tenant isolation, production storage, or legal accuracy. The new contract tests have been added but were not run in this implementation session.
