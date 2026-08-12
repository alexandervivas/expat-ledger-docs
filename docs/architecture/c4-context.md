# C4 — System Context

```mermaid
flowchart LR
  %% Classes
  classDef roadmap stroke-dasharray: 5 5,stroke:#888,color:#666;

  User[End User] -->|Web| NextJS[Next.js Frontend]
  NextJS -->|HTTPS /v1| API[API Module]

  %% Partners interact via RabbitMQ (AMQP)
  Partner[Partner Systems] -->|AMQP| RMQ[RabbitMQ]

  %% Core interactions within the platform
  API -->|gRPC| Modules[Business Modules]
  Modules -->|JDBC| PG[(PostgreSQL)]
  Modules -->|AMQP events| RMQ
  RMQ -->|AMQP events| Modules

  %% Service discovery (Static config)
  API -. static/env config .-> API
  Modules -. static/env config .-> Modules

  %% Observability (roadmap)
  API -. OTel SDK .-> OTel[OTel Collector]
  OTel --> Prom[Prometheus]
  Prom --> Graf[Grafana]

  %% Styling roadmap elements
  class OTel,Prom,Graf roadmap;
```
