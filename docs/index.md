# Expat Ledger — Developer Docs

Welcome! This site documents the architecture, contracts, and governance for the Expat Ledger project.

## Quick links

- **Architecture**:
  - [C4 Context](architecture/c4-context.md)
  - [C4 Containers](architecture/c4-container.md)
- **Decisions**:
  - [ADR Index](/reference/backend/decisions/index.md)
- **Contracts**:
  - [OpenAPI v1 Changelog](/reference/backend/contracts/openapi/v1/CHANGELOG.md)
  - [Traceability Matrix](requirements/TRACEABILITY.md)
- **Governance**:
  - [Glossary](/glossary.md)
  - [Scope CHANGELOG](governance/scope-CHANGELOG.md)
  - [Product CHANGELOG](governance/product-CHANGELOG.md)

## How to run docs locally

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# Pull contracts and ADRs from the application repositories. Required:
# the nav references pages this step generates, so --strict fails without it.
.venv/bin/python scripts/aggregate.py

.venv/bin/mkdocs serve   # open http://127.0.0.1:8000
```

`mkdocs build --strict` is the gate CI enforces. See the
[repository README](https://github.com/alexandervivas/expat-ledger-docs#building-locally)
for the full workflow.

## Contributing

- Use Conventional Commits.
- For breaking API/event changes: open an ADR and update contract changelogs.
- Keep diagrams and examples minimal and testable.
