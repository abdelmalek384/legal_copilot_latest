# SEC-01 — tenant-isolation inventory and audit findings

**Review date:** 2026-10-26  
**Scope:** static review of `app.py`, current API regression tests, schema/table definitions, and the existing multi-firm isolation plan. This is an engineering inventory, not an independent penetration test or production certification.

## Executive finding

The application now has a separate-database runtime when all three paths (`COPILOT_CONTROL_DB`, `COPILOT_TENANT_DB_ROOT`, and `COPILOT_CORPUS_DB`) are configured: identities and memberships live in the control plane, each firm's matters live in a distinct SQLite file, and legal-reference data lives in a shared corpus database. Explicit legacy `COPILOT_DB` compatibility remains, but it is not an approved isolation boundary for unrelated firms' confidential matters. Route/query isolation still needs exhaustive review in the separate runtime.

**Do not onboard unrelated firms or production confidential client material yet.** Exhaustive route/query review, first-deployment operational controls, restore/rollback drills, retention and monitoring policies, and independent security review remain release blockers.

## Current automated coverage

The API suite uses synthetic records and two firms. The separate-runtime integration suite now also verifies that a guessed case ID cannot be read, modified, or deleted after switching to another firm, and that a clean separate-database install preserves firm data, corpus data, and lifecycle metadata across restart. Existing assertions include:
- case list/detail/update/delete and membership/task boundaries;
- dashboard tasks/deadlines and conflict checks;
- user listing/creation/disablement and session revocation;
- document upload, document-to-case linkage, and extraction review history/correction;
- case-scoped search and answer requests;
- research conversation list/detail/rename/delete/message and matter export;
- admin-only case deletion and security audit endpoints;
- legal-review queue/coverage/event authorization and legacy law-import gates.

Merged PR #439 verifies Firm B cannot see Firm A's security events or case-deletion snapshots. Merged PR #465 adds database-level row-scope guards and separate-runtime cross-firm case CRUD plus fresh-install/restart tests. PR #543 behaviorally verifies that wrong-firm UPDATEs abort for cases, documents, extraction reviews, research conversations, and case-deletion audit rows; PR #530 covers wrong-firm INSERT rejection for those tables. The test suite's synthetic setup is not a substitute for a deployment-specific review.

## Route inventory

Routes are grouped by the data boundary they should preserve. "Tested" means there are relevant assertions in `api_test.py`; it does not mean every branch, role, and failure mode has been exhaustively tested.

| Route(s) | Boundary / expected authorization | Current coverage and remaining concern |
|---|---|---|
| `GET /` | Public shell only; no matter content | Security headers/CSP are asserted; browser/manual QA remains |
| `POST /login`, `GET /session`, `POST /logout`, `POST /account/password` | Auth/session belongs to one user; disabled, expired, or revoked sessions must stop working | API tests cover malformed credentials, CSRF, expiry, password change/reset revocation and concurrent login; production browser/cookie policy still needs review |
| `GET /users`, `POST /users`, `POST /users/{uid}/disable` | User records scoped to authenticated firm; administration is role-gated | Cross-firm listing and admin/disable tests exist; review uniqueness and account lifecycle in production |
| `GET /dashboard`, `GET /cases`, `POST /cases`, `GET /cases/{cid}`, `PATCH /cases/{cid}`, `DELETE /cases/{cid}` | Case must belong to same firm; non-admin access must respect case membership | Cross-firm list/detail/update/delete and dashboard tests exist; route/query audit should be repeated after every new endpoint |
| `POST /cases/{cid}/members`, `DELETE /cases/{cid}/members/{uid}` | Both case and target user must be in the same firm; only authorized case lead/admin may manage membership | Role/membership tests exist; add further guessed-ID permutations as the route changes |
| `POST /cases/{cid}/tasks`, `POST /tasks/{tid}/done`, `POST /cases/{cid}/sessions`, `POST /cases/{cid}/notes`, `POST /cases/{cid}/deadlines`, `POST /deadlines/{did}/done`, `POST /cases/{cid}/fees` | Parent case and referenced user/task/deadline must be firm- and membership-scoped | Several role and guessed-ID tests exist; coverage is not exhaustive for every child table and mutation |
| `POST /cases/{cid}/docs`, `POST /cases/{cid}/upload` | Parent case must be authorized; metadata, chunks, and indexes must retain firm/case linkage | Upload ownership, hashes, metadata, and cross-firm upload denial are tested. Original binaries are not retained; retention/page preview is not implemented |
| `GET /cases/{cid}/docs/{document_id}/reviews`, `POST /cases/{cid}/docs/{document_id}/chunks/{chunk_id}/review` | Case, document, chunk, and review history must all resolve inside same authorized firm/case | Cross-firm review read/write and stale correction protections are tested; reviewer UI and page-level source verification remain outstanding |
| `POST /conflicts` | Search only within current firm's cases; hidden same-firm cases may yield a generic warning, not details | Tests cover firm boundary and warning behavior; requires lawyer workflow validation |
| `POST /search`, `POST /ask` | Matter-scoped context must pass case authorization; global statutory corpus is a separate read-only shared scope | Cross-firm case-scoped requests and unscoped retrieval that excludes another firm's private-document sentinel are tested (PR #542); continue auditing new retrieval paths and caches |
| `POST /research/discover` | Must not expose unauthorized matter content or persist cross-tenant context | Scope/permission denial tests exist; test every supported scope and future connector |
| `GET /research/conversations`, `POST /research/conversations`, `GET/PATCH/DELETE /research/conversations/{conversation_id}`, `POST /research/conversations/{conversation_id}/messages`, `POST /research/conversations/{conversation_id}/save-to-matter` | Conversation belongs to user and firm; target matter and message must be authorized | Cross-user and cross-firm read/write/export tests exist |
| `GET /audit/case-deletions`, `GET /audit/security-events` | Admin-only, firm-filtered audit data; snapshots must not cross firm boundary | Existing role/limit tests; this PR adds Firm B no-leak assertions |
| `POST /law/import` | Shared law content is global; import requires admin role plus protected import token; caller flags cannot mark law verified/current | Tests cover missing token, non-admin denial, and forced unverified/ineligible import. Reconsider whether any firm admin should be able to import global law even with token |
| `GET /legal-review/queue`, `GET /legal-review/coverage`, `GET/POST /legal-review/versions/{version_id}/events` | Shared legal registry is global, but review mutations should be restricted to explicitly trusted platform reviewers | These endpoints now require an admin identity whose normalized email is explicitly allowlisted by `LEGAL_REVIEWER_EMAILS`; a firm-admin role alone is insufficient. Configure this allowlist only through trusted deployment configuration, test cross-firm admin denial, and keep global review access disabled when the allowlist is empty. |
| No background worker/scheduled-job route identified in the current `app.py` | Any future OCR, indexing, cleanup, export, backup, and restore job must preserve tenant scope from trusted job metadata | No separate worker implementation was identified in the reviewed application file; re-inventory if one is added |

## Data-table and storage inventory

| Table / resource | Classification | Required isolation rule / gap |
|---|---|---|
| `firms` | Control-plane-like metadata in shared DB | Firm status/identity must be trusted server-side; this is not yet a separate control-plane database |
| `users`, `auth_sessions`, `login_attempts`, `api_rate_limit_windows` | Identity/session/security state | User/session ownership and rate limits must not be client-selectable; review session/token storage and firm lifecycle |
| `cases`, `members`, `tasks`, `events`, `notes`, `deadlines`, `fees`, `sessions` | Firm matter data | Every access path must join to an authorized firm/case; child IDs alone are never authorization |
| `docs`, `document_extraction_reviews` | Firm document metadata and review audit | Enforce case + firm ownership through every read/write; raw uploaded binaries are not retained currently |
| `chunks` | Mixed: global legal passages and firm-linked document chunks | Every firm-document chunk must remain linked to its document/case; shared legal chunks must be clearly distinguished from matter chunks |
| `case_deletion_audit`, `security_audit_events` | Sensitive firm audit data | Firm-filter reads and writes; redact confidential content and ensure retention/deletion policy |
| `research_conversations`, `research_messages` | User/firm private research | Conversation owner and firm scope must be checked for parent and child operations |
| `legal_sources`, `legal_documents`, `legal_document_versions`, `legal_version_relations`, `legal_review_events` | Shared global legal registry | Shared read-only legal data may be global; changes/review outcomes need platform-level authority, immutable audit evidence, and source rights gates |

## Release blockers

1. **Shared database:** target tenant database/storage isolation architecture is not implemented.
2. **Global reviewer privilege:** API access now requires the deployment-configured `LEGAL_REVIEWER_EMAILS` allowlist in addition to the admin role. Production must configure and protect this allowlist; it is not a full independent identity provider or approval workflow.
3. **Incomplete inventory:** static route/table inventory is now recorded, but SQL query-by-query, UI, export, deployment, and operational path review still needs a second pass.
4. **Backups and restore:** no cross-tenant backup/restore isolation test or restore drill has been demonstrated.
5. **File retention:** original upload binaries and secure page previews are not available, so extraction corrections cannot be independently compared to retained original pages.
6. **Independent review:** no independent security assessment is recorded.
7. **Production hardening:** verify HTTPS/cookie flags, CSRF policy, secret handling, rate limits, structured security logging, encrypted backups, retention/deletion, incident response, and rollback in the deployment environment.

## Recommended next sequence

1. Keep the new audit endpoint regression tests in CI.
2. Resolve global legal-registry reviewer authorization before inviting external firms.
3. Perform SQL-query-by-query and UI/API route review, then add tests for every newly identified cross-firm path.
4. Design tenant DB and file-storage boundaries; migrate only after backup, row-count, relationship, and rollback verification are tested.
5. Implement backup/restore/deletion isolation tests and obtain independent security review.
6. Keep public registration and production confidential matter use disabled until release gates pass.


## Read-only ownership preflight extension

`scripts/tenant_ownership_preflight.py` now checks for orphaned rows in the `notes`, `deadlines`, `fees`, `tasks`, `events`, and `sessions` tables when those tables and the `cases` table exist. Such child rows must not be repaired by guessing a parent; reconcile them from trusted records and a reviewed backup. Run `PYTHONPATH=. python tests/test_tenant_ownership_preflight.py` to exercise the added checks.

The preflight also flags document metadata and matter-child rows whose `case_id` is NULL. These rows are reported as unlinked rather than automatically treated as shared or assigned to a firm; an operator must establish their intended classification from trusted evidence. The check remains a read-only data-quality aid. It does not prove that API endpoints authorize every parent/child operation and does not migrate or repair data.


## Ownership preflight schema-readiness guard

The read-only ownership preflight now fails closed when the database is empty or lacks any core ownership table/column (`firms.id`, `users.id`, `users.firm_id`, `cases.id`, `cases.firm_id`). It returns `review_required` instead of treating an uninspectable schema as a clean ownership result. This detects only core schema readiness; it does not prove that all optional tables exist or that tenant isolation is enforced at runtime.
