# Identity session, invitation, and platform-role policy — proposal

**Status:** Proposed defaults for explicit product/security-owner approval; not implemented  
**Depends on:** The approved global identity, multi-firm membership, and separate platform/firm-role decisions  
**Safety boundary:** This document changes no application behavior, schema, or data.

## Goals

- Let one global identity belong to multiple firms without duplicating accounts.
- Make each firm-scoped request depend on current, server-verified membership.
- Prevent a firm role from granting platform-wide corpus or administration access.
- Make account recovery, membership changes, and platform-role changes auditable.
- Avoid silently merging or reassigning legacy identities.

## Recommended session model

1. A session belongs to a global user identity, not to one firm. Store only a cryptographic hash of the opaque session token; never store the raw cookie token.
2. Session state should include creation/expiry, revocation, last-activity metadata, and an optional selected firm ID. The selected firm is a convenience hint, **not authorization**.
3. On every firm-scoped request, resolve the authenticated user and selected firm through the trusted control-plane membership table. Require both the firm and membership to be active. Do not trust a submitted firm ID, database path, or connection string as proof of access.
4. If one membership is suspended or revoked, deny access to that firm on the next request. Do not automatically revoke all sessions for a multi-firm user unless the account itself is disabled or a credential-recovery policy requires it; otherwise a membership change in one firm would unnecessarily disrupt unrelated memberships.
5. If an account is disabled or its password is reset, revoke all sessions for that global identity. Platform-role grants and revocations must be checked against current control-plane state on every platform-protected operation, not trusted from a stale session claim.
6. Apply existing cookie protections (HTTPS-only, HttpOnly, SameSite, and CSRF checks for mutations). Session lifetime and idle timeout values must be set by the deployment/security owner; this proposal deliberately does not invent a production TTL.

## Recommended invitation and bootstrap model

- No public signup flow may choose a platform role or create a platform administrator.
- The first platform administrator must be established through an out-of-band, operator-controlled bootstrap process with a one-time audited record. It must not rely on a default account or a hard-coded credential.
- Firm creation/provisioning and initial firm-admin assignment must be an explicitly authorized workflow. A firm admin may manage that firm's membership only within an approved permission boundary and may not grant platform roles.
- An invitation should be single-use, store only a hash of its random token, expire, be revocable, and record the inviter, target normalized email, firm, intended firm role, creation/expiry/acceptance timestamps, and audit references.
- Accepting an invitation must authenticate the existing global identity or create one through the normal verified signup flow, then require the normalized email to match the invitation. An existing global email is not a reason to create a duplicate account or automatically merge identities.
- Ambiguous legacy accounts, normalized-email collisions, and unclear firm ownership remain quarantined until resolved from authoritative evidence. Do not infer memberships from matching names or historical default firm IDs.

## Platform-role governance

- Keep platform roles in a separate control-plane role domain from firm membership roles.
- Grant/revoke platform roles only through an explicitly authorized platform workflow. Record actor, target, role, action, timestamp, and a reason/reference in a protected audit log.
- Firm membership or a firm-admin role must never imply platform reviewer/admin permission.
- A platform administrator's administrative role must not automatically authorize reading confidential matter contents; any exceptional support access needs a separate, narrow, time-limited, audited process.

## Decisions still requiring owner approval

- Session absolute lifetime and idle timeout.
- Whether any membership change should revoke only the selected-firm session context or also force reauthentication.
- The exact platform-role grant/revoke actors and break-glass procedure.
- Invitation expiry, who may invite each firm role, and whether email verification is required before acceptance.
- Session/audit retention periods and legal retention requirements.
- The one-time bootstrap mechanism supported by the actual deployment environment.

## Required tests before runtime integration

- One identity can access two firms only while each membership is active.
- Suspended/revoked membership is denied immediately on the next request; an unrelated active membership continues to work.
- A client-selected firm ID never bypasses membership checks, and no request can choose a storage path.
- Disabled users and revoked sessions are denied; password reset revokes all sessions under the approved policy.
- Platform roles are independently granted/revoked and never inherited from firm roles.
- Invitation tokens are single-use, expire/revoke correctly, and cannot attach a mismatched email or create a duplicate global identity.
- Session switching, CSRF, cookie settings, account recovery, and concurrency behavior pass adversarial tests.
- Migration and rollback are rehearsed on disposable copies; no legacy identity is merged or reassigned automatically.

## Implementation boundary

This proposal does not authorize production migration, account merging, legacy ownership repair, or platform-role changes. Implement schema and runtime integration only after the outstanding policy decisions are approved and the relevant acceptance tests are in place.
