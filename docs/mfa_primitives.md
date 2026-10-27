# MFA and self-service authenticator recovery

## Implementation status

The TOTP primitives are now integrated into separate-database authentication. The control plane stores encrypted TOTP secrets, replay state, salted scrypt recovery-code hashes, one-time-use timestamps, throttling state, and append-only MFA security events. Existing privileged sessions are invalidated for MFA verification when the migration is applied.

MFA enrollment and verification are available at:
- POST /account/mfa/enroll
- POST /account/mfa/confirm
- POST /account/mfa/verify
- POST /account/mfa/recovery-codes/rotate
- POST /account/mfa/re-enroll
- POST /account/mfa/disable

The login response and GET /session indicate whether the client must enroll or complete an MFA challenge. A session that has not completed a required challenge is restricted to the MFA flow, session status, and logout. The legacy single-database compatibility mode does not provide the MFA integration; production preflight requires separate-database mode.

## Configuration

- Generate a dedicated encryption key with: python manage.py gen-mfa-key
- Store it in the deployment secret manager as MFA_ENCRYPTION_KEY.
- Never reuse BACKUP_KEY, ADMIN_TOKEN, or an LLM credential for MFA encryption.
- Keep the same MFA_ENCRYPTION_KEY available during backup restoration; losing it makes encrypted TOTP secrets unrecoverable. Recovery codes allow users to re-enroll only if the account/session recovery requirements can still be met.
- Set MFA_ENFORCEMENT=admins_required to require MFA for firm administrators and platform administrators/reviewers. Use all_required to require it for every user. optional is intended for development only; production preflight rejects optional mode.
- Keep MFA_ENCRYPTION_KEY out of source control, logs, issue comments, and backup bundles. Back it up through the secret-management system with separate access controls.

## Security behavior

- TOTP secrets are encrypted at rest and shown only during enrollment/re-enrollment. Responses containing setup secrets or recovery codes use no-store headers.
- Accepted TOTP steps are persisted transactionally, so the same step cannot be replayed. Concurrent verification uses an immediate SQLite transaction.
- Recovery codes are shown once; only salted scrypt hashes are stored, and successful use atomically marks a code consumed.
- Failed enrollment/verification attempts are throttled. Recovery and enrollment responses do not expose secrets or codes in logs.
- Recovery-code rotation requires the current password and a valid authenticator code. Replacing a lost authenticator requires a recent verified MFA session plus the current password; a required-MFA administrator cannot disable MFA.
- Security events are append-only and record factor/outcome metadata only. They must never contain TOTP values, recovery codes, secret-bearing URIs, or passwords.
- SMTP/account email is not used as a substitute for MFA recovery.

## Validation

Run:

    PYTHONPATH=. python tests/test_mfa_primitives.py
    PYTHONPATH=. python tests/test_mfa_account_security.py
    python tools/deployment_preflight.py --strict

The automated integration tests use temporary databases and synthetic accounts; they do not validate a production secret manager, real browser-based authenticator setup, or an independent security review. Before production, rehearse first-admin enrollment, lost-device recovery, key rotation/backup restoration, and emergency administrator recovery. Keep the release gate open until an independent security review passes.
