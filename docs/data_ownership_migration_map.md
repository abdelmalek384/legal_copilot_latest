# SEC-01 — data ownership and migration map (Phase 0 draft)

**Status:** Draft for review; no schema or runtime behavior changed  
**Date:** 2026-10-24  
**Sources reviewed:** `app.py` schema declarations, `docs/database_tenancy_architecture.md`, `docs/database_boundary_phase0_review.md`, `docs/repository_storage_entrypoint_inventory.md`, and `docs/identity_firm_membership_contract.md`.

## Purpose and boundary

This document turns the currently declared application tables into a proposed ownership/migration map. It is a planning artifact, not a completed SQL audit. Table names and obvious relationships were inspected, but every SQL call site, every migration/legacy column, the actual production deployment, and all external file/job locations have not been exhaustively verified.

**No migration is authorized by this draft.** The current application still uses one SQLite database. The identity/membership model in PR #117 is a merged proposal, not evidence that the product owner approved global identities or many-to-many memberships.

## Candidate target stores

- **Firm database:** confidential matter data and firm-specific work product. Each firm's database is selected only through trusted server-side tenant resolution.
- **Identity/control plane:** global login identities (if approved), membership/role assignments, tenant catalog and lifecycle, authentication throttles, and tenant database references. Do not store raw credentials or user-supplied database paths in tenant-routing records.
- **Shared legal corpus:** source/document/version provenance, legal review history, and global legal passages. Normal firm requests should have read-only access; corpus writes belong to controlled platform workflows.
- **Operational/security store:** only if approved by a threat model and retention policy; should not become a cross-firm channel for matter content. The first implementation should avoid introducing a new store solely to relocate data without an owner, access policy, and recovery plan.
- **Firm-scoped object storage:** original uploads, page images/previews, extracted artifacts, exports, and other files, if retained. The current reviewed upload flow does not retain original binaries, so historical originals cannot be reconstructed from current metadata.

## Table/resource mapping

| Current table/resource | Proposed ownership | Candidate destination | Important migration and security conditions |
|---|---|---|---|
| `firms` | Tenant catalog / control plane | Identity/control-plane database | Define lifecycle/status and trusted mapping to a server-side database reference. Do not route from a client-supplied firm ID alone. Existing schema does not by itself establish a safe catalog. |
| `users` | Unresolved identity domain | Control plane if global identity is approved; otherwise per-firm identity stores | Resolve duplicate/normalized email cases, legacy `firm_id` defaults, role semantics, account recovery, deactivation, and migration of users linked to multiple firms before moving this table. |
| `auth_sessions` | Identity/security control plane candidate | Control plane if sessions are global | Token hashes and expiry must remain protected. Firm context must be revalidated against current membership; membership removal and account disablement must invalidate or deny old sessions. |
| `login_attempts` | Global authentication throttling candidate | Control plane | Existing email-keyed primary key implies shared account namespace. Confirm normalization, lockout semantics, retention, and privacy. |
| `api_rate_limit_windows` | Operational/security control plane candidate | Control plane or dedicated rate-limit service | Determine whether `client_key` includes IP/user/firm identifiers; avoid accidental cross-firm denial-of-service or bypass. Define cleanup/retention and whether keys are sensitive. |
| `cases` | Firm-owned matter | Firm database | Preserve firm ownership, creator references, case IDs/relations, and object-level authorization. Reject or quarantine orphaned/unknown-firm rows rather than assigning them to a default firm. |
| `notes` | Firm-owned, through case | Firm database | Parent-case ownership and creator references must remain valid. Validate every route's authorization and mutation transaction boundary. |
| `deadlines` | Firm-owned, through case | Firm database | Preserve case relationship, due/status data, and authorization for reads, edits, exports, and deletes. |
| `fees` | Firm-owned, through case | Firm database | Treat amounts and client/case context as confidential; verify exports, audit and retention behavior. |
| `members` | Firm-owned case membership, through case | Firm database | Distinguish case membership from firm membership. Validate every referenced user against the chosen global-identity/membership model. |
| `tasks` | Firm-owned, through case | Firm database | Assignee and creator references need explicit identity mapping; ensure parent authorization and task mutation cannot race. |
| `events` | Firm-owned matter timeline, through case | Firm database | Preserve chronological records and access controls; confirm any free-text fields do not leak to global logs or shared search. |
| `sessions` | Firm-owned case/calendar activity (not authentication sessions) | Firm database | Name is easy to confuse with `auth_sessions`; preserve case ownership and make code/schema naming explicit during migration. |
| `docs` | Firm-owned document metadata, through case | Firm database | Preserve firm/case/uploader metadata and hashes. Original uploaded bytes are not retained by the current flow; do not promise original recovery or page previews for historical rows. |
| `document_extraction_reviews` | Firm-owned review/correction linked to a document | Firm database | Preserve reviewer attribution, correction history, stale-update protections, and firm boundary. Check foreign keys and orphan handling. |
| Matter-linked rows in `chunks` (`case_id` set) | Firm-owned extracted text/search content | Firm database plus firm-specific search index | Verify each row's case/document relationship, provenance, FTS synchronization, deletion, export, and search scoping. Do not copy global corpus rows into tenant databases. |
| `research_conversations` | Firm-owned research history | Firm database | Validate both `firm_id` and user/membership identity during migration; preserve conversation owner checks, retention, export and delete semantics. |
| `research_messages` | Firm-owned child records via conversation | Same firm database as parent conversation | Parent-child integrity must be checked. Every read/update/delete/export path should resolve the parent within the trusted firm context. |
| `security_audit_events` | Mixed concern: current rows are firm-tagged; platform/security events may need a separate stream | Firm database for firm events; explicit control-plane stream for platform events if required | Do not copy all events into a shared platform log by default. Define event taxonomy, access, tamper resistance, retention, and firm-specific export/restore. |
| `case_deletion_audit` | Firm-owned sensitive matter snapshots | Same firm database, or a separately protected firm-keyed archive with explicit design | Snapshots may contain deleted matter data. Preserve actor attribution, retention/deletion rules, restore semantics, and tenant-specific access. An embedded `firm_id` is not a substitute for scoped access. |
| `chunks` rows with `case_id IS NULL` | Shared legal-reference corpus | Shared legal-corpus store | Keep separate from matter chunks. Preserve source/version references, permission state, legal status and provenance; normal firm access should be read-only. |
| `chunks_fts` | Derived index over mixed global and matter passages today | Separate shared-corpus index plus per-firm matter indexes, or a demonstrably safe alternative | Do not mechanically copy the mixed FTS table. Rebuild from authoritative rows after partitioning and verify index consistency, filters, deletion, and no cross-firm result leakage. |
| `legal_sources` | Shared legal-corpus provenance | Shared legal-corpus store | Preserve source terms, collection/reuse permissions and evidence; unknown permission must remain unknown. Only controlled platform workflows may mutate. |
| `legal_documents` | Shared legal-corpus metadata | Shared legal-corpus store | Preserve source relation and stable identifiers; verify all references and uniqueness before import. |
| `legal_document_versions` | Shared legal-corpus version/provenance | Shared legal-corpus store | Preserve hashes, original path references, effective/repeal dates, verification states, and review evidence. Paths may not exist in the destination; migrate file assets separately and reconcile hashes. |
| `legal_version_relations` | Shared legal-corpus version graph | Shared legal-corpus store | Validate both endpoints and relation semantics; never infer repeal/amendment relations from title similarity alone. |
| `legal_review_events` | Shared legal-corpus governance/audit | Shared legal-corpus store with platform-only mutation | Preserve reviewer, outcome, evidence and chronology. Keep separate from firm matter audits and define access/retention. |
| External original uploads, previews, exports and generated artifacts | Not a database table; ownership depends on content | Firm-scoped object storage or explicitly governed shared corpus artifact storage | Inventory actual paths and destinations. Define encryption, authorization, retention, deletion, backup, restore, content type/size limits, and orphan cleanup. Current upload flow does not retain original binaries. |
| Backups, temporary plaintext files, WAL/SHM files and logs | Operational assets potentially containing all database content | Tenant-specific backup boundary and controlled operational storage | Existing CLI backup is whole-database. Design tenant-scoped backups only after partitioning; use unique temporary names, restrictive permissions, cleanup, off-host keys, and restore drills. |
| Corpus collection/OCR outputs and JSONL manifests | Shared-corpus operational artifacts, subject to source rights | Controlled corpus workspace/artifact store | Record provenance and permissions, prevent accidental promotion to production, inventory actual runtime paths, and restrict writes to trusted operators. |

## Migration ordering and unresolved rows

1. Approve the identity model with the product owner; PR #117 is only a proposal.
2. Confirm the production topology with the deployment owner: actual database path, volumes, job schedules, log destinations, backup destinations, secrets, and external services.
3. Enumerate every SQL statement and resource access by route/helper/CLI. For each, record ownership class, trusted firm context, parent authorization, transaction boundary, and export/delete behavior.
4. Classify every existing row before migration. Rows with missing, inconsistent, defaulted, or unknown firm ownership must be quarantined for review; never silently assign them to Firm 1 or infer ownership from creator ID alone.
5. Decide treatment of global identity, memberships, platform reviewer allowlist/configuration, shared legal corpus, mixed FTS, audit records, and existing legacy users.
6. Build a versioned migration with source-preserving dry run, per-table counts, foreign-key checks, stable key/hash reconciliation where appropriate, search consistency tests, two-firm negative tests, and explicit rollback.
7. Only after the mapping is approved, implement storage routing and tenant-specific backup/restore. Run a restore rehearsal for one firm while proving other firms remain unchanged.

## Required review checklist

- [ ] Product owner approves global identity + multi-firm memberships, or records an explicit alternative.
- [ ] Deployment owner confirms actual production topology and scheduled/external jobs.
- [ ] Every SQL-bearing statement and file/resource path is inventoried and reviewed.
- [ ] Mixed `chunks`/FTS ownership is resolved and tested.
- [ ] All existing records can be mapped to an owner; unknown/orphan records have a quarantine plan.
- [ ] Identity, sessions, audit and platform-reviewer data have explicit ownership and revocation semantics.
- [ ] Original-file retention decision is approved; historical missing binaries are documented as unrecoverable.
- [ ] Migration dry run, reconciliation, cross-firm negative tests, restore test and rollback plan are reviewed.
- [ ] Independent security review is scheduled after implementation, not replaced by this document.

## Explicit non-claims

This is a draft table/resource classification based on repository schema and prior static reviews. It is not an exhaustive query audit, a production deployment inventory, a migration script, a passing isolation test, or an independent security review. The shared SQLite runtime remains unchanged and is not a suitable final isolation boundary for unrelated firms' confidential matters.
