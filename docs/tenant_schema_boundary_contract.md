# DB-04 — tenant schema boundary and migration contract

**Status:** Design contract for review; no runtime schema or data migration changed  
**Depends on:** DB-02 versioned migrations, DB-03 trusted tenant catalog/provisioning, and approval of the identity/firm-membership contract  
**Scope:** Define what belongs in a firm database versus the shared legal corpus and control plane before tenant schema initialization is implemented.

## Why this is a separate step

The current application schema in `app.py` is a mixed schema. Copying it into every firm database would duplicate legal-corpus governance and version records, while retaining global FTS structures could create cross-firm retrieval leakage. Conversely, moving tables based only on names could break foreign keys, legacy routes, audit semantics, and backup/restore. This contract is a classification gate, not authorization to move tables.

## Proposed schema profiles

### Firm database (confidential matter/work-product profile)

Candidate tables:
- `cases`, `notes`, `deadlines`, `fees`, `members`, `tasks`, `events`, case/calendar `sessions`, `docs`
- `document_extraction_reviews`, `research_conversations`, `research_messages`
- Matter-linked `chunks` and a firm-local full-text index for those chunks
- `case_deletion_audit` and firm-scoped security events, subject to a final audit-retention decision

Every matter-owned row must have either an explicit `firm_id` constraint or a validated parent chain that is resolved within the already-selected firm database. A parent ID supplied by a client is not authorization. Child reads, writes, exports, deletes and background jobs must resolve the parent inside the same firm boundary.

### Shared legal-corpus profile (platform-controlled)

Candidate tables:
- `legal_sources`, `legal_documents`, `legal_document_versions`, `legal_version_relations`, `legal_review_events`
- Global/reference `chunks` rows only where their provenance establishes `case_id IS NULL`, with a corpus-only search index

Firm-facing application paths should receive read-only access to approved corpus retrieval interfaces. Corpus ingestion, review and version-graph mutations remain privileged platform workflows. Shared corpus permissions and legal-status review must not be inferred from a database boundary.

### Identity/control-plane profile (not yet approved)

Candidate tables:
- `firms` and tenant catalog metadata
- `users`, `auth_sessions`, `login_attempts`, and membership/role data only after product-owner approval of the identity model
- Tenant lifecycle/provisioning state and trusted references to generated database filenames

The global-identity/many-to-many membership proposal in `docs/identity_firm_membership_contract.md` remains unapproved. Do not implement a global `users` table or change sign-in semantics based solely on this document. Revalidate active membership and firm-scoped role on every tenant-context establishment; membership removal, account disablement and session revocation need explicit tests.

### Unresolved operational/security records

- `api_rate_limit_windows`: determine whether limits are global, user-scoped, firm-scoped, or layered. Do not move it without reviewing key construction and denial-of-service implications.
- `security_audit_events`: define separate event classes and access/retention rules for firm activity versus platform security activity.
- File uploads, exports, OCR outputs, temporary files, SQLite WAL/SHM files, logs, backups and scheduled jobs need a real deployment inventory. Database partitioning alone does not isolate these resources.
- Existing whole-database backup/restore cannot be treated as firm-specific backup/restore.

## Full-text search partitioning contract

The current `chunks` table mixes legal corpus and matter text, and `chunks_fts` is a single FTS5 virtual table. The target design must not copy that mixed index into every tenant database or query it without a trusted scope.

1. The shared corpus store contains only corpus chunks with verified source/version provenance and no matter ownership.
2. Each firm store contains only chunks whose case/document ownership resolves within that firm.
3. Search APIs compose results from these separately scoped stores only after authorization; corpus retrieval and matter retrieval keep distinct provenance and access policies.
4. FTS rebuild/update/delete behavior must be transactionally tested, including document correction, case deletion, tenant migration and rollback.
5. Tests must plant unique sentinel text in firm A, firm B and the shared corpus, then prove each query class returns only permitted results. Test both positive access and negative cross-firm leakage.

## Migration and rollout gates

1. Approve the identity/membership model and record explicit decisions for unresolved ownership rows.
2. Complete the exhaustive SQL call-site, route, CLI, job, file, backup, restore, logging and deployment inventory. Existing static inventories are not exhaustive.
3. Define independently testable schema initializers for control plane, firm database and shared corpus. Each initializer must be versioned, deterministic, safe to rerun, and reject incompatible schema state.
4. Run a dry-run against a protected copy of a representative database. Produce per-table source/destination counts, orphan reports, duplicate/key conflicts, hashes where suitable, foreign-key checks, FTS consistency checks and quarantine reports.
5. Never infer ownership from a defaulted `firm_id`, user email, filename, or creator ID alone. Ambiguous rows remain quarantined until evidence-backed reconciliation.
6. Migrate one test firm first. Verify source and destination counts, constraints, application behavior, firm-scoped export/delete, and rollback before attempting another firm.
7. Run cross-firm sentinel tests for all routes, background jobs, search, files, exports, backups and restores. Verify a firm-specific restore does not change another firm's records or corpus state.
8. Switch runtime routing only after the prior gates pass and a rollback plan is approved. The catalog/provisioning module alone does not establish end-to-end isolation.

## Acceptance criteria for implementation

- [ ] Three explicit schema profiles and ownership decisions are approved.
- [ ] Every table, FTS object and external resource has an owner, writer, reader, retention policy and migration strategy.
- [ ] No tenant schema initializer creates platform-only legal review or control-plane tables in a firm DB.
- [ ] No shared corpus schema contains matter text or tenant secrets.
- [ ] Two-firm isolation tests cover reads, writes, search, exports, deletion and background jobs.
- [ ] Migration is dry-run-first, count-reconciled, restartable, auditable and rollback-tested.
- [ ] Firm-specific backup/restore is tested independently of other firms.
- [ ] Independent security review and deployment-owner sign-off precede production use.

## Explicit non-claims

This document does not implement schema initializers, database routing, global identities, membership changes, table movement, FTS separation, firm-specific backup/restore, or production isolation. Current application storage remains a single configured SQLite database until these steps are implemented and verified.
