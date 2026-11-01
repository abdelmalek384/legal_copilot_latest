# Human Legal-Answer Review Scoring Tool

**Status:** Reporting utility only. This tool does not evaluate legal correctness automatically and does not certify product readiness.

The rubric in [Human Review Rubric for Egyptian Legal Answers](legal_answer_review_rubric.md) defines seven dimensions and the required dispositions. This CLI validates recorded human assessments and summarizes them without generating labels.

## Input

Create a UTF-8 JSONL file with one assessment per line. Use synthetic scenarios or approved anonymized material only; never commit privileged/client facts, secrets, or re-identifiable records.

Each record requires:
- Unique `assessment_id`, `case_id`, `practice_area`, `reviewer_id`, `reviewer_name`, `review_date`, and `disposition`. The reviewer ID and name must match a separate approved reviewer registry. `review_date` must be a real calendar date in `YYYY-MM-DD` format; malformed disposition values are rejected without crashing the validator. For independent comparison, include `answer_id`, a stable non-empty identifier for the exact generated answer/version shown to reviewers. It is optional for legacy/single-review records.
- `scores`: all seven dimensions, each scored `0`, `1`, `2`, or `not_applicable`.
- `rationales`: an evidence-based rationale for every dimension. A not-applicable rationale must explain why the dimension does not apply.
- `critical_defect`: explicit boolean. If true, disposition must be `unsafe` and `critical_defect_description` is required.

Dimensions:
`legal_correctness`, `source_support`, `citation_precision`, `temporal_correctness`, `completeness_issue_spotting`, `arabic_clarity`, `uncertainty_abstention`.

Allowed dispositions:
- `pass_for_this_case`
- `needs_revision`
- `unsafe`
- `not_scored_insufficient_evidence`

The last disposition is not a pass and is excluded from dimension means. Invalid records and duplicate assessment IDs are reported and excluded rather than silently scored. Multiple reviewers may assess the same `case_id`; each assessment must have its own unique `assessment_id`. Reviewer agreement is calculated only for records sharing both `case_id` and `answer_id`, and requires distinct approved reviewers. Repeated assessments by the same reviewer for the same answer are excluded as duplicates. Different answer IDs in one case are never compared.

## Run

```bash
python tools/evaluate_legal_answer_reviews.py /secure/path/legal-answer-reviews.jsonl --reviewer-registry /secure/private/reviewer-registry.json
python tools/evaluate_legal_answer_reviews.py /secure/path/legal-answer-reviews.jsonl --reviewer-registry /secure/private/reviewer-registry.json --output /secure/path/legal-answer-review-report.json
python -m unittest tests.test_legal_answer_review_evaluation
```

The JSON report includes disposition counts, practice-area counts, per-dimension score counts and means, invalid records, critical defects, and reviewer-agreement results. For each exact answer reviewed by at least two independent reviewers, it reports disposition agreement, dimension-level exact agreement, conflicts involving insufficient evidence, and whether adjudication is needed. Agreement is descriptive only: it does not prove legal correctness or identify which reviewer is right. The tool deliberately does not calculate a chance-corrected reliability statistic; that requires a sufficiently large, balanced and methodologically approved sample. Records without `answer_id` remain in ordinary review summaries but are counted separately and are not used for reviewer-agreement comparisons.

## Reviewer registry

The private registry must contain a `reviewers` list. Each entry records `reviewer_id`, `display_name`, `status` (`approved`, `pending`, `suspended`, or `rejected`), `qualification_basis`, `evidence_reference`, `verified_by`, and `verified_on`. Only unique, valid, approved entries count. Keep real credential evidence and the registry in controlled private storage; never commit licenses, identity documents, or confidential contact details to the public repository. Registry fields are an auditable human assertion, not independent proof of a license; a trusted operator must check the evidence before marking a reviewer approved.

## Limits

A valid schema does not prove that a source was authentic or current, or that the rationale is correct. The report is only as reliable as the source/version verification and human review behind each record. Do not set release thresholds from a small or unbalanced seed set. Have qualified Egyptian-law reviewers and the product owner approve the benchmark and release policy.


Approved reviewer registry entries must identify Egyptian legal counsel, Egypt as jurisdiction, and an explicit non-empty list of approved practice areas. Reviews outside the registered scope are excluded. The registry remains a human-verified administrative assertion, not independent license verification.
