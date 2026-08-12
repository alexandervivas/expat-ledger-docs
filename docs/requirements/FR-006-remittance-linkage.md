# Requirement FR-006: Remittance Linkage

## Status

- **Type**: Functional Requirement
- **Priority**: Medium
- **Iteration**: 3
- **Status**: Implemented

## Description

A heuristic-based system to link related transactions across different accounts and currencies, specifically for remittances (e.g., sending money from a US account to a Colombian account).

## User Story

As an Expat, I want the system to recognize that a $500 withdrawal from my US account is the same "event" as the 2,000,000 COP deposit in my Colombian account, so my wealth is tracked correctly without double-counting.

## Functional Requirements

1. **Heuristic Matching**: Match transactions based on date proximity and currency-adjusted amount equivalence.
2. **Human Confirmation**: Provide a list of suggested links for user approval.
3. **Fee Calculation**: Automatically calculate the "Real FX Cost" by comparing the linked transaction rates against the mid-market rate at the time of transfer (Hidden Fee Benchmarking).
4. **Link Persistence**: Store the relationship between two (or more) transactions.
5. **Link Locking**: Once confirmed, the link is immutable to prevent accidental decoupling.

## Data Points

- `remittance_id`: Unique UUID for the link.
- `source_transaction_id`: Reference to the outflow.
- `target_transaction_id`: Reference to the inflow.
- `status`: PENDING, CONFIRMED.
- `real_fx_cost`: Calculated difference from mid-market rate (USP-03).

## Constraints

- **Multi-tenant**: Linkage can only happen between accounts within the same tenant.
- **Precision**: Matching must allow for small tolerances due to bank fees or rounding.
