# Requirement FR-011: Multi-Currency Balances (EUR/COP equivalents)

## Status

- **Type**: Functional Requirement
- **Priority**: High
- **Iteration**: 3
- **Status**: Implemented

## Description

The system must calculate and display account balances in their native currency, as well as their equivalents in EUR and COP, using historical exchange rates.

## User Story

As an Expat, I want to see my total wealth in a single currency (EUR or COP) regardless of where the money is held, so that I can understand my overall financial position.

## Functional Requirements

1. **Native Balance Calculation**: Sum of all transactions in the account's currency.
2. **Equivalent Calculation**: Use the FX Service to convert the native balance to EUR and COP equivalents as of the current date or a specific historical date.
3. **Total Wealth View**: Aggregate balances across all accounts in a chosen reporting currency.

## Data Points

- `native_balance`: Amount in the account's original currency.
- `eur_equivalent`: Calculated amount in EUR.
- `cop_equivalent`: Calculated amount in COP.

## Constraints

- **Performance**: Use snapshotting (T3.5) to ensure balance queries remain fast even as transaction history grows.
- **Accuracy**: FX rates must correspond to the date of the balance calculation.
