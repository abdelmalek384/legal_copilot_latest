# Legal source review workbench

Administrators see a **Legal Source Review** item in the application navigation. The page reads `GET /legal-review/queue` to list registered legal-document versions, current recorded status fields, source metadata, effective dates, and review-event counts. A reviewer can select a version, inspect its existing review events, and append a new event through the API documented in [Evidence-backed legal review events](evidence_backed_legal_review_events.md).

The interface supports searching the loaded list, opening a registered source URL in a separate tab, viewing event history, and recording review type, outcome, evidence URL, and notes. A passing outcome requires a syntactically valid HTTPS evidence URL. The server rejects embedded credentials, whitespace, malformed ports, and invalid port ranges. This is URL-shape validation only; it does not prove the linked evidence is authentic or relevant.

## Boundaries

- Only administrators can access the queue and event endpoints.
- This interface records workflow evidence supplied by a reviewer; it does not independently validate linked pages.
- Current eligibility uses the latest event for each required review type. A later fail, pending, or needs-correction event supersedes an older pass; the latest lawyer-approval pass must contain the exact positive account-ID counsel-attestation marker. Each current event also requires a non-empty reviewer, non-empty notes, a valid HTTPS evidence URL, and a non-future timestamp.
- Recording a review event does not change `review_status`, `legal_status`, authenticity/status/amendment verification flags, or legal-research eligibility.
- Source URL availability is not proof of authority. Reviewers should confirm the original official Gazette or other applicable official publication and document the scope of the review.
- The queue is limited to the first 500 versions and is not a substitute for the read-only CLI audit or a complete legal audit.
