# AI-2 #1903 integration contract (implementation checkpoint)

This is a conservative integration design checkpoint, not a claim that retrieval is implemented. The local checkout and Python runtime are unavailable in this session (GitHub clone DNS failure); the repository must be checked out and tests run before code changes are accepted.

## Adapter contract

- In the corpus provenance function, only call `load_source_match_evidence(connection, version_id, source_id)` when both IDs come from the retrieved registry-linked passage/version row, not caller-supplied metadata.
- Attach the returned packet as a nested `source_match_evidence` property only when the adapter returns a packet; do not reconstruct packets from hashes, URLs, flags, or registry fields.
- Treat absent packets as absent. Avoid exposing partial or stale packets as candidates.
- Ensure every returned hit binds provenance `source_id` and `version_id` to the hit's own row and preserve original digest equality.

## Candidate query and isolation

- Add a dedicated candidate retrieval query/scope, distinct from ordinary verified search; never loosen the verified-corpus query.
- Candidate scope must be gated by the explicit non-production environment, feature flag, exact firm-ID, and explicit policy-approval flag. Fail closed if any gate is missing, malformed, or mismatched.
- Candidates must be source-primary, exact-version, evidence-packet complete, and rights-cleared for the use requested by the query. Do not treat metadata existence as rights clearance.
- Do not expose candidate rows to production or other firms; do not allow firm/case data or ordinary search to bleed into the shared-corpus candidate scope.

## Status and legal guardrails

- Candidate status remains source-matched/unreviewed, not verified law.
- Keep verified, authenticity_verified, status_verified, amendment_history_verified false and review status pending. No lawyer-approval event is emitted or inferred.
- Law 14/2025 remains excluded absent explicit rights evidence.

## Required tests before merge

1. Exact source/version row identity and digest binding; stale/revision mismatch and independent-source identity checks.
2. Complete packet, date, article-inventory, difference-resolution, and explicit rights/use scope.
3. Missing, malformed, conflicting, stale, denied-rights packets excluded or downgrade to sources-only/review status.
4. Gate matrix: production, wrong firm, flag missing, policy approval missing, malformed configuration.
5. Candidate query is separate from verified retrieval and does not leak candidates to other firms or scope.
6. No lawyer-approval events and all verification flags remain false.
7. Python 3.12 exact-head suite, corpus isolation, tenant isolation and end-to-end retrieval tests.

## Checkpoint evidence

- Issue #1903 readback: open and acceptance requirements confirmed.
- Existing adapter and migrations 0005/0006 inspected.
- Existing trust-tier and search/provenance path identified through code search.
- Clone retry failed with `Could not resolve host: github.com`; no Python tests executed.
- This document is design/checkpoint documentation only. It does not authorize candidate exposure or certify implementation.


## Follow-up static readback correction — 2026-11-28

- A fresh full-file GitHub readback of current `app.py` confirms `citation_provenance(c, version_id)` already calls `load_source_match_evidence(c, data.get('version_id'), data.get('source_id'))` and attaches the packet when present; search-result construction copies it into the hit. Thus the adapter exposure portion appears already implemented in current main, contrary to the older trace documentation.
- The remaining live gap in the current main readback is `search(..., scope='firm_test_source_matched')`, which still unconditionally returns `[]`. This is direct static source inspection, not runtime verification.
- Local checkout retry again failed DNS. No source code/tests changed/executed. Need next implementation focus: carefully reviewed dedicated retrieval architecture, rights-use gating, and isolation, while reconciling outdated trace/blocker documentation.
