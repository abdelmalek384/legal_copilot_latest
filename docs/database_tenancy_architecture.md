# SEC-01 — Database tenancy architecture decision

**Status:** Proposed; implementation and migration are not complete  
**Date:** 2026-10-24  
**Scope:** firm-owned matter data, uploaded documents, research history, audit records, backups, and shared legal-reference content

## Executive decision

Move away from one shared SQLite file as the production multi-firm storage boundary. The target should be a **shared application tier with a database per firm**, backed by a trusted tenant catalog. Keep the shared legal-reference corpus as a separate, controlled service/store with read-only access for normal firm requests. Store uploaded files and derived artifacts in firm-scoped storage locations with independent authorization and retention rules.

This is a proposed target, not a statement that the system already implements it. The current application still uses one SQLite database and relies substantially on application-level firm filtering. Do not use this proposal as production-readiness evidence.

## Why this model

Microsoft's SaaS tenancy guidance describes database-per-tenant as providing strong data isolation and simpler tenant-level restore, while noting the additional provisioning and operations work. A single shared database is lower cost but depends on every query correctly enforcing tenant scope, and per-tenant restore is more complex. See [Microsoft's SaaS tenancy patterns](https://learn.microsoft.com/en-us/azure/azure-sql/database/saas-tenancy-app-design-patterns).

ZKBioTime's official product page lists PostgreSQL as its default database and also lists Microsoft SQL Server, MySQL, and Oracle options. This is a useful deployment/database-operations reference, but the public product page does **not** establish that ZKBioTime uses database-per-customer isolation. We should not infer its tenant model from its supported database engines. See [ZKBioTime's official specifications](https://www.zkteco.com/en/ZKBio_Time/ZKBioTime).

Legal practice-management vendors also describe controls such as encryption in transit and at rest and restricted production access; those controls complement, but do not replace, tenant separation and authorization. See [Clio's compliance overview](https://help.clio.com/hc/en-us/articles/9284651312411-Compliance).

## Target logical architecture

Browser / API client → shared Legal Copilot application → authentication and trusted tenant resolver → tenant catalog mapping firm identity to a server-side database reference → one firm database per firm.

The firm database holds cases, clients, notes, deadlines, fees, members/tasks, firm-scoped research history, audit events, and document metadata/review corrections. Firm-scoped object/file storage holds original uploads, extracted text, previews, and exports. A separate shared legal-corpus store holds source/document/version provenance and legal review history; normal firm requests get read-only access, while platform review/import operations are separately restricted.

The tenant catalog must never accept a database path, connection string, or tenant ID chosen directly by the client. The authenticated identity resolves to a firm through trusted server-side membership data. A request's firm_id body/query parameter is not an authorization source.

## Options considered

| Model | Isolation | Cost / operations | Decision |
|---|---|---|---|
| One shared SQLite database with firm filters | Primarily application-enforced; a missed query can leak records | Low initial cost, growing audit burden; tenant-only restore is hard | Not acceptable as the final production boundary for unrelated firms' confidential matters |
| One SQLite database per firm | Physical file separation, but shared host/process/admin access still matters | Practical for local/single-server deployments; file lifecycle, locking, backups, encryption, and routing must be engineered | Acceptable as a controlled interim/single-node option only after explicit design and testing |
| One PostgreSQL database per firm, shared application | Stronger database boundary and straightforward firm-level backup/restore; credentials and host/admin access remain privileged paths | More provisioning/migration/monitoring work; can be automated | **Recommended production target** |
| Shared PostgreSQL database with row-level security | Database-enforced row policy if every access path uses safe tenant context and policies are correct | Lower database count, more complex policy and connection-pool correctness | Possible later for a lower-cost tier, but not the first migration target |
| Entire application deployment per firm | Strong operational and data separation | Highest per-firm infrastructure and upgrade overhead | Offer only if a customer needs dedicated/on-prem deployment or stronger isolation |

A dedicated database is not, by itself, complete security: the application still needs least-privilege database credentials, secure secrets, safe tenant resolution, controlled platform access, encrypted transport/storage, and verified backups.

## Implementation sequence

### Phase 0 — Freeze and map the current data boundary

1. Keep the existing cross-firm API tests and fix any failures before architecture migration.
2. Inventory every table, SQL query, background/scheduled job, export, file path, cache, search index, and administrative endpoint.
3. Classify data as firm-owned, platform/control-plane, or shared legal-reference data. Explicitly classify chunks and legal-review tables; do not move them by assumption.
4. Identify the production deployment model, current database path, file storage, backups, and number of firms before designing a one-time migration.
5. Add an architecture test checklist; do not represent static inventory as an independent security review.

### Phase 1 — Separate storage access from routes

1. Introduce a repository/connection-provider interface behind existing route functions.
2. Separate trusted tenant resolution from request payloads.
3. Remove reliance on implicit default firm_id=1 for newly created firm-owned records; require explicit trusted context.
4. Add tests for missing tenant context, invalid catalog mapping, unavailable tenant database, and attempts to select another firm's database.
5. Keep platform/global legal corpus operations on a separate, explicit service path.

### Phase 2 — Provisioning and schema management

1. Add a control-plane tenant catalog with a stable firm identifier, database reference, status, schema version, and lifecycle timestamps.
2. Provision a new firm database through an idempotent, audited admin workflow.
3. Use versioned migrations; test fresh provisioning and upgrades from a copy of the current schema.
4. Use separate least-privilege credentials per tenant database where the hosting platform supports it. Do not put credentials or database URLs in source control or logs.
5. Ensure all connections are created from the server-side catalog, never from user-controlled values.

### Phase 3 — Migration and cutover

1. Back up and verify the existing database before any migration; perform a restore rehearsal first.
2. Write an idempotent migration that copies records by trusted firm_id, preserves IDs/relationships where required, and records row counts and hashes for key tables.
3. Handle users belonging to multiple firms explicitly rather than silently assigning them to one firm.
4. Move shared legal-reference data into the designated shared store with explicit ownership and permissions.
5. Migrate uploaded binaries and derived files separately; the current repository notes that original upload binaries are not retained, so missing originals cannot be reconstructed from metadata.
6. Run a read-only comparison, cross-firm negative tests, export tests, and firm-level restore test before cutover.
7. Define a rollback point and a no-write/freeze window. Do not dual-write to old and new stores without a designed consistency protocol.

### Phase 4 — Release gates

- New firm provisioning, suspension, deletion, and recovery are tested.
- Firm A cannot read, update, delete, search, export, or infer Firm B's matter data, files, research messages, audit records, or metadata.
- Restoring Firm A does not change Firm B.
- Platform reviewers have separate, explicitly configured access to shared legal-registry operations.
- Migration counts and hashes reconcile; failed migration leaves the source intact.
- Production secrets, TLS, encryption, monitoring, backup retention, restore rehearsal, incident response, and independent security review are completed.
- Browser, RTL/LTR, keyboard and screen-reader QA remain separate product release gates.

## Immediate next engineering task

Before replacing the storage engine, implement Phase 0 plus a data classification/migration map and identify every call site using conn(), DB, direct sqlite3, and filesystem paths. Then choose the smallest reversible extraction of database access behind an interface, with the existing API tests as regression gates. Do not perform a one-shot SQLite-to-PostgreSQL rewrite in a single PR.

## Explicit non-goals

- This document does not migrate the database.
- It does not claim SQLite is inherently insecure for a single-user/local deployment.
- It does not claim ZKBioTime uses a specific tenant-isolation model.
- It does not certify compliance with any legal, privacy, or security standard.
- It does not authorize production use with unrelated firms' confidential matter data.
