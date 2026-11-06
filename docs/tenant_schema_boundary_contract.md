# DB-04 — tenant schema boundary and migration contract

**Status:** Current architecture contract for the greenfield separate-database runtime. The core profile migrations and trusted runtime routing are implemented; exhaustive authorization review and production release gates remain open.
**Scope:** Define the ownership boundaries that new migrations, routes, CLI tools, background jobs, backups, and storage adapters must preserve.

## Operating assumptions

- This is a fresh implementation. No legacy customer database has been deployed or used.
- Do not create a legacy-data migration or reconciliation project unless an external database is explicitly proposed for import and approved separately.
- The approved runtime uses three distinct database domains: control plane, one firm database per firm, and shared legal corpus. The shared `COPILOT_DB` runtime was retired in PR #972 and is rejected in every environment; no development/test compatibility mode remains.
- A schema profile, database file, row-scope trigger, or passing CI run is not by itself proof that every application route or query is authorized correctly.

## Current schema ownership

### Control plane — global identity and tenant governance

Owns global identity and firm lifecycle data, including:
- `users`, globally normalized identity/email keys, account status and authentication sessions;
- `firms`, `firm_memberships`, trusted `tenant_database_catalog` entries and immutable firm-to-database bindings;
- platform roles, MFA state, account/invitation/recovery token ledgers, and platform security/lifecycle audit events;
- global security/rate-limit state where the key is intentionally user-, IP-, or platform-scoped.

Memberships and platform roles are separate authorization domains. A firm-admin role never implies a platform-admin or platform-reviewer role. Firm context must be resolved from authenticated server-side identity and current active membership, not from a caller-supplied firm ID alone. Suspension, revocation, account disablement and session invalidation must take effect without relying on stale cached authorization.

### Firm database — confidential matter and work-product data

Each firm has a distinct database bound to its immutable firm ID. It owns:
- cases and case children such as members, tasks, events, notes, deadlines, fees and calendar sessions;
- document metadata, extraction chunks and FTS index, extraction-review history, research conversations/messages, case-deletion snapshots and firm-scoped audit events;
- opaque original-file metadata in `original_file_objects` and the legal-hold/deletion workflow tables added by merged PR #671. Production uploads remain fail-closed until live provider and recovery acceptance.

Every child lookup, mutation, export, deletion and background operation must first establish the parent case/document inside the selected firm database and enforce the applicable case-membership/role rule. A child ID is never authorization. Database triggers enforce immutable tenant binding and selected row-scope constraints, but do not replace route-level checks.

### Shared legal corpus — platform-controlled legal-reference data

Owns global legal sources, legal documents and versions, version relationships, review events, import/review staging, and verified legal-reference chunks with their FTS index. Matter/client content, tenant secrets and firm-private notes must never be written into this profile.

Corpus read access may be shared according to product policy. Ingestion, verification, effective-date/repeal changes, source permission state and review outcomes require platform-level authorization and durable audit history. A caller-supplied flag cannot make content verified or current.

### Identically named tables in separate profiles

The `chunks` and `chunks_fts` names may exist in both firm and legal-corpus files, but the approved separate-database runtime keeps their contents and indexes physically separate:
- firm profile: only matter-linked extracted chunks belonging to that firm;
- legal-corpus profile: only legal-reference chunks linked to corpus provenance/version records.

The older compatibility schema can contain mixed data and is not the approved multi-firm runtime. Never infer that two tables with the same name share ownership, or copy the legacy mixed FTS index into firm databases.

## Migration and runtime invariants

1. Fresh-install schema changes belong in ordered, profile-specific, checksum-validated migrations. Applied migrations are immutable; corrective changes use forward-only migrations.
2. Control-plane, firm and corpus initializers must reject the wrong profile, incompatible schema state, unsafe paths and mismatched immutable bindings.
3. A firm database is resolved only through the trusted catalog. Do not construct database filenames from request input or accept a client-provided storage path.
4. Cross-database operations must not claim distributed atomicity. Use explicit states, append-only audit events, failure injection and conservative reconciliation where a filesystem/object store cannot share a SQLite transaction.
5. FTS maintenance must be tested on the correct profile and preserve the external-content schema and synchronization triggers.
6. Backups must include a coordinated recovery point across control plane, corpus, every cataloged firm database, and configured original-file objects. Writers must be quiesced for the full snapshot; the flag is an operator assertion, not a distributed lock.
7. Restore must target a new isolated directory and validate bundle checksums, profiles, firm bindings, catalog consistency, SQLite integrity, object digests and active/inactive membership behavior before cutover.
8. Temporary plaintext restore files require restricted storage. Cleanup is not guaranteed secure erasure, particularly on SSD or copy-on-write filesystems.
9. Logs, reports and audit exports must not leak passwords, tokens, cookies, original document content, raw secrets or cross-firm data.

## External resource ownership

- Original binary files: the local private filesystem adapter is for development/testing only. The S3/KMS object-storage adapter, integrity checks, reconciliation, backup/restore staging, and guarded live-acceptance probe are implemented. This does not mean the deployment is accepted: production uploads must remain fail-closed until the actual bucket/key/IAM policy passes live validation, a witnessed recovery/deletion drill is complete, and the mandatory current acceptance manifest is approved. Production enablement requires a reviewed configuration/code change after those gates close.
- Encrypted backup bundles: separate from the database paths and backup key; verify and restore before treating a bundle as a recovery point.
- Email invitations/recovery: SMTP delivery and the public HTTPS origin are deployment-configured; no credentials belong in source control.
- Temporary extraction, OCR, upload staging and recovery directories: must be private, bounded, reconciled after interrupted work and excluded from public serving.
- Operational reports and logs: store in the approved restricted evidence location; do not place client content or secret values in the repository.

## Required review gates

- [ ] Complete route-by-route and SQL-query-by-query authorization review, including exports, audit, search, corpus review, CLI commands and background/maintenance tools.
- [ ] Keep route inventory synchronized with every registered route and confirm non-public routes authenticate through the shared identity dependency; then test route-specific firm/case/platform authorization and failure branches.
- [ ] Complete operational acceptance for invitations, recovery, first-platform-admin bootstrap and privileged-account recovery. The implementation is merged in PR #729; live email/provider validation, multi-host rate-limit validation, witnessed bootstrap/recovery drills and independent review remain open.
- [ ] Validate the merged original-file lifecycle with a production object-storage/KMS provider before enabling production matter uploads; live-provider, witnessed recovery, retention, and independent-review gates remain open.
- [ ] Approve jurisdiction-appropriate retention periods, export/deletion semantics and legal-hold policy; test that held material cannot be purged and every purge preserves a tombstone/audit event.
- [ ] Run the automated isolated recovery smoke test, then conduct a witnessed staging restore/startup/isolation/rollback drill with independent reviewer sign-off.
- [ ] Validate production host/proxy/cookie, secret-store, key-recovery, monitoring and incident-response controls.
- [ ] Obtain an independent security review before onboarding unrelated firms or storing confidential production matter data.

## Conditional future import

No legacy customer database is in scope for first deployment. If an external database is deliberately introduced later, treat it as a separate approved import project: work only on protected copies; establish ownership from trusted evidence; report source/target counts, foreign-key and FTS integrity, hashes where suitable, cross-firm references and quarantine decisions; rehearse rollback before any cutover. Never infer ownership from a default firm ID, email, filename or creator ID alone.

## Acceptance rule

The database is not production-ready for unrelated firms' confidential matter data until the release gates above are satisfied. Passing CI proves only the tested code paths, not independent security review, production KMS readiness, real-world recovery or complete legal-content correctness.
