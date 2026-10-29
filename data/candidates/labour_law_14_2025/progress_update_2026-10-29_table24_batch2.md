# Labour-law knowledge progress update — Table 24 extraction batches 1–2

**Date:** 2026-10-29  
**Scope:** Decision 250/2026, Table 24 only. This is a delta report, not a replacement for the full progress report.

## Completed in this work segment

- Added structured candidate transcription for Table 24 numbered entries **1–20** in `decision_250_table24_candidate_batch1_rows001_020_2026-10-29.json`.
- Added structured candidate transcription for numbered entries **21–40** in `decision_250_table24_candidate_batch2_rows021_040_2026-10-29.json`.
- Preserved the secondary-source line pinpoint for each row; kept raw limit strings and units rather than pretending the flattened text has reliable column alignment.
- Preserved an apparent CAS formatting anomaly for Aluminum oxide (`1344-281`) instead of silently correcting it.
- Preserved the nested relationship for Aluminum metal and insoluble compounds and subentries (rows 28–33).
- Added explicit machine-readable warnings that no candidate is suitable for authoritative retrieval, compliance advice, or safety decisions.

## Current subtask completion estimates

| Subtask | Status | Estimate | What remains |
|---|---|---:|---|
| Decision 250 source discovery | Full secondary transcription found | 90% | Official Gazette bytes/hash and full primary-source comparison |
| Table 23 hazardous-substance threshold quantities | 137/137 candidate labels exist | 100% candidate-label coverage | Primary-source match; resolve anomalies; currentness and counsel |
| Table 24 chemical-exposure limits | 99/745 numbered entries structured as candidates | 13.3% by numbered-entry count | Extract remaining entries; preserve row hierarchy/units/footnotes; primary-source comparison |
| Decision 249 circulars | Ministry announced future periodic circulars; separate public circular not located | 35% search work | Find circular or leave unresolved |
| Authoritative retrieval eligibility | None approved | 0% | Primary match, currentness, source-use assessment, and qualified Egyptian OSH counsel approval |

Percentages are work-product coverage only, not legal certainty. For Table 24, 99/745 = 13.29%, rounded to 13.3%. Some entries contain subordinate rows; counts should be reconciled against the full table structure before claiming final completeness.

## Source and safety boundary

The Table 24 transcription is from a secondary reproduction dated 2026-10-26:
https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html

The page's table header begins at extracted source line 4475; entries 1–20 are around lines 4484–4516 and entries 21–40 around lines 4518–4551; entries 41–60 around lines 4553–4585; entries 61–80 around lines 4586–4618; entries 81–99 around lines 4620–4651. This is useful for discovery and candidate extraction, but it is **not** an official Gazette file and has not been compared row-by-row with the Gazette. No official PDF hash is claimed.

The Official Gazette catalogue identifies Decisions 248–252/2026 in the supplement to Egyptian Proceedings issue 225(A), dated 2026-10-12:
https://dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full

## Next work items, in order

1. Continue Table 24 in batches of 20–40 numbered entries, preserving source-line pinpoints and parent/child rows.
2. Continue in batches, with the new rows 41–60 saved in `decision_250_table24_candidate_batch3_rows041_060_2026-10-29.json`.
3. Continue with rows 61–80 saved in `decision_250_table24_candidate_batch4_rows061_080_2026-10-29.json`.
4. Continue with entries 81–99 saved in `decision_250_table24_candidate_batch5_rows081_100_2026-10-29.json`; JSON syntax was repaired and the five batch files parsed successfully.
5. Build validation checks for duplicate CAS values, malformed CAS strings, blank fields, suspicious unit shifts, and repeated chemicals under alternate names; report anomalies without auto-correcting them.
6. Cross-check Table 24 terminology and units against the decision's own explanation of TWA/STEL/C, skin notation, biological exposure indices, carcinogenicity labels, and footnotes before attempting normalization.
7. When the original Gazette PDF is provided, hash the actual bytes and compare each extracted row to the relevant page image. Do not substitute the secondary text for the official scan.
8. Have the qualified Egyptian OSH lawyer review the source-matched high-risk exposure limits before any are exposed as authoritative answers.

## Overall status

The overall evidence-backed legal-content readiness remains **7%**. This work improves the Table 24 extraction subtask, not the overall release-gate score: no rules have become primary-source-matched, currentness-verified, counsel-approved, or authoritative-retrieval-eligible.
