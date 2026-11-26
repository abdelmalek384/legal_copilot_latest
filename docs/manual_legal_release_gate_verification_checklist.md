# Manual legal release-gate verification checklist

**Status:** Prepared for local/manual execution only. No tests or gate commands were run in preparing this checklist.

## Safety and scope
- Use a disposable copy or the project workspace with a backup of candidate/register files.
- Do not download legal materials or change permission, lawyer-review, verification, or legal-status fields to force a pass.
- A synthetic fixture passing is only a structural test; it is not proof of legal correctness, authenticity, permission, or semantic accuracy.
- Keep the local worktree changes intact. Review diffs before and after any manual run.

## Suggested focused test sequence
From the repository root, in the user's local Python environment:

1. Run the dedicated release-readiness tests: `python -m unittest tests.test_legal_release_readiness`.
2. Run candidate catalog tests: `python -m unittest tests.test_legal_candidate_catalog`.
3. Run candidate registration tests: `python -m unittest tests.test_labour_law_candidate_registry`.
4. If those succeed, run the relevant broader suite as documented by the repository; do not assume these focused tests cover retrieval, citation entailment, isolation, or UI behavior.

## Record the result
For each command, record:
- command and interpreter/environment;
- pass/fail/skip and exit code;
- failing test names and traceback (if any);
- whether failure is environmental, structural, or requires maintainer triage.

Do not label the gate or candidate release-ready solely because the synthetic fixture passes. Confirm manually that the actual legal artifact and extracted text are reviewed, permission scope is evidence-backed, amendment/repeal status is confirmed by qualified counsel, and all required reviewer attestations are genuine and traceable.

## Known limitations to track
- Structural checks cannot independently prove evidence truthfulness or legal entailment.
- Host-local date comparisons may produce boundary differences near midnight relative to Egypt/Cairo. This remains a policy/specification question; do not alter date semantics without an explicit requirement and boundary tests.
- Hostname-level source link parity may not establish that rights cover every path/document on a portal. Treat scope as a review question, not an automatic defect.
- CI is intentionally not relied on for this handoff; execution is manual.
