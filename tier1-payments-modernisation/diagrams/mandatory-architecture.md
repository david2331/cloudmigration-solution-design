# Mandatory architecture diagram

**Selected cloud: AWS.** P = Malaysia `ap-southeast-5`; R = Singapore `ap-southeast-1`. One legal entity is shown; every other entity has an identical, separate workload account, recovery account, EKS clusters, Aurora clusters and keys.

![Mandatory AWS architecture: external trust boundary, AWS Organization, network and security accounts, entity workload account with Malaysia primary and Singapore recovery regions, three AZ failure domains, ingress, Kong, payment services, Aurora, regional services and isolated recovery account](mandatory-architecture.png)

Editable source: [mandatory-architecture.drawio](mandatory-architecture.drawio) (open in draw.io / diagrams.net). Icons use the official AWS Architecture Icons set in draw.io (`mxgraph.aws4`); Kubernetes workloads use the Kubernetes icon set.

## How the diagram meets the brief

| Required element | Where it is shown |
|---|---|
| Trust boundaries | External boundary (customers, on-premises, rails, GitHub); AWS Organization; separate network, security/log/tooling, entity workload and entity recovery accounts; VPC; public ingress subnets; EKS node groups |
| Traffic flow | Route 53 + ARC → WAF → internet ALB → Kong → payment services → Aurora writer; on-premises → Direct Connect/VPN → Transit Gateway → Network Firewall → internal ALB → Kong; single active submitter → payment rails; GitHub OIDC → STS deploy roles |
| Failure domains | Pod, EKS node group, AZ-a/b/c within P, P versus R regions, and account (workload versus recovery) |
| Security controls | Shield, WAF, Network Firewall, security groups and NetworkPolicy, Kong authentication, KMS, Secrets Manager, Pod Identity, GuardDuty, Security Hub, CloudTrail, Config, Backup Vault Lock, Object Lock log archive; numbered control points 1-4 |
| Key service names | All AWS services are labelled with their service names alongside the official icon |

The legend distinguishes synchronous payment flow, hybrid private paths, asynchronous replication, deployment, backup copies, fenced recovery paths and security telemetry. The two side panels state the controls at each numbered point and the recovery objectives per failure domain. DNS or ARC routing changes are explicitly shown as traffic switches, not fencing.

## Related diagrams

[Context](context-diagram.md) | [Logical architecture](logical-architecture.md) | [Deployment topology and regional cell](deployment-architecture.md) | [DR architecture](dr-architecture.md) | [Hybrid connectivity](hybrid-connectivity.md) | [Deployment pipelines](deployment-pipelines.md)

[Provider-native evidence](../appendix/provider-native-evidence.md): **S1** Control Tower; **S2-S3** EKS networking and Pod Identity; **S4-S6** Aurora HA, global recovery and region support; **S9-S10** Kong DB-less/KIC; **S11** Backup Vault Lock; **S13-S14** Direct Connect and Transit Gateway; **S18** Route 53 ARC; **S28** S3 Object Lock. ARC availability in `ap-southeast-5` must be confirmed against **S33**.
