# Requirement AI-002: Spending Forecast

## Status

- **Type**: Functional Requirement
- **Priority**: Could Have
- **Iteration**: 6
- **Status**: Draft

## Description

Provide users with a 30/60/90-day forecast of their cash flow based on historical income and spending patterns, accounting for recurring bills and seasonal trends.

## User Story

As an Expat, I want to see my projected balance for the next 3 months so that I can plan large purchases or transfers without risking a low balance.

## Acceptance Criteria

- Forecast accuracy within 15% for the first 30 days.
- Account for known recurring transactions (e.g., rent, salaries).

## Functional Requirements

1. **Recurring Transaction Identification**: Automatically identify recurring payments and income.
2. **Trend Projection**: Use historical data to project future non-recurring spending.
3. **Scenario Planning**: Allow users to add "what-if" transactions to see the impact on the forecast.
