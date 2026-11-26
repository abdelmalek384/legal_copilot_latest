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

The 21 missing document source families were enumerated during the diagnostic:\n\n- EG-CIVIL-STATUS-LAW-143-1994\n- EG-PUBLIC-CONTRACTS-EXEC-REG-AMENDMENT-289-2021\n- EG-PM-DECISION-4498-2023-GOVERNMENT-SPENDING\n- EG-STATE-COUNCIL-AMENDMENT-136-1984\n- EG-STATE-COUNCIL-AMENDMENT-77-2019\n- EG-CIVIL-SERVICE-EXEC-REG-AMENDMENT-714-2019\n- EG-CIVIL-SERVICE-EXEC-REG-AMENDMENT-1509-2026\n- EG-ADMIN-PROSECUTION-AMENDMENT-12-1989\n- EG-ADMIN-PROSECUTION-AMENDMENT-171-1981\n- EG-SAC-APPEAL-10639-54-2018-05-05\n- EG-SAC-APPEAL-2417-45-2003-12-13\n- EG-LABOUR-MINISTER-DECREE-162-2026\n- EG-LABOUR-MINISTER-DECREE-248-2026\n- EG-LABOUR-MINISTER-DECREE-249-2026\n- EG-LABOUR-MINISTER-DECREE-250-2026\n- EG-LABOUR-MINISTER-DECREE-251-2026\n- EG-LABOUR-MINISTER-DECREE-252-2026\n- EG-LABOUR-MINISTER-DECREE-260-2025\n- EG-STATE-COUNCIL-AND-JUDICIARY-AMENDMENT-159-2003\n- EG-SAC-APPEAL-203-38-1995\n- EG-SAC-APPEAL-4286-35-1992\n\nThis is a fail-closed coverage gap, not an invitation to add source records or legal content under the scope freeze. Do not seed these documents until their source records are intentionally reconciled with the existing permission register/catalog and allowed scope.

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

## Remote branch review

Read-only inspection of available remote branches related to candidate registry consistency found:
- `fix/legal-candidate-catalog-validation`
- `fix/unique-legal-candidate-ids`
- `database/legal-candidate-seeder-corpus-profile`

Their candidate catalog/seeder snapshots are older than current `main` and lack the current main seeder's later validation hardening (including duplicate-key/URL checks and canonical permission parity checks). They are not manually integrated; merging these stale snapshots would risk regressing the more hardened current implementation. No PR was created or left pending. The reported local branch `fix/legal-candidate-registry-consistency` remains unavailable as a remote ref and was not reviewed.
