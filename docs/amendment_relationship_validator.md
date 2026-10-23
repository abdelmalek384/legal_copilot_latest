# Amendment relationship register integrity audit

Use the read-only structural audit before relying on the amendment relationship register for any downstream legal-version workflow.

## Run

```bash
python tools/validate_amendment_relationships.py
```

The report separates structural errors from review warnings. The default command reports findings without failing, because the current register intentionally includes unresolved discovery records.

The standard GitHub Actions workflow now runs the validator regression tests and emits the read-only audit report on every CI run. CI uses report mode rather than `--strict` so known unresolved discovery records remain visible without being mistaken for structural breakage; structural errors should be reviewed before a relationship register is used downstream.

To make structural errors fail a CI or review gate:

```bash
python tools/validate_amendment_relationships.py --strict
```

An optional JSON report can be written with `--out path/to/report.json`.

## Checks

- Relationship IDs are present and unique.
- Every source instrument is present in the document inventory.
- Non-base relationships point to a known target instrument; base-instrument records have a null target.
- Relationship types are from the controlled vocabulary.
- Each record has a direct HTTPS evidence URL and a non-empty evidence checklist.
- Unreviewed status, missing provision mapping, and unknown effective dates are reported explicitly.

## Review and legal-status limits

This is a data-integrity check, not legal verification. It cannot prove that a URL is official, that the document is authentic or complete, or that an amendment has the asserted effect. It does not decide commencement, repeal, transitional provisions, or current status.

Do not mark a relationship `reviewed_confirmed` simply to suppress a warning. That status requires the official instrument, Gazette issue/date/page range, exact article or schedule mapping, effective-date analysis, later-amendment search, and qualified Egyptian-lawyer review. Until then, preserve uncertainty and do not use the relationship alone to construct current law.
