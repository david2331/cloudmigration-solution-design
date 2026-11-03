# Payment platform context

**Status: design draft; not implemented or operationally validated.** AWS is the only runtime cloud. P = Malaysia (`ap-southeast-5`); R = Singapore (`ap-southeast-1`). Cross-border approval is **user-confirmed as granted**; its evidence reference is pending and this is not regulator-verified.

```mermaid
flowchart TB
  public["Customers / approved internet channels"]
  hybrid["On-premises channels and payment operations"]
  rails["External payment / settlement partners"]
  gh["GitHub Actions<br/>External CI/CD trust boundary"]

  subgraph aws["AWS organization  -  account and residency boundaries"]
    subgraph net["Network accounts  -  region-local connectivity"]
      edge["Direct Connect + Site-to-Site VPN<br/>Transit Gateway + AWS Network Firewall"]
    end
    subgraph a["entity-a-prod  -  isolated workload account"]
      ap["P: WAF + ALB -> Kong -> EKS services<br/>Three AZs; Aurora / SQS / S3"]
      ar["R: preprovisioned ALB / Kong / EKS<br/>Three AZs; Aurora secondary; local SQS"]
      ap -->|"Aurora Global Database: asynchronous"| ar
    end
    subgraph b["entity-b-prod  -  isolated workload account"]
      bp["P: WAF + ALB -> Kong -> EKS services<br/>Three AZs; Aurora / SQS / S3"]
      br["R: preprovisioned ALB / Kong / EKS<br/>Three AZs; Aurora secondary; local SQS"]
      bp -->|"Aurora Global Database: asynchronous"| br
    end
    subgraph recovery["Separate entity recovery accounts  -  not live databases"]
      av["Entity A: AWS Backup Vault Lock / cleanroom"]
      bv["Entity B: AWS Backup Vault Lock / cleanroom"]
    end
    subgraph tooling["Tooling accounts  -  controlled deployment trust"]
      deploy["Ephemeral connected runners<br/>AWS STS / scoped IAM roles / ECR"]
    end
    subgraph assurance["Separate security and log accounts"]
      security["AWS CloudTrail / GuardDuty / Security Hub"]
      logs["Region-local encrypted log stores<br/>KMS + restricted retention/export"]
    end
  end

  public -->|"HTTPS / WAF; active P ingress"| ap
  public -->|"HTTPS / WAF; active P ingress"| bp
  hybrid -->|"TLS or mTLS over diverse DX / VPN"| edge
  edge -->|"Private internal ALB; entity A routes"| ap
  edge -->|"Private internal ALB; entity B routes"| bp
  edge -.->|"Prebuilt R connectivity; fenced traffic"| ar
  edge -.->|"Prebuilt R connectivity; fenced traffic"| br
  gh -->|"OIDC: exact audience and subject"| deploy
  deploy -->|"Layer/entity/environment-scoped deployment"| a
  deploy -->|"Layer/entity/environment-scoped deployment"| b
  ap -->|"Approved backup copies; independent custody"| av
  bp -->|"Approved backup copies; independent custody"| bv
  a -->|"Sanitized telemetry / approved regional findings"| assurance
  b -->|"Sanitized telemetry / approved regional findings"| assurance
  ap -->|"Controlled egress; idempotent submission"| rails
  bp -->|"Controlled egress; idempotent submission"| rails
```

## Trust and responsibility

- Workload accounts are separate by entity, **not** by region: each has its own EKS cluster in P and another in R. There are no default cross-entity routes, shared payment databases, or shared Kong instances.
- Recovery accounts hold immutable backups and isolated cleanroom restores. Live Aurora Global Database members remain in the corresponding workload account, not the recovery accounts.
- Security, log, network and tooling accounts are separate from workload accounts and one another. Shared administration does not imply unrestricted data access. Logs, backup copies, artifacts, secrets and telemetry require explicit destination, retention, KMS and residency controls; cross-border approval is not blanket permission to export all data.
- Platform owns self-hosted Kong; product/application teams consume its approved routing capability. "Gateway consumers" does not automatically create Kong Consumer entities. No Amazon API Gateway, Konnect or external Kong control plane is proposed.
- Recovery endpoints are provisioned, but payment writers and external submitters must not become active in both regions. Traffic switching alone cannot enforce this.

## Related design and evidence

[Logical architecture](logical-architecture.md) | [Deployment topology](deployment-architecture.md) | [Hybrid connectivity](hybrid-connectivity.md) | [Recovery](dr-architecture.md) | [Ownership and RACI](../governance/ownership-model.md).

[Provider-native evidence register](../appendix/provider-native-evidence.md): **S1** Control Tower/account governance; **S2** EKS networking; **S5** Aurora global recovery; **S11** Backup Vault Lock; **S13-S14** Direct Connect and Transit Gateway. Source IDs identify required supporting evidence, not proof that this design has been deployed.
