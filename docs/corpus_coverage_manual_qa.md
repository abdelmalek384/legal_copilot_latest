# Corpus Coverage & Provenance — Manual QA Checklist

**Purpose:** Record browser-level validation for issue #93 and the corpus-coverage registry drill-down. This is a procedure, not evidence that any check has passed.

## Run record

- Date/time:
- Tester:
- Commit/build:
- Environment: disposable staging/local test instance only
- Browser/version:
- Viewport / zoom:
- Language and direction: Arabic / RTL; English / LTR
- Test account role:
- Result: Not run / Pass / Fail / Blocked
- Evidence link or notes:

## Safety prerequisites

- [ ] Use a disposable database containing synthetic registry fixtures only.
- [ ] Confirm no production client records or confidential matter documents are loaded.
- [ ] Include source records with allowed, limited/restricted, and unknown permission states.
- [ ] Include instruments with no version, pending review, rejected, and fully gated synthetic versions.
- [ ] Record the exact tested commit. CI is not a substitute for this browser checklist.

## Authorization and privacy

| Check | Expected result | Result / notes |
|---|---|---|
| Signed-out request to coverage and catalog endpoints | Denied; no registry data returned. | |
| Ordinary firm user or firm administrator | Denied unless explicitly authorized as a platform legal reviewer. | |
| Firm administrator or email present only in a former reviewer allowlist | Denied unless the identity has an explicit `platform_reviewer` or `platform_admin` role. | |
| Authorized platform legal reviewer | Can open coverage metrics and registry drill-downs. | |
| Source and instrument listings | Show shared legal-registry metadata only; never show matter-document passages or uploaded firm content. | |
| Catalog endpoint input | Unknown kinds are rejected; search is parameterized and bounded; excessive limits are capped. | |
| Network behavior | Opening coverage or searching the catalog does not scrape, download, or contact registered source sites. Only a user click on an approved HTTPS link opens that source. | |

## Metrics and drill-down behavior

| Check | Expected result | Result / notes |
|---|---|---|
| Metric definitions | Every metric exposes a definition via hover and an accessible label; a verified label alone is not described as proof of legal validity. | |
| Source count | Opens the source registry list with authority, registered URL, permission states, and associated instrument count. | |
| Instrument count | Opens the instrument registry list with title/ID, authority, practice area, permission states, and version count. | |
| Metadata-only instruments | Opens only instruments with no registered version. The displayed version count is zero. | |
| Version count | Opens the version review queue without silently applying a narrower status filter. | |
| Review-status / verification metrics | Open the matching filtered version queue. Counts and visible rows agree for the synthetic fixture set. | |
| Catalog search | Search by source ID, instrument ID/title, law number/year, or authority. Query results remain within the selected catalog kind. | |
| Enter-key search | Pressing Enter in the catalog search field produces the same filtered result as the Search button. | |
| Search beyond the default limit | Find a known fixture beyond the first 100 records using the search field; the UI does not imply that unshown records do not exist. | |
| Permission-state summary row | Activate a permission pair with mouse and keyboard; the source list contains only records matching both recorded permission values. | |
| Search within permission-filtered sources | Search by authority/source ID while permission filters remain active; results continue to match both permission states. | |
| More than 100 records | Use search to locate a known record beyond the default first 100; no record is implied absent solely because it is outside the initial result limit. | |
| Permission states | Missing/unknown permission evidence remains unknown or blocked; no click or view changes permissions or legal-status fields. | |
| Coverage by practice area | Unknown/unclassified remains explicit. No overall legal-coverage percentage is presented. | |
| Empty, loading, and API-error states | Each state is understandable and recoverable; empty registry counts are not presented as proof that no law exists. | |

## Keyboard, language, layout, and source links

| Check | Expected result | Result / notes |
|---|---|---|
| Keyboard-only operation | Metric cards, catalog search, close action, review queues, and source links are reachable in a logical order with visible focus. | |
| Arabic / RTL | Metric definitions, counts, permissions, mixed Arabic/Latin IDs, and catalog rows remain readable and aligned. | |
| English / LTR | Labels and reading order switch correctly; no important Arabic-only labels remain. | |
| Narrow mobile (320–420 px), tablet, desktop | No page-level horizontal overflow; rows and controls wrap without overlap. | |
| Zoom (200%) and high contrast | Metrics, labels, status differences, and actions remain available and perceivable. | |
| Registered HTTPS source | Link shows the registered host, opens in a new tab, and uses opener isolation. | |
| Unsafe or non-HTTPS source URL | No clickable source link is rendered. | |

## Release decision

- [ ] Critical authorization and data-boundary checks pass.
- [ ] API/UI failures are recorded as issues with reproduction steps.
- [ ] Lawyer review of source authenticity, current legal status, and licensing is tracked separately.
- [ ] Manual browser/RTL evidence is attached before issue #93 is marked complete.

**This checklist does not establish legal correctness, corpus completeness, production security, or permission to reuse source material. Do not mark manual QA complete while critical checks remain untested or blocked.**
