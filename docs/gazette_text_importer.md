# Offline Gazette text importer

## Purpose and trust boundary

`tools/import_gazette_text.py` converts a lawyer-supplied UTF-8 transcription into quarantined, article-level JSONL candidate rows. It is an offline transcription/staging tool. It does **not**:

- fetch a Gazette document or prove that a supplied file came from the Official Gazette;
- verify a signature, scan, page sequence, transcription accuracy, or document authenticity;
- establish copyright, collection permission, or reuse rights;
- determine whether a provision is currently in force or identify amendments/corrigenda;
- authorize legal retrieval or mark any provision lawyer-reviewed.

Every generated row must remain `verified=0`, `in_force=0`, and `as_of=null`. Do not edit those flags to bypass the human review process.

## Inputs

The command takes three positional arguments:

```sh
python tools/import_gazette_text.py /secure/input/gazette.txt /secure/input/gazette.metadata.json /secure/output/law14-candidate
```

- `text_file`: UTF-8 text transcription. A UTF-8 BOM is accepted. NUL characters are rejected. Maximum 20 MiB.
- `metadata_json`: UTF-8 JSON object. A UTF-8 BOM is accepted. Maximum 1 MiB.
- `output_dir`: a new or empty directory outside the source text's parent directory. Existing output files are never overwritten.

The text and metadata must be different files. Source and metadata inputs must be regular files, not symlinks; the importer checks file identity and size while reading.

## Metadata contract

Required non-empty string fields:

| Field | Requirement |
|---|---|
| `document_id` | 1–128 characters; starts alphanumeric; remaining characters are alphanumeric, dot, underscore or hyphen |
| `official_title` | Human-readable title supplied by the reviewer |
| `language` | Must be `ar` |
| `gazette_issue` | Issue/number as supplied; not independently verified |
| `publication_date` | Exact ISO date `YYYY-MM-DD` |
| `retrieved_at` | ISO date or ISO datetime |
| `captured_by` | Supplier/reviewer attribution |
| `capture_method` | `lawyer_supplied_text` or `manual_transcription` |
| `content_sha256` | SHA-256 hex digest of the exact input text-file bytes |

Additional required control field:

- `supplier_role`: must be `egyptian_lawyer` or `qualified_egyptian_counsel`. This is a supplied declaration, not identity or licence verification.

Source locator: provide either a non-empty `source_url` or a non-empty `source_reference`. If a URL is supplied, it must be HTTPS and must not contain whitespace, C0/DEL control characters, credentials, backslashes, a fragment delimiter (including an empty `#`), invalid authority/port syntax, or recognized signed/credential query parameters. A source reference is a human-supplied locator, not proof of authority.

Optional collection-rights fields:

- `collection_permission`: `unknown` (default), `allowed`, or `not_allowed`. The importer refuses `not_allowed`.
- `permission_evidence_reference`: required and non-empty when permission is `allowed`; retain a reference to the separate evidence. The importer does not assess that evidence.

Example metadata (replace all illustrative values; this example is not a legal-source record):

```json
{
  "document_id": "EXAMPLE-GAZETTE-001",
  "official_title": "عنوان الوثيقة كما ورد",
  "language": "ar",
  "gazette_issue": "العدد ...",
  "publication_date": "2025-05-03",
  "retrieved_at": "2026-11-12T10:00:00+02:00",
  "captured_by": "اسم المراجع",
  "supplier_role": "egyptian_lawyer",
  "capture_method": "lawyer_supplied_text",
  "source_reference": "مرجع المصدر الذي قدمه المحامي",
  "content_sha256": "REPLACE_WITH_64_HEX_SHA256_OF_EXACT_TEXT_BYTES",
  "collection_permission": "unknown"
}
```

## Parsing and output

The parser recognizes Arabic/English numeric article headings using the shared law importer heading pattern. It also separates the 13 known Arabic ordinal promulgation headings from the attached law's numeric article sequence, so numbering restarts do not collide. Preamble text before the first recognized heading is excluded and its character count is reported; review it to ensure no legal provision was missed.

The output directory contains:

- `law_rows.jsonl`: one candidate row per text chunk, with law label, article/provision type, source/document metadata, exact text SHA-256, and collection-permission fields;
- `import_report.md`: heading counts, numbering gaps/duplicates by block, empty article bodies, excluded preamble count, and mandatory human-review warnings.

The importer reports duplicate/missing article numbers but does not repair or renumber them. Empty article bodies and unparsed preamble require human review. Tables, schedules, page breaks, handwritten annotations, OCR errors, and provisions not matching recognized headings may need separate handling.

The candidate JSONL preserves the fields consumed by the quarantined `manage.py importlaws` staging path. Importing into staging is a separate operation; staging is not legal verification or publication to retrieval.

## Safe handling and review checklist

1. Keep the original Gazette scan/file, its hash, page count, and chain-of-custody notes in controlled storage.
2. Have a qualified reviewer compare each transcription block against the corresponding source page.
3. Resolve every numbering gap, duplicate, empty body, excluded preamble, schedule, table, and page discontinuity.
4. Record source authenticity, reuse/collection rights, amendment/corrigendum checks, and currentness separately.
5. Keep all machine-generated trust flags unchanged until the formal lawyer-review workflow authorizes a change.
6. Do not commit confidential source files, lawyer identity evidence, private permission documents, or client data.

## Failure behavior

Invalid UTF-8/JSON, malformed metadata, hash mismatch, unsupported supplier/capture values, invalid source URLs, disallowed collection permission, unsafe input files, missing headings, or non-empty output directories cause a concise command-line error. The importer does not overwrite existing output. If a write fails after creating one output file, it attempts to remove files created during that failed run.

## Validation status

The repository contains focused tests in `tests/test_import_gazette_text.py`, including the 13-promulgation/298-attached-article structure fixture and filesystem/URL safeguards. Test execution must be recorded separately; a source review or the existence of tests is not a test pass. Run:

```sh
python -m unittest tests.test_import_gazette_text
```

Use the repository's Python 3.12 hash-locked environment for release validation.
