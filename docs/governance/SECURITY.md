# Security Policy

## Supported Versions

Until 1.0.0, only the `main` branch receives fixes.

## Reporting a Vulnerability

Open a private security advisory or email the maintainers. Do not create public issues for vulnerabilities.

## Standards

- OWASP ASVS 5.0.0 Level 2 verified target, with 13.3.4, 13.1.4 and the hardware-backed elevation of 13.3.1 adopted deliberately, 13.3.3 deferred on the P95 latency budget, and a recorded 13.2.1 deviation for static database credentials (see ADR-026)
- Security headers (CSP, HSTS, X-Content-Type-Options, Referrer-Policy)
- Least-privilege DB roles; secrets via environment/secret manager
- SBOM + image scanning (e.g., Trivy)
