# SEC-01 — Identity, firm membership, and tenant-routing contract

**Status:** Historical architecture decision record. The separate-database identity and firm-routing design has since been implemented in the application; this document preserves the original rationale and acceptance requirements, not a current implementation checklist. Runtime behavior must be verified against source and tests.  
**Date:** 2026-10-24  
**Depends on:** `docs/database_tenancy_architecture.md`, `docs/database_boundary_phase0_review.md`, and `docs/repository_storage_entrypoint_inventory.md`

## Approved core decisions

The project owner approved multi-firm membership, globally unique normalized email, and separate platform versus firm roles as the working plan on 2026-10-26. This section records the historical decision. It does not itself define or change runtime behavior.

## Approved identity and authorization contract

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

Global identity plus explicit memberships supports a lawyer or staff member working with more than one firm without duplicating credentials, while keeping firm authorization explicit. It also makes account recovery and session revocation semantics easier to state consistently. This explains the rationale for the approved design; current schema and behavior are defined by the application implementation and migrations.

## Alternatives and trade-offs

| Model | Benefits | Risks / migration implications | Recommendation |
|---|---|---|---|
| Global identity + many-to-many firm memberships | Supports cross-firm professionals and consistent recovery | Requires a membership model, firm-scoped roles, session semantics, and migration of current `users.firm_id` data | Preferred if multi-firm membership is a real product requirement |
| Separate identity/account per firm | Clearer account-level separation and simpler membership semantics | Same person may have multiple accounts; duplicate emails, recovery, invitations, and support workflows become complex | Choose only if product explicitly requires firm-isolated identities |
| One identity permanently tied to one firm | Smallest near-term change | Blocks legitimate cross-firm work or encourages duplicate accounts; does not itself make storage tenant-safe | Do not assume without product-owner approval |

## Runtime implementation map (source-level orientation)

The current implementation uses the following separation (inspect the current source and migrations before making changes):

- `users`: global identity and authentication attributes; unique normalized email.
- `firm_memberships`: `user_id`, `firm_id`, firm-scoped role, status, created/updated timestamps, and actor/audit references.
- `firms`: firm lifecycle/status and non-secret tenant-catalog reference.
- Session state: global user identity plus a selected firm context that is revalidated against current membership. Do not trust a cached role indefinitely after membership revocation.
- Tenant catalog: stable firm ID → server-side storage reference and schema/lifecycle status. Credentials and raw connection strings remain in controlled secret/configuration systems, not user records or client payloads.

Relevant implementation entry points include `database_runtime.py`, `tenant_context.py`, `tenant_catalog.py`, `tenant_storage.py`, and the authentication/route integration in `app.py`. The application test fixtures in `tests/test_app_separate_database_runtime.py` and `tests/test_firm_security_policy.py` exercise synthetic multi-firm identities, membership revocation, firm switching, and tenant-scoped access. This list is an orientation aid, not proof that every branch is correct or tested; preserve existing migrations and data when changing these boundaries.

## Operational acceptance still required

Implementation of the architecture does not close deployment acceptance. Verify the following against the actual firm environment and its approved operating procedures:

1. **Membership revocation and sessions:** choose the maximum acceptable revocation delay and whether every request rechecks membership or uses a short-lived, invalidatable cache. Default safe behavior: deny on failed membership/catalog validation and invalidate affected cached tenant connections.
2. **Invitations and first firm owner:** define invitation expiry, email verification, who may invite, and the bootstrap path for the first firm owner. Never grant platform-admin privileges from a firm invitation.
3. **Platform-admin grants:** configure a separate, audited operator process for granting/revoking platform privileges; do not infer platform status from a firm role or email domain.
4. **Legacy deployment facts:** before migration, confirm actual user/account workflows, current database path, number of firms, session/token format, and backup/retention requirements. Repository fixtures are not evidence about production data.

Do not treat this historical design record as authorization to alter identity data, merge accounts, migrate databases, or cut over production. Require current operational evidence and approvals for those actions.

## Security acceptance criteria

Use these as continuing negative-authorization and tenant-isolation acceptance criteria. Source-level presence or a test fixture does not constitute a pass:

- A user with no active membership cannot select or infer a firm's database.
- A user who belongs to Firm A cannot access Firm B by changing path, query, body, header, cookie, or client-side state.
- A multi-firm user can access only the firms for which membership is active; switching firm changes the trusted server-side context and does not carry permissions across firms.
- Suspending or deleting membership prevents further access, including through existing sessions and cached connections.
- Firm roles do not imply platform corpus-review access.
- Account recovery, password reset, session revocation, and audit attribution behave correctly for a global identity and across multiple memberships.
- Tests exercise at least two firms, multiple users, revoked membership, invalid firm selection, and database-unavailable/unknown catalog mappings.
- Migration rehearsal accounts for every existing user and relationship, records reconciliation counts, and can roll back without modifying the source database.

## Scope and limits

This document is a historical design and acceptance reference; it is not the implementation, a migration specification, or a security certification. The current runtime uses separate control-plane, per-firm tenant, and shared legal-corpus database profiles. Do not infer production readiness from the architecture description or from repository tests that have not been executed. Preserve existing firm data and migrations, and require an approved backup/recovery plan before any operational database change.
