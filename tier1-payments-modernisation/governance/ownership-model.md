# Ownership model

**Status: design draft; not implemented.** This is the proposed accountability model, not evidence of deployed controls or tested recovery. The [provider-native evidence register](../appendix/provider-native-evidence.md) contains product documentation sources; bank-specific approvals and operational evidence remain to be attached. Citations do not prove deployed readiness.

## Scope and boundaries

- **AWS only:** Malaysia `ap-southeast-5` is primary (P); Singapore `ap-southeast-1` is recovery (R). Cross-border approval is user-confirmed as granted; its evidence reference is pending and has not been regulator-verified.
- `entity-a-prod` and `entity-b-prod` are separate workload accounts, each with a separate EKS cluster in each region. Separate entity recovery accounts hold immutable backups and cleanroom recovery, **not** the live Aurora Global Database topology.
- Security, log, network and tooling accounts are separate, with explicit residency controls for logs, backups, state, artifacts and administrative access. Foundation owns account guardrails; Security owns policy and evidence requirements ([S1](../appendix/provider-native-evidence.md)).
- The [context](../diagrams/context-diagram.md), [logical architecture](../diagrams/logical-architecture.md) and [deployment architecture](../diagrams/deployment-architecture.md) describe these boundaries. The paper's [threat-control matrix](../architecture-paper/06-threat-control-model.md) remains authoritative; this document does not duplicate it.

## Exactly three delivery layers

| Layer | Scope and accountable owner | Published artifacts and handoff |
|---|---|---|
| 1. Foundation | Platform: accounts, VPC/network integration, EKS nodes/controllers, and platform Kubernetes/Kong releases, lifecycle and policies. Network engineers own network implementation within this layer; Security owns guardrail policy. | Approved Terraform plans/state outputs and versioned platform Helm/configuration releases; publish cluster, network, Gateway and policy contracts to layers 2 and 3. |
| 2. Application infrastructure | Application: Terraform for Aurora, SQS, S3, IAM, secret metadata and alarms. Data engineers implement database topology, backup and recovery configuration; Security reviews access. | Approved Terraform plans and versioned non-secret endpoint, identity and resource contracts consumed by layer 3. |
| 3. Application code | Application: immutable images, Helm workloads/services, approved namespaced HTTPRoutes and database migration logic. Data reviews migration safety; Operations controls production release execution. | Image and chart digests, signatures, scans, provenance, migration compatibility evidence and an approved promotion manifest. |

The **platform Kubernetes/Kong release pipeline is a subpipeline of foundation**, never a fourth layer. Team responsibilities within a layer do not create extra delivery layers. Promotions follow [deployment governance](deployment-governance.md) and the [pipeline diagram](../diagrams/deployment-pipelines.md).

Product/application teams own end-to-end application SLOs, including the impact of their dependencies. Platform owns published EKS/Kong service objectives and platform incident response; delegating release execution to Operations does not transfer product SLO accountability.

### Single resource owner

Terraform provisions AWS infrastructure; Helm owns Kubernetes workloads. Keep Terraform state split by entity, environment and lifecycle, with one state/resource owner and no duplicate AWS declarations. Terraform must not separately manage Helm-owned workloads. Before any ownership transfer, record resource IDs, relinquish the previous reconciler/state binding without destroying the resource, establish the new owner, and prove a clean plan/reconciliation.

The AWS Load Balancer Controller owns the ALB fronting Kong and its controller-managed AWS resources; Terraform owns surrounding network/security foundations, not duplicate ALBs or controller-created rules. Foundation installs/configures that controller. KIC owns the application-routing reconciliation into Kong; no two controllers may own the same routing object. Explicitly record any IaC-to-controller handoff and rollback procedure ([S2](../appendix/provider-native-evidence.md), [S10](../appendix/provider-native-evidence.md)).

Platform provides workload identity integration; Application defines least-privilege workload IAM in layer 2. Security reviews trust boundaries; credentials are not embedded in images or charts ([S3](../appendix/provider-native-evidence.md)).

## Platform product and application contract

Self-hosted Kong is a Platform-owned product; application teams are its consumers, **not automatically Kong Consumer objects**. The proposal is one DB-less gateway per entity per region, with KIC and at least three gateway replicas spread across availability zones. The private Kong Admin API is accessible only to KIC and platform-privileged administration, not application teams.

Platform owns GatewayClass, Gateway, `allowedRoutes`, baseline authentication/plugins, Kong upgrades and admission policy. Applications may submit approved namespace-scoped HTTPRoutes only; they receive neither global plugin nor Admin API privileges. North-south traffic is ALB + WAF -> Kong -> ClusterIP applications; hybrid ingress uses a private internal ALB. There is no Amazon API Gateway, Konnect or external Kong control plane. Security groups, network policies and admission controls prevent public NodePort/LoadBalancer bypass. Applications remain responsible for service TLS/mTLS integration, business authorization and idempotency.

DB-less Kong has no configuration database: versioned Git/Kubernetes desired state is the recovery source, with no `decK sync`. Plugin compatibility, licensing, authentication and rate-limit behavior require assessment; local counters must not be represented as a globally enforced limit ([S9](../appendix/provider-native-evidence.md), [S10](../appendix/provider-native-evidence.md)).

## Consolidated RACI

Roles: **SEC** Security/compliance; **NET** Network; **PLT** Platform/foundation; **APP** Application/product engineering; **DATA** Database/data engineering; **OPS** Operations/incident and release management; **BUS** Business/service risk owner. Each role must have named primary/deputy contacts per entity before implementation. OPS and BUS are separate responsibilities, not interchangeable approvals.

**A** = sole accountable role; **R** = executes; **C** = consulted; **I** = informed; **A/R** = accountable and executing. Each row has exactly one A, including A/R. Consulted control owners can withhold mandatory gate clearance; accountability does not override policy.

| Decision or activity | SEC | NET | PLT | APP | DATA | OPS | BUS |
|---|---|---|---|---|---|---|---|
| Account guardrails, residency policy and evidence custody | A/R | C | R | I | C | C | C |
| Cross-border evidence acceptance and residual business risk | R | C | C | I | C | C | A |
| Foundation delivery and account/EKS lifecycle | C | R | A/R | C | I | R | I |
| Hybrid connectivity, segmentation and firewall paths | C | A/R | R | C | I | R | I |
| Foundation Kubernetes/Kong subpipeline and route guardrails | C | C | A/R | C | I | R | I |
| Application-infrastructure delivery and resource contracts | C | C | R | A/R | R | C | I |
| Database topology, backups and data recovery readiness | C | I | C | R | A/R | R | C |
| Code, HTTPRoutes, authorization and idempotency | C | I | C | A/R | C | R | I |
| Migration logic and expand/contract compatibility | I | I | C | A/R | R | C | I |
| CI identity, artifact trust and privileged-access policy | A/R | I | R | R | C | R | I |
| Production promotion, canary and operational rollback | C | C | R | R | C | A/R | C |
| Regional recovery authorization and uncertain-payment gate | C | C | R | R | R | R | A |
| Fence, promote, reconcile and switch recovery traffic | C | R | R | R | R | A/R | C |
| Cyber cleanroom integrity clearance | A/R | C | R | R | R | R | C |
| Cyber business-service resumption authorization | R | C | R | R | R | R | A |
| Exercises, measured recovery evidence and runbook currency | C | R | R | R | R | A/R | C |

## Data, network and recovery duties

DATA owns Aurora writer/readers with multi-AZ storage: the active regional cluster has a single writer, while R is a read-only global secondary until promotion. There is only one active global write region. P -> R replication is asynchronous: near-zero regional RPO is a goal, not guaranteed zero loss. The supplied matrix lists Aurora PostgreSQL Global Database in both regions; final engine/version, feature and capacity checks remain open ([S4](../appendix/provider-native-evidence.md), [S5](../appendix/provider-native-evidence.md), [S6](../appendix/provider-native-evidence.md)).

APP owns region-local SQS handling and replay from a surviving durable ledger/outbox, not queue replication. External payment submissions require idempotency and querying uncertain outcomes before retry. DATA and APP jointly assess gaps in asynchronously replicated records before BUS authorizes safe resumption ([S12](../appendix/provider-native-evidence.md)).

NET owns diverse Direct Connect routes with VPN fallback from on-premises to **both countries**, TGW segmentation without default cross-entity routes, and symmetric Network Firewall paths with endpoints in each AZ. Direct Connect is not encrypted by itself: use TLS/mTLS or engineered IPsec. Firewall inspection covers routed paths only and does not automatically decrypt TLS ([S13](../appendix/provider-native-evidence.md), [S14](../appendix/provider-native-evidence.md)); see [hybrid connectivity](../diagrams/hybrid-connectivity.md).

OPS maintains recovery readiness across preprovisioned EKS, Kong/routes, keys/secrets, images, networks and databases. Before promotion or traffic switching, fence **both old submitters and the old writer**; DNS changes are not fencing. If fencing cannot be established, do not promote into a possible split-brain state. BUS owns the uncertain-commit decision gate, not permission to bypass fencing.

The draft RTO is **<=30 minutes from disruption to safe critical journeys**, unmeasured. Zero loss is expected for an AZ failure within the regional HA design; regional uncertain commits require reconciliation. Cyber restore from entity-specific immutable backups/cleanrooms has a separate, unmeasured RTO and security clearance ([S11](../appendix/provider-native-evidence.md)). See [DR architecture](../diagrams/dr-architecture.md) and the recovery gates in [deployment governance](deployment-governance.md).
