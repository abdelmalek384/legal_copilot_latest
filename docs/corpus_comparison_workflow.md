# Comparing a candidate corpus with an official reference

This tool produces evidence for human review only; it never imports records or changes verification/currentness/in-force flags.

1. Obtain an authorized official reference. You may supply a UTF-8 text extraction or the original PDF. Record the source URL, Gazette issue/date, access date, and who obtained the file. Do not automate retrieval where source terms prohibit it.
2. Run `python tools/compare_corpus_to_reference.py --candidate law_rows_ar.jsonl --reference official_gazette.pdf --out-dir comparison_report`. Plain UTF-8 text remains supported. Add `--fail-on-difference` to return status 1 unless every aligned article matches after normalization.
3. Review the JSON and Markdown reports. The JSON includes every aligned article's detected PDF page range; the Markdown shows page ranges for flagged articles. Both reports retain the reference-file SHA-256 and extraction mode, and warnings identify pages with no extractable text. Prioritize numeric differences, major differences, missing/extra articles, then minor differences.
4. Verify every flagged passage against the rendered original page, not only extracted text. Scanned/image-only pages require OCR or manual transcription review; a page with no extracted text is explicitly warned.
5. Preserve report hashes and the lawyer's decision in the legal review record.

Candidate JSONL uses one object per line with `article` (or `label`) and `text` (or `body`). Repeated labels are aligned by occurrence order to distinguish promulgation articles from body articles.

Normalization is limited; number-word checks may produce false positives. PDF text extraction is not visual inspection, OCR validation, source authentication, legal-status or amendment-completeness review, or proof of reuse permission. A clean report cannot certify legal accuracy. Human and qualified-lawyer review remain mandatory.
