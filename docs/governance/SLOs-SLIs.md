# SLOs & SLIs

## Objectives

- API P95 latency < 200 ms (steady-state, **excluding cold-start latency**; see Notes)
- Error rate < 0.1%
- MTTR < 30 min

## Indicators (examples)

- Request latency histogram → P95 (PromQL)
- Error ratio of 5xx over total
- DLQ depth for messaging (later when broker is hosted)
- **Cold-start P95** (informational metric, not part of SLO) — label by cause: `reason="deploy"`, `reason="restart"`, or `reason="idle"` where the platform suspends

## PromQL sketches

- **API P95**:
  ```
  histogram_quantile(0.95, sum(rate(http_server_request_duration_seconds_bucket{service="api"}[5m])) by (le))
  ```
- **Error rate**:
  ```
  sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m])) / sum(rate(http_server_requests_seconds_count[5m]))
  ```
- **Cold-start** (example patterns):
  - Option A: expose a dedicated histogram `app_cold_start_request_seconds_bucket` with a `reason` label (`deploy`, `restart`, `idle`) and chart P95 per reason.
  - Option B: add a log/metric label `is_cold_start="true"` on the first request after a cold JVM and compute its P95 separately.

## Notes

- **The cold-start exclusion is not tied to any specific host.** It was originally written for Render Free, which may idle and suspend services — but [ADR-007](/reference/backend/decisions/ADR-007-render-hosting.md) is now marked not in force and was never executed, and a full hosting decision is still owed. The exclusion is retained because a JVM has genuine warmup cost (class loading and JIT) after any restart or deploy regardless of host, so it is stated in host-neutral terms.
- We explicitly **exclude** cold-start latencies from the steady-state latency SLO, but we **track and visualize** them separately so the cost is visible rather than hidden.
- **Restate this once the hosting decision is recorded.** Whether the exclusion needs to cover idle-suspend as well as warmup depends entirely on the platform chosen: an always-on container has warmup only, whereas a scale-to-zero platform reintroduces idle-suspend.
- Document demo windows if using optional keep-alive pings; do **not** run persistent keep-alive.
