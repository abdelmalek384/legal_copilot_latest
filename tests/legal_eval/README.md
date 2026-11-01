# Legal Copilot legal-answer evaluation set

This directory is a scaffold for a lawyer-reviewed benchmark. The seed questions are not legal advice and are not a verified answer key. They intentionally contain no guessed legal conclusions. Do not score model accuracy until a qualified Egyptian lawyer fills in and approves expected answers and authoritative citations.

## Workflow
1. Select questions from practice_questions.seed.jsonl.
2. Retrieve primary legal texts and judgments lawfully; preserve original files and hashes.
3. Have an Egyptian lawyer fill in expected_answer, expected_sources, relevant date, legal-status notes, reviewer and review date. For scoring, expected_sources must be a non-empty list of stable source-ID strings; also set expected_pin_cites, an explicit answerable boolean, and review_status, reviewer_id, reviewer_name, and review_date. The reviewer ID/name must match the private approved reviewer registry used by the evaluator.
4. Require primary-source citations for binding-law claims. Add judgments for questions about judicial interpretation.
5. Include amended/repealed provisions, ambiguous facts, plausible but wrong citations, and cases where the correct response is "insufficient verified sources".
6. Score separately: retrieval recall, citation precision, citation support, citation completeness, temporal correctness, issue spotting, Arabic robustness, and abstention when evidence is insufficient.
7. Agreement between AI platforms is not legal verification.
8. Use synthetic or anonymized facts; do not put confidential client facts into public benchmarks.

## JSONL fields
- id, practice_area, question_ar
- as_of_date (nullable)
- expected_answer (null until lawyer-approved)
- expected_sources (empty until verified; for evaluator compatibility, use a non-empty list of stable source-ID strings; keep URLs, article/paragraph, Gazette/case metadata and hashes in the source register or review notes)
- must_abstain_if_unverified (true by default)
- review_status (needs_lawyer_review in seed)
- expected_pin_cites (empty until reviewed; each entry has source_id and pin_cite)\n- answerable (explicit true/false after legal review)\n- reviewer_name and review_date (blank until review)


## Stable application answer IDs

Each newly generated assistant answer in the research conversation API receives a random opaque `answer_id`. The value is returned by `POST /research/conversations/{conversation_id}/messages` and appears on assistant message records returned by `GET /research/conversations/{conversation_id}`. It is persisted with that exact assistant message; a later answer to the same question receives a different ID. Historical assistant messages created before this feature may not have an ID.

Copy the returned value unchanged when preparing the model-output evaluation row and the corresponding human-review record. Never derive it from a question ID, case number, client name, or other personal data. The evaluator's stable-ID propagation is tracked separately in PR #1127; until that change is merged, the current main-branch evaluator does not include this ID in its report.

## Initial release gate
Do not describe Legal Copilot as legally accurate or production-ready until an Egyptian lawyer reviews the answer key and results, corpus provenance is audited, and failures are documented.

## Labour-law draft question set (awaiting lawyer review)
- `labour_law_questions.draft.jsonl`: 61 draft questions in the same format as the seed file (20 direct, 10 paraphrased, 10 colloquial Egyptian, 10 plain-terms, 6 date-sensitive, 5 that must be refused). Every `expected_answer` and `expected_sources` field is intentionally empty.
- `labour_law_questions_for_lawyer.csv`: the same questions as an Excel-friendly sheet with Arabic headers and blank answer columns for the reviewing lawyer.
- Do not score model accuracy on these until an Egyptian lawyer has filled in the answers, cited primary sources, and recorded `reviewer_name` and `review_date`. After review, copy approved rows back into the JSONL and set `review_status` accordingly.
- The date-sensitive questions test whether the system applies the correct law for events before and after the new labour law took effect; the lawyer must confirm the applicable dates from the Official Gazette.


## Automated evidence-behavior evaluator

The tool `tools/evaluate_legal_answers.py` computes source-ID recall, exact reviewed pin-citation recall, citation presence for answerable questions, and agreement with a lawyer-reviewed answerability/abstention label. It does **not** score whether the generated legal explanation is semantically correct.

Only rows with `review_status: "lawyer_approved"` are scored. Each scored row must include a non-empty expected answer, named reviewer, ISO review date, explicit boolean `answerable`, and reviewed citations for answerable questions. Unreviewed drafts are reported as excluded. The evaluator refuses to run if no reviewed questions exist, if results are missing for reviewed IDs, or if result IDs are unknown.

Model-output JSONL format (one record per question ID):

```json
{"id":"Q-CIVIL-001","answer":"...","abstained":false,"cited_sources":["LAW-123"],"cited_pin_cites":[{"source_id":"LAW-123","pin_cite":"المادة 163"}]}
```

Run it after a lawyer has approved the benchmark and a model-output JSONL has been collected:

```bash
python tools/evaluate_legal_answers.py --questions tests/legal_eval/reviewed_questions.jsonl --results model_outputs.jsonl --reviewer-registry /secure/private/reviewer-registry.json --out evaluation-report.json
```

Do not turn this report into a claim of legal accuracy. A lawyer must separately review substantive correctness, source authenticity/currentness, and whether citations actually support each legal proposition. Keep the real reviewer registry and credential evidence in private controlled storage; the registry is an accountable human assertion, not independent proof of a license.


The evaluation runner validates the API base URL before sending requests. It rejects whitespace, embedded credentials (including empty userinfo), malformed URL structures, and invalid ports. Remote targets still require explicit `--allow-remote` opt-in and HTTPS. These checks validate URL syntax and target policy; they do not establish that a remote service is trusted.
