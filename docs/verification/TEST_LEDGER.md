# Test Ledger — Legal for Today

Evidence log; no retroactive certification.

| Date | Commit / scope | Command or evidence | Outcome | Classification |
|---|---|---|---|---|
| 2026-11-28 | Baseline `60b2ebd0d2a0940c904a6ac6afb54a4ac221fcec` | Source read-back of adapter, docs, issue #1903, PR #1902 | No tests executed | Inspection only |
| 2026-11-28 | Continuity docs #2048 merged `2a16454c52e660156d9fe7c6634678c442706db6` | GitHub merge response | Merge confirmed; documentation-only | Integration evidence |
| 2026-11-28 | #1903 code investigation | GitHub read-back: schema migrations 0005/0006, adapter, storage test, trust helper, provenance trace | Integration gap located; clone attempt failed DNS; tests not executed | Inspection/blocker |

## Evidence requirements
Record exact commit SHA, supported runtime, command, exit status, test output/count, and whether local or CI. Separate source inspection, synthetic harnesses, CI, staging, and live acceptance. Never claim unexecuted tests passed.


## 2026-11-28 AI-2 continuation checkpoint

- Re-read continuity files and #1903 issue; source-match adapter, migrations 0005/0006 and integration boundary confirmed.
- Repeated shallow clone attempt failed DNS (`Could not resolve host: github.com`); no code or tests executed.
- Added `docs/ai2_1903_integration_contract.md` on branch `ai2-1903-integration-contract`, documenting exact packet-binding, test-firm isolation, fail-closed retrieval and acceptance requirements. Design documentation only; no implementation/validation claim.
- Candidate serving remains disabled/fail-closed; verified/legal flags unchanged; Law 14/2025 remains rights-blocked.


## Follow-up static readback correction — 2026-11-28

- A fresh full-file GitHub readback of current `app.py` confirms `citation_provenance(c, version_id)` already calls `load_source_match_evidence(c, data.get('version_id'), data.get('source_id'))` and attaches the packet when present; search-result construction copies it into the hit. Thus the adapter exposure portion appears already implemented in current main, contrary to the older trace documentation.
- The remaining live gap in the current main readback is `search(..., scope='firm_test_source_matched')`, which still unconditionally returns `[]`. This is direct static source inspection, not runtime verification.
- Local checkout retry again failed DNS. No source code/tests changed/executed. Need next implementation focus: carefully reviewed dedicated retrieval architecture, rights-use gating, and isolation, while reconciling outdated trace/blocker documentation.
