# SEC-01 — Phase 0 database and storage boundary review

**Review date:** 2026-10-24  
**Reviewed source:** `app.py` on `main` (1,717 lines), `api_test.py` (631 lines), and `docs/tenant_isolation_inventory.md`.  
**Review type:** static source inspection and initial SQL-bearing-statement scan. This is not a complete formal query audit, a penetration test, or production certification.

## Finding

The application opens one SQLite database path from `COPILOT_DB` (default `copilot.db`) and initializes the full schema in that database. The connection helper creates a thread-local connection, but it does not select a database based on the authenticated firm's trusted server-side identity. Firm filters in individual routes are application-level controls; they do not provide database-level tenant separation.

**No firm-database migration is performed by this review.** Do not point multiple unrelated firms at the same production database on the assumption that the current filters are equivalent to isolation.

## Current storage entry points

| Entry point | Current behavior | Migration requirement |
|---|---|---|
| `DB = os.environ.get("COPILOT_DB", "copilot.db")` | One process-wide database path | Replace the single global path with a trusted tenant-aware database/session provider; never accept a tenant database path from request input |
| `conn()` | Thread-local SQLite connection; creates/migrates the shared schema once per process | Make connection acquisition explicit about trusted tenant context; define lifecycle, transaction, pooling, error and migration behavior before switching adapters |
| `SCHEMA` and inline startup migrations | Shared schema creation and `ALTER TABLE` operations run during connection initialization | Move migrations into versioned, repeatable migration tooling; do not run a tenant migration implicitly on an arbitrary request |
| `chunks` plus `chunks_fts` | Mixes global legal-corpus passages (`case_id IS NULL`) and firm matter chunks (`case_id` set) in the same database and search index | Separate shared legal corpus from firm-owned chunks/indexes, or prove a different explicit isolation design; preserve index-to-row consistency |
| `docs` metadata | Firm/case-linked metadata, including hash and extraction status; original upload binaries are not retained by the current reviewed flow | Design firm-scoped object storage and retention before claiming recoverable originals or page previews |
| `research_conversations` and `research_messages` | Conversations have user and firm IDs in the shared database; messages inherit scope through their parent conversation | Keep parent ownership checks and ensure every read/export/delete path resolves the parent under trusted tenant context |
| `legal_sources`, `legal_documents`, `legal_document_versions`, `legal_version_relations`, `legal_review_events` | Shared legal registry in the same database | Keep the corpus separately governed and read-only for normal firm workflows; restrict mutations to platform reviewers |
| `auth_sessions`, `login_attempts`, `api_rate_limit_windows`, `security_audit_events` | Session, login-throttle, rate-limit, and audit records in shared storage | Decide explicitly which belong to a control plane and which are firm-scoped; preserve global identity/session revocation semantics if a user can belong to multiple firms |
| `case_deletion_audit` | Firm-tagged deletion snapshots in shared storage | Keep snapshots in the same firm security boundary as the matter, with tested retention and firm-specific restore/deletion behavior |

## Data classification for target architecture

### Firm-owned data — candidate for each firm's database

- `cases`, `members`, `tasks`, `events`, `notes`, `deadlines`, `fees`, `sessions`
- `docs` metadata and `document_extraction_reviews`
- Matter-linked `chunks` and any matter-specific search indexes
- `research_conversations` and `research_messages`
- `case_deletion_audit` and firm-scoped `security_audit_events`

These are candidate classifications, not a completed migration mapping. Foreign keys and joins, audit retention, account membership, and any export path must be verified before moving them.

### Shared/control-plane candidates — must not be copied blindly into every firm database

- Shared legal registry: `legal_sources`, `legal_documents`, `legal_document_versions`, `legal_version_relations`, `legal_review_events`, plus shared legal `chunks` and FTS index.
- Firm catalog and lifecycle: `firms`, tenant provisioning status, database location/secret references, and migration version state.
- Identity and security infrastructure: `users`, `auth_sessions`, `login_attempts`, `api_rate_limit_windows`. Their final location depends on whether identities are global or firm-specific; do not decide this solely from current schema.
- Platform-level reviewer identity/allowlist configuration and its audit trail.

## Query-boundary observations to carry into the next code phase

1. **Application checks remain important during migration.** Helpers such as `need(...)` and `need_lead(...)`, firm-filtered list queries, and checks on document/research parent rows must remain enforced. Database-per-firm is defense in depth, not permission to remove object-level authorization.
2. **Some child-table statements are scoped by a prior parent check rather than by a firm predicate in every SQL statement.** Examples include case detail child queries and task completion after resolving the task's case. The migration review must prove the parent authorization check and mutation occur safely in the same transaction or that concurrent changes cannot invalidate the authorization decision.
3. **Audit data is sensitive.** Deletion snapshots and security events require firm-specific read, retention, export, backup, and restore behavior. An audit row's `firm_id` alone does not prove every read path is safe.
4. **The legal search corpus is mixed.** The search SQL intentionally allows shared rows where `case_id IS NULL` and firm rows linked to cases belonging to the current firm. That query/index design cannot be mechanically copied into a firm database without separating global and matter-scoped retrieval.
5. **Account/session semantics are unresolved for multi-firm users.** Moving `users` or `auth_sessions` into per-firm stores changes login, password reset, disablement, and revocation behavior. Define the identity model before migration.
6. **File/object storage is not yet a separate subsystem.** The reviewed upload path records metadata/hash and extraction state; original binaries are not retained. Database migration alone cannot add original-file recovery, secure previews, or firm-scoped file retention.
7. **Background jobs and external integrations need re-inventory.** The reviewed `app.py` did not expose a separate worker implementation, but deployment schedules, scripts, backups, maintenance commands, caches, and future jobs still require a repository/deployment-wide check.
8. **Startup schema changes are not a tenant migration strategy.** Per-firm databases need versioned migrations, migration locking, per-tenant status reporting, retries, and a tested rollback/recovery plan.



## Repository-wide database and operations entry points found

A follow-up GitHub code search identified these non-route entry points. They are in scope for Phase 0 because a future tenant-aware web connection helper will not automatically make command-line tools, maintenance scripts, or backups tenant-safe.

| Path | Observed database behavior | Required follow-up |
|---|---|---|
| `manage.py` | `adduser`, `resetpw`, `importlaws`, and `backup` call `app.conn()`; backup exports the entire current database to one encrypted file. Restore decrypts a backup and replaces a caller-selected output path. | Define explicit control-plane vs tenant-admin commands; implement firm-scoped backup/restore and restore validation; ensure account operations target the intended firm and cannot silently default to firm 1 in a multi-tenant deployment. |
| `tools/seed_legal_candidates.py` | Imports `app` and calls `app.conn()` to write shared legal-registry metadata. | Route registry writes through an explicitly selected platform/shared-corpus store, with a safe dry-run and permission controls. |
| `tools/register_labour_law_candidate.py` | Accepts an optional `--db` path by setting `COPILOT_DB`, then uses the app connection to write shared legal registry metadata and review events. | Make target-store selection explicit; do not let a tenant DB path be mistaken for the shared legal registry. |
| `tools/audit_legal_corpus.py`, `tools/legal_source_review_queue.py` | Open a caller-specified SQLite file in read-only mode and inspect corpus tables. | Keep read-only behavior; validate that operators point to the intended shared-corpus store and label reports with clear scope. |
| `tools/deployment_preflight.py` | Checks the configured `COPILOT_DB` path, permissions, and deployment environment; it does not provision a tenant or establish isolation. | Extend preflight for tenant catalog/connection configuration and require explicit production topology, while retaining the current shared-SQLite warning until migration is complete. |
| `selftest.py`, `tests/test_security_surface_inventory.py`, and scenario tests | Set `COPILOT_DB` to temporary paths before importing `app`; these exercise the current single-store model. | Add isolated-store and tenant-routing tests when the storage interface is introduced; avoid shared temp filenames that can collide between concurrent CI runs. |
| `docs/production_deployment_checklist.md`, `README.md`, `docs/multi-firm-isolation-plan.md` | Document one configured database path and encrypted whole-database backups; the multi-firm plan already states that separate tenant stores are not implemented. | Keep docs consistent after the architecture changes; never present path hardening or encrypted backup as tenant isolation. |

The initial code search did not find a cache/Redis integration or a registered scheduler in `app.py`. That is not proof that deployment automation, shell scripts, external services, or imported modules have no such behavior; those still require direct inspection. The repository's existing attack-surface inventory also notes that route/schema drift checks do not cover dynamic routes, indirect SQL, frontend calls, reverse-proxy paths, or infrastructure jobs.

## Required Phase 0 completion checklist

- [ ] Enumerate every SQL statement by route/helper and mark it firm-owned, control-plane, shared-corpus, or mixed.
- [ ] Verify every read, mutation, export, audit query, and delete path against trusted tenant context; record the parent authorization guard and transaction boundary.
- [ ] Search the whole repository for `COPILOT_DB`, `sqlite3.connect`, database file paths, raw SQL, upload destinations, temporary files, exports, caches, scheduled jobs, and backup/restore scripts.
- [ ] Decide whether user identity is global or firm-specific, including cross-firm memberships, password changes, disablement, and session revocation.
- [ ] Define shared legal-corpus serving and cache/index invalidation without allowing firm matter content to enter shared indexes.
- [ ] Define firm-scoped file/object storage, export destinations, backups, retention and deletion.
- [ ] Write an explicit old-to-new table/resource mapping, including mixed tables and orphan/unknown rows.
- [ ] Specify migration verification: source/destination row counts, stable per-table hashes where feasible, foreign-key checks, sample retrieval checks, tenant leakage tests, and rollback criteria.

## Exit criteria before database adapter implementation

Phase 0 is complete only when the SQL/resource inventory has been checked against the full repository and deployment setup, identity semantics and shared-corpus boundaries are decided, and the table/file mapping is reviewed. The next implementation step should be a small, testable storage/connection interface with no behavior change, followed by tests that prove tenant selection is server-controlled. Do not begin a bulk migration until that interface and the migration plan are reviewed.

## Explicit non-claims

- This review does not mean the database problem is fixed.
- The current SQLite database is still shared.
- The proposed database-per-firm architecture is not implemented.
- The scan is not an exhaustive independent security audit and does not establish production readiness.
