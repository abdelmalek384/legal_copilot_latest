# Coordinator research-agent evidence intake — 24 November 2026

## Scope and provenance

This intake summarizes the supplied `files.zip` package. It is an acquisition lead and provenance record, **not a legal corpus import**.

The package contained:
- Research Agent 5: 40 instrument records — tax, customs and public finance.
- Research Agent 6: 29 records — personal status and family law (27 candidate additions, 2 enrichments).
- Research Agent 7: 23 records — constitutional and administrative law (18 candidate additions, 5 enrichments).
- Research Agent 8: 52 records — specialised fields (50 candidate additions, 2 enrichments).
- Total: **144 agent rows** across the four usable registers.
- A union register with 807 keyed instrument candidates and 94 unkeyed records, measured against repository commit `558c43a`.
- Collection metrics and a dashboard snapshot, also measured against `558c43a`.

The supplied agent dossiers explicitly report **zero lawyer-reviewed records** and no official-text verification by those agents. The source links are a mixture of secondary reproductions, snippets, official listing pages and a small number of official-portal locators. A URL, Gazette citation, snippet or agent statement is not evidence that the instrument's complete text was acquired or source-matched.

The 807-key union and its dashboard are historical snapshots of commit `558c43a`, not current-main totals. They predate the subsequent addition of EG-0542 / FT-0217 (Decision 111/2023) and other later repository changes. Do not copy the snapshot's headline counts into current status reporting without rerunning the measurement against the current branch. The supplied snapshot itself reports:
- 3 / 807 instruments (0.4%) as structurally validated full text, based on the then-current index and not recomputed by the tool.
- 96 / 807 with locally captured text but not validated; another 18 claimed with caveats.
- 0 lawyer-reviewed instruments.
- Rights status unknown for 186 / 199 sources; 9 blocked absent a licence/exception; 4 narrowly limited site-text permissions that do not extend to Gazette scans or third-party material.
- 83 delta keys classified as new candidates after heuristic deduplication, plus 110 candidate keys inferred from previously unindexed evidence filenames/titles. Both are leads requiring manual identity resolution, not 193 confirmed new laws.

## Agent 5 — tax, customs and public finance

**40 rows; 0 lawyer-reviewed; 0 rights-cleared.** The dossier says no Gazette, ETA or ECA PDF was downloaded/read by this agent. Most entries are secondary summaries, WIPO Lex annotations or official listing metadata.

Priority acquisition leads:
1. **Law 6/2022 — Unified Public Finance Law**, plus **Law 18/2024** amending it and Finance Minister Decision **73/2024** (claimed executive regulation). The dossier records a citation conflict: another source calls the regulation Decision 13/2024. Resolve the decision number and obtain Gazette/Al-Waqa'i copies before linking it as the operative regulation.
2. **Decision amending Article 80 item 18** of that regulation: source reports an EGP 6,000 annual limit, but the decision number and Gazette reference are missing. Do not cite the limit as verified law.
3. **Income Tax Executive Regulation, Finance Minister Decision 991/2005**, with WIPO Lex consolidation only through Decision 296/2020. The dossier lists amendment leads 172/2015, 195/2017, 643/2019, 217/2020 and 296/2020; post-2020 currentness remains open.
4. Continue the VAT, customs and unified tax-procedure amendment leads only after checking overlap with existing EG records; the dossier explicitly lists several already-held laws/decisions.

## Agent 6 — personal status and family law

**29 rows; 0 lawyer-reviewed; 0 rights-cleared.** The dossier says no Gazette PDF, ministry PDF or judgment was downloaded/read. Most sources are secondary reproductions, press reports or snippets. It also separates drafts from enacted laws; preserve that distinction.

Priority acquisition leads:
1. **Law 25/1929** and its amendment chain: Decree-Law 44/1979, Law 100/1985, the reported 1985 corrigendum, Law 4/2005 and Law 140/2017. The corrigendum's affected articles are not identified in the dossier; do not silently build a consolidated version without it.
2. **Law 1/2000** (personal-status litigation procedure) and **Law 10/2004** (family courts), plus the Law 91/2000 and Law 215/2017 amendment leads. Obtain full Gazette text and identify article-level changes.
3. **Law 77/1943** (inheritance) and Law 219/2017; **Law 71/1946** (wills).
4. **Law 462/1955** and Law 626/1955 for jurisdiction/procedure context. The dossier cautions that applicability differs by religion/denomination and that several boundaries are not established by its sources.
5. The two family-law bills are explicitly **drafts**, not enacted law; they must never be ingested as operative law.

The dossier reports secondary annotations of Supreme Constitutional Court rulings affecting Law 25/1929 Arts 18 bis (3) and 20, but the case numbers/dates are not captured. Treat these as case-retrieval leads only, not holdings ready for citation.

## Agent 7 — constitutional and administrative law

**23 rows; 0 lawyer-reviewed; 0 official-text verified.** The dossier identifies several useful official locators, but states that no Gazette, Presidency, Ministry of Justice or State Council PDF was downloaded/read.

Priority acquisition leads:
1. **Law 48/1979 — Supreme Constitutional Court Law**: official Court of Cassation legislation portal locator: https://www.cc.gov.eg/legislation_single?id=404930. The dossier reports Gazette 36 (6 Sep 1979), a 14-day commencement rule and amendment by Decree-Law 168/1998; all operative wording and currentness need source collation.
2. **Law 43/1979 — Local Administration Law** and **PM Decree 707/1979** (executive regulation), with Law 50/1981 and other amendment leads. The 2017 local-administration bill is a draft only; it does not establish repeal or replacement.
3. **Law 40/1977 — Political Parties Law** and Law 144/1980. Publication-date sources conflict (2 vs 7 July 1977).
4. **Civil Service Law 81/2016** and PM Decree 1216/2017, with subsequent decision/amendment leads. The dossier says the 1978 regulation was repealed by the 2017 regulation; verify against official texts.
5. Law 144/2017 is a candidate amendment lead, but the dossier itself flags a possible relationship to Law 168/2025 (Private State Property Law). Do not infer repeal without the enacted texts.

## Agent 8 — specialised fields

**52 rows; 0 lawyer-reviewed; 0 rights-cleared.** The dossier says no Gazette, ministry or authority PDF was downloaded/read. It distinguishes official listing pages from secondary copies and warns that reuse terms were not checked. It also explicitly says no new environmental work was done because that domain is already substantially represented in the repository.

Priority acquisition leads:
1. **Law 13/2025 — Medical Liability and Patient Safety**, plus three Prime Minister decisions reportedly published 28 Oct 2025. The three decision numbers/titles are missing; identify them from the Gazette before adding individual instrument records. The source for the law is secondary.
2. **Law 151/2019** and PM Decision **777/2020** (executive regulation): the Egyptian Drug Authority site is an official listing locator, but the dossier did not download the underlying PDFs. Capture the actual texts and amendment chain.
3. **Law 10/2003 — Telecommunications Regulation** and Law 172/2022. The Arabic copy located by the agent is secondary; the existing repository's AMT-005 is English-only, so this is a potentially useful Arabic-text acquisition lead.
4. **Law 87/2015 — Electricity** and Minister of Electricity Decision 230/2016; the agent has a metadata snippet and a secondary regulation copy, not a Gazette collation.
5. **Education Law 139/1981** and Law 169/2025; the Ministry of Education listing is a locator, while the amendment copy is secondary.
6. **Universities Law 49/1972** and amendment leads 100/1992, 82/2000, 116/2008, 52/2014, 152/2019 and 179/2020. The dossier points to UNESCO HEPO and Ministry of Education copies, but rights and source identity must be checked.

## Excluded material and safety rules

- The package also contains an early Agent 2 criminal-law dossier explicitly marked **SUPERSEDED**. Its Law 174/2025 Article 2 extract is described as contradicted by a later repository note referencing the official MOJ PDF. This superseded dossier and its source JSONL are deliberately excluded from the usable intake.
- Do not turn any of the 144 rows into full-text inventory entries merely because a URL or Gazette issue is present.
- Do not ingest summaries, snippets, draft bills or secondary case annotations as statutory article text.
- Do not change `lawyer_reviewed`, `rights_cleared`, `verified`, currentness or production-eligibility flags based on this package.
- Do not treat official-site listing metadata as proof that a source PDF was retrieved, read, or permitted for reuse.
- Preserve issuer identity when deduplicating. The metrics snapshot identified a same-number/year collision for Decision 300/2025 (Finance Ministry vs Labour Ministry); never merge solely on number/year.
- Duplicate-key groups in the snapshot are candidates only. No aliases should be created automatically.

## Recommended acquisition order

1. Obtain official Gazette/agency PDFs for the pilot-relevant labour and personal-status instruments first; then the missing primary texts in the above leads.
2. Resolve amendment chains and corrigenda before producing any consolidated current text.
3. Capture text with page/article locators and source hashes; keep original source and transcription separately.
4. Assess rights per source and per document type before redistributing text.
5. Have a qualified Egyptian lawyer explicitly approve the relevant instrument/article before any lawyer-reviewed label is set.

**Evidence status of this intake:** agent-reported leads preserved; no new legal text source-matched; no currentness review; no lawyer review; no rights clearance.
