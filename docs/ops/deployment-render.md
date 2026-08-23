# Deployment — Render (Free Tier) — NOT IN FORCE

> **This runbook does not describe a real environment and must not be followed.** The Render decision — now devops [ADR-016](https://github.com/alexandervivas/expat-ledger-devops/blob/main/docs/decisions/ADR-016-render-hosting.md) — is marked not in force: it was never executed — the `render.yaml` that step 1 below asks you to commit was never committed, and no Render environment was ever created — and [ADR-026](/reference/backend/decisions/ADR-026-secret-management-proportionality.md) selects AWS for key and secret management because Render provides no managed KMS.
>
> **The hosting decision has since been made elsewhere:** devops [ADR-017](https://github.com/alexandervivas/expat-ledger-devops/blob/main/docs/decisions/ADR-017-hosting-platform.md) selects GCP-native hosting in `europe-west4`, so this runbook is not authoritative for any environment. It is retained as the historical record of the September 2025 intent. The steps below never worked, because they were never carried out.

Originally: an environment for demos only, expecting cold starts and DB expiry (~30 days) on the free plan.

## Blueprint

Render supports declarative deploys via `render.yaml` at the repository root.

### Steps

1. Commit `render.yaml` (see repo root).
2. In Render, create a **Blueprint** pointing to your GitHub repo.
3. Set env vars if needed (secrets in Render dashboard):
   - `NEXT_PUBLIC_API_BASE_URL=https://<api-service>.onrender.com`
4. First deploy will provision the DB; the app applies Flyway migrations on boot.
5. Verify health endpoint on the API service.

## Known constraints

- **Cold starts**: services may idle; first request latency spikes.
- **DB expiry**: Free Postgres may be deleted after ~30 days. Use seed/export scripts.

## Seed & export (outline)

- **Seed**: Scala runner or SQL script to insert minimal tenants/accounts/banks.
- **Export**: `pg_dump` job invoked locally; do not dump secrets/PII.

## Next steps

- Add synthetic pings only during **scheduled demos** (optional), and document them.
