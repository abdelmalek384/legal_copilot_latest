# Read-only legal version comparison

## Purpose

`tools/compare_legal_versions.py` compares extracted passages linked to two version IDs for the same registered legal document. It is an initial support tool for the “what changed?” workflow; it does not interpret the legal effect of an amendment.

## Run

Use the approved legal-corpus database or a protected copy that preserves its immutable `legal_corpus` profile marker:

```bash
export COPILOT_CORPUS_DB="/absolute/path/to/legal-corpus.sqlite3"
python tools/compare_legal_versions.py --left-version-id 12 --right-version-id 18
```

Alternatively, pass an explicit `--db` path to a database bound to the `legal_corpus` profile. The CLI refuses to run when `COPILOT_DB` compatibility mode is set, and the comparison refuses unbound databases or databases bound to the control-plane or firm profile. The left version is the baseline and the right version is compared against it. IDs must refer to two distinct versions of the same `legal_documents.document_id`. The tool opens SQLite in read-only mode and does not run migrations or update records.

## Output

- Groups extracted chunks by the exact stored `article` label.
- Reports labels as `unchanged`, `changed`, `added_in_right`, or `removed_from_right`.
- Includes source/version metadata, page references when recorded, exact extracted text, and a unified text diff for changed labels.
- Leaves passages with no article label in an unmapped list rather than guessing where they belong.
- Excludes malformed chunk records, passages with missing/empty text, and every occurrence of a duplicated non-null chunk ID; affected article labels are marked `uncomparable_incomplete_text` rather than falsely classified as added, removed, changed, or unchanged. Duplicate IDs can also affect multiple labels, and are counted separately in the summary.
- Warns when a version is not fully marked as reviewed/verified or either version has no linked chunks.

Whitespace-only differences are treated as unchanged for classification, but the returned text preserves the extracted content. If an article contains multiple chunks, they are joined in chunk-ID order.

## Important limits

- This is a text comparison of indexed/extracted chunks, not a comparison of complete official source files.
- Missing articles can reflect incomplete extraction; they do not prove repeal or deletion from law.
- Exact article-label matching cannot infer renumbered or restructured provisions; those may appear as added/removed.
- Registry review flags and HTTPS source URLs are metadata, not independent proof of authenticity or legal correctness.
- A qualified Egyptian lawyer must compare the authoritative texts, effective dates, transitional provisions, and amendment/repeal evidence before drawing legal conclusions.

## Validation

Run:

```bash
python tests/test_compare_legal_versions.py
```

Tests cover article-level change categories, multi-chunk grouping, unmapped passages, duplicate chunk IDs (including collisions across article labels), malformed/incomplete extraction, missing registry data, cross-document rejection, and a read-only database check. Passing software tests do not validate legal content.
