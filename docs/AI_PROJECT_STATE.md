# AI Project State — Legal for Today

**Repository:** [legal_copilot_latest](https://github.com/abdelmalek384/legal_copilot_latest)  
**Checkpoint:** 2026-11-28; continuity docs merged as commit `2a16454c52e660156d9fe7c6634678c442706db6`.

## Direction
Controlled law-firm pilot. Fail-closed source trust, tenant isolation, security, and lawyer review are release-critical. Pilot is NOT READY.

## Current P0
- **Issue #1903:** implement exact-version source-match evidence retrieval only for the explicitly gated non-production test firm.
- Existing `migrations/legal_corpus/0005_source_match_evidence.sql` and `0006_source_match_evidence_use_rights_guard.sql`, plus `tools/source_match_evidence.py`, already store and read validated evidence. Missing integration is the corpus provenance adapter and candidate-search scope.
- Draft PR #1902 classifier is a prerequisite, not an end-to-end integration. Review its exact-head CI and prior blockers before dependency use.
- Preserve `verified=0`, pending review, false authenticity/status/amendment verification flags, no lawyer-approval event, and complete rights evidence. Do not activate Law 14/2025 without explicitly cleared reuse rights.

## Session accomplishments
- Restored `docs/AI_PROJECT_STATE.md`, `docs/AI_TASK_BOARD.md`, and `docs/verification/TEST_LEDGER.md`; PR #2048 merged, commit `2a16454`.
- Read back issue #1903, adapter, schema migrations, trust-tier helper, storage test, and status/trace references.
- Identified integration boundary: `citation_provenance()` returns registry-linked provenance but currently omits the full machine evidence package; test-mode search scope yields no candidates.
- No repository tests executed. No legal permissions, status, or real-source data altered.

## Next implementation action
Implement adapter exposure and candidate retrieval with synthetic evidence only, exact version/source binding and firm/environment/policy gate; test isolation and malformed/missing evidence. Current workspace cannot clone GitHub (DNS resolution failed), so source changes/test execution are blocked until a checkout/runtime is available. Do not claim implementation or tests passed.


## 2026-11-28 AI-2 continuation checkpoint

- Re-read continuity files and #1903 issue; source-match adapter, migrations 0005/0006 and integration boundary confirmed.
- Repeated shallow clone attempt failed DNS (`Could not resolve host: github.com`); no code or tests executed.
- Added `docs/ai2_1903_integration_contract.md` on branch `ai2-1903-integration-contract`, documenting exact packet-binding, test-firm isolation, fail-closed retrieval and acceptance requirements. Design documentation only; no implementation/validation claim.
- Candidate serving remains disabled/fail-closed; verified/legal flags unchanged; Law 14/2025 remains rights-blocked.
