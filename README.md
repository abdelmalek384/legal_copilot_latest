# Legal Copilot MVP (Egyptian law, Arabic-first)
Case folders with Egyptian case metadata, internal notes, legal deadlines separate from court sessions, fee tracking, team management, session tracking, hybrid law search (SQLite FTS5 + Arabic-normalized trigram similarity + exact article lookup),
and answers that must cite numbered sources. If nothing relevant is found, or the model's citations fail the check, it shows sources only.

Mac quick start: double-click `start_mac.command`; it creates a virtual environment, installs dependencies, initializes separate control-plane, firm, and shared-corpus databases under `./data`, prompts to create the first firm administrator if needed, and starts the app locally. Manual run: set `COPILOT_CONTROL_DB`, `COPILOT_TENANT_DB_ROOT`, and `COPILOT_CORPUS_DB` to three distinct paths, then run `uvicorn app:app --host 127.0.0.1 --port 8000` and open http://127.0.0.1:8000. The app fails closed if neither the separate paths nor an explicit legacy `COPILOT_DB` path is configured.
Load law: POST a JSON list of {law, article, text, as_of, in_force, source} to /law/import (see sample_law.jsonl: FICTIONAL test text only).
Model: set LLM_URL (OpenAI-compatible /chat/completions, e.g. vLLM, Ollama, or a hosted provider), LLM_MODEL, and LLM_KEY. The app does not choose or bundle a model. LLM_URL alone is not enough to send prompts: explicitly set LLM_DATA_PROCESSING_APPROVED=1 only after reviewing the endpoint, data-processing terms, retention, and whether matter data may be sent. Matter-file passages additionally require `LLM_FIRM_DATA_PROCESSING_APPROVED=1`; otherwise those requests return sources only. These are deployment attestations, not consent or privacy guarantees. See [LLM data-processing policy](docs/llm_data_processing_policy.md).

Not included yet: a complete verified official law/ruling corpus, production-ready reminder operations (a tenant-scoped durable outbox and dry-run-by-default operator scheduler now exist, but SMTP provider staging, external scheduling/monitoring, and operator reconciliation remain release gates; see docs/reminder_scheduler_contract.md), WhatsApp/SMS delivery, embedding-model semantic search, and a complete end-to-end amendment/consolidation workflow.

## Egyptian legal corpus bootstrap

The repository currently contains source registers and candidate metadata, not a complete verified Egyptian legal corpus. `sample_law.jsonl` contains fictional test material and must not be used as real law.

Validate the initial candidate catalogue (dry run):

```bash
python tools/seed_legal_candidates.py
```

To seed source and document-candidate metadata into the local SQLite registry (no legal text is downloaded and no law is marked verified):

```bash
python tools/seed_legal_candidates.py --apply
```

Before any authorized acquisition, review [the acquisition-readiness audit](docs/acquisition_readiness_audit.md) and run its read-only preflight against the candidate manifest and source permission register. For the narrow distinction between copyright in official legal documents and rights in a portal/database/collection, also read [the legal-text reuse framework](docs/legal_text_reuse_framework.md); it does not itself grant permission or override the acquisition gate. A manifest entry marked pending is not permission to download, and collection readiness is not commercial reuse permission. Any permission marked allowed must link to inspectable HTTPS rights evidence; commercial reuse needs separate evidence and a separate review date.

For a read-only snapshot of the source registers, acquisition queue, candidate counts, and cross-register inconsistencies, run `python tools/report_legal_corpus_inventory.py` (see [inventory report guide](docs/legal_corpus_artifact_inventory.md)). This counts planning metadata only; it does not count candidate entries as collected or verified legal documents.

See [the bootstrap guide](docs/legal_corpus_bootstrap.md), [candidate instrument catalogue](docs/legal_document_candidates.json), and [source permission register](docs/source_permission_register.json). Do not collect or commercially reuse a source unless the applicable permission has been established and documented.

## Arabic handling
Normalizes diacritics, tatweel, alef/hamza forms, ya/alef maqsura, ta marbuta, and Arabic-Indic digits (so "المادة ٥" finds article 5);
light prefix/suffix stemming and stopword removal at both index and query time; exact article-number lookup; RTL UI with Arabic fonts.
Known limits: no broken-plural or Egyptian-dialect handling, no semantic embeddings yet (next step: an Arabic-capable multilingual
embedding model such as bge-m3 or multilingual-e5, stored in pgvector), and MIN_SCORE (default 0.3) must be tuned on a real evaluation set.

## Setup and security

Before deploying for real client matters, use the [production deployment checklist](docs/production_deployment_checklist.md). It is a release gate, not a substitute for an independent security review or legal validation.

Run the read-only deployment configuration preflight as the application OS account before release:
```bash
python tools/deployment_preflight.py --strict
```
It checks basic secret configuration, `MIN_SCORE`, and SQLite path/access settings. It does not test TLS, proxy configuration, legal corpus validity, or certify deployment security.

Before any production launch, also run the [aggregate production release gate](docs/production_release_gate.md):
```bash
PYTHONPATH=. python tools/production_release_gate.py --out reports/production-release-gate.json
```
The gate combines strict deployment configuration, legal-corpus permission/integrity/review evidence, and the lawyer-approved multi-area benchmark. It is expected to block release while the corpus candidates or benchmark remain unreviewed; do not change draft review markers merely to obtain a pass.
1. `pip install -r requirements.txt`, then `python selftest.py && python api_test.py`.
2. Create the first account: `python manage.py adduser "Name" name@firm.eg admin` (roles: admin, lawyer, junior; password min 12 characters). When typing the password in the terminal, characters do not appear on screen; this is normal. Press Enter after typing it. If you need to change a forgotten password later, run `python manage.py resetpw name@firm.eg`.
3. Set `ADMIN_TOKEN` to a randomly generated secret of at least 32 characters in the server environment (never commit it or print it in logs). `/law/import` requires both a valid signed-in admin account and the `X-Admin-Token` header. Rotate the secret immediately if exposed. Optional: `LLM_URL` / `LLM_MODEL` / `LLM_KEY`.
4. Run `uvicorn app:app` only behind an HTTPS reverse proxy (Caddy or nginx).
5. Backups: `python manage.py genkey` once (store the key OFF the server), then daily via cron:
   `BACKUP_KEY=... python manage.py backup /safe/path --keep 14`. Restore: `python manage.py restore FILE OUT.db`. Test a restore.
6. Encrypt the server disk (LUKS or your host's volume encryption). The database itself is not encrypted, so disk encryption is what protects it at rest.

Permissions: admin sees all cases; a lawyer sees only cases they belong to; only a case's lead (or admin) can edit status, manage the team, or delete.
Uploads: PDF/DOCX up to 15 MB. Text-based PDFs and DOCX files are extracted locally; scanned PDFs may use optional local OCR when the OCR dependencies and Arabic/English Tesseract language data are installed. Original uploads are not retained by this workflow; extracted text is stored. OCR output remains unverified until checked against the original.
Not yet done: independent security review, production acceptance of MFA and account recovery (TOTP enrollment and recovery codes are implemented but the last-platform-admin offline recovery drill remains open), email-based password reset, audit export, production reminder operations, embeddings, a formal conflict-check workflow, and production acceptance of the separate-database cutover. Fresh-install mode routes firm data to per-firm databases and legal-registry data to a shared corpus. Encrypted multi-database bundles are available through `python manage.py backup-tenancy DIR --quiesced` and `python manage.py restore-tenancy FILE --target-root NEW_DIRECTORY`; stop application writes for the full backup window, configure `BACKUP_KEY`, and restore only to a new directory. Rollback rehearsal and end-to-end recovery acceptance are still required before production use. Optional local OCR exists, but Arabic OCR quality has not yet been validated on a representative Egyptian court-scan benchmark. Admins can reset passwords manually with `python manage.py resetpw EMAIL`; there is no self-service email reset.

## Loading law data
1. Download PDFs plus their .json metadata (see download_egypt_laws.py), then: `python tools/import_laws.py egypt_laws out` (needs pymupdf; PDFs with a broken text layer are OCR'd, which needs tesseract; the run is resumable).
2. Read `out/import_report.md` (articles found per block, missing numbers) and fix or flag gaps by hand.
3. Load: `python manage.py importlaws out/law_rows.jsonl`.
Every row generated by the PDF and Arabic fetch scripts defaults to `in_force: 0` and `verified: 0`; this deliberately does not assert that the law is currently in force. The API also defaults omitted `in_force` to 0. Keep imported records unavailable to current-law retrieval until a qualified reviewer verifies both the text and legal status. The source URL, retrieval date and file hash help trace the material, but do not prove authenticity or current force.
Search works on the language of the data: English texts are found by English questions only. Arabic questions need Arabic law texts.

## Arabic law text (labor law)
`python tools/fetch_arabic_law.py out_dir` downloads the Arabic text of Labor Law No. 14 of 2025 (run it on a machine with internet), splits it into articles
(issuing articles and the accompanying law as separate blocks), and writes `law_rows_ar.jsonl` plus `import_report_ar.md`. Check the report (missing numbers,
the end of the last article) before loading with `python manage.py importlaws out_dir/law_rows_ar.jsonl`. The source page is an unofficial republication of the
Official Gazette text: compare it with the Gazette (issue 18 bis, 3 May 2025) before treating it as verified. If the download is blocked, save the page in your
browser and use `--file saved_page.html`.


## Arabic law dataset (not bundled)
This repository does **not** contain `data/law_rows_ar.jsonl`. Generate an Arabic dataset with `python tools/fetch_arabic_law.py out_dir`, or obtain a separately supplied dataset and verify its provenance. The fetch script uses an unofficial republication of Labor Law No. 14 of 2025; compare every imported text with the Official Gazette (issue 18 bis, 3 May 2025) before relying on it. Imported rows should remain marked unverified until reviewed by a qualified person. Do not assume that a downloaded dataset is official or complete.

## Legal Research chat behavior

The Legal Research tab stores conversations per user and firm and uses earlier **user questions** to interpret short follow-ups. Prior assistant answers are not reused as legal evidence. Each answer is grounded in the currently retrieved passages, with numbered citations checked against the returned source set; if retrieval finds no sufficiently relevant source, the API returns a no-source response rather than inventing an answer. Arabic and English questions are supported by the response instructions, but answer quality depends on the language and quality of the indexed source material and configured model.

Source status labels are intentionally conservative: material not marked verified is shown as **Unverified source**, not automatically as repealed or not in force. Only verified material explicitly marked not in force receives the **Not in force** label. This is not a substitute for checking the official publication and amendment history. Uploaded material does not retrain the model; it must be ingested into the searchable corpus and reviewed under the legal-data workflow before being relied on.

## Optional scanned-PDF OCR

The case-file upload endpoint can attempt local OCR when a PDF has no extractable text. Install the optional Python packages from `requirements-ocr.txt` and install the Tesseract executable plus Arabic and English language data on the host. Set `OCR_LANG` if your installed language codes differ (default: `ara+eng`). OCR is limited to 30 pages per upload and uses a per-page timeout. Missing dependencies, missing language packs, or OCR failures produce an explicit error instead of silently storing an empty document.

A successful OCR upload returns `ocr_used: true` and `text_status: "ocr_unverified"`. This indicates only that text was recognized; it does not establish authenticity, completeness, or legal status. Review OCR against the original page images before relying on it, and do not mark legal materials verified solely because OCR succeeded.

For a repeatable page-level quality measurement workflow, see [Arabic OCR evaluation](docs/arabic_ocr_evaluation.md). The evaluator is tooling only; no representative real-scan benchmark has passed yet.

## Amendment-history audit

Run `python tools/audit_legal_corpus.py --db path/to/legal.db --out-dir reports/legal-audit` to generate a read-only metadata audit. The audit flags versions marked in force and verified without an amendment-history review, amendment-history flags that lack a passing review event with an evidence URL, and version relations whose endpoints have unreviewed histories. It reports findings; it never changes review flags or legal status. A passing metadata audit is not proof that the legal instrument is authentic, consolidated, or currently in force. A qualified reviewer must compare the official source and the applicable amendment/repeal instruments.

## Version-aware research citations

Research search results include a `provenance` object for each citation. When a passage is linked to the legal-version registry, this includes the registered title and version, source URL, publication/effective/repeal dates, gazette metadata, recorded legal/review status, content hash when available, review events and their evidence URLs, and linked amendment/repeal/consolidation relations. The research UI displays the metadata that exists; absent values remain absent rather than being inferred.

Legacy passages without a `document_version_id` are explicitly returned as `legacy_unlinked`; they do not gain provenance by inference. This is a migration warning, not proof that a passage is false. Before relying on a citation for a legal opinion, reviewers should link the passage to the exact reviewed version and verify the cited official publication and applicable amendments. Registry metadata and an evidence URL alone do not establish legal correctness.


## Phase 2 amendment relationship register

Before using the discovery-level amendment graph, run `python tools/validate_amendment_relationships.py`. It checks structural integrity and reports unresolved evidence, provision-mapping, and review-status gaps without changing the register. See [the audit guide](docs/amendment_relationship_validator.md). Structural validation is not legal confirmation; only evidence-backed review by qualified Egyptian counsel can support current-law conclusions.

## Legal source review queue

Run `python tools/legal_source_review_queue.py --db path/to/legal.db --out reports/legal-source-review-queue.json` to generate a read-only reviewer queue for missing source/version provenance, legal-status and amendment-history checks, review-event evidence, and source collection/commercial-reuse permissions. See [`docs/legal_source_review_queue.md`](docs/legal_source_review_queue.md) for report fields and limitations. The queue prioritizes follow-up; it does not verify legal correctness or change review statuses.

## Evidence-backed legal review events

Administrators can append and inspect legal-source review events through `POST /legal-review/versions/{version_id}/events` and `GET /legal-review/versions/{version_id}/events`. Events require scoped review types and passing events require an HTTPS evidence URL. Recording an event never changes verification flags or legal status. See [`docs/evidence_backed_legal_review_events.md`](docs/evidence_backed_legal_review_events.md) for access controls and limitations.

## Legal source review workbench

Administrators can inspect registered legal document versions and review-event history from the **Legal Source Review** page, and append evidence-backed review events. Events never automatically change verification flags or legal status. See [`docs/legal_source_review_workbench.md`](docs/legal_source_review_workbench.md) and [`docs/evidence_backed_legal_review_events.md`](docs/evidence_backed_legal_review_events.md).

## Safe legacy law imports

The legacy bulk import endpoint forces imported passages to remain unverified and not in force until reviewed; caller-supplied flags cannot make an unlinked passage searchable as verified law. See [`docs/safe_legacy_law_imports.md`](docs/safe_legacy_law_imports.md). This does not retroactively repair existing unlinked records.
