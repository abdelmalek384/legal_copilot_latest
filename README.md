# Legal Copilot MVP (Egyptian law, Arabic-first)
Case folders with Egyptian case metadata, internal notes, legal deadlines separate from court sessions, fee tracking, team management, session tracking, hybrid law search (SQLite FTS5 + Arabic-normalized trigram similarity + exact article lookup),
and answers that must cite numbered sources. If nothing relevant is found, or the model's citations fail the check, it shows sources only.

Mac quick start: double-click `start_mac.command`; it creates a virtual environment, installs dependencies, prompts to create the first admin account if needed, and starts the app locally. Manual run: `pip install -r requirements.txt`, then `python selftest.py`, then `uvicorn app:app --host 127.0.0.1 --port 8000` and open http://127.0.0.1:8000
Load law: POST a JSON list of {law, article, text, as_of, in_force, source} to /law/import (see sample_law.jsonl: FICTIONAL test text only).
Model: set LLM_URL (OpenAI-compatible /chat/completions, e.g. vLLM or Ollama), LLM_MODEL, LLM_KEY. Unset = sources-only mode.

Not included yet: verified official law/ruling data, Arabic OCR, WhatsApp/SMS delivery
of reminders (use /sessions/upcoming from a scheduler), embedding-model search, amendment/version tracking.

## Arabic handling
Normalizes diacritics, tatweel, alef/hamza forms, ya/alef maqsura, ta marbuta, and Arabic-Indic digits (so "المادة ٥" finds article 5);
light prefix/suffix stemming and stopword removal at both index and query time; exact article-number lookup; RTL UI with Arabic fonts.
Known limits: no broken-plural or Egyptian-dialect handling, no semantic embeddings yet (next step: an Arabic-capable multilingual
embedding model such as bge-m3 or multilingual-e5, stored in pgvector), and MIN_SCORE (default 0.3) must be tuned on a real evaluation set.

## Setup and security
1. `pip install -r requirements.txt`, then `python selftest.py && python api_test.py`.
2. Create the first account: `python manage.py adduser "Name" name@firm.eg admin` (roles: admin, lawyer, junior; password min 12 characters). When typing the password in the terminal, characters do not appear on screen; this is normal. Press Enter after typing it. If you need to change a forgotten password later, run `python manage.py resetpw name@firm.eg`.
3. Set ADMIN_TOKEN='<long random>' (header X-Admin-Token on /law/import). Optional: LLM_URL / LLM_MODEL / LLM_KEY.
4. Run `uvicorn app:app` only behind an HTTPS reverse proxy (Caddy or nginx).
5. Backups: `python manage.py genkey` once (store the key OFF the server), then daily via cron:
   `BACKUP_KEY=... python manage.py backup /safe/path --keep 14`. Restore: `python manage.py restore FILE OUT.db`. Test a restore.
6. Encrypt the server disk (LUKS or your host's volume encryption). The database itself is not encrypted, so disk encryption is what protects it at rest.

Permissions: admin sees all cases; a lawyer sees only cases they belong to; only a case's lead (or admin) can edit status, manage the team, or delete.
Uploads: PDF/DOCX with real text only (max 15 MB); original files are not stored, only the extracted text. Scanned PDFs are rejected.
Not yet done: independent security review, rate limiting beyond login lockout, 2FA, password reset, audit export, OCR, reminders, embeddings, a formal conflict-check workflow beyond the basic text-match screen.

## Loading law data
1. Download PDFs plus their .json metadata (see download_egypt_laws.py), then: `python tools/import_laws.py egypt_laws out` (needs pymupdf; PDFs with a broken text layer are OCR'd, which needs tesseract; the run is resumable).
2. Read `out/import_report.md` (articles found per block, missing numbers) and fix or flag gaps by hand.
3. Load: `python manage.py importlaws out/law_rows.jsonl`.
Every imported row is marked unverified and carries its source URL, retrieval date and file hash; the UI shows "not verified in force" and "unofficial English translation" badges until a human reviews it.
Search works on the language of the data: English texts are found by English questions only. Arabic questions need Arabic law texts.

## Arabic law text (labor law)
`python tools/fetch_arabic_law.py out_dir` downloads the Arabic text of Labor Law No. 14 of 2025 (run it on a machine with internet), splits it into articles
(issuing articles and the accompanying law as separate blocks), and writes `law_rows_ar.jsonl` plus `import_report_ar.md`. Check the report (missing numbers,
the end of the last article) before loading with `python manage.py importlaws out_dir/law_rows_ar.jsonl`. The source page is an unofficial republication of the
Official Gazette text: compare it with the Gazette (issue 18 bis, 3 May 2025) before treating it as verified. If the download is blocked, save the page in your
browser and use `--file saved_page.html`.


## Included Arabic law dataset
`data/law_rows_ar.jsonl` is supplied separately from the application database and is **not imported automatically**. It contains 311 rows associated with Labor Law No. 14 of 2025, from an unofficial republication. Rows are marked unverified. Verify the text against the Official Gazette and review the accompanying source notes before importing. To import only after review: `python manage.py importlaws data/law_rows_ar.jsonl`.
