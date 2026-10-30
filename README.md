# Legal Copilot MVP (Egyptian law, Arabic-first)
Case folders with Egyptian case metadata, internal notes, legal deadlines separate from court sessions, fee tracking, team management, session tracking, hybrid law search (SQLite FTS5 + Arabic-normalized trigram similarity + exact article lookup),
and answers that must cite numbered sources. If nothing relevant is found, or the model's citations fail the check, it shows sources only.

Mac quick start: double-click `start_mac.command`; it creates a virtual environment, installs dependencies, initializes separate control-plane, firm, and shared-corpus databases under `./data`, prompts to create the first firm administrator if needed, and starts the app locally. Manual run: follow the initialization and first-owner bootstrap steps under [Setup and security](#setup-and-security), set `COPILOT_CONTROL_DB`, `COPILOT_TENANT_DB_ROOT`, and `COPILOT_CORPUS_DB` to three distinct paths, then run `python -m uvicorn app:app --host 127.0.0.1 --port 8000` and open http://127.0.0.1:8000. The app fails closed unless the separate profile paths are configured. The shared `COPILOT_DB` compatibility harness is not an approved fresh-install path and is allowed only when `COPILOT_ENV=development` is explicitly selected; never use it for staging or production. No legacy data import is part of this project.
Load law: POST a JSON list of {law, article, text, as_of, in_force, source} to /law/import (see sample_law.jsonl: FICTIONAL test text only).
Model: set LLM_URL (OpenAI-compatible /chat/completions, e.g. vLLM, Ollama, or a hosted provider), LLM_MODEL, and LLM_KEY. The app does not choose or bundle a model. LLM_URL alone is not enough to send prompts: explicitly set LLM_DATA_PROCESSING_APPROVED=1 only after reviewing the endpoint, data-processing terms, retention, and whether matter data may be sent. Case-scoped research, follow-up conversation context, and matter-file passages additionally require `LLM_FIRM_DATA_PROCESSING_APPROVED=1`; otherwise those requests return sources only. These are deployment attestations, not consent or privacy guarantees. See [LLM data-processing policy](docs/llm_data_processing_policy.md).

Container deployment template: see [the hardened Docker/Compose deployment guide](docs/container_deployment.md). It uses the checked-in Python 3.12 hash lock, a non-root read-only container, separate persistent database paths, S3/KMS configuration, and explicit database-acceptance evidence. It is a deployment template, not a completed production deployment; staging, recovery, security, and lawyer acceptance gates remain mandatory.

Not included yet: a complete verified official law/ruling corpus, production-ready reminder operations (a tenant-scoped durable outbox, dry-run-by-default operator scheduler, and read-only external health probe now exist, but SMTP provider staging, external scheduling/alerting, and operator reconciliation remain release gates; see [the scheduler contract](docs/reminder_scheduler_contract.md) and [the monitoring runbook](docs/reminder_outbox_monitoring_runbook.md)), WhatsApp/SMS delivery, embedding-model semantic search, and a complete end-to-end amendment/consolidation workflow.

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

## Reminder operations and monitoring

The deadline reminder scheduler is dry-run by default. Do not enable SMTP delivery until provider staging, authorization/concurrency tests, and operator ownership are complete. Run the read-only outbox monitor with `PYTHONPATH=. python tools/reminder_healthcheck.py`; it returns exit code 1 when operator attention is needed and 2 when it cannot safely complete. See [reminder outbox monitoring and reconciliation](docs/reminder_outbox_monitoring.md). SMTP acceptance is not proof of inbox delivery.

## Arabic handling
Normalizes diacritics, tatweel, alef/hamza forms, ya/alef maqsura, ta marbuta, and Arabic-Indic digits (so "المادة ٥" finds article 5);
light prefix/suffix stemming and stopword removal at both index and query time; exact article-number lookup; RTL UI with Arabic fonts.
Known limits: no broken-plural or Egyptian-dialect handling, no semantic embeddings yet (next step: an Arabic-capable multilingual
embedding model such as bge-m3 or multilingual-e5, stored in pgvector), and MIN_SCORE (default 0.3) must be tuned on a real evaluation set.

## Install on a phone or desktop

The web app includes an installable PWA shell for compatible browsers. Serve it over HTTPS, then use the browser's **Install app** or **Add to Home Screen** action. The service worker caches only a static offline notice; case data, uploaded files, account/session data, and research responses are never cached. See [PWA installation and privacy limits](docs/pwa_installation.md) and the [manual device/browser acceptance runbook](docs/device_browser_acceptance_runbook.md).

## Setup and security

For a fresh installation, use the separate-database architecture. Do not follow old single-file database instructions for a fresh install.

### Mac quick start

Install Python **3.12 or newer**, then run `./start_mac.command` from the repository folder (or double-click it in Finder). The script creates a virtual environment, verifies that both the host Python and any existing `.venv` meet the version requirement, installs dependencies, initializes separate control-plane, per-firm, and shared-legal-corpus databases, and uses the shared bilingual first-firm bootstrap helper when no active membership exists. It will not delete an existing `.venv` if its Python version is too old.

### Windows quick start

On Windows 10/11, install **Python 3.12** with the Python Launcher enabled, then double-click `start_windows.bat` from the repository folder. The launcher creates a local virtual environment, installs the requirements, initializes the separate control-plane/firm/corpus database profiles, and safely prompts for the first firm owner when needed. It binds the development server to `127.0.0.1` only; keep the terminal window open while using the app.

The launcher refuses an inherited `COPILOT_DB` setting because that selects the legacy shared-database compatibility mode. It does not reset or delete existing data. For an existing installation, keep the three profile paths pointed at the same persistent directories used previously. This is a local development launcher, not a production deployment procedure.


### Manual local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

mkdir -p data/tenants
export COPILOT_CONTROL_DB="$PWD/data/control_plane.sqlite3"
export COPILOT_TENANT_DB_ROOT="$PWD/data/tenants"
export COPILOT_CORPUS_DB="$PWD/data/legal_corpus.sqlite3"

python -c "from database_runtime import DatabaseRuntime; DatabaseRuntime.from_env().initialize()"
python manage.py init-tenancy --firm-name "Example Firm" --owner-name "First Owner" --owner-email owner@example.com
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 on the same machine. The three database paths must remain distinct. Do not set `COPILOT_DB` for a fresh install; it is legacy compatibility mode. Do not expose the development server directly to the internet.

### Production and model-processing gates

Before any real-client deployment, follow the [production deployment checklist](docs/production_deployment_checklist.md), run `python tools/deployment_preflight.py --strict`, and review the [aggregate production release gate](docs/production_release_gate.md). These checks are necessary but not a substitute for independent security review, witnessed recovery testing, or legal validation.

A model endpoint must not receive prompts until its data-processing terms, retention, access controls, and matter-data suitability have been reviewed and `LLM_DATA_PROCESSING_APPROVED=1` is set. Case-scoped prompts, prior-question follow-up context, and matter-file passages additionally require `LLM_FIRM_DATA_PROCESSING_APPROVED=1`. These flags are deployment attestations, not client consent or a guarantee of provider compliance. See [LLM data-processing policy](docs/llm_data_processing_policy.md).

### Automated security scanning

The repository's CodeQL workflow analyzes Python and frontend JavaScript, and Bandit scans the backend/security tooling. Review code-scanning alerts and CI finding summaries; a successful scan is not proof of a vulnerability-free application. See [static security analysis and finding triage](docs/static_security_analysis.md). Independent security assessment remains a production release gate.

### Backup and restore

The single-file `backup` / `restore` commands are disabled. Use encrypted tenancy bundles so the control plane, per-firm databases, and legal corpus are captured and restored together.

```bash
python manage.py genkey
# Store the generated key in a protected secret store, not in the repository.
read -rsp "BACKUP_KEY: " BACKUP_KEY; echo
export BACKUP_KEY
python manage.py backup-tenancy /safe/backup/path --quiesced --keep 14
python manage.py verify-backup-tenancy /safe/backup/path/backup-file.enc
python manage.py restore-tenancy /safe/backup/path/backup-file.enc --target-root /new/restore/directory
unset BACKUP_KEY
```

Keep application writes paused for the full backup snapshot window. Verify a bundle before recovery, restore only to a new target directory, and complete a witnessed restore/rollback drill before production. For non-interactive deployments, inject the key from the deployment's protected secret manager. Never place real keys in tickets, chat, or source control. The commands above are operator examples; replace paths and the key placeholder with values from your deployment's protected secret store.

### Account and privilege operations

The first firm owner is created with `init-tenancy` during fresh setup. Platform roles are distinct from firm roles. Use the reviewed account-lifecycle and privileged-role procedures; do not treat a firm administrator as a platform administrator, and do not use an ad-hoc SQL edit to recover an account. See the current CLI help (`python manage.py --help`) and production checklist before operator actions.

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
