# Static application security analysis

## Automated CodeQL coverage

The repository's `.github/workflows/codeql.yml` runs GitHub CodeQL's `security-extended` query suite for:

- Python backend and tooling.
- JavaScript frontend code embedded in the static web client.

The workflow runs on pull requests and pushes to `main`, weekly, and by manual dispatch. Findings are uploaded to GitHub code scanning; they are not silently suppressed or auto-dismissed by this workflow.

## Triage policy

1. Review every new high/critical alert before release. Confirm the affected code path, reachability, trust boundary, and whether untrusted user/case/document data can reach the sink.
2. Fix exploitable findings and add regression tests. Do not add broad suppressions to make the scan green.
3. For a false positive or accepted low-risk finding, document the exact alert/rule, affected code, reasoning, compensating controls, reviewer, and review date. Use the narrowest supported suppression.
4. Re-run CodeQL on the fix and verify that the alert is resolved in the resulting commit.
5. Keep independent penetration testing and security review as separate release gates.

## Limitations

CodeQL is static analysis. It does not prove runtime authorization, firm isolation, dependency integrity, secret handling in deployment, infrastructure configuration, or absence of vulnerabilities. It does not replace `pip-audit`, manual review, dynamic testing, or an independent security assessment.
