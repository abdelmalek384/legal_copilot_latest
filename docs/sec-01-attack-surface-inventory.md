# SEC-01 attack-surface inventory (historical static baseline)

**Snapshot:** 2026-10-24  
**Status:** Historical snapshot; do not use its old architecture/status statements as current. The current route/tenant findings are in [the tenant-isolation inventory](tenant_isolation_inventory.md), the [database completion tracker](database_completion_tracker.md), and the [repository storage entrypoint inventory](repository_storage_entrypoint_inventory.md).  
**Source:** static scan of `app.py` on `main` after PR #104 merged.  
**Purpose:** preserve the initial attack-surface baseline for audit history. This is an inventory aid, not proof of isolation or a security certification.

## Findings at a glance

- Found **45 FastAPI route decorators** in `app.py`.
- Found **25 SQLite `CREATE TABLE` declarations** plus the `chunks_fts` FTS5 virtual table in `app.py`.
- Static scan found no registered background task framework, scheduler, cron hook, or explicit thread/timer worker in `app.py`. This does **not** prove no jobs exist in deployment scripts, external services, GitHub Actions, or imported modules.
- At this snapshot, the application used a shared SQLite database configured by `COPILOT_DB`. This is historical: the current approved runtime routes through a control plane, per-firm database files, and a shared legal corpus; the legacy compatibility path is rejected in production and is not an approved isolation boundary.
- CI now compares this documented list with registered FastAPI routes and initialized SQLite schema objects through `tests/test_security_surface_inventory.py`. Dynamic routes, indirect SQL, migration-created tables, frontend calls, reverse-proxy paths, and infrastructure jobs still require separate review.

## HTTP route inventory

For every route, review authentication and role checks, tenant derivation from the validated session, guessed-ID behavior (prefer consistent 404s for cross-firm records), write side effects, rate limiting, logging/redaction, and tests. Route presence does not imply that any of these controls are absent; each requires code-level verification.

| Method | Route | Required review |
|---|---|---|
| `GET` | `/` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/manifest.webmanifest` | Public install metadata only; review content integrity and cache policy |
| `GET` | `/service-worker.js` | Public service-worker code; review scope, CSP, update behavior, and cache boundaries |
| `GET` | `/offline.html` | Public static offline notice only; must contain no matter or account data |
| `GET` | `/app-icon.svg` | Public static app icon only; no user-controlled file path |
| `GET` | `/apple-touch-icon.png` | Public fixed PNG home-screen icon decoded from a repository asset; no user-controlled file path |
| `POST` | `/login` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/session` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/logout` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/account/password` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/conflicts` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/legal-review/queue` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/legal-review/coverage` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/legal-review/versions/{version_id}/events` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/legal-review/versions/{version_id}/events` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/users` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/users/{uid}/disable` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/users` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/dashboard` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/cases` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/cases/{cid}` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `PATCH` | `/cases/{cid}` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/members` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `DELETE` | `/cases/{cid}/members/{uid}` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/tasks` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/tasks/{tid}/done` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/sessions` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/notes` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/deadlines` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/deadlines/{did}/done` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/fees` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/docs` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/upload` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/cases/{cid}/docs/{document_id}/reviews` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/cases/{cid}/docs/{document_id}/chunks/{chunk_id}/review` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `DELETE` | `/cases/{cid}` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/audit/case-deletions` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/audit/security-events` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/law/import` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/search` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/ask` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/research/discover` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/research/conversations/{conversation_id}/save-to-matter` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/research/conversations` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/research/conversations` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `GET` | `/research/conversations/{conversation_id}` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `PATCH` | `/research/conversations/{conversation_id}` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `DELETE` | `/research/conversations/{conversation_id}` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |
| `POST` | `/research/conversations/{conversation_id}/messages` | Review authorization, firm scoping, IDOR, rate limits, input validation, and audit behavior |

## Database table inventory

The inventory is the union of the current `control_plane`, `firm`, and `legal_corpus` migration profiles. Names such as `database_profile`, `schema_migrations`, `chunks`, and `chunks_fts` may appear in more than one profile but remain physically separate. The inventory includes the FTS5 virtual table `chunks_fts`; SQLite internal tables and FTS shadow tables are excluded.

The table list below is a schema-review queue. “Needs schema-level review” is deliberately not a finding that a table is vulnerable. For each table, inspect its actual columns, indexes, foreign keys, insert/update/delete paths, firm ownership, and backup/restore/deletion behavior. Shared statutory-law data may be global and read-only only where explicitly intended; firm/client data must be tenant-scoped.

| Table | Schema profile(s) | Required review |
|---|---|---|
| `api_rate_limit_windows` | control_plane | Rate-limit state; confirm retention, key normalization, and cross-process behavior. |
| `auth_sessions` | control_plane | Global authenticated-session state; verify revocation, expiry, and credential-change invalidation. |
| `case_deletion_audit` | firm | Matter-deletion snapshots; enforce tenant/case scope, immutable audit behavior, and retention. |
| `cases` | firm | Confidential matter records; enforce firm/case ownership and safe export/deletion behavior. |
| `chunks` | firm, legal_corpus | Physically separate matter extraction from legal-reference text; verify FTS and access boundaries. |
| `chunks_fts` | firm, legal_corpus | Profile-local FTS5 indexes; verify synchronization, rebuild, and integrity checks. |
| `database_profile` | control_plane, firm, legal_corpus | Immutable profile marker; startup and migration preflight must reject missing or altered guards. |
| `deadlines` | firm | Matter deadlines; enforce case membership, tenant scope, and reminder lifecycle rules. |
| `docs` | firm | Document metadata and extraction state; enforce case linkage and atomic audit persistence. |
| `document_extraction_reviews` | firm | Append-only extraction review history; enforce case/document/chunk binding and integrity. |
| `events` | firm | Matter event history; enforce case scope, audit atomicity, and retention. |
| `fees` | firm | Financial matter data; enforce case membership and aggregate isolation. |
| `firm_memberships` | control_plane | Global identity-to-firm access grants; audit creation, suspension, and revocation. |
| `firms` | control_plane | Tenant lifecycle state; enforce provisioning, disablement, and recovery transitions. |
| `identity_invitations` | control_plane | Single-use firm-scoped invitations; enforce expiry, revocation, and audit behavior. |
| `identity_lifecycle_events` | control_plane | Identity and membership lifecycle audit; protect integrity and limit sensitive details. |
| `legal_document_versions` | legal_corpus | Versioned legal sources; require review evidence before verified/current status. |
| `legal_documents` | legal_corpus | Global legal-source registry metadata; respect source permissions and licensing decisions. |
| `legal_import_staging` | legal_corpus | Unverified import staging; ensure staged passages are not searchable as verified law. |
| `legal_review_events` | legal_corpus | Global legal-review evidence; require platform roles and atomic writes. |
| `legal_sources` | legal_corpus | Source provenance and reuse permissions; preserve reviewed licensing decisions. |
| `legal_version_relations` | legal_corpus | Version relationship metadata; validate relation endpoints and provenance. |
| `login_attempts` | control_plane | Authentication throttling state; validate normalized-email and distributed rate limits. |
| `members` | firm | Case membership; enforce row-scope guards and atomic task reassignment on member removal. |
| `mfa_credentials` | control_plane | Authenticator secrets and state; protect encryption, re-enrollment, and revocation. |
| `mfa_recovery_codes` | control_plane | Single-use recovery-code hashes; never store plaintext codes. |
| `mfa_security_events` | control_plane | MFA security history; enforce append-only audit and safe access. |
| `notes` | firm | Matter notes; enforce case membership and atomic audit writes. |
| `original_file_deletion_events` | firm | Original-file deletion audit; preserve append-only lifecycle evidence. |
| `original_file_deletion_requests` | firm | Original-file deletion workflow; require authorization, legal-hold checks, and atomic approvals. |
| `original_file_hold_events` | firm | Legal-hold event ledger; preserve immutable hold/release evidence. |
| `original_file_objects` | firm | Opaque original-file references and lifecycle state; validate object integrity and tenant binding. |
| `password_recovery_tokens` | control_plane | Hashed, single-use recovery tokens; enforce expiry and session revocation. |
| `platform_security_events` | control_plane | Privileged platform security audit; ensure atomic writes and restricted access. |
| `reminder_deliveries` | firm | Durable reminder outbox; prevent duplicate sends and suppress disabled accounts/firms. |
| `reminder_delivery_attempts` | firm | Reminder delivery attempt history; ensure safe retry and audit behavior. |
| `research_conversations` | firm | User-owned research conversations; enforce owner and firm scope. |
| `research_messages` | firm | Research messages and answer payloads; enforce conversation ownership and safe retention. |
| `schema_migrations` | control_plane, firm, legal_corpus | Immutable migration ledger; verify checksums, ordering, and missing applied files. |
| `security_audit_events` | firm | Firm-scoped security audit exports; enforce admin access and CSV formula neutralization. |
| `sessions` | firm | Matter/session data; verify scope, lifecycle, and retention. |
| `tasks` | firm | Matter task state; enforce case membership and prevent dashboard/calendar disclosure. |
| `tenant_database_binding` | firm | Immutable firm ID binding; require database-level update/delete guards. |
| `tenant_database_catalog` | control_plane | Trusted database filename and lifecycle catalog; reject orphan rows/files and binding mismatch. |
| `user_platform_roles` | control_plane | Privileged platform roles; enforce explicit grant governance, revocation, and audit. |
| `users` | control_plane | Global identities and credentials; enforce canonical email uniqueness, MFA, disablement, and recovery. |
## Cross-cutting surfaces not fully represented by route decorators

- **Document upload and extraction:** `POST /cases/{cid}/upload`, document metadata, chunks, extraction-review audit, correction writes, temporary buffers, file retention and cleanup.
- **Research and search:** `POST /search`, `POST /ask`, `POST /research/discover`, conversation/message CRUD and save-to-matter; inspect every query joining chunks, legal sources, conversations and cases.
- **Legal corpus/admin operations:** legal import, source/document/version/relation/review-event tables, permission gates and admin credentials.
- **Exports and generated artifacts:** inspect source-inspector memo export/save, downloads, generated files and any route that serializes matter or client content. Static route scan alone cannot establish all export paths.
- **Authentication/session:** login attempts, sessions, password change, disabled users, cookie/token lifecycle, session expiry/revocation and concurrent login behavior.
- **Audit/security events:** ensure audit endpoints are role-gated, events are firm-scoped where appropriate, and logs never expose client text, secrets or authentication material.
- **Storage and operations:** database files, uploaded binary storage (currently binaries are not retained by the ingestion flow), temp files, deployment volumes, backups, restore tooling, deletion, logs and operator access.
- **External/background execution:** review GitHub Actions workflows, deployment platform jobs, shell scripts, imported modules and any future queue/worker before declaring the background-job inventory complete.

## Status and next actions

| Work item | Status | Exit evidence |
|---|---|---|
| Route decorator baseline | Initial static list generated | Reconcile with OpenAPI at runtime and frontend/network calls |
| SQLite table baseline | Initial `CREATE TABLE` list generated | Reconcile with actual database schema and all migrations |
| Per-route authorization / tenant review | Outstanding | Reviewer records findings and links tests for every route |
| Query and table ownership map | Outstanding | Every sensitive table has documented owner/tenant key or approved global-data rationale |
| Background job / deployment surface | Partial only | Inspect workflows, deployment scripts, external services and imported modules |
| Backup/restore isolation tests | Outstanding | Restore one tenant's backup without exposing or overwriting another tenant |
| Independent security review | Outstanding | Written review with remediation and release decision |

## Safety and release gate

Do not enable public registration or use unrelated firms' production client data until the endpoint/query inventory is reconciled, tenant storage architecture is implemented, cross-tenant tests cover reads and writes, backup/restore and deletion are tested, and an independent reviewer signs off. Passing tests on the shared database are useful regression evidence but are not proof of tenant database separation.
