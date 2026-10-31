# LLM data-processing policy and release gate

**Status:** technical fail-closed gate implemented in this change; provider, legal, privacy, and deployment approval are not completed.

## What the application currently does

The research pipeline can send a prompt to the configured OpenAI-compatible chat-completions endpoint. That prompt includes the current question, selected retrieved passages, their provenance metadata, and (when present) earlier user-question context. Depending on the selected research scope, passages may contain confidential matter information. The application does not train or fine-tune the configured model from uploaded documents, but that does **not** mean the provider cannot process, retain, or log prompts.

The model integration is generic. It does not bundle a model or choose a vendor. Configuration is supplied through:

- `LLM_URL`: full endpoint URL, including the chat-completions path.
- `LLM_MODEL`: model name sent to that endpoint (defaults to `local`).
- `LLM_KEY`: bearer credential, if the endpoint requires one.
- `LLM_DATA_PROCESSING_APPROVED`: must equal `1` before any prompt is transmitted.
- `LLM_FIRM_DATA_PROCESSING_APPROVED`: must equal `1` before any retrieved firm/matter document passage can be sent in a prompt. This separate gate applies even when general LLM processing is approved.

If `LLM_URL` is unset, or the general approval flag is absent or has any value other than `1`, the model call is skipped and the app remains in sources-only mode. If retrieved passages include matter-file content, the separate firm-data approval must also equal `1`; otherwise the app returns the retrieved sources without a generated answer. This gate is intentionally fail-closed and does not itself establish consent, provider compliance, tenant isolation, or legal privilege protection.

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


## Separate gate for matter-file content

The separate firm-data gate applies when the caller explicitly associates a research request with a case, when prior user-question context is included in a follow-up, or when retrieval returns matter-file passages. Conversation history can itself contain confidential facts, even when the latest retrieval returns only public-law passages. Without the flag, the application returns sources only.

The general model-processing switch does not automatically authorize sending client/matter file passages to an endpoint. The research path now checks whether any retrieved hit belongs to a case. If so, it requires `LLM_FIRM_DATA_PROCESSING_APPROVED=1` before calling the model. Without it, the answer is withheld and the sources-only result is returned. The switch is a deployment-level attestation, not per-client consent or automated redaction. Keep it unset unless the provider, data classes, client/firm permissions, retention, access, region, and contractual terms have been specifically reviewed. This does not make confidential case-file research production-safe; tenant isolation and an independent security review remain required.

## Approved default privacy posture

The product-owner's approved default is **no cross-firm training or fine-tuning on customer data**. Matter documents, extracted text, prompts, conversations, client identifiers, and firm-specific outputs must not be used to train, fine-tune, or improve a model shared with other firms. They must not be exposed across firms through retrieval, memory, caches, logs, evaluation datasets, or provider-side reuse.

The application itself does not train or fine-tune its configured model from uploaded documents. Model inference may still require transmitting the question and selected context to the configured endpoint. Before enabling any endpoint, verify the actual provider/model, processing region, retention/deletion behavior, subprocessors, incident terms, and contractual prohibition on provider training/use for model improvement. If these conditions cannot be verified, keep model calls disabled or use a genuinely controlled local/self-hosted endpoint that has been reviewed. Do not infer that an OpenAI-compatible API is local or privacy-preserving from its URL format alone.

Using firm data for a firm-specific feature such as authorized retrieval, search, or explicitly scoped matter context is not model training. Any future proposal to use real customer data for cross-firm training or evaluation requires a separate opt-in decision, documented lawful basis and client/firm authorization where required, minimization/de-identification review, provider/contract review, and an auditable opt-out/deletion process. It is not permitted by default. Public legal materials and synthetic test fixtures may be used subject to source rights and review.


## AI case-brief minimization

The case-brief workflow omits the case title, client name, opposing-party name, and case number from its model context. It also omits task-assignee names, activity actor names, and document filenames. Common email-address, Egyptian national-ID, mobile-phone, and landline patterns are redacted from the remaining serialized records before prompt construction.

These measures are **not complete anonymization**. Names, addresses, rare facts, privileged strategy, and other identifiers may remain in free-text notes or extracted document passages. The feature must not be used with a hosted or otherwise uncontrolled endpoint unless the exact provider, model, region, retention, access, and contractual terms have been reviewed and approved. Keep both LLM approval attestations unset otherwise. Users must review matter text and follow the firm's client-authorization and minimization policy before generating a brief. The pattern redactor is a supplementary safeguard, not a substitute for legal/privacy review or a guarantee that sensitive content is removed.


## AI case-brief authorization attestations

The AI case-brief endpoint requires both an explicit firm-authorization attestation and an explicit client-authorization/lawful-basis attestation in the authenticated request body before it calls the configured model. The case access check and the deployment-level `LLM_FIRM_DATA_PROCESSING_APPROVED=1` gate remain separate prerequisites. The deployment flag is not a per-firm or per-client consent record. The UI requires the user to affirm both statements, the server independently rejects missing or false attestations, and the case activity log records that the user made the attestations.

These attestations are user assertions, not independent proof that a valid authorization or lawful basis exists. They do not replace the firm's engagement terms, client instructions, privacy notice, data-processing agreement, privilege review, or provider assessment. The feature must remain unavailable unless the user has documented authorization for the specific matter and the deployment operator has separately approved the exact endpoint and data class. Do not treat a checkbox or audit event as the underlying consent evidence.
