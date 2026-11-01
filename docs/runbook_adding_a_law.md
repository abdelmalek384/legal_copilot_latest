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
     --source-url "https://official-source.example/document-page" \
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

Save the manually obtained official text as UTF-8 plain text and run:

```bash
python tools/compare_corpus_to_reference.py \
  --candidate law_rows_ar.jsonl \
  --reference official_reference.txt \
  --out-dir comparison_report
```

Review missing/extra articles, numeric mismatches, major differences, and minor differences. Check every discrepancy against the original Gazette pages; do not automatically replace text based on a comparison report. Preserve the report and reference hash.

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

## 8. Change log and rollback

Keep immutable copies of source files, extracted text, hashes, comparison reports, review records, and the commit that introduced the candidate. A correction creates a new version with a documented relationship to the prior version; do not erase historical evidence. If a source, rights decision, or legal interpretation is withdrawn, quarantine the affected version and prevent it from being used for authoritative retrieval.
