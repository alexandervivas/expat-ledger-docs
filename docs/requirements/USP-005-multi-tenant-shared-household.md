# USP-005: Multi-Tenant "Shared Household" Ledgers

## Status

- **Type**: Unique Selling Point
- **Priority**: Should Have
- **Status**: Draft

## Description

Allows expats to manage financial data for family members (e.g., parents back home) or share expenses with a partner who has a different base currency, all within the same application but with strict isolation.

## Technical Implementation

- Leverages the **M:N User-Tenant Mapping** (Iteration 2).
- Users can be members of multiple tenants with different roles.

## Key Features

1. **Sub-Ledger Delegation**: Allow "View-only" or "Manager" access to specific sub-ledgers for family members.
2. **Cross-Tenant Dashboard**: A unified view for the user showing their personal ledger and any "Shared" or "Family" ledgers they manage.
3. **Multi-Currency Shared View**: Automatically converts shared ledger balances into the user's preferred viewing currency.

## Business Value

Makes the ledger the central "Operating System" for the entire expat family, increasing product "stickiness" and user retention.
