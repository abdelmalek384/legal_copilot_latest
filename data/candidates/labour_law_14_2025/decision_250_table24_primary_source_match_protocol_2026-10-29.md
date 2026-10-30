# Decision 250/2026 Table 24 — primary-source matching protocol

**Purpose:** Convert the 642 currently extracted secondary-transcription candidates into auditable, row-by-row comparisons when the original Official Gazette PDF is available.  
**Current status:** Template/protocol only. No official PDF hash or Table 24 row match is claimed.

## 1. Preserve and identify the source file

1. Obtain the original Official Gazette supplement PDF through ordinary authorized access. Do not use a secondary reproduction as the primary file and do not bypass a request-a-copy control.
2. Keep the original bytes unchanged in a read-only location.
3. Record the exact source URL or acquisition route, retrieval date/time, file name, byte size, Gazette issue/supplement details, and SHA-256 of the actual PDF bytes.
4. Verify that the file is the supplement containing Decision 250/2026 and the Table 24 pages. The known secondary page map places Table 24 around printed pages 249–360; treat that as a locator, not proof that the uploaded PDF has the same pagination.
5. If a different PDF version, scan, or pagination is received, create a new source record and hash. Never overwrite the earlier source identity.

Example local hash command (run on the actual original PDF):
```bash
shasum -a 256 "/path/to/original-gazette.pdf"
```

## 2. Compare each candidate row

**Important fidelity warning:** The candidate field named `raw_limit_and_note_text` is not guaranteed to be verbatim. It may contain manually assembled, translated, normalized or text-layer fragments. Treat it as a comparison lead only; transcribe the official page independently and compare field by field.

For each numbered Table 24 entry, including the newly extracted secondary-source candidates through row 642:

1. Open the official page image containing the row. Record both the PDF page index and the printed page number if they differ.
2. Compare the Arabic label, English label, CAS identifier(s), formula, molecular weight, every numeric limit, units, footnote markers, classification labels, and health-effect text.
3. Preserve parent/child relationships for isomers, salts, oxidation states, particle fractions, and group-level entries. Never assign a parent value to a child or a sibling's limit to another chemical.
4. Keep air-exposure and surface limits separate. Confirm whether the table column means TWA, STEL, ceiling, inhalable/respirable fraction, vapor, skin notation, or a surface sampling limit before normalizing.
5. Record a short evidence excerpt or precise image/page locator for the comparison. Do not replace the original candidate transcription; record the result alongside it.
6. If the row is blurry, cropped, contradictory, or cannot be located, mark it unresolved. Do not guess from a safety data sheet or model memory.

## 3. Allowed match outcomes

- **exact_match:** Every legally/materially significant field agrees with the official page.
- **formatting_only_difference:** Only typography/spacing/subscript formatting differs; both the raw text and reason for normalization are recorded.
- **material_mismatch:** CAS, formula, label, limit, unit, footnote, or legal meaning differs.
- **unreadable:** Official scan does not support a reliable transcription.
- **not_found:** No corresponding entry located after a documented page/range search.
- **not_started:** No comparison performed yet.

Only `exact_match` or an individually documented `formatting_only_difference` may proceed to currentness and counsel review. Neither outcome alone makes the row authoritative.

## 4. Separate release gates

These checks are distinct and must not be collapsed into a single “verified” flag:

1. **Primary-source identity:** original file URL/route, retrieval date, byte size and SHA-256.
2. **Text match:** row-by-row official page comparison.
3. **Currentness:** amendments, corrigenda, repeal/replacement and effective-date status checked as of a recorded date.
4. **Source-use review:** legal text status and the source website's terms/compilation rights assessed separately.
5. **Qualified Egyptian OSH counsel:** approve the exact row and its interpretation, or reject/qualify it.
6. **Retrieval eligibility:** enable only after all required gates pass; candidate-only rows remain unavailable to authoritative answer generation.

## 5. Priority order

1. All rows with malformed or suspicious CAS/formula/decimal/unit strings.
2. All surface-limit rows and entries with multiple limits/units in one flattened line.
3. High-risk carcinogens, toxic metals, sensitizers and other entries where a wrong number could create immediate safety harm.
4. Parent/child groups, isomers, salts and mixed-substance rows.
5. Rows that secondary text says were removed, consolidated, or superseded.
6. Remaining rows in numerical order.

This prioritization determines review order, not legal importance or release eligibility. Every row still needs its own recorded outcome.

## 6. Required fields per row

The primary-match register generator supplies one row-level record per candidate. Populate these only from actual evidence:

- original Official Gazette PDF SHA-256 and source identity
- PDF page index and printed page number
- official page/image locator
- candidate-to-official match outcome
- exact field-level differences and any approved formatting normalization
- currentness result and review date
- source-use result
- counsel reviewer, decision, date, and qualification/notes
- retrieval-eligibility decision and reason

Never fill missing values by inference. Keep the register and the original candidate batches versioned together.

## Release stop conditions

Any unresolved mismatch, unverified numeric limit, unknown unit/column, uncertain currentness, unresolved source-use question, or missing counsel approval blocks authoritative retrieval of that row. A review session in the app is a separate final acceptance gate; it does not replace primary-source matching.


## 2026-10-30 extraction extension

A secondary-source candidate batch now covers rows 618–642, with source-line locators 5514–5555. The entries include group headings and numbered subentries (including rhodium, crystalline silica and silicon carbide groupings). These have been preserved as separately numbered candidates without inferring hierarchy or assigning parent limits to subentries. The candidate batch remains secondary-only, has no official Gazette match or PDF hash, and every row remains pending official match. The primary-source comparison protocol and all release gates remain unchanged.
