# DB-06 — initial isolated profile schemas

**Status:** Versioned profile schemas are wired into the separate-database runtime and firm provisioning. Clean-install and restart tests pass; production deployment and operational acceptance remain incomplete.

Each allowlisted profile initializes through its own versioned migration directory. The current runtime uses a control-plane database for global identities/memberships/catalog, a separate SQLite database per firm, and one shared legal-corpus database. No production database has been deployed; legacy shared-database compatibility is not an approved multi-firm isolation boundary.

## Profile ownership implemented

- **Control plane:** firm lifecycle metadata, tenant_database_catalog, global user identities with a globally unique canonical email key, many-to-many firm memberships with firm-scoped roles/status, platform-role assignments, and control-plane session/authentication state. Runtime authentication and membership checks use this control plane; platform roles are checked live for platform-protected operations. Invitation/account recovery policy, platform-role grant governance, and audit/retention decisions remain open.
- **Firm:** case/matter tables, child records, document metadata, extraction review records, research conversations/messages, matter chunks and a firm-local FTS5 index. The runtime selects this database only after resolving an authenticated identity's active membership through the trusted catalog. Provisioning adds an immutable tenant_database_binding after profile migrations; database triggers enforce the bound firm ID on protected inserts/updates.
- **Legal corpus:** source, document, version, relation, review-event, import-staging, corpus-chunk provenance, and corpus-local FTS5 index. Each corpus chunk must reference a legal document version. Corpus administration requires a current platform reviewer/admin role; firm roles alone do not grant this permission.

## Safety properties and remaining limits

- Migrations are checksum tracked by the versioned runner. Migration files are immutable after merge; corrections require forward migrations.
- Clean profile migration tests verify disjoint ownership tables, foreign-key/integrity checks, FTS insert/update/delete synchronization, two-firm search separation, corpus provenance, and database-bound firm row-scope guards.
- Separate-runtime integration tests cover cross-firm case reads/updates/deletes, child writes, document and extraction-review paths, research conversations, search/ask, conflict checks, dashboard/calendar/finance, audit exports, membership administration, and live platform-role revocation. Coverage is growing but is not yet exhaustive for every route, SQL query, export, or background path.
- Encrypted multi-database backup and non-destructive restore are implemented. A coordinated snapshot requires all application writers to remain paused; the operator runbook is in docs/database_recovery_runbook.md. A witnessed recovery drill and deployment-specific acceptance have not yet been completed.
- No migration copies, deletes, or automatically reassigns legacy rows. The older shared-schema startup/compatibility path has been retired; application startup rejects `COPILOT_DB` in every environment. Strict deployment preflight requires the three separate paths and rejects any `COPILOT_DB` setting.
- Because no production database is deployed, production legacy-row reconciliation and cutover are not first-deployment tasks. If a legacy database is deliberately introduced for import later, run the read-only ownership/FTS preflights, classify anomalies from trusted evidence, quarantine unresolved rows, and rehearse the import/rollback before accepting the data.

## Remaining acceptance gates

1. Complete route-by-route and query-by-query tenant isolation review, including background work and administrative operations.
2. Resolve the still-open invitation, account-recovery, platform-role governance, session/audit retention, and bootstrap policy decisions before implementing those workflows.
3. Run and record a representative encrypted backup/restore drill, including startup, tenant-isolation, corpus-search, and rollback acceptance on a staging copy.
4. Complete deployment-specific operational controls and independent security review before using confidential matter data for unrelated firms.
