# Research Agent 1 — repository audit and priority continuation (2026-11-18)

## Scope and method

This checkpoint records a read-only audit of the current repository state and targeted source research. The master index, checkpoint 85–88 files, checkpoint 92, the checkpoint 93 reconciliation, checkpoint 94 scan-acquisition note, the Civil Code deduplication record, the Law 168/2025 deadline calculation, the four-statute Gazette scan verification note, the Constitutional Court scan note, the acquisition CSV and source-permission JSON were inspected. The repository's later index contains embedded/supplemental sections for subsequent checkpoint work; those were treated as supplements, not as separate legal instruments.

No restricted DSpace download was bypassed. No new legal instrument or article text was added in this audit. This checkpoint is a source/provenance and count reconciliation only.

## 1. Current register audit

### Acquisition register

File: `data/research/egypt_initial_statute_acquisition_register_2026-11-17.csv`

- Data rows: **189** (header excluded).
- Columns: **12**.
- Unique instrument IDs: **189**.
- Duplicate IDs: **0**.
- Highest ID: **EG-0193**.
- Numeric ID gaps: **EG-0076, EG-0077, EG-0078, EG-0079**.
- IDs are not a contiguous serial counter: missing IDs are historical gaps, not permission to create speculative rows.
- All rows observed retain `lawyer_reviewed=false` and `rights_cleared=false`.

This supersedes older checkpoint counts of 172, 182, 184 and 187 rows. Those counts were accurate snapshots at earlier points, not the present file count. The current file has 189 data rows, including EG-0192 and EG-0193 for the two judgment scan upgrades.

### Source-permission register

File: `docs/source_permission_register.json`

- Assessment date: **2026-11-18**.
- Source records: **52**.
- Permission state remains source-specific; no general collection or commercial reuse permission is implied by public availability, Gazette reproduction, or repository visibility.
- No source permission was upgraded in this audit.

## 2. Four historical Gazette statutes — scan status

All pages of the four available Manshurat-hosted PDF scan reproductions were visually inspected, including mastheads and printed pagination:

| Instrument | Gazette issue/date shown in scan | Pages inspected |
|---|---|---:|
| Law 114/1946 | Egyptian Proceedings issue 85, 24 Aug 1946 | 6 |
| Law 142/1964 | Official Gazette issue 69, 24 Mar 1964; pp. 781–787 | 7 |
| Law 68/1947 | Egyptian Proceedings issue 58, 3 Jul 1947; pp. 2–3 | 2 |
| Law 70/1964 | Official Gazette issue 67, 22 Mar 1964; pp. 644–654 | 11 |

These are scans of printed Gazette pages hosted by a secondary legal archive. They are not Amiri Press-hosted original digital files; no publisher-certified hash, formal authentication, or commercial reuse permission is available. The corresponding acquisition rows are EG-0144, EG-0145, EG-0150 and EG-0151. Do not create duplicate instrument rows.

## 3. State private-property law and Decision 480/2026

### Source status

- **Law 168/2025:** Gazette issue 32 bis (و), 13 Aug 2025. DSpace identifies the Amiri Press original bundle (294.4 KB), but download is request-only. A ten-page printed Gazette scan reproduction hosted by Vetogate has been visually inspected; a Court of Cassation-hosted reproduction and secondary searchable text are available.
- **PM Decision 200/2026:** Gazette issue 3 bis (A), 18 Jan 2026. A complete official SIS-hosted Gazette PDF is publicly readable (562 extracted lines), including issuing provisions, all 20 regulation articles and forms. Article 4 makes it effective on **19 Jan 2026**. The separate Amiri Press DSpace bundle remains request-only.
- **Presidential Decision 480/2026:** Gazette issue 45 bis (ج), 10 Nov 2026. DSpace confirms the Amiri Press original bundle (178.37 KB), but download is request-only. The two operative provisions are reproduced by secondary media; no original PDF bytes were obtained.

### Deadline computation — unresolved

Law 168/2025 Article 3 measures the six-month application period from commencement of the Executive Regulation. Decision 200/2026 took effect on 19 Jan 2026. Applying the general month-computation rule (excluding the triggering day) gives an initial period ending at the end of **19 Jul 2026**.

Decision 480/2026 says only that the Article 3(1) period is extended for another equivalent period. It does not expressly specify the renewed period's start date or how the apparent gap after 19 Jul 2026 is treated.

- **19 Jan 2027** is the conditional date if the extension runs consecutively from the original expiry.
- **10 or 11 May 2027** are alternative conditional dates if a new six-month period runs from publication/effectiveness.
- **No final application deadline is certified.** Obtain the original Decision 480 issue and an official implementation circular or binding judicial interpretation before selecting a date. Do not treat applications in the gap as definitely valid or invalid.
- Decision 480 expressly refers to Article 3(1); it does not expressly extend the separate Article 11 period.

Official DSpace metadata: https://dspace.id.com.eg/items/03b3721d-4847-4be0-8130-5d4bf38da540/full

## 4. Constitutional Court judgments and rent-law status

### Existing primary/scan upgrades

- **Case 10/35 (2 Jun 2018):** ten-page printed Gazette judgment scan visually inspected; Gazette issue 22 bis (ط), 6 Jun 2018, pp. 16–25. Declared Law 142/1964 Articles 21 and 24 unconstitutional; Article 23 and Justice Decision 553/1976 fell consequentially. Secondary-hosted printed Gazette scan, not Amiri Press digital original.
- **Case 24/20 (9 Nov 2024):** fourteen-page printed Gazette judgment scan visually inspected; Gazette issue 45 bis (A), 10 Nov 2024, pp. 17–30. Invalidated the first paragraphs of Law 136/1981 Articles 1 and 2 insofar as they fixed annual rent for residential premises; effect was deferred to the day after the end of the then-current ordinary parliamentary session. This is not a blanket invalidation.
- **Case 101/26 (1 Feb 2009):** official SCC-hosted judgment page located. It invalidated Article 22(1) of Law 143/1981. Official SCC URL: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3204_26_101_1_2.html . The official page records publication in Gazette issue 7 bis (A), 15 Feb 2009, and an erratum.
- **Case 42/17 (6 Jun 1998):** available full text remains a secondary reproduction; it reports invalidation of Law 142/1964 Article 37(2) and consequential fall of Article 38. Original Gazette scan remains outstanding; reported Gazette reference is issue 35 supplement, 18 Jun 1998.

### Remaining rent-law judgments

The prior judgment scan note identifies rent-law Cases **81/19** and **108/19** as further original Gazette scan priorities. Retrieve their official SCC texts and Gazette publication pages; retain each judgment's precise challenged provision, operative effect and temporal qualification. Do not merge judgments into statutory amendment records.

Official Case 101/26 source corroboration: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3204_26_101_1_2.html

## 5. Civil Code Law 131/1948 — extraction status correction

The later master-index/deduplication record reports **1,093 unique non-repealed article provisions**, all with complete text. The statutory numbering runs through Article 1149; the 56-number difference consists of the repealed base-text ranges Articles 54–80 (27) and 389–417 (29). Article 766(2), previously partial, was recovered from official PDF page images and is included. No non-repealed article-number gaps remain under the repository's current deduplication method.

Important qualifications:
- The extracted text is the government-hosted ETA base-law PDF, not an original 1948 Gazette scan.
- Complete base-text extraction is not a current consolidated code.
- Amendment, constitutional judgment, special-law displacement and repeal/version metadata remain to be reconciled article by article.
- OCR/page-image review and provenance links remain necessary before production use.

## 6. Evidence Law 25/1968 — extraction status correction

The repository's later checkpoints supersede the earlier partial status:

- Full Arabic extraction now covers Articles **1–162**, including inserted Article **148 bis**.
- Checkpoint 112: Articles 1–59.
- Checkpoint 113: Articles 60–117.
- Checkpoint 107: Articles 125–162; Articles 118–124 were separately source-compared and incorporated.
- The statute's terminal enacted article is treated as Article 162. A WIPO OCR line labelled Article 163 duplicates Article 153 and is not counted.
- The official Ministry of Finance 12-page Gazette reproduction is located; 11 of 12 pages were visually inspected. PDF index 4 did not render, and the missing page/image comparison remains outstanding.
- Amendment instruments located: Laws 54/1974, 23/1992, 18/1999 and 76/2007. Original amendment Gazette scans and complete historical article diffs remain outstanding.

Therefore, the requested Articles 1–117 are text-extracted, but source-image verification and amendment versioning are incomplete. Do not describe the entire law as fully verified.

## 7. Building Law 119/2008 and Decision 144/2009

- Law 119/2008: official Ministry of Housing-hosted Gazette reproduction, issue 19 bis (A), 11 May 2008; searchable text through substantive Articles 1–114. Selected OCR-corrupted provisions remain quarantined for visual correction.
- Law 23/2015: amendment identified; original Gazette scan and full article-by-article substitution comparison remain outstanding.
- Decision 144/2009: Executive Regulation, Gazette issue 82 supplement (A), 8 Apr 2009. Full regulation text is available through a secondary-hosted PDF; original Gazette scan and complete forms/schedules visual review remain outstanding.
- Later regulation amendment leads already in the acquisition register include Decision 954/2022 (replacing Articles 135 bis and 139 bis), Decision 120/2025 (Article 26(5)), and Decision 1505/2025 (Articles 43 and 50). Official SIS Gazette issue PDFs are identified for Decisions 120/2025 and 1505/2025; image/OCR comparison and full temporal versioning remain open.
- Do not count these source upgrades as new instruments where the instrument is already registered.

## 8. Amendment-chain findings requiring integration

### Law 114/1946

The repository identifies Laws 223/1996, 186/2020, 5/2021 and 9/2022 among the key amendment/deferred-commencement instruments, with Justice Decision 2332/2022 implementing the 2022 amendments to the regulation. Law 186/2020 inserted Article 35 bis; Law 5/2021 deferred its operation; Law 9/2022 materially rewrote multiple application/procedure provisions. The exact complete chain, historical article versions, and the relationship between amendment, postponement and effective dates remain to be represented in a version graph.

Official government-hosted Law 186/2020 Gazette reproduction: https://www.investinegypt.gov.eg/PublishingImages/Lists/LawsAndRegulations/AllItems/%D8%AA%D8%B9%D8%AF%D9%8A%D9%84%20%D8%A8%D8%B9%D8%B6%20%D8%A3%D8%AD%D9%83%D8%A7%D9%85%20%D9%82%D8%A7%D9%86%D9%88%D9%86%20%D8%A7%D9%84%D8%B4%D9%87%D8%B1%20%D8%A7%D9%84%D8%B9%D9%82%D8%A7%D8%B1%D9%8A%20%D8%A8%D8%A7%D9%84%D9%82%D8%A7%D9%86%D9%88%D9%86%20186%20%D9%84%D8%B3%D9%86%D8%A9%202020.pdf

### Law 142/1964

Law 142/1964's executive regulation is Decision 825/1975, amended by Decision 11264/2016 and other identified decisions. Constitutional Case 10/35 removes Articles 21 and 24, with consequential fall of Article 23 and Decision 553/1976. The complete amendment/commencement chain and article-level historical versions remain open.

### Law 143/1981

Law 11/2024 amended Article 11(2) and Article 12(2), effective 25 Feb 2024. The official Ministry of Agriculture legislation PDF for the base law is located. Case 101/26 invalidated Article 22(1). A complete amendment/repeal/version graph is still required; do not treat the 2024 amendment as the only amendment.

Law 11/2024 text metadata: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/24-02-2024/no-11?id=2111874&sub=10757134

## 9. Deduplicated category counts and status

These counts are deliberately kept in separate dimensions:

| Metric | Current audited/recorded value | Meaning |
|---|---:|---|
| Acquisition register rows | 189 | Catalogue records, not all collected texts |
| Unique acquisition IDs | 189 | No duplicates in current CSV |
| Source-permission records | 52 | Provenance/permission questions, not permissions granted |
| Civil Code unique non-repealed article provisions | 1,093 | Complete base-text extraction set, not consolidated/current law |
| Evidence Law article provisions | 163 | Articles 1–162 plus inserted Article 148 bis; OCR/source verification remains |
| Gazette scan reproductions visually inspected for four priority statutes | 4 | 26 pages total, secondary-hosted |
| Constitutional Court Gazette scan reproductions visually inspected in the judgment note | 2 | Cases 10/35 and 24/20, 24 pages total |
| Official original Amiri Press binaries obtained for the four historical statutes | 0 | Only secondary-hosted page scans inspected |
| Official original Decision 480/2026 PDF obtained | 0 | DSpace bundle request-only |
| Lawyer-verified legal texts | 0 | No counsel sign-off |
| Commercial reuse permissions established by this audit | 0 | No permission inferred |

Instrument-category totals are not recomputed here because the register is a catalogue of instruments with heterogeneous source states; count base laws, amendments, regulations and judicial decisions separately in the next normalized inventory report. Do not add article provisions, full-text files or source records to the instrument total.

## 10. Next actions

1. Obtain authorized original Amiri Press files for Laws 114/1946, 142/1964, 68/1947 and 70/1964; compare page by page with the 26-page secondary-hosted scan set.
2. Request original Gazette bundles for Law 168/2025 and Decision 480/2026; obtain/retain official SIS full-issue PDF for Decision 200/2026 with provenance/hash where permitted.
3. Resolve Decision 480's extension start date and filing deadline through the original issue and official administrative guidance.
4. Obtain original SCC Gazette judgment scans for Cases 42/17 and 101/26, and rent Cases 81/19 and 108/19; preserve Case 101/26 official SCC HTML as a distinct source.
5. Complete amendment/version graphs for Laws 143/1981, 114/1946 and 142/1964, including article-level pre/post text, commencement, repeal and judgment effects.
6. Complete visual validation of Civil Code and Evidence Law text; recover Evidence Law Gazette PDF index 4 and obtain amendment Gazette scans.
7. Complete Law 119/2008 visual OCR review and Decision 144/2009 original Gazette scan, forms, schedules and full amendment graph.
8. Reconcile missing acquisition IDs EG-0076–EG-0079 against repository history; do not create replacement IDs without evidence.
9. Keep `lawyer_reviewed=false`, `rights_cleared=false` and source-specific permission states unchanged absent documentary evidence.


## 11. Follow-up direct SCC-page reconciliation

A targeted follow-up located the direct official SCC HTML pages for two rent-law cases that an earlier scan-priority note had listed as missing:

- **Case 81/19**, judgment 6 February 1999: official SCC page https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/637_19_81_1_2.html . The Court invalidated only the final phrase of Article 18(b) of Law 136/1981 requiring urgent eviction execution to occur in the tenant's presence. The official page provides the full judgment text. Original Gazette scan remains a separate acquisition task.
- **Case 108/19**, judgment 19 December 2004: official SCC page https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1617_19_108_1_2.html . The Court rejected the challenge as inadmissible, relying on Case 203/20 (14 April 2002), which had rejected the challenge to Law 6/1997. This is not a merits invalidation. Original Gazette scan remains a separate acquisition task.

These are source-tier upgrades to already indexed judicial authorities, not new legal-instrument rows. The master index and checkpoint 90 already record the official SCC pages; checkpoint 147 now confirms the URLs and operative distinctions.

### Case 42/17 Gazette metadata discrepancy

The full text remains available only through secondary legal repositories; no direct official SCC Case 42/17 page or original Gazette scan was found in this follow-up. The reported Gazette publication is 18 June 1998, but issue numbering conflicts: checkpoint 90 and some references state issue 35 supplement, while a secondary scanned consolidation points to issue 25 supplement. Keep the issue number unresolved pending the actual Gazette page. The operative holding remains: invalidation of Law 142/1964 Article 37(2)'s bar on acquisitive prescription contrary to the register, with Article 38 falling consequentially; Article 37(1)'s evidentiary rule was not invalidated.


## 12. Additional amendment-chain source leads confirmed

### Law 143/1981

Law 11/2024 is an amending statute to Law 143/1981. It replaces Article 11(2) and Article 12(2), and the secondary legislation record gives commencement as 25 February 2024. The official Ministry of Agriculture PDF for the base Law 143/1981 is available. Record Law 11/2024 as a distinct amending instrument only if it is not already present in the instrument catalogue; do not count it twice. The Law 143 amendment graph also needs all earlier amendment instruments and the Case 101/26 constitutional invalidation.

### Law 114/1946

Key chain components already identified:
- Law 223/1996: amendment to Article 21 (as annotated in the government-hosted Ministry of Justice text).
- Law 186/2020: inserted Article 35 bis; official government-hosted Gazette reproduction is available.
- Law 5/2021: deferred the operation of Law 186/2020 to 30 June 2023 (the statutory deferral itself must be versioned separately from the substantive amendment).
- Law 9/2022: materially amended multiple procedural/application provisions; commencement calculated as 6 May 2022.
- Justice Minister Decision 2332/2022: amends the Executive Regulation, effective with Law 9/2022.

This is a confirmed key chain, not yet a claim that every historical amendment/correction/repeal has been found. Preserve the pre-2022 and post-2022 versions of affected provisions rather than overwriting them.

### Law 142/1964

Additional amendment and implementation relationships:
- Law 83/2006 amended Law 142/1964 and Law 70/1964; its Gazette metadata is issue 22 bis, 6 June 2006. It must be mapped as a statutory amendment, including its fee provisions and the post-amendment Article 30 wording.
- Executive Regulation Decision 825/1975 is amended by Justice Minister Decision 11264/2016 (published in Egyptian Proceedings issue 30, 6 February 2017; instrument number 11264/2016).
- Territorial commencement postponement decisions are a separate implementing-decision series, not amendments to the substantive statute. Recent Gazette examples include Decisions 7173/2024, 7175/2024, 6512/2024, 739/2025, 5207/2026 and 5208/2026, each with its own cadastral sections and date schedule. The official SIS PDFs for Decisions 7175/2024 and 739/2025 are available; retain all territorial sections and dates in a temporal schedule rather than a single nationwide commencement flag.
- Constitutional Cases 42/17 and 10/35 affect Articles 37(2), 38, 21, 23 and 24 and Decision 553/1976, as separately mapped above.

## 13. Checkpoint 147 incremental category counts

| Category | New records/texts added in checkpoint 147 |
|---|---:|
| Base laws | 0 |
| Amending laws | 0 |
| Executive regulations | 0 |
| Judicial decisions | 0 |
| Full legal texts newly acquired | 0 |
| Unique article provisions newly transcribed | 0 |
| Existing-source audits / provenance reconciliations | 1 batch |

This is intentionally a zero-addition checkpoint: the work updated status and source distinctions without creating duplicate legal-instrument or article-text records. Cumulative instrument-type totals require a normalized instrument-type field and repository-wide deduplication; the 189-row catalogue count must not be presented as a count of base laws or full texts.
