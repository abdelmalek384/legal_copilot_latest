# Labour Law No. 14 of 2025 — candidate corpus

**Status: all 311 provisions have recorded Gazette page locators and visual page-image comparison notes; source-matched, not lawyer-reviewed. Pending source/reuse permission, currentness/amendment/corrigenda review, and qualified Egyptian-lawyer sign-off. Not approved for authoritative retrieval.**

This directory tracks the supplied Arabic JSONL corpus and its source review. The file is **not** committed to this public repository because redistribution and commercial-reuse permission have not been established.

## Inspected artifact

- Supplied filename: `law_rows_ar.jsonl`
- SHA-256: `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600`
- Size: 393,861 bytes
- Records: 311 valid JSONL records (13 promulgation provisions and 298 articles of the accompanying law)
- All rows had `verified=0`; all rows had `in_force=1`. The latter is untrusted input and must never be used to establish legal status.
- Source: [Manshurat text copy](https://manshurat.org/content/qnwn-lml-ljdyd-rqm-14-lsn-2025)
- Claimed primary publication: Official Gazette issue 18 (supplement), 2025-05-03
- Review result: structural audit and machine triage completed; all 311 provisions have page locators and recorded visual page-image comparison notes. All 273 machine-difference records, five numeric alerts, 120 quantitative cues, six known spelling outliers, and 29 previously unreviewed identical articles have recorded visual checks. No confirmed textual mismatch was found in the inspected passages. These are assistant checks, not counsel sign-off.

## Current review documents

- [Source and legal-status review](source_and_legal_review.md)
- [Detailed review report](review_report_2026-10-24.md)
- [Versioned registry candidate metadata](registry_candidate.json)
- [Related implementing-instrument candidates](related_instruments_candidates.json)
- Registration helper: [`tools/register_labour_law_candidate.py`](../../../tools/register_labour_law_candidate.py)

## Commencement and repeal leads

The accessible promulgation text states general commencement from 2025-09-01, specialized labour courts from 2025-10-01, and repeal of Labour Law No. 12/2003 and Law No. 125/2010 in Article 12. The supplied 112-page Gazette reference has now been visually compared against all 311 candidate provisions, including the promulgation provisions. Treat the dates and transitional effects as provisional version metadata until qualified Egyptian counsel independently confirms their legal interpretation and current effect.

Later official-source leads include Prime Minister's Decree 2652/2026 and Labour Ministry Decisions 74/2026 and 75/2026. They are tracked separately as possible implementing/related instruments, not assumed to be formal amendments.

## Permission and import safeguards

The IDSC repository [End User Agreement](https://dspace.id.com.eg/info/end-user-agreement) says commercial exploitation and systematic retrieval to compile a database require express written permission. No permission has been obtained. Public accessibility is not treated as a license.

The registry helper creates metadata and pending review events only. It does not import article chunks, trust incoming `verified`/`in_force` flags, or enable search. It has **not** been run against the user's local SQLite database from this session.

Before activation:
1. Obtain permission for storage, extraction, indexing, embeddings, display, redistribution, and commercial use, or verify another lawful licensed source.
2. Have qualified Egyptian counsel independently review the 311-row lawyer tick-sheet against an authorized source copy. The assistant's page-image comparisons are evidence aids, not a substitute for counsel's own review; if the supplied copy cannot lawfully be used, counsel must obtain an authorized copy and remap page locators.
3. Register related instruments separately and determine their exact legal relationship and dates.
4. Obtain qualified Egyptian-lawyer review of authenticity, commencement, transitional rules, repeals, and the amendment/implementation chain.
5. Only then consider approval and search eligibility.

A JSONL hash proves the identity of the supplied data file, not the authenticity of the law or permission to reuse it.

## Source-linked provision evidence cards (2026-10-28)

See [`provision_evidence_cards.json`](provision_evidence_cards.json) for 360 provisional Arabic research cards with article/page pinpoints, official publisher and government-hosted Gazette-PDF links, secondary cross-checks, explicit limitations, and related-instrument follow-ups.

The canonical main inventory contains 294 selected cards. Three separate split files (Articles 256–274, Articles 275–298, and promulgation Articles 2–11) are retained as archived review snapshots, but are not loaded by the manifest because their records overlap the canonical main file and include divergent duplicate IDs. Any useful unique updates from those snapshots must be reconciled into the canonical file before the split files can be re-enabled. The selection is not a complete one-card-per-article corpus. They are **provisional research leads only**. The exact 112-page user-supplied comparison PDF and 311-row JSONL were recovered from the Library source bundle on 2026-11-06; their SHA-256 values match the recorded comparison hashes. All 311 provisions now have page locators and recorded page-image comparison notes. The PDF reports copy/print restrictions, and the upload URL/capture chain is unknown. Do not infer permission to copy, extract, redistribute, index, or commercially reuse it. The comparisons are not lawyer sign-off. For Decision 49/2026 (annual-leave categories), IDSC-hosted Official Gazette metadata identifies the supplement to issue 64 dated 2026-03-18 as listing the decision. For Decision 294/2025 (paid holidays), IDSC-hosted metadata identifies the supplement to issue 291 dated 2025-12-25 as listing the decision. For both, the full text/page range has not been obtained and reviewed here; neither decision is a verified operative rule in this corpus.

These cards must not be activated as authoritative retrieval, used to calculate individual entitlements, or presented as a lawyer-reviewed current-law answer. Source reuse permission, complete amendment/currentness review, and qualified Egyptian-lawyer review remain outstanding.

A human-readable, source-linked rendering is available in [`provision_evidence_cards_review.md`](provision_evidence_cards_review.md). It is generated from the JSON record by:

```bash
python tools/report_labour_law_evidence_cards.py
```

The report is a review aid only; it does not change any source-permission, legal-status, lawyer-review, or retrieval-eligibility flags. Its regression test requires the checked-in Markdown report to match the JSON cards.

## Evidence-card inventory (2026-10-28)

The provisional evidence-card inventory currently represents 294 unique records in the canonical main file. Use [`provision_evidence_cards_manifest.json`](provision_evidence_cards_manifest.json) as the manifest; the report builder loads the canonical file, validates unique card IDs and preserves non-authoritative status. The split snapshots are intentionally excluded until duplicate IDs and divergent content have been reconciled. The 112-page user-supplied Law 14/2025 Gazette comparison PDF has been recovered and hashed; all 311 Law 14/2025 provisions have page-image comparison notes. This does not cover page-level review of separate implementing-instrument supplements: the Decision 49/2026 and Decision 294/2025 source texts and page ranges remain outstanding. All cards remain disabled for authoritative retrieval pending currentness, reuse and Egyptian-lawyer review.

