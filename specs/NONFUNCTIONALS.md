# Non-Functional Requirements

This document captures the quality attributes and system properties that must be preserved in every change, mapped back to the constitution’s principles of integrity, reliability, and consistency.

## Security & Compliance

- Encrypt data at rest/in transit and log every critical decision for verifiable attestation.
- Use strong authentication/authorization (e.g., JWT, ABAC policies) and restrict secrets to environment variables.
- Schedule automated security scans, threat modeling, and regulatory reviews; enforce policies through automation and alerting.

### Reliability, Availability & Observability

- Provide health checks, monitoring dashboards, and alerts for key workflows (model read/write, diagram generation, CLI exports).
- Implement structured logging, metrics, and traces so teams can diagnose issues without touching production artifacts.
- Design for graceful degradation and retry/backoff behavior to keep exports available during downstream outages.

### Performance & Efficiency

- Keep core operations (model read/write, diagram render) below 200ms when practical; justify slower paths with async or batching.
- Track and improve efficiency metrics (e.g., CPU/memory for large models, export latency) to minimize user effort and compliance risk.
- Automate repeatable workflows (CLI conversions, documentation generation) and maintain machine-readable artifacts for automation.

### Maintainability & Testing

- Modularize code, rewrite large modules (e.g., `pyArchimate.py`) into focused files, and keep functions short and descriptive.
- Update documentation (README, UML/C4 diagrams, specs) whenever behavior or architecture changes.
- Target >90% coverage on critical logic and automate linting/testing via CI (scripts such as `create_documentation.sh`, `render_diagrams.sh`).
- Use conventional commits and trace each change back to a feature spec/task matrix.

### Process & Automation

- Enforce automated workflows (lint, test, doc build) in CI; maintain traceability matrices linking FR/SC/task/test.
- Use `poetry` for dependency management (fallback to `uv` only when necessary) and keep `pyproject.toml` aligned with PEP 621.

### Error Management

- Provide standardized error payloads with codes/messages and log exceptions with full context.
- Ensure critical operations surface actionable diagnostics so reviewers can reason about failures and state transitions.
