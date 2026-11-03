# Pilot firm onboarding and support playbook

**Status:** operating draft for the first three controlled Egyptian law-firm pilots. Owner names, support channels, service hours, response targets, pricing and customer evidence must be confirmed before external commitment. This playbook does not authorize production client-data use by itself; the production security, storage, privacy-counsel and legal-corpus gates remain separate.

## 1. Pilot principles

- Treat each law firm as a separate tenant. Never use one firm's data to demonstrate another firm's workflow.
- Use the clearly marked synthetic demo firm for demonstrations. Never enter real client or matter data into a demo tenant.
- Do not import client data until the firm's authorized owner confirms the source file, scope and authority to upload it.
- Keep external AI processing disabled until the exact provider/model/region/retention terms and firm approval are recorded.
- A successful sign-in is an authentication event, not evidence of a unique active user or product value.
- A generated answer is decision support, not a legal opinion or a substitute for lawyer verification.
- Record actual adoption, defects, support burden and willingness-to-pay evidence. Do not infer traction from invitations, sign-ins or demo activity.

## 2. Before onboarding

The pilot owner and firm owner complete a preflight call and record:
- contracting entity, firm name, authorized owner and escalation contacts;
- tenant ID and environment (synthetic demo, protected staging, or approved production);
- named firm administrator and initial users, role expectations and seat limit;
- practice areas and representative workflows to test;
- whether any client/matter data will be imported, the source file owner and approved import scope;
- document types, file sizes, original-file retention expectations and any legal holds;
- reminder preferences, approved recipient addresses and whether live SMTP is enabled;
- AI provider/model/region/retention terms and the exact data classes the firm authorizes for processing;
- support channel, service hours, severity contacts and incident escalation path;
- backup, export and restore evidence for the exact environment.

Do not proceed to real client data if the tenant, storage, external-AI, privacy or independent security release gates are unresolved.

## 3. Owner-led onboarding sequence

1. **Create and verify the firm.** Confirm the tenant name, owner identity, active status, plan/seat limit and firm-local data boundary.
2. **Complete first-run setup.** The owner completes the setup wizard, confirms firm profile and timezone, and records the actual start/end timestamps.
3. **Add users.** Invite only named firm users, verify their identities and assign the least-privilege firm role.
4. **Configure daily operations.** Set reminder preferences and hearing timezone; confirm who owns deadlines, tasks, document review and billing.
5. **Import existing matters.** When the matter CSV import feature is deployed, use its documented UTF-8 CSV template. Until then, use only the currently approved owner-led import path; never alter tenant databases manually. Review created/skipped counts, open sample matters and confirm client-profile linkage. Excel sheets must be exported as CSV UTF-8 until native XLSX upload is supported.
6. **Validate documents.** Upload only approved test documents first. Verify file type/size validation, extraction status, original-file integrity, access control and export behavior.
7. **Validate AI boundaries.** Demonstrate the three backend trust tiers only when AI-1's backend values are present. Confirm provider/model approval and firm-data approval separately; do not infer approval from a UI toggle.
8. **Run one real workflow.** With firm authorization, complete a representative client-to-matter workflow: search, assign a task, record a hearing/deadline, attach a document, review an answer and verify the activity history.
9. **Test export.** The owner performs a firm ZIP export, reviews the manifest and documented exclusions, and confirms that the archive is stored securely.
10. **Close onboarding.** Record elapsed time, incomplete steps, support interventions, defects and owner acceptance. A wizard completion event is not equivalent to successful independent onboarding.

## 4. First-week adoption review

Review with the firm owner after the first working week:
- unique weekly active users under the published qualifying-workflow definition, once that dashboard metric is deployed; otherwise record **not measured**;
- successful sign-in events separately;
- active users by firm role, without exposing another firm's identities;
- matters created/imported, task assignments/completions and hearing/deadline activity;
- document uploads, OCR/draft/research workflows and answer feedback;
- invoices issued, payments, outstanding balances and any expense workflow gaps;
- export test result, data integrity concerns and unresolved attachment exclusions;
- support requests, severity, time to acknowledge/resolve and recurring friction;
- whether users completed work without operator assistance.

Use aggregate counts for platform reporting. Do not put matter titles, client names, prompts, answer text or individual user IDs in a cross-firm pilot report.

## 5. Support handling

Assign named primary and backup contacts before onboarding. Use a restricted support channel and collect the minimum information needed to diagnose an issue.

| Priority | Examples | Initial handling |
|---|---|---|
| P0 critical | Suspected cross-firm exposure, privileged account compromise, confirmed bulk disclosure, storage-key compromise | Activate the incident runbook immediately; contain the affected boundary; preserve evidence; involve the affected firm and qualified counsel |
| P1 high | Firm-wide login failure, inaccessible matter documents, export failure near a client deadline, data integrity concern | Acknowledge promptly during agreed support hours; assign an engineer; keep the firm updated; do not bypass access controls |
| P2 normal | Import validation issue, reminder preference problem, noncritical workflow defect | Record reproducible steps with synthetic/redacted data; provide workaround only if safe; track to resolution |
| P3 request | UI improvement, report field, training question | Log the request, clarify business value and include it in the pilot review |

Proposed response targets must be approved by the product owner and reflected in customer terms before being promised. Support must never ask a firm to send passwords, session cookies, full client files or confidential prompts through ordinary email or chat.

For any suspected security or privacy incident, stop normal support handling and follow the approved pilot incident response runbook. Do not independently decide legal notification duties or deadlines.

## 6. Weekly pilot scoreboard

Populate this table only from measured evidence. Keep firm names/identities in a restricted customer-success record; use pseudonymous firm labels in platform-wide reports.

| Measure | Firm A | Firm B | Firm C | Evidence |
|---|---:|---:|---:|---|
| Onboarding elapsed minutes | — | — | — | Wizard timestamps and support interventions |
| Weekly active users | — | — | — | Platform aggregate under documented WAU definition; mark not measured until deployed |
| Successful sign-in events | — | — | — | Authentication event count, separate from WAU |
| Active matters | — | — | — | Firm-local case report |
| Matters imported | — | — | — | Import result |
| Documents uploaded | — | — | — | Firm-local usage and document records |
| Research/draft workflows | — | — | — | Usage ledger aggregate |
| Export test | — | — | — | Export audit event and owner confirmation |
| Support requests / P0-P1 | — | — | — | Restricted support register |
| Owner-rated workflow value | — | — | — | Recorded interview, date and question set |
| Paid pilot / prepayment evidence | — | — | — | Signed order, invoice/payment evidence or explicit written offer response |

A dash means **not measured**, not zero. Do not enter forecast, target or synthetic-demo values as customer outcomes.

## 7. Willingness-to-pay evidence

For each firm, record:
- the exact plan and monthly/annual price presented;
- included seats, matter/document limits, support scope and AI usage assumptions;
- whether the decision-maker has budget authority;
- the firm's stated price range and objections;
- whether the firm accepted a written offer, requested changes, declined or deferred;
- any paid invoice, signed order or cleared prepayment with date and amount.

A positive interview response is not revenue. A verbal statement of interest is not a prepayment. Count a firm toward the prepayment target only when a real, attributable payment or binding purchase commitment is evidenced and reconciled.

## 8. Exit and renewal review

Before renewal or offboarding, the owner confirms subscription state, access restrictions, export availability, outstanding invoices, legal holds, retention/deletion decisions and any open support/security issues. Subscription expiry must not be treated as permission to delete tenant data. Use the approved firm offboarding and original-file deletion workflows; never use demo removal for a real firm.
