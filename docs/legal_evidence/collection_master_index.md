# Egyptian legal knowledge collection — master index

**Last updated:** 2026-11-17  
**Repository:** `abdelmalek384/legal_copilot_latest`  
**Purpose:** durable index of source discovery and text-extraction checkpoints. This is not a legal corpus release, consolidated code, rights clearance, or lawyer certification.

## Current progress

- **Overall corpus coverage estimate: approximately 2% (provisional).**
- The estimate is deliberately conservative. Most work to date is source discovery, selected search-indexed text inspection and preservation of research notes. We do not yet have a validated count of unique law articles ingested into the product's searchable corpus.
- Do not increase overall coverage based on number of URLs, catalogue records, or checkpoint files.
- Lawyer-verified legal content: 0% under the project's current sign-off rule.
- Legal-source rights/permission: not presumed. Official public accessibility does not automatically establish commercial indexing, excerpt-display or redistribution rights.
- Machine labels must remain `source-matched, not lawyer-reviewed` where applicable; no `verified` label without qualified Egyptian lawyer approval.

## Collection checkpoints

| File | Main contents |
|---|---|
| [collection_checkpoint_2026-11-17.md](collection_checkpoint_2026-11-17.md) | Tax legislation: VAT Laws 67/2016, 149/2026, 157/2025; Income Tax 91/2005 and 151/2026; Unified Tax Procedures 206/2020; correction notice |
| [collection_checkpoint_2_social_insurance_fra_2026-11-17.md](collection_checkpoint_2_social_insurance_fra_2026-11-17.md) | Social Security 12/2025; Social Insurance 148/2019; Unified Insurance 155/2024; FRA implementation-decision inventory |
| [collection_checkpoint_3_procurement_admin_2026-11-17.md](collection_checkpoint_3_procurement_admin_2026-11-17.md) | Public Contracts 182/2018; amendment 188/2020; executive regulation and administrative-law leads |
| [collection_checkpoint_4_health_environment_ip_2026-11-17.md](collection_checkpoint_4_health_environment_ip_2026-11-17.md) | Universal Health Insurance 2/2018; Environment 4/1994; IP 82/2002; Competition 3/2005; Education 49/1972; Banking and telecom leads |
| [collection_checkpoint_5_civil_companies_procurement_2026-11-17.md](collection_checkpoint_5_civil_companies_procurement_2026-11-17.md) | Search-indexed Arabic Civil Code 131/1948 text and verbatim opening provisions; Companies 159/1981 latest displayed text and amendment list; Public Contracts 182/2018 text excerpts; Procedure 13/1968 and 157/2024 amendment; Income Tax source route |
| [collection_checkpoint_6_commercial_family_criminal_2026-11-17.md](collection_checkpoint_6_commercial_family_criminal_2026-11-17.md) | Commercial Code 17/1999, Trade Register 34/1976, family statutes, Penal Code 58/1937, procedural amendment mapping |
| [collection_checkpoint_7_criminal_finance_fra_2026-11-17.md](collection_checkpoint_7_criminal_finance_fra_2026-11-17.md) | Official Criminal Procedure 174/2025 text and transitional provisions; Evidence 25/1968; Public Finance 6/2022, regulations and discrepancy; FRA 10/2009; Economic Courts 120/2008 amendment |
| [collection_checkpoint_8_customs_tax_fra_2026-11-17.md](collection_checkpoint_8_customs_tax_fra_2026-11-17.md) | Customs 207/2020 and regulation amendment leads; Tax Procedures 206/2020 text; Economic Courts 120/2008 amendment; Financial Leasing/Factoring 176/2018 text; FinTech 5/2022 and FRA decisions |
| [collection_checkpoint_9_digital_consumer_law_2026-11-17.md](collection_checkpoint_9_digital_consumer_law_2026-11-17.md) | Data protection 151/2020, cybercrime 175/2018, e-signature 15/2004 and consumer protection 181/2018 source/dependency map |
| [collection_checkpoint_10_digital_consumer_finance_2026-11-17.md](collection_checkpoint_10_digital_consumer_finance_2026-11-17.md) | Official ITIDA e-signature texts, MCIT cybercrime index, CPA consumer-law index, FRA consumer-finance Law 18/2020 and 2026 guide |

## High-value primary-source portals

- Ministry of Finance legislation and decisions: https://mof.gov.eg/ar/legislation/legislation
  - Portal currently reports 936 laws and a separate decisions catalogue of 2,037 records. These are catalogue counts only.
  - It expressly warns that its electronic texts are guidance and the Official Gazette is the legal reference.
- Ministry of Investment and Foreign Trade legislation: https://www.mift.gov.eg/legislation/details/252
  - Structured law detail, amendments, executive regulations and attachments. Companies Law 159/1981 is an example.
- Egyptian Tax Authority law indexes:
  - VAT: https://www.eta.gov.eg/ar/content/qwanyn-aldrybt-ly-alqymt-almdaft
  - Income tax: https://www.eta.gov.eg/ar/content/qwanyn-aldrybt-ly-aldkhl
- Ministry of Justice official document downloads: https://moj.gov.eg/
  - Criminal Procedure Law 174/2025 direct Gazette PDF is recorded in checkpoint 7.
- Financial Regulatory Authority:
  - General legislation: https://fra.gov.eg/القرارات-الصادرة-تطبيقا-لاحكام-قانون/
  - Law 10/2009 updated PDF and general frameworks are recorded in checkpoint 7.
- Presidency constitutional text page: https://www.presidency.eg/ar/مصر/الدستور/

## Priority queue for next collection sessions

1. **Obtain and archive complete PDFs / text** for Civil Code 131/1948, Income Tax 91/2005, Public Contracts Executive Regulation 692/2019, Companies Executive Regulation 96/1982, Social Insurance Law 148/2019, and Unified Tax Procedures Law 206/2020.
2. **Build amendment graphs** with Gazette locators for each base statute, including corrigenda, repeals, commencement and transitional rules.
3. **Extract all articles** into stable UTF-8 JSONL with article ID, Arabic heading, full text, source URL, Gazette issue/date/page, source file SHA-256, extractor/version, retrieval timestamp, amendment status and review flags.
4. **Collect secondary legislation** from ministries and regulators: ministerial/PM decisions, executive regulations, circulars and binding instructions; classify guidance separately.
5. **Expand foundational law**: Penal Code 58/1937, Evidence 25/1968, Civil and Commercial Procedure 13/1968 (including 157/2024), Economic Courts 120/2008 (including 156/2024), Commercial Code 17/1999, personal status, administrative courts, property and tenancy.
6. **Judicial principles**: use only permitted public access; the Court of Cassation terms already reviewed in the source register require prior written approval for commercial use/publication and do not establish bulk/API permission. No bypass or scraping.
7. **Run source matching and lawyer review** before any content receives verified status.

## Rules for future updates

- Append a new dated checkpoint; do not overwrite historical observations.
- Distinguish (a) discovered, (b) text visible/indexed, (c) PDF bytes lawfully obtained, (d) text extracted and structurally validated, (e) Gazette-matched, (f) currentness checked, (g) lawyer-reviewed, and (h) rights-cleared.
- Count unique instruments and unique article texts, not repeated references.
- Record failed retrievals and conflicting metadata explicitly.
- Never claim the entire Egyptian legal system is complete. The scope includes national laws, regulations, decisions, treaties, court judgments/principles and changes over time; it is a continuously maintained corpus.
