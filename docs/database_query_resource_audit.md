# SEC-01: database query and resource audit (initial static pass)

**Status:** Initial repository-code audit; not an exhaustive runtime/deployment audit, security certification, or proof of tenant isolation.  
**Reviewed:** `app.py`, `storage.py`, `manage.py`, and the current SEC-01 architecture/ownership documents on `main`.  
**Purpose:** Turn the known storage inventory into concrete findings and safe implementation gates.

**Current-state note (2026-10-26):** This file preserves the initial, pre-separation static baseline. The findings and remediation text below describe that earlier state and are not a claim about the current runtime. Since then, the separate control-plane / per-firm database / shared-corpus runtime, versioned profile migrations, immutable firm binding, encrypted multi-database backup/restore, and extensive cross-firm regression tests have been merged. Current execution status is tracked in `docs/database_completion_tracker.md` and `docs/tenant_isolation_inventory.md`. Remaining release blockers include exhaustive route/query review, live original-upload object storage and retention, invitation/account-recovery and platform-role grant governance, a witnessed staging restore/rollback drill, and independent security review. No legacy database has been deployed or used; reconciliation is conditional future work only if an external database is explicitly introduced and approved for import.

## Executive finding

The application still opens one SQLite file selected by `COPILOT_DB` (default `copilot.db`). `SQLiteConnectionProvider` provides one connection per thread for that one configured path; it does not resolve an authenticated tenant or choose a database. A separate-firm production deployment is therefore **not ready**.

The schema has some firm-aware checks at the application layer, but not a consistent database boundary: several matter tables have no `firm_id` and rely on joining through `cases`; shared legal corpus rows and matter rows coexist in `chunks` and `chunks_fts`; identity and tenant ownership decisions are unresolved.

## Confirmed findings

### P0 — do not onboard unrelated firms to the current shared database

1. **One database path for all users.** `app.py` sets `DB = os.environ.get("COPILOT_DB", "copilot.db")`; `conn()` initializes one configured SQLite schema. `storage.py`'s provider takes a single path and has no tenant selector.
2. **Firm assignment defaults can silently assign new records to firm 1.** The fresh startup schema defines `users.firm_id` and `cases.firm_id` with `DEFAULT 1`, so any writer that omits firm ownership can silently attach a new record to firm 1. The current legacy-ownership helper quarantines rows whose firm is NULL; it does not update those NULL rows to firm 1. Before tenant rollout, remove implicit defaults through a reviewed forward-compatible schema change and require an explicit trusted firm context for new records. The CLI account-creation path also omits `firm_id`; changing that onboarding behavior depends on the approved initial-firm-owner/bootstrap policy.
3. **Mixed search index.** `chunks` contains both matter-scoped rows (`case_id` set) and shared legal corpus rows (`case_id IS NULL)); `chunks_fts` indexes both. Query filters exist in the search path, but physical/index separation and complete route/background-job verification are not established.
4. **Ownership is application-enforced and distributed.** Case access checks compare the case's `firm_id` with the user's current `firm_id` and then check membership/role. Multiple endpoints perform their own SQL and must continue to be covered by cross-firm tests. A new route or background worker could bypass a check.

### P1 — schema and operational migration risks

5. **Matter child tables do not carry a tenant key.** `notes`, `deadlines`, `fees`, `members`, `tasks`, `events`, and case `sessions` are associated through `case_id`; access relies on verifying the parent case before returning or mutating children. Tenant-scoped database migration must preserve these relationships and test orphan detection.
6. **Legacy identity is still single-firm at runtime; the approved target schema is not runtime-integrated.** The current application schema has a globally unique `users.email` and one `firm_id` per user. The fresh control-plane profile now defines globally normalized email identities, many-to-many `firm_memberships`, and separate `user_platform_roles` (PR #253 merged). It does not migrate legacy users or change login/session behavior. Do not infer or merge legacy memberships without authoritative evidence and explicit approval.
7. **Security audit data has mixed scope.** `security_audit_events` stores a required `firm_id` and user ID; the taxonomy does not yet formally distinguish firm audit events from platform/control-plane events. `case_deletion_audit` includes sensitive case snapshots and must remain firm-scoped and tightly access-controlled.
8. **Backup is whole-database, not firm-specific.** `manage.py backup` uses unique temporary staging files, validates the SQLite snapshot, encrypts to a staged output, and applies retention after a completed backup; `tests/test_backup_restore_safety.py` covers sequential backups and restore failure safety. It still backs up only the single configured database, not an individual firm. Concurrent backup/retention behavior, per-firm backup/restore, and an operator-run restore drill remain unverified.
9. **Original uploaded binaries are not retained by the current upload flow.** The `docs` row records metadata/hash and extracted chunks, not a recoverable original file object. Historical original-file recovery/re-extraction cannot be promised; future object storage needs tenant-scoped paths, retention, encryption and restore coverage.
10. **Schema changes run at application startup.** `conn()` runs `CREATE TABLE` and conditional `ALTER TABLE` operations guarded by an in-process flag. This is not a versioned, per-tenant migration system and is not sufficient for a controlled multi-database rollout.

## Historical remediation note (baseline-era; not current branch status)

The SEC-01 ownership-hardening change in the current working branch removes the startup updates that silently set NULL user/case ownership to firm 1. When an older schema lacks the ownership columns, it adds nullable columns without a default and records rows whose ownership remains NULL in `tenant_ownership_quarantine`. Login is denied and existing sessions are invalidated for accounts with NULL firm ownership. The quarantine is a review ledger, not an automatic repair mechanism.

Important limits:
- This does not identify or reverse records that a prior application version already assigned to firm 1.
- It does not create database-per-firm routing, partition mixed legal/matter search, or prove tenant isolation.
- Operators must inspect a protected copy, reconcile rows from authoritative evidence, and approve any ownership assignment. Do not automatically map every quarantined row to the first firm.
- Existing schema columns that already have a DEFAULT 1 are not rewritten by SQLite; this change does not establish the provenance of such values.

## Endpoint families reviewed

The static route pass found the following database-facing families in `app.py`:

- Authentication/account: `/login`, `/session`, `/logout`, `/account/password`, `/users`, `/users/{uid}/disable`.
- Firm/matter workspace: `/dashboard`, `/conflicts`, `/cases`, `/cases/{cid}`, case members/tasks/sessions/notes/deadlines/fees/docs/upload, task/deadline completion, case deletion.
- Auditing: `/audit/case-deletions`, `/audit/security-events`.
- Shared corpus/review: `/law/import`, `/legal-review/queue`, `/legal-review/coverage`, legal-review version event reads/writes.
- Search/research: `/search`, `/ask`, `/research/discover`, research conversations/messages, save-to-matter.
- Extraction review: document review list and chunk review/correction endpoints.

This is a source-code route inventory only. It does not include every SQL statement in tests/scripts, deployment configuration, externally scheduled jobs, production cloud storage, or runtime-generated paths.

## Data ownership map (candidate, pending owner approval)

| Resource | Candidate ownership | Required boundary |
|---|---|---|
| `firms` | Trusted tenant catalog/control plane | Provisioning authority; no client-controlled tenant selection |
| `users`, `firm_memberships`, platform-role assignments, `auth_sessions`, `login_attempts` | Control plane (approved target; runtime integration incomplete) | Global canonical email key and multi-firm membership; define session/revocation and audit-retention semantics; reconcile legacy users only with evidence and approval |
| `cases` and children (`notes`, `deadlines`, `fees`, `members`, `tasks`, `events`, case `sessions`) | Firm-owned | Parent/child integrity, membership checks, no orphan or cross-firm references |
| `docs`, `document_extraction_reviews`, matter `chunks` | Firm-owned | Firm-scoped original-object storage; tenant-aware search and retention |
| `research_conversations`, `research_messages` | Firm-owned plus user ownership | Enforce both firm and owner; delete/save-to-matter checks |
| `legal_sources`, `legal_documents`, `legal_document_versions`, `legal_version_relations`, `legal_review_events` | Shared legal corpus/control plane | Platform reviewer authorization, separate corpus lifecycle and permission controls |
| `chunks` with `case_id IS NULL`, `chunks_fts` | Shared corpus/index partition | Design and test physical/logical separation; do not assume shared FTS is tenant isolation |
| `security_audit_events` | Needs firm/platform split policy | Define event taxonomy, retention, access and cross-firm visibility |
| `case_deletion_audit` | Firm-owned sensitive audit | Firm-filtered reads, access policy, retention and restore tests |
| `api_rate_limit_windows` | Operational/security store | Confirm whether limits are per user, IP, firm or global; avoid tenant-key collisions |
| Backup files, restore staging, logs, OCR outputs, exports, temporary files | Deployment-dependent | Inventory actual runtime locations and assign encryption, access, retention and deletion policy |

## Original baseline follow-up checklist (historical; use the current tracker for execution)

1. Implement the approved global-identity / many-to-many membership direction in fresh control-plane schemas, then define session revocation, invitation, recovery, and audit-retention semantics before wiring runtime authentication. Keep legacy identity reconciliation separately approval-gated.
2. Inventory real deployment configuration, containers/volumes, environment variables, scheduled jobs, external workers, file/object storage, logs, exports and backup destinations.
3. Search every SQL query and data-writing script; classify each read/write by resource owner and tenant authorization source. Add a test inventory so new endpoints must declare their scope.
4. Define how to classify every existing user, case, document, chunk and child row. Quarantine ambiguous/orphaned records; do not silently assign them to Firm 1.
5. Decide physical partitioning of shared corpus and matter indexes; define integrity checks for cross-firm child references and FTS rows.
6. Build a versioned dry-run migration with row counts, foreign-key checks, hashes, reconciliation reports, deterministic reruns, rollback and restore rehearsal.
7. Implement trusted tenant provisioning/routing only after the above decisions. Add adversarial tests for every endpoint family, including direct object IDs, bulk/search paths, research messages, document review, exports and background jobs.
8. Require independent security review and restore/incident rehearsal before production use by unrelated firms.

## Original baseline acceptance checklist (historical)

- [ ] Product owner approves identity and membership model.
- [ ] Deployment and external-job inventory is verified by the deployment owner.
- [ ] SQL and file/object resource inventory is exhaustive and reviewed.
- [ ] Ambiguous/orphaned rows are quarantined with reconciliation evidence.
- [ ] Tenant routing cannot be selected or overridden by client input.
- [ ] Cross-firm tests cover every route family and worker.
- [ ] Shared legal corpus and full-text indexes have a documented, tested boundary.
- [ ] Firm-specific backup/restore, migration rollback and recovery are rehearsed.
- [ ] Independent security review findings are resolved or formally accepted.

**Status remains IN PROGRESS.** This document records a static code pass and implementation gates; it does not claim runtime verification, complete coverage, or a security certification.
