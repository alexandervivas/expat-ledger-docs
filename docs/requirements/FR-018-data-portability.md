# Requirement FR-018: GDPR/CCPA Data Portability

## Status

- **Type**: Functional Requirement
- **Priority**: Should Have
- **Iteration**: 5
- **Status**: Draft

## Description

Users must be able to request and receive a full dump of their ledger data in a structured, commonly used, and machine-readable format. This ensures compliance with GDPR (Right to Data Portability) and CCPA.

## User Story

As a user, I want to be able to download all my data (tenants, accounts, transactions) so that I can migrate it to another service or keep it for my own records.

## Acceptance Criteria

- Users can trigger a "Request Data Dump" from their profile.
- The system generates a ZIP file containing CSV/JSON files for all user-owned data.
- The dump includes: Tenants, Accounts, Transactions, Banks, and Remittance Links.

## Functional Requirements

1. **Self-Service Export**: A dedicated UI section for data portability requests.
2. **Complete Data Coverage**: Export must include all entities owned by the tenant.
3. **Machine-Readable Format**: Data should be exported in JSON or CSV.
4. **Secure Delivery**: The data dump should be protected (e.g., via a time-limited signed URL).

## Constraints

- **Tenant Isolation**: Users can only export data for tenants they have "Owner" or "Admin" roles in.
- **Performance**: Large data dumps must be processed as background jobs to avoid blocking the API.
