# First platform administrator bootstrap — proposal

**Status:** Decision required; no bootstrap command or web endpoint is implemented by this proposal. The existing platform-role grant/revoke CLI is intentionally actor-authorized and cannot grant the first platform administrator when no platform administrator exists.

## Recommended default

Use a one-time, CLI-only bootstrap command on an authorized operator host after a clean control-plane install. Do not add a public or authenticated web route for first-platform-admin creation.

The command should:

1. Resolve an existing global identity by normalized email or explicit user ID; do not create a global identity implicitly.
2. Require that identity to be active and have an active firm membership with the **admin** firm role. Firm-admin status does not itself grant platform privileges; it is only an eligibility precondition for this one-time bootstrap.
3. Require a non-empty reason, an explicit confirmation flag, and a restricted operator/change-record reference. Do not accept a password, token, or secret in the command line.
4. Start an immediate write transaction on the control-plane database.
5. Refuse if any active **platform_admin** role already exists, if a successful bootstrap event already exists, or if the target identity/membership is disabled or suspended.
6. Insert the initial **platform_admin** role and an append-only **platform_admin_bootstrap_cli** security event in the same transaction. The event should record the target user ID, reason, command method, and operator/change-record reference; never store the raw email or any secret.
7. Roll back both changes if either insert or commit fails. Print only a safe result, not identity secrets or database contents.
8. Refuse all subsequent invocations. Later role grants/revocations must use the existing actor-authorized CLI and last-platform-admin protection.

The initial bootstrap should be performed under a recorded change with an independent reviewer/witness. The operator should verify the resulting role and audit event through the bounded read-only platform audit command, then secure the control-plane file and operator access.

## Required implementation and test gates

- A migration-managed audit event type for the initial bootstrap, preserving prior platform audit rows and append-only triggers.
- Atomic role-plus-event transaction, with failure-injection coverage proving neither row persists if audit insertion fails.
- Refusal tests for an existing platform administrator, prior bootstrap event, disabled identity, suspended/inactive firm membership, missing reason, missing confirmation, and a target without an active firm-admin membership.
- No HTTP route or self-service flow for initial platform-admin creation.
- Audit output must not include raw email, passwords, session cookies, tokens, or database paths.
- A second platform administrator must be created through the normal audited grant CLI after the first bootstrap, before routine platform administration is handed over.

## Decisions needed from the product owner

Approve or change these recommended defaults before implementation:

1. Must the initial target be an active firm administrator, or may another active global identity be selected?
2. Is an independent reviewer/witness in the change record sufficient, or must the CLI require a second operator's signed approval artifact?
3. Should a successful bootstrap event permanently disable the bootstrap command even if every platform-admin role is later revoked? Recommended: yes; recovery from loss of all platform administrators should be a separate break-glass procedure.
4. Should the operator identify the target by immutable user ID only, or may normalized email be accepted as a lookup input? Either way, the audit event should store the target user ID, not raw email.

Until these decisions are approved, do not add a bootstrap bypass or grant platform roles through direct SQL. The current first-platform-admin bootstrap blocker remains open.
