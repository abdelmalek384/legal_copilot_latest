### Identity email acceptance

The SMTP configuration preflight validates required settings and encrypted transport; it does not prove that the configured provider accepts or delivers messages. Use the controlled probe only against a mailbox owned by the operator:

```bash
COPILOT_ENV=staging python tools/verify_identity_email.py \
  --recipient <controlled-staging-mailbox> \
  --confirm-controlled-mailbox
```

The command reports SMTP submission acceptance only. A named operator must independently confirm mailbox receipt, sender identity, spam placement, SPF/DKIM/DMARC results where applicable, and message integrity. For a production probe, use an approved change window and require both explicit flags:

```bash
COPILOT_ENV=production python tools/verify_identity_email.py \
  --recipient <controlled-production-mailbox> \
  --confirm-controlled-mailbox \
  --confirm-production-send
```

Then exercise the real invitation and recovery flows using synthetic identities: delivery and link origin, token expiry, resend invalidation, single-use/replay refusal, generic known/unknown recovery responses, session revocation, audit rollback, and no token/credential leakage. Run the multi-host rate-limit test against at least two actual application hosts sharing the deployed control-plane/rate-limit backing store; the repository test with independent runtime instances is not a substitute for that deployment test. Capture provider event IDs and redacted evidence in the restricted acceptance store.

For privileged recovery/bootstrap, use the one-time CLI only on the target deployment from the restricted maintenance environment. A distinct witness must verify the resulting platform role, immutable audit event, and that no unintended firm membership or role was granted. Rehearse privileged-account assisted recovery, MFA/recovery-code handling, session revocation, and the documented offline two-person last-platform-admin recovery procedure. Never rehearse with a real client account or disclose a token/secret to the witness.

Do not mark `production_identity_email` or `privileged_recovery_bootstrap` passed until the corresponding actual deployment evidence, named verifier, timestamps, and required witness are recorded in the controlled acceptance manifest.

