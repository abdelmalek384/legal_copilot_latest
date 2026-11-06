# Experimental deadline arithmetic

**Status: integrated experimental preview only; not approved for legal reliance.** The included periods and holiday list are unverified drafts. The case workspace exposes an authenticated, read-only estimate endpoint and a separate manual action to copy the suggested date into the ordinary case-deadline form. The preview itself never creates or changes a deadline row. Saved dates are ordinary user-entered case records, not validated legal deadlines.

## Safety and calculation assumptions

- Draft rules are refused unless a caller explicitly supplies `--allow-unverified`; output still contains an Arabic warning.
- A rule is treated as verified only when `verified=true`, `verified_by` is non-empty, `verified_by_role` is `egyptian_lawyer` or `qualified_egyptian_counsel`, `verified_on` is a valid non-future ISO date, `source_article` is non-empty, and `review_evidence_url` is a valid HTTPS URL without embedded credentials. These fields must only be set after qualified Egyptian-lawyer review against a reliable primary source. This metadata check is not independent proof that the review happened.
- Holiday data is explicitly incomplete. Every result warns when the deadline year is not marked complete.
- Input validation rejects malformed rule and holiday structures, invalid calendar dates, duplicate weekday entries, invalid date ranges, and arithmetic overflow.
- Current arithmetic excludes the trigger date for day-count arithmetic, adds calendar days/months/years, clamps month-end dates, then applies manually supplied distance days and extends across configured non-working days. These are prototype conventions, not legal conclusions. The API returns the calculation steps and assumptions for display; the UI shows the missing source-article field, trigger-basis note, warnings, holiday extensions and disclaimer.
- The default weekend is Friday/Saturday. Confirm the relevant court's applicable calendar and any official holiday-transfer decisions before use.
- Judicial recesses, suspension/interruption, service/notification rules, special statutory counting rules, and other exceptions are not modeled.

## Local prototype

```bash
python deadline_calculator.py --rule civil_commercial_appeal_40d --from 2026-10-26
```

The command should refuse the unverified draft rule. For arithmetic testing only, use `--allow-unverified`; never rely on that output as a legal deadline.

## Validation

Run the focused regression suite with:

```bash
PYTHONPATH=. python tests/test_deadline_calculator.py
```

The suite covers date arithmetic, weekend extension, malformed rules/holiday data, date overflow, and refusal to treat unverified draft rules as verified.

## Required before any legal reliance or promotion from experimental preview

1. Obtain qualified Egyptian-lawyer review of each rule, trigger event, counting convention, exceptions, and primary-source citation.
2. Validate the holiday calendar against official notices for each relevant year.
3. Record the rule version, reviewer identity, review date, primary source, scope, and review outcome in a controlled review process.
4. Before relying on a suggested date, require a reviewed rule/version, confirmed trigger event, applicable calendar, exceptions, and auditable reviewer approval. The current preview does not store a legal-rule snapshot or create a deadline automatically.
5. Do not use this prototype to generate or communicate legally relied-upon deadlines until those gates pass.
