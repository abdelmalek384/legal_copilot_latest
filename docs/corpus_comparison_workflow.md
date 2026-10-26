# Comparing a candidate corpus with a reference text

This tool produces evidence for human review only; it never imports records or changes verification/currentness/in-force flags.

1. Obtain reference text manually from an authorized official source. Save UTF-8 plain text and record the source URL, Gazette issue/date, access date, and who saved it. Do not automate retrieval where source terms prohibit it.
2. Run `python tools/compare_corpus_to_reference.py --candidate law_rows_ar.jsonl --reference official_reference.txt --out-dir comparison_report`. Add `--fail-on-difference` to return status 1 unless all articles match after normalization.
3. Review the JSON and Markdown reports. Prioritize numeric differences, major differences, missing/extra articles, then minor differences. Verify the original source before correcting anything.
4. Preserve report hashes and the lawyer's decision in the legal review record.

Candidate JSONL uses one object per line with `article` (or `label`) and `text` (or `body`). Repeated labels are aligned by occurrence order to distinguish promulgation articles from body articles.

Normalization is limited; number-word checks may produce false positives. A clean report cannot authenticate the reference, establish legal status or amendment completeness, or prove reuse permission. Human and lawyer review remain mandatory.
