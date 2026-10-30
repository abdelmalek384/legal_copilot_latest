# Decision 250/2026 — full secondary transcription route and missing-page recovery

Research date: 2026-10-29  
Status: **full secondary text transcription found; not primary-source verified; not eligible for authoritative retrieval.**

## Breakthrough

A full text transcription of Labour Ministry Decision 250/2026 is publicly viewable at:

- Riwaq Al-Jamal, “قرار وزير العمل 250 لسنة 2026 بقواعد ومعايير وبيان الأمان في أماكن العمل والاشتراطات والاحتياطات اللازمة لدرء المخاطر”: https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html
- The page identifies the instrument as Egyptian Proceedings issue 225 supplement (A), dated 2026-10-12.
- It exposes 6,454 web-extracted lines in the browser view, including the instrument's preamble, Articles 1 onward, technical requirements, Tables 1–24, and record templates.
- The table of contents places the chemical exposure material at printed pp. 229–360: Table 23 (hazardous substances and threshold quantities) starts at printed p. 242; Table 24 (chemical exposure limits) starts at printed p. 249; the register templates start at printed p. 361.
- Therefore, the previously missing printed pp. 296–370 are no longer a complete text-discovery gap: pp. 296–360 fall inside the secondary transcription of Table 24, and pp. 361 onward contain record templates. This does **not** mean those pages have been visually compared against the official Gazette scan.

## What the newly found text supports

1. Article 1 expressly makes the decision, accompanying tables, and register forms part of the rules/standards and workplace safety limits.
2. Article 2 says publication in Egyptian Proceedings and effectiveness from the day following publication.
3. Table 23 is a list of hazardous substances and threshold quantities, with chemical names, quantity values and CAS identifiers where included.
4. Table 24 contains hundreds of chemical exposure-limit entries with names, CAS identifiers, formulas, molecular weights, limits/units, hazard codes and health effects where provided.
5. The document also contains physical-risk tables (heat, noise, vibration, illumination, radiation, magnetic/electric fields and safe electrical approach distances) and record templates.

## Targeted extracted evidence pinpoints

These are **secondary transcription line ranges**, not official Gazette PDF page citations:

- Table of contents / page map: lines 5954–6025.
- Table 23 entries visible in the extracted text: e.g. lines 4262–4357.
- Table 24 entries visible in the extracted text: e.g. lines 4786–4828 and 5694–5727.
- Article 52 references Table 23 threshold quantities and chemical exposure controls: around lines 2254–2276.
- Physical-risk tables: e.g. Table 1 begins around line 2556; Table 22 around lines 3946–3956.

## Access and source-use status

- Official Gazette catalogue record: https://dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full
- The catalogue lists a 6.13 MB PDF bundle, but its download link opens a request-a-copy form. The original bundle's bytes have not been obtained here; no SHA-256 is claimed.
- Law Hub also exposes a Google Drive PDF preview: https://drive.google.com/file/d/1cfdkIR6MlAXJwMJNB8flmvxKKd1Es4gm/preview. A first-page image is accessible, but direct page-image/download requests were not usable in this interface.
- Riwaq is an independent secondary transcription. It is useful for broad extraction and cross-checking, but it is not a substitute for exact comparison with the original official Gazette file.
- Do not infer that the full text transcription grants permission to bulk-copy, redistribute, or commercially reuse the source. Complete a source-use assessment before moving its content into a public product corpus.

## New extraction milestone — Table 23

The candidate JSON at [decision_250_table23_first_page_candidate_rows_2026-10-29.json](decision_250_table23_first_page_candidate_rows_2026-10-29.json) now has Arabic labels for **137/137** listed rows. Rows 64–137 were filled from Riwaq's secondary text, and CAS values for rows 47–48 were recorded from that same text. Each newly transcribed row carries the secondary URL and a text-line range. The text's raw defects were preserved: row 96 has malformed Arabic, and row 137 has a mismatch between the Arabic label and English name. This is extraction completeness by row count, not legal correctness or official matching.

Table 24 exposes 745 numbered chemical entries in the secondary text, but a complete structured row-by-row Table 24 dataset has not been built yet. No values from Table 24 are cleared for operational/legal use.

## Remaining work

1. Export/structure Table 23 and Table 24 rows into machine-readable records while preserving the raw Arabic and source-line pinpoints.
2. Validate row counts, identifiers, numeric formats, units, blanks and OCR anomalies; never fill an unclear value from plausibility.
3. Compare high-impact limits and chemical thresholds against the official Gazette scan or another independent authorized primary source.
4. Obtain the official PDF bytes through an ordinary authorized route and record its SHA-256 only after actual download.
5. Check amendments/corrections and obtain qualified Egyptian OSH/labour counsel review.
6. Keep all Decision 250 content in candidate/review state until those gates pass.

## Status

- Full secondary text route: found.
- Missing pp. 296–370 covered by secondary text discovery: yes.
- Exact structured extraction of every table row: incomplete.
- Official Gazette byte comparison/hash: not completed.
- Currentness review: not completed.
- Source-use clearance: not completed.
- Counsel approval: not completed.
- Authoritative retrieval eligibility: no.


## Superseding Table 24 extraction status — 2026-10-30

The earlier statements above that Table 24 exposed 745 entries or that the structured extraction was incomplete are historical and superseded. The complete secondary transcription was subsequently reconciled to a numbered sequence of **1–781**, and 38 candidate JSON batches now contain all 781 entries with no numbering gaps or duplicates. See `decision_250_table24_structural_audit_2026-10-30.md` and `decision_250_table24_secondary_source_count_discrepancy_2026-10-30.md`.

The same secondary contents map identifies Table 24 at printed page 249 and the records chapter beginning at page 361; therefore the secondary-text section spans pp. 249–360. This does not imply that every printed page was visually inspected, nor that the original Gazette file was obtained. All 781 entries remain candidate-only, 0/781 official Gazette matches, 0 counsel-approved, and 0 retrieval-eligible.
