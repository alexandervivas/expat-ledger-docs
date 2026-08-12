# Requirement FR-001: Tenant Onboarding

## Status

- **Type**: Functional Requirement
- **Priority**: Must Have
- **Iteration**: 1
- **Status**: Implemented

## Description

The system must allow a user to create a tenant to enable multi-tenancy. A Tenant represents a legal or personal financial entity (e.g., an individual expat or a family unit). Onboarding involves defining the entity's name, primary reporting currency, and initial tax residencies.

## User Story

As an authenticated user, I want to create my profile with my base currency and tax residencies so that the system can correctly track my wealth across borders.

## Acceptance Criteria

- Given an authenticated user, when tenant data is valid, then a tenant is created.
- Success Metric: Tenant creation succeeds > 99.9%.

## Functional Requirements

1. **Entity Definition**: Create a tenant with a unique name.
2. **Currency Selection**: Choose a reporting currency (ISO 4217, e.g., USD, EUR, COP).
3. **Tax Residency**: Define one or more initial tax residencies (ISO 3166-1 alpha-2).
4. **Owner Assignment**: The user performing the onboarding is automatically assigned as the "Owner" of the tenant.
5. **Isolation**: All data subsequently created must be scoped to this `tenant_id`.

## Data Points

- `tenant_id`: Unique UUID.
- `name`: String.
- `reporting_currency`: 3-letter currency code.
- `tax_residencies`: List of 2-letter country codes.

## Constraints

- **One Owner Rule**: A user can be the owner of at most one tenant (business rule enforced in Iteration 2).
- **Auditability**: Creation time and ID must be tracked in UTC.
