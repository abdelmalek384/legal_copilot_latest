# Runbook: adding a law to the Egyptian legal corpus

This workflow is evidence-preserving and deliberately separates acquisition, text comparison, legal review, currentness, and reuse permission. **A successful script run never makes a law authoritative.** Do not set a candidate to verified or in-force until the required primary-source and lawyer-review gates have been met.

## 1. Identify the legal instrument

1. Create or locate its entry in `docs/legal_document_candidates.json`. Record the exact official title, instrument type, number/year, jurisdiction, issuing authority, and candidate source.
2. Identify the Official Gazette issue and publication date. Keep publication date distinct from commencement/effective date.
3. Record amendment, repeal, transitional, and commencement relationships as candidates only until checked against primary text.
4. Do not use a search-result snippet, secondary summary, generated dataset, or a law-firm article as the official reference.

## 2. Acquire the primary source lawfully

1. Check the source-permission register and applicable terms before automated collection. Never bypass a login, robots restriction, access control, or technical block.
2. If automated acquisition is explicitly permitted, use the approved collection manifest and `tools/collect_legal_documents.py`.
3. Otherwise, have a person save the document manually from the official source. Record the exact source page/file URL, retrieval date, person, and method:
   ```bash
   python tools/record_manual_capture.py \
     --file ~/Downloads/official_gazette.pdf \
     --document-id EG-LABOUR-14-2025 \
     --source-url "https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf" \
     --captured-by "Reviewer name" \
     --capture-method browser_download \
     --retrieved-on YYYY-MM-DD \
     --gazette-issue "Issue as printed" \
     --dry-run
   ```
   Review the dry-run output, then repeat without `--dry-run` to record the capture. The recorder does not fetch the URL. If the capture URL host differs from the document's default source, select the registered matching source with `--source-id`; the recorder rejects a source-ID/host mismatch. Its output remains pending human review and does not grant permission to store, index, display, or reuse the content.

## 3. Preserve provenance and extract text

1. Preserve the original file unchanged. Record its SHA-256, exact URL, issue/date, capture details, and storage path.
2. Confirm the extracted text is readable and that article headings, page order, tables, footnotes, and annexes have not been lost. OCR output is a candidate transcription, not the Gazette original.
3. Keep the original, extracted text, metadata, and audit outputs linked by their hashes. Never overwrite a prior capture; a new source file or corrected scan gets a new provenance record.

## 4. Run structural checks on candidate article rows

For a JSONL candidate with `law`, `article`, and `text` fields:

```bash
python tools/audit_article_rows.py --input law_rows_ar.jsonl --out-dir audit_report
```

Review `audit.md`, `audit.json`, and every row in `quantity_checklist.csv`. Resolve numbering gaps, duplicates, malformed/short text, hidden characters, cross-reference anomalies, orthography outliers, and suspicious endings. Quantity-bearing provisions (periods, amounts, percentages, counts) require particular attention.

A clean structural audit only means the file is internally consistent. It does not prove Gazette fidelity, legal validity, currentness, or reuse rights.

## 5. Compare every article with the official reference

Prefer comparing the candidate rows directly with the manually captured Official Gazette PDF. This preserves the original PDF hash and reports the Gazette page range detected for each article:

```bash
python tools/compare_corpus_to_reference.py \
  --candidate law_rows_ar.jsonl \
  --reference ~/Downloads/official_gazette.pdf \
  --out-dir comparison_report
```

The PDF path must point to the exact file captured in step 2. The tool uses `pypdf` text extraction; it is not OCR, visual inspection, source authentication, or legal review. Inspect the original PDF page images for every article, especially pages with extraction warnings, empty text, tables, columns, footnotes, or Arabic glyph/order problems. Review missing/extra articles, numeric and number-word mismatches, major differences, and minor differences. A high similarity score or `all_identical` result is not an approval to import or serve the candidate.

If an authorized, human-checked UTF-8 transcription is also available, it can be compared as a secondary cross-check:

```bash
python tools/compare_corpus_to_reference.py \
  --candidate law_rows_ar.jsonl \
  --reference official_reference.txt \
  --out-dir text_comparison_report
```

Check every discrepancy against the original Gazette pages; do not automatically replace text based on a comparison report. Preserve both reports, the original PDF, its SHA-256, and the extracted-text hash.

## 6. Record legal review and version status

A qualified Egyptian lawyer must review:
- exact article wording and numbering against the Gazette;
- promulgation provisions, commencement/effective dates, transitional rules, and territorial/material scope;
- amendments, repeal, corrigenda, implementing decisions, and whether later instruments alter the result;
- citation pinpointing and any uncertainty or conflicting interpretation.

Record reviewer identity, review date, source/page pinpoints, findings, unresolved questions, and the decision for each article or instrument. Keep unreviewed, disputed, incomplete, OCR-derived, or secondary-only material visibly quarantined. Do not infer an effective date from the publication date.

## 7. Release gates

Before an instrument can support authoritative legal answers, confirm all of the following independently:

- [ ] Primary Gazette source captured with provenance and integrity hash.
- [ ] Storage/indexing/display/reuse rights reviewed and documented.
- [ ] Article-by-article comparison completed and discrepancies resolved.
- [ ] Commencement, amendment, repeal, and currentness checked as of the requested date.
- [ ] Qualified Egyptian lawyer review recorded with pinpoint citations.
- [ ] Citation and retrieval tests pass; unsupported claims fail closed.
- [ ] Existing legal release gate is satisfied.

If any item is missing, keep the instrument non-authoritative and make the assistant abstain or clearly state that the material was not verified. Do not weaken release gates to increase corpus coverage.


## 8. Disposable fictional-fixture smoke test

Run this before processing a user-supplied instrument. It exercises the manual-capture CLI in dry-run mode, article audit, quantity checklist, corpus/reference comparison, commencement-date extraction, and the source-matched-unreviewed classifier without touching an application database. The fixture is fictional and must never be indexed or treated as Egyptian law. The Amiri Press URL below is a host-matching placeholder; it is never fetched.

From the repository root:

```bash
FIXTURE_OUT="$(mktemp -d "${TMPDIR:-/tmp}/legal-copilot-ingestion.XXXXXX")"

python tools/record_manual_capture.py \
  --file tests/fixtures/law_ingestion/fictional_reference.txt \
  --document-id SYNTHETIC-LAW-ONLY \
  --source-id EG-AMIRI-PRESS \
  --source-url "https://www.alamiria.com/fixture-only" \
  --captured-by "Fixture operator" \
  --capture-method manual_transcription \
  --retrieved-on "$(date +%F)" \
  --publication-date 2025-05-03 \
  --effective-date 2025-09-01 \
  --gazette-issue "fictional fixture only" \
  --notes "SYNTHETIC FIXTURE ONLY — not Egyptian law or legal evidence" \
  --out "$FIXTURE_OUT/capture" --dry-run

python tools/audit_article_rows.py \
  --input tests/fixtures/law_ingestion/fictional_candidate.jsonl \
  --out-dir "$FIXTURE_OUT/audit"

python tools/compare_corpus_to_reference.py \
  --candidate tests/fixtures/law_ingestion/fictional_candidate.jsonl \
  --reference tests/fixtures/law_ingestion/fictional_reference.txt \
  --out-dir "$FIXTURE_OUT/comparison"

PYTHONPATH=. python tests/test_law_ingestion_fixture_pipeline.py
```

The audit intentionally sees article labels 1 and 13, so gaps 2–12 are expected fixture gaps, not a production-law finding. Its `quantity_checklist.csv` must contain the test period (**five years**) and amount (**500 جنيه**). The fixture test reads the publication date (2025-05-03), general effective date (2025-09-01), and separate specialized-courts date (2025-10-01) from the text, not only from capture metadata. It also exercises the gated `source_matched` tier with synthetic-only evidence and expects the explicit `not_lawyer_reviewed` reason. This does not approve real-source rights, enable the production feature, or change any legal record.

## 9. Change log and rollback

Keep immutable copies of source files, extracted text, hashes, comparison reports, review records, and the commit that introduced the candidate. A correction creates a new version with a documented relationship to the prior version; do not erase historical evidence. If a source, rights decision, or legal interpretation is withdrawn, quarantine the affected version and prevent it from being used for authoritative retrieval.
