# Dependency security and update policy

## Automated controls

- `.github/dependabot.yml` checks Python packages and GitHub Actions weekly. Dependency PRs are reviewed and tested; they are not auto-merged.
- `.github/workflows/dependency-audit.yml` runs `pip-audit --strict` against the direct and resolved transitive Python dependency tree on pull requests, pushes to main, and a weekly schedule.
- A failing or unavailable audit is a release blocker until the result is understood. Do not suppress an advisory merely to make CI green; document a narrowly scoped exception, affected versions, compensating controls, owner, and expiry if a temporary exception is unavoidable.

## Updating dependencies

1. Review the package's upstream release notes, supported Python versions, security advisories, and license.
2. Update `requirements.txt` or accept a reviewed Dependabot change.
3. Run the complete test suite and the dependency audit on the proposed versions.
4. Review transitive changes and ensure no dependency introduces telemetry, external network calls, or a new data-processing path without explicit assessment.
5. Record the reviewed versions and merge only after required checks pass.

## Current limitation: no deployment lockfile yet

The application requirements file pins most direct packages but leaves the AWS SDK as a compatible version range. It does not yet provide a fully resolved, hash-locked production requirements file for all transitive dependencies. Therefore, a clean `pip-audit` result is evidence about the versions resolved during that run, not proof that every future install will be byte-for-byte reproducible.

Before production, generate and review a Python 3.12 deployment lockfile with pinned transitive versions and artifact hashes, validate installation from that lockfile in a clean environment, and configure deployment to install only from it. Do not invent or hand-write hashes. Keep the source requirements file as the intentional dependency input and update the lockfile through a reproducible resolver process.

## Release requirements

- [ ] No unresolved high/critical known vulnerabilities in the exact deployment lock.
- [ ] Lockfile includes all transitive packages and verified artifact hashes.
- [ ] CI audit passes on the exact release candidate.
- [ ] Dependabot update PRs have a human review and full CI result.
- [ ] Dependency licenses and data-processing implications are reviewed.
- [ ] A rollback path exists for dependency updates that break runtime behavior.

The audit is an automated known-vulnerability check. It is not a software bill of materials, malware analysis, provenance attestation, or independent supply-chain security assessment.
