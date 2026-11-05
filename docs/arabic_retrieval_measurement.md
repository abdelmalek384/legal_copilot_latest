# Arabic retrieval measurement — before/after record

**Status:** not yet measurable. Do not tune MIN_SCORE until the same lawyer-approved question set is scored before and after the change.

## Locked measurement contract

- Benchmark: tests/legal_eval/arabic_retrieval_110.template.jsonl.
- All 110 questions are currently unlabeled; expected article, lawyer-approved answer, answerability and pin-cites are blank.
- Existing evaluator tools/evaluate_retrieval_quality.py already measures Recall@3, MRR@3, citation metrics and abstention compliance against lawyer-reviewed labels.
- tools/score_arabic_retrieval.py adds article-specific top-3 hit rate, wrong-article answer rate and abstention rate. It excludes all unlabeled questions. The scorer also reports target_status as not_evaluable, below_target, or targets_met; targets_met requires at least 80% top-3 hit rate in each separately approved cohort (colloquial and synonym) and a 0.00 wrong-article rate.
- The API runner `tools/run_legal_eval.py` emits ranked `retrieved_article_ids`, answer-cited `cited_article_ids`, and `abstained`. IDs must use `<source_id>::law:<law-label>::article:<article-number>`, so repeated article numbers in promulgation and attached-law blocks do not collide. The runner omits sources without a law label rather than emitting an ambiguous ID; counsel labels the matching value in `expected_article_id`. Runs for known unlabeled questions can be captured now and are excluded from metrics until labels are approved. Wrong-article rate is the share of non-abstained answers with article citations that contain at least one article outside the lawyer-approved expected article; uncited answers are reported separately.
- Target after tuning: top-3 hit rate at least 0.80 on the approved colloquial cohort and at least 0.80 on the approved synonym cohort, measured separately, with wrong-article answer rate 0.00. Report abstention separately; do not improve recall by answering without adequate verified evidence.

## Results

| Metric | Before tuning | After tuning |
|---|---:|---:|
| Lawyer-approved questions scored | Not available | Not run |
| Top-3 hit rate — all reviewed answerable | Not measurable | Not run |
| Top-3 hit rate — colloquial cohort | Not measurable | Not run |
| Top-3 hit rate — synonym cohort | Not measurable | Not run |
| Top-3 hit rate — combined colloquial-or-synonym | Not measurable | Not run |
| Wrong-article answer rate | Not measurable | Not run |
| Abstention rate | Not measurable | Not run |
| Abstention compliance on unanswerable questions | Not measurable | Not run |
| MIN_SCORE | 0.30 (existing default) | unchanged; tuning blocked |

The machine-readable comparison file is docs/arabic_retrieval_measurement.json. It is initialized with null metrics, not fabricated zeros. The scorer updates one phase at a time while enforcing a stable benchmark SHA-256 over sorted question IDs, practice areas, prompt text and origin only. Lawyer-approved answers, expected articles, reviewer fields and style/synonym approval labels may be added later without invalidating the captured baseline; editing a question's text or identity requires a new comparison report.

## Why there are no numbers yet

A retrieval score without expected article labels would be meaningless. All 110 questions are curated prompts, not production user-query logs or lawyer-approved ground truth; the 11 newly added candidates are separately marked as not user-observed. The style/synonym slice is excluded until a lawyer approves the per-row style and retrieval tags. No baseline run output with ranked article IDs is available in the repository. Therefore neither a before score nor an after score can honestly be reported.

## Capture baseline now; score after counsel labels the set

Set the evaluation credentials in the environment (do not put passwords in shell history or commit them), start the app with `MIN_SCORE=0.30`, and capture all 110 candidate runs:

    python tools/run_legal_eval.py --questions tests/legal_eval/arabic_retrieval_110.template.jsonl --out tests/legal_eval/retrieval_runs.before.jsonl

The runner writes ranked source/article IDs and cited article IDs. It does not calculate accuracy. You may run the scorer now; it will record all 110 questions/runs as unlabeled/excluded and keep all rate metrics null. After counsel labels the same questions, rerun the scorer against the same before-run file to obtain the actual baseline.

## Run after counsel labels the set

    python tools/score_arabic_retrieval.py --questions tests/legal_eval/arabic_retrieval_110.template.jsonl --runs tests/legal_eval/retrieval_runs.before.jsonl --phase before --min-score 0.30 --output docs/arabic_retrieval_measurement.json

    python tools/score_arabic_retrieval.py --questions tests/legal_eval/arabic_retrieval_110.template.jsonl --runs tests/legal_eval/retrieval_runs.after.jsonl --phase after --min-score VALUE --output docs/arabic_retrieval_measurement.json

The `--min-score` argument records the threshold used by the running API; it does not change the server configuration. Set the server's `MIN_SCORE` before starting it, and pass the same value to the scorer. Do not change the threshold based on unlabeled prompts, unit-test phrase matches, or a single aggregate score. Investigate wrong-article cases individually and retain zero tolerance for wrong-article answers.
