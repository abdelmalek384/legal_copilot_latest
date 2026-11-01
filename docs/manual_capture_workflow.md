# Recording a document you saved by hand

Use `tools/record_manual_capture.py` when a source cannot or should not be collected automatically (for example the site disallows bots, has a certificate problem, or only offers a browser download). A person opens the official source, saves the file, and records it. The tool never touches the network.

## Steps

1. **Open the official source in a browser** and save the document (PDF, HTML, plain-text UTF-8, or DOCX). Write down the exact page or file URL you used.
2. **Record it:**
   ```bash
   python tools/record_manual_capture.py \
       --file ~/Downloads/gazette_issue_18.pdf \
       --document-id EG-LABOUR-14-2025 \
       --source-url "https://exact.source/url/you/used" \
       --captured-by "Your Name" \
       --capture-method browser_download \
       --retrieved-on 2026-10-26 \
       --gazette-issue "18 (تابع)"
   ```
   Add `--dry-run` first to see what would be written. The document id must exist in `docs/legal_document_candidates.json` (or pass `--source-id`).
3. **Read the result.** The tool copies the original into `legal_corpus/originals/<id>/`, writes `metadata/<id>.json`, extracts text, runs the article audit, and appends a `pending_human_review` entry to `review_queue.jsonl`.
4. **Compare and review.** Use `tools/compare_corpus_to_reference.py` to compare any candidate corpus with this text, then have a lawyer review the differences.

## What this does and does not establish

- It records what was saved, from where, when and by whom, plus the SHA-256 of the file.
- It does **not** establish permission to store, index, embed, display or commercially reuse the content. The metadata keeps `collection_permission: not_established_manual_capture`.
- It does **not** prove authenticity or current legal status. Those remain `false` and the item remains `pending_human_review` until separate review.
- It never fetches the URL, bypasses access controls, or changes source-permission registers.
