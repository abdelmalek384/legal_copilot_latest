# AI-2 manual implementation checkpoint — 26 November 2026

**Scope:** Small security hardening change to logout/session revocation. This is implementation evidence, not runtime acceptance or pilot approval.

## What changed directly on main

- Logout continues to revoke the current user's session and commit that revocation first.
- It now attempts a platform security audit event (`logout`) with only actor/target identity IDs and a minimal method/session-revoked detail.
- Audit insertion is deliberately best-effort after revocation: if logging fails, the logout remains successful, the cookies are still cleared, and the response includes `audit_warning: true`. The failure does not roll back or restore the revoked session.
- Added tests for (1) successful logout creates the audit event and revokes the session, and (2) injected audit failure still logs the user out and surfaces the warning.
- These commits were made directly to `main`, not left as a PR: app handler `8e70e8fd8e29b6d674aed47b024fa9d1facf3398`, regression tests `77a85315cf54a60504dbd8407905f31bb2796511`, blocker note `1c37ec2c6f26deadd653443fba371122d652ba24`.

## Progress update (conservative; estimates, not test pass rates)

| Workstream | Previous | Current | Change |
|---|---:|---:|---:|
| Security / tenant isolation | 84.7% | 84.9% | +0.2 pp |
| Documents / file handling | 99.1% | 99.1% | 0.0 pp |
| Deployment / backup / recovery | 46.7% | 46.7% | 0.0 pp |
| Test execution readiness | 10% | 10% | 0.0 pp |
| AI-2 overall | 76.0% | 76.1% | +0.1 pp |

The progress increase is only a small source-level implementation estimate. The tests are **added but not executed**. GitHub Actions were not invoked. No local checkout/runtime was available in this work session, so no repository tests, browser acceptance, two-firm test, or backup/restore drill are claimed as passing.

- Follow-up after source review: the event table CHECK constraint originally rejected the new `logout` event. Added migration `0009_platform_security_events_logout.sql` preserving existing audit IDs/rows and append-only triggers, and a migration test covering the preserved history, new event, integrity checks, and trigger behavior. Direct-main commits: migration `7ed1e29`, migration test `121593f`, blocker follow-up `de9646a`. Tests are still not executed.

## Remaining release blockers

- Run the focused identity lifecycle tests and the complete test/security/release suites on exact main in the documented Python 3.12 environment.
- Verify browser logout, cookie clearing, session revocation, and firm switch behavior in desktop and mobile browsers.
- Complete two-firm isolation acceptance and witnessed backup/restore.
- Keep production/pilot release gated until these checks and the separate AI-1 legal-source/lawyer review are satisfied.

## Test commands for later local run

```bash
python3.12 -m pytest tests/test_identity_lifecycle.py -q
python3.12 -m pytest tests/test_route_auth_audit.py tests/test_tenant_route_inventory_coverage.py -q
bash scripts/security_regression_check.sh
python3.12 tools/run_local_test_suite.py
bash scripts/local_release_check.sh
```

Run tests later, at the user's planned local-test window, not now. Do not treat the list above as executed evidence.
