# Requirement FR-003: Transaction Ledger

## Status

- **Type**: Functional Requirement
- **Priority**: High
- **Iteration**: 3
- **Status**: Implemented

## Description

A centralized ledger that records all financial transactions across all accounts. It supports multi-currency entries and maintains metadata for categorization and reconciliation.

## User Story

As an Expat, I want a single place where all my transactions are recorded so that I can see my historical spending and income across all my accounts and currencies.

## Functional Requirements

1. **Transaction Recording**: Save transactions with date, amount, currency, and account reference.
2. **Metadata**: Support for bank-provided descriptions and custom tags.
3. **Immutability**: Once recorded, transactions should ideally be immutable (corrections via reversals).
4. **Querying**: Filter and sort transactions by date range, account, or bank.

## Data Points

- `transaction_id`: Unique UUID.
- `account_id`: Source/Destination account.
- `amount`: Decimal (positive for inflow, negative for outflow).
- `currency`: ISO 4217 code.
- `booking_date`: Date the transaction was recorded by the bank.
- `description`: Raw text from bank statement.

## Constraints

- **Performance**: P95 latency for date-range queries < 200ms.
- **Accuracy**: Calculations must use high-precision decimals (BigDecimal).
