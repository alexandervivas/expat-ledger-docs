# Requirement FR-014: Advanced Filtering Engine

## Status

- **Type**: Functional Requirement
- **Priority**: Should Have
- **Iteration**: 4
- **Status**: Draft

## Description

Provide a robust UI for slicing data by date, category, and region.

## User Story

As a user, I want to filter my transactions by date range and category so that I can understand where my money is going.

## Acceptance Criteria

- Filters must update the dashboard state in real-time.
- Filter configurations can be saved for future use.

## Functional Requirements

1. **Multi-criteria Filtering**: Support filtering by date range, account, category, amount range, and description.
2. **Real-time Updates**: Applying a filter should immediately update the displayed data and charts.
3. **Saved Filters**: Users can save a set of filters with a name for quick access later.
4. **Tenant Scoping**: Filters only apply to the current tenant's data.

## Data Points

- `filter_name`: String.
- `criteria`: JSON object containing filter parameters.
