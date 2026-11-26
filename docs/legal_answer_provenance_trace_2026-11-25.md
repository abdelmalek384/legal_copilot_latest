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


## Follow-up citation-alignment hardening — 2026-11-26

- The answer citation relevance guard previously concatenated all passages cited by one sentence before checking for lexical anchors. A relevant passage could therefore mask an unrelated additional citation.
- The guard now checks each cited passage independently and abstains if any cited passage has no meaningful lexical anchor in that sentence.
- Regression coverage includes both an unrelated extra citation (must abstain) and complementary cited passages (must pass the lexical relevance check).
- Commits: `05c13aac94d47f50c840df18c75175ea4a3e851a` and `d6edf36158c1fbb4a979af4128e024fecf240563`.
- Tests are committed but have not been executed on this remote branch. This lexical check is not semantic entailment or legal review; broader answer quality and end-to-end research acceptance remain open.


## Follow-up multi-source polarity hardening — 2026-11-26

- The Arabic source-polarity guard previously concatenated all passages cited by one sentence. When separate cited passages expressed opposite polarities, the combined text could be classified as ambiguous and bypass the contradiction check.
- The guard now compares the generated sentence with each cited passage independently. An ambiguous passage remains unclassified, but it cannot mask a clear reversal in another cited passage.
- Added a direct regression and an end-to-end `ask()` abstention regression for conflicting multi-source polarity.
- Commits: `de1eed998bcf0af39eb138b67556ad0f8bbd1f39` and `b0e7eb11647fea8d92f4245f411ebdc0df9243dc`.
- Tests are committed but unexecuted on this remote branch. The check remains a narrow polarity heuristic, not semantic interpretation or lawyer review.

## Follow-up independent-source claim checks — 2026-11-26

- Actor-role attribution now evaluates each cited passage independently. A second passage that mentions the answer's actor cannot mask a role substitution in another cited passage.
- Conditional-scope checking now evaluates each cited passage independently. A second passage with unconditional wording cannot mask a conditional rule in another cited passage.
- Numeric support now requires the complete normalized value-and-unit quantity to appear together in at least one cited passage. Separate citations can no longer be concatenated to fabricate a quantity from a value fragment and a unit fragment.
- Added focused regressions for multi-source actor masking, conditional masking, and split-source numeric quantities.
- Commits: `5bab6a32392ef293d836150e78e41835b6c5ebaf`, `dadba963e80206be30585e548da9166104073636`, `cc0eace8f1b7d4cf64f28b19d909499599d572eb`, `7d6448452d63ea9130e800c6f7129ef74a494703`, `94d418e952c931e0a76b60730e696703762ee47f`, and `8214d2ecf3695e0c485960ccecc24fa4f7c3e588`.
- These tests are committed but have not been executed in this remote-only workflow. The checks are conservative lexical/quantity safeguards, not semantic entailment, currentness verification, or qualified Egyptian lawyer review.


## Follow-up claim-support citation isolation — 2026-11-26

- The optional broad claim-support screen previously concatenated cited passage text before checking numeric value/unit consistency. A number and its unit could therefore be assembled across separate citations.
- Numeric, modality, qualifier, reversal, and finite-limitation contradiction checks now run against each cited passage independently. The existing combined lexical-coverage check remains unchanged.
- Added a fictional regression where one citation ends with a number and the next begins with its unit; the claim must be rejected.
- Direct main commits: implementation `83f7321`, regression `5579126`. Both files were read back from main. Tests remain unexecuted; no Actions/CI or runtime validation was performed.
- This is a conservative lexical safeguard only. It does not establish semantic entailment, legal currentness, or lawyer review.


## Follow-up citation-index parser hardening — 2026-11-26

- Bounded citation-index parsing in the optional claim-support module. Oversized numeric markers now return a fail-closed result instead of risking Python's integer-string conversion limit in direct guard use.
- Added a synthetic regression exercising both the broad claim-support and negated-obligation guards with an oversized citation marker.
- Direct main commits: implementation `222ac52`, regression `abdfc35`. Files were read back from main; no tests or CI were executed.
- During review of concurrent Arabic numeral parser changes, a literal escaped newline was found in the parser source and corrected in commit `9cf10a8`. The corrected file was read back; no runtime syntax check was run.
- These changes are bounded input-hardening and lexical safeguards, not semantic legal validation.
