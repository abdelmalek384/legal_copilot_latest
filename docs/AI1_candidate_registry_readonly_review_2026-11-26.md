# AI-1 Candidate Registry Consistency Read-Only Review — 2026-11-26

## Scope and evidence
Reviewed the current `main` versions of:
- `docs/legal_document_candidates.json`
- `docs/source_permission_register.json`
- `tests/test_claim_support.py`
- `tools/register_labour_law_candidate.py`
- `tools/seed_legal_candidates.py`

The user-reported worktree branch `fix/legal-candidate-registry-consistency` was not found among available remote refs at inspection; fetch-by-ref returned 404. The review therefore does not claim to inspect that local branch or its uncommitted files. No files on the owner's local checkout were changed.

## Registry diagnostic (computed from fetched JSON, not repository tests)
- Candidate catalog: 43 source records, 548 document records.
- Permission register: 220 source records.
- Duplicate candidate source IDs: none.
- Duplicate permission-register source IDs: none.
- Duplicate document IDs: none.
- Catalog source records absent from permission register: none.
- Permission-field parity (collection and commercial reuse) for shared source IDs: no mismatches.
- Documents whose source_id is not represented among the catalog's 43 sources: 21.

The 21 missing document source families were enumerated during the diagnostic. This is a fail-closed coverage gap, not an invitation to add source records or legal content under the scope freeze. Do not seed these documents until their source records are intentionally reconciled with the existing permission register/catalog and allowed scope.

A separate host-parity diagnostic was inconclusive due to the review helper's URL handling and is not reported as a verified defect.

## Code inspection observations
- The seeder's validation requires document source IDs to be represented by the catalog source list, and permission parity is checked against the canonical permission register before database writes.
- Existing source/document seed operations are transaction/savepoint guarded and conflict-check metadata rather than overwriting.
- Candidate status remains discovery-only; the reviewed seeder does not create legal-text chunks or promote sources to verified.
- These are source-inspection observations only; runtime execution was not performed.

## Limitations
- GitHub Actions not used.
- No Python runtime/test suite executed.
- No lawyer-approved evaluation or live retrieval check.
- No legal source, law, dataset or corpus was added.
- No branch changes were integrated and no PR was left pending.

## Next
Inspect the actual remote branches/commit diffs related to registry consistency and seeder validation, then make a narrowly scoped fix only if code evidence supports it and the scope freeze allows it. Otherwise keep the gap explicitly fail-closed and hand it to the owner's local testing/reconciliation process.
