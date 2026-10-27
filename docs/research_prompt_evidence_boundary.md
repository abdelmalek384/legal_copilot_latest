# Research prompt evidence boundary

Retrieved legal passages, citation labels, and provenance metadata are untrusted input. The research prompt serializes each source as a separate JSON record with explicit fields: citation_index, reference, recorded_provenance, and passage_text. This avoids placing passage text into instruction-like prose.

The prompt instructs the model to use those records only as evidence and to ignore any embedded commands, role changes, requests to reveal information, or output instructions. This reduces ambiguity and keeps passage newlines inside the JSON string representation.

## Important limitations

- Prompt formatting is not a complete prompt-injection defense. A model can still follow malicious text in retrieved content.
- Never include another firm's data in the retrieval set; tenant authorization must be enforced before prompt construction.
- Keep firm-document model processing disabled unless the deployment operator has explicitly approved the exact model endpoint and data-processing terms.
- Continue to validate citations, legal quantities, and uncited claims after generation. If validation fails, show sources only.
- Do not treat provenance metadata or a model-generated answer as proof that a legal source is authentic, current, or legally reusable.
- Before production, evaluate adversarial Arabic and English passages against the actual configured local model and record results.

The regression tests verify prompt serialization and that the existing fail-closed answer validation remains active. They do not certify immunity to prompt injection.
