# Arabic OCR Quality Evaluation

**Status:** Evaluation tooling; no representative Egyptian court-scan benchmark has been collected or passed yet.

## Purpose

Use `tools/evaluate_arabic_ocr.py` to compare OCR text with a manually corrected transcription of the same page. The tool reports character error rate (CER) and word error rate (WER) per page and as a reference-length-weighted aggregate. It does not authenticate documents, determine legal status, or measure whether an answer is legally correct.

## Input format

Provide one JSON object per line in UTF-8 JSONL:

```json
{"document_id":"approved-test-scan-01","page":"1","reference_text":"Manually corrected page transcription","ocr_text":"Text returned by the OCR pipeline"}
```

- Use one record per page, not one record per entire multi-page document.
- Reference text must be manually transcribed and checked against the page image by a qualified reviewer.
- Use only scans you are authorized to process. Do not commit client documents, privileged content, personal data, or unlicensed court materials to the public repository.
- Keep a private mapping from opaque document IDs to source files; do not include names or case numbers in a public benchmark.
- Preserve the original page and OCR configuration outside the public repository under the approved retention and access policy.

## Run

```bash
python tools/evaluate_arabic_ocr.py /secure/path/ocr-evaluation.jsonl --output /secure/path/ocr-report.json
python -m unittest tests.test_evaluate_arabic_ocr
```

The script has no third-party dependency. CER is character edit distance divided by normalized reference characters; WER is word edit distance divided by normalized reference words. Aggregate scores are micro-averaged by reference length, so long pages contribute proportionally more than short pages.

Normalization applies Unicode NFKC, removes Arabic diacritics and tatweel, normalizes common alef forms and alef maksura, converts Arabic and Persian digits to ASCII, and collapses whitespace. Punctuation is preserved because punctuation and numbering may be material in legal citations. Review the normalization policy before comparing results across OCR engines.

## Recommended evaluation protocol

1. Assemble a lawyer-approved, permission-cleared sample across scan quality, skew, faint text, stamps, tables, multi-column pages, Arabic numerals, article headings, footnotes, and mixed Arabic/English.
2. Have one person prepare page-level reference text and a second reviewer spot-check it against the image. Record adjudications for disputed text.
3. Freeze the OCR engine/version, language packs, DPI, preprocessing, and configuration for each run.
4. Report aggregate and per-page CER/WER, failure rates, and examples of high-impact errors. Do not report only a single average.
5. Separately inspect legal-critical fields: law/article numbers, dates, negation, monetary amounts, party names, provisos, footnotes, and amendment/repeal language. A low overall CER can still hide a dangerous error in one of these fields.
6. Compare configurations on the same pages and keep a held-out set for regression testing.
7. Ask qualified Egyptian-law reviewers to approve practical release thresholds after inspecting the dataset and error severity. Do not invent a universal acceptable CER/WER threshold.
8. Keep OCR text marked unverified until a human checks it against the original. OCR success must never promote a legal source's authenticity, legal status, permission, or verification flags.

## Release gate

The evaluation is not complete until a representative, authorized Arabic scan set has been reviewed, the report is reproducible, critical citation/number errors are analyzed, and a qualified reviewer signs off on the use case. This repository addition provides measurement tooling only; it does not mean OCR quality has been validated on real Egyptian court papers.
