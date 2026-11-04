# ADR-001: EKS and Helm for payment applications

**Selected cloud: AWS. Task 7 (10%). Status: proposed architecture; EKS/Helm is the bank platform standard.**

An **ADR (Architecture Decision Record)** captures a significant decision, why it was made, alternatives rejected, consequences, risks and review triggers. It preserves reasoning so later teams can revisit a decision without reconstructing the original debate.

The challenge response below is approximately two pages of narrative; final pagination depends on export formatting. The supporting compact records after it are separate from that two-page-equivalent response.

## Challenge response

### Context and owners

The bank's Tier 1 payments platform must support multiple legal entities, hybrid dependencies, 99.99% critical-journey availability, 30-minute regional recovery and near-zero RPO for committed payments. Malaysia (`ap-southeast-5`) is primary and Singapore (`ap-southeast-1`) is recovery. Cross-border approval is granted per bank confirmation (assumption C05); the formal evidence reference remains to be attached.

Teams disagree about containers, serverless operations and portability. The bank's platform standard is Kubernetes and Helm, with Terraform infrastructure, GitHub Actions delivery and self-hosted Kong operated by the platform team. This ADR tests whether that runtime choice is defensible on its merits against ECS, Lambda and EC2, without claiming it resolves data durability or every operational problem.

The architecture authority is the decision custodian. Platform and application service owners are accountable for their supported capabilities, with mandatory security, data, operations and business-risk concurrence before production approval.

### Decision and scope

Use Amazon EKS for payment APIs, orchestration, rail adapters and reconciliation workloads. Deploy separate production accounts per legal entity and separate clusters per region. Use OCI images and Helm charts, promoting immutable versions through GitHub Actions.

Keep exactly three delivery layers: foundation infrastructure, application infrastructure and application code. Platform-owned EKS/Kong Helm releases are a foundation subpipeline, not a fourth ownership layer. Terraform provisions AWS dependencies; controller-created resources have a documented single owner. Product teams deploy application workloads and approved gateway routes without cluster administration.

Run self-hosted Kong independently per entity and region. Platform owns lifecycle, security policy and administration; applications consume governed routing interfaces and remain responsible for business authorization. DB-less Kong with KIC is proposed, subject to plugin, licensing, authentication and compatibility assessment. It is not a commitment to every feature of a particular Kong edition.

Keep authoritative ledger data in managed AWS data services, not application pods. Platform choice does not approve the separate Aurora regional-loss assumptions.

### Rationale

EKS provides a managed Kubernetes control plane while preserving standard container scheduling and deployment interfaces [S2]. Long-running integration services, leader-elected rail submitters and Jobs-based reconciliation map directly onto Kubernetes primitives. A central platform team can offer reusable security, networking and release patterns as admission policy instead of each product assembling them independently.

Per-entity clusters limit gateway and workload blast radius. Regional application replicas provide availability while a single authoritative ledger writer avoids unresolved active-active payment conflicts. GitHub OIDC and separated deployment roles limit release authority. None of these controls eliminates the need for application idempotency, reconciliation or disaster fencing.

Kubernetes portability is useful but partial. OCI images, standard resources and API contracts preserve application structure; AWS identity, Aurora, SQS, Kong policies and recovery operations still require adaptation. The desired outcome is a known switching cost, not a zero-effort platform move.

### Rejected alternatives

**Amazon ECS** is a credible, often simpler container platform with no control-plane version to upgrade [S15]. It is not rejected for being less secure or less available. It is rejected as the primary runtime for three workload reasons. First, central guardrails: Kubernetes admission policy and Gateway API let the platform team enforce route ownership, image signatures and pod security as declarative policy that product teams self-serve within; on ECS the same rules move into IAM, SCPs and pipeline checks, which are harder to make uniform across many teams and entities. Second, the gateway: the selected Kong Ingress Controller reconciles from Kubernetes resources, so ECS would need a different Kong configuration model and a second release path. Third, workload mix: rail adapters need leader election and fenced single-active submitters, and reconciliation needs Jobs on separate interruptible pools — both native Kubernetes patterns. The weighted assessment in [Task 3](../architecture-paper/04-application-platform-decision.md) scores ECS within 0.2–0.4 of EKS, so the margin is real but narrow; ECS is the documented fallback if the Kubernetes operating cost is not justified.

**AWS Lambda** suits bounded event handlers and automation. Its execution-mode limits, concurrency, retries and downstream connections need workload-specific design. It is not the dominant runtime for the desired uniform container model and long-lived adapters, but exceptions are allowed. Regulation alone is not a reason to reject serverless.

**Direct EC2 deployment** accommodates vendor requirements and host-level control but distributes more patching, process lifecycle and release work to teams. Restrict it to documented transitional exceptions with retirement triggers.

**Self-managed Kubernetes** preserves Kubernetes interfaces but adds control-plane operation and recovery responsibilities without sufficient business benefit for this AWS target. It is rejected in favour of EKS.

### Consequences and controls

The bank must fund Kubernetes/Kong upgrades, compatibility testing, node lifecycle, capacity, admission policy and staffed incident support. Three replicas alone do not prove AZ-loss resilience: topology, spare capacity and dependencies must all support the journey SLO. EKS's private API also requires connected deployment runners.

Platform operates Kong as a product, not an unrestricted shared administration surface. Applications receive namespace-scoped routes and approved policy attachment, not global plugin or Admin API privileges. Gateway configurations and artifacts must be ready in Singapore before a disaster. Edition-specific features and local versus global rate limiting remain explicit trade-offs.

Helm rollback cannot reverse arbitrary database changes or committed payments. Use expand-and-contract schema evolution and controlled compensating entries. Terraform state and saved plans require encryption, access separation and locking; multiple reconcilers must not manage the same resource.

Regional recovery needs exclusive writer and rail-submission authority, not merely a DNS update. Aurora Global Database replication is asynchronous. If zero acknowledged regional commit loss is required, redesign commitment durability; do not use EKS selection as evidence that this requirement is met.

### Risks, review triggers and approval

Review this decision after Kubernetes/Kong incidents repeatedly consume error budgets, upgrades miss support windows, team capacity becomes inadequate, entity expansion changes economics, or a portability exercise exposes unacceptable coupling. Also review material Kong plugin/licensing changes and measured total-cost differences against ECS.

Approve production use only after ownership, security, capacity and operational evidence are accepted. The quantified RPO and fencing gates remain independently blocking. Provider evidence: EKS [S2], Kong [S9-S10], ECS [S15], Lambda [S16], GitHub OIDC [S7] and Aurora recovery [S5] in the [source register](../appendix/provider-native-evidence.md).

## Supporting compact decision records

| Record / status | Decision and reason | Rejected alternative / consequence | Review trigger |
|---|---|---|---|
| D02: Entity isolation / confirmed direction | Separate production accounts and regional EKS clusters per legal entity; central ownership with local data boundaries | Shared cross-entity cluster reduces baseline cost but increases policy/blast-radius risk | Entity growth, regulatory scope or cost change |
| D03: Terraform and three layers / confirmed tools, proposed controls | Separate foundation, application-infrastructure and application-code pipelines/state authority; native S3 locking | Monolithic state/role couples unrelated changes and broadens authority; separation adds interface management | Ownership changes, state recovery or deployment incidents |
| D04: Kong platform service / ownership confirmed, topology proposed | Per-entity/region self-hosted Kong; DB-less/KIC avoids a gateway DB and offers governed Kubernetes routes | App-owned gateways fragment controls; one shared gateway spans entities; database-backed topology may be needed for incompatible plugins | Plugin/edition requirements, scale, config recovery or license change |
| D05: Data and DR / conditional proposal | Single-writer Aurora PostgreSQL, regional HA, asynchronous Singapore secondary; compatible managed relational operations | Active-active ledger conflicts rejected; async cannot satisfy strict zero-loss regional commits | Numerical RPO decision, fencing results, regional feature changes |
| D06: Delivery identity / confirmed tool, proposed controls | GitHub Actions OIDC, protected environments, isolated runners and immutable artifact promotion | Stored long-lived keys expand credential exposure; direct human release reduces repeatability | Repository/environment/trust format or runner changes |
| D07: Transactional outbox / proposed | Commit state and outbox atomically; idempotent consumers and external outcome reconciliation | Uncoordinated DB/queue dual writes lose consistency; outbox adds relay and deduplication operations | Throughput, ordering or rail semantic change |
| D08: Recovery custody / proposed | Live DR in entity production account; immutable supported backup copies in isolated recovery account | A live replica alone propagates corruption and shares account-compromise risk | Restore results, key custody, retention or approval scope changes |

Full consequences and controls remain in the [target architecture](../architecture-paper/03-target-architecture.md), [data and DR](../architecture-paper/05-data-and-dr.md), [risk register](../architecture-paper/08-risk-register.md) and [ownership model](../governance/ownership-model.md). Supersede records with explicit rationale rather than silently rewriting an approved historical decision.
