# Multi-firm isolation: implementation plan

## Current state (do not overstate)

The application currently uses one SQLite database configured by `COPILOT_DB`. Users and cases have a `firm_id`, and selected queries enforce firm scope. Related records such as notes, documents, fees, sessions, deadlines and tasks are stored in the same database and mostly relate to cases by ID. This is useful row-level isolation, but it is **not** a separate database per firm and has not had an independent security review.

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

The API tests now exercise cross-firm case list/detail/update/delete, conflict checks, dashboard tasks, user listings, case search/answer requests, and admin-only user creation. Passing tests cover these cases in the current shared-database model only; they do not prove the target separate-database architecture is implemented.
