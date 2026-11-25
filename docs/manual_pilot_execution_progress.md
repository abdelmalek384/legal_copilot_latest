# Manual pilot execution progress — 2026-11-25

**Purpose:** Track delivery without depending on GitHub Actions billing. This is an evidence-based planning snapshot, not a runtime test report or release certification. Percentage estimates measure work/evidence completeness against the acceptance gates, not code volume.

## Operating rules
- Do not retry unavailable hosted CI, billing-dependent workflows, or closed draft PRs.
- Prefer runnable local checks, source inspection, manual API/browser tests, disposable databases, and written evidence.
- A task cannot reach 100% without the acceptance evidence required by its gate. Source review alone is not a runtime pass.
- Never use real client data or production credentials in the test firm.
- For a pilot, any cross-firm/client authorization defect is a release-blocking failure.
- Keep legal-source verification separate from software readiness. Candidate text, secondary sources, and source matching are not lawyer verification.

## Progress snapshot (estimates)
| Workstream | Estimated completion | Remaining evidence / work | Can proceed without hosted CI? |
|---|---:|---|---|
| Core case management & matter workflow | 70% | Manual create/edit/navigation, deadline/session/fee persistence, export and edge-case acceptance | Yes |
| Document upload, extraction & review | 65% | Browser/API checks for PDF/DOCX limits, extraction, original-file retrieval, review history and rejection paths | Yes |
| Firm/client/matter access isolation | 55% | Two synthetic firms; direct-ID/API/search/download/export denial matrix; record evidence | Yes |
| Authentication, MFA, invitation & recovery | 65% | Clean browser checks, token lifecycle, MFA enrolment/recovery, session revocation and throttle behavior | Yes |
| Tenant storage, DB migrations & path safety | 71% | Disposable database profiles; migration and symlink/race boundary checks on supported host | Yes |
| Backup, restore & retention | 45% | Witnessed encrypted backup/restore rehearsal, archive tamper rejection, post-restore consistency | Yes |
| Deployment and configuration | 55% | Clean Python 3.12 install, local preflight, staging HTTPS/SMTP/S3 configuration and operator evidence | Yes, except live provider verification |
| Mobile, RTL/LTR & usability | 45% | Responsive browser/device acceptance in Arabic and English; keyboard/accessibility/error states | Yes |
| Legal Research UI & source trust labels | 60% | UI interaction acceptance and correct fail-closed trust-label behavior under controlled fixtures | Yes |
| Verified Egyptian legal corpus | 15% | Licensed/authorized originals, Gazette pinpoint evidence, current-law review and counsel attestation | Partially; counsel/source access required |
| Release evidence, monitoring & pilot sign-off | 25% | Consolidated evidence, defects, deployment monitoring, recovery/operator sign-off and approval | Yes, except external sign-off |

**Overall estimated delivery progress: 52%.** This weighted estimate is intentionally provisional; it reflects implementation/documentation already present and substantial acceptance work still open. It is not a measured success rate. Do not use it as a safety claim.

## Next executable sequence (do not loop blocked work)
1. Run the focused local regression modules on an available Python 3.12 environment and record exact command, interpreter, result and environment.
2. If a local runtime is unavailable, continue source-level review of one distinct subsystem and create concrete fixes/tests; do not repeatedly retry the same blocked command.
3. Create a disposable two-firm acceptance environment and run authorization-denial tests.
4. Run the document/matter workflow acceptance matrix with synthetic files.
5. Complete the encrypted backup/restore rehearsal.
6. Complete bilingual browser/device acceptance.
7. Reconcile defects and evidence before any pilot approval.

## Evidence log
| Date | Work | Result | Evidence |
|---|---|---|---|
| 2026-11-25 | Repository source/docs checkpoint; hosted CI excluded from plan | Read-only inspection completed; runtime execution not available in this session | docs/STATUS.md, docs/BLOCKERS.md, docs/test_firm_runbook.md, docs/document_intelligence_workspace.md, docs/legal_research_document_intelligence.md |
| 2026-11-25 | Repository checkout in current tool runtime | Blocked by DNS/network resolution; no retry planned in this session | Tool-session note; not a repository test result |\n| 2026-11-25 | Manual tenant-storage pathname-race source review | Bounded review completed; residual pathname-open identity race documented, no test execution or exploit demonstration | docs/manual_tenant_storage_review_2026-11-25.md; draft PR #1975 |

## Acceptance evidence template
For each run, record:
- commit SHA and branch
- OS, Python version, browser/device and locale
- environment type (disposable local/staging; never production)
- exact command or steps
- expected and actual result
- PASS / FAIL / BLOCKED
- defect ID and sanitized evidence location
- tester and timestamp/timezone

