# DB-06 — initial isolated profile schemas

**Status:** Initial versioned schema proposal; not wired to application runtime or production provisioning.

This change adds one first migration for each allowlisted profile and acceptance tests proving each can initialize in an empty SQLite database independently.

## Profile ownership implemented

- **Control plane:** firms lifecycle metadata, tenant_database_catalog, global user identities with a globally unique canonical email key, many-to-many firm memberships with firm-scoped roles/status, and a separate platform-role assignment table. The initial identity schema is fresh-database infrastructure only; it is not wired into application login/session handling and does not migrate legacy users. Auth-session storage and security-event retention remain separate design gates.
- **Firm:** case/matter tables, child records, document metadata, extraction review records, research conversations/messages, matter chunks and a firm-local FTS5 index. Case-child rows use foreign keys and cascade on case deletion. The database is assumed to have already been selected by trusted server-side tenant resolution.
- **Legal corpus:** source, document, version, relation, review-event, corpus-chunk provenance, and corpus-local FTS5 index. Each corpus chunk must reference a legal document version.

## Safety properties and limits

- Migrations are checksum tracked by the versioned runner.
- No migration copies or deletes legacy data. These are fresh-schema foundations only.
- The control-plane identity/membership tables now encode the approved direction for fresh databases. Runtime authentication, session revocation, invitations, identity/legacy ownership reconciliation, and cross-database references remain unimplemented; no migration copies or deletes legacy data.
- This does not switch app.py, authenticate firm context, route requests, split existing chunks_fts, or make the current mixed database safe for multi-firm production.
- FTS triggers are tested for insert/update/delete. Production ingestion and delete paths still require integration tests.
- Schema parity with every legacy query/write call site remains unverified.
- Before runtime use: review all call sites, decide audit retention, implement trusted routing, verify tenant lifecycle/session semantics, test sentinel isolation end-to-end, and rehearse data migration/rollback against a protected copy.
