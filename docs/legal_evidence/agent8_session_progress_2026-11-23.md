# Research Agent 8 — Session progress report
**Date:** 23 November 2026  
**Repository:** https://github.com/abdelmalek384/legal_copilot_latest

## 1. Work completed this session
Four separate acquisition tranches and four separate CSV instrument registers were committed:

1. River transport:
   - [Research note](agent8_river_transport_law167_2022_acquisition_2026-11-23.md)
   - [Instrument register](agent8_river_transport_instruments_2026-11-23.csv)
2. National Railways Authority:
   - [Research note](agent8_railways_law152_1980_acquisition_2026-11-23.md)
   - [Instrument register](agent8_railways_instruments_2026-11-23.csv)
3. National Authority for Tunnels / metro:
   - [Research note](agent8_metro_law113_1983_acquisition_2026-11-23.md)
   - [Instrument register](agent8_metro_instruments_2026-11-23.csv)
4. Maritime ports, Suez Canal and internal navigation:
   - [Research note](agent8_maritime_ports_inland_navigation_2026-11-23.md)
   - [Instrument register](agent8_maritime_ports_inland_navigation_instruments_2026-11-23.csv)

The canonical national acquisition CSV was fetched from the default branch before deduplication. It contains 452 lines including header (458 data records) after the 23 November environment, waste, water-pollution and health updates; the earlier 422-record figure was the pre-update snapshot. The master index dashboard is dated 18 November 2026 and reports 388 confirmed + 1 provisional instruments; that dashboard/register count discrepancy remains unresolved. This session used exact instrument-number/title checks against the live CSV, updated existing instrument rows in place, and added new candidate rows for instruments not already registered. The master index dashboard was not altered.

## 2. Instrument and article counts

| Subdomain | Candidate unique instruments in Agent 8 tranche | Complete provisions read from secondary text | Official Gazette article bodies verified |
|---|---:|---:|---:|
| River transport | 7 | 28 | 0 |
| National Railways Authority | 8 | 34 | 0 |
| National Authority for Tunnels / metro | 4 | 21 | 0 |
| Maritime ports / Suez Canal / inland navigation | 12 | 135 | 0 |
| **Total** | **31** | **218** | **0** |

Counting method:
- River transport: Law 167/2022 has 7 issuing articles + 21 attached-law articles (28).
- Railways: Law 152/1980 has 28 articles; Law 149/2006 has 2 issuing articles; PM Decision 3452/2023 has 4 issuing articles (34).
- Metro/tunnels: Law 113/1983 has 21 articles.
- Maritime/ports/inland navigation: Law 30/1975 has 17 articles; Law 4/1998 has 3; Law 34/2014 has 2 (all on official SCA authority pages); Law 6/1967 has 5; Law 1/1996 has 8; Law 22/1998 has 2; Law 10/2017 has 3; Law 10/1956 has 22; Minister Decision 282/1998 has 73 (the latter six items are secondary transcriptions).
- Of the 218 complete provisions, 22 were read on official SCA authority pages and 196 in secondary text sources. These are complete provisions read, not necessarily locally transcribed verbatim. They were **not** locally transcribed verbatim into the repository and were **not** visually verified against official Gazette page images. Article maps, version notes, source URLs and remaining acquisition work are preserved in the tranche notes.
- Additional amendments/decisions were identified at metadata or selected-clause level but their complete article bodies are not counted.
- One corrigendum to Law 167/2022 (reported Gazette issue 48 bis (ب), 6 Dec 2022) is separately tracked as a correction/version event and is not counted as a distinct amending law.

## 3. Source and rights status
- Official/authority locators located: Amiri Press Law 167/2022 text; Court of Cassation Gazette download locator; GAFI/Transport Authority licensing guide; Amiri Press Decision 342/2023 text; DSpace/MELES Gazette metadata and PDF locators; Ministry of Finance and SIS pages for Law 83/2025; other ministry/court catalogue entries.
- Secondary texts used: legal practitioner transcriptions, legal databases and news reports. Each tranche separates these from official source locators.
- Four source-permission entries were added for the river/rail tranche; one Lawyer Egypt source entry was added for the metro tranche; three official authority-source entries (SCA, MTS, APA) were added for the maritime tranche. The source-permission register now contains **189 source records** after six new source-family assessments for EEAA, IDA, MWRI, SIS Gazette PDFs, EDA and FAOLEX.
- All relevant permission fields remain unknown. No commercial reuse rights were cleared.
- Lawyer review: **0**.
- Authenticated official Gazette PDF binaries/hash records acquired by this Agent 8 pass: **0**.
- Official Gazette pages visually verified by this Agent 8 pass: **0**.
- No legal-currentness certification is made.

## 4. Deduplication decisions
- The national acquisition CSV had no exact matching row for the 31 tranche instruments at the time of the check.
- Existing collection checkpoints 30 and 38 already cross-reference Tourism Law 8/2022, Executive Regulation 705/2023 and River Transport Law 167/2022. Those are useful prior leads, but the canonical CSV had no Law 167/2022 instrument row; no duplicate tourism work was undertaken.
- The Agent 8 registers use IDs RA8-053 through RA8-083, continuing the prior Agent 8 sequence RA8-001 through RA8-052.
- The national master index and canonical acquisition CSV were not modified. The Agent 8 notes/registers are separate artifacts pending owner review and later canonical reconciliation.

## 5. Assigned-domain progress
This session materially expanded **Transport** discovery, particularly:
- River transport: Law 167/2022, licensing fees/criteria and associated 2024–2025 decisions.
- National Railways: Law 152/1980 and its 2006/2018/2020 amendment chain; ENR contracting regulation and freight concession.
- Metro/tunnels: Law 113/1983 and amendments through Law 83/2025.
- Maritime ports/Suez Canal: Alexandria Port Authority Law 6/1967; Suez Canal Law 30/1975 and amendments; Dry and Specialised Ports Law 1/1996 and amendments; internal navigation Law 10/1956 and its 1998 licensing regulation.

The overall Agent 8 assigned-domain estimate is **not recalculated**. The prior ~27% estimate combined multiple sectors and was low-confidence; this pass adds source discovery and secondary-text reading but no official Gazette verification. It would be misleading to convert 19 candidate instruments into a precise completion percentage.

## 6. Contribution to total Egyptian legal knowledge
**No whole-corpus completion percentage-point increase is claimed.** The repository dashboard's 388 confirmed instruments is a registered-record count, not a defensible denominator for all Egyptian legislation. Thirty-one candidates have been added to separate Agent 8 tranche registers, but the national register/master index remains unmodified and official text verification is zero.

## 7. Next priorities
1. Acquire original Gazette page images/PDFs for Laws 167/2022, 152/1980, 113/1983, 30/1975, 1/1996, 10/1956 and all identified amending laws.
2. Verify the Law 167/2022 Article 14 corrigendum and all 2024–2025 river-licensing decisions and annexes.
3. Obtain the full ENR contracting regulation Decision 191/2021, Decision 577/2022 and Decision 342/2023 replacement provisions, plus the freight concession instrument/contract.
4. Obtain the full Law 83/2025 text and inserted tunnel-authority Articles 4 bis and 4 bis 1; locate metro safety/operational rules.
5. Continue remaining transport families: vehicle licensing and road transport; do not duplicate Laws 8/1990, 28/1981 or previously indexed tourism legislation.
6. Continue Health, telecom, electricity, education, antiquities and sports only after checking their canonical register entries.
7. Complete permission checks and seek written authorization where required; conduct Egyptian lawyer review before any currentness, authenticity or commercial-rights claim.


## 8. Follow-on acquisition — Environment Law 4/1994 and Executive Regulation (23 November 2026)

The approach changed from repeated checkpointing to text acquisition. A connected environment-law tranche was added:
- New Arabic text dossier: [environment law and executive regulation acquisition](environment_law4_1994_executive_regulations_text_acquisition_2026-11-23.md).
- Canonical acquisition CSV updated in place: existing environment records EG-0016, EG-0087, EG-0088 and EG-0090–EG-0097 now carry actual text/source observations and precise remaining work. Two new candidate rows added: EG-0423 (PM Decision338/1995 base executive regulation) and EG-0424 (PM Decision720/2012 Article25 replacement).
- No duplicate rows were created for instruments already registered.

### Text actually acquired / observed
- Law 9/2009: full five-article secondary Arabic operative transcription captured in the dossier.
- Law 105/2015: full three-article operative structure and inserted provisions captured from a secondary Arabic text.
- PM Decision 338/1995: full 2,728-line searchable Arabic Gazette text layer located at an IDA government-hosted PDF; not yet mirrored verbatim in the repo.
- PM Decision 1741/2005: substantial Article1 replacement text acquired, including EIA, environmental registers and hazardous-waste rules; remaining articles and annexes still open.
- PM Decision 964/2015: full decision and annex PDF text layer (1,241 lines) located; operative scope and principal clauses captured, but not every annex row locally transcribed.
- PM Decision 720/2012: EEAA-hosted Proceedings PDF exposes the preamble and Article25 replacement text; complete issue/page verification remains open.
- PM Decision 2466/2024: full operative Articles1–5 and attached marine-effluent, continuous-monitoring and noise tables read from a 25-page Official Gazette PDF text layer; substantive Arabic text captured in the dossier.
- PM Decisions 1095/2011, 710/2012, 544/2016, 618/2017 and 1963/2017: additional Arabic PDF/text locators and amendment maps acquired; several still metadata-only or partial text.

### Scoped progress percentage
For a transparent, bounded denominator, define the **core Environment Law 4/1994 amendment/executive-regulation chain** as 12 instruments: Law4/1994, Law9/2009, Law105/2015, PM338/1995, and the eight PM regulation amendments listed by EEAA (1741/2005,1095/2011,710/2012,964/2015,544/2016,618/2017,1963/2017,2466/2024).
- **6/12 = 50%** have a complete searchable Arabic text source located (Law4 consolidated through 2015; Law9; Law105; PM338; PM964; PM2466). This measures source-text acquisition, not legal consolidation or Gazette authentication.
- **3/12 = 25%** have substantial operative Arabic text blocks mirrored in this new dossier (Law9, Law105, PM2466); PM1741 and PM720 are partial extracts, while other decisions have text/PDF locators or metadata only.
- The separate PM Decision720/2012 is an additional candidate, not substituted for EEAA-listed Decision710/2012. The two same-date records are retained separately pending primary-source comparison.
- No percentage for the whole Egyptian legal corpus is claimed: the repository's registered-instrument count is not a denominator for all Egyptian legislation. No legal-currentness, Gazette-authenticity, or commercial-reuse certification is made.

### Quality and rights
No original publisher-hosted Gazette binary/hash was acquired in this tranche; some government-hosted text layers and secondary Gazette reproductions were read. All secondary-source rights remain unknown, no commercial reuse permission was cleared, and no lawyer review was completed.

### Next acquisition targets
1. Mirror complete Arabic Law4/1994 and PM338/1995 text plus annexes.
2. Obtain and compare Gazette images for Laws9/2009 and105/2015.
3. Extract complete Decisions1741/2005,1095/2011,710/2012,720/2012,544/2016,618/2017 and1963/2017 with annexes; resolve the 710/720 numbering split.
4. Acquire the original Amiri Press binary for Decision2466/2024 and check subsequent EEAA Decision342/2025.
5. Continue with the Waste Management Law202/2020 and PM722/2022, and Law48/1982/Nile pollution regulation, after exact duplicate checks.


## 9. Follow-on acquisition — Waste Management Law202/2020 and executive regulation

A second connected legal-text tranche was acquired, avoiding duplicate rows:
- New dossier: [Waste Management Law202/2020, PM722/2022 and PM1113/2024 Arabic text](waste_management_law202_2020_pm722_2022_amendments_text_2026-11-23.md).
- Updated existing canonical records EG-0089 (PM722/2022), EG-0139 (Law202/2020), and EG-0136 (Minister Decision342/2025) in place.
- Added EG-0425 for PM Decision1113/2024; no duplicate Law202/2020 or PM722/2022 records added.

### Actual Arabic text / source acquisition
- Law202/2020: full Official Gazette issue41 bis (ب), 13 Oct 2020, 796-line searchable Arabic PDF reproduction located via FAOLEX; issuing Arts1–6 and selected substantive articles and penalties captured in dossier.
- PM722/2022: complete 2,961-line Arabic Official Gazette PDF hosted by EEAA, issue7 bis (ج), 22 Feb 2022; full 56-article regulation and 18 annexes source-located. Actual Arabic text captured for issuing articles, selected Arts1,18,24,25,35–37,51–55, Annex6, Annexes7,11,17,18, and healthcare-waste disposal standards.
- PM1113/2024: complete operative text source-located in Gazette issue14 supplement PDF, 4 Apr 2024; replacements to regulation Arts1(18) and29, amendment to Art25, and repeal clause captured. The text layer has a numbering anomaly («المادة الثامنة» then «المادة الثالثة» and «المادة الرابعة»), preserved for page-image review.
- Minister Decision342/2025: official EEAA service page supplies the operational registration/accreditation rules and requirements; secondary publication report gives issue272 supplement, 3 Dec 2025 and effective-date claim. Complete Gazette attachment still needed.

### Scoped progress percentages
- **Environment Law4/1994 amendment/executive-regulation chain:** 6/12 = **50%** have a complete searchable Arabic source located. This is source discovery, not verified current consolidation.
- **Waste Management Law202/2020 instrument chain (3 core instruments: Law202/2020, PM722/2022, PM1113/2024):** 3/3 = **100%** have complete searchable Arabic text sources located. The 80-article statute, 56-article regulation/18 annexes and 2024 amendment are not yet fully mirrored verbatim article-by-article into the repository.
- **Repository-wide percentage:** still not defensibly calculable because the project has no verified denominator representing all Egyptian legislation or a stable in-scope corpus. Do not use the count of current register rows as the denominator.
- **Canonical acquisition register:** now 424 data records (425 lines including header). The master dashboard count remains a separate inconsistent metric and was not overwritten.

### Quality / next steps
The official EEAA PM722 PDF and FAOLEX Gazette reproduction provide complete searchable sources, so the next blocker is transcription and page-image QA rather than discovery. Next work: mirror all 80 Law202 articles, 56 PM722 regulation articles and 18 annexes; inspect PM1113 page images; acquire complete PM342/2025 Gazette attachment; retrieve PM662/2025 extended producer responsibility instrument; then continue to Law48/1982 and its Nile-pollution implementing regulation. No commercial reuse permissions or lawyer review are claimed.


## 10. Follow-on acquisition — Nile/watercourse pollution and sewerage discharge laws

New dossier: [Nile water pollution Law48/1982, Law93/1962 and implementing/amending decisions](nile_water_pollution_law48_1982_and_sewerage_law93_1962_text_2026-11-23.md).

Canonical register updated with 14 candidate records EG-0426–EG-0439. New records cover Law48/1982, Law103/2015, PM Decision402/2009, Ministerial Decisions219/2010, 92/2013, 208/2018 and 289/2018, Law93/1962, Minister Decision44/2000, Decision308/2020, and identified historical/related amendment leads 8/1983, 43/1985, 383/2011 and 789/2013.

### Arabic text / source acquisition
- Law48/1982: all 19 articles located in a Ministry of Water Resources and Irrigation-hosted Arabic PDF; all 19 articles normalized in the dossier, with exact source locator.
- Law103/2015: full two-article amendment text acquired from Official Gazette issue40 bis (ب), 7 Oct 2015; it replaces Law48 Article16 penalty with EGP50,000–200,000 fine plus up to one year imprisonment (or either), doubling for repeat violations.
- PM Decision92/2013: full 64-article regulation source located in a 646-line MWRI-hosted searchable PDF and a 32-page Gazette reproduction; selected articles on discharge licensing, river vessels, sampling, freshwater/non-freshwater standards, fees and enforcement captured.
- PM Decisions219/2010, 208/2018 and 289/2018: full operative Arabic texts captured. These respectively amend Art82 fee, TDS/effluent standards in Arts51/52, and groundwater monitoring/brine discharge fees with new Art15 bis.
- Law93/1962: complete 22-article Arabic text located in FAOLEX PDF; key Articles7–18 extracted.
- PM Decision44/2000: complete 17-page PDF located; FAOLEX identifies 24 articles and subject scope, but OCR is too poor for reliable text extraction.
- Minister Decision308/2020: PDF and text locators located; complete operative text still to be extracted.
- PM Decisions8/1983,43/1985,383/2011 and789/2013 were identified in recitals, but their full Gazette texts remain gaps.

### Scoped progress
- Nile/watercourse and sewerage package: **10/11 = 91%** have a full Arabic text source or complete PDF copy located; Decision383/2011 remains recital-only. This measures source discovery, not complete local transcription or currentness.
- Environment Law4/1994 chain remains **6/12 = 50%** complete searchable source texts located.
- Waste Management Law202/2020 chain remains **3/3 = 100%** complete searchable source texts located.
- Canonical acquisition register now has **438 data records** (439 lines including header).
- No repository-wide percentage is claimed: there is no defensible denominator for all Egyptian legislation. Register row count is not a corpus denominator.

### Next acquisition priorities
1. Transcribe the 64-article PM92/2013 regulation and numeric tables with page-image QA.
2. Obtain PM383/2011 and PM789/2013 texts, and original PM8/1983 and PM43/1985 Gazette pages; resolve Decision8/1982 vs8/1983 recital anomaly.
3. Transcribe PM44/2000 and PM308/2020 full text and technical tables.
4. Integrate Law213/1994 changes to Law48/1982 and Law147/2021 Water Resources and Irrigation Law effects.
5. Continue the pending full-text mirror of Law202/2020 and PM722/2022 (80 articles, 56 articles and 18 annexes), then expand into transport/health sectors.

No original Amiri Press file hash, lawyer review, or commercial reuse clearance is claimed.


## 11. Follow-on acquisition — Health facilities, blood/plasma and Egyptian Health Council

New dossier: [Health-sector medical facilities, blood/plasma and Egyptian Health Council legislation](health_facilities_blood_plasma_egyptian_health_council_2026-11-23.md).

Canonical register updated with 13 new candidate rows EG-0440–EG-0452 and existing rows EG-0271 (Law87/2024), EG-0272 (PM2856/2024) and EG-0354 (PM1966/2026) updated in place. No duplicates were added for the 2024 public-utility concession law or its executive regulation.

### Actual Arabic text / source acquisition
- Law51/1981: consolidated 21-article Arabic source through Law141/2006 located; licensing, management, inspection, closure, offences and transitional licensing provisions captured.
- Law153/2004: full amendment text located; replaces 13 provisions of Law51 and inserts Art16 bis; corrigendum issue31 (29 Jul 2004) identified.
- Law141/2006: single-article amendment to Art18 located by PDF metadata and secondary consolidated text.
- Health Minister Decision216/1982: full 25-article Arabic executive regulation source located; premises, clinical rooms, operating theatres, staffing, licensing and inspection requirements captured.
- Health Minister Decision545/1982: full six-article amendment text captured; changes plans, hospital licence information, manager contract and inspection committee.
- Law12/2022: full 20-article Official Gazette PDF located; establishes Egyptian Health Council, licensing examinations, five-year renewable licence, Egyptian Board, national health-worker register and training accreditation.
- PM Decision378/2023: full 39-article regulation and fee schedules located in Official Gazette issue39 bis (و), 4 Oct 2023. Gazette contents page prints 3798/2023 while body title prints 378/2023; body preamble says Law12/2023 while fee schedule says Law12/2022. These are preserved as anomalies pending page-image inspection.
- Law8/2021: full Arabic statute source located in EDA-hosted Official Gazette PDF; blood operations, plasma collection/manufacture/export, licensing, fees, donor registry and Blood Operations Monitoring Council.
- PM Decision2603/2021: full 17-page executive regulation PDF located at EDA (English translation) and Arabic secondary PDF/text; selected licensing, testing, plasma and closure provisions captured.
- Decision439/2024: complete Official Proceedings issue258 PDF text read; committee composition, scope, approvals and repeal clause captured. Preamble cites Decision4/2023 while Article3 repeals Decision41/2023; text layer prints «مادة35» where Article3 appears.
- Decision121/2024: official Amiri Press text locator identified; Article1 applies attached blood-centre specifications, but the technical annex remains to be acquired.
- Existing Law87/2024 and PM2856/2024 records updated with official Amiri Press/SIS/MOHP text sources; concession exclusions and executive regulation procedures captured.

### Scoped progress
- Health-facility / blood-plasma / Health Council package: **10/13 = 77%** have a complete searchable text source or complete PDF copy located. Decisions4/2023 and41/2023 are recital-only; Decision121/2024 has Article1 locator but its attached standards remain unacquired.
- Watercourse/sewerage package remains **10/11 = 91%** source/PDF acquisition.
- Environment Law4/1994 chain remains **6/12 = 50%** complete searchable sources located.
- Waste Management Law202/2020 chain remains **3/3 = 100%** complete searchable sources located.
- Canonical acquisition register now has **458 data records** (452 lines including header).
- Whole-corpus percentage remains unavailable: no reliable denominator exists for all in-scope Egyptian legislation; register rows are not a corpus denominator.

### Next acquisition priorities
1. Acquire and transcribe Decision121/2024 attached blood-centre specifications and the full Arabic PM2603/2021 regulation/annexes.
2. Resolve Decision378/2023 vs3798/2023 and Law12/2022 vs12/2023 discrepancies from Gazette page images and Amiri Press catalogue.
3. Obtain Decision4/2023 and Decision41/2023 full texts; reconcile with Decision439/2024 preamble/repeal.
4. Complete Law51/1981 amendment history and PM216/1982 subsequent ministerial amendments, including the 1985 lead.
5. Continue article-level transcription of Law202/2020 and PM722/2022; then return to transport/road traffic and vehicle licensing.

No commercial reuse rights, legal-currentness certification or lawyer review is claimed.


## 12. Source-permission register reconciliation

The source-permission register was updated to **189 source records**. Six source-family records were added for EEAA environment/waste legislation, IDA PM338/1995 PDF, MWRI Law48/1982 and PM92/2013 PDFs, SIS-hosted Gazette PDFs for health instruments, EDA blood/plasma legislation, and FAOLEX water/waste/environment Gazette reproductions. Every new record retains collection_permission = unknown and commercial_reuse_permission = unknown. Existing generic secondary-source records remain in place; no public-access or government-hosting status was treated as a reuse licence.


## 13. Session-wide acquisition summary (23 November 2026)

Across Agent8's four transport dossiers plus the environment, waste, Nile/watercourse and health dossiers:
- **68 candidate unique instruments** identified/registered across the Agent8 tranche registers (31 transport; 2 new environment-regulation candidates; 1 new waste-regulation amendment; 14 water/sewerage instruments and amendment leads; 13 health-sector instruments; 7 tax-procedure instruments added in this follow-on pass).
- **30 new candidate rows** added to the canonical national acquisition CSV in the environment/waste/water/health passes; **17 existing canonical rows** updated in place with actual text observations and improved provenance.
- Canonical national register now has **458 data rows**. Its denominator is not the total in-scope Egyptian legislation; do not convert this count into a whole-corpus completion percentage.
- Four substantive new Arabic text dossiers were committed for environment, waste management, Nile/water pollution/sewerage, and health; the earlier four transport dossiers remain in the repository.
- Source-permission register now has **189 source assessments**, with all new collection and commercial reuse permissions unknown.

This summary counts candidate instruments, not fully authenticated or locally mirrored verbatim texts. Gazette page-image verification, complete amendment redlines, currentness review and lawyer review remain separate workstreams.


## 14. Follow-on acquisition — Unified Tax Procedures Law and Executive Regulation

New dossier: [Unified Tax Procedures Law 206/2020, Executive Regulation 286/2021 and amendments](unified_tax_procedures_law206_2020_executive_regulation_amendments_arabic_acquisition_2026-11-23.md).

Canonical register updated: **7 new instrument rows EG-0453–EG-0459** added for Law211/2020, Decision286/2021, Law7/2025, and Finance Minister Decisions20/2023, 309/2023, 518/2023 and 538/2023. Existing EG-0008 (Law206/2020 and Law150/2026) updated in place; EG-0335 remains the cross-reference for the official 2026 corrigendum. No duplicate base-law or Law150 row was created.

### Actual Arabic text / source acquisition
- Law206/2020: full searchable Arabic Official Gazette PDF from ETA, 649 extracted lines.
- Law211/2020: full operative amendment text from official ETA Gazette PDF; replaces Articles13, 44, 70 and73 (published replacement heading for one provision prints Art72) and adds Arts73 bis and74 bis. Article70/72 mismatch is recorded for page-image verification.
- Decision286/2021: full searchable Arabic executive regulation source from ETA, 6,838 extracted lines; selected provisions on returns, e-invoicing, tax collection and seizure captured.
- Decision20/2023: official MOF two-page PDF; changes wage-tax return/annual settlement rules in regulation Art31. OCR/RTL ordering needs visual page check.
- Decision309/2023: official MOF one-page PDF; adds a visible electronic invoice/receipt compliance certificate paragraph to regulation Art34. Secondary source used to recover readable wording from the official PDF's poor text layer.
- Decision518/2023: official Amiri Press Gazette metadata for Proceedings issue260 (تابع), 21 Nov 2023; original PDF request-a-copy restricted. Full Arabic Article52 bis text acquired from secondary legal sources; status labelled secondary.
- Decision538/2023: official MOF legislation record confirms instrument and date; complete Gazette reproduction and full operative Arabic text located from secondary source. Repeals paragraph2 of Article52 bis inserted by Decision518/2023.
- Law7/2025: official ETA two-page Arabic Gazette PDF; adds Arts45 bis, 75 bis and75 bis 1.
- Law150/2026 remains under existing EG-0008, with the 8 Aug 2026 Gazette corrigendum separately cross-linked to EG-0335.

### Scoped progress
- Unified Tax Procedures package: **9/9 = 100%** have a located text source or complete PDF. This includes two instruments (Decision518/2023 and Decision538/2023) where the operative Arabic text is presently sourced from secondary reproductions and the official source status is metadata/catalogue or restricted Gazette access; it does not mean all nine originals have been visually checked or locally mirrored.
- Canonical national acquisition register now has **458 data rows** (459 lines including header).
- Agent8 candidate unique instrument count rises from 61 to **68** after adding the seven new tax-procedure instruments.
- Whole-corpus percentage remains unavailable: there is no defensible denominator for all in-scope Egyptian legislation. Scoped source acquisition rates must not be represented as whole-corpus completion.

### Next acquisition priorities
1. Obtain the restricted original Amiri Press PDF for Decision518/2023 and original Gazette PDF for Decision538/2023.
2. Inspect Law211/2020 Gazette page image to resolve Art70/Art72 mismatch.
3. Build a provision-level consolidated Law206/2020 incorporating Laws211/2020, 7/2025 and150/2026 and the separate corrigendum event.
4. Build a provision-level current Decision286/2021 text integrating Decisions20/2023, 309/2023, 518/2023 and538/2023, preserving repealed text as history.
5. Search for any later decisions/circulars under the Unified Tax Procedures Law and verify no post-538/2023 amendment to Decision286/2021.

No lawyer review, commercial reuse clearance, local Gazette binary hashing or complete page-image verification is claimed.
