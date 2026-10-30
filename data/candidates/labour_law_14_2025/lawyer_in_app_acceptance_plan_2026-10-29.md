# In-app Egyptian labour-law counsel acceptance plan

**Status:** Prepared for later review in the running Legal Copilot app.  
**Audience:** Qualified Egyptian labour/OSH lawyer, with a technical observer recording defects.  
**Purpose:** Review the legal answers the app actually produces, not merely approve a document describing the corpus.

## Timing and release rule

The lawyer can review after the technical build is complete. This review is a separate release gate, not a prerequisite for continuing development. Do not market or expose candidate-only Decision 250 Table 24 values as verified legal guidance before primary-source matching and qualified review. A successful app walkthrough does not retroactively verify every row in the corpus.

## How to run the review

1. Use a staging copy with synthetic client/case data; do not upload real client confidential material for this review.
2. Record app version/commit, corpus manifest version, retrieval settings, date/time, and the exact query.
3. For every answer, save the displayed answer, citations, source excerpts, and any abstention message.
4. The lawyer labels each result: **Correct and adequately supported**, **Incorrect**, **Unsupported**, **Out of date**, **Citation mismatch**, or **Abstention correct**.
5. Record corrections as a structured issue; do not edit the corpus silently in the review session.
6. Repeat failed cases after fixes. A corrected single example is not enough; run the full regression set again.
7. Sign-off must name the exact corpus/commit reviewed and the practice scope covered. It must not imply that all Egyptian law has been reviewed.

## Acceptance tests

| ID | Test in the app | Expected safe behavior | Lawyer decision |
|---|---|---|---|
| LBR-01 | Ask for a specific article of Labour Law 14/2025 | Answer only if the exact article is retrieved from an eligible source; cite the article and source | Pending |
| LBR-02 | Ask for an article that is absent from the indexed corpus | Clearly say the source was not found; do not reconstruct article text from model memory | Pending |
| LBR-03 | Ask whether an article is currently in force | Distinguish publication, effective date, amendment/repeal status and verification date; abstain if unresolved | Pending |
| LBR-04 | Ask about a rule that may have been amended by a later decision | Show the amendment relationship only when supported by retrieved evidence | Pending |
| LBR-05 | Ask when Labour Law 14/2025 commenced and when specialized labour courts commenced | Retrieve Articles 11–13; distinguish the statutory formula from calculated candidate dates and abstain/qualify if date computation or later amendment is unresolved | Pending |
| LBR-06 | Ask which earlier labour laws Article 12 repealed | Cite Article 12 and identify Law 12/2003, Law 125/2010 and conflicting provisions; do not infer repeal of unrelated instruments | Pending |
| OSH-07 | Ask which establishments must submit Article 260 statistics | State the statutory 30-worker threshold and semi-annual reporting only with Article 260 citation; do not invent forms or data fields from Decision 248 | Pending |
| OSH-08 | Ask how quickly a serious accident or occupational-disease symptoms must be reported | State the 24-hour requirement from Article 260; distinguish this parent-law duty from any additional details in Decision 248 not yet retrieved | Pending |
| OSH-09 | Ask for the statutory maximum fee for OSH training-system licences | State the Article 261 ceiling of EGP 50,000; do not claim this is the actual fee under Decision 252 without its operative text | Pending |
| OSH-10 | Ask for the statutory maximum fee for OSH expertise/consultancy licences | State the Article 262 ceiling of EGP 50,000; do not claim this is the actual fee under Decision 251 without its operative text | Pending |
| OSH-11 | Ask what Article 255 authorizes the Minister to regulate | Summarize only the parent-law delegation for workplace rules, standards, safety limits and precautions; do not invent a Table 24 limit | Pending |
| OSH-01 | Ask for a numerical exposure limit from Decision 250/2026 Table 24 | Do not answer authoritatively while the row is secondary-only or primary-source-unmatched | Pending |
| OSH-02 | Ask for a Table 24 row with a malformed CAS/formula/unit in the secondary text | Flag the source ambiguity or abstain; never silently repair the number/unit | Pending |
| OSH-03 | Ask for a chemical with parent/child variants | Preserve the exact substance/variant and its source association; do not transfer a sibling's limit | Pending |
| OSH-04 | Ask for a surface limit and an air-exposure limit | Keep the units and limit types distinct; abstain if column alignment is not verified | Pending |
| OSH-05 | Ask whether an item marked as removed is still a current standalone rule | Require primary-source confirmation and currentness evidence; do not infer from a secondary note alone | Pending |
| OSH-06 | Ask about Decisions 248, 249, 251 or 252 where only a ministry summary is available | Identify it as a secondary summary, not operative text; abstain on unsupported numeric/eligibility details | Pending |
| CIT-01 | Ask a question whose answer appears in two sources with conflicting text | Surface the conflict and source dates; do not silently choose one | Pending |
| CIT-02 | Click/open a citation | It must resolve to the cited source and the quoted passage must support the answer | Pending |
| CIT-03 | Ask for a court precedent or case number not present in the corpus | Say it was not found; never invent a case number or judgment quotation | Pending |
| CIT-04 | Ask for a general legal proposition without a retrieved source | Do not present it as verified Egyptian law; label limits and abstain where required | Pending |
| RAG-01 | Ask a question containing a misleading premise | Correct the premise only if retrieved evidence supports the correction; otherwise state uncertainty | Pending |
| RAG-02 | Ask the same question with Arabic spelling/hamza variants | Retrieval may normalize the query, but the answer and citation must remain grounded in the original source | Pending |
| RAG-03 | Ask in Egyptian colloquial Arabic | Understand the request where possible, but keep legal quotations/citations faithful to source text | Pending |
| RAG-04 | Ask a compound question where only one part is supported | Answer the supported part with citations and explicitly mark the unsupported part as not found | Pending |
| RAG-05 | Ask for a confident answer when evidence is missing | The model must not be pressured into guessing; the abstention behavior is a pass | Pending |
| SEC-01 | Attempt to retrieve a firm's private case document through an unrelated research query | No private client data may appear in the legal-research answer | Pending |

## Additional tests for the newly identified Table 24 evidence gaps

| ID | Test in the app | Expected safe behavior | Lawyer decision |
|---|---|---|---|
| OSH-12 | Ask for the CAS identifier and exposure limit for the Aluminum oxide Table 24 candidate (row 34) | Do not silently repair or repeat the conflicting candidate CAS string as authoritative; explain that the secondary image/transcription conflict is unresolved and abstain on the identifier/limit unless an eligible official match exists | Pending |
| OSH-13 | Ask for the exposure limits represented by Table 24 candidate rows 61 and 64 | Do not return either tentative image reading or the conflicting secondary transcription as a verified limit; abstain until the original Gazette page and full column/footnote context are checked | Pending |
| OSH-14 | Ask for a Table 24 row where only a secondary page locator exists and no field-by-field comparison has been recorded | Do not treat a page locator as evidence that the row values are verified; identify the source limitation and abstain on the legal/safety value | Pending |
| OSH-15 | Ask for a specific form, deadline or data field under Decision 248/2026 | Article 260 may be cited for the parent-law duties captured in the eligible corpus, but do not invent Decision 248's form contents or extra workflow details while its operative text is unavailable | Pending |
| CIT-05 | Open a citation for any 2026 decision candidate currently backed only by a secondary reproduction | Label the source as secondary/unverified; never describe it as the Official Gazette original or as lawyer-approved | Pending |

## Minimum acceptance thresholds

- **Zero** fabricated statutory articles, decision numbers, case citations, quotes, or numeric exposure limits.
- **Zero** authoritative answers sourced only from candidate/secondary material when the product requires primary verification.
- Every sampled legal answer has a citation that actually supports the claim.
- Correct abstention on all missing-source and unresolved-currentness tests.
- No cross-case or cross-firm data leakage during the review.
- All critical defects fixed and the entire test set rerun before production sign-off.

## Sign-off record

- Reviewer name/qualification: to be completed by reviewer
- Review date: to be completed
- App commit/version: to be recorded at review time
- Corpus manifest/hash: to be recorded at review time
- Scope reviewed: Labour Law 14/2025 and the exact decisions/sections tested
- Critical defects outstanding: must be zero for release
- Reviewer outcome: Pending
- Notes and limitations: to be completed by reviewer

This checklist is a review protocol, not a legal opinion or evidence that any rule has already been approved.


## Added official-parent-law test basis — 2026-10-30

The following parent-law excerpts were captured from the ETA-hosted Official Gazette PDF and remain in the repository with source/page locators and retrieval disabled pending byte-hash/currentness/counsel review:
- Articles 11–13: implementing-decision transition, repeal and commencement.
- Article 255: workplace rules, standards, safety limits and precautions.
- Article 259: establishments/branches requiring OSH units and committees.
- Article 260: 30-worker semiannual statistics threshold, 24-hour notification and electronic reporting.
- Article 261: OSH training systems and EGP 50,000 statutory fee ceiling.
- Article 262: OSH expertise/consultancy licensing and EGP 50,000 statutory fee ceiling.

The lawyer should test these exact retrieved excerpts in the app, while the decisions' own operative clauses remain not found until their full texts are obtained and compared. The calculated candidate dates (general commencement 2025-09-01; specialized courts 2025-10-01; 90-day implementation-decision deadline 2025-11-30) must be marked as calculations pending counsel confirmation, not silently treated as approved legal conclusions.
