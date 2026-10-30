# Decision 250 Table 24 — full candidate-batch structural audit

**Audit date:** 2026-10-30  
**Branch:** `legal-knowledge-evidence-2026-10-29`  
**Purpose:** Record an independent structural pass over all 38 committed Table 24 candidate JSON files through row 781. This is not legal verification.

## Result

- Batch files parsed: **38/38**
- Flattened top-level and nested child records: **781**
- Unique row numbers: **781**
- Number range: **1–781**
- Missing row numbers in that range: **0**
- Duplicate row numbers: **0**
- Every batch reports source class `secondary_transcription`.
- Every batch reports `official_gazette_match=not_performed`.
- Every batch has a null `official_pdf_sha256`; no original Gazette hash is claimed.

## Batch count reconciliation

| Batch range | Flattened records |
|---|---:|
| 1–20 | 20 |
| 21–40 | 20 |
| 41–60 | 20 |
| 61–80 | 20 |
| 81–99 | 19 |
| 100–120 | 21 |
| 121–140 | 20 |
| 141–160 | 20 |
| 161–180 | 20 |
| 181–200 | 20 |
| 201–220 | 20 |
| 221–240 | 20 |
| 241–260 | 20 |
| 261–280 | 20 |
| 281–300 | 20 |
| 301–320 | 20 |
| 321–340 | 20 |
| 341–360 | 20 |
| 361–380 | 20 |
| 381–403 | 23 |
| 404–423 | 20 |
| 424–443 | 20 |
| 444–463 | 20 |
| 464–483 | 20 |
| 484–503 | 20 |
| 504–523 | 20 |
| 524–543 | 20 |
| 544–563 | 20 |
| 564–583 | 20 |
| 584–603 | 20 |
| 604–617 | 14 |
| 618–642 | 25 |
| 643–668 | 26 |
| 669–694 | 26 |
| 695–720 | 26 |
| 721–746 | 26 |
| 747–772 | 26 |
| 773–781 | 9 |
| **Total** | **781** |

Batches 32–38 (618–781) extend the flattened sequence. Batches 36–38 cover the remainder of the secondary transcription through row 781, including group headings and wood-dust subentries; hierarchy is not inferred beyond source labels. Batch 35 source lines 5646–5686 includes tin, titanium dioxide and related numbered subentries; hierarchy is not inferred beyond the labels recorded. Batch 34 source lines 5601–5644 include synthetic vitreous fiber and talc group headings/subentries; hierarchy is not inferred beyond the labels recorded. Batch 33 source lines 5557–5600 include silver and sodium group headings/subentries; hierarchy is not inferred beyond the labels recorded. Its source lines 5514–5555 include group headings and numbered subentries; hierarchy is not inferred beyond the labels recorded. The unusual file-name ranges around batches 5–6 and 19–20 reflect the actual flattened row grouping: batch 5 contains rows 81–99, batch 6 rows 100–120, and batch 20 contains parent/child records covering 381–403. The structural audit found no overlap or gap in the final flattened row sequence.

## Explicit limitations

This audit checks JSON parsing, row-number continuity and source metadata as read from the repository. It does **not** establish that any label, CAS number, formula, molecular weight, limit, unit, footnote, column association or health-effect description accurately transcribes the secondary page or the Official Gazette. It does not establish currentness, source-use rights, or legal/safety correctness.

All candidates must remain `pending_official_match`. Table 24 rows officially matched: **0**. Counsel-approved rows: **0**. Rows eligible for authoritative retrieval: **0**.

## Next gate

Obtain the original Gazette supplement through authorized access, record the actual file hash, compare each candidate against the exact page image, resolve anomalies, assess currentness and source-use, and obtain qualified Egyptian OSH counsel review before enabling any row for authoritative retrieval.


## Technical table-index cross-check — 2026-10-30

The secondary transcription's contents map explicitly lists Table 24 at printed page 249 and the next chapter (records) at printed page 361. The same transcription labels the chemical exposure limits at its Table 24 heading; no Table 25 is listed. The technical table index had accidentally split this single table into entries 24 and 25 and incorrectly limited entry 24 to pages 249–250. The index is corrected: one Table 24, pp. 249–360, with the duplicate Table 25 entry removed.

A new regression test, `tests/test_decision_250_table24_inventory.py`, checks that:
- the technical index contains exactly 24 numbered tables and one Table 24 only;
- Table 24's candidate section range is 249–360;
- all 38 secondary candidate batches contain exactly rows 1–781 with no gaps/duplicates;
- all candidate batches remain secondary-only, have no official PDF hash, and remain retrieval-ineligible.

This cross-check is against the secondary transcription's own contents map and structure. It does not establish the original Gazette's exact pagination or validate any exposure value. Official Table 24 matches remain 0/781.
## Targeted high-risk row cross-check against secondary transcription — 2026-10-30

The full secondary transcription was searched for the three previously flagged rows. It confirms the transcription's own raw strings and makes the remaining image conflicts explicit:

| Table 24 row | Secondary transcription line | Transcribed value | Separate watermarked-image spot-check | Disposition |
|---:|---:|---|---|---|
| 34 — Aluminium oxide | 4541 | CAS string `1344-281` | Earlier tentative image read suggested `1344-28-1` | Still unresolved. The transcription itself preserves a malformed/nonstandard CAS string; do not normalize or infer the intended identifier. |
| 61 — Benomyl | 4586 | `1 مجم/ م3(I)` | Earlier tentative image read appeared to show `0.3 mg/m3` | Still unresolved. Do not select a value or infer the exposure-limit column. |
| 64 — Benzene | 4591 | `0,02 جزء / مليون` | Earlier tentative image read appeared to show `0.5 ppm` | Still unresolved. Do not select a value or infer the exposure-limit column. |

Secondary source: https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html. The exact transcription line references are secondary-text line numbers, not Official Gazette page citations. The image spot-check is itself a watermarked third-party reproduction and is not the original Gazette. The new cross-check fields were added to candidate batches 2 and 4; they do not alter raw values, status, or eligibility.

**Disposition:** all three rows remain `pending_official_match`; official Gazette matches remain 0/781; counsel-approved rows remain 0; retrieval-eligible rows remain 0. Obtain and compare the original issue before resolving any discrepancy. Do not use these values for occupational exposure advice or compliance decisions.
