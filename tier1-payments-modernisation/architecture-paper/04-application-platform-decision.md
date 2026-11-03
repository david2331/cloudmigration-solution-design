# Application platform decision

**Selected cloud: AWS. Task 3 (15%). EKS/Helm is the confirmed runtime direction, not a claim of universal superiority.**

| Platform | Representative component | AWS behavior and operational trade-off | Decision |
|---|---|---|---|
| EKS | Payment API, orchestration, long-running rail adapters, reconciliation | AWS-managed Kubernetes control plane; bank owns worker lifecycle, add-ons, policy, capacity and workload resilience | Standard runtime; separate clusters by entity and region |
| ECS | Containerized APIs and workers | Task definitions/services with scheduler replacement; EC2 or Fargate capacity reduces some orchestration work but uses AWS-specific deployment APIs | Credible alternative; rejected as primary to preserve chosen Kubernetes/Helm operating model |
| Lambda | Bounded event handlers, peripheral automation | Event-driven concurrency, retry and execution-mode limits; cold-start and downstream connection behavior require assessment | Exception for justified peripheral work, not default payment runtime |
| EC2 | Vendor agents or legacy software needing host control | Full OS/process control with corresponding hardening, patching, failover and scaling work | Transitional exception with owner and retirement gate |

AWS sources: EKS [S2], ECS [S15], Lambda [S16] in the [evidence register](../appendix/provider-native-evidence.md). Lambda limits vary with execution mode; do not apply a single duration claim to all modes. ECS is not rejected for being less safe or less available.

Kong also runs on EKS but is platform-owned. Applications package only their workloads and allowed routes, not private Kong administration or duplicate gateway installations. Terraform application infrastructure provisions stateful dependencies; the application's Helm release must not delete its ledger.

## Portability comes from design, not a platform label

| Boundary | Evidence to create | Remaining coupling |
|---|---|---|
| Runtime | Run the same OCI image with standard Kubernetes resources | Scheduling, identity and ingress integrations |
| Packaging | Thin platform overlays and pinned Helm dependencies | Kong CRDs/plugins, service annotations and storage classes |
| APIs | Versioned OpenAPI/event schemas and contract tests | Identity provider integration and edge policies |
| Messaging | Adapter interfaces, durable outbox, idempotent consumption | SQS delivery, ordering and DLQ semantics |
| Data | PostgreSQL-compatible schema and rehearsed export/import | Aurora replication, extensions, operations and performance |
| Observability | OpenTelemetry instrumentation | CloudWatch queries, dashboards and operational tooling |
| Automation | Terraform module interfaces and isolated state | AWS-specific provider resources; Terraform is not cloud-agnostic infrastructure |

Gateway API HTTPRoutes reduce some routing coupling, but Kong-specific policies still require translation. Keep payment rules and business authorization in services, not proprietary gateway plugins.

Demonstrate portability by moving one representative service to a separate conformant Kubernetes environment with alternate infrastructure adapters and recording the changes, elapsed work and correctness results. Do not add a second cloud to this target architecture just to claim portability.

The [two-page-equivalent ADR](../adr/ADR-001-EKS-Platform-Decision.md) records the decision, rejected alternatives, risks and review triggers.
