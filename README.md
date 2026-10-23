# Legal Copilot MVP (Egyptian law, Arabic-first)
Case folders with Egyptian case metadata, internal notes, legal deadlines separate from court sessions, fee tracking, team management, session tracking, hybrid law search (SQLite FTS5 + Arabic-normalized trigram similarity + exact article lookup),
and answers that must cite numbered sources. If nothing relevant is found, or the model's citations fail the check, it shows sources only.

Mac quick start: double-click `start_mac.command`; it creates a virtual environment, installs dependencies, prompts to create the first admin account if needed, and starts the app locally. Manual run: `pip install -r requirements.txt`, then `python selftest.py`, then `uvicorn app:app --host 127.0.0.1 --port 8000` and open http://127.0.0.1:8000
Load law: POST a JSON list of {law, article, text, as_of, in_force, source} to /law/import (see sample_law.jsonl: FICTIONAL test text only).
Model: set LLM_URL (OpenAI-compatible /chat/completions, e.g. vLLM or Ollama), LLM_MODEL, LLM_KEY. Unset = sources-only mode.

Not included yet: a complete verified official law/ruling corpus, WhatsApp/SMS delivery
of reminders (use /sessions/upcoming from a scheduler), embedding-model semantic search, and a complete end-to-end amendment/consolidation workflow.

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

Before any authorized acquisition, review [the acquisition-readiness audit](docs/acquisition_readiness_audit.md) and run its read-only preflight against the candidate manifest and source permission register. A manifest entry marked pending is not permission to download, and collection readiness is not commercial reuse permission.

See [the bootstrap guide](docs/legal_corpus_bootstrap.md), [candidate instrument catalogue](docs/legal_document_candidates.json), and [source permission register](docs/source_permission_register.json). Do not collect or commercially reuse a source unless the applicable permission has been established and documented.

## Arabic handling
Normalizes diacritics, tatweel, alef/hamza forms, ya/alef maqsura, ta marbuta, and Arabic-Indic digits (so "المادة ٥" finds article 5);
light prefix/suffix stemming and stopword removal at both index and query time; exact article-number lookup; RTL UI with Arabic fonts.
Known limits: no broken-plural or Egyptian-dialect handling, no semantic embeddings yet (next step: an Arabic-capable multilingual
embedding model such as bge-m3 or multilingual-e5, stored in pgvector), and MIN_SCORE (default 0.3) must be tuned on a real evaluation set.

## Setup and security
1. `pip install -r requirements.txt`, then `python selftest.py && python api_test.py`.
2. Create the first account: `python manage.py adduser "Name" name@firm.eg admin` (roles: admin, lawyer, junior; password min 12 characters). When typing the password in the