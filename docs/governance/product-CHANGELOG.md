# Changelog

All notable changes to this project will be documented here. Format: Keep a Changelog.

> **Decoding ADR identifiers in this log.** Entries are historical records and keep the
> identifiers they were written with. The backend series was renumbered on 2026-08-21
> ([backend#228](https://github.com/alexandervivas/expat-ledger-backend/issues/228)) and the
> devops series on the same day ([devops#34](https://github.com/alexandervivas/expat-ledger-devops/issues/34)).
> Resolve any identifier below through the old → new mapping tables in the
> [backend decisions index](https://github.com/alexandervivas/expat-ledger-backend/blob/main/docs/architecture/decisions/index.md)
> and the [devops decisions index](https://github.com/alexandervivas/expat-ledger-devops/blob/main/docs/decisions/index.md).
> A number alone never identifies a decision across repositories — the repository is the disambiguator.

## [Unreleased]

### Added

- Bank attribution per transaction (FR-10).
- Balances with EUR/COP equivalents (FR-11).
- Render Free tier hosting (ADR-007, now devops [ADR-016](https://github.com/alexandervivas/expat-ledger-devops/blob/main/docs/decisions/ADR-016-render-hosting.md); not in force), docs & blueprint.

## [0.1.0] - 2025-10-10

### Added

- Initial tenants/accounts/transactions API.
