# Legal Copilot — release-candidate status

**Updated:** 2026-11-14  
**Decision:** **NOT READY** for lawyer pilot or production. This is an engineering checkpoint, not legal, security or operational certification. Historical tracker detail is archived at [STATUS history](archive/STATUS_history_through_2026-11-13.md).

## AI-1 delivery

| Workstream | Current state |
|---|---|
| Answer rating contract | **Complete.** [Contract](answer_rating_contract.md) defines answer ID, rating, cited-article rating, notes, rater, timestamp, trust tier and UTF-8 CSV export for AI-2. The firm export now includes message-time `trust_tier` with a conservative fail-closed mapping; `tools/adapt_answer_rating_export.py` implements the canonical interchange and `docs/answer_rating_contract.md` documents its usage. A route regression passes actual export rows through the adapter; execution remains pending. Adapter tests are committed and registered in `.github/workflows/tests.yml`, but unexecuted. `tools/validate_answer_ratings.py` validates exported CSV structure, enums and timezone-aware timestamps; tests are committed but unexecuted. Evidence-URL validation parity was extended across `research_inspector`, `evaluate_legal_answers`, `app.validate_review_evidence_url`, the deadline-rule verifier, and the legal-document collector/manifest, manual-capture, deadline-rule attestation, source-match rights, legal-draft source and bulk-law-import URL checks (DEL, raw backslashes, query/fragment ambiguity where evidence URLs are used); regression tests remain unexecuted. The evaluation API runner now rejects DEL and raw-backslash base URLs; the legal-candidate seeder validates HTTPS source-page, terms, official-PDF and secondary-metadata URLs and rechecks source hosts against the permission register. The Gazette importer CLI now has a direct-execution import fallback; its CLI regression explicitly clears `PYTHONPATH`. |
| Negation guard | **Implemented; tests unexecuted.** Always-on guard is in `app.ask()`. Three focused English/Arabic reproductions and an integrated answer-path test are committed directly to main (`92e5177`, `f988e76`). No test pass is claimed. |
| Firm-test source-matched mode | **Fail-closed response gate implemented; real retrieval unavailable.** Exact firm-ID + non-production environment flag, source-only fallback and explicit `source-matched, not lawyer-verified` API label are on main (`ce2ebc8`, `7c5e09d`, `5ec22a1`, `b377af0`, `311287d`, `2009b9f`, `29e4a13`). The dedicated scope currently returns no candidates; tests use synthetic hits and are unexecuted. Never enable in production. |
| Reviewer spreadsheets | **Templates complete.** [Gazette review CSV](legal_evidence/law_14_2025_gazette_comparison_template.csv) has 311 rows, machine comparison labels, similarity, page locators and prior page-review notes. Text and lawyer decision fields remain blank pending authorized source text. [Deadline CSV](legal_evidence/deadline_rules_lawyer_review.csv) has five draft rules. [Review guide](legal_evidence/lawyer_review_quick_guide.md) gives steps and time estimates. |
| Evaluation | **116 unapproved drafts complete; a new structural validator checks Arabic question text, question IDs/text uniqueness, one formal/one colloquial variant per article pin, expected-article pin consistency and no premature lawyer approval/release flags. Static audit of the current inventory found 116 rows (58 formal/58 colloquial), 58 proposed article pins and zero invariant mismatches. [Lawyer review guide](legal_evidence/law14_2025_evaluation_review_guide.md) added. Metrics unavailable.** Structural-validator, negation reproducer, firm-test gate, rating-validator and adapter tests are now explicitly registered in `.github/workflows/tests.yml`; they remain unexecuted. Dataset contains 58 formal + 58 colloquial questions with machine-proposed article IDs. [Unreviewed inventory](legal_evidence/law14_2025_retrieval_baseline_unreviewed.json) records 116 unique questions, zero approved answer keys and zero run records. Top-3 hit rate, wrong-article rate and abstention rate are null—not zero. The scorer requires lawyer-approved labels and real retrieval runs. |
| Documentation | **Complete.** Detailed tracker archived; this is the concise release summary. |
| Gazette importer owner handoff | **Prepared.** Added [operator handoff](legal_evidence/law14_2025_import_operator_handoff.md) and [metadata template](legal_evidence/law14_2025_import_metadata.template.json), including exact input requirements, SHA-256 procedure, CLI command and trust safeguards. The importer accepts explicit expected promulgation/attached-law counts and reports internal gaps, missing trailing numbers, out-of-range headings, and an entirely absent expected block; focused regression cases are committed but unexecuted. No real import run is claimed; authorized UTF-8 text and truthful supplier/source metadata are still required. |

## AI-2 delivery

| Workstream | Current state |
|---|---|
| Security mainline | Trusted-proxy hardening (#1495), LLM SSRF IP pinning and payment self-approval prevention (#1505), role-aware subscription recovery (#1504), and phone-login readability (#1506) are merged. Relevant security invariants still require exact-head local execution. |
| Lawyer answer rating | **Implemented on main; tests unexecuted.** Firm-scoped submit/update/read API, reviewer identity from the authenticated principal, admin-only firm list/export, append-only event ledger, CSV BOM/quoting/formula neutralization, bilingual per-answer controls, and universal assistant trust-tier fallback badge are committed. Its export now includes message-time `trust_tier` with conservative mapping: explicit `source_matched` is preserved, `verified` requires every source to be verified operative text, and all other cases become `unverified`. The AI-1 adapter maps `partially_correct` to `partial` and excludes `not_applicable` without coercion. The export also now emits a real UTF-8 BOM and RFC-style CRLF row endings and normalizes SQLite UTC timestamps to explicit `Z` timestamps. The route regression sends actual exported rows through the canonical AI-1 adapter. Export/adapter tests remain unexecuted. See [firm export contract](answer_rating_export_contract.md) and [canonical interchange contract](answer_rating_contract.md). |
| CSV import/export injection | Added an import-to-invoice-export regression using formula-like case title/client values; the export must neutralize spreadsheet formulas. Test is registered in the existing workflow and security matrix; execution remains pending. |
| Upload and prompt-injection tests | Encrypted-PDF rejection and the 500-page parser limit have focused tests; multipart route regressions now cover oversized, over-500-page, malformed, and encrypted PDF uploads and assert that rejected objects are not retained. Case-scoped retrieved-passage/provenance prompt-injection serialization has a regression. A new end-to-end regression uploads a hostile DOCX through the multipart route, retrieves it from the tenant-scoped index, checks cross-firm isolation, verifies the matter-data LLM approval gate, and asserts the hostile content is serialized as untrusted JSON. Concurrent OCR/rasterization jobs are bounded to two, with a five-second capacity wait and fail-closed 503 before expensive page rendering; saturation and timeout-release regressions are committed. The per-page OCR subprocess timeout remains 30 seconds and has timeout-propagation/semaphore-release coverage. All remain unexecuted. |
| Test-firm package | Demo-firm procedure, test-mode banner and first-run wizard are documented; clean-clone-to-first-login procedure has been added. It has not been executed. |
| Staging and recovery | The local release checker now explicitly runs the focused security matrix, an isolated encrypted multi-tenant backup/restore drill, placeholder-only Compose configuration validation, and optional workflow lint/security scan when installed. All remain unexecuted. Credential-only preflight failures must be recorded separately from missing infrastructure/configuration. |
| Validation | GitHub Actions billing prevents hosted test execution. No newly added local tests have been executed in this work session. Direct-main commits are implementation evidence, not test passes or pilot acceptance. |

## AI-2 implementation completion estimate

These are unweighted engineering estimates for the seven AI-2 delivery workstreams, not test-pass rates or production-readiness scores.

| Workstream | Estimated implementation completion | Remaining acceptance |
|---|---:|---|
| Local release baseline | 0% | Exact local checker output still unavailable |
| Security integration | 75% | Exact-head security verification remains blocked |
| Security regression coverage | 75% | Added route, OCR, rating and injection regressions remain unexecuted |
| Lawyer rating UI/export | 95% | Browser acceptance and adapter execution remain pending |
| Test-firm package | 90% | Clean-clone first-login rehearsal remains unexecuted |
| Repository cleanup/accessibility | 80% | Run hygiene scan and finish manual accessibility review |
| Staging/recovery | 25% | Compose validation, provider configuration and witnessed restore remain pending |

**Unweighted implementation estimate: 63%.** The application remains **NOT READY** for lawyer pilot or production. No test pass is inferred from committed test code.

## Legal evidence boundary

- Labour Law 14/2025 remains **source-matched, not lawyer-reviewed**; `verified=0` for all 311 candidate rows; `authoritative=false` and `retrieval_eligible=false`.
- The supplied ZIP candidate JSONL was structurally inventoried (13 promulgation provisions + 298 articles; no missing/duplicate numbers; malformed rows 0). The separately supplied 112-page Gazette PDF text layer was also inspected locally: all 13 promulgation headings and all 298 attached-law article headings appear in sequence, with no gaps/duplicates. See [inventory audit](legal_evidence/law14_2025_uploaded_candidate_inventory_audit.json) and [PDF heading audit](legal_evidence/law14_2025_uploaded_pdf_heading_audit.md). This is numbering coverage only—not article-body matching, an importer run, or legal verification.
- Collection/reuse permission remains unknown and the supplied scan reports copy/print restrictions. Do not commit or serve the candidate text, or bypass source restrictions.
- Decisions 248–252/2026 are metadata-only related-instrument candidates; full text is restricted/unavailable, permission unknown and legal review pending.
- No law becomes verified without qualified Egyptian counsel reviewing text, commencement, amendments/currentness and source rights.

## Remaining gates

1. GitHub billing/runtime access or a supported local Python 3.12 environment is needed to execute the focused tests; no CI or local test output is claimed.
2. AI-2 implementation is on main; execute rating-route/frontend tests and Arabic/English browser acceptance in a clean Python 3.12 checkout.
3. Owner must supply the UTF-8 Gazette transcription and completed truthful metadata described in [the importer handoff](legal_evidence/law14_2025_import_operator_handoff.md). The importer can create quarantined candidates while permission remains unknown, but no collection/reuse or production ingestion is permitted without evidence of permission.
4. Counsel must approve the evaluation questions/article key and answerability; then an authenticated corpus/API and before/after run exports are needed for scoring.
5. Billing/provider acceptance, tenant-isolation/recovery rehearsal, device/accessibility acceptance and pilot-firm workflow remain separate release gates.

**Last formally recalculated whole-project score:** 50.10% (2026-11-01). No newer weighted score is asserted.
