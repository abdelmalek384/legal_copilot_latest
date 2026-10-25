# Legal source review queue

Run a read-only queue against a local Legal Copilot SQLite database:

```bash
python tools/legal_source_review_queue.py --db path/to/legal.db --out reports/legal-source-review-queue.json
python tests/test_legal_source_review_queue.py
```

The report prioritizes version records that need evidence for source authenticity, extraction quality, legal status, amendment history, licensing, and lawyer approval. It also lists source records with unresolved collection/commercial reuse permission, restricted commercial reuse, or limited reuse scope, as well as missing terms links or missing permission evidence. Commercial reuse is considered unrestricted only when the recorded value is exactly `allowed`; `allowed_limited`, prohibited, and unknown states stay visible for review.

Each version entry includes the metadata currently recorded, review events, machine-readable reasons, and a suggested next action. Versions whose document or source record is missing are retained in the queue and flagged instead of disappearing through an inner join. Missing dates or review evidence are unknown/unresolved—not proof that an instrument is invalid. This queue does not fetch sources, modify the database, change a review status, establish legal effect, or grant collection/reuse rights. Reviewers must inspect the original official publication and record the scope and evidence for each decision. A passing event with an evidence URL is a recorded workflow fact, not independent proof that the URL is authoritative or its contents are correct.

The tool exits with status 2 when required registry tables or columns are missing. An empty queue means only that no records matched these configured checks; it does not certify legal correctness.
