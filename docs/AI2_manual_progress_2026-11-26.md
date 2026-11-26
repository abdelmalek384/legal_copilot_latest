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
| Security / tenant isolation | 84.7% | 85.1% | +0.4 pp |
| Documents / file handling | 99.1% | 99.1% | 0.0 pp |
| Deployment / backup / recovery | 46.7% | 46.7% | 0.0 pp |
| Test execution readiness | 10% | 11% | +1.0 pp |
| AI-2 overall | 76.0% | 76.2% | +0.2 pp |

The progress increase is only a small source-level implementation estimate. The tests are **added but not executed**. GitHub Actions were not invoked. No local checkout/runtime was available in this work session, so no repository tests, browser acceptance, two-firm test, or backup/restore drill are claimed as passing.

- Follow-up after source review: the event table CHECK constraint originally rejected the new `logout` event. Added migration `0009_platform_security_events_logout.sql` preserving existing audit IDs/rows and append-only triggers, and a migration test covering the preserved history, new event, integrity checks, and trigger behavior. Direct-main commits: migration `7ed1e29`, migration test `121593f`, blocker follow-up `de9646a`. Tests are still not executed.

- Last refinement: logout audit rows include the active firm ID, and the success regression checks that tenant context is retained (`9222b59`, `fb80572`, checkpoint `bb37549`).

- Additional manual-gate integration: added `test_identity_lifecycle.py` and `test_platform_security_audit_migrations.py` to the security regression script, so the new logout behavior and schema migration are included in the documented local security run. This improves test discoverability/integration, not test execution evidence (`9441f7a`, `982237d`).

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

## Follow-on regression wiring — 2026-11-26

- Added the existing `tests/test_uploaded_filename_sanitization.py` regression to `scripts/security_regression_check.sh` and the explicit `.github/workflows/tests.yml` test list. This is not a new feature; it ensures the existing upload filename path/bidi/control-character defenses are included in both regression inventories.
- Direct-main commits: security matrix `87f9c873d17ffe25f999f5a202ae628385409955`; explicit workflow registration `07307d31354d13145cadea4fe39b44fd99d6286f`.
- Manual source check only: the module is present in both inventories. No tests were executed and no GitHub Actions were invoked.
- Progress: security / tenant isolation remains 85.1%; documents / file handling remains 99.1%; deployment / backup / recovery remains 46.7%; test execution readiness increases conservatively from 11.0% to 11.2% for better regression coverage integration (not test execution); AI-2 overall remains 76.2%.
- Release gates remain: execute Python 3.12 suites locally, verify browser/device workflows, complete two-firm isolation, and perform a witnessed backup/restore.

## Expanded manual security coverage — 2026-11-26

- Expanded the focused security regression script with six existing high-value modules: auth-cookie expiry middleware, per-firm MFA/security policy, separate-runtime security-audit reads, bounded original-file audit history, staged-original recovery, and disposable-copy database migration rehearsal.
- Commit: `fdad149733411b9dd298b8325c99a877d7822c68`.
- Manual inventory comparison: all modules named by the security script exist in the repository and are explicitly present in `.github/workflows/tests.yml`; no duplicate entries were found. This is source-list inspection only, not test execution.
- Test execution readiness: 11.2% to 11.5% (+0.3 pp) for broader focused coverage. Security / tenant isolation remains 85.1%; documents / file handling remains 99.1%; deployment / backup / recovery remains 46.7%; AI-2 overall remains 76.2%.
- No GitHub Actions were run. No repository tests were executed. Browser/device acceptance, two-firm isolation, and witnessed restore remain release gates.

- Follow-up consistency correction: the manual inventory comparison caught that `test_bounded_original_file_audit_history.py` had not yet been added to the explicit workflow. Added it immediately; commit `cd38dc4b5309a9685fa888d959293e48ca8e98e3`. The full 100-module security matrix now has explicit workflow entries (to be rechecked after this commit).
- Test execution readiness: 11.5% to 11.6% (+0.1 pp) for closing the workflow-registration gap. This is integration readiness only; no test or CI run is claimed.
