# Agent 7 — Administrative, local government, public finance and election acquisition delta
**Research date:** 23 November 2026  
**Repository:** `abdelmalek384/legal_copilot_latest`  
**Status:** discovery and text-retrieval pass; not a legal-corpus release.

## Repository deduplication and gate
The existing repository already has dedicated checkpoints for State Council/SCC, civil service, procurement, unified public finance, PPP, and elections (including `collection_checkpoint_3`, `40`, `55`, `67`, and `68`). This pass therefore adds only new source/version leads and amendment detail, rather than rewriting those checkpoints.

The repository's source-reuse gate is controlling. Official-hosted PDFs and secondary full-text transcriptions were opened and text-extracted for research, but the source permission register records collection and commercial reuse as **unknown** for the relevant portals. Accordingly, no complete third-party or official-hosted text has been copied into the legal corpus in this commit. The candidate register and permission register now record the new instruments and unresolved rights gates. These are not corpus-ready records and are not lawyer-reviewed.

## A. Local administration — Law 43/1979 and Decision 707/1979

### 1. Law 43/1979
- Official Ministry of Finance locator: https://mof.gov.eg/ar/legislation/legislation-5fe86ab47bfc600007cc005c
- Original Gazette scan locator (Manshurat): https://manshurat.org/node/13261 — metadata states Official Gazette issue 25 (تابع), issued 20 June 1979, published and effective 21 June 1979; 24-page PDF.
- Full current-consolidated Arabic transcription (LAW HUB): https://lawhub.info/eg/?p=11568 — 1,442 extracted lines, with article-level amendment and SCC judgment annotations.
- Related amendment register (Manshurat): https://manshurat.org/node/13261/relations
- Ministry of Finance locators additionally identify Law 50/1981, Law 106/1987, Law 84/1996, Law 96/2003 and Law 178/2005 as related instruments; the Manshurat relation list also identifies Laws 168/1981, 26/1982, 145/1988, 9/1989 and 115/2011, plus Law 225/1996.
- Exact Arabic excerpt, current transcription, Art.1: «وحدات الإدارة المحلية هى المحافظة والمراكز والمدن والأحياء والقرى».
- Exact Arabic excerpt, Art.2: local units «إنشاء وإدارة جميع المرافق العامة الواقعة فى دائرتها».
- Important amendment/validity annotations found in the consolidated transcription:
  - Art.1 and Art.2 replaced by Law 50/1981 (Official Gazette issue 26, 25 June 1981).
  - Art.3's first paragraph later replaced by Law 84/1996; the transcription also annotates SCC judgment in Case 2/16 Constitutional, 3 February 1996, concerning the local-council election method.
  - Art.4's local-fee provisions are annotated with SCC judgment in Case 36/18 Constitutional, 3 January 1988, invalidating Minister of Local Administration Decision 239/1971 and causing the fall of the related Art.4 provisions and PM Decision 870/1990.
  - The 2003 and 2005 amendments are linked by the Ministry portal but their Gazette PDFs and exact article-level effects still need acquisition.
- The Law HUB transcription is useful as a full Arabic recovery source, not an authenticated Gazette consolidation. Its annotations need cross-checking against each amending Gazette and SCC judgment.

### 2. PM Decision 707/1979 — Executive Regulation
- Official Ministry of Finance locator: https://mof.gov.eg/ar/legislation/legislation-5fe86ab67bfc600007cc0063 — portal labels the decision «سارٍ».
- Gazette metadata: issue 29 مكرر, 25 July 1979. The issuing Art.2 says it takes effect on publication.
- Manshurat scan/text locator: https://manshurat.org/node/13282 — 20-page PDF; the downloadable transcription returned 793 extracted lines.
- Laweg issuing-clause page: https://www.laweg.net/framePlain.aspx?NID=50671&action=viewactivepages&itemid=39803&type=6 — exact issuing Arts.1–2 are visible.
- Exact Arabic issuing excerpt: «يعمل باللائحة التنفيذية لقانون نظام الحكم المحلي المرافقة».
- Annex text recovered includes allocation of local responsibilities across education, health, housing/urban planning, municipal utilities, roads, agriculture, irrigation, labour, culture, transport and local public assets. Examples in the transcription include local responsibilities for water and sewage, public cleanliness, roads and state property.
- **Text-quality warning:** the OCR/transcription has inconsistent article numbering, Gazette page/date labels and apparent typographical errors. The 20-page scan must be visually inspected page-by-page and the complete amendment chain located before relying on any article as current law. Do not treat this as a clean current consolidation.

## B. Political rights / election administration

### 3. Law 45/2014 — Political Rights
- Official NEA digital library: https://www.elections.eg/digital-library-laws
- Official NEA Arabic PDF: https://www.elections.eg/images/pdfs/laws/PoliRights-2014-45.pdf.pdf — 23 pages; 749 extracted lines.
- Gazette issue 23 (تابع), 5 June 2014. Issuing Art.3 provides commencement on the day after publication.
- Exact Arabic Art.1 excerpt: «على كل مصري ومصرية بلغ ثماني عشرة سنة ميلادية أن يباشر بنفسه الحقوق السياسية الآتية».
- Issuing Art.2 assigns the NEA the task of issuing the executive regulation and preserves earlier regulations/decisions under Law 73/1956 until the new regulation is issued, insofar as they do not conflict.
- The official NEA PDF carries annotations for Decree-Law 92/2015, Law 198/2017 and Law 140/2020. It records, among other things, that Law 198/2017 repealed Chapter II of Law 45/2014. This is an official-hosted annotated text, not a substitute for obtaining every amending Gazette instrument.

### 4. Decree-Law 92/2015
- Official NEA PDF: https://www.elections.eg/images/pdfs/laws/HouseOfRepresentativesAmendments2015-92.pdf — 4 pages, but text extraction is garbled; visual transcription is needed.
- Official NEA index lists it as amending Laws 45/2014 and 46/2014.
- Secondary metadata/text recovery: https://temp.manshurat.org/node/4310 and https://www.elwatannews.com/news/details/779076.
- The consolidated NEA Law 45 text annotates changes to Art.2, Art.12, Art.25 and Art.33. Exact Gazette page-by-page comparison remains open.

### 5. Law 198/2017 — National Election Authority
- Official NEA PDF: https://www.elections.eg/images/pdfs/laws/NEAlaw-2017-198.pdf.pdf — 15 pages; OCR extraction only 82 lines, although the official indexed result exposes the article structure.
- Gazette issue 30 مكرر (ب), 1 August 2017; Art.37 provides commencement on the day after publication.
- Exact Arabic Art.2 excerpt: «الهيئة الوطنية للانتخابات هيئة مستقلة، لها شخصية اعتبارية».
- Art.36 repeals Chapter II of Law 45/2014 and conflicting provisions.
- Full article-level OCR and visual inspection remain required.

### 6. Law 140/2020
- Official NEA PDF: https://www.elections.eg/images/pdfs/laws/PoliRightsAmendments2020-140.pdf — 9 pages; 363 extracted lines.
- Gazette issue 26 مكرر (ك), 1 July 2020; commencement metadata indicates 2 July 2020.
- It amends Law 45/2014, Law 46/2014 and Law 198/2017. Article-by-article consolidation map still required.

## C. Public finance — Law 6/2022 amendment and current executive regulation

### 7. Law 18/2024 — amendment to Law 6/2022
- Official Gazette PDF hosted by ETA: https://www.eta.gov.eg/sites/default/files/2024-09/law_no.18-2024.pdf — 79 extracted lines.
- Gazette issue 13 مكرر (أ), 30 March 2024; Art.5 provides commencement the day after publication.
- It amends the transition to full program/performance budgeting (within no more than six years), definitions, and provisions including Arts.23, 30, 35 and 74; adds definitions and Arts.25 مكرراً and 31 مكرراً; and phases inclusion of economic public authorities in the general-government budget over no more than five fiscal years.
- Exact Arabic transition excerpt: «خلال ست سنوات على الأكثر».
- **OCR correction:** the text extractor misread the article number in the amended provision. The Gazette page image was checked; the heading is Art.30 (not Art.20). Keep the visual page as the controlling transcription aid.

### 8. Minister of Finance Decision 73/2024 — Executive Regulation of Law 6/2022
- Official Ministry of Finance PDF: https://media.mof.gov.eg/mof-prd/qrar_wzyr_almalyt_73_lsnt2024_7207e41665.pdf — 126 pages; 1,988 extracted lines.
- Gazette issue 45 (تابع), 24 February 2024; issuing Art.4 makes it effective the day after publication.
- Issuing Art.2 applies to central-government administrative units, local administration units, service public authorities, independent entities and oversight bodies, special units/funds/accounts, and economic public authorities, subject to stated exclusions.
- Issuing Art.3 repeals the executive regulations to Law 53/1973 (public budget) and Law 127/1981 (government accounting).
- This is a substantial newly recovered official-hosted text, not merely a locator. Full 126-page text is not copied into the repository because source reuse permission is still unknown.

### 9. Minister of Finance Decision 94/2025 — amendment to Decision 73/2024
- Official Ministry of Finance PDF: https://media.mof.gov.eg/mof-prd/qrar_wzyr_almalyt_rqm_94_lsnt_2025_btedyl_bed_ahkam_allayht_altnfydhyt_lqanwn_almalyt_aleamt_almwhd_alsadrt_bqrar_wzyr_almalyt_rqm_73_lsnt_2024_7202f97b5d.pdf — one page; 31 extracted lines.
- Gazette issue 69 (تابع), 24 March 2025; Art.2 makes it effective the day after publication.
- Art.1 replaces item 18 of Art.80 of Decision 73/2024. The annual amount for the specified deduction/settlement based on an authorized declaration increases from EGP 3,000 to EGP 6,000.
- Exact Arabic excerpt: «بحد أقصى ستة آلاف جنيه فى السنة المالية الواحدة».
- The official PDF directly identifies Decision 73/2024 as the amended regulation; some secondary reporting contains an inconsistent recital reference. Prefer the official Gazette PDF.

## D. Related procurement amendment — incremental lead only
The existing procurement checkpoint already covers Law 182/2018 and Decision 692/2019. This pass recovered:
- Official Ministry of Finance locator for Law 188/2020: https://mof-web-prd.apps.fslabs.net/ar/legislation/legislation-5fe868ae7bfc600007cbec2b
- Official-hosted PDF locator: https://mof-assets.apps.fslabs.net/mof-prd/2123_64f01cffad.pdf (3 pages; image-only/no usable text extraction).
- Secondary full-text transcription: https://www.aldhshan.com/2026/02/188-2020-182-2018.html
- The secondary text identifies Law 188/2020 as replacing Art.92 of Law 182/2018 concerning assignment of the contract or sums due under it. The official PDF must be visually transcribed and checked against Gazette issue 36 مكرر (ب), 5 September 2020 before treating the amendment as verified.
- Decisions 28/2020 and 614/2020 remain amendment leads to Decision 692/2019; their full Gazette texts were not acquired in this pass.

## E. Repository changes in this commit
1. Added candidate metadata for Law 43/1979, Decision 707/1979, Law 45/2014, Decree-Law 92/2015, Law 198/2017, Law 140/2020, Law 18/2024, Decision 73/2024 and Decision 94/2025.
2. Added/normalized source permission records for the Ministry of Finance legislation portal, ETA-hosted Gazette PDF, Manshurat and LAW HUB. All relevant collection and commercial-reuse fields remain **unknown**.
3. No full legal text was ingested into the production corpus; no lawyer review is claimed.

## F. Next acquisition targets (no checkpoint repetition)
1. Visually transcribe Decision 707/1979 annex and identify all amending PM decisions; compare against the Law 43/1979 full text.
2. Obtain Gazette texts for local-government amendments 168/1981, 26/1982, 106/1987, 145/1988, 9/1989, 84/1996, 96/2003, 178/2005, 115/2011 and Law 225/1996; map SCC rulings affecting local councils and fees.
3. Extract Law 92/2015 and Law 198/2017 from official PDF page images; map Law 140/2020 into Law 45/2014 and Law 198/2017.
4. Complete article-level review of Decision 73/2024 (126 pages), overlay Decision 94/2025 and search for any later amendments.
5. Return to the existing procurement checkpoint for Gazette-image transcription of Law 188/2020 and full text of Decisions 28/2020 and 614/2020.
6. Only after source permission is resolved, move the candidate records into the authorized acquisition workflow and local corpus.

## Progress accounting
- **New discovery records added:** 9.
- **Full/near-full Arabic texts opened in this pass:** Law 43/1979 consolidated transcription; Decision 707/1979 annex transcription/scan; Law 45/2014 official NEA PDF; Law 198/2017 official NEA PDF (sparse OCR); Law 140/2020 official NEA PDF; Law 18/2024 official Gazette PDF; Decision 73/2024 official Gazette PDF; Decision 94/2025 official Gazette PDF. Law 92/2015 official PDF is located but OCR is not usable.
- **New full texts ingested into authorized repository corpus:** 0, because collection/reuse permission remains unknown.
- **Whole-repository confirmed text-source coverage:** no percentage recalculated by this candidate-only commit. The repository's last audited baseline is in the 18 November 2026 inventory/checkpoint; this pass does not change the corpus numerator. Do not count candidate discovery as text-source coverage.
- **Agent 7 research coverage:** do not reuse the earlier rough 46% estimate as a repository percentage. A new denominator and article-level rubric are required to calculate a defensible subdomain percentage after source permissions and the amendment matrix are reconciled.


## G. Newly recovered amendment chain for Decision 707/1979 and Law 43/1979
The relation page for the Executive Regulation (Manshurat) identifies **eight amending PM decisions**: 314/1982, 1139/1984, 1251/1988, 488/1989, 1105/1990, 1543/1993, 2718/1996 and 220/2000. This is a new amendment-chain result; it materially expands the local-government tranche beyond the base regulation.
- Relation register: https://manshurat.org/node/13282/relations
- 314/1982: 12-page scan; issued 7 April 1982, published 15 April 1982. A Supreme Administrative Court judgment quotes amended Arts.3 and 10, including the local-unit public-facilities remit and local agricultural affairs. Searchable quotation: https://lawhub.info/eg-j/?p=4828.
- 1139/1984: 1-page scan; issued 3 November 1984, published 15 November 1984. Exact article effect remains to be transcribed.
- 1251/1988: 5-page scan; issued 24 November 1988, published/effective 1 December 1988. Secondary consolidated text attributes amendments to Arts.48 bis, 56, 78 and 91 bis; Gazette transcription remains open.
- 488/1989: full Arabic text recovered from the indexed Gazette PDF, Gazette issue 21, 25 May 1989. Art.1 replaces Art.25 with provisions on governorate cooperation with the Ministry of Awqaf in studying endowment investment plans, religious الدعوة, charity, mosque maintenance and protection of Awqaf assets. The source recital refers to Decision 707/1978 even though the base regulation is Decision 707/1979; preserve and flag this apparent source error.
- 1105/1990: 1-page scan; issued 22 August 1990, published/effective 30 August 1990. Secondary consolidated text identifies Art.94 bis, for a city of special importance with an independent organizational structure.
- 1543/1993: full Arabic text recovered from MKS Egypt; Gazette publication 23 September 1993. Replaces paragraphs 1–3 of Art.35 with sitting allowances for local popular and executive council members. The specified historical EGP amounts are not evidence of current allowance levels.
- 2718/1996: full Arabic text recovered from MKS Egypt; Gazette issue 40, 10 October 1996. Replaces Art.29 governing local popular council composition and filling vacant seats, including the then-applicable workers/farmers representation rule.
- 220/2000: one-page Gazette scan visually inspected; issue 26 تابع (أ), 2 February 2000; effective 3 February 2000. Art.1 adds to Art.18 the governor's authority over governorate-owned parking facilities and operation of passenger vehicles within governorate boundaries. Screenshot/source locator: https://manshurat.org/file/24924/download?token=ygQ39PZf.
- Source-quality boundary: amendment scans are hosted by Manshurat, not authenticated here as official Amiri Press originals. Full text is available for 488/1989, 1543/1993 and 2718/1996; 220/2000 was visually inspected; remaining scans still need OCR and article-level transcription. No amendment should be treated as a fully reconciled current text until all eight and later amendments are checked.

### Law 43/1979 statute amendment leads confirmed on Ministry portal
The official Ministry of Finance legislation portal now supplies individual locators and linked PDFs for:
- Law 50/1981 — 27-page official-hosted scan; Law HUB annotates replacements of Arts.1, 2, 144 and 145.
- Law 106/1987 — one-page official-hosted scan.
- Law 84/1996 — five-page official-hosted scan; Art.97 is replaced, including the local-council vacancy/complimentary-election rule.
- Law 96/2003 — one-page official-hosted scan; adds two paragraphs to Art.10.
- Law 178/2005 — one-page official-hosted scan; repeals paragraph 2 of Art.89.
Additional amendments found in the consolidated transcription include Law 145/1988 (Art.145/Art.144 effects) and Law 9/1989 (adds Art.4 bis, with transcription metadata stating effective 17 February 1989 and Gazette issue 11 on 16 March 1989). The Law 43 relation register also points to Laws 168/1981, 26/1982 and 115/2011; original text/precise effects still need recovery.
- Official Ministry portal caveat: the Ministry expressly says its online texts are for guidance and the Official Gazette is the controlling legal reference. The official-hosted PDFs are not automatically original Gazette scans; page and issue authentication remains required.


## H. Actual SCC and Supreme Administrative Court decisions recovered
### SCC Case 2/16 (3 February 1996) — local-council electoral system
- **Official SCC full judgment:** https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/895_16_2_1_2.html (136 extracted lines).
- **MKS Egypt full transcription:** https://mksegypt.org/public/ar/judgments-of-the-supreme-constitutional-court/15497 (197 lines; page displays CC BY 4.0 attribution).
- The Court held unconstitutional Arts.3, 10, 39, 47, 59, 66 and 75 مكرراً of Law 43/1979, but only insofar as they prescribed a single individual seat and selection of the remaining local-council members by party lists. The reasoning addresses equality, freedom of expression, political participation, voter/nominee equality and the disproportionate advantage given to party members.
- The judgment also states that although the councils' composition is invalid from election, acts and decisions made before publication of the judgment in the Official Gazette remain valid unless separately annulled/amended by the competent authority or struck down on another ground.
- Exact Arabic operative excerpt: «حكمت المحكمة بعدم دستورية المواد (3، 10، 39، 47، 59، 66، 75 مكرراً)» — the qualification following this excerpt limits the ruling to the combined party-list/individual-seat system.

### SCC Case 36/18 (3 January 1998) — unpublished local fees
- **Full Arabic judgment:** https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/15543 (129 lines; page displays CC BY 4.0 attribution).
- **Corrected date:** the judgment was delivered **3 January 1998**, not 3 January 1988. An earlier Agent 7 checkpoint's 1988 date was a transcription error.
- Gazette publication is recorded as 15 January 1998; the next day, 16 January 1998, is the effective non-application/refund date stated in PM Decision 736/1998.
- The SCC invalidated Minister of Local Administration Decision 239/1971 on unified local fees and held that inseverable provisions of Art.4 of the issuing law to Law 43/1979 and PM Decision 870/1990 fell with it. Central reasoning: publication is a condition of a normative rule's enforceability against third parties; a rule not published cannot bind them.
- Exact Arabic operative excerpt: «بعدم دستورية قرار وزير الإدارة المحلية رقم 239 لسنة 1971 بشأن الرسوم الموحدة للمجالس المحلية».

### PM Decision 736/1998 — direct implementation of SCC Case 36/18
- Full text: https://www.laweg.net/framePlain.aspx?NID=52053&action=viewactivepages&itemid=40599&type=6.
- Gazette Egyptian Facts issue 53 تابع (أ), 7 March 1998.
- Art.1 prohibits local units from collecting any fee on the basis of Art.4 of Law 43/1979 issuing provisions or Decision 239/1971, and requires repayment of prior collections from 16 January 1998. Art.2 directs the competent authorities to implement.
- Exact Arabic excerpt: «يحظر على وحدات الإدارة المحلية تحصيل أية رسوم بأى وجه من الوجوه».

### Supreme Administrative Court — three full-text decisions
1. **Appeal 2566/34, 23 December 1990** — full text: https://www.mksegypt.org/ar/judgments-of-the-supreme-administrative-court/3354 (131 lines; CC BY 4.0 page notice). Interprets Decision 707/1979 Arts.94 and 96 as amended by Decision 314/1982. The special ministry-budget treatment of directorate heads/deputies means the competent ministry, not an individual governorate directorate, is the relevant seniority/promotion unit for those posts. The Court rejected the administration's appeal.
2. **Appeals 8175 and 9771/49, 3 April 2004** — full text: https://lib.legal-reform.org/legal-observatory-view/المحكمة-الإدارية-العليا---مجموعة-رقم-3---رقم-المبدأ-69---رقم-الصفحة-555---القضية-رقم-8175---لسنة-49-ق---تاريخ-الجلسة-3-/-4-/-2004 (77 lines). Applies Law 43/1979 Arts.3, 76 and 97 (Art.97 as replaced by Law 84/1996) and Decision 707/1979 Art.29 (replaced by Decision 2718/1996). It fixes the date for worker status at the nomination filing date and applies same-category vote succession for a vacant seat before a supplementary election.
3. **Appeal 1282/45, 28 August 2001** — full text: https://lawhub.info/eg-j/?p=4828 (judgment text at lines 220–261). Applies Civil Code Art.970, Law 43/1979 Art.26 and Decision 707/1979 Arts.3 and 10 as amended by Decision 314/1982. Holds that the governor may protect state public/private property and remove encroachments administratively; the delegated local-unit head was competent to remove an encroachment on Agricultural Reform Authority land. Appeal allowed; first-instance annulment reversed and claim dismissed.

### Further SCC-related administrative appeals
- Supreme Administrative Court Appeal 4479/46, 8 November 2003: https://lawhub.info/eg-j/?p=50749 — applies Case 36/18 to local fee decisions and explains the effect of the invalidated fee basis.
- General Assembly of the State Council opinion 519/2002, 9 June 2002 is quoted in the official Tax Authority Circular 9/2002: https://www.rta.gov.eg/sites/default/files/periodical-books/9_16.pdf. It confirms that occupant fees cannot be collected after the SCC invalidated Decision 239/1971 and Art.4 of Law 43/1979.
- PM Decision 736/1998 is the implementing measure prohibiting those collections and requiring refunds from 16 January 1998.

### Source and legal-status notes
- SCC Case 2/16 has an official SCC-hosted HTML judgment. SCC Case 36/18 is fully transcribed on MKS Egypt; an official SCC-hosted copy was not found in this pass. MKS Egypt pages display CC BY 4.0; the repository source register now records the license as applying to site text as displayed only, not embedded third-party scans.
- Legal Reform and LAW HUB judgments are secondary full-text reproductions; MKS Egypt texts are licensed transcriptions, not Gazette originals. None of these entries is marked lawyer-reviewed.
- These judgments affect the operative status of Law 43/1979 and its fee provisions. The consolidated statute must carry judgment-driven invalidity annotations, not only statutory amendment notes.


## I. Two further official SCC judgments on local executive powers and local taxation
### SCC Case 21/11 (6 April 1991) — governor's regulatory and penal authority
- Official SCC full text: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/416_11_21_1_2.html (54 extracted lines).
- The case concerned Suez Governor Decision 108/1987, which regulated fresh-fish transport and imposed criminal penalties and confiscation.
- The SCC invalidated Art.9(b) of the governor's decision. It expressly construed Art.27(1) of Law 43/1979: the governor's powers are executive/administrative powers over local facilities and do not extend to making executive regulations or issuing regulatory decisions that define crimes or penalties where the statute assigns that competence to a minister. Such delegated criminalization is a legislative-type competence and must be exercised by the authority designated by law.
- Exact Arabic excerpt: «ودون أن يتعدى ذلك إلى الاختصاص بإصدار اللوائح التنفيذية».
- This is a controlling constitutional boundary for the interpretation of Law 43/1979 Art.27 and governorate decision-making.

### SCC Case 221/26 (5 October 2024) — local taxes must be created by law
- Official SCC full text: https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/15188_26_221_1_2.html (76 extracted lines).
- **Calendar-date clarification:** the case number is 221/26 (judicial year 26), but the judgment was delivered on **5 October 2024**; it is not a 2026 judgment.
- The Court invalidated Fayoum Governor Decision 328/2002 insofar as it imposed an annual charge on warehouses for iron, wood, building materials and sanitary ware. Since no specific service was provided in return, the charge was a local tax, regardless of the label used by the governorate.
- The judgment interprets Constitution Arts.38, 101 and 178: the law must state the essential elements of a local tax; the local council's Art.43/1979 Art.12(6) competence is only to propose local taxes, not impose them by governor's decree. The tax's base, amount, liable persons and collection structure require a legislative basis.
- Exact Arabic excerpt: «قاصرًا اختصاصه في هذا الشأن على الاقتراح بفرضها».
- This judgment complements SCC Case 36/18: Case 36/18 addresses an unpublished ministerial local-fee decision and its inseverable enabling provisions; Case 221/26 addresses the constitutional reservation of local-tax creation to legislation and the limits of a governor's decree.


## J. Updated progress after the complete 23 November pass
- **New candidate records added in this pass:** 33 (9 initial instruments, 15 local-law/local-regulation amendments, 7 SCC/SAC/implementing decisions, 2 further official SCC judgments).
- **Current repository candidate catalogue:** 517 document records across 43 candidate-source entries. This is a discovery inventory, not a count of unique laws or full texts.
- **Current central source-permission register:** 163 source records. New entries preserve unknown permission where no license/terms evidence was found; MKS Egypt site text is recorded as CC BY 4.0 with the scope limited to page text as displayed.
- **Arabic text recovery:** more than 20 legal text/scan artifacts were opened in this pass, including full searchable or near-full texts for Law 43/1979, Decision 707/1979, Law 45/2014, Law 18/2024, Decision 73/2024, Decision 94/2025, SCC Cases 2/16 and 36/18, SCC Cases 21/11 and 221/26, and several Supreme Administrative Court decisions. Other items are image-only scans or have OCR limitations; those are explicitly marked.
- **New complete full-text documents ingested into the authorized production corpus:** 0. This is intentional: most source reuse permissions remain unknown, and candidate/research notes must not be counted as corpus ingestion. The MKS page-level CC BY 4.0 notice is recorded, but no long-form reproduction has been committed in this research note.
- **Agent 7 domain research coverage:** approximately **50% (±10 percentage points)**, up from the previous rough 46% estimate. This is a qualitative estimate of the breadth of instruments, amendments and decisions discovered and text-recovered across the assigned scope; it is not a verified percentage of article text, authenticated sources, or release-ready corpus content.
- **Whole Egyptian legal corpus:** the last audited national estimate remains **about 2% provisional** (Checkpoint 121, 18 November 2026). This pass does not change that figure because the new material is candidate metadata and research evidence, not newly authorized corpus ingestion. There is no validated national denominator.
- **Separate engineering/workstream percentages** in other project checkpoints are not comparable to this Agent 7 legal-research estimate and should not be combined.
