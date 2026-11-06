# First platform administrator bootstrap — proposal

**Status:** The one-time CLI implementation is merged (PR #729) and its automated tests pass. It is not yet operationally accepted for production: an authorized operator must rehearse the first bootstrap on the target deployment, have an independent witness verify the resulting role and audit event, and complete the separate privileged-recovery acceptance gate.

## Implemented behavior

Use a one-time, CLI-only bootstrap command on an authorized operator host after a clean control-plane install. Do not add a public or authenticated web route for first-platform-admin creation.

The command implements the following controls:

1. Resolve an existing global identity by normalized email or explicit user ID; do not create a global identity implicitly.
2. Require that identity to be active and have an active firm membership with the **admin** firm role. Firm-admin status does not itself grant platform privileges; it is only an eligibility precondition for this one-time bootstrap.
3. Require a non-empty reason, an explicit confirmation flag, and a restricted operator/change-record reference. Do not accept a password, token, or secret in the command line.
4. Start an immediate write transaction on the control-plane database.
5. Refuse if any active **platform_admin** role already exists, if a successful bootstrap event already exists, or if the target identity/membership is disabled or suspended.
6. Insert the initial **platform_admin** role and an append-only **platform_admin_bootstrap_cli** security event in the same transaction. The event should record the target user ID, reason, command method, and operator/change-record reference; never store the raw email or any secret.
7. Roll back both changes if either insert or commit fails. Print only a safe result, not identity secrets or database contents.
8. Refuse all subsequent invocations. Later role grants/revocations must use the existing actor-authorized CLI and last-platform-admin protection.

The initial bootstrap should be performed under a recorded change with an independent reviewer/witness. The operator should verify the resulting role and audit event through the bounded read-only platform audit command, then secure the control-plane file and operator access.

## Verified code controls

- [x] The bootstrap audit event is migration-managed and append-only.
- [x] Role creation and the audit event commit atomically; failure-injection tests cover rollback.
- [x] Tests cover prior bootstrap/admin state, inactive identities or memberships, missing reason/confirmation, and ineligible targets.
- [x] No HTTP route or self-service flow exists for initial platform-admin creation.
- [x] Output and audit data avoid raw email, passwords, session cookies, tokens, and database paths.
- [ ] Operationally create and verify a second platform administrator through the normal audited grant CLI before routine platform administration is handed over.

## Remaining operational acceptance

The implemented command requires an existing active global identity with an active firm-admin membership, explicit confirmation, a non-empty reason, and restricted operator/change references. It refuses an existing active platform administrator and any prior successful bootstrap event, and writes the role plus append-only audit event atomically. It does not cryptographically authenticate the human operator. The trusted operator host, recorded change, independent witness, privileged-account recovery rehearsal, and first-deployment sign-off remain mandatory before production use.
