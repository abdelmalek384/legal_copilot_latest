# Legal knowledge progress report — 2026-10-29

Scope: only the Labour Law 14/2025 evidence-backed legal-knowledge workstream and the related OSH implementing Decisions 248–252/2026.

## Headline

**Overall evidence-backed legal-content readiness remains 7%.** A full secondary transcription of Decision 250 has now been found, including the technical tables and register templates, materially reducing the text-discovery gap. The legal-release gates remain open: official-file authenticity/hash, exact row extraction and primary-source comparison, complete currentness, source-use assessment and qualified Egyptian-lawyer approval.

## Work completed in this work session

1. Added a reusable inventory of alternative public-source routes (official searchable text, Ministry pages, Gazette catalogue, secondary transcriptions).
2. Built 35 clause/value checks for Decisions 248–252/2026 and stored them both as Markdown and machine-readable JSON. JSON was parsed; 35 clause records match the declared count.
3. Located reproduced Gazette page-image sequences hosted by Al-Masdar:
   - Decision 249: printed pp. 19–44, including Articles 1–22 and Tables 1–3.
   - Decision 250: printed pp. 45–90 inspected so far; definitions, fire, risk assessment, emergency plans, heat/cold stress, noise, vibration, illumination, ionizing/non-ionizing radiation, laser, explosion and excavation sections. A new full secondary transcription was found at Riwaq Al-Jamal: https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html. It maps Table 24 (chemical exposure limits) to printed pp.249–360 and register templates from p.361, covering the previously missing pp.296–370 at the text-discovery layer. This is not an official Gazette file and has not been compared row-by-row to official bytes.
   - Decision 251: printed pp. 371–377.
   - Decision 252: printed pp. 378–398.
4. Added a structured candidate extraction for Decision 249 Table 3: 12 activity/pollutant combinations.
5. Added 17 structured candidate requirements/values for Decision 251 licensing, experience, fees, notification timing and licence terms. JSON/count validated (17/17).
6. Added a machine-readable index of 25 Decision 250 technical tables and transcribed 137 candidate rows from Table 23 (pp.242–248). The table-index JSON (25/25) and Table 23 JSON (137/137) parse and match their declared counts. After finding Riwaq's full secondary transcription, all 137 Table 23 candidate rows now have Arabic labels; the last 74 labels and CAS values for rows 47–48 were filled from that secondary text, with source-line ranges and pending-official-match statuses. Raw anomalies (including row 96's malformed Arabic and row 137's Arabic/English name mismatch) were preserved rather than silently corrected. The same source exposes Table 24's 745 numbered chemical-exposure entries and covers pp.296–370, but the complete Table 24 rows have not yet been normalized into structured data.
7. Found independent Law Hub full-PDF preview routes for Decisions 250, 251 and 252. The preview pages load, but individual Google Drive page-image requests returned 403 in this research interface; no access control was bypassed and no PDF bytes/hash are claimed.
8. Added a scan-based Decision 251/252 article map and 32 structured numerical candidate assertions for Decision 252. The JSON was parsed and its declared count matches the 32 records.
9. Transcribed 137 candidate rows from Decision 250 Table 23 (printed pp.242–248) into JSON with quantity/CAS fields. JSON/count validated (137/137); Arabic transcription remains blank for rows 64–137, and CAS values for rows 47–48 remain unresolved rather than guessed.
10. Located the Ministry's official clarification dated 2026-10-27 about Decision 249. It says existing specialists/acquired positions should not be harmed and directs the competent administration to issue periodic circulars.
11. Targeted searches on 2026-10-29 did not locate a separate public implementation circular. This is “announced but not located”, not proof none exists.

## Subtask status

| Subtask | Status | Completion estimate | Remaining gate |
|---|---|---:|---|
| Alternative source inventory | Added and linked | 100% for the inventory document | New source leads can still be added |
| 35-item cross-instrument discrepancy checklist | Structured and count-validated | 100% for checklist structure | Legal text still needs primary-file match |
| Decision 249 scan discovery | pp.19–44 and Tables 1–3 located | 75% source discovery | Official PDF hash, exact Table 1/2 transcription, currentness and counsel |
| Decision 250 source discovery | Full secondary transcription found; Tables 1–24 and register templates exposed; missing pp.296–370 covered at text-discovery layer | 90% source discovery | Structured extraction of all rows, primary Gazette comparison, official PDF bytes/hash, currentness and counsel |
| Decision 251 scan extraction | pp.371–377 indexed; Articles 1–11 summarized and 17 candidate assertions structured | 70% extraction work | Official-file comparison, currentness, counsel, exact procedural day-count check |
| Decision 252 scan extraction | pp.378–398 indexed; page-pinned article map plus 32 numerical candidates structured | 75% extraction work | Official-file comparison; ambiguous table cells; currentness and counsel |
| Decision 249 implementation circulars | Ministry says circulars will be issued; separate circular not located publicly | 35% | Find a public circular or preserve the unresolved gap |
| Original Gazette PDF hash / full official-byte comparison | Not completed | 0% | Obtain original PDF bytes through ordinary authorized access |
| 311-row candidate JSONL comparison | Candidate file unavailable in current runtime | 0% | User must provide original JSONL for exact comparison; do not reconstruct it |
| Qualified counsel approval | No review recorded | 0% | Qualified Egyptian labour/OSH lawyer review |
| Reuse/access assessment | Open | 0% | Assess rights and conditions for each source/asset before redistribution |

Percentages above describe the completion of the *subtask work product*, not legal certainty. They do not add up to the headline score.

## Non-negotiable release state

- Candidate numerical ledger: 120/120 candidate entries exist, but this is not verification.
- Lawyer-approved numerical candidates: 0/120.
- Fully currentness-reviewed numerical candidates: 0/120.
- Eligible for authoritative retrieval: 0/120.
- Decisions 248–252: full secondary text is now available for Decision 250; the other decisions remain partially transcribed/indexed. No complete comparison to the original official PDF and no counsel approval have been recorded.
- No restricted request-a-copy route was bypassed.
- The PR is open and draft; the current head had no reported combined-status checks when checked.

## Next highest-value actions

1. Finish transcribing Decision 249 Table 1 and Table 2, especially risk classification and required OSH staffing counts, without guessing low-resolution cells.
2. Use the newly found Riwaq transcription to structure Table 24 (printed pp.249–360) and validate all rows/units/identifiers; then compare high-risk values and Table 23 against the official Gazette when bytes become available. Keep every exposure limit source-pinned.
3. Complete the remaining legible Decision 252 tables and verify ambiguous cells from higher-resolution images or official file.
4. Continue targeted public searches for Decision 249 implementation circulars; if none surface, keep the gate explicitly unresolved.
5. Reconcile all reproduced scans to the official Gazette file if available and record the file hash only after the bytes are actually obtained.
6. Do not activate rules until currentness, source-use and qualified counsel gates pass.

## Current conclusion

The alternate-source work has moved Decision 250 from partial page images to a full secondary text transcription, including the previously missing printed pages 296–370. It has **not** made the five decisions fully verified law for the product. The honest overall readiness estimate therefore remains **7%**.
