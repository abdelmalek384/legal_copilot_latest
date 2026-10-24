# SEC-01 — Identity, firm membership, and tenant-routing contract

**Status:** Proposed decision for product/operations approval; implementation not started  
**Date:** 2026-10-24  
**Depends on:** `docs/database_tenancy_architecture.md`, `docs/database_boundary_phase0_review.md`, and `docs/repository_storage_entrypoint_inventory.md`

## Decision needed

Before implementing multi-firm database routing, the product owner and deployment owner must approve the identity semantics below. This document makes a concrete recommendation to unblock that decision; it does not change runtime behavior or authorize migration.

## Recommended contract

Use a **global login identity with explicit firm memberships**:

- A user identity represents a person and has a globally unique, normalized login email.
- A user may have zero, one, or multiple firm memberships. Membership records are the authority for which firms the identity may access.
- Each membership has a firm ID, firm-scoped role, status (at minimum active/suspended), and auditable lifecycle metadata. Firm roles must not silently grant platform-wide privileges.
- An authenticated session identifies the global user. Every firm-scoped request must also resolve an active firm context from a server-side-validated membership.
- The client may request a firm context or switch firms, but the server must verify that the authenticated identity has an active membership for that firm on every relevant request. A submitted `firm_id`, URL identifier, database path, or connection string is never sufficient authorization.
- Switching active firm context must not elevate permissions. Firm-specific authorization is evaluated after membership validation, and data access must use the trusted resolved context.
- Platform-wide corpus administration/review is a separate permission domain, backed by an explicit deployment-configured platform reviewer/admin policy. Membership in a law firm does not imply platform access.
- Revoking a membership must invalidate or deny the affected firm context promptly; account disablement and credential reset must revoke sessions according to a documented global policy.
- Account recovery is identity-wide and must not let an email collision, stale membership, or user-supplied firm identifier select another firm's account.

## Why this is the recommended default

Global identity plus explicit memberships supports a lawyer or staff member working with more than one firm without duplicating credentials, while keeping firm authorization explicit. It also makes account recovery and session revocation semantics easier to state consistently. This is a product/security recommendation, not a claim about the current schema.

## Alternatives and trade-offs

| Model | Benefits | Risks / migration implications | Recommendation |
|---|---|---|---|
| Global identity + many-to-many firm memberships | Supports cross-firm professionals and consistent recovery | Requires a membership model, firm-scoped roles, session semantics, and migration of current `users.firm_id` data | Preferred if multi-firm membership is a real product requirement |
| Separate identity/account per firm | Clearer account-level separation and simpler membership semantics | Same person may have multiple accounts; duplicate emails, recovery, invitations, and support workflows become complex | Choose only if product explicitly requires firm-isolated identities |
| One identity permanently tied to one firm | Smallest near-term change | Blocks legitimate cross-firm work or encourages duplicate accounts; does not itself make storage tenant-safe | Do not assume without product-owner approval |

## Data-model implications (not implemented)

A likely target is:

- `users`: global identity and authentication attributes; unique normalized email.
- `firm_memberships`: `user_id`, `firm_id`, firm-scoped role, status, created/updated timestamps, and actor/audit references.
- `firms`: firm lifecycle/status and non-secret tenant-catalog reference.
- Session state: global user identity plus a selected firm context that is revalidated against current membership. Do not trust a cached role indefinitely after membership revocation.
- Tenant catalog: stable firm ID → server-side storage reference and schema/lifecycle status. Credentials and raw connection strings remain in controlled secret/configuration systems, not user records or client payloads.

This sketch is not a migration specification. Before implementation, inventory uniqueness constraints, existing users with missing or default `firm_id`, duplicate emails under normalization, foreign keys, session/token format, audit attribution, and any routes that currently infer a firm implicitly.

## Required answers before implementation

The product owner and deployment owner must confirm:

1. Can one person legitimately access more than one firm?
2. Is email globally unique across all firms, and what normalization/verification rules apply?
3. Are roles firm-scoped, platform-scoped, or both? Who can grant platform privileges?
4. What should happen to active sessions when a membership is suspended or removed?
5. How are invitations accepted and how is initial firm ownership/admin status established?
6. Does the actual deployment have any legacy users or operator workflows not represented in repository fixtures?

If question 1 is answered “no,” explicitly select separate firm identities and document duplicate-account/recovery behavior before schema work. Do not silently implement the recommended model merely because it is convenient.

## Security acceptance criteria

Before enabling tenant routing:

- A user with no active membership cannot select or infer a firm's database.
- A user who belongs to Firm A cannot access Firm B by changing path, query, body, header, cookie, or client-side state.
- A multi-firm user can access only the firms for which membership is active; switching firm changes the trusted server-side context and does not carry permissions across firms.
- Suspending or deleting membership prevents further access, including through existing sessions and cached connections.
- Firm roles do not imply platform corpus-review access.
- Account recovery, password reset, session revocation, and audit attribution behave correctly for a global identity and across multiple memberships.
- Tests exercise at least two firms, multiple users, revoked membership, invalid firm selection, and database-unavailable/unknown catalog mappings.
- Migration rehearsal accounts for every existing user and relationship, records reconciliation counts, and can roll back without modifying the source database.

## Explicit non-goals

This document does not implement authentication changes, add a membership table, change session behavior, provision databases, route requests by tenant, migrate data, or certify security. The shared SQLite database remains the current runtime boundary. Obtain product/operations approval and finish the Phase 0 data/deployment inventory before implementing the contract.
