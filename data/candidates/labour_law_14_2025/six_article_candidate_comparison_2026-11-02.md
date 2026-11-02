# Labour Law 14/2025 — six-row candidate transcription spot-check

**Checked:** 2026-11-02  
**Status:** Partial spot-check only; not a full 311-row comparison and not legal verification.

## Candidate file audit

The Library file `/legal/law_rows_ar.jsonl` contains **311 parseable JSONL rows**: 13 promulgation articles and 298 provisions. The structural audit found no duplicate law/article keys and no missing article sequence entries.

- All 311 rows have `verified: 0`.
- All 311 rows have `in_force: 1`.
- All 311 rows have `as_of: 2025-05-03`.
- The row schema has no explicit `effective_from` field.
- The source field points to a Manshurat secondary transcription, retrieved 2026-10-22, and labels it unofficial until Gazette comparison.
- The embedded source string includes the truncated fingerprint `dd3a52c346fb`; this was **not** independently verified as the JSONL file's SHA-256. The original Library bytes could not be materialized, so the original-file hash remains unverified.

## Official commencement metadata

Promulgation Article 13 states that the law takes effect on the first day of the month following the expiry of 90 days from publication. For the 3 May 2025 publication date, the general commencement date is **1 September 2025**. The specialized labour courts commence on **1 October 2025**. Therefore `as_of: 2025-05-03` is the publication date, not the commencement date. Because every row has `in_force: 1` but no documented semantics or `effective_from`, do not infer that the provisions were in force on 3 May 2025.

## Six manually compared provisions

| Article | Gazette page(s) | Result |
|---:|---:|---|
| 66 | 35 | Matches after normalization |
| 103 | 48 | Matches after normalization; page image reads «كل ستة أشهر على الأقل» |
| 124 | 54 | Matches after normalization |
| 134 | 57–58 | **Textual difference:** candidate omits «ه» in «يعرضه للخطر» |
| 141 | 61 | Matches after normalization |
| 278 | 106 | Matches after normalization |

### Confirmed Article 134 difference

- Official Gazette, printed page 58 / PDF index 56: **«ما يعرضه للخطر»**
- Candidate JSONL row: **«ما يعرض للخطر»**

The candidate transcription omits the final pronoun suffix **ه**. This is a textual difference requiring correction or explicit quarantine before the row is used in an authoritative corpus. Article 134 starts on printed page 57 and continues on page 58; both page images were checked.

### Article 103 extraction note

The ETA-hosted page image at printed page 48 visibly reads **«كل ستة أشهر على الأقل»**. The SIS text layer and one indexed extraction of the ETA PDF include an extra «سنة»; the SIS page image remains unchecked. The page image, not the inconsistent extracted text, is the current visual evidence.

## Comparison method and limits

The six candidate rows were compared against the ETA-hosted Official Gazette page images and the corresponding PDF text extraction. Normalization used NFKC, removal of Arabic diacritics/tatweel, normalization of alef variants and ى/ي, punctuation removal, and whitespace collapse. No numeric difference was identified in these six rows.

This does **not** establish that the other 305 rows match, that all 120 quantitative provisions have been checked, or that the candidate transcription is current, licensed for reuse, or lawyer-approved. All rows remain `verified: 0`; all evidence cards remain `search_eligible: false`.

## Remaining gates

1. Compare all 311 rows against the official Gazette, prioritizing the 120 quantitative provisions.
2. Correct or quarantine the Article 134 suffix omission.
3. Define `in_force` and `as_of` semantics and add an explicit effective-from date.
4. Obtain and hash the original JSONL and Official Gazette PDF bytes.
5. Complete amendment/corrigenda/currentness review, source-rights review, and qualified Egyptian-counsel review.
