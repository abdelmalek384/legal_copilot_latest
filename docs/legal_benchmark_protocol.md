# Egyptian legal-answer benchmark: Constitution v1

This is a small seed benchmark for retrieval/citation testing, not a legal opinion or a lawyer-approved gold set.

## Source
- Official Presidency Constitution page: https://www.presidency.eg/ar/مصر/الدستور/
- Officially hosted 2019 PDF: https://www.presidency.eg/media/46122/دستور-جمهورية-مصر-العربية-2019.pdf
- WIPO Lex catalog identifies its Constitution text as the 2019 version incorporating amendments adopted on 23 April 2019: https://www.wipo.int/wipolex/en/legislation/details/19863

## Important limitations
- Every record has `status: pending_lawyer_review`. The question/article mappings and expected answer facts are test hypotheses to be compared with the official PDF.
- Do not use this benchmark to certify legal correctness until an Egyptian lawyer checks exact text, version, article numbers, expected facts and any caveats.
- A passing keyword check is not proof of a legally correct answer. The intended evaluator must check citation precision, answer completeness, misleading omissions and unsupported assertions.
- The seed set currently focuses on constitutional questions. Practice-area coverage should be expanded only after source documents are collected and versioned for the Civil Code, Penal Code, procedural codes, labour, commercial, tax, personal status, administrative, consumer protection, data protection, social insurance and other fields.

## Release-gate sample size

When configuring any quality threshold in `tools/evaluate_legal_answers.py`, pass an explicit `--min-questions N`. The release gate fails if fewer lawyer-approved questions are scored than this minimum, and refuses to run quality thresholds without the minimum. For example:

```sh
python tools/evaluate_legal_answers.py --questions reviewed.jsonl --results model-results.jsonl \
  --min-questions 100 --min-source-precision 0.98 --min-pin-cite-precision 0.98
```

The value `100` and metric thresholds above are illustrative, not approved acceptance criteria. The product owner and qualified Egyptian-law reviewers must set an appropriate sample size and thresholds for a representative benchmark, including practice-area and answerability coverage. Sample size and citation/abstention metrics do not establish legal correctness.

## Evaluation contract
For each query, the product should:
1. Answer in Arabic when asked in Arabic.
2. Cite the exact article and source/version.
3. Avoid adding details not supported by retrieved text.
4. Say it cannot establish the answer, or return sources only according to the app's existing policy, when no reliable supporting source is retrieved.
5. Distinguish constitutional text from implementing statutes, regulations, judgments and legal interpretation.

## Human answer review

Use [the proposed human legal-answer review rubric](legal_answer_review_rubric.md) to record evidence-based scores, critical defects, and case dispositions after an actual run. The rubric is a proposed workflow, not an approved legal standard. Do not claim answer accuracy until qualified Egyptian-law reviewers validate the source versions and review the outputs.
