# Multi-firm isolation: implementation plan

## Current state (do not overstate)

The configured fresh-install runtime now supports the separate-database architecture (PR #372): control-plane identity and membership, one SQLite database per firm, and a shared legal corpus. The runtime resolves a selected firm from the authenticated session and server-side membership/catalog, not a client-provided path. Encrypted multi-database backup/restore is implemented (PR #382), and deployment preflight validates separate-path configuration (PR #384). The shared `COPILOT_DB` runtime was retired in PR #972 and is rejected in every environment; it is not a migration/import path and no legacy database has been deployed or used. Route/query isolation coverage, legacy data reconciliation, and recovery/rollback drills are incomplete; this is **not yet production-ready** and has not had an independent security review.

Public registration must remain disabled. Do not onboard unrelated law firms or store their production client data on this implementation.

## Target architecture

Use a small control-plane database only for firm registry and authentication routing. Give each firm its own tenant database file (or managed database/schema with equally strong isolation), its own document storage prefix/bucket, and firm-specific backup/restore and deletion workflows.

The control plane should contain only the minimum needed to authenticate and route: firm ID, firm status, user login identity/password hash or external identity mapping, roles, and session/token metadata. Case/client/document/fee/note/task/session/deadline data must live only in that firm's tenant store.

## Required migration stages

1. **Inventory and baseline:** list every table, endpoint, background job, upload path, export, search query, and admin operation; add regression tests for cross-firm access.
2. **Tenant connection layer:** replace implicit global `conn()` usage with an explicit, authenticated tenant connection. Never trust a client-supplied firm ID to select a tenant. Resolve it from a validated session.
3. **Provisioning:** admin-only creation of a firm, tenant database and storage location with safe defaults. No public self-service registration yet.
4. **Migration:** take a verified backup; copy existing records to one explicitly designated initial firm; preserve IDs and relationships; verify row counts and foreign-key integrity; keep rollback instructions. Never automatically assign real data to a newly created firm.
5. **Storage and search:** store uploaded files per tenant; enforce tenant scope for case-file chunks, indexing, search, answers, backups, restores and cleanup. Shared statutory law content may be global and read-only, with provenance and versioning.
6. **Isolation tests:** create Firm A and Firm B; verify cross-firm reads, writes, list endpoints, IDs, document uploads, search, legal answers, dashboard, conflict checks, user management, backup/restore, and deletion are denied. Test guessed IDs and missing/expired sessions.
7. **Release gate:** run unit/API tests, migration tests and a manual UI check; get an independent security review before production use. Enable public registration only after all release gates pass.

## Operational controls before production

- HTTPS, secure cookie/token policy, CSRF protections where cookies are used, rate limiting, login abuse monitoring, and secure secret management.
- Encrypted disks/backups, documented retention/deletion, tested restore drills, least-privilege operator access, and audit logging without leaking client content.
- Clear disclosure that the service operator/hosting provider processes data; separate databases reduce accidental cross-tenant access but do not by themselves mean the platform operator can never access data.
- Do not claim confidentiality guarantees until architecture and operations have been reviewed.

## Current automated coverage

The detailed route/table boundary inventory and current review findings are maintained in [tenant isolation inventory](tenant_isolation_inventory.md). It records the shared-database limitation, backup/restore gaps, and the policy gap around global legal-review mutations being authorized by the generic firm-admin role.

The API tests now exercise cross-firm case list/detail/update/delete, conflict checks, dashboard tasks, user listings, case search/answer requests, and admin-only user creation. Passing tests cover these cases in the current shared-database model only; they do not prove the target separate-database architecture is implemented.

## Additional regression coverage (SEC-01)

The API test suite now creates a private research conversation with synthetic sentinel content and verifies that:

- the owning user can read its messages;
- another user in the same firm and an administrator in another firm receive 404 for the conversation detail;
- the other firm's conversation list does not include it;
- cross-firm rename, delete, and message attempts are denied;
- saving the owner's answer into a matter belonging to another firm is denied.

These are regression tests for the current shared-database implementation, not proof of independent tenant storage. The target separate-database architecture, exhaustive endpoint inventory, backup/restore isolation, independent security review, and production controls remain outstanding.


## SEC-01 follow-through: extraction-review boundary

The API regression suite now also attempts to use a second firm's administrator session to read an extraction-review audit and submit a correction against a guessed document/chunk ID. Both operations must return 404, and the test confirms the existing reviewed chunk text remains unchanged. This protects against a cross-firm correction path in the shared-database model; it does not replace a full route/table/background-job inventory or prove tenant database separation.


## SEC-01 attack-surface baseline (PR follow-through)

A static scan of `app.py` is recorded in [`sec-01-attack-surface-inventory.md`](sec-01-attack-surface-inventory.md). It lists 45 route decorators and 25 `CREATE TABLE` declarations found by simple source patterns. Treat this as a starting baseline only: reconcile with runtime OpenAPI, migrations/actual schema, indirect SQL and frontend calls; inspect external/deployment jobs and backup/restore paths. No separate tenant database is implemented, and no independent security review has been completed.
