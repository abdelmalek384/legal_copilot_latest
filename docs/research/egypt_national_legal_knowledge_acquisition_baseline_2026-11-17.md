# Egyptian national legal knowledge — acquisition baseline and collection roadmap

**Snapshot:** 17 November 2026  
**Purpose:** establish a nationwide, Arabic-first acquisition programme for Egyptian legal knowledge. This is a source inventory and first tranche of collected legal material, not a claim that Egypt's law is fully covered.

## 1. Collection objective

Build a source-grounded knowledge base across the entire Egyptian legal system:
- Constitution, legislation, amendments, executive regulations, presidential/Cabinet/ministerial/regulatory decisions and circulars.
- Court of Cassation, Supreme Constitutional Court, State Council, administrative and economic court decisions/principles, plus official legal opinions where publicly available.
- Procedural rules, court forms, official fees, filing/notification requirements and legal practice materials.
- Treaties, ratification instruments, reservations and domestic implementation.
- Historical versions, repeal/supersession chains, commencement and transitional rules.

Every record must carry the issuing authority, instrument/case number, year, publication and effective dates, Gazette issue/page, source URL, source hash when lawfully downloaded, text status, amendment/repeal relations, source tier, rights status, currentness date and lawyer-review status.

## 2. Free-source policy and access limits

The project prioritizes freely accessible public materials. It will not bypass subscriptions, authentication, request-copy restrictions, robots/access controls or copyright restrictions.

### Sources discovered

1. **Egyptian Legislation Portal (IDSC):** https://elpai.idsc.gov.eg/GeneralSearch/LegalDatabases?tab=legislation. It offers search entry points for Egyptian legislation, Supreme Constitutional Court, Cassation, Supreme Administrative Court, Administrative Judiciary, economic judgments, State Council opinions and restrictions/descriptions. The portal's About page reports historical records back to 1828, more than 290,000 legislative records and over 100,000 judgments. Its subscription page shows that some database services are paid; only free public content will be collected.
2. **Court of Cassation:** https://cc.gov.eg/judgments_search/. Public pages expose recent principle summaries and subject categories, including labour, commercial, economic, rent and family. The Court's subscription notice says full judgment texts, advanced search, legislative database and official PDF downloads are paid services; it lists an annual fee of EGP1,080 for Egyptian subscribers. Do not scrape or bypass restricted content. Public summaries and genuinely free official PDFs may be used.
3. **Government Printing Office / Official Gazette:** https://alamiria.com/Sec/Home. Primary publication channel for laws and Gazette issues. Some full archive copies/certified copies require request/payment; individual online text availability varies.
4. **DSpace Gazette catalogue:** https://dspace.id.com.eg/. Useful for Gazette issue metadata and publication identifiers; public catalogue metadata does not mean the PDF itself is freely downloadable.
5. **Ministry of Finance:** https://mof.gov.eg/ar/legislation/legislation. Public guidance collection for tax, customs, financial legislation, Civil Code and related texts. It expressly says the Official Gazette is the sole legal reference and ministry texts are for guidance.
6. **Egyptian Tax Authority:** https://www.eta.gov.eg/ar/content/qwanyn-aldrybt-ly-aldkhl. Public downloadable PDFs, including Official Gazette copies for 2026 tax amendments and historic amendment instruments.
7. **Financial Regulatory Authority:** https://fra.gov.eg/en/تشريعات-عامة-للهيئة/. Public regulator portal spanning capital markets, insurance, non-bank finance, fintech, AML, accounting and movable collateral. Some consolidated texts are version-dated (e.g. Capital Market Law95/1992 updated 2022); later decisions still need checking.
8. **Central Bank of Egypt:** https://www.cbe.org.eg/en/laws-regulations/laws/banking-laws. Public listing includes Banking Law194/2020 and executive regulations; listing page says last updated 23 March 2023, so it cannot be treated as a complete current circular register.
9. **Egyptian Environmental Affairs Agency:** https://www.eeaa.gov.eg/laws/55/index. Public law library for Environment Law4/1994, amendments and executive regulations. EEAA states that the Arabic text is the original official version and the English version is only an aid.
10. **Ministry of Social Solidarity:** public legislation list includes social insurance, social security, family and child laws; list is partial/paginated and each item needs verification.
11. **ILO NATLEX / UNEP LEAP:** useful free intergovernmental discovery and metadata sources, but not promulgating authorities.
12. **Manshurat / other publishers:** useful for locating texts and secondary comparison; record-level rights and source provenance must be checked.

Detailed URLs, access tiers and limitations are recorded in `data/research/egypt_national_legal_sources_register_2026-11-17.csv`.

## 3. First statute tranche acquired / located

See `data/research/egypt_initial_statute_acquisition_register_2026-11-17.csv` for 25 instruments and source state. Important distinctions:
- **Official PDF text actually opened:** Civil Code Law131/1948; Income Tax amendments Law151/2026; Unified Tax Procedures amendment Law150/2026; tax dispute renewal Law152/2026; Stamp Tax amendment Law153/2026; Capital Market Law95/1992 consolidated copy; Criminal Procedure Law174/2025 and commencement amendment Law160/2026.
- **Official government listing/metadata only:** Evidence Law25/1968; Civil and Commercial Procedure Law13/1968 and amendment Law157/2024; Companies Law159/1981; VAT Law67/2016 and amendment lead Law149/2026; Customs Law207/2020 and executive regulation/Decision262/2026; Social Insurance Law148/2019; Banking Law194/2020; Unified Insurance Law155/2024; Environment Law4/1994 and Natural Reserves Law102/1983; Child Law12/1996.
- **Secondary-only lead or candidate source:** Personal Status Law25/1929; Penal Code Law58/1937; Investment Law72/2017; IP Law82/2002; Consumer Protection Law181/2018. These are not primary-source verified in this tranche.

The 32-domain matrix is in `data/research/egypt_national_legal_domain_inventory_2026-11-17.csv`.

## 4. New high-value 2026 tax tranche — Official Gazette PDFs opened

The Egyptian Tax Authority's official page lists laws 150–153/2026 and links directly to Gazette PDFs. The four PDFs were opened and their text layers inspected.

### Law 150/2026 — Unified Tax Procedures Law206/2020
- Official PDF: https://eta.gov.eg/sites/default/files/2026-08/law.no_.150.of_.2026.pdf
- Gazette issue 30 bis (A), 28 July 2026; two pages.
- Amends Article38's bookkeeping obligation: taxpayers conducting commercial, industrial, craft or professional activities must maintain regular accounting books/records under Commercial Law17/1999, manually or electronically, subject to the stated statutory qualifications.
- Adds Article27 bis: on taxpayer request, the Tax Authority may issue a temporary tax card for eight months to complete establishment/licensing procedures. It cannot be used to issue electronic receipts or invoices. Tax liabilities accrued during its validity are payable after expiry.
- Effective day after publication under Article3.

### Law 151/2026 — Income Tax Law91/2005
- Official PDF: https://eta.gov.eg/sites/default/files/2026-08/law.no_.151.of_.2026.pdf
- Gazette issue 30 bis (A), 28 July 2026; ten pages.
- Rewrites provisions including Articles28, 43, 46 bis (3) and (4), 50, 52 and 56; adds provisions to Articles23, 31 and 33.
- The text includes changes to bad-debt deductibility, a 2.5% real-estate disposition tax, capital gains treatment for unlisted securities/company interests, dividend treatment, interest deductibility for related financing and exemptions/conditions for qualifying infrastructure financing.
- Introduces a one-time 15% investment incentive against tax payable for qualifying IPOs subject to market-capitalization and offer-size thresholds, with non-cumulation and possible extension conditions.
- Contains transitional simplified tax settlement rules for eligible enterprises and companies with annual turnover not exceeding EGP10m for specified past tax periods.
- Repeals Article18 of Law91/2005 while preserving rules and procedures issued under it for tax periods 2027 and earlier; other listed provisions are also repealed. Exact application must be mapped against the executive regulation and individual transition clauses.
- Effective day after publication under Article7.

### Law 152/2026 — tax dispute settlement renewal
- Official PDF: https://eta.gov.eg/sites/default/files/2026-08/law.no_.152.of_.2026.pdf
- Gazette issue 30 bis (A), 28 July 2026; one page.
- Renews the Law79/2016 tax-dispute settlement procedures and committees through **31 December 2026**. Existing committees continue pending applications and receive new applications through that date.
- Add an expiry/currentness check; do not assume the temporary framework continues beyond 31 December 2026 without a later law.

### Law 153/2026 — Stamp Tax Law111/1980
- Official PDF: https://eta.gov.eg/sites/default/files/2026-08/law.no_.153.of_.2026.pdf
- Gazette issue 30 bis (A), 28 July 2026; two pages.
- Replaces Article83 bis A: stamp tax on aggregate sales of listed securities, borne by seller and buyer. The text sets 0.5 per thousand for each side generally and 0.25 per thousand each for same-day buy/sell transactions; market-makers are exempt. The clearing entity withholds/remits within the statutory timetable and bears joint responsibility as specified.
- Repeals Article5 of Law199/2020.
- Effective day after publication under Article3.

These are source-text extraction findings, not tax advice or lawyer sign-off. Preserve Arabic source wording, exact numerical units, effective dates and cross-references. Full amendment consolidation and subsequent circular checks remain necessary.

## 5. Other substantive primary-source acquisitions

### Civil Code Law131/1948
- Official ETA PDF: https://www.eta.gov.eg/sites/default/files/2024-10/law-131-1948.pdf
- Full PDF text layer is available (2,660 extracted lines). The opening provisions establish application of legislation, supplementary sources where no text applies, repeal/conflict rules, computation of periods and conflict-of-laws rules. The Ministry of Finance catalogue labels the Civil Code in force and lists selected related amendments.
- This is the base text, not a consolidated 2026 version. A complete amendment chain is required before operational use.

### Capital Market Law95/1992
- FRA consolidated PDF: https://fra.gov.eg/wp-content/uploads/2024/06/قانون-سوق-المال-بصيغة-WORD-6.pdf
- 42-page updated text inspected. The document identifies amendments including Laws13/2022,17/2018,27/2014,123/2008,143/2004,13/2004,158/1998,89/1996 and10/1995. The FRA page labels its consolidated version updated in 2022; later rules and decisions still need checking.

### Environmental Law4/1994
- Official EEAA page: https://www.eeaa.gov.eg/laws/55/index
- The official page lists Arabic Law4/1994 as amended by Law9/2009 and Law105/2015; Executive Regulation PM338/1995 with listed amendments including PM2466/2024; and Natural Reserves Law102/1983.
- EEAA explicitly says the Arabic original is the official version and English is only an aid. Full attachment-by-attachment acquisition and consolidation remain pending.

## 6. Critical currentness correction — Criminal Procedure Law

Law174/2025 was enacted with a commencement clause originally pointing to 1 October 2026. That date was amended by Law160/2026.

- Law174/2025 official Ministry of Justice Gazette copy: https://moj.gov.eg/backend/api/documents/download/20F3150C-29F1-487E-A0F0-FCCE10CB207B
- Law160/2026 official Government Printing Office text: https://www.alamiria.com/Sec/TashTxt?id=Aalg37zxdcU%3D
- Official Gazette issue39 bis (B) metadata dated 30 September 2026: https://dspace.id.com.eg/items/1b1e2a48-59d9-4307-b215-1ac3a07b4ee3
- Law160 Article1 substitutes **1 October 2027** for the previous commencement wording in Article6 of Law174. Article2 makes Law160 effective the day after Gazette publication.
- Therefore, as of this snapshot, Law174/2025 is enacted but not yet in force. Do not answer ordinary current criminal procedure questions using the new 546-provision Code before 1 October 2027. Law174 Article4's repeal of Law150/1950 and Law140/2014 must be treated in the commencement transition, not as already operative.
- See `egypt_criminal_procedure_law_174_2025_status_after_law_160_2026.md` for the focused status note.

## 7. Court decisions — free/restricted boundary

The Court of Cassation public page provides recent principle summaries and lists civil categories including labour, commercial, economic, rent and family; criminal categories include felony, misdemeanour and economic misdemeanour appeals. However, the Court's subscription notice explicitly places full judgments, advanced search, the legislative database and official PDF downloads behind subscription. It advertises EGP1,080/year for Egyptian subscribers.

Policy:
- Collect public headnotes and freely downloadable official principles with direct case references.
- Record full-text judgment acquisition as a gap if only a headnote is public.
- Do not copy or scrape paid full texts.
- Use open official decisions from the Supreme Constitutional Court, State Council, administrative and economic courts where they are genuinely public.
- Distinguish holding, headnote, summary, ratio, obiter and secondary commentary; no case principle without a traceable decision locator.

## 8. Initial progress measurement

A defensible percentage needs a denominator. The first denominator is now **36 legal domains**, not an estimate of all individual laws/cases:
- 36/36 domains have been named in the national inventory (scope definition only; this is not 100% coverage).
- 30 source institutions/platforms are registered, including the Supreme Constitutional Court, State Council, Consumer Protection Agency, NOSI, Administrative Control Authority, National Elections Authority, Customs Authority and Economic Courts.
- 139 anchor instruments have acquisition records with their source/access status.
- 35 source PDFs have been opened across the tranches (not all are bare Gazette originals: Commercial Code is a government-published reprint and Customs Law is an authority-annotated compilation); Law160/2026 official HTML text was also opened. Several more have only official listing metadata.
- No nationwide article-by-article consolidated statute corpus has been produced. A public judicial collection register now includes 25 leads (one Constitutional Court press summary, one recent bulletin and 23 State Council principle-series targets); the underlying judgments/volumes are mostly not yet acquired.
- No nationwide court judgment corpus has been acquired.
- No lawyer-reviewed national corpus exists.

Do not turn the 33-domain planning inventory into a false legal-coverage percentage. Report separate metrics for domain mapping, source acquisition, primary-source matching, amendment/currentness validation, judicial collection and lawyer review.

## 9. Next acquisition priorities

1. **Civil/constitutional/procedural core:** retrieve complete Arabic texts for Civil Code, Evidence Law, Civil and Commercial Procedure Code, Constitution and constitutional judgments; enumerate every amendment.
2. **Criminal core:** Penal Code and all special penal laws; preserve Law174/2025 as future law until 1 Oct 2027; acquire Law160/2026 Gazette PDF and all implementing instruments.
3. **Tax/customs:** download all ETA-listed amendment PDFs, including Laws149–153/2026; create article-level redlines and expiry alerts; acquire current executive regulations and Customs Authority circulars.
4. **Commercial/company:** Commercial Law17/1999, Companies Law159/1981, Investment Law72/2017, Bankruptcy Law11/2018 and executive regulations/GAFI decisions.
5. **Social/family:** Social Insurance Law148/2019, Unified Insurance Law155/2024, Family Courts Law10/2004, Personal Status laws and Child Law12/1996.
6. **Regulatory sectors:** FRA rules, CBE circulars, EEAA regulations, building/urban planning, consumer/competition, data protection/cybercrime and health/education/transport.
7. **Judicial principles:** harvest free official headnotes by subject and court; identify restricted full-text gaps and never bypass access controls.

## 10. Trust and rights defaults

Every newly discovered record starts as `unverified` or `source_matched` only when exact source comparison has actually been done. Keep `lawyer_reviewed=false` and `rights_cleared=false` unless supported by explicit evidence. Do not commit source PDFs or bulk transcriptions unless repository policy, source terms and copyright/reuse rights have been assessed.


## Additional public legal sources and anchor laws

The acquisition register has been expanded to 40 anchor instruments. Newly located official public sources include:
- Consumer Protection Agency's 32-page Law181/2018 PDF (text layer has character-encoding problems in portions and needs page-image checking).
- National Organization for Social Insurance announcement confirming Law148/2019 and its original commencement structure; full law text remains to acquire.
- Administrative Control Authority's official legislative-framework page, which identifies a broad set of criminal, administrative, judicial, public procurement, AML, competition and public-integrity statutes, and expressly labels Civilian State Employees Law47/1978 repealed while identifying Civil Service Law81/2016.
- GAFI and ITIDA as official discovery portals for investment/company and intellectual-property/e-signature legislation.

Additional statutes indexed include Laws 46/1972, 47/1972, 54/1964 as amended by 207/2017, 75/1963, 80/2002, 81/2016, 109/1971, 117/1958, 182/2018, 3/2005, 11/1968 and 47/1973. These are source-index leads, not full text acquisitions.


## 11. Progress dashboard — explicit denominator and no false 100%

| Measure | Result | Meaning |
|---|---:|---|
| Legal-domain scope mapped | 36/36 (100%) | Scope definition only; not full legal coverage |
| Source institutions/platforms registered | 29 | Government, courts, regulators and discovery sources |
| Seed anchor instruments inventoried | 139 | Starter set, not the total universe of Egyptian laws and decisions |
| Source PDFs opened | 35/139 (25.2% of seed list) | Includes government reprints, official agency copies and files with unreadable/garbled text layers; not all are bare Gazette originals |
| Nationwide consolidated statute domains | 0/36 | No domain yet has all base laws, amendments, executive regulations and currentness fully consolidated |
| Full official SCC judgment texts acquired/indexed | 6 | Five additional 2026 invalidity notices are registered as public homepage summaries only, not full judgments. Cases2/44 (2026), 115/25 (2026), 98/43 (2026), 100/43 (2023) and188/35 (2023); cases99/43 and16/24 remain cited-holding leads |
| Lawyer-reviewed national instruments | 0 | Human legal review remains mandatory |

**Overall nationwide legal knowledge collection estimate: 5%.** This is a cautious project-management estimate, not a count of all Egyptian laws or judicial decisions. It reflects the still-small share of actual full-text acquisition, amendment consolidation, currentness verification, judicial corpus collection and lawyer review. It must rise only when the underlying documents and legal relationships are acquired and checked—not when source URLs are merely discovered.



## Constitution and election-law tranche

The National Elections Authority public library yielded seven further official Arabic PDFs: the 2014 Constitution as amended in 2019 (63 pages), Law198/2017 (15 pages), Political Rights Law45/2014 (23 pages), House Law46/2014 (18 pages), Senate Law141/2020 (21 pages), House district Law174/2020 (21 pages), and amendment Law140/2020 (9 pages). The consolidated Law46 PDF records Law85/2025 amendments; standalone Law85/2025 and Law84/2025 primary Gazette copies remain pending. Full acquisition notes are in [Constitution and election-law tranche](egypt_constitution_and_election_law_acquisition_2026-11-17.md).


## Commercial, customs and social insurance tranche

New official source discoveries:
- Commercial Code Law17/1999: government-published second-edition PDF hosted by ETA; 3,759 extracted lines. It records Gazette issue19 bis, 17 May 1999 and amendment Law168/2000's changes to cheque dates.
- Customs Law207/2020: 70-page Customs Authority compilation reproducing Gazette issue45 bis (D), 11 Nov 2020, with commentary; separately retain its annotated status.
- Customs Executive Regulation Decision430/2021: official Egyptian Gazette supplement issue193, 31 Aug 2021; 4,482 extracted lines. Amendment leads include Decisions52/2023, 347/2023, 50/2024, 54/2024 and 262/2026.
- NOSI library: 168 public legal/decision records across 34 pages. NOSI's 30 Nov 2025 announcement states that from 1 Jan 2026 insured contribution wage limits are EGP2,700 minimum and EGP16,700 maximum; minimum new pension EGP1,755 and maximum EGP13,360. These are dated operational parameters, not amendments to Law148/2019.
- Customs Authority has a public export control notice for Circular19/2026 concerning controlled pharmaceutical preparations to Kuwait; the 22 MB attachment and schedules remain unacquired.

See [Commercial, Customs and Social Insurance tranche](egypt_commercial_customs_social_insurance_acquisition_2026-11-17.md).


## Companies and insolvency tranche

- Companies Law159/1981: official ETA-hosted PDF opened (993 extracted lines). It records amendments by Law3/1998 and Law94/2005 and cites a 2001 Supreme Constitutional Court ruling invalidating part of Article17. It is not a consolidated 2026 text; Law17/2015 and GAFI rules remain to integrate.
- Insolvency Law11/2018: 279-article secondary full text located; primary Gazette issue7 bis(D), 19 Feb 2018 still outstanding.
- Law11/2021: official government-hosted Gazette PDF (issue16 bis(W), 28 Apr 2021) acquired; it adds electronic litigation under Article3 bis and amends numerous insolvency provisions.
- Ministry of Justice Decision3715/2026: official GPO text page located; amends Decision2208/2019 on Bankruptcy Administration expert fees/deposits. Exact Gazette metadata and effective date still need capture.
- Insolvency, restructuring and bankruptcy are now a dedicated 33rd domain.

See [Companies and Insolvency acquisition](egypt_companies_insolvency_economic_courts_acquisition_2026-11-17.md).


## Investment and public-finance tranche

- Law72/2017 Investment Law: official 924-line ETA PDF opened; Article8 expressly repeals Law8/1997; it establishes four investment regimes and requires PM executive regulation.
- Law8/1997: official PDF acquired as historical/superseded only.
- PM Decision2310/2017 Investment Executive Regulation: official 89-page PDF located; non-circulation watermark and unreadable text layer mean article extraction is still pending.
- Mortgage Finance Law148/2001 and Finance Leasing Law95/1995: official ETA-hosted PDFs opened (16 and 10 pages) but no readable text layer.
- Commercial Registry Law34/1976: official six-page PDF with 173 extracted lines; Article4 records Law98/1996 amendment.
- Law148/2026 amending Law147/1984: official Gazette PDF sets EGP100 departure fee (with stated exemptions) and EGP35 per ton cement levy, effective 29 July 2026.
- Law154/2026: official Gazette PDF imposes 5% distributable net profit allocation for wholly state/public-owned companies and 4% for state/public ownership above 50%, capped at state share; transferred within four months, effective 29 July 2026.
- Law12/2003 is recorded as a historical predecessor expressly repealed by Labour Law14/2025 Article12.

See [Investment, Commercial Registry and Public Finance acquisition](egypt_investment_commercial_registry_public_finance_acquisition_2026-11-17.md).


## VAT Law149/2026 amendment extraction

The official ETA-hosted Gazette PDF for Law149/2026 (issue30 bis(A), 28 July 2026) has been opened and extracted. It amends VAT Law67/2016 Articles3,5,28 bis and30, updates six exempt-list items, adds a new Article22 rule for machinery/equipment/medical devices under Article28 bis, adds natural gas at EGP20 per 1,000 cubic feet, and repeals two prior schedule entries. It commenced 29 July 2026. A four-page article-by-article extraction with conditions and product safeguards is recorded in [VAT Law149/2026 extraction](egypt_vat_law149_2026_amendment_extraction.md).


## Real-estate and historic tax-law tranche

- Real Estate Tax Law196/2008: official 12-page ETA PDF opened; OCR is materially corrupted and requires page-image transcription.
- Law103/2012 amending Real Estate Tax Law196/2008: official 8-page PDF opened; extracted dates/article numbers are corrupted, so no substantive values are accepted from OCR.
- General Sales Tax Law11/1991: official 38-page PDF opened without text layer; historical only after VAT Law67/2016.
- Law102/2012 amendment to Sales Tax Law11/1991: official 6-page PDF opened without text layer; historical only.
- State Financial Resources Development Fee Law147/1984: ETA index lead; base PDF retrieval failed; Law148/2026 is only a narrow amendment.
- Stamp Tax Law111/1980: base law PDF retrieval failed; Law153/2026 confirms the base law identifier; ETA filename incorrectly appears to say 1981 and must be reconciled against Gazette.

See [Real-estate and historical tax acquisition](egypt_real_estate_and_historical_tax_law_acquisition_2026-11-17.md).


## Environmental and waste-management tranche

- Natural Reserves Law102/1983: official EEAA six-page Arabic PDF opened; Articles1–2 define reserves and prohibit harmful/unauthorized activity.
- Environment Law4/1994: EEAA official law library lists Law9/2009 and Law105/2015 amendments, PM338/1995 Executive Regulation and eight amendments through PM2466/2024.
- Waste Management Law202/2020: official EEAA index; PM722/2022 full official GPO text page located. Annexes6–11 and18 are identified as containing healthcare-waste standards, tracking forms and records; Articles65–78 contain penalties.
- PM662/2025: official EEAA 2026 page confirms extended producer responsibility for single-use plastic shopping bags; Articles27, 18 and19 are relevant.
- EEAA decision register: 39 official index-listed decisions plus PM662/2025 (40 rows) covering coal, charcoal, EIA, protected areas, climate, waste, fees and environmental consultants.
- **Identity discrepancy:** an EEAA search-result extract appears to label Law152/2021 as medical-waste regulation, but Official Gazette DSpace metadata identifies Law152/2021 as the Epidemics and Health Pandemics Law. This conflict is flagged; the law is not classified as a medical-waste statute pending source reconciliation.

See [Environmental and Waste Law acquisition](egypt_environmental_and_waste_law_acquisition_2026-11-17.md) and [dedicated environmental instruments register](../../data/research/egypt_environmental_instruments_register_2026-11-17.csv).


## 2026 strategic development authority and budget tranche

- GPO full text for Law147/2026 reorganizing the Future of Egypt Sustainable Development Agency was located. It creates sustainable development zones, an Ahramat Al Nile sovereign wealth fund and a Daem service fund, and contains special licensing, asset-transfer, governance and financial rules.
- **Identifier discrepancy:** Ministry of Finance's public index labels a same-title instrument Law47/2026, while the GPO primary text and secondary text identify Law147/2026. This is flagged for Gazette cover/issue reconciliation; no duplicate law is created.
- Law77/2026 State General Budget for FY2026/2027: GPO full text located; effective from 1 July 2026; budget tables remain to be structured.
- PM Decision2034/2026: MOF listing says Cotton Arbitration and Testing Authority becomes a service public authority from FY2027/2028; full text pending.
- Cabinet Decision80/2026: MOF listing shows 50% of inspection/examination fees allocated for specified purposes under an incompletely displayed Law168 reference; full title/text pending.

See [2026 Future Egypt authority and budget acquisition](egypt_2026_future_egypt_authority_and_budget_law_acquisition.md).


### Law147/2026 identifier and commencement correction

Official Gazette DSpace metadata now resolves the earlier Law47/147 discrepancy:
- Gazette issue30 (repeated), 26 July 2026.
- DSpace record identifies Law147/2026 reorganizing the Future of Egypt Sustainable Development Agency; original 426.95 KB PDF is listed.
- Official GPO text also identifies Law147/2026.
- Article14 commencement is the day after publication: 27 July 2026.
- Ministry of Finance's Law47/2026 listing is treated as a catalogue-number error for this same title unless a separate Gazette instrument is produced.
- The DSpace original PDF has not yet been downloaded/hashed, so primary metadata is matched but file-byte verification remains pending.


## Additional SCC case-law tranche — salary and social insurance

Three further official SCC judgment texts were located:
- Case98/43 (7 March 2026): declares Law18/2015 Art61 unconstitutional insofar as it withholds half salary during pretrial detention where criminal responsibility is finally excluded; concerns the historical 18/2015 validity period (12 Mar 2015–20 Jan 2016).
- Case100/43 (4 Nov 2023): declares Law81/2016 Art64(1) unconstitutional in the same limited scope; Official Gazette issue44 (repeated), 4 Nov 2023; effects from 5 Nov 2023.
- Case188/35 (8 July 2023): declares Law79/1975 Art20(2) (as amended by Law130/2009) and attached Table9 unconstitutional for early-retirement pension actuarial factor inequality. Law79/1975 was later repealed by Law148/2019, so the judgment is historical-period relevant. Exact Gazette publication/effective date still pending.

See [SCC salary and social-insurance judgments](egypt_scc_public_service_salary_and_social_insurance_judgments_2026-11-17.md).


## SCC case244/23 — public-official criticism and publication fines

The official SCC full judgment for case244/23 (session 7 March 2026) was acquired. It rejects the constitutional challenge to Penal Code Art185 (insulting public officials), Art302(2) (public-interest criticism), and Art307 insofar as applied to Art185. It confirms that the Art302(2) safe harbor requires **good faith, connection to official duties, and proof of truth**. It records Art185 fine range EGP10,000–20,000 and the Art307 newspaper-publication multiplier of EGP20,000–40,000 in the statutory version before the Court. The judgment also confirms that earlier challenges to Arts302/303/306/307 were already resolved by cases60/22 (2024) and16/24 (2025).

See [SCC case244/23 analysis](egypt_scc_public_official_criticism_case_244_23_2026.md).


## Court of Cassation public headnotes tranche

The Court of Cassation official homepage yielded 18 public headnotes across labour, social insurance, customs, commercial/insolvency, banking, criminal procedure/sentencing, family and civil procedure. These are headnotes only, not full judgments. The Court's official subscription page states full judgments, advanced search, legislative database and stamped PDF downloads require subscription; it lists EGP1,080/year for Egyptian subscribers. No subscription restrictions were bypassed. The public headnotes and their exact access boundary are recorded in [Court of Cassation public headnotes harvest](egypt_court_of_cassation_public_headnotes_harvest_2026-11-17.md).


## 2026 SCC invalidity watchlist

The official Court of Cassation homepage lists five recent SCC invalidity notices:
- Case71/37: fourth paragraph of Article39, Law117/1958 (Administrative Prosecution), published 11 Oct 2026.
- Case46/46: final paragraph of Article41, Presidential Decree316/1994 (National Water Research Center), published 11 Oct 2026.
- Case47/46: fourth paragraph of Article45, Law110/1975 (Productive Cooperation), published 10 Sep 2026.
- Case49/42: final paragraph of Article78, Law148/2019 (Social Insurance and Pensions), published 10 Sep 2026.
- Case25/43: second paragraph of item(b) of Article1, Agriculture Decision1432/1991, published 5 Apr 2026.

These are public invalidity notices only; full judgments, exact Gazette issue/pages and effective dates remain outstanding. Case49/42 is the highest priority because it concerns current Law148/2019. The statutory register now flags Article78 for non-application pending the full operative judgment.

See [2026 SCC invalidity watchlist](egypt_scc_2026_recent_unconstitutionality_watchlist.md).


## 15. Additional nationwide acquisition tranche — FRA, CBE, IDA, MOHP, SCC and Ministry of Finance

**Added 17 November 2026.** Companion registers:
- `data/research/egypt_regulatory_instrument_harvest_2026-11-17.csv` — 19 regulatory/judicial records.
- `data/research/egypt_sectoral_law_harvest_2026-11-17.csv` — 19 construction, industry, health and constitutional records.
- `data/research/egypt_mof_general_law_catalogue_harvest_2026-11-17.csv` — 19 cross-domain catalogue/instrument records.

### FRA and CBE

The FRA portal is a large discovery index with 61 pages in its English general-legislation section and separate Arabic/sector pages. It includes laws, executive regulations, board decisions, chairman decisions and circulars across capital markets, insurance, non-bank finance, AML/CFT, fintech, accounting, carbon/sustainability and movable collateral. Public consolidated PDFs opened in this pass:
- AML Law 80/2002 (15 pages), with the text identifying amendments including Laws 17/2020 and 154/2022.
- FRA Board Decision 145/2021 on bond offerings (9 pages), whose consolidation states its latest amendment was Decision 136 dated 8 July 2026.
- FRA Board Decision 173/2014 on microfinance-company rules (57 pages), consolidated through 8 October 2025, with an amendment history listed in its footnote.
- Law 155/2024 Unified Insurance Law page and prior-insurance-law list.
- Law 10/2009 non-bank financial market regulation page and consolidated-copy link (version label 2019).
- Further leads include Decision 135/1993 (Capital Market Law executive regulation, version label 2025), PM Decision 951/2003 (AML executive regulation, version label 2023), Laws 141/2014, 159/1981, 3/2005, 93/2000, 203/1991 and 146/1988.

The CBE circular index exposes 405 records. Visible examples include circulars dated 27 October, 12 October, 28 September and 24 September 2026. The CBE Regulations Book page was last updated 30 September 2026 and points to an Arabic Banking Supervision Regulations Guide. Direct page retrieval was rejected in this pass, so the 405 are catalogue entries, not acquired circular texts.

### IDA and MOHP

The IDA legislation page lists Building Law 119/2008; Industrial Licensing Law 15/2017 and Executive Regulation 1082/2017; Reconciliation Law 187/2023 and Executive Regulation 1121/2024; Environment Executive Regulation 338/1995; Industry Law 21/1958; Industrial Register Law 24/1977; and multiple hazardous-material, waste and heavy-industry decisions. Official PDF links for Laws 119/2008 and 15/2017 and Decisions 338/1995 and 1082/2017 were opened and page-count checked, but their text was not exposed by the web parser. Law 187/2023's Official Gazette facsimile (issue 50 bis A, 17 December 2023) was opened with readable text; it repeals Law 17/2019 and contains transition rules for pending applications. Decision 1121/2024 was listed but timed out when fetched.

The MOHP 2025 Health Investment Guide was opened with 1,155 extracted lines. It reproduces substantial text from Law 87/2024 on public-utility concessions for health facilities and identifies PM Decision 2856/2024 as the executive regulation. It also indexes Law 51/1981 (amended by 153/2004), medical practice Law 415/1954, physical therapy Law 3/1985 and Decision 150/1986, dentistry Law 537/1954, pharmacy Law 127/1955, blood/plasma Law 8/2021, mental health Law 71/2009 amended by 210/2020, and medical laboratory professions Law 367/1954. The guide is a discovery/administrative source, not a substitute for Gazette acquisition.

### Supreme Constitutional Court

The official SCC portal exposes separate searches for legislation, case status, legal principles, substantive/formal constitutional judgments, jurisdiction conflicts, execution disputes and legislative interpretation decisions. The portal's indexed dashboard shows counters including 7,848 judgments and 1,080 substantive judgments; these are portal counters, not acquired files. A public summary for 3 January 2026 records rejection of a challenge to specified Penal Code terrorism provisions and Anti-Terrorism Law 94/2015. Full judgment and exact docket locator remain to be acquired. The official portal also displays featured judgment sessions in 2026; each docket must be harvested individually.

### Ministry of Finance cross-domain index

The Ministry of Finance search index reports 936 general-law catalogue records and 522 financial-law catalogue records. These are enumeration queues only, not the universe of Egyptian law. The Ministry expressly warns that its online texts are guidance and the sole legal reference is the Official Gazette.

New catalogue leads recorded include:
- Law 157/2024 amending Civil and Commercial Procedure Law 13/1968 (Gazette issue 27 bis D, 10 July 2024).
- Evidence Law 25/1968; Civil Code Law 131/1948 and related amendment Law 55/1970; Companies Law 159/1981 and Executive Regulation Decision 96/1982 (including amendment Decision 1212/2004).
- Unified Public Finance Law 6/2022, amendment Law 18/2024 and related decisions.
- 2026 catalogue entries: Laws 148/2026, 154/2026, 47/2026, 149/2026, 152/2026 and 153/2026; Customs Decision 262/2026.
- Economic Courts Law amendment 156/2024; judicial organization Law 15/2025; VAT amendment Law 157/2025; Constitution 2014 as amended in 2019.

**Important identifier warning:** the Ministry catalogue's Law 47/2026 title concerning the Future of Egypt authority conflicts with a separate primary-source acquisition identifying Law 147/2026 for the same title. The main research baseline records the primary-source reconciliation; do not duplicate or rely on the catalogue number without checking the Gazette.

### Counting rules

- An index entry is not a downloaded instrument.
- A PDF link opened by page count is not a text extraction.
- A ministry guide reproducing statutory text is not an Official Gazette match.
- A public case summary is not a full reasoned judgment.
- All new records retain `lawyer_reviewed=false` and `rights_cleared=false`.
- No domain is yet complete end-to-end with all base laws, amendments, executive instruments, currentness and judicial interpretation.


## 16. Asylum, migration, telecoms and data-protection acquisition — 17 November 2026

A new 12-record register is added at `data/research/egypt_asylum_migration_telecom_data_protection_harvest_2026-11-17.csv`.

### Foreign Asylum Law and executive regulation

The Official Gazette publisher's indexed text identifies Prime Minister Decision 1568/2026 as the Executive Regulation of Foreign Asylum Law 164/2024. DSpace metadata identifies Official Gazette issue 21 supplement (B), dated 21 May 2026, with a 404.03 KB file. The decision states that it takes effect after three months from publication. The exact effective date should be computed and recorded under the applicable statutory time-computation rules before use.

The regulation defines the competent ministry as the Ministry of Interior and the competent committee as the Permanent Committee for Refugee Affairs. The indexed text includes:
- Definitions of refugee, asylum seeker and priority/vulnerable groups.
- Application and legal representation procedures, including a free qualified representative where a person lacking capacity has no legal representative.
- Family applications and written consent for adult family members.
- Registration, preliminary medical screening, classification and referrals.
- Case-management, health, psychological and social support duties.
- A decision deadline of up to six months for applicants who entered lawfully and up to one year for those who entered unlawfully.
- Temporary measures, including prior permission for travel between governorates or outside Egypt, with proportionality safeguards and challenge procedures.
- Registration cards, refugee documents and travel documents.
- Cessation/termination grounds.

This is a high-priority current legal domain. Acquire the Gazette PDF, compare the full GPO text to the scan and extract every article; the index snippets are not a substitute for full text. The regulation's preamble also points to Law 89/1960 (foreigners' entry/residence), Nationality Law 26/1975, Child Law 12/1996, Anti-Trafficking Law 64/2010, Illegal Migration Law 82/2016, Persons with Disabilities Law 10/2018, Personal Data Protection Law 151/2020 and other related laws. These are now in the cross-reference queue.

### Telecommunications and spectrum

NTRA's official digital services portal displays a notice that new rules for wireless communication devices and radio spectrum began on **16 November 2026** under an NTRA Board decision. The exact decision number and linked instrument still need acquisition. NTRA also publishes:
- Telecommunications Regulation Law 10/2003 (the located English translation expressly says Arabic prevails and prohibits republication without prior permission; do not copy the translation into the corpus).
- General Rules for Protection of Telecommunications Service Users (official Arabic PDF lead).
- Radio Spectrum Fees rules, with the located Arabic PDF stating application from 1 July 2020.
- Additional service-specific rules and licensing frameworks.

The next step is to acquire the Arabic Gazette text of Law 10/2003, current NTRA board decisions and the 16 November 2026 wireless/spectrum rules. A public official portal notice is a discovery lead, not the decision text.

### Data protection, cybercrime and electronic transactions

The official MCIT Digital Egypt legislative framework identifies:
- Personal Data Protection Law 151/2020.
- Anti-Cyber and Information Technology Crimes Law 175/2018.
- Electronic Signature Law 15/2004.

MCIT describes Law 151/2020 as regulating personal-data collection and processing, Law 175/2018 as addressing crimes directed at networks and information systems, and the e-signature law as granting legal validity to digital transactions. The primary Gazette texts, executive regulations and regulator decisions remain to be acquired. A 2024 MCIT fintech report is only a secondary explanatory source and must not substitute for the law.

An official GPO decision, PM Decision 2564/2024 on the unified government complaints system, cites Laws 151/2020 and 175/2018 alongside Civil Service Law 81/2016 and Local Administration Law 43/1979. It is a useful cross-reference for public-sector data handling and secure digital complaints, but the full instrument and implementation details still require extraction.

### Rights and status

The NTRA English Law 10/2003 translation carries an explicit restriction against publication without prior permission. The corpus should prioritize Arabic official Gazette texts and store the English translation only as a locator/reference unless permission is obtained. All new records remain lawyer-unreviewed and rights-un-cleared.


## 17. Focused asylum-law instrument note

A dedicated note has been added at `egypt_asylum_law_164_2024_pm_decision_1568_2026.md`. It records the Official Gazette issue 21 supplement (B), 21 May 2026, DSpace metadata, the three-month commencement clause, selected articles on legal representation, family applications, screening/case management, decision periods, temporary measures, registration cards and cessation grounds. It preserves the distinction between the indexed official publisher text, repository metadata and the still-pending full-file hash/article-by-article scan comparison. The source note is not lawyer-reviewed.


## 18. Supreme Constitutional Court public docket index tranche

A 19-row public docket/disposition register has been added at `data/research/egypt_scc_public_case_index_harvest_2026-11-17.csv`. It records visible SCC session-index entries from 3 January, 9 September and 7 November 2026, including constitutional cases, conflict-of-jurisdiction matters and execution disputes. The register preserves only what the public court page exposes: docket number, session/publication date and disposition. Most entries do not identify challenged provisions or reasoning. The January 2026 featured anti-terrorism summary has no docket number in the indexed snippet and is deliberately kept separate from the docket list. None of these records is treated as a full judgment or legal ratio. Full judgments, exact legal issues, Gazette publication and lawyer review remain outstanding.


## 19. Progress dashboard — 17 November 2026, after current acquisition pass

### National legal knowledge completion

**Overall nationwide legal-content completion: approximately 1.5% (rounded to 2% for reporting).** This is a conservative project-management estimate, not a statistically measured percentage of every Egyptian statute, regulation, circular, judgment, opinion or historical version. The complete denominator remains unknown and the 936/522 MoF catalogue counters are only partial catalogue denominators.

### Measurable sub-progress

| Workstream | Current result | What it means |
|---|---:|---|
| Legal-domain scope map | 30/30 (100%) | All planned domains have been named; this is scope mapping only |
| Initial source register | 17 source records | Core official and discovery sources registered; not all institutions identified |
| Initial anchor statute register | 40 records | Seed statutes/amendments with acquisition states |
| FRA/CBE register | 19 records | Regulatory decisions and collection leads; CBE 405 circulars are index records, not full-text acquisitions |
| IDA/MOHP/SCC sector register | 19 records | Construction, industrial, health and constitutional source/instrument leads |
| MoF catalogue register | 19 records | Cross-domain law and decision leads; MoF portal reports 936 general and 522 financial catalogue records |
| Asylum/telecom/data protection register | 13 records | Includes PM Decision 1568/2026 and NTRA/data-protection/cybercrime leads |
| SCC public docket register | 19 records | Public docket/date/disposition records; not full judgments |
| Full national domains complete | 0/30 | No domain yet has all base laws, amendments, regulations, decisions, case law and currentness checks complete |
| Full SCC/Cassation/State Council judgment corpus | 0 | Public summaries and docket indexes only; no nationwide full judgment corpus |
| National-corpus lawyer sign-off | 0% | Human review remains outstanding |

### Actual text acquisition versus discovery

- **Primary/official legal text opened or inspected in the initial tranche:** Civil Code 131/1948; tax amendments Laws 150–153/2026; Capital Market Law 95/1992 consolidated text; Criminal Procedure Law 174/2025; Law 160/2026 commencement text; Consumer Protection Law 181/2018 (text-layer issues); FRA AML Law 80/2002; FRA Decisions 145/2021 and 173/2014; Law 187/2023; PM Decision 1568/2026 executive regulation text.
- **Official PDF links opened but not yet text-extracted:** Building Law 119/2008; Industrial Licensing Law 15/2017; Environment Executive Regulation Decision 338/1995; Industrial Licensing Executive Regulation Decision 1082/2017.
- **Official administrative guide extracted:** MOHP 2025 Health Investment Guide (1,155 lines), containing legal extracts and cross-reference lists but not a substitute for primary Gazette copies.
- **Index-only queues:** MoF general/financial catalogue, FRA 61-page index, CBE 405 circular index, SCC docket calendar, State Council principle-series leads, and IDA law/decision listings.

The exact list above is a status snapshot; it is not a claim that every listed text is complete, current, Gazette-matched, reusable or lawyer-approved.

### Repository integration

- PR #1855 merged: national FRA/CBE, sectoral, MoF and baseline/index expansion.
- PR #1856 merged: focused asylum-law note index.
- PR #1857 merged: SCC public docket register.
- PR #1854 closed as a stale diverged draft superseded by #1855.
- GitHub Actions billing issue remains external; no CI success is claimed. Structural CSV checks were run through the available tooling for the 19-row FRA/CBE, 19-row sectoral and 19-row MoF CSV files: all had 11 columns per row, no malformed row lengths and no duplicate record IDs. This is structural validation only, not legal validation.

### Next work priority

1. Acquire and article-map the complete official Gazette texts for Laws 164/2024 and Decision 1568/2026, Civil Procedure Law 13/1968 with Law 157/2024, Evidence Law 25/1968 and Companies Law 159/1981 with its current regulation.
2. Harvest the NTRA 16 November 2026 rules and the CBE circular archive as dated individual instruments.
3. Expand SCC public full judgments and Cassation public headnotes with case numbers, challenged provisions, holding and Gazette publication.
4. Start article-level consolidation of the highest-priority core codes; no domain is counted complete until amendment and currentness checks pass.


## 20. NTRA wireless-device and radio-spectrum rules — effective-operation notice

A focused update is added to the asylum/telecom/data-protection register as AMT-013. The official NTRA digital portal notice states that new rules governing wireless communication devices and radio spectrum began operating on **16 November 2026**, pursuant to an NTRA Board decision. Existing licensees are instructed to regularize their position within three months, with the stated deadline **15 February 2027**, before the rules' sanctions and penalties begin to apply. The public notice does not expose the Board Decision number in the indexed text, and the linked full Arabic rules have not yet been acquired. This is a time-sensitive regulatory lead: the exact instrument, scope, transitional protection, penalties and Gazette status must be retrieved before the rules are used in legal answers.


## 21. Personal Data Protection Law 151/2020 and PDPC guidance acquisition

A dedicated 8-record register and legal-source note have been added:
- `data/research/egypt_personal_data_protection_law_151_2020_acquisition_2026-11-17.csv`
- `egypt_personal_data_protection_law_151_2020_acquisition_note.md`

The official MCIT-hosted Law 151/2020 PDF link was opened and reports 31 pages, but the text parser exposed no readable lines. The official PDPC-hosted Executive Regulation PDF URL for Ministerial Decision 816/2025 was identified but could not be retrieved in this pass. Secondary legal publishers identify publication in Gazette issue 244 (A) on 1 November 2025 and commencement on 2 November 2025; the Arabic Gazette copy remains required for verification.

Two official PDPC guideline PDFs were successfully text-extracted:
- Data Subject Consent Guidelines v1.1, 26 January 2026 (233 extracted lines).
- Privacy Notice Guidelines v1.1, 26 January 2026 (79 extracted lines).

The consent guideline lists six lawful bases under Article 6 of Law 151/2020 and sets conditions for valid consent, sensitive data, Arabic-first requests, granular/affirmative design, withdrawal and consent records. The privacy-notice guideline distinguishes notices from consent requests and internal privacy policies; it lists minimum notice contents and says direct collection requires notice at collection, while indirect collection generally requires notice within 30 days. Both guidelines state that they are not binding administrative/regulatory decisions and do not replace the Law or Executive Regulation.

**Currentness warning:** secondary legal sources report a one-year reconciliation period under Decision 816/2025 ending around 31 October/1 November 2026. The exact date varies by source. As of this snapshot the period appears to have elapsed, but the Arabic promulgation article, Gazette date-counting and any PDPC extension must be checked before asserting a deadline or enforcement consequence. MCIT's official 4 November 2026 news confirms PDPC implementation activity and a forum held on 26 October 2026; it is not itself a binding compliance circular.

The PDPC public portal and guideline suite are now a continuing source stream. Next: retrieve the full Arabic Executive Regulation, obtain the remaining PDPC guidelines (lawful bases, DPO, breach notification, security, data-subject rights, cross-border transfers and licensing), and capture all post-November 2026 decisions and forms.
