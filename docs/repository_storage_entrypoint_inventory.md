# SEC-01 — repository storage, file, backup, and job inventory

**Review date:** 2026-10-24  
**Scope:** targeted static review of the current repository's storage-related entry points beyond the main request handlers, including CLI commands, corpus tooling, backup/restore, collection outputs, and deployment guidance.  
**Evidence level:** engineering inventory based on source inspection and repository searches. This is not an exhaustive SQL audit, a deployment-host inspection, a penetration test, or an independent security review.

## Executive finding

The application still uses one SQLite database selected by the process-wide `COPILOT_DB` environment variable (default `copilot.db`). The connection-provider extraction in PR #115 is only a connection-lifecycle boundary. It does not route by trusted firm identity or establish per-firm database isolation.

This pass identifies additional non-request paths that must be accounted for before tenant migration. No tenant-routing or data-migration behavior is implemented by this document.

## Entry-point inventory

| Entry point | Observed behavior | Tenant/isolation implications | Follow-up |
|---|---|---|---|
| `app.py: DB / conn()` | Uses one configured SQLite path; schema setup and inline migrations run through the app connection path. | All firms and shared legal corpus currently coexist in one database. | Keep tenant database selection server-side; move schema changes to versioned migrations before multi-database provisioning. |
| `manage.py adduser` | Creates a user through `app.conn()`; command accepts a role but no firm selector. | User creation is tied to the single configured database and does not provision a firm boundary. | Redesign onboarding only after deciding whether identities are global or firm-specific and how initial firm membership is trusted. |
| `manage.py resetpw` | Finds an account by email, updates its password, revokes that user's sessions, and writes a security audit event through `app.conn()`. | Assumes email identifies one account in the shared database; implications change if users can belong to multiple firms. | Specify global identity, membership, session revocation, and firm audit semantics before moving identity tables. |
| `manage.py backup` | Uses SQLite's backup API, unique temporary staging files, snapshot validation, encrypted staged output, cleanup, and retention after successful output creation. Regression tests cover sequential backups and restore safety. | Produces a whole configured-database backup, not a firm-specific backup. Concurrent retention behavior and operational restore drills remain unverified. | Keep current single-database backup for existing deployments; design per-firm backup/restore only after routing and storage boundaries exist, then test concurrent runs and restore on disposable targets. |
| `manage.py restore` | Decrypts/authenticates the input before writing a staged file and atomically replacing the requested destination path. | Restore is path-oriented and not tenant-aware; a successful restore is not a firm-scoped restore workflow. | Validate destination policy, coordinate app shutdown/connection handling, and test firm-specific restore plus rollback after migration. |
| `manage.py importlaws` | Reads a JSONL file and imports batches using `app.conn()`. | Mutates the shared legal corpus in the configured database. | Restrict to controlled platform corpus workflows; keep permission, provenance, review, and verification gates intact. |
| `tools/seed_legal_candidates.py` | Seeds legal-source/document candidate metadata in the database configured through `COPILOT_DB`. | Writes global legal-registry candidates, not firm-owned matters. | Treat as a platform/admin maintenance command; ensure production execution explicitly selects the intended corpus database. |
| `tools/register_labour_law_candidate.py` | Accepts optional `--db`, otherwise uses `COPILOT_DB`/app default, then writes a candidate record. | A command-line path can select which database receives registry data; it is not request input, but operational mistakes could target the wrong file. | Require explicit environment/database confirmation for production corpus writes and log a non-secret target identifier. |
| `tools/audit_legal_corpus.py` | Opens a caller-specified database path read-only for corpus auditing. | Read-only reduces mutation risk but does not itself ensure the selected database contains only authorized data. | Keep access limited to trusted operators and record which database was audited without exposing sensitive paths or content. |
| `tools/legal_source_review_queue.py` | Opens a caller-specified database path read-only for source-review queue reporting. | Same operator/path-selection concern as corpus audit. | Apply the same trusted operational access and target-selection controls. |
| `tools/collect_legal_documents.py` | Downloads documents from a manifest into an output directory (default `legal_corpus`) and appends JSONL collection records; supports size limits and request delay. | Downloaded source files and manifests live outside the application database and may be copied into build/deployment artifacts or shared folders unless operators control them. | Classify corpus artifacts, restrict write/read permissions, keep source-permission checks as hard gates, and document promotion from collection to reviewed corpus. |
| `tools/import_laws.py`, `tools/fetch_arabic_law.py` | Read local law metadata/PDFs or fetch configured sources, perform text extraction/OCR, and write generated rows/reports/output files. | Local source PDFs, OCR cache, generated JSONL, and reports may persist independently of the database. Their actual runtime locations depend on arguments and operator working directory. | Inventory real deployment paths, retention, permissions, provenance, and backup treatment; do not treat OCR output as reviewed law. |
| `tools/deployment_preflight.py` | Checks environment configuration and warns when `COPILOT_DB` is unset or relative. | Preflight validates a single database path, not a tenant catalog or per-firm database mapping. | Replace/extend checks when tenant provisioning exists; fail closed on missing or ambiguous tenant storage configuration. |
| `selftest.py`, `api_test.py`, `arabic_scenario_test.py` | Set temporary `COPILOT_DB` values and exercise app, upload, backup, and restore behavior in test databases. | Test isolation is explicit for these scripts; this does not establish production tenant isolation. | Keep tests on temporary fixtures and add multi-firm storage tests only after the identity/routing contract is approved. |
| `README.md`, `docs/production_deployment_checklist.md` | Recommend a persistent absolute SQLite path, disk/volume protection, encrypted backups, off-host key storage, and daily cron backups. | Documentation describes one database and operator-managed cron; it does not define a tenant-aware backup scheduler or a deployment inventory. | Reconcile docs with the eventual architecture and document who owns scheduled jobs, secrets, logs, retention, and restore drills. |
| GitHub Actions `.github/workflows/tests.yml` | Runs validation/tests, including legal-data tooling and a restore safety test. | These are repository CI jobs; no evidence from this source inspection establishes what external deployment schedules, host cron entries, or cloud jobs exist. | Obtain deployment-owner confirmation and inspect actual hosting configuration before declaring job inventory complete. |

## Uploads, exports, caches, and generated files

- The `POST /cases/{cid}/upload` handler reads a bounded amount of uploaded content, extracts text from supported formats, and persists document metadata/extracted content through the application database flow.
- The reviewed flow does **not** retain original uploaded binaries. Therefore, original-page preview, future re-extraction, and recovery of source files cannot be assumed from the database metadata alone.
- Search found a research `save-to-matter` action and memo-generation helper, but this pass did not establish a complete inventory of every possible export, browser download, reverse-proxy cache, external log sink, or operator-created copy. These remain explicit review items rather than presumed absent.
- No background worker/scheduler was identified in the reviewed `app.py`; the README describes an operator-configured cron backup. Repository inspection cannot enumerate cron/systemd/Kubernetes/cloud schedules or external automation that is not stored here.
- Database, SQLite WAL/SHM files, temporary backup plaintext, encrypted backup files, legal-corpus downloads, OCR caches, generated reports, application logs, and any future original-file storage all need explicit access, encryption, retention, deletion, and backup policies.

## Decisions required before tenant routing

1. **Identity integration:** the working direction is approved: global login identity, globally unique normalized email, many-to-many firm membership, and separate platform/firm roles. Define active-firm selection, session binding/revocation, invitations, account recovery, and audit semantics before runtime integration. A request-supplied `firm_id` or database path must never be trusted as the routing authority.
2. **Data ownership:** finalize which data belongs to the shared legal corpus, control plane, and each firm's database. Mixed `chunks`/FTS search and shared-vs-matter retrieval need a concrete split plan.
3. **File storage:** decide whether originals will be retained; if yes, define firm-scoped object keys/buckets, encryption, access checks, retention, and deletion before implementation.
4. **Operational interfaces:** define provisioning, versioned migrations, per-firm backup/restore, disaster recovery, audit retention, and safe tenant decommissioning.
5. **Deployment inventory:** have the deployment owner enumerate actual hosts, persistent volumes, cron/systemd/container/cloud jobs, reverse-proxy behavior, external logs, secrets, and backup destinations.
6. **Acceptance tests:** use at least two firms and users to test routing, guessed IDs, search/FTS, files, exports, audit records, backup, restore, deletion, and failure/rollback paths.

## Status and limits

- PR #115 introduces a testable SQLite connection-provider boundary and is merged; its CI run passed.
- This inventory records identified repository paths and unresolved operational questions; it does not prove every path or deployment job has been found.
- Shared SQLite remains in use. The approved target architecture and fresh profile-schema foundations do not yet provide runtime identity integration or database-per-firm isolation. Tenant provisioning/routing, firm-specific backup/restore, original-file retention, and independent security review remain incomplete.
