# Labour Law No. 14 of 2025 — source and legal-status review

**Review state: provisional desk review only. Not a legal opinion; not approved for authoritative retrieval.**

## Candidate corpus under review

- Instrument: قانون رقم 14 لسنة 2025 بإصدار قانون العمل
- Candidate secondary text: [Manshurat — Labour Law No. 14 of 2025](https://manshurat.org/node/76602)
- Candidate file: `law_rows_ar.jsonl`
- Recorded SHA-256: `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600`
- Recorded size/count: 393,861 bytes; 311 JSONL records (13 promulgation/introductory provisions and 298 accompanying-law articles)
- Claimed publication: Official Gazette issue 18 (supplement), 3 May 2025
- Current repository status: the candidate manifest is present; the 311-row source file is not committed to this public repository.

## Findings and limits

### 1. Source permissions

**Outcome: unresolved — keep all permissions unknown.**

The Manshurat page is a secondary-hosted text copy. Publicly viewing a legal text does not, by itself, establish permission to download/store the site’s compilation, reproduce its editorial content, redistribute the JSONL, index it, or use it commercially. No sufficiently clear licence or written permission was established in this review.

Do not set `collection_permission`, redistribution permission, or commercial reuse permission to allowed based only on public accessibility. Keep the full supplied JSONL out of the public repository until the applicable terms or written permission are documented. The source SHA-256 identifies the supplied artifact; it does not prove authenticity or confer reuse rights.

### 2. Official Gazette comparison

**Outcome: not performed article-by-article.**

The supplied JSONL file is not available in the current working session, so the 311 records could not be compared against a copy of the exact Official Gazette issue. The manifest’s previously recorded count and hash are retained as supplied metadata, not independently re-computed here.

Before marking the text as matched, acquire/inspect the exact Official Gazette issue 18 (supplement), dated 3 May 2025, and compare:
- all 13 promulgation/introductory provisions;
- each of the 298 law articles, including article labels and exact Arabic wording;
- repeated/missing/inserted provisions, punctuation and paragraph boundaries;
- Gazette issue/page references and any corrigenda.

Record mismatches with row/article identifiers and evidence. A matching article count alone is not sufficient.

### 3. Commencement, transitional rules and amendment history

**Outcome: dates/status require primary-text and qualified Egyptian-counsel confirmation.**

The candidate file’s `as_of=2025-05-03` is treated as a claimed publication date only. It must not be copied into `effective_date` automatically. Public summaries indicate a general commencement date of 1 September 2025 and a separate date of 1 October 2025 for the specialized labour courts, but this review has not yet tied those conclusions to a page-verified copy of the enacted Official Gazette text. Treat these dates as leads for verification, not registry-approved facts.

The amendment/repeal chain and transitional rules have not been comprehensively verified for the date the application is answering. Do not mark the instrument currently in force, fully consolidated, or amendment-history-verified until the relevant provisions and subsequent official instruments are checked.

### 4. Registry/import decision

**Decision: register as a pending candidate only; do not activate for authoritative search.**

When the exact artifact and primary-source evidence are available:
1. Preserve the original file and calculate its SHA-256 locally.
2. Register the stable document identity and a distinct version in `legal_document_versions`, retaining publication date separately from the legally established effective date.
3. Set `legal_status='unknown'` and `review_status='pending_human_review'` while the evidence remains incomplete; leave `authenticity_verified`, `status_verified`, and `amendment_history_verified` false.
4. Do not trust incoming `verified` or `in_force` flags. Do not link the text to production-eligible chunks until the application’s source/version eligibility conditions are met.
5. Append review events with reviewer, evidence URL, outcome and timestamp. A qualified Egyptian lawyer should sign off on commencement, transitional rules, amendments, repeal/supersession and the relevant as-of timeline.

## Exact blocker to completing this work

Please provide `law_rows_ar.jsonl` in this conversation (or put it in the project working directory). Without the bytes of that file and the exact Gazette copy, I cannot truthfully report a completed 311-record comparison or perform the local database import. This report intentionally leaves those gates open.
