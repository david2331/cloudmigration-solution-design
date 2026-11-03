# Deployment architecture

**Status: design draft; not implemented or capacity-tested.** P = Malaysia `ap-southeast-5`; R = Singapore `ap-southeast-1`. AZ-a/b/c below are logical slots: map actual AZ IDs and supported capacity per account, rather than assuming identical AZ names across accounts.

## Account and regional topology

```mermaid
flowchart TB
  subgraph org["AWS organization  -  isolated account boundaries"]
    subgraph a["entity-a-prod workload account"]
      ap["P: entity A EKS + DB-less Kong<br/>VPC across 3 AZs<br/>Aurora primary / local SQS / S3"]
      ar["R: entity A EKS + DB-less Kong<br/>VPC across 3 AZs; submitters fenced<br/>Aurora secondary / local SQS / S3"]
      ap -->|"Aurora Global Database  -  asynchronous"| ar
    end
    subgraph b["entity-b-prod workload account"]
      bp["P: entity B EKS + DB-less Kong<br/>VPC across 3 AZs<br/>Aurora primary / local SQS / S3"]
      br["R: entity B EKS + DB-less Kong<br/>VPC across 3 AZs; submitters fenced<br/>Aurora secondary / local SQS / S3"]
      bp -->|"Aurora Global Database  -  asynchronous"| br
    end
    subgraph ra["Entity A recovery account  -  isolated custody"]
      ba["Immutable AWS Backup vault / Vault Lock<br/>Isolated cleanroom VPC"]
    end
    subgraph rb["Entity B recovery account  -  isolated custody"]
      bb["Immutable AWS Backup vault / Vault Lock<br/>Isolated cleanroom VPC"]
    end
    network["Network account(s)<br/>Regional TGW / DX / VPN / Network Firewall"]
    sec["Security account<br/>GuardDuty / Security Hub"]
    log["Log account<br/>Regional CloudTrail / log stores + KMS"]
    tools["Tooling account<br/>ECR / isolated runners / scoped STS deployment"]
  end
  network -->|"Segmented entity A attachments"| a
  network -->|"Segmented entity B attachments"| b
  tools -->|"Approved role + EKS RBAC"| a
  tools -->|"Approved role + EKS RBAC"| b
  a -->|"Approved backup copies; no live replication here"| ba
  b -->|"Approved backup copies; no live replication here"| bb
  a -->|"Region-controlled findings"| sec
  b -->|"Region-controlled findings"| sec
  a -->|"Region-controlled audit logs"| log
  b -->|"Region-controlled audit logs"| log
```

No default cross-entity connectivity exists. Security, log, network and tooling are distinct accounts, not a combined shared workload account. Live global database members are in the entity workload account in both regions. Recovery accounts are for backup/cleanroom isolation, **not** live Aurora secondaries.

## Regional cell: repeat independently for each entity and region

The detailed cell below depicts an active region. In R before promotion, substitute Aurora secondary readers for the writer and keep payment submitters disabled; all ingress, EKS, Kong and supporting resources are preprovisioned.

```mermaid
flowchart TB
  clients["Internet clients"]
  hybrid["Hybrid clients via regional TGW<br/>Private routes only"]
  subgraph account["One entity workload account  -  one region"]
    cp["AWS-managed EKS control plane<br/>Outside customer VPC; private API access"]
    subgraph vpc["Customer VPC  -  SG / subnet / NetworkPolicy boundaries"]
      subgraph ingress["Ingress subnets spanning AZ-a / AZ-b / AZ-c"]
        pub["Internet-facing ALB + AWS WAF<br/>Owned by AWS Load Balancer Controller"]
        priv["Private internal ALB<br/>Owned by AWS Load Balancer Controller"]
      end
      subgraph za["AZ-a  -  private compute and DB subnets"]
        ka["Kong replica + payment pods<br/>ClusterIP services"]
        da["Aurora writer (active region)"]
      end
      subgraph zb["AZ-b  -  private compute and DB subnets"]
        kb["Kong replica + payment pods<br/>ClusterIP services"]
        db["Aurora reader / failover candidate"]
      end
      subgraph zc["AZ-c  -  private compute and DB subnets"]
        kc["Kong replica + payment pods<br/>ClusterIP services"]
        dc["Aurora reader / failover candidate"]
      end
      controllers["Platform controllers spread across AZs<br/>KIC + AWS Load Balancer Controller"]
      storage["Aurora regional cluster storage<br/>Replicated across all three AZs"]
      endpoints["Private VPC endpoints / restricted SGs<br/>S3, ECR, SQS, Secrets Manager, STS as supported"]
      admin["Private Kong Admin API<br/>KIC and authorized platform operators only"]
    end
    services["Regional AWS services<br/>SQS / S3 / ECR / Secrets Manager / KMS"]
  end
  clients -->|"HTTPS; WAF inspection at ALB"| pub
  hybrid -->|"HTTPS; internal DNS"| priv
  pub -->|"TLS to Kong targets"| ka
  pub -->|"TLS to Kong targets"| kb
  pub -->|"TLS to Kong targets"| kc
  priv -->|"TLS to Kong targets"| ka
  priv -->|"TLS to Kong targets"| kb
  priv -->|"TLS to Kong targets"| kc
  cp -.->|"Managed API / node connectivity"| ka
  cp -.->|"Managed API / node connectivity"| kb
  cp -.->|"Managed API / node connectivity"| kc
  controllers -.->|"Private configuration path"| admin
  admin -.-> ka
  admin -.-> kb
  admin -.-> kc
  ka -->|"App TLS via cluster writer endpoint"| da
  kb -->|"App TLS via cluster writer endpoint"| da
  kc -->|"App TLS via cluster writer endpoint"| da
  da --- storage
  db --- storage
  dc --- storage
  ka --> endpoints
  kb --> endpoints
  kc --> endpoints
  endpoints -->|"IAM / endpoint policy / KMS"| services
```

## Availability and implementation constraints

- Kong is a **proposed per-entity, per-region DB-less deployment with KIC**, at least three ready replicas spread across AZs. Enforce topology spread/anti-affinity, disruption budgets and tested spare capacity for an AZ loss; replica count alone does not prove resilience. Payment pods and controllers also require appropriate spreading and recovery capacity.
- Platform owns Gateway/GatewayClass, `allowedRoutes`, baseline plugins/authentication and private Kong administration. Applications own approved namespaced HTTPRoutes. Dedicated fronting resources belong to the AWS Load Balancer Controller; application route reconciliation belongs to KIC. No arbitrary public NodePort/LoadBalancer services, global plugin overrides or application admin access.
- The Kong -> application hop is TLS/mTLS, even where combined in the diagram. SGs, NetworkPolicy and admission prevent bypass. No Amazon API Gateway or Konnect is involved. DB-less has no configuration DB and uses Git/Kubernetes desired state, not decK sync.
- Aurora has regional storage replicated across AZs, a single active regional writer and failover readers. Aurora Global Database adds **asynchronous** cross-region replication; expected AZ-failure zero loss is not a guaranteed regional zero RPO. There is one active global write region; a promoted secondary becomes its new regional writer.
- The existing AWS matrix lists Aurora PostgreSQL Global Database support in both P and R. Final engine version, features, instance classes, quotas and capacity must be checked before approval. Validate all required EKS, controller, endpoint, backup and network features in each region as well.
- Terraform owns AWS provisioning; Helm owns Kubernetes workloads, with explicit controller-owned AWS-resource exceptions such as ALBs. Never declare the same resource in two states or under competing reconcilers.
- Preposition R images/chart digests, routes, keys, certificates, secrets, DNS, network and database capacity. Do not rely on cross-region KMS keys or secret values becoming available automatically.
- Residency controls apply separately to logs, findings, state, artifacts and backup copies. Cross-border approval is user-confirmed granted; evidence reference remains pending, not regulator-verified.

[Logical flow and control ownership](logical-architecture.md) | [DR architecture](dr-architecture.md) | [Hybrid networking](hybrid-connectivity.md) | [Delivery governance](../governance/deployment-governance.md).

[Provider-native evidence](../appendix/provider-native-evidence.md): **S1** Control Tower; **S2-S3** EKS networking/Pod Identity; **S4** Aurora HA; **S5** global recovery; **S6** region support; **S9-S10** Kong DB-less/KIC; **S11** Backup Vault Lock. These references do not establish deployed readiness.
