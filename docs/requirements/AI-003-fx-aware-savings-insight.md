# Requirement AI-003: FX-Aware Savings Insight

## Status

- **Type**: Functional Requirement
- **Priority**: Could Have
- **Iteration**: 3 (Capture only)
- **Status**: Draft (Pivoted from Daily Savings)

## Description

The "FX-Aware Savings Insight" engine provides users with strategic advice on where to hold their liquidity to avoid inflation, devaluation, or to maximize interest in a multi-currency environment. It replaces simple savings tracking with a proactive currency optimization tool.

## User Story

As an Expat with accounts in USD and COP, I want to know if I should keep my savings in USD to avoid COP devaluation or if there's a specific day to send money home to maximize my "home country" purchasing power.

## Acceptance Criteria

- System suggests which account/currency is "safer" or "more efficient" for savings based on historical FX trends.
- Non-intrusive UI elements that explain upcoming "Smart Insights" features.

## Functional Requirements

1. **Liquidity Optimization**: Suggest the best currency/account to hold savings based on historical FX rates from `fx-service`.
2. **Inflation/Devaluation Awareness**: Flag when a specific currency in the user's portfolio is losing significant value compared to their reporting currency.
3. **Purchasing Power Tracking**: Show how much a fixed savings amount in a "host" currency is worth in the "home" currency over time.
4. **AI Placeholder**: Display a non-intrusive UI element explaining the upcoming "Smart Insights" feature (USP-004).

## Data Points

- `tenant_id`: To ensure data isolation.
- `portfolio_currencies`: List of currencies held by the tenant.
- `historical_fx_trend`: 30/60/90 day trend analysis.
- `suggested_currency`: The recommended currency for holding savings.

## Constraints

- **Multi-currency**: Must leverage the `fx-service` historical SPI.
- **Privacy**: All savings data must be subject to the same tenant isolation and encryption standards as other financial data.
