# Human Legal-Answer Review Scoring Tool

**Status:** Reporting utility only. This tool does not evaluate legal correctness automatically and does not certify product readiness.

The rubric in [Human Review Rubric for Egyptian Legal Answers](legal_answer_review_rubric.md) defines seven dimensions and the required dispositions. This CLI validates recorded human assessments and summarizes them without generating labels.

## Input

Create a UTF-8 JSONL file with one assessment per line. Use synthetic scenarios or approved anonymized material only; never commit privileged/client facts, secrets, or re-identifiable records.

Each record requires:
- Unique `assessment_id`, `case_id`, `practice_area`, `reviewer_id`, `reviewer_name`, `review_date`, and `disposition`. The reviewer ID and name must match a separate approved reviewer registry. `review_date` must be a real calendar date in `YYYY-MM-DD` format; malformed disposition values are rejected without crashing the validator.
- `scores`: all seven dimensions, each scored `0`, `1`, `2`, or `not_applicable`.
- `rationales`: an evidence-based rationale for every dimension. A not-applicable rationale must explain why the dimension does not apply.
- `critical_defect`: explicit boolean. If true, disposition must be `unsafe`, `critical_defect_description` is required, and `critical_defect_categories` must contain at least one unique category from the taxonomy below. Categories are reviewer-entered labels, never inferred by the evaluator. If false, the category list must be empty or omitted.

Critical-defect categories:
`unsupported_legal_claim`, `contradicted_source_or_polarity`, `wrong_legal_actor_or_role`, `overbroad_conditional_scope`, `incorrect_article_or_page_pin`, `missing_material_issue`, `temporal_or_currentness_error`, `source_authenticity_or_status`, `privacy_or_confidentiality`, `other`.

The report includes a count for each category and preserves category labels on each critical-defect record. One assessment may have multiple categories, so category counts can sum to more than the number of critical defects. These are human-review findings, not automated measurements of model behavior or legal correctness.

Dimensions:
`legal_correctness`, `source_support`, `citation_precision`, `temporal_correctness`, `completeness_issue_spotting`, `arabic_clarity`, `uncertainty_abstention`.

Allowed dispositions:
- `pass_for_this_case`
- `needs_revision`
- `unsafe`
- `not_scored_insufficient_evidence`

The last disposition is not a pass and is excluded from dimension means. Invalid records and duplicate assessment IDs are reported and excluded rather than silently scored. Multiple reviewers may assess the same `case_id`; each assessment must have its own unique `assessment_id` so independent reviews and adjudications remain countable.

## Run

```bash
python tools/evaluate_legal_answer_reviews.py /secure/path/legal-answer-reviews.jsonl --reviewer-registry /secure/private/reviewer-registry.json
python tools/evaluate_legal_answer_reviews.py /secure/path/legal-answer-reviews.jsonl --reviewer-registry /secure/private/reviewer-registry.json --output /secure/path/legal-answer-review-report.json
python -m unittest tests.test_legal_answer_review_evaluation
```

The JSON report includes disposition counts, practice-area counts, per-dimension score counts and means, invalid records, and critical defects. Critical defects remain separately visible and must never be hidden inside an average.

## Reviewer registry

The private registry must contain a `reviewers` list. Each entry records `reviewer_id`, `display_name`, `status` (`approved`, `pending`, `suspended`, or `rejected`), `qualification_basis`, `evidence_reference`, `verified_by`, and `verified_on`. Only unique, valid, approved entries count. Keep real credential evidence and the registry in controlled private storage; never commit licenses, identity documents, or confidential contact details to the public repository. Registry fields are an auditable human assertion, not independent proof of a license; a trusted operator must check the evidence before marking a reviewer approved.

## Limits

A valid schema does not prove that a source was authentic or current, or that the rationale is correct. The report is only as reliable as the source/version verification and human review behind each record. Do not set release thresholds from a small or unbalanced seed set. Have qualified Egyptian-law reviewers and the product owner approve the benchmark and release policy.


Approved reviewer registry entries must identify Egyptian legal counsel, Egypt as jurisdiction, and an explicit non-empty list of approved practice areas. Reviews outside the registered scope are excluded. The registry remains a human-verified administrative assertion, not independent license verification.
