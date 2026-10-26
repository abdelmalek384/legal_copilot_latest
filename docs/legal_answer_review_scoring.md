# Human Legal-Answer Review Scoring Tool

**Status:** Reporting utility only. This tool does not evaluate legal correctness automatically and does not certify product readiness.

The rubric in [Human Review Rubric for Egyptian Legal Answers](legal_answer_review_rubric.md) defines seven dimensions and the required dispositions. This CLI validates recorded human assessments and summarizes them without generating labels.

## Input

Create a UTF-8 JSONL file with one assessment per line. Use synthetic scenarios or approved anonymized material only; never commit privileged/client facts, secrets, or re-identifiable records.

Each record requires:
- Unique `assessment_id`, `case_id`, `practice_area`, `reviewer_name`, `review_date`, and `disposition`. `review_date` must be a real calendar date in `YYYY-MM-DD` format; malformed disposition values are rejected without crashing the validator.
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

The last disposition is not a pass and is excluded from dimension means. Invalid records and duplicate assessment IDs are reported and excluded rather than silently scored. Multiple reviewers may assess the same `case_id`; each assessment must have its own unique `assessment_id` so independent reviews and adjudications remain countable.

## Run

```bash
python tools/evaluate_legal_answer_reviews.py /secure/path/legal-answer-reviews.jsonl
python tools/evaluate_legal_answer_reviews.py /secure/path/legal-answer-reviews.jsonl --output /secure/path/legal-answer-review-report.json
python -m unittest tests.test_legal_answer_review_evaluation
```

The JSON report includes disposition counts, practice-area counts, per-dimension score counts and means, invalid records, and critical defects. Critical defects remain separately visible and must never be hidden inside an average.

## Technical release gate sample size

When using any numeric quality threshold, the CLI also requires an explicit `--min-questions` value. This prevents a release gate from reporting a pass based on a tiny reviewed sample. The gate fails when fewer lawyer-approved questions were scored than the requested minimum.

Example (the numbers below are illustrative, not approved release thresholds):

```bash
python tools/evaluate_legal_answers.py \
  --questions /secure/path/reviewed-questions.jsonl \
  --results /secure/path/model-results.jsonl \
  --min-questions 100 \
  --min-source-precision 0.98 \
  --min-pin-cite-precision 0.98 \
  --min-abstention-accuracy 0.99 \
  --max-invalid-citation-question-rate 0
```

Choose the minimum sample size and all metric thresholds only after qualified Egyptian-law reviewers and the product owner approve a sufficiently representative benchmark. A total sample-size gate does not guarantee coverage of every practice area or scenario; report and review those distributions separately. The gate measures technical citation/abstention behavior only and cannot certify legal correctness or product readiness.

## Limits

A valid schema does not prove that a reviewer is qualified, that the source was authentic or current, or that the rationale is correct. The report is only as reliable as the source/version verification and human review behind each record. Do not set release thresholds from a small or unbalanced seed set. Have qualified Egyptian-law reviewers and the product owner approve the benchmark and release policy.
