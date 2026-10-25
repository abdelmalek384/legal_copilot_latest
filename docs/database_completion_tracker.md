# Database completion tracker

**Last updated:** 2026-10-25  
**Estimated completion:** 28%  
**Status:** In progress — not production-ready for confidential multi-firm matter data.

This is a planning estimate across database migrations, tenant isolation, legacy-data reconciliation, operational recovery, and release validation. It is not a percentage of tests passing. Update this file as database PRs merge and as acceptance criteria are completed.

## Completed and merged

- [x] Harden SQLite backup concurrency, staged validation, encryption output, retention ordering, and restore replacement safety (PR #138).
- [x] Extend read-only tenant ownership preflight to detect orphaned child records (PR #139).
- [x] Move six operational indexes into versioned migration 0002 (PR #140).
- [x] Add disposable-copy migration rehearsal with source read-only behavior and integrity checks (PR #141).
- [x] Move remaining operational indexes into versioned migration 0003 (PR #142).
- [x] Add read-only preflight checks for unlinked matter records (PR #143).
- [x] Add persistent database completion tracker (PR #144).
- [x] Inventory remaining startup DDL without opening a database (PR #145).
- [x] Reject symlinked tenant storage roots and explicitly test tenant catalog safety in CI (PR #146).
- [x] Expand read-only ownership preflight for cross-firm document, extraction-review, and audit inconsistencies (PR #147).
- [x] Move `legal_version_relations` and `security_audit_events` into versioned migrations 0004 and 0005, with migration-order, constraint, inventory, and rehearsal coverage (PR #148, merged).
- [x] Move six independent authentication/case-workspace tables (`auth_sessions`, `notes`, `fees`, `tasks`, `events`, and case-calendar `sessions`) into migration 0006, with migration, inventory, and disposable-copy coverage (PR #149, merged).
- [x] Add end-to-end fresh database startup and restart coverage in CI; verify the migration ledger and preservation of an existing row (PR #151, merged).
- [x] Reject out-of-order recorded migration histories in the migration runner, with regression coverage and CI (PR #152, merged).

## In progress

- [ ] **PR #153 — Move `legal_sources` and FTS5 setup into migrations 0007 and 0008.** `legal_documents` remains in bootstrap because startup conditionally inspects/alters it before the migration runner. FTS migration preserves an existing virtual table and does not attempt an implicit rebuild. Awaiting latest CI.

## Remaining database work

### 1. Finish versioned schema migrations
- [ ] Move legacy table creation, FTS setup, and conditional `ALTER TABLE` statements out of startup bootstrap into ordered, checksum-protected migrations.
- [ ] Define a supported fresh-install schema path and an upgrade path for each currently deployed legacy schema shape.
- [ ] Test migration order, idempotency, checksum drift, interrupted migrations, and rollback/restore on representative disposable database copies.
- [ ] Keep migrations immutable after merge; add new forward migrations for corrections.

### 2. Approve identity and tenant contract
- [ ] Product/deployment owners decide whether identities can belong to multiple firms, email normalization/uniqueness, role domains, invitation rules, and session behavior after membership revocation.
- [ ] Complete the deployment and storage inventory before selecting production routing behavior.
- [ ] Implement firm memberships and trusted active-firm resolution only after contract approval.

### 3. Implement actual tenant storage boundaries
- [ ] Route each firm-scoped request through an authenticated, server-validated firm membership and trusted server-side tenant catalog.
- [ ] Replace the shared `COPILOT_DB` runtime boundary with firm-specific database selection; never trust client-supplied firm IDs, paths, or connection strings as authorization.
- [ ] Separate firm matter data from identity/control-plane data and the shared legal corpus; classify mixed `chunks`/FTS data before splitting.
- [ ] Enforce lifecycle behavior for provisioning, disabled tenants, unknown catalog entries, unavailable tenant DBs, and revoked memberships.

### 4. Reconcile existing data safely
- [ ] Run read-only ownership preflight against a protected production-like copy and retain its report.
- [ ] Resolve missing/unknown firm ownership, orphaned rows, unlinked documents/children, cross-firm references, and ambiguous shared-corpus chunks from trusted evidence.
- [ ] Migrate with source/target row counts, stable hashes where applicable, foreign-key checks, FTS reconciliation, and explicit quarantine for unresolved rows.
- [ ] Confirm retention/availability of original uploaded binaries; current inventory says original upload binaries are not retained.

### 5. Prove tenant isolation and operational recovery
- [ ] Complete route-by-route and SQL-query-by-query cross-firm authorization tests, including exports, audit, search, legal review, background work, and administrative paths.
- [ ] Add per-firm backup, restore, retention, export, and deletion behavior with isolation tests.
- [ ] Rehearse deployment, restore, and rollback using representative copies; validate permissions, secrets, encryption keys, monitoring, and incident runbooks.
- [ ] Obtain an independent security review before production use with unrelated firms' confidential matters.

## Release gate

**Do not describe the database as production-grade multi-tenant isolation yet.** The application currently uses a shared SQLite database. Passing migration, preflight, and API tests improves safety but does not substitute for separate tenant storage, approved identity semantics, full data reconciliation, operational drills, and independent review.

## Progress update rules

- Count a code change as completed only after its PR is merged and its required CI checks pass.
- Keep open or failed-CI work in the in-progress section.
- Increase the overall percentage only when a meaningful release gate is completed; do not equate test count with database readiness.
- Preserve this tracker until every remaining task and the release gate are complete.
