# Requirement FR-002: Account Management

## Status

- **Type**: Functional Requirement
- **Priority**: Must Have
- **Iteration**: 2
- **Status**: Implemented

## Description

The system must allow the creation of accounts per tenant to maintain data structure. Tenants can manage multiple financial accounts (checking, savings, etc.) across different currencies and banks. Each account is tied to a specific bank and has a native currency.

## User Story

As an Expat, I want to register my various bank accounts (e.g., a USD checking account in the US and a COP savings account in Colombia) so that I can track my global liquidity.

## Acceptance Criteria

- Accounts are tenant-scoped and isolated.
- Success Metric: Zero instances of cross-tenant data leakage.

## Functional Requirements

1. **Account Creation**: Define an account with a name, type (CHECKING, SAVINGS), and currency.
2. **Bank Linking**: Each account must be associated with a Bank (see FR-010).
3. **Multi-Currency Support**: Support for at least USD, EUR, and COP.
4. **Initial Balance**: Option to set an initial balance upon creation.
5. **Tenant Scoping**: Accounts are strictly isolated by `tenant_id`.

## Data Points

- `account_id`: Unique UUID.
- `tenant_id`: Owner of the account.
- `bank_id`: Reference to the bank.
- `type`: Account type enum.
- `currency`: ISO 4217 code.
- `initial_balance`: Decimal amount.

## Constraints

- **Security**: Account numbers and sensitive PII must be encrypted at the application level (ADR-017).
