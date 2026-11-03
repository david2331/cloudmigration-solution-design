# Cost transparency and capacity economics

**AWS; Malaysia primary and Singapore recovery. No price estimate is asserted without workload, region, retention and capacity inputs.**

| Cost driver | Design implication | Allocation/optimisation |
|---|---|---|
| EKS and worker capacity | Per-entity clusters in two regions create baseline cost | Allocate directly by entity; retain funded AZ-loss and DR headroom |
| Self-hosted Kong | Replicas, controllers, observability, engineering and possible enterprise/support license | Platform service cost split by agreed baseline plus usage; include both regions |
| Aurora | Writer/readers, storage/I/O, global replication and backup | Compare applicable provisioned/I/O pricing against measured workload; never remove required replicas solely to lower cost |
| Network | DX, VPN, TGW, firewall, cross-AZ/region traffic, NAT/endpoints | Model actual traffic paths; use endpoints where security and total cost justify them |
| Delivery | GitHub plan/minutes, private runners, ECR storage/transfer, scanning and provenance | Ephemeral runners and retention policies; no payloads in CI artifacts |
| Recovery | Ready Singapore capacity, isolated vaults, immutable retention and exercises | Explicit resilience budget, not hidden operational overhead |
| Telemetry | CloudWatch ingestion/storage/query, audit retention and optional managed dashboards | Redact/summarise safely; retain required audit evidence and useful payment indicators |
| Operations | Kubernetes/Kong upgrades, security response, training and on-call | Compare total cost with ECS alternative, not just compute price |

Use account-level attribution and mandatory entity, product, environment, owner and cost-centre tags where supported. Track untaggable/shared resources through allocation rules. AWS billing exports, budgets and anomaly monitoring provide visibility; business owners approve material deviations.

**Unit cost = allocated application + platform + security/network + recovery + operational cost / completed payments**, with the measurement period and allocation policy stated. Show rejected/failed payment cost separately rather than hiding it.

Size normal peak, AZ-loss peak and regional recovery scenarios. Reserve critical baseline capacity and appropriate database connections; noncritical batch workloads may use interruptible capacity if restartable. Right-size from measurement and consider commitments only after stable demand; do not trade away hard resilience requirements without approval.

Vault Lock compliance retention becomes irreversible after its grace period while recovery points exist. Review lifecycle and legal retention before locking; accidental indefinite retention can produce persistent cost [S11 in the evidence register](provider-native-evidence.md).
