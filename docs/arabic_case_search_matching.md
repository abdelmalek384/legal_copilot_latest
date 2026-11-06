# Arabic case-file search and conflict screening

## Current matching behavior

Case-file and legal-text retrieval uses FTS5 candidate retrieval plus a lightweight Arabic tokenizer/stemmer and bounded, curated query expansion. This change adds a small set of common inflection/derivation variants for terms that appeared in manual testing, including **الشيك / شيكا** and **التأخير / تأخر**. Expansion affects query candidates and ranking only; it does not rewrite stored text, cited passages, or source evidence.

Conflict screening now compares normalized token sets without depending on exact word order or repeated whitespace, and ignores generic organization descriptors such as **شركة**, **مؤسسة**, **مجموعة**, and **مكتب**. A generic descriptor alone does not match. Existing partial-substring matching remains available for partial names and case numbers.

## Limits and safety

- This is lexical matching, not Arabic morphological analysis, entity resolution, or a definitive legal-conflict determination.
- Similar names can belong to different people or entities; every result requires human review.
- Curated morphology is deliberately small. Egyptian colloquial terms, misspellings, transliteration, broken plurals, OCR corruption, and unseen derivations may still be missed.
- Query expansion does not establish that a retrieved legal passage is authentic, current, applicable, or legally equivalent to another wording.
- No database schema, migration, index contents, or live records are changed by this work. Existing text/indexing is left untouched; only query-side expansion and conflict comparison behavior change.

## Validation

The new tests in tests/test_arabic_matching.py cover the reported word-form pairs, reordered names, whitespace normalization, company descriptors, and generic-only/empty queries. Retrieval quality still needs evaluation on a lawyer-reviewed Arabic test set; these regression tests are not a benchmark and do not support a quality percentage claim.
