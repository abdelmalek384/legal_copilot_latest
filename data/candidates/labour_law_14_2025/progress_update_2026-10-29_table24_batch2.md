# Labour-law knowledge progress update — Table 24 extraction batches 1–5

**Date:** 2026-10-29  
**Scope:** Decision 250/2026, Table 24 only. This is a delta report, not a replacement for the full progress report.

## Completed in this work segment

- Added structured candidate transcription for Table 24 numbered entries **1–20** in `decision_250_table24_candidate_batch1_rows001_020_2026-10-29.json`.
- Added structured candidate transcription for numbered entries **21–40** in `decision_250_table24_candidate_batch2_rows021_040_2026-10-29.json`.
- Added structured candidate transcription for entries **41–60**, **61–80**, **81–99**, **100–120**, **121–140**, **141–160**, **161–180**, **181–200**, **201–220**, **221–240**, **241–260**, **261–280**, **281–300**, **301–320**, and **321–340** in batches 3–17, retaining parent/child rows for isomers and chemical variants.
- Preserved the secondary-source line pinpoint for each row; kept raw limit strings and units rather than pretending the flattened text has reliable column alignment.
- Preserved an apparent CAS formatting anomaly for Aluminum oxide (`1344-281`) instead of silently correcting it.
- Preserved the nested relationship for Aluminum metal and insoluble compounds and subentries (rows 28–33).
- Added explicit machine-readable warnings that no candidate is suitable for authoritative retrieval, compliance advice, or safety decisions.
- Added `tools/validate_decision250_table24_candidates.py` to fail closed on missing/duplicate row numbers, malformed batch JSON, missing source pinpoints, or a candidate row marked as reviewed prematurely; its expected range now covers rows 1–617.
- Added `tools/build_decision250_table24_review_queue.py` to generate a human triage queue for text/identifier anomalies, high-risk entries, currentness leads, group rows, and possible surface/air-unit ambiguity; it never repairs a candidate automatically.
- Prepared `lawyer_in_app_acceptance_plan_2026-10-29.md` so the later in-app lawyer review is a distinct, testable release gate. This preparation does not count as lawyer approval.
- Parsed all five batch files and structurally checked row numbers 1–617: 617 unique numbers, no gaps/duplicates, all flattened rows source-pinned and pending official match. This was a structural audit of the fetched JSON, not execution of the Python validator or legal verification.

## Current subtask completion estimates

| Subtask | Status | Estimate | What remains |
|---|---|---:|---|
| Decision 250 source discovery | Full secondary transcription found | 90% | Official Gazette bytes/hash and full primary-source comparison |
| Table 23 hazardous-substance threshold quantities | 137/137 candidate labels exist | 100% candidate-label coverage | Primary-source match; resolve anomalies; currentness and counsel |
| Table 24 chemical-exposure limits | 617/745 numbered entries structured as candidates | 82.8% by numbered-entry count | Extract remaining entries; preserve row hierarchy/units/footnotes; primary-source comparison |
| Decision 249 circulars | Ministry announced future periodic circulars; separate public circular not located | 35% search work | Find circular or leave unresolved |
| Authoritative retrieval eligibility | None approved | 0% | Primary match, currentness, source-use assessment, and qualified Egyptian OSH counsel approval |

Percentages are work-product coverage only, not legal certainty. For Table 24, 617/745 = 82.82%, rounded to 82.8%. Some entries contain subordinate rows; counts should be reconciled against the full table structure before claiming final completeness.

## Source and safety boundary

The Table 24 transcription is from a secondary reproduction dated 2026-10-26:
https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html

The page's table header begins at extracted source line 4475; entries 1–20 are around lines 4484–4516 and entries 21–40 around lines 4518–4551; entries 41–60 around lines 4553–4585; entries 61–80 around lines 4586–4618; entries 81–99 around lines 4620–4651; entries 100–120 around lines 4653–4686; entries 121–140 around lines 4688–4720; entries 141–160 around lines 4722–4754; entries 161–180 around lines 4755–4786; entries 181–200 around lines 4788–4819; entries 201–220 around lines 4821–4852; entries 221–240 around lines 4854–4885; entries 241–260 around lines 4887–4918; entries 261–280 around lines 4919–4950; entries 281–300 around lines 4952–4983; entries 301–320 around lines 4984–5016; entries 321–340 around lines 5017–5049; entries 341–360 around lines 5051–5082; entries 361–380 around lines 5084–5116; entries 381–403 around lines 5117–5155; entries 404–423 around lines 5157–5188; entries 424–443 around lines 5190–5222; entries 444–463 around lines 5224–5255; entries 464–483 around lines 5257–5287; entries 484–503 around lines 5289–5321; entries 504–523 around lines 5322–5353; entries 524–543 around lines 5355–5388; entries 544–563 around lines 5390–5422; entries 564–583 around lines 5424–5456; entries 584–603 around lines 5457–5489; entries 604–617 around lines 5491–5513. This is useful for discovery and candidate extraction, but it is **not** an official Gazette file and has not been compared row-by-row with the Gazette. No official PDF hash is claimed.

The Official Gazette catalogue identifies Decisions 248–252/2026 in the supplement to Egyptian Proceedings issue 225(A), dated 2026-10-12:
https://dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full

## Next work items, in order

1. Continue Table 24 extraction from row 618 onward in batches, preserving source-line pinpoints and parent/child rows.
2. Extend the structural validator to detect duplicate/malformed CAS strings, blank values, and suspicious row/field shifts without auto-correcting the source.
3. Cross-check terminology and units against the decision's own explanation of TWA/STEL/C, skin notation, biological exposure indices, carcinogenicity labels, and footnotes before attempting normalization.
4. When the original Gazette PDF is provided, hash the actual bytes and compare each extracted row to the relevant page image. Do not substitute secondary text for the official scan.
5. Have qualified Egyptian OSH counsel review the source-matched high-risk exposure limits before any are exposed as authoritative answers.

## Overall status

The overall evidence-backed legal-content readiness remains **7%**. This work improves the Table 24 extraction subtask, not the overall release-gate score: no rules have become primary-source-matched, currentness-verified, counsel-approved, or authoritative-retrieval-eligible.
