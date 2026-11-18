# Collection checkpoint 203 — Research Agent 1 continuation: Gazette access, deadline and judgment provenance

**Date:** 18 November 2026  
**Repository:** `abdelmalek384/legal_copilot_latest`  
**Scope:** continuation of the ten Research Agent 1 priorities; source acquisition, provenance reconciliation and targeted full-text upgrades.

**Superseding note (checkpoint 204):** The Building Law 119/2008 cumulative extraction count stated in Section 6 below was incorrect. All 114 substantive base articles are already transcribed across checkpoints 93 and 108–111. Decision 144/2009 has 13/185 substantive regulation article bodies captured (172 remain). See checkpoint 204 for the reconciled evidence and corrected registers.

## 1. Repository and register audit

Inspected the master index, checkpoints 85–92 (including their supplemental sections and cross-references), and the later reconciliation records relevant to these workstreams: checkpoints 147, 159–160, 170, 185, 188–202, including 190, 191 and 197. The acquisition register and source-permission JSON were read from their current default-branch paths.

Current register state:
- Acquisition CSV: **250 rows including header = 250 canonical instrument records**, with 250 distinct instrument IDs. The current repository file is `data/research/egypt_initial_statute_acquisition_register_2026-11-17.csv`. This differs from a 172-record count mentioned in the task; the live repository version is 250 rows, so no 172-row historical snapshot was substituted.
- Source-permission JSON: **86 unique source IDs**. These are assessments, not grants of permission.
- Existing type ledger: 66 base-law records, 48 amending-law records, 13 executive regulations, 35 executive-regulation amendment records, 21 judicial decisions, 54 other decision/circular/advisory records, 13 other/unclassified records.
- Priority full-text inventory: 27 unique instruments.
- Core unique article provisions: 1,370 (Civil Code 1,093; Evidence Law 163; Building Law 114).
- Additional property-law searchable headings: 200; historical article-version events: 44.

No new instrument or unique article provision is counted in this checkpoint. The Case 11/23 provenance update below is an additional source reference to an existing acquisition record, not a new judgment record.

## 2. Four older Gazette originals — retrieval status

The existing four scan-copy records were rechecked:
- Law 114/1946: Manshurat six-page scan copy, Gazette issue 85, 24 August 1946.
- Law 142/1964: Manshurat seven-page scan copy, Official Gazette issue 69, 24 March 1964.
- Law 68/1947: Manshurat two-page scan copy, Egyptian Proceedings issue 58, 3 July 1947.
- Law 70/1964: Manshurat eleven-page scan copy, Official Gazette issue 67, 22 March 1964.

These total 26 visually inspected pages, but are **secondary-hosted page-image reproductions**, not original Amiri Press digital binaries. No original Amiri Press PDF bytes or SHA-256 hashes are archived. The Ministry of Justice PDF for Law 114 is an official-hosted text reproduction, not the original 1946 Gazette scan. The original Gazette PDF acquisition objective remains open for all four statutes.

Direct fallback scan URLs already recorded in the acquisition register:
- Law 114/1946: https://manshurat.org/file/83333/download?token=Kv0YfwAI
- Law 142/1964: https://manshurat.org/file/44021/download?token=5Zwo9ziS
- Law 68/1947: https://manshurat.org/file/82270/download?token=fuDVQjIu
- Law 70/1964: https://manshurat.org/file/43842/download?token=z-q7csZN

## 3. Law 168/2025, Decision 200/2026 and Decision 480/2026

### Law 168/2025
Official DSpace item metadata identifies:
- Official Gazette issue 32 bis (و), 13 August 2025;
- publisher: مطابع الأميرية;
- file: العدد 32 مكرر و - مؤمن.pdf, 294.4 KB.

The DSpace download control leads to a request-a-copy page. The SIS repository metadata also identifies the issue and a 295.3 KB PDF, but the SIS item and direct PDF routes returned 502/inaccessible during this session. No original PDF bytes or hash were acquired. The 20-page VetoGate scan remains a secondary reproduction, and its own notice says the electronic copy is not valid for circulation.

### PM Decision 200/2026
The SIS-hosted Official Gazette issue 3 bis (أ), dated 18 January 2026, remains the official full-issue PDF source already identified in the register. It is not archived locally or hashed. Its Article 20 text-layer wording (annual reporting) conflicts with Form 3 and other transcriptions (quarterly reporting); page-image verification is still required.

### Presidential Decision 480/2026
Official DSpace metadata was opened directly:
https://dspace.id.com.eg/items/03b3721d-4847-4be0-8130-5d4bf38da540/full

It identifies Official Gazette issue 45 bis (ج), publication date 10 November 2026, publisher المطابع الأميرية, and an original bundle of 178.37 KB. The download control leads to a request-a-copy page. The original bundle is therefore not locally acquired.

### Deadline analysis — unresolved legal commencement
- Decision 200/2026 issuing Article 4 states that it takes effect on the day following publication: 19 January 2026.
- Law 168/2025 Article 3(1) starts the six-month application period from commencement of the Executive Regulation.
- Cairo Governorate's official notice dated 21 June 2026 states that 18 July 2026 is the final application date. Several Cairo district notices repeat that date.
- Decision 480/2026 Article 1 extends the Article 3(1) period for another equivalent period. Article 2 says it is to be published in the Official Gazette; the operative text does not print a calendar end date or an express extension commencement date.
- If the second period immediately succeeds the first period ending 18 July 2026, the calculated final day is 18 January 2027. If it is measured from publication/commencement of Decision 480 on 10/11 November 2026, the candidate endpoint is 10/11 May 2027. The latter calculation is not an authoritative reading either.
- The decision's publication after the stated first-period deadline makes the legal commencement question material. The repository must retain 18 January 2027 as a conditional append-period calculation, not a verified statutory deadline, until an official implementing circular, agency confirmation or authoritative legal interpretation resolves the issue.

Sources:
- Official DSpace Decision 480 metadata: https://dspace.id.com.eg/items/03b3721d-4847-4be0-8130-5d4bf38da540/full
- Cairo Governorate official deadline notice: https://www.cairo.gov.eg/ar/more/more/taqnen/
- CPC Article 15 text (secondary searchable reproduction): https://lawhub.info/eg/?p=15122

## 4. Constitutional Court judgments

### Case 101/26 — original official court text obtained
The official SCC page is available:
https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3204_26_101_1_2.html

It reproduces the full judgment dated 1 February 2009 and records publication in Official Gazette issue 7 bis (أ), 15 February 2009. It invalidated Article 22(1) of Law 143/1981 insofar as it vested exclusive jurisdiction in ordinary courts over disputes under that law; related paragraphs 2 and 3 fell to the extent inseparably linked. The original printed Gazette page image remains outstanding.

### Case 10/35 — official later SCC corroboration; original direct judgment still missing
The official SCC later judgment in Case 14/41/2022 reproduces the holding of Case 10/35/2018: Articles 21 and 24 of Law 142/1964 were unconstitutional; Article 23 and Justice Minister Decision 553/1976 fell consequentially. The original Case 10/35 signed judgment and original Gazette page remain unacquired. Existing secondary Gazette reproduction is issue 22 bis (ط), 6 June 2018, pages 16–25.

Official corroborating SCC page:
https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/12158_41_14_3_2.html

### Case 42/17 — original judgment remains outstanding
The secondary full text remains at MKSEgypt. An official later SCC judgment and Court of Cassation digest corroborate the partial invalidity of Article 37(2) and consequential fall of Article 38. The Article 37 evidentiary-force limb remains. Publication metadata remains unresolved between two same-day catalogue/digest references: issue 35 تابع and issue 25 تابع (ب), both dated 18 June 1998. The original signed judgment and Gazette page are not acquired.

### Rent-law judgments
A full searchable Gazette-issue reproduction was newly identified for SCC Case 11/23/2018:
https://www.laweg.net/framePlain.aspx?JID=98789&NID=56502&Type=16&action=LawEg

It reproduces the judgment in Official Gazette issue 19 bis (ب), 13 May 2018. The judgment invalidated the opening of Article 18(1) of Law 136/1981 insofar as it extended statutory continuation to non-residential premises leased to legal persons, with effect deferred until the day after the end of the ordinary parliamentary session following publication. This is a secondary-hosted Gazette reproduction, not a direct signed SCC binary. The acquisition record EG-0261 was updated with this source; no new judgment row was created.

Existing rent judgment text leads remain:
- Case 4/23: University of Minnesota Human Rights Library full Arabic judgment transcription; original SCC binary/Gazette original still not separately acquired.
- Case 14/23: Riwaq Al-Jamal full Arabic judgment transcription; original SCC binary/Gazette original still not separately acquired.
- Case 47/21: Riwaq Al-Jamal full Arabic judgment transcription; original SCC binary/Gazette original still not separately acquired.
- Case 116/27: Egylaw full Arabic judgment transcription; original SCC binary/Gazette original still not separately acquired.

The source-permission record EG-LAWEG-LEGAL-ARCHIVE was updated to include the Case 11/23 Gazette reproduction. Collection and commercial reuse permissions remain unknown.

## 5. Amendment-chain status

- Law 143/1981: consolidated Arabic text is recorded for all 29 substantive articles. Six statutory amendment laws and seven executive-regulation decisions are mapped. Law 11/2024 is represented; the 2024 amendment has a secondary-hosted Gazette scan lead. Article 21 repeal and Article 22(1) constitutional invalidity are separately flagged. Law 55/1988 standalone text remains missing; full historical redlines and original amendment Gazette scans remain incomplete.
- Law 114/1946: 12 statutory/transitional events are identified. The Ministry of Justice base text and 2022-updated secondary consolidation are available; 43/70 article IDs have text. Original Gazette and amendment binaries, full article-by-article versions and reconciliation of Law 9/2022 remain outstanding.
- Law 142/1964: Law 83/2006 is identified as the express statutory replacement of Article 30, plus a 1964 corrigendum for Articles 62/65. Thirty substantive article IDs have text in the master-index snapshot, with some excerpts; constitutional invalidity effects from Cases 10/35 and 42/17 must be reflected in temporal article versions. Full amendment redlines and original amendment Gazette scans remain outstanding.

No amendment count is increased in this checkpoint.

## 6. Civil Code, Evidence Law and Buildings Law

- Civil Code Law 131/1948: 1,093 unique non-repealed article provisions are already captured in the core set. This is the repository's deduplicated provision count, not a representation that all 1,149 numbered article slots are independently current. Remaining work is article-level amendment/currentness mapping, historical version separation, and image/source validation. Do not append duplicate bodies from checkpoints 86 or earlier.
- Evidence Law 25/1968: Articles 1–117 are already fully transcribed in checkpoints 112–113. The full statute has 163 provision units including Article 148 bis. No new article bodies are added here. Official Ministry of Finance Gazette reproduction is 11/12 pages visually inspected; printed page 315 remains a rendering blocker. Amendment Gazette scans and historical versions remain outstanding.
- Building Law 119/2008: official MHUC-hosted 114-article source is available. Nine substantive article bodies were captured before checkpoint 202; checkpoint 202 added eight bodies (Articles 2, 4–10) from a 1 December 2020 secondary consolidation. The core count remains 114 unique Building Law provisions only where the underlying text is actually captured; the remaining 105 article bodies need extraction and version comparison. Decision 144/2009 has a full 185-article searchable secondary text, with eight regulation bodies captured; 177 remain. Do not count article headings as full text.

## 7. Count control and rights

No new instrument or unique article provision is counted in this checkpoint. The only register change is a provenance/source-page update to existing EG-0261 and the existing Laweg source assessment.

Keep separate:
- base laws;
- amending laws;
- executive regulations;
- executive-regulation amendments;
- judicial decisions;
- other decisions/circulars;
- complete full texts;
- unique article provisions;
- historical article-version events.

No lawyer verification is claimed. No commercial reuse permission is claimed. Public access, a Gazette masthead on a secondary reproduction, or an official catalogue record does not by itself establish bulk collection, redistribution or commercial reuse permission.
