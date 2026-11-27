# AI-2 stabilization progress — 2026-11-27

## Focused implementation: original-file local deletion name-swap guard

- Reviewed the existing local private original-file storage adapter. Its delete operation checked a name's metadata and then unlinked the name directly; a same-namespace replacement between those operations could result in removing the substituted entry.
- Implemented inode pinning through an opened descriptor, an atomic same-directory quarantine rename, and post-rename identity/type/link-count validation before unlinking.
- If the moved entry does not match the pinned inode, the implementation restores regular-file/symlink entries through no-follow hardlinking where possible and fails. If recovery cannot be completed, it leaves the quarantined entry for operator recovery rather than unlinking an unverified object.
- Added an injection regression in `tests/test_original_file_storage.py` that swaps the staged name after the descriptor is pinned and asserts that the replacement remains and the raced entry is restored. Existing security-regression script and workflow registration were checked and already include this module.
- This change is confined to the local storage adapter; it does not alter S3 purge semantics, legal-hold checks, caller authorization, retention policy, or legal retrieval.

## Task completion and validation

| Item | Status |
|---|---|
| Source implementation | 100% authored |
| Regression test | 100% authored |
| Standalone temporary-directory harness | 2/2 scenarios passed |
| Exact repository test module | Not run |
| Full local suite | Not run |
| Browser/mobile acceptance | Not performed |
| Live storage/offboarding/backup recovery | Not performed |

The harness exercised normal verified deletion and a synthetic name substitution that preserved both the replacement and the pinned original. It is copied helper logic in a standalone Python run, not execution of the repository module or regression test.

## Eight-workstream estimates

| Workstream | Previous | Current | Delta |
|---|---:|---:|---:|
| Backend / existing workflows | 90.0% | 90.0% | 0.0 pp |
| Frontend / usability | 95.0% | 95.0% | 0.0 pp |
| Mobile / Arabic-English UI | 83.0% | 83.0% | 0.0 pp |
| Security / tenant isolation | 85.1% | 85.1% | 0.0 pp |
| Documents / file handling | 99.1% | 99.1% | 0.0 pp |
| Deployment / backup / recovery | 47.1% | 47.1% | 0.0 pp |
| Local testing / regression readiness | 12.0% | 12.0% | 0.0 pp |
| Overall AI-2 | 76.4% | 76.4% | 0.0 pp |

These are inherited engineering estimates including the previously reported unmerged backup-retention branch contribution; they are not acceptance or test-pass rates. The repository's mainline progress note remains 76.3% overall, 46.9% deployment/recovery, and 11.8% testing-readiness because PR #2036 was closed unmerged. Do not treat PR #2036 as integrated.

## Branch and integration

- Branch: `ai2/guard-original-object-delete-race-20261127`.
- No PR was merged.
- The local Python 3.12 repository runtime/checkouts remain unavailable; GitHub Actions were not used.
- Pilot remains NOT READY pending route-level and tenant isolation execution, browser/mobile and Arabic-English acceptance, document-integrity acceptance, deployment and witnessed backup/restore, live storage policy evidence, and independent review.
