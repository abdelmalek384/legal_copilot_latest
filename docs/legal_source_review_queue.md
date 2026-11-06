# Legal source review queue

Run the read-only queue against the approved legal-corpus database or a protected copy bound to the immutable `legal_corpus` profile:

```bash
export COPILOT_CORPUS_DB="/absolute/path/to/legal-corpus.sqlite3"
python tools/legal_source_review_queue.py --out reports/legal-source-review-queue.json
python tests/test_legal_source_review_queue.py
```

You may pass an explicit `--db` path instead. The tool refuses unbound databases, databases bound to another profile, and any run with the old `COPILOT_DB` compatibility variable configured.

The report prioritizes version records that need evidence for source authenticity, extraction quality, legal status, amendment history, licensing, and lawyer approval. It also lists source records with unresolved collection/commercial reuse permission, restricted commercial reuse, or limited reuse scope, as well as missing terms links or missing permission evidence. Commercial reuse is considered unrestricted only when the recorded value is exactly `allowed`; `allowed_limited`, prohibited, and unknown states stay visible for review.

Each version entry includes the metadata currently recorded, review events, machine-readable reasons, and a suggested next action. Versions whose document or source record is missing are retained in the queue and flagged instead of disappearing through an inner join. Missing dates or review evidence are unknown/unresolved—not proof that an instrument is invalid. This queue does not fetch sources, modify the database, change a review status, establish legal effect, or grant collection/reuse rights. Reviewers must inspect the original official publication and record the scope and evidence for each decision. A passing event with an evidence URL is a recorded workflow fact, not independent proof that the URL is authoritative or its contents are correct.

A current review checklist is evaluated against the latest event for each required review type, ordered by reviewed timestamp and event ID. Every latest event must pass, include a non-empty reviewer, non-empty notes, and a valid HTTPS evidence URL without credentials; the latest lawyer-approval event must also contain the exact positive account-ID counsel-attestation marker. A later fail, pending, or needs-correction event supersedes an earlier pass. Malformed or future-dated event history is flagged rather than treated as current evidence; older events remain in the report for audit context. The tool exits with status 2 when required registry tables or columns are missing. An empty queue means only that no records matched these configured checks; it does not certify legal correctness.


Evidence URLs are checked for HTTPS syntax, whitespace, embedded credentials, and malformed or out-of-range ports. The audit does not fetch links or establish that the linked material is authentic, relevant, or authoritative.
