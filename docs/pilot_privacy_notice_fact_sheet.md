# Pilot privacy notice and data-processing fact sheet

**Status:** internal fact-gathering worksheet only. This is not a customer privacy notice, data-processing agreement, legal opinion or determination of compliance. Do not publish or rely on it until product facts are confirmed and qualified Egyptian privacy counsel reviews and approves the final documents.

## 1. Product and controller/processor facts to confirm

| Required fact | Current evidence / owner action |
|---|---|
| Contracting entity and legal identity | **BLOCKED:** product owner must supply registered legal name, address and contact |
| Role of the law firm and Legal Copilot operator for each processing purpose | **COUNSEL REVIEW:** do not assume controller/processor roles without contract and actual-purpose analysis |
| Hosting provider, region, infrastructure locations and support access | **BLOCKED:** deployment owner must provide live production configuration and provider contract |
| Storage provider, bucket, region, KMS key ownership and backup locations | **BLOCKED:** live S3/KMS/IAM validation is not complete |
| Identity, email, monitoring, support and analytics subprocessors | **BLOCKED:** produce a verified subprocessor inventory; do not infer from optional code paths |
| External AI provider, endpoint, model/version, region, retention and subprocessors | **PER-DEPLOYMENT:** exact endpoint must be documented; approval flags are operator attestations, not proof of provider compliance |
| Data retention, legal holds, backup expiry and deletion schedule | **COUNSEL/OWNER DECISION:** the current retention document is a proposal, not an approved schedule |
| Security contact, privacy contact and request channel | **BLOCKED:** named, monitored contacts and response ownership must be supplied |
| Effective date, version and change-notice process | **BLOCKED:** set after counsel approval |

## 2. Data inventory to reconcile against deployed behavior

The product may process the following categories depending on features enabled and information entered by a firm:
- firm identity, contact, membership, user account, authentication and security-event data;
- client identity/contact information and matter metadata;
- case notes, tasks, deadlines, hearing/session details, fees, invoices and payment records;
- uploaded files, extracted text, document metadata, checksums, previews and export packages;
- research questions, conversation history, retrieved passages, generated answers and user feedback;
- AI authorization attestations and external-processing request metadata;
- reminder preferences, delivery metadata and notification destinations;
- billing, subscription, seat, usage and support records;
- backup, recovery, audit and security evidence.

Confirm each category against the actual production deployment, enabled features, logs and connected providers. Do not claim that a category is never processed merely because it is optional or disabled in one environment.

## 3. Purpose and disclosure matrix

For each data category, counsel and the product owner must approve:
- specific purpose and whether it is necessary for the service;
- source of the data and which party supplies it;
- recipients, subprocessors and support-access conditions;
- whether the data is sent outside the firm's tenant or outside Egypt;
- retention period, legal-hold exception, backup expiry and deletion trigger;
- access, correction, export, restriction or deletion request handling;
- security controls and incident escalation path.

The AI-processing policy already requires review of the exact provider/model, hosting region, retention, training use, abuse monitoring, subprocessors and contractual terms. Keep the relevant approval flags unset until the deployment owner has recorded the exact approval. A user checkbox or deployment flag is not a substitute for underlying firm/client authorization.

## 4. Rights-request workflow to implement and evidence

Before offering a customer-facing request channel, assign an owner and define:
1. identity and authority verification for the requester;
2. whether the request concerns a law-firm client, a firm user, or the firm itself;
3. firm-owner notification and approval where the firm controls the matter relationship;
4. search scope across tenant databases, object storage, exports, backups, logs and connected processors;
5. legal-hold, privilege, confidentiality and third-party restrictions requiring counsel review;
6. secure response delivery, export manifest, approval record and expiry of temporary copies;
7. deletion eligibility, second-person approval, tombstone/audit evidence, provider purge and backup expiry;
8. refusal, partial fulfilment, escalation and response-time ownership.

The existing firm export is an owner-controlled firm export, not a complete client-facing personal-data access package. Do not present it as automatic fulfilment of an individual's statutory request. The current retention proposal is not an approved deletion schedule.

## 5. Approval gates

- [ ] Product owner confirms the contracting entity, customer terms, support contacts and product purposes.
- [ ] Deployment owner supplies verified hosting, storage, backup, region and subprocessor facts.
- [ ] Security owner supplies access-control, encryption, incident and recovery evidence.
- [ ] Firm pilot owners confirm their actual workflows, client instructions and external AI preferences.
- [ ] Qualified Egyptian privacy counsel reviews the data inventory, role allocation, notice, processor terms, cross-border processing, retention, rights and incident-notification decisions.
- [ ] Native Arabic legal/editorial review is completed for the Arabic customer-facing notice.
- [ ] Approved notice and data-processing documents are versioned, published, linked at onboarding and retained with the applicable customer acceptance evidence.

Until all gates are complete, keep the customer-facing privacy notice and data-processing approval status explicitly pending. Do not claim compliance with Law No. 151/2020 or any other privacy regime based on this worksheet.
