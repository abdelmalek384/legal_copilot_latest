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

The 30-domain matrix is in `data/research/egypt_national_legal_domain_inventory_2026-11-17.csv`.

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

A defensible percentage needs a denominator. The first denominator is now **30 legal domains**, not an estimate of all individual laws/cases:
- 30/30 domains have been named in the national inventory (scope definition only; this is not 100% coverage).
- 23 source institutions/platforms are registered, including the Supreme Constitutional Court, State Council, Consumer Protection Agency, NOSI and Administrative Control Authority.
- 40 anchor instruments have acquisition records with their source/access status.
- 8 instruments have official PDF text actually opened in this tranche (including the Consumer Protection Law PDF, whose text layer has encoding issues); Law160/2026 official HTML text was also opened. Several more have only official listing metadata.
- No nationwide article-by-article consolidated statute corpus has been produced. A public judicial collection register now includes 25 leads (one Constitutional Court press summary, one recent bulletin and 23 State Council principle-series targets); the underlying judgments/volumes are mostly not yet acquired.
- No nationwide court judgment corpus has been acquired.
- No lawyer-reviewed national corpus exists.

Do not turn the 30-domain planning inventory into a false legal-coverage percentage. Report separate metrics for domain mapping, source acquisition, primary-source matching, amendment/currentness validation, judicial collection and lawyer review.

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
| Legal-domain scope mapped | 30/30 (100%) | The national scope has been enumerated; this is planning coverage only |
| Source institutions/platforms registered | 23 | Includes government, courts, regulators and public discovery sources |
| Seed anchor instruments inventoried | 40 | A starter list, not the total universe of Egyptian legislation |
| Official PDF texts opened in this tranche | 8/40 (20% of seed list) | Civil Code, four 2026 tax laws, Capital Market Law, Criminal Procedure Law174/2025 and Consumer Protection Law181/2018; Law160/2026 official HTML text also opened |
| Nationwide consolidated statute domains | 0/30 | No domain is yet complete end-to-end with all amendments and currentness |
| Full judicial judgments acquired in this national tranche | 0 | One SCC press-summary lead and a bulletin were registered; State Council series are bibliographic targets |
| Lawyer-reviewed national instruments | 0 | Human legal review remains mandatory |

**Overall nationwide legal knowledge collection estimate: 3%.** This is a cautious project-management estimate, not a count of all Egyptian laws or judicial decisions. It reflects that the domain map and source discovery are ahead of actual full-text acquisition, consolidation, judicial corpus collection and lawyer review. It should rise only when primary text and amendment chains are actually acquired—not when a source URL is merely found.
