# Agent instructions — Legal Copilot

## Project purpose
Legal Copilot is an Arabic-first legal case-management and research assistant for Egyptian legal professionals. Treat legal accuracy, tenant isolation, privacy, and auditability as release-critical.

## Working agreement
- Work only in the currently opened Legal Copilot checkout. Never treat the user's home directory as a project root.
- Before editing, inspect `git status --short --branch`, the current branch, recent commits, relevant files, and existing tests.
- Never work directly on `main`. Create one focused branch per task, named `codex/<short-task-name>` or `fix/<short-task-name>`.
- Do not overwrite, reset, clean, or discard pre-existing user changes. If the worktree is not clean, stop and report the exact files before proceeding.
- Keep changes small and scoped. Do not refactor unrelated code or repeat completed work.
- Do not run two agents on the same files at the same time. Coordinate ownership and hand off using a branch/PR.
- Before committing, inspect `git diff --check`, `git diff --stat`, and the full diff. Never commit secrets, credentials, local databases, customer data, generated artifacts, or virtual environments.
- Do not force-push, rewrite shared history, merge a PR, or disable required/security checks without explicit authorization.
- Report exact commands and actual results. Never claim tests, scans, CI, or deployment passed unless they were run and the result was observed. Separate not-run, blocked, and failed checks.

## Legal evidence rules
- Never label Egyptian legislation or legal propositions as lawyer-verified without explicit sign-off by a qualified Egyptian lawyer.
- Machine matching, Gazette comparison, extraction, or automated checks may support only a label such as `source-matched, not lawyer-reviewed`.
- Preserve existing `verified=0` flags unless documented human sign-off is supplied and the authorized workflow explicitly changes them.
- Do not invent statutory text, article numbers, case citations, court principles, effective dates, amendments, or currentness claims.
- Legal answers must be grounded in retrieved, traceable sources. If the sources do not support an answer, abstain or say the information was not found.
- Keep fictional fixtures and test cases clearly separated from real Egyptian legal authorities.

## Engineering and security rules
- Preserve tenant isolation and per-firm access boundaries. Do not move or expose private firm data into shared legal-corpus paths.
- Treat authentication, authorization, session handling, uploads, exports, backups, and audit logs as security-sensitive.
- Do not weaken security controls or remove tests merely to obtain a green CI run.
- Follow the repository's pinned dependency files and documented runtime version. Prefer the project's Python 3.12 lock file when running its supported test environment; do not silently substitute another Python version.
- Run the narrowest relevant tests first, then broader checks when feasible. Record environment limitations and exact failures.
- Inspect existing architecture and migration conventions before changing schemas, database runtime, or tenant data. Avoid database changes unless explicitly assigned.

## Task completion report
For every task, report:
1. What changed and why.
2. Exact files changed.
3. Tests/checks run and their actual outcomes.
4. Checks not run and why.
5. Security, legal-evidence, migration, or compatibility risks.
6. Branch and PR link, if created.
7. Remaining blockers and the next unblocked task.

## Scope discipline
- Follow the task's explicit ownership boundaries. Do not take over database or product/UI work assigned to another agent.
- If blocked by missing source material, credentials, lawyer review, external service access, or unavailable hardware, document the blocker and move to an independent unblocked task.
- Do not manufacture progress percentages. Base completion estimates on verified acceptance criteria.
