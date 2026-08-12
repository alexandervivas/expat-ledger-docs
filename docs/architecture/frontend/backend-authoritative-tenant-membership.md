# Backend-authoritative tenant membership

Issue #16 implements FR-001, FR-007, FR-012, and NFR-003 using backend OpenAPI v1.2.0 `GET /v1/tenants` as the only tenant-membership authority. The discovery projection is deliberately limited to UUID `id`, non-empty `name`, and exact-case role `Owner`, `Admin`, or `Viewer`.

Discovery is authenticated but is not tenant-scoped; it omits `X-Tenant-Id` only through the explicit authentication request scope. All normal Ledger API operations retain mandatory tenant scope. A persisted last-active ID is a convenience preference, not authority, and is revalidated against every successful snapshot. Empty, unauthorized, malformed, unavailable, and failed responses clear in-memory authority and do not use browser-local tenant records.

The backend contract also defines tenant administration operations. This frontend slice intentionally implements discovery only, so legacy administration and invitation pathways fail explicitly rather than infer authorization from local state. A separately approved frontend change must integrate those operations.
