# AI-2 manual stabilization progress — 2026-11-28 (reconciliation identity)

## Focused fix: pin object identity across local reconciliation hashing

- The local original-file reconciler used an inventory `lstat` for type/link-count checks, then opened the name and hashed bytes without comparing the opened descriptor to the inventory inode. It also did not verify that the directory entry still referenced that inode after hashing.
- The hash helper now requires the expected device/inode identity, compares it with `fstat` immediately after opening, and rechecks the name's no-follow metadata after hashing.
- Added synthetic regressions that replace an object name between inventory and open, and between open and hash completion. The reconciler must report the object as unreadable and retain the replacement/parked entries.
- Scope: read-only local reconciliation only. No purge, repair, legal content, tenant routing, or retrieval architecture change.

## Task completion and validation

| Item | Status |
|---|---|
| Source implementation | 100% authored |
| Regression tests | 100% authored (2 race cases) |
| Read-back of source, tests and progress/blocker documentation | Verified |
| Isolated copied-logic harness | 2/2 race scenarios passed (before-open; post-open) |
| Repository test module | Not run |
| Full regression suite | Not run |
| Browser/mobile/Arabic-English acceptance | Not performed |
| Live storage or backup/restore | Not performed |

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

These estimates are unchanged. This source-level race detection does not establish full filesystem race immunity or acceptance.

## Integration and blockers

- Branch: `ai2/pin-reconciliation-object-identity-20261128`, based on main commit `621468e37dd8f7e0ca0fc932a96d0a6d13ab8ade`.
- Draft PR #2046; no PR merged and no GitHub Actions used.
- Repository Python 3.12 runtime/checkouts remain unavailable.
- Pilot remains NOT READY.
