# Candidate Registry Consistency — Remote Review Notes (2026-11-26)

## Scope and limitation

This is a read-only review of the public default branch, not the user's local branch `fix/legal-candidate-registry-consistency`. GitHub did not resolve that branch, so its local changes are not visible remotely. No local worktree files were read, changed, staged, reset, or overwritten. These notes do not claim test execution.

## Findings from the default-branch seeder

- `tools/seed_legal_candidates.py` validates catalog structure, duplicate source/document IDs, source references, discovery-only candidate status, HTTPS URL cleanliness, and a subset of permission states.
- The permission-parity check validates each candidate source against a matching canonical register record; it does not require the catalog to enumerate every source in the permission register (which may be intentional).
- Source-page parity currently compares hostname rather than exact canonical URL. This is a deliberately noted review point, not a confirmed vulnerability: same-host URL divergence can be legitimate, but a stricter policy may be preferable for stable registry identifiers.
- Seed writes are transactional and fail on conflicting existing source/document metadata rather than silently overwriting.
- Candidate registration/seeding must not be treated as a permission grant, source verification, corpus ingestion, or legal-currentness assertion.

## Manual acceptance checklist for the local branch

1. Preserve the pre-existing worktree and all backup files; inspect diffs before any edits.
2. Check duplicate IDs, document-to-source references, and required fields in both JSON registries.
3. Confirm that permission parity compares collection and commercial-reuse states and does not silently upgrade unknown/restricted states.
4. Confirm host/path consistency behavior is documented and intentional; avoid introducing permission assumptions based on host matching alone.
5. Confirm candidate registration remains metadata-only, idempotent, transactional, and non-overwriting on conflicts.
6. Confirm candidate records do not create article chunks, source verification, review approval, or search eligibility.
7. Run the focused test slices in `docs/AI1_legal_test_handoff_2026-11-26.md` manually at the owner's test window, capture exact failures, and avoid retrying unchanged failures.
8. After manual test results, record the commit SHA and actual outcomes (including skipped/unavailable checks). Do not report unrun checks as passing.

## Status

- Remote static review: limited to publicly visible default-branch files.
- Local branch review: blocked because the branch is local-only/not remotely resolvable.
- Test execution: none.
- CI: unavailable due billing; no retry.
- Changes: this note only; no application code or legal-source records altered.
