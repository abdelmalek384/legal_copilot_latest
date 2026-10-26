# Experimental deadline arithmetic

**Status: prototype only; not approved for legal reliance.** The included periods and holiday list are unverified drafts. This calculator is not wired into matter deadlines or reminders.

## Safety

- Draft rules are refused unless a caller explicitly supplies \`--allow-unverified\`; output still contains an Arabic warning.
- A rule is considered verified only when \`verified=true\`, \`verified_by\` is non-empty, \`verified_on\` is a valid ISO date, and \`source_article\` is non-empty. These fields must only be set after qualified Egyptian-lawyer review against a reliable primary source.
- Holiday data is explicitly incomplete. Every result warns when the deadline year is not marked complete.
- Counting conventions (event-day exclusion, month-end handling, distance days, weekends and holiday extension) are configurable assumptions that require legal review.
- Judicial recesses, suspension/interruption, special statutory rules, and other exceptions are not modeled.

## Local prototype

\`\`\`bash
python deadline_calculator.py --rule civil_commercial_appeal_40d --from 2026-10-26
\`\`\`

The command should refuse the unverified draft rule. For arithmetic testing only, use \`--allow-unverified\`; never rely on that output as a legal deadline.

## Required before user-facing integration

1. Obtain review of each rule and the counting conventions by a qualified Egyptian lawyer.
2. Validate the holiday calendar against official notices for each relevant year.
3. Add representative edge-case tests and a documented review record.
4. Only then design integration with matter deadlines, preserving the rule/version, trigger, inputs, calculation steps, reviewer and override history.
