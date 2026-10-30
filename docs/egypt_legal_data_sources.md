# Egyptian Legal Data Collection — Source Registry

Status: initial source inventory; **not** a verified legal corpus. Links and access conditions must be rechecked before automated collection. Do not mark a document in force merely because it was found online.

## Collection goals

Build a broad Arabic-first Egyptian legal knowledge base with:
1. Constitution and constitutional amendments.
2. Laws, presidential decrees with legislative effect, prime-ministerial and ministerial decisions, executive regulations, circulars and other instruments.
3. Official Gazette (الجريدة الرسمية) and Egyptian Proceedings (الوقائع المصرية) issue-level records.
4. Court judgments, published principles, constitutional rulings and administrative judgments.
5. Treaties and ratification instruments.
6. Legal commentary, treatises, practitioner materials and forms in a separate non-primary-source collection.
7. Historical versions, amendments, repeals, effective dates and transitional provisions.

## Source registry

### Tier 1 — official primary sources

| Source | URL | Collection targets | Notes |
|---|---|---|---|
| Amiri Press / Official Gazette and Egyptian Proceedings | https://www.alamiria.com/Sec/Home | Gazette issues, laws, decrees, ministerial decisions, publication dates and issue metadata | Official publisher portal. Some historical copies may require archive requests, subscriptions or paid certified copies. Respect site terms and access controls. |
| Egyptian Court of Cassation | https://cc.gov.eg/ | Civil and criminal principles, published rulings, court publications and search metadata | Official court website. Search pages expose civil and criminal categories. Capture judgment/appeal identifiers, circuit, date and exact text when available. |
| Supreme Constitutional Court | https://www.sccourt.gov.eg/newportal/ | Constitutional rulings, interpretive decisions, constitutional documents, principles and publications | Official court portal with judgment and principle search. |
| Presidency of the Republic — Constitution (Arabic) | https://www.presidency.eg/AR/مصر/الدستور/ | Constitution text and official constitutional materials | Preserve the exact version and amendments reflected by the source. |
| State Information Service — Constitution (English) | https://sis.gov.eg/en/egypt/constitution-of-egypt/ | English-language reference/translation | Translation/reference only; Arabic official text should govern. |
| Ministry of Labour — laws and legislation | https://www.labour.gov.eg/ar/القوانين-والتشريعات/ | Labour Law No. 14/2025, older labour law, union law, social insurance and related instruments | Official ministry publication portal. Verify all texts against the relevant Gazette issue and later amendments. |
| Ministry of Labour — publications | https://www.labour.gov.eg/ar/الإصدارات/ | Official ministry guides, Q&A and publications | Label explanatory publications as guidance, not statutory text. |
| Ministry of Justice / Egyptian legislative and jurisprudence database | https://www.arablegalportal.org/ | Legislation and judicial materials where accessible | Listed as an Egyptian legal database in the Library of Congress guide. Verify the current operator, access terms, completeness and source provenance before bulk import. |
| Egypt House of Representatives | https://www.parliament.gov.eg/ | Bills, legislative history, parliamentary documents and enacted-law references where published | Bills and explanatory materials must not be treated as enacted law unless promulgation/publication is confirmed. |
| Ministry of Foreign Affairs | https://www.mfa.gov.eg/ | Treaties, agreements, ratification and international instruments where published | Record signature, ratification, entry-into-force and publication details separately. |

### Tier 2 — official specialist and sector sources

Start with the relevant ministry/regulator's official domain and collect legislation, executive regulations, decisions, circulars, official forms and guidance. Confirm the current official URL before adding a connector.

- Taxation, customs and tax procedures: Egyptian Tax Authority; Ministry of Finance; Egyptian Customs Authority.
- Banking, payments and financial regulation: Central Bank of Egypt; Financial Regulatory Authority; Egyptian Exchange where relevant.
- Companies, investment and commercial registration: GAFI; Ministry of Investment/Trade; relevant commercial-registration authorities.
- Employment, social insurance and workplace safety: Ministry of Labour; National Organization for Social Insurance; relevant occupational-safety authorities.
- Data protection, telecoms and cybercrime: National Telecom Regulatory Authority; relevant data-protection authority or official government publication; Ministry of Communications and Information Technology.
- Intellectual property: Egyptian Intellectual Property Authority and relevant official registers.
- Environment, agriculture, water and land: Ministry of Environment; Ministry of Agriculture; Ministry of Water Resources and Irrigation; land-registration and surveying authorities.
- Construction, housing, planning and local administration: Ministry of Housing; New Urban Communities Authority; relevant governorates and local authorities.
- Health, medicines and medical practice: Ministry of Health and Population; Egyptian Drug Authority; relevant professional regulators.
- Transport, aviation, maritime and public utilities: relevant ministries and statutory regulators.
- Education, universities and professional licensing: Ministry of Education; Ministry of Higher Education; relevant official bodies.
- Family, personal status, civil status and nationality: applicable legislation and official court/agency publications.
- Criminal law, procedure, prisons and prosecution: official Gazette, Court of Cassation, Supreme Constitutional Court and official prosecution publications where accessible.

These are collection categories, not confirmation that every agency provides a public downloadable dataset.

### Tier 3 — curated legal research and international repositories

| Source | URL | Appropriate use | Limitation |
|---|---|---|---|
| Library of Congress — Egypt legal research guide | https://wwws.loc.gov/law/help/legal-research-guide/egypt.php | Map official sources, court structure and print/archive sources | Research guide, not an authoritative legal text repository. |
| Library of Congress — Guide to Law Online: Egypt | https://guides.loc.gov/law-egypt/legal-guides | Discover primary and secondary sources | Follow each source back to the original publisher. |
| WIPO Lex — Egypt | https://www.wipo.int/wipolex/ | IP legislation, selected regulations and treaty materials | Coverage is subject-specific; verify current status against official sources. |
| ILO NATLEX — Egypt | https://natlex.ilo.org/ | Labour and social-policy legislation metadata and selected texts | Useful discovery source; translations may be unofficial and coverage may lag. |
| FAOLEX | https://faolex.fao.org/ | Agriculture, food, environment, water and natural-resource legislation | Subject-specific; verify against Egyptian primary sources. |
| Cyrilla / legal information resources | https://cyrilla.org/ | Discover digital-rights, privacy and technology-related legal texts | Secondary/discovery source; verify source, version and reuse rights. |

### Tier 4 — books, journals and practitioner materials

Collect only when the office has lawful access and the intended storage, indexing, model processing and user access are permitted.

- Current statutory collections and annotated codes.
- Treatises and explanatory works on civil law, civil procedure, evidence, criminal law and procedure, commercial/company law, labour, tax, administrative law, family law, intellectual property, data protection and other practice areas.
- Court-of-Cassation principle collections and judgment digests.
- Legal journals, dissertations, bar/practitioner publications and carefully sourced articles.
- Pleading templates, contracts, notices, checklists and forms.

Store commentary and templates separately from primary law. Preserve author, title, edition, year, publisher, volume, page and licence/access basis. A headnote or author's summary is not the judgment itself.

## First-pass collection order

1. **Foundational set:** Constitution; Civil Code; Civil and Commercial Procedure; Evidence; Penal Code; Criminal Procedure; Commercial Law; Companies Law; Labour Law 14/2025; Personal Data Protection Law 151/2020; relevant executive regulations and amendments.
2. **Court set:** published Court of Cassation civil and criminal principles; Supreme Constitutional Court decisions; Council of State/administrative judgments where officially accessible; other specialist court materials by practice area.
3. **Business and regulatory set:** tax, customs, banking, investment, companies, employment/social insurance, IP, telecoms/cybercrime and consumer protection.
4. **Public-law and personal-status set:** administrative, nationality, family/personal-status and civil-registration laws.
5. **Sector expansion:** environment, agriculture, construction/real estate, health, transport, education, public procurement, utilities and other fields identified by actual case demand.
6. **Secondary sources:** licensed commentary and practice materials, linked to the provisions and judgments they discuss.

This list is a prioritization proposal, not a claim that the listed laws have already been downloaded or verified.

## Required metadata for every document

Use one document-level record plus article/judgment chunks that point back to it.

- Stable internal ID and document type.
- Arabic title and optional English title.
- Instrument number, year, issuing authority, jurisdiction and subject tags.
- Gazette name, issue/number, publication date, page range and official source URL/archive reference.
- Original file URL, retrieval timestamp, file format, SHA-256 hash and preserved source file when permitted.
- Effective date, end/repeal date, status and the date on which status was checked.
- Amendment/repeal relationships and affected article numbers.
- Text language, whether translated, translator/source and translation authority.
- OCR status, extraction method, page/article boundaries and quality flags.
- Review status: unreviewed → source checked → text checked → amendment/status checked → approved.
- Reviewer, review date, licence/access restrictions and permitted processing/storage.
- For judgments: court, circuit, case/appeal number, judgment date, parties only where lawfully publishable, cited statutes, outcome, headnote-vs-full-text flag and source citation.

## Safe ingestion rules

- Keep original PDFs/HTML and extracted text linked by stable IDs; never replace the source with OCR output.
- Hash source files to detect duplicate or changed files.
- Keep article text and metadata in UTF-8; preserve Arabic punctuation, numbering and original page references.
- Split laws into articles only after checking the parser report against the original document. Preserve preambles, issuing provisions, schedules and annexes.
- Do not set `in_force=true` just because a source page exists. Use an explicit unknown/unverified state until effective status and amendments are checked.
- Do not merge amendments into the original text without storing the original and each amendment as separate versioned instruments.
- Do not mix official text, unofficial translations, commentary, templates and fictional test data in the same trust tier.
- Respect robots/access controls, terms, copyright and database rights. Do not bypass paywalls or login controls. Do not bulk-copy commercial books without permission.
- Do not upload client case files or confidential documents to external AI services as part of public-law collection.
- After each batch, publish a collection report: documents found, successfully downloaded, parse failures, duplicate hashes, missing article numbers, OCR flags, licence restrictions and unverified items.

## Immediate implementation checklist

- [ ] Review and correct the existing download manifest and downloader; README mentions `download_egypt_laws.py`, but verify that the file exists in the target branch before relying on it.
- [ ] Build a source manifest with source tier, source URL, allowed collection method, last checked date and expected document types.
- [ ] Add a document-level registry separate from article rows.
- [ ] Make legal status nullable/unknown; do not default unverified documents to in-force.
- [ ] Add a resumable downloader with conservative rate limits, hashes, retries and a per-source audit log.
- [ ] Add parsers and quality reports per source type (Gazette PDF, HTML law page, judgment page, scanned PDF).
- [ ] Add duplicate detection and amendment/version relationships.
- [ ] Add a human verification queue before the UI presents any item as current law.
- [ ] Build a benchmark set of Arabic legal questions with independently verified answers and citations.

## References checked for this initial registry

- Amiri Press portal: https://www.alamiria.com/Sec/Home
- Court of Cassation: https://cc.gov.eg/
- Court of Cassation judgments search: https://cc.gov.eg/judgments_search/
- Supreme Constitutional Court: https://www.sccourt.gov.eg/newportal/
- Presidency Constitution page: https://www.presidency.eg/AR/مصر/الدستور/
- Ministry of Labour legislation: https://www.labour.gov.eg/ar/القوانين-والتشريعات/
- Library of Congress Egypt legal research guide: https://wwws.loc.gov/law/help/legal-research-guide/egypt.php
- Library of Congress Egypt legal sources: https://guides.loc.gov/law-egypt/legal-guides
- WIPO Lex: https://www.wipo.int/wipolex/
- ILO NATLEX: https://natlex.ilo.org/
- FAOLEX: https://faolex.fao.org/

### Newly mapped discovery endpoints — 30 October 2026

- **Ministry of Parliamentary Affairs — issued laws index:** https://www.mpa.gov.eg/legislative-results/parliament. The public page exposes an enacted-laws search with legislative-session filters. Use it to discover law identifiers and cross-check them against promulgated Gazette texts; it is not itself proof of the exact Gazette text or current legal status.
- **IDSC digital repository:** https://dspace.id.com.eg/. Item pages expose issue metadata and PDF listings, sometimes with an item-specific `license.txt`. Access is item-dependent; some records are request-copy restricted. Inspect each item's licence and access state individually. Do not bypass restrictions or infer commercial reuse rights from a visible file listing.
- **Manshurat Qanuneya:** https://manshurat.org/. AUC's Law and Society Research Unit describes it as an open-access archive of Arabic Egyptian primary legal materials and judicial documents. Treat it as a high-value discovery/cross-reference source, not as blanket permission for bulk collection, commercial reuse, or redistribution. Follow each record to its original Gazette or court source and review item-level terms.

These additions are discovery-only. The source permission register deliberately leaves collection and commercial reuse unknown until supported by item-specific evidence. Public availability/open access is not the same as an open licence.
