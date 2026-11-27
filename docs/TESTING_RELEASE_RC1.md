# Legal for Today — Testing Release Candidate (RC1)

## Release objective

Produce a small-firm testing build of the existing application. RC1 is for workflow, usability, reliability, and security testing with **fictional data only**. It is not a production release, legal-answer validation, or permission to enter real client information.

Do not add features, expand the legal corpus, redesign the interface, or tune retrieval thresholds during RC1 preparation. Prefer fixing demonstrable blockers in existing flows over adding new audit tooling.

## Release decision

RC1 is not considered ready until every applicable gate below has actual execution evidence. Static source inspection, test files that merely exist, mocked tests, synthetic release manifests, and GitHub read-back are not acceptance evidence.

- [ ] Supported Python 3.12 environment created from a clean checkout.
- [ ] Dependencies install from the pinned lock file with hashes.
- [ ] Database initialization succeeds for control-plane, firm, and legal-corpus domains.
- [ ] First-firm owner bootstrap succeeds and credentials are not exposed in logs.
- [ ] App starts and the user can sign in/out; session expiry and recovery behavior are checked.
- [ ] Owner, lead, associate, and junior access restrictions are exercised using separate accounts.
- [ ] Client/matter creation, edit, search, status/stage, and access boundaries work.
- [ ] Tasks, deadlines, court sessions, fee records, notes, and history workflows work; date behavior is checked against Cairo calendar dates.
- [ ] Document upload, extraction, search, preview, classification review, original-file download, and deletion/retention boundaries are checked using safe fixture files.
- [ ] Legal Research can create, continue, rename, delete, and scope conversations; source displays and abstentions are understandable; matter-scoped context does not cross matter/scope boundaries.
- [ ] Save-research-to-matter flow works and creates an appropriately scoped note.
- [ ] Export and backup/recovery behavior is tested using synthetic data and non-production storage.
- [ ] Desktop Arabic RTL and English navigation are exercised; core flows are tested on a phone viewport.
- [ ] No client/matter data, files, research, sessions, or secrets are cached in the PWA offline shell.
- [ ] Security regression matrix and release checks are executed on Python 3.12; failures and blocked optional checks are recorded, not relabeled as passed.
- [ ] Known issues are triaged into blocking, non-blocking, and deferred categories with reproducible steps.

## Test protocol

1. Use a fresh, disposable test installation and fictitious firm/accounts/matters. Do not point test procedures at live data or a production database.
2. Follow the repository quick-start exactly and record the commit SHA, Python version, dependency-install outcome, database paths/configuration, and startup output (redact credentials and secret values).
3. Run `python tools/run_local_test_suite.py`, `bash scripts/local_release_check.sh`, and `bash scripts/security_regression_check.sh` from the repository root in Python 3.12. Save each complete result. If a runner cannot execute, record the exact blocker and mark it BLOCKED; do not claim a pass.
4. Exercise the user flows above manually. Record expected result, actual result, defect ID, and evidence location for each failed check.
5. Repeat the critical isolation checks with two separate test firms and multiple roles. Confirm that cross-firm and unauthorized matter reads/writes are denied—not merely hidden in the UI.
6. Do not configure outbound email, external model/data processing, S3 destructive operations, purging, or real-law ingestion during the basic test unless the test owner has explicitly set up a separate safe staging service and reviewed its data/security boundaries.
7. Stop and report a blocker if it could expose or destroy data, bypass access controls, or produce a misleading legal-verification claim.

## Legal-research test boundary

The repository does not currently contain a qualified Egyptian-lawyer-reviewed, complete, current legal corpus. Use fictional fixtures to exercise retrieval and UI contracts only. A returned source, matching article number, successful citation check, or plausible answer is not proof of legal accuracy or currentness. Do not present any research output as lawyer-verified. Real-law evaluation and approval require a qualified Egyptian lawyer and authorized legal-source evidence, and remain outside RC1.

## Tester defect report

For each defect, record:
- ID and severity (release-blocker / high / medium / low)
- RC1 commit SHA and test environment
- user role and fictional matter (no real personal data)
- exact steps to reproduce
- expected versus actual behavior
- screenshot/log/evidence reference with secrets and personal data removed
- whether repeatable and workaround, if any

## RC1 release status

All gates begin **NOT RUN**. No status may be changed to PASS without recorded execution evidence. No fabricated evidence, test accounts, approvals, witnesses, device checks, or benchmark reviews may be used to satisfy a release gate.
