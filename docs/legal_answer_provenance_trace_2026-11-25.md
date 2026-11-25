# Legal answer provenance trace — 2026-11-25

**Scope:** static source trace only; no runtime tests executed. No corpus or legal source content was added.

## Findings

- `citation_provenance(c, version_id)` binds a retrieved corpus passage to its document-version, document, source registry row, central permission-register result, review-event evidence, and version relationships.
- Both verified retrieval query paths require verified version state, required review evidence, collection/commercial permission evidence, and effective/repeal date gates before retrieval.
- Search-result adapters populate `source_id`, `source_status`, and citation text from registry provenance.
- The dedicated `firm_test_source_matched` answer path reads `source_match_evidence` from hit records and validates it with the trust-tier helper. However, the corpus provenance adapter does **not** populate/persist the full evidence package, and the documented test-mode search scope intentionally yields no eligible candidates. The synthetic tests stub the search layer, so they exercise response labeling but not end-to-end corpus retrieval.
- Therefore, source-matched answer mode is currently fail-closed in actual corpus retrieval. This is an intentional boundary, not a defect to bypass. Do not add an evidence object from metadata or hashes alone, and do not enable candidate retrieval until the storage/adapter owner supplies a reviewed schema and a permission-cleared candidate record.

## Integration recommendation

Keep existing verified-corpus retrieval unchanged. A future adapter/schema change must be reviewed separately with: exact source/version binding, independent capture identifiers and hashes, completeness and difference-resolution records, rights evidence, and negative tests proving the source-matched tier cannot become verified or lawyer-approved. Until those exist, test with synthetic stubs only and report this gap as unresolved.

## Scope and limitations

This audit does not establish legal accuracy, currentness, licensing, security, or runtime behavior. No Python tests, browser tests, or supported Python 3.12 execution were performed.
