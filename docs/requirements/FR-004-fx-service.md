# Requirement FR-004: FX Service (Historical Conversion)

## Status

- **Type**: Functional Requirement
- **Priority**: High
- **Iteration**: 2
- **Status**: Implemented

## Description

Provides historical exchange rates for currency conversion (USD, EUR, COP). Essential for calculating multi-currency equivalents of balances and transactions.

## User Story

As an Expat, I want the system to automatically know the exchange rate on the day a transaction happened so that I can see its value in my home and host currencies accurately.

## Functional Requirements

1. **Historical Lookups**: Fetch the exchange rate for a specific pair (Base/Target) on a specific date.
2. **Identity Rate**: The rate for a currency to itself is always 1.0.
3. **Inversion**: If a rate for A/B exists, the system can derive B/A.
4. **Caching**: Frequent lookups must be cached to ensure performance.

## Data Points

- `from_currency`: ISO 4217 code.
- `to_currency`: ISO 4217 code.
- `date`: Reference date.
- `rate`: Decimal exchange rate.

## Constraints

- **Precision**: Rates must be tracked with at least 10 decimal places.
- **Availability**: System must handle cases where a rate is missing (e.g., using a proxy rate or throwing a domain error).
