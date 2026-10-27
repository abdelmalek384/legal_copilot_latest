# Uploaded document extraction limits

The case-document upload path accepts PDF and DOCX files only. The request is capped at 15 MB, PDFs are capped at 500 pages, DOCX archives are checked for expanded size, member count, unusually large entries and compression ratios, and extracted text is capped at 1,000,000 characters.

The text cap is enforced incrementally while PDF pages, DOCX paragraphs, table rows, headers and footers are extracted. If adding the next extracted block would exceed the budget, extraction stops with HTTP 413 instead of joining the entire document before checking its size.

PDF page markers are retained for page-aware citations. DOCX paragraphs and table rows preserve body order; headers and footers are added once when their text is repeated across sections.

## Remaining limits

- A single parser call may still allocate memory before returning an individual page or paragraph. Incremental output accounting is not a full parser sandbox.
- Keep document parsing libraries patched and run parsing in a process/container with CPU, memory, and wall-clock limits in production.
- Do not accept macro-enabled DOCM or arbitrary ZIP/XML files through this endpoint.
- OCR has separate page and image-processing costs; OCR output is also capped incrementally at 1,000,000 characters. Keep OCR bounded and treat OCR text as unverified until reviewed.
- A successful extraction only means text was extracted, not that it is complete, authentic, or legally accurate.
