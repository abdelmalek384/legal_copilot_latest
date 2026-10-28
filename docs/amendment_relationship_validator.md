# Amendment relationship register integrity audit

Use the read-only structural audit before relying on the amendment relationship register for any downstream legal-version workflow.

## Run

```bash
python tools/validate_amendment_relationships.py
```

The report separates structural errors from review warnings. The default command reports findings without failing, because the current register intentionally includes unresolved discovery records.

To make structural errors fail a CI or review gate:

```bash
python tools/validate_amendment_relationships.py --strict
```

An optional JSON report can be written with `--out path/to/report.json`.

## Checks

- Relationship IDs are present and unique.
- Duplicate source/target/type/provision edges are warnings so accidental duplicate records can be reviewed.
- Directed cycles in non-base instrument relationships are warnings for manual review, not automatic proof of legal invalidity; cross-amendment relationships can require contextual legal analysis.
- Inventory entries must be objects with non-empty, unique document IDs; duplicate or missing IDs are errors.
- Every source instrument is present in the document inventory.
- Non-base relationships point to a known target instrument; base-instrument records have a null target.
- Relationship types are from the controlled vocabulary. Malformed non-string type/status values are reported instead of crashing the audit.
- Each record has a direct, syntactically valid HTTPS evidence URL and a non-empty evidence checklist. URL checks reject whitespace, embedded credentials, malformed or out-of-range ports, and malformed URL structures; they do not establish that the evidence is genuine or legally sufficient.
- Effective dates must be real calendar dates in `YYYY-MM-DD` format or an explicit unknown sentinel; impossible dates and malformed strings are errors.
- Unreviewed status, missing provision mapping, and unknown effective dates are reported explicitly.
- A `reviewed_confirmed` relationship is structurally rejected unless it carries a `confirmation_evidence` object with Gazette issue, real publication date, page range, review date, reviewer role, and review basis.
- Confirmed non-base relationships must record affected provisions and a known effective date. Publication date is not treated as an effective date.

## Review and legal-status limits

This is a data-integrity check, not legal verification. It cannot prove that a URL is official, that the document is authentic or complete, or that an amendment has the asserted effect. It does not decide commencement, repeal, transitional provisions, or current status.

Do not mark a relationship `reviewed_confirmed` simply to suppress a warning. The structural gate requires a `confirmation_evidence` object with these fields: `gazette_issue`, `gazette_publication_date` (real `YYYY-MM-DD`), `gazette_page_range`, `reviewed_on` (real `YYYY-MM-DD`), `reviewer_role`, and `review_basis`. A confirmed non-base edge also needs an explicit `affected_provision` or `affected_provisions` value and a known `instrument_effective_date`. These fields are an auditable record of review, not proof that the review was correct. Confirmation still requires the official instrument, exact article or schedule mapping, commencement and transitional analysis, later-amendment search, and qualified Egyptian-lawyer review. Until then, preserve uncertainty and do not use the relationship alone to construct current law.


## Additional evidence gate for `reviewed_confirmed`

A relationship marked `reviewed_confirmed` must now include an inspectable `confirmation_evidence` record with:

- Gazette issue and page range, publication date, and a review date that is not in the future and does not precede publication.
- A stable reviewer ID, the explicit `qualified_egyptian_lawyer` role, and a substantive review basis.
- A valid HTTPS evidence URL without embedded credentials and a 64-character hexadecimal SHA-256 digest for the reviewed evidence artifact.

These are metadata and traceability gates only. The validator does not fetch the evidence, recompute the referenced artifact hash, independently authenticate the source, verify the reviewer’s licence, or determine legal effect. A passing record still requires trusted human verification before it can support a current-law claim.
