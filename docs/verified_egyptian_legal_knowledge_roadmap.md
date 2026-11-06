# Verified Egyptian Legal Knowledge — Delivery Roadmap

**Status:** planning and evidence-gate specification; not evidence that any law is verified.  
**Owner:** project maintainer, with qualified Egyptian-lawyer review required for legal conclusions.  
**Scope:** non-database work only. This document does not authorize schema, migration, tenant-storage, or production-data changes.

## Purpose and release rule

Build an Arabic-first Egyptian legal research corpus that can explain where each legal proposition came from, which version/date it applies to, whether reuse is permitted, and who reviewed it. Do not describe the whole corpus—or a particular instrument—as verified unless every required gate below is evidenced.

Publicly reachable does not mean licensed for commercial republication, extraction, indexing, or display. If rights or terms are unclear, keep the content quarantined from production retrieval. A missing reply to a permission request is not permission.

## Current baseline and blockers

- The repository's source registry and authorized-acquisition workflow are discovery/planning artifacts, not a verified corpus.
- Existing source-to-release checks require rights scope, original-file hash integrity, legal status, and passed source/extraction/amendment/licensing/lawyer-review evidence. Keep those checks as hard release gates.
- A passing candidate `lawyer_approval` record must also carry the runtime marker `[qualified_egyptian_counsel_attested:user_id=N]`, with the positive platform account ID matching `reviewer_id`. This proves only that the configured counsel-allowlist gate was satisfied when the review was recorded; operators must independently verify qualifications and protect the allowlist.
- The repository now has a local-only `tools/validate_manual_capture_record.py` sidecar validator (merged in PR #688), not a `record_manual_capture` acquisition command. Its supported invocation is `python tools/validate_manual_capture_record.py --record path/to/capture.json`. It validates metadata and original-file hash/path integrity only; it does not capture/download a source, establish legal authenticity, grant reuse rights, or make content retrieval-eligible. Confirm the validator is merged into the target branch before relying on it.
- The proposed comparison file `law_rows_ar.jsonl` (reported elsewhere as 311 rows) and an independently captured, permission-cleared Gazette text have not been verified as present in the repository in this task. Labour Law 14/2025 reconciliation is therefore **blocked pending artifacts**, not completed.
- No source is labelled lawyer-approved merely because two web copies agree or an extraction test passes.

## Instrument state model

Track each dimension independently; never infer one state from another:

- Source discovery: `not_started` / `discovered`
- Terms review: `not_reviewed` / `reviewed`
- Collection permission: `unknown` / `permission_pending` / `allowed` / `not_allowed`
- Commercial use: `unknown` / `allowed` / `restricted` / `prohibited`
- Acquisition: `not_acquired` / `acquired`
- Extraction: `not_started` / `extracted` / `OCR_required` / `extraction_reviewed`
- Authenticity: `unknown` / `source_checked` / `verified` / `rejected`
- Amendment history: `unknown` / `partial` / `reviewed`
- Legal status: `unknown` / `under_review` / `not_yet_in_force` / `in_force` / `partially_repealed` / `repealed` / `historical`
- Lawyer review: `not_started` / `pending` / `approved` / `rejected`

Keep original-source facts, extracted/transcribed text, reviewer findings, and model-generated interpretations distinguishable.

## Workstream checklist

### Phase 0 — establish a defensible review and rights process

- [ ] Keep the existing lawyer source/data-rights opinion checklist; record outreach attempts and unanswered questions without treating silence as approval.
- [ ] For every candidate source, record exact source URL, access/terms URL, terms-check date, intended uses (download, storage, extraction, indexing, retrieval, display, commercial use), permission evidence, and unresolved restrictions.
- [ ] Quarantine candidates whose permitted use is unknown or too narrow for the planned use.
- [ ] Confirm the actual CLI and manifest schema for source records, review events, and release checks before writing operator instructions; distinguish the manual-capture sidecar validator from any acquisition command.
- [ ] Name the qualified reviewer role and preserve an append-only record of review outcome, date, scope, and evidence.
- **Exit criteria:** a reviewer can trace a proposed item from discovery to rights decision and explain why it is allowed, blocked, or awaiting evidence.

### Phase 1 — Labour Law No. 14 of 2025, end to end

- [ ] Obtain a primary-source Gazette text through a documented, permitted route. Save the original bytes unchanged; record SHA-256, exact source and final URLs, retrieval timestamp, Gazette issue/date/page range, publication date, and any known commencement provision.
- [ ] Obtain the reported 311-row comparison file and verify its origin, completeness, encoding, and rights before using it. Record the file hash; do not assume row count proves completeness.
- [ ] Compare every article and issuance provision against the primary text. Produce a machine-readable difference report for missing/duplicate article numbers, changed wording, punctuation that may change meaning, dates, amounts, exceptions, negations, cross-references, schedules, and commencement/transitional clauses.
- [ ] Resolve **every legal-critical/numeric difference** against the primary source; preserve each resolution and its evidence. A mismatch must never be silently normalized away.
- [ ] Have qualified Egyptian counsel review every legal-critical/numeric difference and a documented 10–20% sample of otherwise matching provisions. Counsel may expand the sample or reject the source if risk warrants.
- [ ] Independently confirm the amendment, commencement, transitional, and current-status chain. Add Labour Law No. 12 of 2003 only as a separately versioned historical instrument after its status and relationships are evidenced.
- [ ] Run the source-to-release gate and a lawyer-approved Arabic question set. Target at least 90% on the pre-agreed evaluation metrics, with citation correctness, date correctness, and unsafe-answer rate reported separately. A single aggregate score must not conceal a critical error.
- **Exit criteria:** rights scope allows the actual use; original hash and provenance are intact; article-level comparison has no unresolved critical differences; legal status is reviewed; counsel's approval event is recorded; all release checks pass; evaluation meets the agreed threshold.
- **Current status:** blocked on confirmed source artifacts, comparison-file provenance/availability, permitted reuse, and counsel review. No verification claim is authorized.

### Phase 2 — expand by priority, one instrument at a time

After Phase 1 passes, repeat the same gates for:
1. Civil Code.
2. Civil and Commercial Procedure and Evidence.
3. Criminal Procedure and Penal Code.
4. Commercial Law and cheque-related instruments.
5. Personal-status instruments.
6. Rent instruments, including Law No. 164 of 2025 and relevant legacy versions.
7. Social insurance.
8. Companies and core tax statutes.

For each instrument, keep a separate checklist and release decision. Do not batch-mark an entire topic as verified. For amendments, capture each amending instrument as its own record and map affected provisions explicitly.

### Phase 3 — as-of-date and deadline correctness

- [ ] Build an instrument-by-instrument timeline of publication, commencement, amendments, repeal/partial repeal, transitional provisions, and any judicial decisions affecting status.
- [ ] Prioritize the ten instruments most used by the first supported practice area; the practice area must be explicitly selected rather than assumed.
- [ ] Add test questions on historical dates, future-effective provisions, partial repeal, conflicting versions, and “law in force today” queries.
- [ ] Validate deadline arithmetic separately from legal deadline rules. Require the legal trigger, applicable rule, holidays/suspension assumptions, and source citations to be reviewed; never describe a generic date calculator as legally verified.
- **Exit criteria:** every current-law answer resolves to the correct instrument version for the requested date or abstains when evidence is insufficient.

### Phase 4 — judgments and secondary materials

- [ ] Begin with metadata-only discovery for judgments unless full-text acquisition and intended reuse are explicitly permitted.
- [ ] Before collecting Supreme Constitutional Court, Court of Cassation, or Council of State text, review the specific portal's terms and restrictions. No scraping or bulk extraction of restricted court portals without documented authorization.
- [ ] Keep firm-uploaded judgments private to the supplying firm and case/matter access rules; do not promote private uploads into the shared corpus.
- [ ] Separate primary legislation, judgments, translations, commentary, practice notes, and model-generated summaries in labels and retrieval policy.
- **Exit criteria:** each collection has its own rights scope, provenance, access boundary, and review standard.

### Phase 5 — ongoing maintenance and regression

- [ ] Maintain a review panel of qualified Egyptian lawyers; record actual participation rather than assuming availability.
- [ ] Build a benchmark of at least 100 lawyer-approved questions before claiming broad answer-quality readiness. Expand the existing seed set only with provenance and reviewer approval.
- [ ] Run regression tests on every corpus or retrieval-policy update: citation correctness, exact article recall, as-of-date correctness, amendment conflicts, false abstentions, unsupported-answer rate, Arabic colloquial/synonym retrieval, and tenant-private document isolation.
- [ ] Check official publication sources on a scheduled cadence and record each check, including checks that found no relevant update.
- [ ] For each update, preserve old versions and review events; do not overwrite history or silently change a previously reviewed legal status.
- **Exit criteria:** each release has a reproducible report, explicit unresolved issues, reviewer sign-off, and rollback path.

## Source handling rules

- Official Gazette / Amiri Press is the preferred primary source for promulgated text, subject to the actual access and reuse terms for the specific item.
- Ministry pages and official portals can be useful leads and cross-checks; verify the Gazette issue and current status before treating a copy as authoritative.
- IDSC repository, Manshurat/AUC, WIPO Lex, ILO NATLEX, Wikisource, and other third-party copies may help locate or compare material. Their presence does not by itself grant commercial reuse rights or establish currentness. Check item-level terms and preserve the distinction between primary and secondary copies.
- Translations are aids; Arabic authoritative text governs unless a specific legal instrument states otherwise.
- Never bypass login/paywall/access controls or turn a discovery queue into a downloader input without a passed permission gate.

## Reporting and percentage rules

Report progress by instrument and gate, not only by number of files or rows. Suggested status:
- **Progressing:** a concrete artifact or test is being produced and no external dependency prevents that step.
- **Lagging:** the work is feasible but has no owner, acceptance criteria, or current evidence.
- **Blocked:** required source, rights evidence, qualified review, or necessary input is unavailable.
- **Complete:** all documented exit criteria pass and the required change/evidence is merged or recorded.

A document being written is not the same as the corpus being verified. The roadmap itself is a planning deliverable only; it does not raise the verified-law coverage percentage.
