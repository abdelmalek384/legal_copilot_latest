# Human Review Rubric for Egyptian Legal Answers

**Status:** Proposed evaluation protocol; not a legal standard, legal opinion, or evidence that the product is accurate.

## Purpose

Use this rubric when a qualified Egyptian-law reviewer evaluates an actual Legal Copilot answer against the exact source versions available for the question's relevant date. It complements the metrics in [Arabic Retrieval & Citation Evaluation](arabic_retrieval_evaluation.md). It does not replace source authentication, legal-status review, or professional judgment.

Do not use model-to-model agreement, a plausible-sounding answer, or a high automated retrieval score as a substitute for lawyer review.

## Required case record

Record these fields for every reviewed answer:

- Stable question ID and practice area.
- Stable `answer_id` for the exact generated answer/version being reviewed; copy it unchanged from the model-output evaluation record. Do not reuse a question ID as an answer ID or derive an identifier from personal/client information.
- Exact question and relevant facts, using synthetic or anonymized facts only.
- Relevant as_of_date (or explicitly record why the date is not applicable/known).
- Exact answer text shown to the user.
- Run/model identifier and configuration sufficient to reproduce the run, without recording secrets.
- Retrieved source IDs and versions, cited source IDs, article/paragraph/page pin-cites, and source hashes or stable evidence references where available.
- Stable reviewer ID matched to a separately maintained approved qualification registry, reviewer name/role, and review date.
- Per-dimension score, concise evidence-based rationale, and any critical defect.
- Final disposition: pass_for_this_case, needs_revision, unsafe, or not_scored_insufficient_evidence.

Do not place confidential client facts, secrets, API keys, or privileged material in a public benchmark or public repository. Prefer synthetic scenarios; anonymization must be reviewed for re-identification risk.

## Scoring scale

Score each applicable dimension from 0 to 2. Add a short explanation tied to the answer and the source. A score is not meaningful if the reviewer has not verified the relevant source text and version.

| Score | Meaning |
|---|---|
| 0 | Materially wrong, unsupported, misleading, or absent |
| 1 | Partially correct, incomplete, imprecise, or requires a material qualification |
| 2 | Adequate for this test case and supported by the reviewed evidence |

### Dimensions

1. **Legal correctness:** Does the answer accurately state the rule and avoid unsupported legal conclusions?
2. **Source support:** Does the cited source actually support each material legal proposition, rather than merely mention the topic?
3. **Citation precision:** Are the instrument, version, article/paragraph/page, and source locator correct?
4. **Temporal correctness:** Does the answer use the version applicable on the requested date and handle commencement, amendment, repeal, and transitional rules where relevant?
5. **Completeness and issue spotting:** Does it identify material conditions, exceptions, missing facts, and related instruments needed for this question without pretending to be exhaustive?
6. **Arabic clarity:** Is the Arabic understandable and faithful to the legal meaning, with no translation or terminology error that changes the result?
7. **Uncertainty and abstention:** Does it state limits and abstain or return sources-only when the available verified evidence cannot support a reliable answer?

If a dimension genuinely does not apply, mark it not_applicable and explain why; do not silently count it as zero or remove it to improve an aggregate score.

## Critical defects and case disposition

Regardless of any average score, mark the case unsafe and record a critical defect if the answer, for example:

- Invents a statute, article, judgment, quotation, or citation.
- Attributes a proposition to a source that does not support it in a material way.
- Presents a repealed, future, or unverified version as definitely operative for the relevant date.
- Gives a definite substantive conclusion where the reviewed evidence is insufficient and the product should abstain.
- Omits a condition or exception that materially reverses or changes the answer.
- Exposes confidential data in a way that breaches the evaluation's approved data-handling rules.

These examples guide review; the reviewer must explain the actual defect and its legal significance. Do not infer that an unlisted defect is harmless.

Use needs_revision when there is no critical defect but one or more dimensions need material correction. Use pass_for_this_case only when the reviewer considers the answer acceptable for this particular test case and records the evidence. Use not_scored_insufficient_evidence when the reviewer cannot obtain or authenticate the source/version needed to judge the answer; this is not a pass.

## Aggregation and release decisions

- Report counts by practice area, answerability, temporal scenario, source type, and disposition alongside any dimension scores.
- Report critical defects separately; never hide them inside a mean score.
- Do not set a release threshold from a small or unbalanced seed set. Define thresholds only after the product owner and qualified Egyptian-law reviewers approve the benchmark scope, sample size, severity policy, and acceptable risk.
- Keep retrieval recall/MRR, citation source-match metrics, and human legal-answer scores separate. They measure different things.
- Re-review cases when source versions, prompts, retrieval logic, models, or answer formatting materially change.
- Preserve failed cases and regression tests; do not delete a failure merely because a later run passes.
- A benchmark pass is bounded to the reviewed cases and source versions. It does not establish general legal accuracy, comprehensive Egyptian-law coverage, or production readiness.

## Suggested review sequence

1. Freeze the exact question, as_of_date, retrieved passages, citations, and answer for the run.
2. Obtain the authoritative source/version and verify authenticity, applicable date, and any relevant amendment/repeal evidence.
3. Check each material proposition against the text and pin-cite.
4. Score each applicable dimension and write a short rationale.
5. Mark critical defects before considering an overall disposition.
6. Have a second qualified reviewer adjudicate disputed or high-severity cases; preserve both assessments and the adjudication.
7. Feed the failure into a regression case without publishing confidential matter facts.
