# Invitation and account-recovery policy — proposal

**Status:** Recommended defaults were approved on 2026-10-27. A first implementation is under review in draft PR #690; it is not merged or release-ready. SMTP delivery remains deployment-configured, and the exact provider must be reviewed before production use.

## Identity model constraints

- A global identity has one globally unique normalized email and may have memberships in multiple firms.
- A firm membership grants access only to that firm's database and authorized cases. It does not grant platform roles.
- Platform roles remain a separate control-plane privilege domain.
- Membership creation, suspension, role changes, credential changes, and token consumption must be audited atomically with the state change.
- Email, invitation tokens, password-reset tokens, passwords, and session cookies must not be written to logs or audit details.

## Recommended invitation flow

1. A firm administrator creates an invitation for a normalized email, firm ID, and allowed firm role. The server derives the firm from the authenticated active-firm context; the request cannot select an arbitrary tenant database.
2. Store only a cryptographic hash of a randomly generated one-time token in the control plane. Bind it to the target firm, normalized email, invited role, inviter user ID, creation time, expiry, and status.
3. Recommended expiry: 24 hours. Re-sending an invitation revokes any previous outstanding token for the same email/firm pair. Token comparison is constant-time and acceptance is single-use.
4. If the global identity already exists, invitation acceptance requires authentication as that identity and creates only the new firm membership. It must not create a second global identity or change memberships in other firms.
5. If the identity does not exist, acceptance verifies the invited email through the configured email channel, then creates the global identity and firm membership in one control-plane transaction. Credential creation must meet the existing password-strength policy or use the approved SSO flow.
6. The membership insert and append-only audit event commit together. If any step fails, no identity/membership is left partially created. The invitation token is consumed in the same transaction.
7. Invited users receive no platform role. Platform-role changes use the separate audited CLI workflow.

## Recommended account-recovery flow

1. A user submits an email address to request recovery. Return the same response for known and unknown identities so the endpoint does not disclose account existence.
2. Rate-limit by network source and normalized identity using the application's established throttle approach. Do not rely only on a client-supplied forwarding header.
3. Generate a cryptographically random one-time token, store only its hash, and bind it to the global identity. Recommended expiry: 30 minutes. A new token revokes older outstanding reset tokens for that identity.
4. Deliver the token only through the configured verified email channel. Never return it in the HTTP response, expose it in a URL under an untrusted origin, or log it.
5. On consumption, validate expiry and one-time status, update the global credential, revoke all sessions across every firm membership, mark the token consumed, and append the password-reset audit event in one control-plane transaction.
6. Failure of the credential/session/audit write rolls back the complete change. A token is not consumed if the transaction fails.
7. Do not automatically restore suspended memberships, re-enable disabled identities, or grant any firm/platform role during password recovery.

## Operator recovery

Until an approved email delivery provider and self-service flow exist, retain the audited CLI password-reset path as a restricted operator procedure. It must require a reason, revoke sessions, avoid raw email/password audit details, and never bypass disabled-identity or membership state. Operator recovery is not a substitute for a tested user-facing recovery workflow.

## Decisions needed from the product owner

Approve or change these recommended defaults before implementation:

1. **Email delivery:** which transactional email provider or identity provider will deliver invitations and recovery links?
2. **Expiry:** approve 24-hour invitation tokens and 30-minute password-reset tokens, or specify alternatives.
3. **Inviter authority:** may every firm admin invite any firm role, or are some roles reserved for a separate approval process?
4. **Identity verification:** is verified email sufficient for a new global identity, or is SSO/MFA required before membership activation?
5. **Recovery assurance:** should password reset require MFA, an additional identity check, or both for privileged firm administrators?
6. **Membership changes:** should suspension/revocation invalidate only the selected firm's session context immediately, or invalidate all global sessions? Current behavior is intended to preserve access to other active firm memberships while preventing access to the suspended firm.
7. **Retention:** how long are consumed/expired invitation and recovery-token hashes retained for audit, and when are they purged?

## Acceptance gates

Before enabling invitations or self-service recovery:

- Add migration-managed token tables with unique constraints and indexes.
- Use hashed, high-entropy, single-use tokens; test expiry, replay, resend invalidation, and concurrent consumption.
- Test global identity uniqueness and membership creation across multiple firms.
- Test atomic rollback on audit-write failure and immediate session revocation after password reset.
- Test generic responses, rate limits, CSRF/Origin protections, secure cookies, and no-store responses.
- Confirm tokens and personal data are absent from application logs and platform audit details.
- Obtain independent security review of the chosen email/identity provider integration.

Draft PR #690 implements migration-managed token ledgers, SMTP delivery, firm-admin invitations, token-bound acceptance, generic recovery requests, session-revoking password resets, and regression tests. Until the PR is merged with passing CI and the deployment email provider is reviewed, this document does not establish release readiness; initial platform-admin bootstrap and broader lifecycle acceptance remain separate blockers.
