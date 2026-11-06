# Phase 2 — Egyptian Legal Knowledge Base

**Status:** execution specification; not a claim that the corpus is complete.  
**Jurisdiction:** Arab Republic of Egypt.  
**Working rule:** the knowledge base must distinguish source discovery, acquisition, text extraction, source verification, legal-status review, and lawyer approval. These are separate states.

## Objective

Build an Arabic-first, version-aware Egyptian legal knowledge base across civil, criminal, labour, commercial, family/personal-status, administrative, tax, property/real-estate, and intellectual-property law. Add other foundational and regulatory areas needed to interpret those fields. Prioritize official legislation and its amendment chain. Add court judgments only through access and reuse methods permitted by the issuing court or rights holder.

## Current baseline and gaps

The repository already contains a source inventory, a collection pipeline, a permission register, a versioned legal-document registry, an audit tool, and a coverage matrix. These are infrastructure and planning assets, not proof of a complete legal corpus. The first-batch manifest contains only a small set of candidates; records may still have unknown effective dates, legal status, or review state. Treat any subject marked `not_started` in the coverage matrix as unbuilt until actual source records and reviewed documents demonstrate otherwise.

Do not solve coverage gaps by importing AI-generated answers, unverified consolidated codes, unofficial summaries, or search-result snippets as if they were primary legal texts.

## Subject coverage and collection targets

For every subject below, collect (where applicable): original enactment; every identified amending, repealing, correcting, or commencement instrument; executive regulations; relevant ministerial/regulator decisions; transitional provisions; official forms/guidance in a separate non-binding class; and judgments or principles where lawful access permits.

| Subject | Initial legislative targets | Critical temporal / classification issues | Priority |
|---|---|---|---|
| Civil | Civil Code No. 131/1948; Evidence Law No. 25/1968; obligations, contracts, torts, agency and special civil statutes | Amendment chain; historical vs current text; applicable date of transaction/event; article-level changes | P0 |
| Criminal | Penal Code No. 58/1937; special criminal statutes | Offence date; amendment and repeal dates; more-favourable-law questions require lawyer review | P0 |
| Criminal procedure | Code No. 150/1950 and every replacement, postponement, amendment, commencement and transition instrument | Never infer operative law from enactment alone; represent future commencement and transition explicitly; obtain specialist review | P0 |
| Labour | Labour Law No. 14/2025; commencement/transitional provisions; implementing decisions; Social Insurance and Pensions Law No. 148/2019; occupational safety and union legislation | Employment date and event date; distinguish statutes from ministry guidance; track implementing decisions and later amendments | P0 |
| Commercial / corporate | Commercial Code No. 17/1999; Companies Law No. 159/1981; Investment Law No. 72/2017; Bankruptcy Law No. 11/2018; competition, consumer and agency rules | Company type; transaction date; regulator circulars vs binding legislation | P1 |
| Family / personal status | Applicable personal-status statutes, procedure, marriage/divorce, maintenance, custody, guardianship, inheritance, nationality and civil-status instruments | Do not flatten differing legal regimes or topic-specific laws into one generic “family law”; mark disputed/uncertain applicability for counsel | P1 |
| Administrative / public law | State Council framework and procedure; administrative decisions; civil service; public procurement; public property and local administration | Identify issuing body, delegated authority, publication, commencement, review/appeal deadlines and court level | P1 |
| Tax / customs | Income Tax Law No. 91/2005; VAT Law No. 67/2016; Unified Tax Procedures Law No. 206/2020; Customs Law No. 207/2020; annual and amending finance instruments | Tax period/year; transaction/import date; annual amendments, rates, executive regulations and circulars; do not generalize a rate across periods | P1 |
| Property / real estate | Registration and real-estate publicity; tenancy regimes; mortgages; building/planning; urban communities; construction and land rules | Registration date; property type/location; special and historical tenancy regimes; national vs local instruments | P1 |
| Intellectual property | IP Protection Law No. 82/2002; implementing regulations and amendments; copyright, trademarks, patents, designs and relevant treaties | Right type; filing/priority/renewal dates; treaty status; distinguish official Arabic text from translations and commentary | P1 |

### Cross-cutting supporting areas

Add constitutional law and amendments, civil/commercial procedure, evidence, consumer protection, data protection, cybercrime, telecommunications, banking/finance, investment, insolvency, social insurance, treaties, environment, health, construction, transport, education and professional licensing. Link these to the core subjects through controlled topic tags rather than duplicating the same document.

## Source hierarchy and lawful acquisition

1. **Primary source first:** Official Gazette (الجريدة الرسمية), Egyptian Proceedings (الوقائع المصرية), Amiri Press, the Presidency, Parliament, competent ministries/regulators, and official court publications.
2. **Official specialist sources:** competent agencies for their own regulations, decisions, official forms and publications.
3. **Discovery/cross-check sources:** WIPO Lex, ILO NATLEX, FAOLEX, Library of Congress guides, and legal research services. These help locate materials; they do not replace source verification.
4. **Secondary commentary:** books, journals, headnotes, legal encyclopedias and practitioner guides, stored separately with author, edition, publisher, page and rights metadata.

For each source, record its exact URL, responsible authority, material types, terms URL, date checked, access method, permission state, evidence reference, allowed purposes, known coverage and next action. A publicly viewable page is not by itself proof of permission for automated collection, local storage, commercial indexing, model processing, or republication. Never bypass logins, subscriptions, paywalls, CAPTCHAs, or technical restrictions.

### Judgments

Prioritize official court portals and published decisions/principles. Before bulk acquisition, record the court-specific terms and obtain any required licence or written permission. In particular, the repository's existing assessment says the Court of Cassation site terms prohibit automated/bulk extraction and require prior written permission for commercial use or republication; do not scrape it while permission is absent. Do not assume another court has the same terms: assess each court separately.

Where full-text collection is not authorized, do not circumvent restrictions. Use only metadata/citations or links that the source's terms permit, and mark full text as unavailable. Preserve the distinction between a full judgment, an official principle/headnote, a database summary, and commentary. Judgment records must include court, chamber/circuit, case/appeal number, date, source, text type, disposition (if available), cited provisions, and access/reuse basis.

## Required provenance and version model

Every source/document/version must have stable identifiers and the following fields where applicable:

- **Identity:** document ID, Arabic title, optional English title, document type, instrument number/year, issuing authority, language, topic tags.
- **Publication provenance:** exact source URL, source ID, Official Gazette/Egyptian Proceedings name, issue/date/pages, archive/certified-copy reference, retrieval timestamp, original filename/format, SHA-256 of original bytes.
- **Legal timeline:** enactment date, publication date, effective date, end/repeal date, status-as-of date, transitional provisions, and evidence for each known date. Unknown dates remain null/unknown; do not infer an effective date from publication.
- **Version relations:** amends, amended by, repeals, repealed by, corrects, supersedes, implements, consolidates. Store each instrument separately and identify affected articles where established.
- **Processing:** extraction method/version, OCR state, page/paragraph/article anchors, extraction-quality findings, missing/duplicate article labels, and original-to-text comparison status.
- **Rights:** collection permission, storage, indexing, commercial use, model processing, display/excerpt and redistribution permissions, terms checked date, evidence reference and any limitations.
- **Review:** source review, text transcription review, legal-status review, lawyer approval, reviewer identity/role, review date, outcome, evidence and unresolved issues. The release gate requires every review record to name an accountable reviewer, role, and non-future review date; the lawyer-approval record must explicitly identify a qualified Egyptian lawyer/counsel. These fields improve traceability but do not independently prove identity, qualifications, or evidence authenticity.

The original file is immutable. Extracted text and normalized article chunks are derivative records linked to a specific source version. Corrections create a new processing/review event; they do not silently replace the original.

## Controlled review states

Use independent fields rather than one ambiguous “verified” flag:

- Acquisition: `candidate`, `permission_pending`, `approved_for_collection`, `collected`, `blocked`.
- Text quality: `not_extracted`, `extracted`, `ocr_required`, `text_checked`, `extraction_rejected`.
- Legal status: `unknown`, `under_review`, `not_yet_in_force`, `in_force`, `partially_repealed`, `repealed`, `historical`.
- Legal review: `unreviewed`, `source_checked`, `status_checked`, `lawyer_approved`, `rejected`.

Do not collapse these into a single score. A source can be official while a transcription is poor; a text can be accurate while its current legal status is unknown; a source can be legally accurate but not licensed for a particular product use.

## Collection and review workflow

1. Register and assess the source; record its terms and exact intended use.
2. Identify a specific document and exact URL or authorized archive/export method.
3. Resolve collection rights before retrieval. Record evidence, not just a checkbox.
4. Preserve original bytes, hash, retrieval metadata and source reference.
5. Extract Arabic text while preserving pages, headings, article numbering, tables, schedules and annexes. OCR output must be compared with the page images.
6. Detect duplicate documents and versions; run extraction completeness diagnostics.
7. Register every amendment and link affected provisions without overwriting prior versions.
8. Have a qualified Egyptian legal reviewer assess source authenticity, effective/repeal dates, current status, transitional effects and interpretation-sensitive relationships.
9. Index only records permitted for the intended use. Keep unreviewed material out of the verified/current-law retrieval path.
10. Publish a coverage report that distinguishes discovered, collected, text-checked, status-checked and lawyer-approved materials.

## Retrieval and product rules

- Support an explicit “law as of” date and filter by legal effective period and review state.
- Return the source citation, article/paragraph anchor, relevant version, publication metadata, status/review label and any uncertainty.
- If no reviewed source supports an answer, say the knowledge base does not yet contain enough verified material.
- Never present a future-effective law as currently operative.
- Never present commentary, a headnote, a translation, or an AI summary as the official Arabic statute.
- When amendments or conflicting versions cannot be resolved, surface the conflict and request legal review rather than silently choosing one.
- Do not claim that the corpus is complete based on file counts. Report coverage by subject, instrument, version, period, source and review state.

## Phase 2 acceptance criteria

Phase 2 is not complete until:

- Each of the nine requested practice areas has a documented source map and a populated inventory of identifiable legal instruments.
- Each collected instrument has provenance, original hash, rights/access basis, publication metadata and an explicit review state.
- Amendment/repeal/commencement relationships are represented as linked records; unknown values remain unknown.
- A documented lawful path exists for each judgment source used; no restricted court content has been bulk-collected without permission.
- Arabic extraction quality is recorded, with scanned/low-confidence text queued for human review.
- Legal retrieval can distinguish current, historical, future-effective and status-unknown versions.
- A coverage report shows real counts by source, subject and review state, without labeling unreviewed candidates as verified law.
- An Egyptian lawyer has reviewed the initial production corpus and the temporal rules for high-risk subject areas.

## First implementation order

1. Complete the source/permission review and pin the first official documents for the P0 statutes, including all identifiable amendment instruments.
2. Build the provenance and version records before increasing chunk volume.
3. Collect and review the initial civil, criminal, criminal-procedure and labour sets; keep all uncertain status fields explicit.
4. Add commercial, family, administrative, tax, property and IP inventories in parallel, with each topic's specialist review requirements.
5. Seek authorized judgment exports/API access separately for each court; meanwhile, do not automate restricted sources.
6. Only after the collection is real, report coverage gaps and select the next acquisition batch. Final product testing remains a later project phase.
