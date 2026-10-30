# First Egyptian legal document batch — collection plan

**Status:** planning only. No entries here are approved for automated retrieval. Populate the executable manifest only after recording evidence of permission for the exact intended use.

## Batch A — constitutional and foundational law

| Order | Material | Preferred source | Required checks before ingestion |
|---|---|---|---|
| A1 | Constitution text and 2019 amendment instrument | Presidency publication plus corresponding Official Gazette material | Confirm exact version, text, later amendments, publication metadata, and collection/reuse permission |
| A2 | Civil Code, Law No. 131 of 1948 | Official Gazette / Amiri Press | Obtain original law and each amending instrument; confirm any official consolidated version and its provenance |
| A3 | Penal Code, Law No. 58 of 1937 | Official Gazette / Amiri Press | Original law, amendment chain, and any repeals/transitional provisions |
| A4 | Code of Civil and Commercial Procedure, Law No. 13 of 1968 | Official Gazette / Amiri Press | Original and amendments; preserve article renumbering and repeal notes |
| A5 | Criminal procedure transition package: Law No. 150 of 1950; Law No. 174 of 2025 promulgating a replacement Code; Law No. 160 of 2026 amending Law No. 174/2025 | Official Gazette / Ministry of Justice Gazette PDF for Law 174; Amiri Press official text for Law 160; official Parliament announcement for the amendment's stated purpose | Store each instrument separately. Do not assign Law 174/2025 an effective date yet: Law 160/2026's published Article 6 substitution ("first October following publication") must be reconciled with the official Parliament's description of a 2027 postponement and the Gazette publication references. Have qualified Egyptian counsel resolve the wording and transitional effect against both Gazette texts. Keep Law 174/2025 unverified and do not treat it as the operative code until that review is recorded. |
| A6 | Labour Law, Law No. 14 of 2025 | Amiri Press / Official Gazette | Original publication, commencement clause, executive regulations, transitional provisions and subsequent amendments |
| A7 | Social Insurance and Pensions Law, Law No. 148 of 2019 | Official Gazette / relevant authority | Original, executive regulations, amendments and implementation decisions |
| A8 | Companies Law, Law No. 159 of 1981 | Official Gazette / GAFI for supporting materials | Separate binding legislation from non-binding guidance; collect amendments |
| A9 | Consumer Protection Law, Law No. 181 of 2018 | Official Gazette / Consumer Protection Agency | Original, executive regulations and amendments |
| A10 | Personal Data Protection Law, Law No. 151 of 2020 | Official Gazette / competent authority | Verify implementing decisions and commencement/applicability; don't infer status from the law number alone |

## Batch B — add after foundational coverage

- Commercial Code No. 17 of 1999 and amendments.
- Income Tax Law No. 91 of 2005 and annual/amending instruments.
- VAT Law No. 67 of 2016 and executive regulations.
- Intellectual Property Protection Law No. 82 of 2002.
- Central Bank and Banking System Law No. 194 of 2020.
- Cybercrime Law No. 175 of 2018.
- Relevant personal-status statutes and procedures, carefully scoped by applicable legal regime.
- State Council and administrative-law materials.
- Environmental, construction, health, education, telecoms and transport legislation.

## Per-document ingestion checklist

- [ ] Exact direct URL and redirect host checked.
- [ ] Terms/licence covers local storage, extraction, indexing, commercial use and display as applicable.
- [ ] Permission evidence reference and review date recorded.
- [ ] Original bytes stored unchanged and SHA-256 calculated.
- [ ] Authority, official Arabic title, law number/year, publication date, Gazette issue/page recorded.
- [ ] Effective date, repeal date, transitional clauses and status evidence recorded or left unknown.
- [ ] Each amendment stored as its own source record and linked to affected law/provisions.
- [ ] Extraction output compared against source pages; scanned pages routed to OCR/manual review.
- [ ] Article numbers, duplicate labels, omitted pages and OCR anomalies checked.
- [ ] Reviewer identity/date and review outcome recorded.
- [ ] Only lawyer-reviewed records enter the production legal-search corpus with the appropriate verification state.

## Release rule

Do not call a document “current law” merely because it was downloaded from an official website. Do not call a database “complete” based on the number of downloaded files. Report coverage by document, source, date range, version status, and review status.
