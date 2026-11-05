# Arabic retrieval measurement — before/after record

**Status:** not yet measurable. Do not tune MIN_SCORE until the same lawyer-approved question set is scored before and after the change.

## Locked measurement contract

- Benchmark: tests/legal_eval/arabic_retrieval_110.template.jsonl.
- All 110 questions are currently unlabeled; expected article, lawyer-approved answer, answerability and pin-cites are blank.
- Existing evaluator tools/evaluate_retrieval_quality.py already measures Recall@3, MRR@3, citation metrics and abstention compliance against lawyer-reviewed labels.
- tools/score_arabic_retrieval.py adds article-specific top-3 hit rate, wrong-article answer rate and abstention rate. It excludes all unlabeled questions.
- Run records must contain ranked retrieved_article_ids, cited_article_ids and abstained for each reviewed question. Wrong-article rate is the share of non-abstained answers with article citations that contain at least one article outside the lawyer-approved expected article; uncited answers are reported separately.
- Target after tuning: top-3 hit rate at least 0.80 on the colloquial-or-synonym slice and wrong-article answer rate 0.00. Report abstention separately; do not improve recall by answering without adequate verified evidence.

## Results

| Metric | Before tuning | After tuning |
|---|---:|---:|
| Lawyer-approved questions scored | Not available | Not run |
| Top-3 hit rate — all reviewed answerable | Not measurable | Not run |
| Top-3 hit rate — colloquial-or-synonym slice | Not measurable | Not run |
| Wrong-article answer rate | Not measurable | Not run |
| Abstention rate | Not measurable | Not run |
| Abstention compliance on unanswerable questions | Not measurable | Not run |
| MIN_SCORE | 0.30 (existing default) | unchanged; tuning blocked |

The machine-readable comparison file is docs/arabic_retrieval_measurement.json. It is initialized with null metrics, not fabricated zeros. The scorer updates one phase at a time while enforcing the same benchmark SHA-256.

## Why there are no numbers yet

A retrieval score without expected article labels would be meaningless. The current 110 questions are realistic prompts, not lawyer-approved ground truth; the 11 added candidates are explicitly not user-observed queries. No baseline run output with ranked article IDs is available in the repository. Therefore neither a before score nor an after score can honestly be reported.

## Run after counsel labels the set

    python tools/score_arabic_retrieval.py --questions tests/legal_eval/arabic_retrieval_110.template.jsonl --runs tests/legal_eval/retrieval_runs.before.jsonl --phase before --min-score 0.30 --output docs/arabic_retrieval_measurement.json

    python tools/score_arabic_retrieval.py --questions tests/legal_eval/arabic_retrieval_110.template.jsonl --runs tests/legal_eval/retrieval_runs.after.jsonl --phase after --min-score VALUE --output docs/arabic_retrieval_measurement.json

Do not change the threshold based on unlabeled prompts, unit-test phrase matches, or a single aggregate score. Investigate wrong-article cases individually and retain zero tolerance for wrong-article answers.
