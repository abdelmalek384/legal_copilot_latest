# AI-1 legal research local test handoff — 26 November 2026

**Scope:** Prioritize existing legal-research regressions using synthetic data only. This package is test instructions, not test results, legal accuracy evidence, or lawyer approval. Use the Python 3.12 environment prepared by the main handoff; do not start tests during the owner's current work.

## First legal test slice (fast, highest risk)

From repository root and the locked Python 3.12 environment:

```sh
python -m unittest tests.test_negation_guard_repro -v
python -m unittest tests.test_answer_source_polarity -v
python -m unittest tests.test_answer_citation_coverage -v
python -m unittest tests.test_answer_pincite_binding -v
python -m unittest tests.test_citation_quantity_binding -v
python -m unittest tests.test_claim_support -v
python -m unittest tests.test_arabic_matching -v
python -m unittest tests.test_synthetic_retrieval -v
python -m unittest tests.test_synthetic_retrieval_benchmark -v
```

These modules target explicit reversal of negation/obligation, citation coverage, pinpoint binding, quantities/thresholds, lexical claim-support checks, Arabic normalization/colloquial retrieval hints, and synthetic retrieval boundaries. Stop on first failure in a module; save command and traceback and don't repeat unchanged failures.

## Second slice: legal trust/provenance boundaries

```sh
python -m unittest tests.test_source_match_evidence_storage -v
python -m unittest tests.test_firm_test_source_matched_mode -v
python -m unittest tests.test_answer_actor_role_binding -v
python -m unittest tests.test_legal_versioned_registry -v
python -m unittest tests.test_legal_article_reference -v
python -m unittest tests.test_legal_answer_evaluation -v
python -m unittest tests.test_legal_answer_review_evaluation -v
python -m unittest tests.test_legal_eval_runner -v
python -m unittest tests.test_score_arabic_retrieval -v
```

If any named test module is absent in this exact checkout, record it and skip; don't create test files during the local run. Candidate/unreviewed or unverified sources must not be promoted into verified/legal-authority results. Test mode is expected to abstain if no permission-cleared source-match evidence packet is available.

## Third slice: source-version and data-readiness audits

```sh
python -m unittest tests.test_compare_legal_versions -v
python -m unittest tests.test_amendment_relationship_validator -v
python -m unittest tests.test_legal_corpus_audit -v
python -m unittest tests.test_legal_source_review_queue -v
python -m unittest tests.test_validate_law14_eval_draft -v
python -m unittest tests.test_labour_law_evidence_cards -v
```

## Scored retrieval and generated answers — only with approved labels

Do **not** score unreviewed seed/candidate questions or interpret excluded rows as zero error. The current retrieval measurement is explicitly unmeasured. If a lawyer-approved, provenance-cleared cohort and reviewer registry are available, use the existing runner/scorer only as documented in `docs/arabic_retrieval_evaluation.md`; do not invent ground truth, change the threshold, or collect confidential client questions without approval.

## Release interpretation

Passing unit tests proves only the exercised contracts. No pilot use until lawyer review of actual answer/source/version/pincite, synthetic two-firm security acceptance, application/browser acceptance, and the existing release gates are completed. Keep AI-1's unexecuted status explicit.