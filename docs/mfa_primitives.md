# MFA cryptographic primitives (non-integrated)

The module tools/mfa_primitives.py provides database-independent TOTP and recovery-code primitives. It does not add MFA to login, create enrollment routes, store secrets, or persist replay/one-time-use state.

## TOTP enrollment

- Generate a 160-bit Base32 secret with generate_totp_secret().
- Build an otpauth URI with build_totp_uri(); display it only during an authenticated enrollment flow. The application must never return the secret again after enrollment completes.
- Store the secret encrypted at rest using the application's approved secret-storage approach. Do not log it or place it in URLs outside the standard authenticator URI.
- Verify codes with verify_totp(). The return value is the matched time step, not just a boolean.

## Replay and concurrency boundary

The caller must atomically persist the accepted step and reject steps at or below the stored step. Concurrent login attempts must use a transaction/conditional update so the same code cannot be accepted twice. The helper's last_accepted_step argument is only a local check; it does not replace persistence.

## Recovery codes

generate_recovery_codes() returns plaintext codes for one-time display and salted scrypt hashes for storage. Persist only hashes, show plaintext once, and require recent re-authentication before generating or rotating codes. verify_recovery_code() checks one hash; the application must atomically mark that code as consumed in persistent storage. Never store plaintext codes or log verification inputs.

## Required integration work before claiming MFA is implemented

1. Coordinate with the database workstream on encrypted TOTP-secret storage, last accepted step, hashed recovery-code rows, one-time consumption, rotation/revocation, and migration/backups.
2. Add enrollment, confirmation, login challenge, disablement, and recovery routes with recent re-authentication.
3. Enforce MFA for platform/firm administrators before enabling policy-based enforcement.
4. Rate-limit enrollment, verification, and recovery; use generic responses that do not enable account enumeration.
5. Add audit events that never include secrets, TOTP values, recovery codes, or secret-bearing URIs.
6. Test transaction-level replay prevention and one-time recovery-code consumption against the real persistence adapter, including concurrent requests.
7. Conduct an independent security review before production use.

## Tests

    PYTHONPATH=. python tests/test_mfa_primitives.py

These tests use fixed timestamps and local fake values. They do not exercise application login or persistence and do not establish production readiness.
