# Case search and pagination

The Cases page uses the firm-scoped `GET /cases/search` endpoint instead of loading every matter into the browser.

## Search behavior

Search matches case title, client name, case number, case year, court, circuit and opposing party. Search input is parameterized and SQL wildcard characters are treated literally. Status filters support open and closed matters.

## Pagination contract

- Default page size: 50.
- Maximum page size: 100.
- Offset range: 0–100,000.
- Search text: maximum 200 characters.
- Response includes `items`, `total`, `limit` and `offset`.
- Ordering is stable by client name then case ID.
- The previous/next controls use the returned total and never request an unbounded result set.

## Authorization

The endpoint resolves the active firm from the authenticated session. Firm administrators can search all matters in their firm. Other users see only cases for which they have case membership. No caller-supplied firm ID or tenant path is accepted.

The legacy `GET /cases` endpoint remains for existing internal callers. New case-discovery UI should use the paginated endpoint.

## Operational limits

The endpoint caps each page at 100 rows. This bounds response size but does not replace database indexing or load testing against a large representative firm. Before claiming large-firm performance, measure query latency and query plans using realistic matter counts and search terms, then add indexes only where measured plans justify them.
