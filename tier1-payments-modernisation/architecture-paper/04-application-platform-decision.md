# Application platform decision

**Selected cloud: AWS. Task 3 (15%). EKS/Helm is the proposed standard runtime; ECS, Lambda, Fargate and EC2 are assessed per component rather than excluded by policy.**

## Evaluation criteria

Weights reflect the scenario constraints: 99.99% critical journeys, 30-minute RTO, entity isolation, central guardrails with product ownership, and portability without coupling to one platform product.

| Criterion | Weight | What "good" means for a Tier 1 payment path |
|---|---|---|
| Resilience and recovery fit | 25% | Multi-AZ spread, predictable failover, pre-provisionable in Singapore, no cold dependency on a control plane during recovery |
| Correctness and state handling | 20% | Long-lived connections, controlled concurrency, graceful drain, no hidden retries that duplicate side effects |
| Governance and isolation | 15% | Central guardrails enforceable as policy (admission, RBAC, SCP); per-entity separation; auditable change |
| Operational burden | 15% | Upgrade, patching and capacity work the bank must staff 24x7 |
| Portability | 15% | How much packaging, routing, identity and deployment survives a runtime move |
| Cost profile | 10% | Baseline versus burst economics, including idle recovery capacity |

## Platform behavior on AWS

| Platform | AWS behavior that drives the decision | Main trade-off |
|---|---|---|
| **EKS (managed node groups)** | AWS operates a multi-AZ Kubernetes control plane; the bank owns nodes, add-ons, admission policy and upgrades [S2]. Pod Identity gives per-service-account IAM [S3]. Standard Kubernetes and Gateway API resources let central teams enforce guardrails as admission policy while product teams self-serve in namespaces | Highest operating burden: version skew, add-on compatibility, node lifecycle and Kong/KIC upgrades are bank-owned |
| **EKS on Fargate** | Per-pod isolated capacity with no node management, but no DaemonSets, privileged pods or host networking [S32] | Removes node patching for stateless pods; cannot host Kong data-plane or DaemonSet-based security agents in the same way; per-pod cost higher at steady load |
| **ECS (EC2 or Fargate)** | AWS-native scheduler with task definitions and services; no control-plane version to upgrade [S15]. Direct ALB, IAM task-role and CloudWatch integration | Simpler to run; deployment descriptors, service discovery and guardrails become AWS-specific and move from admission policy to IAM/SCP and pipeline checks |
| **Lambda** | Event-driven per-request scaling; asynchronous invocations retry automatically; concurrency, duration and payload limits depend on invocation mode [S16] | Strong for bursty bounded handlers; automatic retries and connection fan-out to Aurora conflict with strict idempotency and connection budgets unless explicitly designed |
| **EC2 (Auto Scaling groups)** | Full host and OS control; supports vendor software requiring specific kernels, agents or licensing | Bank owns hardening, AMI pipeline, patching, scaling and failover logic; slowest path to uniform guardrails |

## Representative components

Scores are design-review judgements (1 poor – 5 strong) weighted by the criteria above. They are inputs for the architecture board to calibrate, not measurements; the stated reason is what carries the decision.

| Component | Characteristics | EKS | ECS | Lambda | EC2 | Decision and reason |
|---|---|---|---|---|---|---|
| Payment initiation API | Synchronous, latency-sensitive, idempotency keys, Aurora writer access | **4.3** | 4.1 | 2.6 | 2.9 | **EKS.** Warm capacity in three AZs and in Singapore, connection-budgeted Aurora access and governed Kong routes |
| Payment orchestration / saga | Long-running state transitions, outbox publishing, controlled concurrency | **4.4** | 4.0 | 2.3 | 3.0 | **EKS.** Long-lived workers with graceful drain; Lambda duration limits and retry semantics complicate single business effects |
| Rail adapter (ISO 20022 / partner session) | Persistent sessions, mTLS client certificates, single active submitter for fencing | **4.2** | 3.9 | 1.8 | 3.6 | **EKS** with leader election and fenced single-active submission; EC2 only if a vendor rail agent mandates host control |
| Reconciliation batch | Scheduled, compute-heavy, restartable, off the request path | **4.0** | 3.9 | 3.0 | 2.8 | **EKS Jobs** on a separate interruptible node pool; ECS scheduled tasks would be equally valid |
| Inbound settlement-file ingestion | Event per object, bounded parse, idempotent by file hash | 3.6 | 3.5 | **4.1** | 2.5 | **Lambda permitted:** S3 event → validate → staging/outbox, with reserved concurrency, RDS Proxy [S21] and idempotent file keys |
| Notification / audit event fan-out | Bursty, stateless, at-least-once acceptable | 3.5 | 3.4 | **4.2** | 2.2 | **Lambda permitted** for non-financial side effects; never a system of record |
| Operational automation (rotation, tagging, guardrail remediation) | Infrequent, AWS-API-centric | 2.8 | 2.9 | **4.5** | 2.0 | **Lambda**, platform-owned, no payment-data access |
| Vendor fraud/screening agent | Vendor-certified OS image and host agent | 2.5 | 2.4 | 1.2 | **4.0** | **EC2 transitional exception** with owner, hardening baseline and retirement gate in migration wave 5 |

**Outcome.** EKS is the default for payment-path services because the critical components are long-running, connection-heavy and need uniform guardrails, fencing and pre-provisioned recovery. Lambda is approved for bounded, idempotent, off-critical-path handlers. EC2 is a time-limited exception. ECS scores within roughly 0.2–0.4 of EKS on most components and is the documented fallback if the Kubernetes operating cost is not justified (see [ADR-001](../adr/ADR-001-EKS-Platform-Decision.md) review triggers). Fargate on EKS is permitted for stateless application pods where DaemonSet-based controls have Fargate-compatible equivalents.

Kong runs on EKS but is platform-owned. Applications package only their workloads and allowed routes, not private Kong administration or duplicate gateway installations. Terraform application infrastructure provisions stateful dependencies; an application's Helm release must never be able to delete its ledger.

## Portability comes from design, not a platform label

| Boundary | Evidence to create | Remaining coupling |
|---|---|---|
| Runtime | Run the same OCI image with standard Kubernetes resources | Scheduling, identity and ingress integrations |
| Packaging | Thin platform overlays and pinned Helm dependencies | Kong CRDs/plugins, service annotations and storage classes |
| APIs | Versioned OpenAPI/event schemas and contract tests | Identity provider integration and edge policies |
| Messaging | Adapter interfaces, durable outbox, idempotent consumption | SQS delivery, ordering and DLQ semantics |
| Data | PostgreSQL-compatible schema and rehearsed export/import | Aurora replication, extensions, operations and performance |
| Identity | Services use the SDK default credential chain only; no AWS-specific credential code | Pod Identity associations and IAM policy model |
| Observability | OpenTelemetry instrumentation | CloudWatch queries, dashboards and operational tooling |
| Automation | Terraform module interfaces and isolated state | AWS-specific provider resources; Terraform is not cloud-agnostic infrastructure |

The same boundaries make the ECS fallback cheap: images, APIs, outbox, schema and telemetry carry over unchanged; only packaging, routing and identity bindings change. That is the practical portability test — the cost of moving between two runtimes is visible and bounded before any wider move is contemplated.

Gateway API HTTPRoutes reduce some routing coupling, but Kong-specific policies still require translation. Keep payment rules and business authorization in services, not proprietary gateway plugins.

Demonstrate portability by moving one representative service to a separate conformant Kubernetes environment with alternate infrastructure adapters, recording the changes, elapsed effort and correctness results. Do not add a second cloud to this target architecture just to claim portability.

AWS sources: EKS [S2-S3], Fargate [S32], ECS [S15], Lambda [S16], RDS Proxy [S21] in the [evidence register](../appendix/provider-native-evidence.md). The [ADR](../adr/ADR-001-EKS-Platform-Decision.md) records the decision, rejected alternatives, risks and review triggers.
