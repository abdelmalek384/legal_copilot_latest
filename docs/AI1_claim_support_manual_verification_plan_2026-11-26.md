# AI-1 Claim Support Manual Verification Plan — 2026-11-26

## Target
`tools/claim_support.py`, its 69 tests in `tests/test_claim_support.py`, and the integration call site in `app.py`.

## Static review findings
- Ordinary broad lexical support screen is opt-in via `LEGAL_CLAIM_SUPPORT_CHECK=1`; absent that explicit flag, the broad screen is disabled.
- The answer path still has separate mandatory guards for citation anchoring, number/period mismatches, source polarity, negated-obligation conflicts, pinpoint citations, actor/role mismatch and conditional-source overstatement.
- Source-matched experimental answers call the broad lexical screen even if the ordinary opt-in flag is not set.
- The broad support screen is a conservative lexical heuristic; its docstring expressly does not claim semantic entailment or lawyer review.
- The fetched test module contains 69 test methods. This count is source-inspection only; no tests were executed.

## Manual test protocol (owner-run)
1. Confirm environment profile and test DB separation before invoking application tests.
2. Run the claim-support test module locally, capturing exit code and full output.
3. Run the existing citation/source-polarity/negated-obligation tests and any related app-level test modules.
4. Test both default configuration (flag absent) and opt-in configuration (`LEGAL_CLAIM_SUPPORT_CHECK=1`) in isolated local test processes.
5. Test source-matched feature gating using existing fixtures, not live legal content.
6. Confirm fail-closed behavior does not expose an unsupported answer when guards reject it.
7. Report failures; do not convert lexical coverage into an accuracy claim.

## No runtime verification
No GitHub Actions, remote execution, application runtime, test command, database mutation, or live legal source retrieval was performed during this review.
