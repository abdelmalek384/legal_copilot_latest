# LLM data-processing policy and release gate

**Status:** technical fail-closed gate implemented in this change; provider, legal, privacy, and deployment approval are not completed.

## What the application currently does

The research pipeline can send a prompt to the configured OpenAI-compatible chat-completions endpoint. That prompt includes the current question, selected retrieved passages, their provenance metadata, and (when present) earlier user-question context. Depending on the selected research scope, passages may contain confidential matter information. The application does not train or fine-tune the configured model from uploaded documents, but that does **not** mean the provider cannot process, retain, or log prompts.

The model integration is generic. It does not bundle a model or choose a vendor. Configuration is supplied through:

- `LLM_URL`: full endpoint URL, including the chat-completions path.
- `LLM_MODEL`: model name sent to that endpoint (defaults to `local`).
- `LLM_KEY`: bearer credential, if the endpoint requires one.
- `LLM_DATA_PROCESSING_APPROVED`: must equal `1` before any prompt is transmitted.

If `LLM_URL` is unset, or the approval flag is absent or has any value other than `1`, the model call is skipped and the app remains in sources-only mode. The UI/API may still show retrieved sources without a generated answer.

## Before setting the approval flag

The operator and appropriate legal/privacy decision-maker must record:

1. Exact provider, endpoint, model/version, hosting region, and whether the endpoint is genuinely local or sends traffic to a third party.
2. Applicable contract/terms covering prompt use for training, retention, abuse monitoring, subprocessors, data residency, deletion, and incident notification.
3. Whether confidential client data may be processed under the firm's engagement terms, applicable professional duties, client instructions/consent where required, and relevant law.
4. Data minimization: avoid sending names, national IDs, contact details, privileged strategy, or unrelated matter text when not needed; define redaction and access/logging rules.
5. Network egress controls, secret management, timeout/error behavior, and tests confirming no request is made while the flag is unset.
6. Who approves the setting, evidence/date of approval, scope of permitted data, review cadence, and how approval is withdrawn.

A self-hosted endpoint is not automatically safe: verify where inference runs, whether prompts are logged, who can administer it, and whether outbound telemetry or hosted dependencies exist.

## Limits of the gate

`LLM_DATA_PROCESSING_APPROVED=1` is a deployment-level operator attestation. It does not verify a provider's identity, contract, location, retention behavior, consent, redaction, or network route. It is not per-firm consent and does not provide data-loss prevention. Anyone who can change deployment environment variables may change the policy. Keep the flag unset until the review above is complete.

This gate is a minimum safeguard, not a production-readiness certification. Shared SQLite tenant isolation, legal-corpus verification, independent security/privacy review, and the remaining release checklist are separate blockers.
