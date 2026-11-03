# Pilot security incident response runbook

**Status:** operational draft; deployment-specific contacts, notification decisions and witnessed exercise remain mandatory before production use.

This runbook is an operational procedure, not a legal opinion. It does not determine whether an event is a personal-data breach, establish a notification deadline, or interpret Egyptian Law No. 151/2020. The affected firm and qualified Egyptian privacy counsel must assess applicable duties and client communications.

## 1. Activation and roles

Activate this procedure for suspected or confirmed:
- cross-firm access or disclosure;
- compromised administrator, platform operator, signing key, or service credential;
- unauthorized access to case documents, attachments, exports, backups, or audit data;
- unauthorized external AI processing or provider retention;
- destructive data loss, ransomware, storage integrity failure, or backup compromise;
- sustained service abuse that threatens confidentiality, integrity, or availability.

Assign and record:
- **Incident commander:** owns severity, timeline, decisions and closure.
- **Security/technical lead:** contains the issue, preserves evidence and coordinates recovery.
- **Affected-firm liaison:** communicates with the firm's authorized owner; never shares another firm's information.
- **Privacy/legal counsel:** assesses legal, contractual, professional-secrecy and notification questions.
- **Provider liaison:** contacts hosting, storage, identity, email or AI providers where relevant.

Before production, populate a restricted contact sheet with named primary/backup people, secure contact channels, provider escalation details and decision authority. Do not put credentials or personal client data in this runbook.

## 2. Severity and immediate response

| Severity | Examples | Initial handling |
|---|---|---|
| SEV-1 critical | Confirmed cross-firm disclosure, privileged/admin compromise, confirmed bulk exfiltration, signing/encryption key compromise | Page incident commander and security lead immediately; suspend affected access path; preserve evidence; block risky processing |
| SEV-2 high | Suspected account takeover, unauthorized single-firm access, suspicious export/download, object integrity anomaly | Revoke affected identity/session, contain the affected route or firm, investigate scope |
| SEV-3 moderate | Repeated abuse/rate-limit events, isolated service degradation, failed backup with a known good recovery point | Apply rate/availability controls, verify data integrity and recovery state |
| SEV-4 low | Non-sensitive defect with no evidence of unauthorized access or data loss | Record, triage and track through normal incident/defect process |

Severity is provisional. Escalate when new evidence changes the impact.

## 3. First 15 minutes

1. Open a restricted incident record with an opaque incident ID, UTC start time, reporter, suspected systems/firm scope and initial severity.
2. Name the incident commander and technical lead. Start a timestamped decision/action log.
3. Preserve existing security, authentication, application, deployment, provider and storage logs before changing retention or configuration.
4. Do not copy case content, credentials, tokens, prompts, attachments or personal data into tickets, chat, screenshots or general-purpose logs.
5. Contain the smallest safe boundary. Prefer revoking the affected identity/session or disabling the affected route/tenant over taking unrelated firms offline.
6. If exposure may continue, suspend the relevant capability: uploads/downloads, exports, invitations, AI processing, or affected tenant access. Record exactly what was disabled and by whom.
7. Do not delete databases, objects, backups, audit events or user accounts as an investigative shortcut.

## 4. Containment playbooks

### Account or administrator compromise
- Disable the affected identity and revoke active sessions using the supported account lifecycle controls.
- Rotate affected passwords, API credentials, deployment secrets and provider tokens through the secret manager.
- Review recent platform and firm audit events, role grants, invitation activity, export/download events and authentication throttles.
- Verify that platform privileges are separate from firm roles; review any platform-role grant/revocation events.
- Restore access only after identity verification and an approved recovery path.

### Suspected cross-firm access
- Treat as SEV-1 until disproved.
- Preserve the request IDs, timestamps, actor/firm IDs and sanitized route evidence.
- Disable the affected route or tenant access if continued disclosure is plausible.
- Verify the trusted membership resolution and per-firm database binding. Do not use client-supplied firm IDs or paths as evidence of authorization.
- Test the exact affected resource against two synthetic firms after the fix. Do not probe unrelated live client matters without authority.
- Require independent review before reopening the affected boundary.

### External AI processing
- Unset the deployment approval flags for the affected endpoint/data class, including both general and firm-data processing attestations where relevant.
- Stop new requests to the endpoint and revoke/rotate the provider credential if compromise is suspected.
- Preserve exact endpoint/model/version, region, request times and sanitized request identifiers; do not copy prompt or matter content into the incident record.
- Contact the provider through the contracted security channel to establish access, retention, deletion/hold and subprocessor facts.
- The affected firm and qualified counsel decide client communication and any legal/contractual action.

### Original-file storage or export incident
- Suspend affected upload, download, export or purge capability.
- Preserve object metadata, checksums, ETags/version identifiers, KMS key identity, legal-hold state, audit records and storage-provider evidence.
- Do not run physical purge or lifecycle cleanup while scope, legal holds or evidence preservation are unresolved.
- Reconcile tenant metadata with object storage using the approved read-only reconciliation tools.
- Restore only to a new isolated target; never overwrite the source as an investigative step.

### Data corruption, deletion or ransomware
- Stop application and background writers before taking a coordinated backup snapshot.
- Preserve the original database files and the last known-good encrypted bundle.
- Verify backup integrity and keys before restore. Restore to a new target directory.
- Run startup, tenant-isolation, integrity and application smoke tests against the restored copy.
- Record recovery point, restore duration, known loss and data-owner acceptance. A code-level restore test is not a witnessed production recovery drill.

## 5. Evidence handling

- Keep evidence in a restricted, access-logged location with least-privilege access.
- Record collector, UTC collection time, source system, method, file size and SHA-256 digest.
- Preserve original evidence read-only; perform analysis on copies.
- Keep a chain-of-custody log for exported logs, storage metadata, backup manifests and provider responses.
- Sanitize evidence before attaching it to repository issues or pull requests. Never publish credentials, session material, client identities, matter text or confidential legal content.
- Record any evidence that could not be obtained and why. Absence of evidence is not proof that no access occurred.

## 6. Scope and notification assessment

The incident commander and affected-firm liaison prepare a factual impact record:
- affected firm(s), identities, systems, resources and time window;
- data categories potentially accessed, changed, disclosed or lost;
- whether matter content, attachments, prompts, exports or backups were involved;
- known and unknown recipients, provider/subprocessor involvement and evidence confidence;
- containment completed, remaining exposure and recovery state.

The affected firm and qualified Egyptian privacy counsel must decide whether client, regulator, insurer, professional body, law-enforcement or provider notification is required, by whom and when. Do not infer legal duties or deadlines from this runbook. Record the decision-maker, rationale, approval and communication evidence in the restricted incident record.

## 7. Recovery and closure

Do not restore normal service until:
- the root cause is understood sufficiently to prevent immediate recurrence;
- affected credentials, sessions and access grants are revoked or rotated;
- the relevant tenant, storage, export and AI-processing boundaries pass targeted tests;
- data integrity and backup/restore state are verified;
- the affected firm receives an approved factual status update;
- the incident commander and independent reviewer approve reopening for SEV-1/SEV-2.

Close with a timeline, impact assessment, evidence manifest, root cause, corrective actions, owners and due dates. Track corrective actions to verified completion; do not close because service has merely restarted.

## 8. Exercise and review

Before production, run a tabletop covering at least: administrator compromise, cross-firm access, accidental external AI processing, original-file deletion anomaly, and failed restore. Record participants, injects, decisions, response times, gaps and corrective actions. Repeat after material architecture/provider changes and at the cadence approved by the security owner.
