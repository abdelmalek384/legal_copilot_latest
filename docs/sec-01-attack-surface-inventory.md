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

The inventory includes the FTS5 virtual table `chunks_fts`; SQLite's internal FTS shadow tables are implementation details and are excluded from the application-owned object list.

The table list below is a schema-review queue. “Needs schema-level review” is deliberately not a finding that a table is vulnerable. For each table, inspect its actual columns, indexes, foreign keys, insert/update/delete paths, firm ownership, and backup/restore/deletion behavior. Shared statutory-law data may be global and read-only only where explicitly intended; firm/client data must be tenant-scoped.

| Table | Initial status | Required review |
|---|---|---|
| `chunks_fts` | Virtual table | FTS5 search index over normalized chunk text; inspect index rebuild and consistency behavior |
| `chunks` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `firms` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `users` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `auth_sessions` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `security_audit_events` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `login_attempts` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `cases` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `notes` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `deadlines` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `fees` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `members` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `tasks` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `events` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `case_deletion_audit` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `api_rate_limit_windows` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `sessions` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `docs` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `legal_sources` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `legal_documents` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `legal_document_versions` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `legal_version_relations` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `legal_review_events` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `research_conversations` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `research_messages` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |
| `document_extraction_reviews` | Needs schema-level review | Confirm firm ownership / global-law status, foreign keys, access paths, retention and backup treatment |

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
