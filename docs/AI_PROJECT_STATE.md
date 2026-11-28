# AI Project State — Legal for Today

**Repository:** [legal_copilot_latest](https://github.com/abdelmalek384/legal_copilot_latest)  
**Branch baseline:** main  
**Baseline SHA (session start):** 60b2ebd0d2a0940c904a6ac6afb54a4ac221fcec  
**Checkpoint:** 2026-11-28

## Current direction
Controlled law-firm pilot; fail-closed source trust, tenant isolation, security, and legal review boundaries remain release-critical. No production deployment or legal verification is claimed.

## Current engineering focus
- **AI-2 integration blocker #1903:** Persist and expose exact-version source-match evidence to the dedicated, non-production test-firm retrieval scope. Requires normalized schema, provenance adapter integration, dedicated scope, and exact-head Python 3.12 / tenant-isolation tests.
- Draft PR #1902 supplies a classifier prerequisite but is not an integrated retrieval implementation; do not treat as ready or merge without its acceptance gates.
- Other release gates remain unresolved, including storage deletion/recovery acceptance, legal-source rights and lawyer review, MFA/email staging acceptance, and manual UI/accessibility acceptance.

## Session evidence
- GitHub read-back inspected `tools/source_match_evidence.py`, `docs/STATUS.md`, issue #1903, and draft PR #1902 summary.
- Required prior continuity files were absent at the expected paths.
- Tests were not executed; this environment has no local checkout/runtime evidence.
- No legal sources, permission grants, verification status, or production readiness were changed.

## Next implementation
Resolve #1903 by inspecting the corpus schema, adapter, dedicated test-firm scope, and draft #1902 dependencies; implement only on a feature branch with synthetic data and explicit fail-closed tests. Keep Law 14/2025 excluded unless rights are explicitly cleared.
