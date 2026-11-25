# AI-2 stabilization progress

**Snapshot:** 2026-11-25. Implementation-only estimates; NOT pilot or production acceptance. No GitHub Actions are used.

## Eight workstream snapshot

| Workstream | Previous | Current | Delta (pp) | Acceptance boundary |
|---|---:|---:|---:|---|
| Backend / existing workflows | 90% | 90% | 0 | Existing case, finance, audit, admin and operational flows remain unaccepted end-to-end |
| Frontend / usability | 95% | 95% | 0 | UI contracts/source review; browser acceptance pending |
| Mobile / Arabic-English UI | 83% | 83% | 0 | Responsive and bilingual source work exists; real mobile/browser/accessibility acceptance pending |
| Security / tenant isolation | 83% | 83% | 0 | Narrow filesystem hardening is committed in draft PRs; route and cross-tenant execution remain pending |
| Documents / file handling | 99.1% | 99.1% | 0 | Extraction/OCR/storage source controls; actual parser, route and integrity acceptance pending |
| Deployment / backup / recovery | 40% | 40% | 0 | Compose/provider validation and witnessed backup/restore acceptance remain pending |
| Local testing / regression | 20% | 20% | 0 | Supported Python 3.12 checkout/runtime is unavailable; committed tests are not passes |
| **Overall AI-2** | **72.7%** | **72.7%** | **0** | Historical aggregate remains unchanged; this is not a test-pass or readiness score |

The prior separate security-regression-source-coverage estimate remains 98%; it is tracked as coverage authoring, not executed validation, and is not folded into the above local-runtime workstream. Estimates are held flat because this slice adds regression code without executing the repository tests or changing broad acceptance evidence.

## 2026-11-25 manual continuation

- **Task:** exercise tenant DB and SQLite sidecar hard-link checks after SQLite opens, rather than only before connection setup.
- **Changes:** two race-injection regressions in `tests/test_tenant_storage.py` on draft PR #2007. Each uses a synthetic tenant fixture and injects an external hard-link alias after the journal-mode query creates the SQLite sidecar state; the router must fail closed and close the untracked connection.
- **Task implementation:** regression source added, 100%.
- **Isolated harness:** 2/2 synthetic SQLite checks passed for alias injection after the journal-mode query (one database-file alias and one WAL-sidecar alias). This validates the race-injection pattern and observed link-count behavior, not the tenant router itself.\n- **Repository execution:** 0%; the repository test module is not executed here. No Python 3.12 checkout/runtime is available and hosted Actions are blocked by billing.
- **Read-back:** the changed test file was re-fetched and inspected after the commit.
- **Security limitation:** filesystem hard-link checks do not demonstrate race-free directory-descriptor-based SQLite opening or protection from a privileged/local filesystem attacker. Route-level tenant isolation and browser acceptance are still unverified.
- **Pilot status:** NOT READY.

