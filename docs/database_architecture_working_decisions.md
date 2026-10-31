# Database architecture — working decisions

**Status:** Product-owner working plan recorded 2026-10-26; production cutover and irreversible operations are not authorized by this document.
**Scope:** Database tenancy, identity, legacy-data handling, legal corpus, rollout, and billing sequencing.

## Decisions to implement against

1. **Firm storage:** one separate database per firm. The target production engine and hosting topology still require a deployment decision; per-firm database routing must use a trusted server-side tenant catalog, never a client-supplied path or connection string.
2. **User membership:** a global user identity may have memberships in multiple firms. Membership and firm role must be validated for every firm-scoped request.
3. **Email uniqueness:** email is globally unique after a documented normalization policy. Before enforcing this on existing data, audit normalized collisions and define a reviewed resolution process; do not merge or delete identities automatically.
4. **Administration:** platform-wide privileges are separate from firm-scoped roles. Platform privileges require explicit, audited grant/revocation rules.
5. **Legacy data:** the working target is a fresh database after an explicit backup and retention review. No existing database or record may be wiped, replaced, or discarded until the backup is verified, retention obligations are reviewed, reconciliation is signed off, and cutover/rollback is approved.
6. **Legal corpus:** keep a shared central legal corpus with controlled write/review access. Firm documents, research, annotations, and matter-derived content remain isolated per firm. Corpus classification must be provenance-based; a missing case ID alone does not prove a chunk is shared legal content.
7. **Release:** controlled rollout with safety gates, rehearsal, isolation testing, backup/restore validation, monitoring, and a rollback plan. Do not expose confidential production matter data to a new tenancy implementation before the gates pass.
8. **Billing:** defer billing schema and payment integration until the database safety work is complete.

## Required implementation principles

- Treat these as working product decisions, not evidence that the current runtime implements them.
- Keep current data read-only during inventory and preflight. Never auto-assign ambiguous records to a default firm or user.
- Keep migrations forward-only after merge. Test fresh provisioning and upgrades on disposable database copies.
- Separate identity/control-plane records, firm-owned matter data, and shared legal-reference data according to a reviewed table/resource map.
- Tenant selection must be resolved from authenticated identity plus an active membership and trusted server-side catalog mapping.
- Revalidate membership and role on requests; suspension/revocation must prevent access through existing sessions and cached tenant connections.
- Keep firm-role authorization separate from platform corpus administration.
- Record migration reconciliation counts, unresolved/quarantined records, schema versions, and restore evidence before cutover.

## Approval gates — do not perform these automatically

Explicit approval is required before:
- deleting, overwriting, or abandoning the existing database or any legacy records;
- applying a migration to production or changing the production database/storage topology;
- resolving duplicate normalized emails by merging, renaming, or deleting accounts;
- moving, reclassifying, or deleting legal-corpus/chunk data where provenance is uncertain;
- changing platform-admin grants or production access policies;
- switching production traffic to per-firm databases.

## Release gate checklist

- [ ] Complete SQL/table/route/background-job/file/cache/search-index inventory.
- [ ] Finalize normalized-email rules and collision report against a protected copy.
- [ ] Specify firm membership invitation, initial firm owner, role grant, session revocation, and account recovery behavior.
- [ ] Implement trusted tenant catalog and per-firm database provisioning with least-privilege access.
- [ ] Exercise cross-firm isolation tests for APIs, background jobs, search, exports, uploads, and administrative flows.
- [ ] Rehearse fresh-database provisioning and legacy-data reconciliation on disposable copies.
- [ ] Verify per-firm backup and restore, shared-corpus recovery, monitoring, and rollback.
- [ ] Obtain explicit backup/retention and cutover approval before any destructive or irreversible action.
- [ ] Keep billing deferred until the database safety gates are accepted.

## Current-state warning

The configured separate-database runtime is now implemented and merged (PR #372): control-plane authentication/session lookup, trusted firm membership/catalog resolution, per-firm matter databases, and a shared legal corpus. Encrypted multi-database backup/restore is merged (PR #382), and deployment preflight validates the three-path configuration (PR #384). The shared `COPILOT_DB` runtime was retired in PR #972 and is rejected in every environment; this does not mean legacy data has been reconciled, every route/query has been proven isolated, or recovery/rollback has been rehearsed. Do not treat the system as production-ready until the remaining tracker gates pass.
