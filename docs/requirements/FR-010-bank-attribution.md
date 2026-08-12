# Requirement FR-010: Bank Attribution

## Status

- **Type**: Functional Requirement
- **Priority**: High
- **Iteration**: 3
- **Status**: Implemented

## Description

Every transaction must be explicitly attributed to a specific bank. This allows for better categorization, filtering, and reconciliation.

## User Story

As an Expat, I want to see which bank each transaction belongs to so that I can reconcile my ledger with my real-world statements.

## Functional Requirements

1. **Bank Association**: Link every transaction to a `bank_id`.
2. **Bank Scoping**: Banks are created and managed within the context of a tenant.
3. **Dropdown Selection**: UI should provide a way to select existing banks or create new ones inline.

## Data Points

- `bank_id`: Reference to a bank entity.
- `transaction_id`: The transaction being attributed.

## Constraints

- **Referential Integrity**: A transaction cannot be created without a valid `bank_id` belonging to the same tenant.
