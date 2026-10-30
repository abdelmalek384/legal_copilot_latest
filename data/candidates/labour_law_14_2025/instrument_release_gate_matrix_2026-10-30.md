# Egyptian Labour Law / OSH instrument release-gate matrix

**As of:** 2026-10-30  
**Scope:** Labour Law 14/2025 and Ministry of Labour Decisions 248–252/2026  
**Purpose:** Prioritize evidence acquisition and make it impossible to confuse parent-law text, secondary reproductions, catalogue metadata, and approved operative rules.

## Gate definitions

| Gate | Pass condition | What does not pass it |
|---|---|---|
| G1 — Identity/provenance | Instrument identity, issuer, Gazette issue/date, source URL and exact original bytes or official full-text locator are recorded | News article, catalogue abstract, third-party transcription alone |
| G2 — Operative text | Full articles, annexes, tables, footnotes and forms are independently compared to official Gazette pages; page/line locators and source hash are recorded where bytes are available | Parent-law enabling article, summary, partial page sample, watermarked scan alone |
| G3 — Currentness | Commencement, transitional rules, amendments, corrections, repeal/supersession and status are checked through the review date | Publication date alone; assuming a new decision remains unchanged |
| G4 — Source-use | Legal basis for reproducing/indexing/displaying the underlying official text is documented; third-party site/database terms are assessed separately | Assuming public access means unrestricted reuse; assuming Article 141 clears third-party compilations |
| G5 — Qualified counsel | Egyptian lawyer approves exact provision/rule, interpretation, effective date and citation against exact corpus/app version | UI walkthrough, generic product approval, developer self-review |
| G6 — Retrieval release | Only the exact approved rule/version is marked retrieval-eligible; negative tests prove all unapproved records remain excluded | Import success, CI pass, candidate completeness, or a global “document approved” flag |

## Instrument-by-instrument state

| Instrument | Present evidence | G1 | G2 | G3 | G4 | G5 | G6 |
|---|---|---|---|---|---|---|---|
| Labour Law 14/2025 | Government-hosted ETA Official Gazette PDF route; eight Arabic excerpt records for Arts. 11–13, 255, 259–262; selected rendered-page inspection | Partial: official URL and Gazette identity; original bytes/hash unavailable | Partial: eight selected articles, not whole statute or all amendments | Not complete | Not complete; Article 141 route is a research lead only | Not reviewed | No |
| Decision 248/2026 | Official Ministry issuance announcement; exact Gazette Supplement 225(A) DSpace catalog record (12 Oct 2026; original 6.13 MB bundle request-copy restricted); parent-law Art. 260 cross-reference | Partial: catalog identity confirmed; no original decision PDF bytes or official-page comparison | No operative decision text | Not started | Not started | Not reviewed | No |
| Decision 249/2026 | Official announcement; exact Gazette Supplement 225(A) catalog record; secondary watermarked pages 19–44; candidate Articles 1–22 and annex maps; enabling Art. 259 | Partial: catalog identity confirmed; no original decision PDF bytes or official-page comparison | Secondary map only; no official page match | Not started | Not started | Not reviewed | No |
| Decision 250/2026 | Official announcement; exact Gazette Supplement 225(A) catalog record; 781-row secondary Table 24 sequence; 137 Table 23 labels; secondary images for Table 24 rows 1–327; parent-law Art. 255 | Partial: catalog identity confirmed; 781 candidate entries structurally complete but 0/781 official-page matches | No official row match; 76 partial secondary-image spot-checks; 3 discrepancies quarantined | Not started | Not started | Not reviewed | No |
| Decision 251/2026 | Official announcement; exact Gazette Supplement 225(A) catalog record; secondary pages 371–377; 11-article map and 17 assertions; enabling Art. 262 | Partial: catalog identity confirmed; no original decision PDF bytes or official-page comparison | Secondary map only; no official page match | Not started | Not started | Not reviewed | No |
| Decision 252/2026 | Official announcement; exact Gazette Supplement 225(A) catalog record; secondary pages 378–398; 36-article map, programme-hours table and 40 assertions; enabling Art. 261 | Partial: catalog identity confirmed; no original decision PDF bytes or official-page comparison | Secondary map only; no official page match | Not started | Not started | Not reviewed | No |

**Status rule:** “Partial” means only the evidence explicitly described in the present repository has been captured. It is not a legal verification label. All five 2026 decisions remain quarantined and retrieval-ineligible.

## Highest-value next work

1. Acquire the exact Gazette supplement 225(A), dated 2026-10-12, through an ordinary authorized route. The Amiri Press DSpace catalogue identifies the bundle but currently routes its Download action to request-a-copy; no request or access bypass has been made.
2. If the original bundle becomes available, hash the original bytes before extraction; record page count, printed-page/PDF-page mapping, each decision boundary, annexes and all footnotes.
3. Compare Decision 250 Table 24 first because it contains numerical occupational exposure limits and the existing candidate transcription has three known discrepancies. Do not normalize CAS/formula/unit values until source comparison resolves them.
4. Compare Decisions 249, 251 and 252 clause-by-clause against their candidate maps. Decision 248 needs its own operative text and forms compared against Article 260.
5. Complete currentness and source-use review per instrument and per version; do not use one generic approval for all five decisions.
6. Run the in-app counsel acceptance plan only after the corpus and retrieval controls are technically ready. Record counsel, date, app build, corpus version, exact provisions tested, decisions, corrections and re-test outcome.
7. Release only records that independently pass G1–G6. A CI pass validates software safeguards, not legal correctness.

## Non-negotiable quarantine controls

- Candidate/secondary-source records must never enter authoritative retrieval.
- An enabling provision in Law 14/2025 may support the subject matter of a later decision but cannot substitute for that decision's operative text.
- Secondary page images may identify transcription anomalies; they cannot be labelled official-source matches.
- Unknown, conflicting, missing, or visually ambiguous values remain unresolved and must trigger abstention rather than an inferred answer.
- The legal assistant must expose the source, exact article/annex locator, instrument version and effective-date status for each answer.


## Exact Gazette bundle identity/access note — 2026-10-30

The Amiri Press DSpace record for Supplement 225(A) is now directly inspected: https://dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full. It identifies the publisher as المطابع الأميرية, contributing authority as وزارة العمل, issue date 2026-10-12, and original bundle `العدد 225 تابع أ - مؤمن.pdf` (6.13 MB), with Decisions 248–252 listed in its abstract. The repository's download action is request-copy restricted. This advances catalog identification only; no original bytes, hash, reuse permission, or operative-text comparison are claimed.
