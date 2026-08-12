# USP-003: Hidden Fee Benchmarking

## Status

- **Type**: Unique Selling Point
- **Priority**: Must Have (Integrated into FR-006)
- **Status**: Draft

## Description

When linking a remittance between two accounts (outflow in Currency A, inflow in Currency B), the system calculates the "Real FX Cost" by comparing the effective rate against the mid-market rate provided by the `fx-service`.

## Functional Alignment

- **FR-006**: Sub-requirement for "Fee Calculation".
- **FR-004**: Uses `fx-service` for mid-market rate benchmarking.

## Key Features

1. **Spread Calculation**: "This transfer cost you $45 in hidden spreads compared to the mid-market rate."
2. **Efficiency Score**: Assigns a grade (A-F) to specific remittance providers based on historical costs.
3. **Cumulative Savings Tracker**: Shows how much the user has "lost" to hidden fees over the year.

## Business Value

Transfers power from banks/remittance providers to the user by exposing the true cost of moving money across borders.
