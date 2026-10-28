# Approved product and security defaults

**Status:** Product owner approved the recommended defaults on 2026-10-27. These are implementation defaults, not a production-readiness certification. A deployment-specific legal/privacy review is still required before processing real confidential client material.

## Product model

- Build for a centrally operated, multi-firm legal platform, with hard firm boundaries and the ability to adapt storage/deployment interfaces later.
- No public self-registration or production onboarding of unrelated firms until the release gates in the database tracker are closed.
- Treat the control plane, each firm's matter database, the shared legal corpus, original-file storage, and external AI services as distinct security domains.

## Approved defaults

### Original legal files

- Use a private S3-compatible object-storage interface, with a local development adapter. Keep the production provider configurable rather than hard-coding a vendor.
- Original files remain private firm data, never part of the shared legal corpus. Use opaque object identifiers, server-side authorization, tenant-bound metadata, upload/download size limits, content validation, and no public object URLs.
- Require staged upload and metadata commits with integrity hashes, safe failure cleanup, and backup/restore verification.

### Encryption and key management

- Use a configurable key-management interface and prefer a managed KMS in production, with firm-scoped keys where supported and justified by the selected platform.
- Keep secrets and key material outside the database and source repository. Do not claim per-firm cryptographic isolation until the chosen backend and key policy actually enforce it.
- Test key rotation, access revocation, backup encryption, and recovery before production use.

### Retention, deletion, and legal hold

- Initial default: no automatic permanent deletion. Use explicit, authorized, audited deletion workflows.
- Implement legal holds that block deletion while active. Hold placement/release must be authorized and audited.
- Do not invent a universal retention period. Before production, each deployment must define retention by document/case class, applicable legal duties, deletion semantics across originals/derivatives/backups, and hold release behavior.

### Email, invitations, and account recovery

- Use a configurable SMTP-compatible delivery interface. Provider credentials are deployment secrets, never committed to source.
- Invitation and recovery tokens must be cryptographically unpredictable, single-use, expiring, purpose-bound, and stored safely (prefer hashes); consume tokens atomically with the resulting state change and audit event.
- Ordinary accounts may use verified-email recovery only after delivery and account ownership checks are implemented. Privileged/platform accounts require stronger assisted verification; recovery must never grant roles or reactivate suspended membership.
- Rate-limit and audit invitation/recovery attempts without logging secrets or token values.

### Platform bootstrap and roles

- Use a one-time operator CLI/bootstrap procedure for the first platform administrator. It must refuse overwrites, require a secure operator context, and emit an audit event without exposing credentials.
- Firm administrators manage membership within their own firm. Platform administrators manage platform-level roles and platform operations; platform privileges do not automatically grant routine access to firm matter content.
- Platform role grants/revocations remain separately authorized and audited, with last-admin protections.

### AI and firm data

- **No cross-firm training or fine-tuning on customer data by default.** One firm's documents, prompts, conversations, identifiers, or outputs must not train or improve a model shared with other firms.
- Firm content may be used only as authorized context for that firm's requested inference/retrieval, with firm and case authorization checked before retrieval and before transmission.
- Keep both LLM_DATA_PROCESSING_APPROVED and LLM_FIRM_DATA_PROCESSING_APPROVED unset until the exact endpoint/provider/model, region, contractual training restrictions, retention, subprocessors, incident terms, legal basis, and firm/client authorization are reviewed and recorded.
- If provider processing terms cannot be verified, do not transmit confidential matter content; remain in sources-only mode or use a genuinely controlled local endpoint that has itself been reviewed. An OpenAI-compatible API is not evidence that a service is local.
- Any future use of real customer data for cross-firm training or evaluation requires separate explicit opt-in, legal/privacy review, minimization/de-identification controls, auditability, and an effective withdrawal/deletion process. Public legal materials and synthetic test fixtures are preferred for general improvements.

### Recovery and release validation

- Begin with isolated local restore/rollback rehearsal, then perform a witnessed staging drill before production.
- Verify the restored control plane, firm databases, legal corpus, original files, key access, revoked memberships, and firm isolation together.
- Keep the overall project marked not production-ready until exhaustive route/query review, storage and lifecycle implementation, operational monitoring, witnessed restore/rollback, and independent security/privacy review are complete.

## Explicitly not decided yet

- Specific object-storage vendor, cloud/KMS vendor, email provider, and AI provider/model/region.
- Legal retention periods, jurisdiction-specific policy, and any customer opt-in for future model-training/evaluation use.
- Production hosting environment and staging infrastructure.

These are configuration/legal-review choices, not permission to weaken the approved defaults. Until provider and deployment details are selected, fail closed and do not send confidential firm data to unreviewed services.
