# Acquisition-readiness audit

The read-only audit compares the candidate collection manifest with the source permission register before any retrieval is attempted.

## Run

From the repository root:

```bash
python tools/validate_acquisition_readiness.py
```

The default command writes a JSON report to stdout and exits successfully when the audit completes, even if documents are blocked. This is deliberate: the current example manifest is a planning artifact, and its pending entries should be reported rather than silently promoted.

To use the command as the production release gate, require both collection readiness and source-level commercial product-use permission:

```bash
python tools/validate_acquisition_readiness.py --manifest path/to/authorized_manifest.json --register docs/source_permission_register.json --require-ready
```

`--require-ready` exits nonzero unless every manifest document is both collection-ready and commercially cleared. If a document may be collected for a non-commercial research purpose only, `--require-collection-ready` checks collection permission alone; it is not sufficient for production use in the commercial Legal Copilot product.

Use `--out path/to/report.json` to preserve a report.

## What it checks

- Each manifest document has a source record in the permission register.
- The manifest's collection permission is explicitly `allowed`.
- The source register independently records `allowed` or `allowed_limited`, with permission evidence and a valid terms-review date.
- The manifest has its own permission evidence and a valid terms-review date that is not in the future.
- A document-level `permission_scope_review` is marked `passed` and records a reviewer, evidence reference, valid review date not earlier than the terms-check date, reviewed source terms, and the `direct_document_url` method. It must explicitly approve storage, text extraction, indexing, commercial product use, and excerpt display. Optional evidence URLs must be HTTPS and contain no credentials.
- The direct URL is HTTPS and its hostname matches the document's explicit allowlist.
- Commercial product use requires both source-level commercial permission and a complete document-level scope review. Collection permission or a status flag alone is insufficient. The production `--require-ready` switch enforces both gates; `--require-collection-ready` intentionally checks only the narrower collection gate.

## Limits

The audit is a preflight consistency check, not a legal opinion and not a permission grant. It cannot independently determine whether evidence actually covers the exact document, acquisition method, storage, extraction/OCR, indexing, commercial use, excerpt display, or redistribution. The `permission_scope_review` record must be completed by a human reviewer who compares the written authorization or applicable terms against each intended use; do not set it to `passed` merely to silence a blocker. Its required fields now match the collection pipeline's runtime gate so a manifest cannot be reported ready under a weaker scope-review contract than the downloader enforces.

The audit does not download files, crawl sites, change status fields, verify legal authenticity, infer commencement dates, establish amendment history, or mark a document current law. Legal-status review and qualified Egyptian-lawyer approval remain separate release gates.
