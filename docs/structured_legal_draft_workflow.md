# Structured legal draft packet (initial workflow)

This is a conservative first step toward drafting common Egyptian legal documents such as **مذكرة دفاع** and **صحيفة دعوى**. It creates an editable Markdown structure from lawyer-supplied data; it is not an AI legal-reasoning engine and does not integrate with the web UI or case database.

## Safety model

- Facts, legal arguments, and requested relief must be entered by the lawyer. The tool formats them; it does not invent facts or generate legal theories.
- A source is listed only when the input explicitly records lawyer approval, authenticity_verified = true, legal_status = "in_force", status_verified = true, a permitted source state (allowed or allowed_limited), recorded permission evidence, an HTTPS source URL, an effective date, a review date, a title, and a citation.
- Future-effective, future-reviewed, and repealed-at-the-requested-date sources are excluded. This is a fail-closed filter on supplied metadata, not independent verification of that metadata.
- Source permission in this input is not a blanket determination that every use or commercial reuse is lawful. The applicable source terms and permission evidence still need human review.
- If no source passes the filter, the draft says so and instructs the reviewer not to invent article numbers or judgments.
- Missing information becomes a visible placeholder or checklist item. The generated document is always marked as an unapproved draft and requires a lawyer's final review.

## Input JSON

Create a JSON file with these fields:

- draft_type: defense_memo or statement_of_claim
- as_of_date: date for which legal status is to be checked (YYYY-MM-DD)
- case: optional object with court, case_number, claimant, respondent, drafted_for
- facts: list of lawyer-entered factual statements
- lawyer_arguments: list of arguments explicitly supplied/approved by the lawyer
- requests: list of requested remedies/relief supplied by the lawyer
- missing_information: list of unresolved facts/documents
- sources: list of source records with the fields shown below

Example source record (fictional, for tests only):

    {
      "title": "قانون افتراضي للاختبار",
      "citation": "المادة ١",
      "url": "https://example.org/law",
      "lawyer_approved": true,
      "legal_status": "in_force",
      "status_verified": true,
      "authenticity_verified": true,
      "permission_status": "allowed",
      "permission_evidence": "Reviewed permission record T-1",
      "url": "https://example.org/law",
      "effective_date": "2020-01-01",
      "reviewed_at": "2025-01-01",
      "repeal_date": null
    }

Do not copy the fictional example as a real authority.

## Run

    python tools/build_legal_draft.py intake.json --output draft.md

Or omit --output to print the draft to standard output.

## Current limitations and acceptance gates

- No UI, DOCX/PDF export, template library approval, saved draft history, or database integration.
- No OCR-to-fact extraction, document-to-fact evidence links, or access-control/tenant checks are added by this tool.
- No legal merits, jurisdiction, procedural deadlines, limitation periods, or citation correctness are independently determined.
- No real Egyptian legal sources or client data are included in tests.
- Before a paid pilot: Egyptian counsel should approve each template and its language; add fact-to-document provenance and audit history; validate all source metadata against underlying texts; add authenticated, tenant-scoped storage and exports; and run lawyer usability and regression evaluations.
