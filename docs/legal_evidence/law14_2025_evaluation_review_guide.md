# Law 14/2025 evaluation-question review guide

**Status:** preparation aid only. The current question inventory is machine-proposed and unapproved. This guide does not approve any question, article pin, legal answer, source, or Law 14/2025 text.

## Files and commands

- Draft inventory: `tests/legal_eval/law_14_2025_machine_proposed_questions.draft.jsonl`
- Structural safety check: `python tools/validate_law14_eval_draft.py`
- Reviewed-label scorer: `python tools/score_arabic_retrieval.py`
- Baseline inventory: `docs/legal_evidence/law14_2025_retrieval_baseline_unreviewed.json`

Run the structural validator before and after editing the draft. It must remain clearly unapproved until the lawyer's review is complete. The validator is a safety check, not a legal assessment.

## What is in the draft

The current draft has 116 unique question records: 58 formal Arabic and 58 Egyptian-colloquial versions. They cover 58 proposed article pins, with a formal/colloquial pair per pin. These are not 116 independent legal provisions, and a matching article number does not establish that either question is legally answerable or correctly pinned.

All records currently have:
- `expected_article_status = "machine-proposed, unapproved"`
- `label_status = "machine_proposed_unapproved"`
- `review_status = "needs_lawyer_review"`
- no approved answer, reviewer identity, source key, pin-cite key, or answerability decision
- `release_eligible = false` and `must_abstain_if_unverified = true`

## Review each record

1. **Question meaning:** confirm that the question is understandable, legally coherent, and asks one identifiable issue. For each pair, confirm that the colloquial version preserves the formal version's legal meaning; rewrite or reject it if it changes scope or adds an assumption.
2. **Article pin:** inspect the complete applicable primary text and independently confirm the expected article. Check promulgation provisions separately from Labour Law articles. Record the exact source ID and pin cite; do not approve based on the machine-proposed ID alone.
3. **Answerability:** decide whether the question can be answered from the permitted, current corpus. If not, mark it unanswerable and require abstention. Do not invent a fallback answer.
4. **Approved answer:** where answerable, write a concise Arabic answer grounded in the reviewed source, including material conditions, exceptions, dates, and cross-references. Add the supporting source IDs and exact pin cites.
5. **Currentness and source eligibility:** check commencement, amendments, repeal/supersession, and source collection/reuse eligibility. A readable copy or text-extraction spot-check is not proof of Gazette equivalence or permission.
6. **Review record:** enter the approved reviewer ID, name, role, review date, and evidence reference required by the project's reviewer registry and scoring schema. Keep review provenance traceable.

## Promotion rules

Do not set `review_status` to `lawyer_reviewed` or `approved_for_evaluation` until the qualified Egyptian lawyer has completed all applicable checks and the required reviewer evidence is recorded. Do not change `expected_article_status` to `verified` merely because a question is approved for a benchmark. Benchmark approval and legal-source verification are separate decisions.

Keep rejected, ambiguous, unanswerable, and pending records explicit. Never delete them just to improve the score. Do not combine formal and colloquial pair results without reporting the two cohorts separately.

## Scoring and baseline

The scorer accepts reviewed labels only. It requires a valid approved reviewer registry and run records from the authenticated retrieval API. Capture the same benchmark fingerprint and corpus/version metadata for before/after runs. Report at least:
- top-3 article hit rate
- wrong-article rate
- abstention rate and answerability cohort
- formal vs colloquial results separately
- excluded, malformed, and unreviewed records

The current unreviewed inventory has no approved answer keys or retrieval run records. Its metrics are null, not zero. Do not tune retrieval thresholds against this draft or claim an evaluation baseline until the reviewed dataset and actual run exports exist.
