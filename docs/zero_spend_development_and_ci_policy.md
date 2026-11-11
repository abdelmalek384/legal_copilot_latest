# Zero-spend development and CI policy

## Non-negotiable spending constraint

Legal Copilot development must incur **$0 in additional spending** unless the project owner explicitly changes this policy in writing.

- Keep GitHub Free. Do not add a payment method, upgrade the plan, enable paid usage, or increase Actions spending limits.
- Do not purchase Actions minutes or enable paid CI providers.
- Do not introduce paid hosting, storage, email, model, scanning, or other services as a workaround.
- Do not weaken security controls, skip tests, reduce coverage, or relabel an unverified check as passing to accommodate the constraint.

## CI execution and evidence

GitHub repositories, commits, branches, pull requests, diffs, and review remain usable without paid Actions. Remote GitHub Actions availability is not a prerequisite for continued development.

Until remote Actions are available within the zero-spend allowance:

1. Treat billing/quota/runner-provisioning failures that occur before a job starts as **infrastructure-blocked**, not as application test failures and not as passing tests.
2. Do not repeatedly rerun workflows that are blocked before job execution. Do not change billing or spending settings to make them run.
3. Run the repository's test and release-check commands locally on the developer's Mac with Python 3.12 and the repository's pinned dependency lock. Preserve the exact command, commit SHA, Python version, dependency-lock identity, exit code, and test output in the evidence record.
4. Report local results separately from GitHub Actions results. A local pass does not imply that remote CI passed; a blocked remote workflow does not imply that the code failed.
5. Review pull-request diffs manually for correctness, security, tenant isolation, migration safety, dependency changes, and test adequacy. Do not recommend merging solely because a workflow is blocked or because a local command passed.
6. Mark any check that could not be executed as **NOT RUN** or **BLOCKED**, with the reason. Keep hardware, staging, production, external-provider, and lawyer-review gates distinct from automated tests.

## Local test execution

Use Python 3.12 and the dependency lock committed with the repository. Prefer the repository's local release-check and focused security-regression scripts when present on the checked-out revision. Run the full test suite as defined by the repository's workflow/test inventory; do not substitute a smaller selection without recording the omitted tests and reason.

A clean local run should record at least:

- repository and exact commit SHA;
- Python version and operating system;
- lockfile path and hash;
- exact command(s) executed;
- start/end time and exit status;
- passed, failed, skipped, and blocked test counts;
- full logs and any environment-dependent omissions.

Do not include client files, secrets, credentials, or production data in test evidence. Use synthetic fixtures only.

## Scope and legal-quality safeguards

The zero-spend policy does not relax legal-intelligence safeguards. Retrieval, Arabic normalization, negation handling, source matching, citation validation, and lawyer-review packet generation must retain their tests and provenance requirements. Synthetic or candidate legal material must never be represented as verified Egyptian law. Lawyer verification and legal-status approval remain independent gates.

## Reconsidering remote CI

Remote CI may be reconsidered only if it becomes available within the existing no-cost allowance and without adding payment methods, paid usage, or spending limits. Any change that could incur cost requires explicit owner approval first.

## Current operational note

This document records the project's policy; it is not evidence that local tests have been run or that remote CI is currently disabled in repository settings. Confirm the account's Actions state and capture local execution evidence separately.