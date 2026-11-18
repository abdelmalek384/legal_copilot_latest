# Research Agent 1 — checkpoint 148: Law 70/1964 tariff schedule acquisition and cumulative status (18 November 2026)

## 1. New instrument acquisition

Two previously unregistered ministerial decisions were identified and added to the acquisition register. They implement Article 21(II) of Law 70/1964 by setting annual minimum values for rapid-transport-vehicle instruments. They are subordinate tariff decisions, not amendments to the statute.

### Decision 278/2025 — 2025 schedule

- Instrument ID: **EG-0194**.
- Official Gazette: Egyptian Proceedings issue 39, 17 February 2025.
- Official SIS-hosted issue PDF: https://mediadr.sis.gov.eg/bitstream/handle/123456789/89851/WQ39_20250217_4123.pdf?isAllowed=y&sequence=2
- Decision date: 15 January 2025.
- Article 1 establishes minimum vehicle values by attached schedule for instruments under Article 21(II) of Law 70/1964.
- Article 2 applies the schedule through **31 December 2025**.
- Article 3 makes it effective from issuance, **15 January 2025**.
- The attached table values still require page-image extraction and validation. Do not carry this schedule into 2026.

### Decision 7657/2025 — 2026 schedule

- Instrument ID: **EG-0195**.
- Official Amiri Press searchable text portal: https://www.alamiria.com/Sec/TashTxt?id=99IsDvXE8+o%3D
- Decision date: 25 November 2025.
- Article 1 establishes minimum values by attached schedule for instruments under Article 21(II) of Law 70/1964.
- Article 2 applies the schedule for one year, **1 January–31 December 2026**.
- Article 3 makes it effective **1 January 2026**.
- Secondary publication report identifies Egyptian Proceedings issue 16, 20 January 2026: https://www.cairo24.com/2356386
- Amiri Press heading and operative text identify Decision **7657/2025**. One passage in the secondary report inconsistently says 7656; retain the official publisher's number.
- The official publisher page exposes the three operative articles, but the attached schedule values and full issue PDF bytes were not obtained. No vehicle-value figure is certified in this checkpoint.

## 2. Law 70/1964 amendment-chain correction

The earlier checkpoint's enumerated chain omitted Law **163/2019**. The consolidated transcription records that Law 163/2019 added an item to Table B (non-registrable instruments), Official Gazette issue 50 supplement, 12 December 2019. Law **67/2021** then replaced the term “contracting companies” with “companies” in the item preceding the last item of Table B, Official Gazette issue 23 bis, 13 June 2021.

The statutory amendment chain now includes at least:
- Law 94/1980 (Articles 21 and 22);
- Law 6/1991 (Articles 21, 25, 26, 27, Article 19 additions and associated repeal/additions);
- Law 224/1996 (Article 24 bis and 34 bis);
- Law 225/1996 (Article 21 table item);
- Law 9/2003 (Article 34 bis 2);
- Law 3/2004 (Article 34 bis 3);
- Law 83/2006 (Article 19 and cross-statute amendments to Law 142/1964);
- Law 163/2019 (Table B addition);
- Law 67/2021 (Table B terminology change).

Constitutional Case 65/17 (1 February 1997) affects the pre-Law 6/1991 valuation regime; Case 2/24 (14 December 2003) invalidates only the absolute no-refund bar in Article 30 where the service has not been completed. Neither is a statutory amendment; keep judgments in a separate legal-effect layer.

Decisions 2936/1992 and 5424/2006 are tariff/valuation implementation decisions. Decisions 278/2025 and 7657/2025 are annual vehicle-valuation schedules. Do not merge these subordinate instruments into the Law 70 amendment count.

## 3. Register changes and integrity

- Acquisition register file: `data/research/egypt_initial_statute_acquisition_register_2026-11-17.csv`.
- Added exactly two records: EG-0194 and EG-0195.
- Current data rows: **191**.
- Unique instrument-record IDs: **191**.
- Duplicate IDs: **0**.
- Numeric gaps EG-0076–EG-0079 remain unresolved; do not fill without source evidence.
- Source-permission register: `docs/source_permission_register.json`.
- Added one source-specific record for SIS issue 39/2025, Decision 278/2025: **53 source records**, 53 unique source IDs, no duplicate source IDs.
- Collection permission and commercial reuse permission remain unknown for the new SIS source. The existing Amiri Press portal source entry remains source-specific and does not grant reuse permission.
- Both new acquisition rows retain `lawyer_reviewed=false` and `rights_cleared=false`.

## 4. Separate cumulative counts and what they mean

| Metric | Current recorded value | Scope / qualification |
|---|---:|---|
| Acquisition-register data rows | **191** | Catalogue records, not unique base laws |
| Unique acquisition IDs | **191** | No duplicate IDs |
| Source-permission records | **53** | Permission assessments, not permissions granted |
| Core complete article provisions | **1,370** | Civil Code 1,093 + Evidence Law 163 + Building Law 114 |
| Core base statutes with article-number extraction completed | **3** | Law 131/1948, Law 25/1968, Law 119/2008 |
| Full regulation texts identified | **12** | Earlier normalized snapshot; source tiers vary |
| Further subordinate decisions amending regulations | **13** | Earlier normalized snapshot; not all original Gazette texts |
| Amending-law records identified | **25** | Earlier snapshot; compound entries need splitting/normalization |
| Relevant Constitutional Court cases identified | **11** | Earlier snapshot; seven had direct official SCC pages/records at that point |
| New instruments in this checkpoint | **2** | Both ministerial annual tariff/valuation decisions |
| New base laws | **0** | — |
| New amending laws | **0** | — |
| New executive regulations | **0** | — |
| New judicial decisions | **0** | — |
| New full legal texts with complete annexes | **0** | Operative Decision 7657 text found, but annex table not acquired |
| New unique article provisions transcribed | **0** | No article-text additions |

The 1,370 core provisions are unique by statute plus article identifier. They are not a count of current consolidated article versions. Repealed Civil Code base-text article numbers are excluded. Evidence Law Article 148 bis is included as a distinct provision.

The cumulative counts of base laws, amending laws, executive regulations, judicial decisions and full texts must remain separate. Do not infer them from the 191 acquisition rows. The 12 regulation and 25 amending-law values are historical normalized snapshots, not newly re-audited totals in this checkpoint.

## 5. Completion percentage

- Core article-number extraction: **100%** for the three defined core statutes, subject to OCR/page-image and amendment/currentness validation.
- Broader civil/property/contract corpus: **15% provisional**.
- Whole Egyptian legal corpus: **2% provisional**.

The last two figures remain unchanged. Two new tariff instruments and one provenance record do not justify increasing a breadth estimate. There is no validated national denominator; percentages are directional, not statistical coverage claims.

## 6. Remaining priority work

1. Obtain Decision 7657/2025 Official Gazette issue 16 PDF and all attached 2026 vehicle valuation tables; visually inspect and extract every category/value.
2. Obtain original Gazette issue 39/2025 and inspect Decision 278/2025's 2025 schedule for historical comparison.
3. Obtain authorized Amiri Press originals for Laws 114/1946, 142/1964, 68/1947 and 70/1964; current available scan copies are secondary-hosted.
4. Obtain original Gazette bundles for Law 168/2025 and Decision 480/2026; settle Decision 480's commencement and filing deadline with authoritative guidance.
5. Complete original Gazette judgment scans for Cases 42/17 and remaining rent-law decisions; preserve official SCC HTML pages as distinct source tiers.
6. Finish amendment/version graphs for Laws 143/1981, 114/1946, 142/1964 and 70/1964.
7. Complete Law 119/2008 / Decision 144/2009 amendment diffs and visual checks of all 185 regulation articles, forms and schedules.
8. Complete Civil Code and Evidence Law page-image validation and historical amendment/repeal mapping.
9. Reconcile missing IDs EG-0076–EG-0079 against repository history without inventing records.

## 7. Rights and verification declaration

No lawyer verification, commercial reuse permission, certified publisher authentication, or permission for bulk retrieval is claimed. Publicly accessible official-hosted text and Gazette reproductions do not imply a reuse licence. Preserve source-specific provenance and rights states.
