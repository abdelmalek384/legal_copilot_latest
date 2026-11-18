# Research Agent 1 — checkpoint 149: Law 142/1964 territorial commencement chain and Gazette-text conflicts (18 November 2026)

## 1. Newly registered decisions 6910/2025 and 6911/2025

Two territorial commencement decisions under Law 142/1964 were located in the full SIS-hosted Egyptian Proceedings issue 295 (30 December 2025) and corroborated against official Amiri Press searchable text.

### Decision 6910/2025 — Sohag (Decision 2134/2001 track)

- Register ID: **EG-0196**.
- Official Amiri Press searchable text: https://www.alamiria.com/Sec/TashTxt?id=TRqav4vXATE%3D
- SIS issue 295 PDF: https://mediadr.sis.gov.eg/bitstream/handle/123456789/117440/WQ295_20251230_9062.pdf?isAllowed=y&sequence=2
- Issued 19 November 2025; appears in issue 295 dated 30 December 2025.
- Applies to the Al-Saqriya and Kom Badar cadastral sections in Sohag under the Decision 2134/2001 designation series.
- **Date discrepancy:** Amiri Press text says postponement from 2 December 2025 to 1 December 2026, with Article 19 settlement forms for two months from 2 December 2025. The SIS PDF extracted text at lines 106–112 instead reads 2 February 2025 to 1 June 2026 and 2 February 2025 as the form period/effective date. Those SIS extracted dates appear inconsistent with the issue/decision chronology and Amiri Press text. PDF page-image retrieval failed in this session. Keep both source readings and do not certify the date until printed page image or an authorized certified copy is inspected.

### Decision 6911/2025 — Sohag, Aswan, Damietta and Ismailia (Decision 2089/2004 track)

- Register ID: **EG-0197**.
- Official Amiri Press searchable text: https://www.alamiria.com/Sec/TashTxt?id=3v6fSYjAkYU%3D
- SIS issue 295 PDF: same issue-level PDF above.
- Issued 19 November 2025; appears in issue 295 dated 30 December 2025.
- Applies to the listed cadastral sections in Damietta, Aswan, Ismailia and Sohag under the Decision 2089/2004 designation series.
- The Amiri Press text and SIS extracted issue text show postponement from **2 December 2025 to 1 December 2026**, with Article 19 settlement forms accepted for two months from 2 December 2025 and commencement from 2 December 2025.
- The issue text lists the affected Sohag sections and relevant areas in Damietta, Aswan and Ismailia; spelling and full territorial schedule still require page-image verification.

Both are territorial postponements under Law 142/1964. They do not amend the substantive title, registration-effect or evidentiary rules. They must be represented as dated, section-specific applicability events, not a single nationwide commencement status.

## 2. Reconciliation with 2026 Decisions 5207/2026 and 5208/2026

- Decision 5207/2026 is recorded as EG-0187 and concerns specified sections in Qena and Luxor under the Decision 1725/2006 track, with a 1 October 2026–1 October 2027 postponement.
- Decision 5208/2026 is recorded as EG-0188 and concerns specified sections in Sohag, Aswan and Damietta under the Decision 1538/2003 track, with dates through 30 September 2027.
- The official Amiri Press searchable text for Decision 5208/2026 is https://www.alamiria.com/Sec/TashTxt?id=P%2F4+rBlZm44%3D; DSpace metadata identifies Gazette supplement issue 244 dated 3 November 2026 and the same decision number.
- A separate third-party Gazette-mirror PDF indexed as issue 244 (URL path ending `2026-11-3-2026-5208.pdf`) exposes extracted text headed **Decision 5280/2026**, not 5208/2026. The Amiri Press text and DSpace item metadata both say 5208/2026. Treat the third-party mirror's number as a source/text mismatch; do not create a separate Decision 5280 instrument from that one anomalous mirror. Obtain the DSpace original bundle/page image to resolve.
- The 2026 decisions may overlap with earlier area-specific Decision 6910/6911 schedules. No non-overlap or complete territory matrix is certified yet; map exact cadastral sections and source dates before deciding which prior postponement is superseded for a given section.

## 3. Acquisition and permission register updates

- Added EG-0196 and EG-0197 to `data/research/egypt_initial_statute_acquisition_register_2026-11-17.csv`.
- Acquisition register now contains **193 data rows**, **193 unique IDs**, and **0 duplicate IDs**.
- Missing numeric IDs EG-0076–EG-0079 remain historical gaps pending reconciliation.
- Added one source-specific provenance assessment for SIS issue 295/2025 to `docs/source_permission_register.json`.
- Source-permission register now contains **54 unique source records**, no duplicate source IDs.
- SIS issue 295 source collection permission and commercial reuse permission remain **unknown**.
- Both new acquisition records retain `lawyer_reviewed=false` and `rights_cleared=false`.

## 4. Separate corpus metrics (not conflated)

| Metric | Recorded value | Qualification |
|---|---:|---|
| Acquisition-register data rows | **193** | Catalogue records, not unique base laws |
| Unique acquisition IDs | **193** | No duplicate IDs |
| Source-permission records | **54** | Not permissions granted |
| Core complete article provisions | **1,370** | Civil Code 1,093 + Evidence Law 163 + Building Law 114 |
| Core statutes with article-number extraction complete | **3** | Law 131/1948, Law 25/1968, Law 119/2008 |
| Full regulation texts identified | **12** | Earlier normalized snapshot; source quality varies |
| Further subordinate decisions amending regulations | **13** | Earlier snapshot; not all primary Gazette texts |
| Amending-law records identified | **25** | Earlier snapshot; compound rows require normalization |
| Relevant SCC cases identified | **11** | Earlier normalized snapshot; later source upgrades remain separate |
| New base laws in this checkpoint | **0** | — |
| New amending laws in this checkpoint | **0** | — |
| New executive regulations in this checkpoint | **0** | — |
| New judicial decisions in this checkpoint | **0** | — |
| New subordinate ministerial decisions in this checkpoint | **2** | Decisions 6910/2025 and 6911/2025 |
| New complete full texts with all annexes | **0** | Operative decision text located; image validation/complete schedules incomplete |
| New article provisions transcribed | **0** | No statutory article-text additions |

## 5. Updated completion estimates

- Core article-number extraction: **100%** for the three defined core statutes, subject to source-image and version validation.
- Broader civil/property/contract corpus: **15% provisional**.
- Whole Egyptian legal corpus: **2% provisional**.

These estimates remain unchanged: two territorial decisions and one provenance record do not materially change breadth coverage. There is no validated national denominator.

## 6. Next work

1. Obtain page images or authorized original issue 295 PDF and resolve Decision 6910 date conflict.
2. Verify every cadastral section and date in Decisions 6910/2025 and 6911/2025 against printed page images.
3. Obtain original DSpace issue 244 PDF for Decision 5208/2026 and resolve the 5208/5280 third-party-mirror discrepancy.
4. Build a section-level temporal matrix across Decisions 2134/2001, 2089/2004, 1538/2003 and 1725/2006, with every extension, start/end date and Article 19 settlement window.
5. Continue original Gazette acquisition for the seven priority instruments and judgments; preserve restricted-access blockers and do not bypass them.
6. Continue full Arabic text extraction and article-level amendment graph work for Laws 131/1948, 25/1968, 119/2008, 114/1946, 142/1964 and 143/1981.

## 7. Rights and verification

No lawyer verification, commercial reuse permission, certified original publisher authentication, or permission for bulk retrieval is claimed. Official publisher text, official repository metadata, and third-party Gazette mirrors remain distinct source tiers.


## 8. Follow-up: Decision 6909/2025 and correction of the 5208/5280 mirror anomaly

### Decision 6909/2025 — Assiut and Aswan

- Added to acquisition register as **EG-0198**.
- Official Amiri Press searchable text: https://www.alamiria.com/Sec/TashTxt?id=rM0p75C16KY%3D
- Gazette issue 295/2025 SIS PDF: https://mediadr.sis.gov.eg/bitstream/handle/123456789/117440/WQ295_20251230_9062.pdf?isAllowed=y&sequence=2
- Issued 19 November 2025; issue 295 dated 30 December 2025.
- Postpones the Decision 2456/2003 cadastral sections in Assiut (El-Ghanayem, El-Badari, El-Motiea, Abnoub) and Aswan from **1 December 2025 to 30 November 2026**; Article 19 settlement forms accepted for two months from 1 December 2025; effective 1 December 2025.
- A successor 2026 decision for these exact Decision 2456/2003 areas has not yet been located. Decisions 5207/5208/2026 relate to different designation tracks and section lists; do not assume they renew the 6909 areas.

### Corrected interpretation of the 5208/5280 anomaly

The Amiri Press searchable text and DSpace issue 244 metadata both identify the cadastral postponement instrument as **Decision 5208/2026**. A third-party mirror of issue 244 had extracted text that labelled the heading “5280/2026”. A separate official DSpace item for issue 248, dated 8 November 2026, identifies genuine Decisions **5280/2026 and 5281/2026** as different Ministry of Justice instruments. Secondary reports identify those two as establishing new notarization branches (Suez Canal Club, Ismailia; and Gezira Club, 6 October), not cadastral postponements.

Therefore:
- Do not relabel the issue 244 cadastral postponement as 5280.
- Do not treat the issue 248 branch-establishment Decision 5280 as the same act as Decision 5208.
- Preserve the issue 244 mirror's 5280 heading as a likely source/OCR/mirror misattribution pending the original DSpace page image.
- Decision 5281/2026 in issue 248 is also a distinct branch-establishment decision, not the 2025 cadastral Decision 5281/2025.

### Updated register totals

- Acquisition register: **194 data rows**, 194 unique IDs, zero duplicate IDs.
- Source-permission register: **54 unique source records** (unchanged; issue 295 source record already covers Decisions 6909–6911).
- Core article provisions remain 1,370; no article text was added.
