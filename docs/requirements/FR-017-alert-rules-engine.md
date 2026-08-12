# Requirement FR-017: Alert Rules Engine (DSL)

## Status

- **Type**: Functional Requirement
- **Priority**: Won't Have
- **Iteration**: N/A
- **Status**: Deferred (Replaced FR-017 Custom SQL)

## Description

The system should provide a Rule Engine or a restricted Domain Specific Language (DSL) to allow users to trigger system alerts based on ledger events or balance thresholds. This replaces the previous "Custom SQL Alerts" to ensure security and prevent performance degradation.

## User Story

As a power user, I want to define custom rules (e.g., "Alert me if my COP balance drops below 2,000,000") without compromising the system's security or stability.

## Strategic Alternative

Instead of raw SQL, the system will implement a safe, restricted Rule Engine. This provides the flexibility users need while preventing SQL injection and protecting the database schema.

## Acceptance Criteria

- N/A (Deferred for current cycle)
