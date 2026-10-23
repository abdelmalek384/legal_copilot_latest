# Legal Copilot legal-answer evaluation set

This directory is a scaffold for a lawyer-reviewed benchmark. The seed questions are not legal advice and are not a verified answer key. They intentionally contain no guessed legal conclusions. Do not score model accuracy until a qualified Egyptian lawyer fills in and approves expected answers and authoritative citations.

## Workflow
1. Select questions from practice_questions.seed.jsonl.
2. Retrieve primary legal texts and judgments lawfully; preserve original files and hashes.
3. Have an Egyptian lawyer fill in expected_answer, expected_sources, relevant date, legal-status notes, reviewer and review date.
4. Require primary-source citations for binding-law claims. Add judgments for questions about judicial interpretation.
5. Include amended/repealed provisions, ambiguous facts, plausible but wrong citations, and cases where the correct response is "insufficient verified sources".
6. Score separately: retrieval recall, citation precision, citation support, citation completeness, temporal correctness, issue spotting, Arabic robustness, and abstention when evidence is insufficient.
7. Agreement between AI platforms is not legal verification.
8. Use synthetic or anonymized facts; do not put confidential client facts into public benchmarks.

## JSONL fields
- id, practice_area, question_ar
- as_of_date (nullable)
- expected_answer (null until lawyer-approved)
- expected_sources (empty until verified; then stable source IDs, URLs, article/paragraph, Gazette/case metadata and hashes where available)
- must_abstain_if_unverified (true by default)
- review_status (needs_lawyer_review in seed)
- reviewer_name and review_date (blank until review)

## Initial release gate
Do not describe Legal Copilot as legally accurate or production-ready until an Egyptian lawyer reviews the answer key and results, corpus provenance is audited, and failures are documented.