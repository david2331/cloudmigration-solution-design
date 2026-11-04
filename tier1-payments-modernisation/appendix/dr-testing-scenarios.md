# DR exercise catalogue

**Design acceptance exercises; no runs or results are claimed. P: Malaysia `ap-southeast-5`; R: Singapore `ap-southeast-1`.**

| Scenario | Injected condition | Required observations and acceptance |
|---|---|---|
| Kong replica/node loss | Kill a gateway pod/node during safe load rehearsal | Healthy replicas serve; draining/retries do not duplicate payments |
| AZ failure | Remove an AZ's compute/path capacity | Remaining Kong/app/database capacity supports agreed critical SLO; committed data survives |
| KIC/config failure | Block reconciliation or submit invalid routes | Fail closed for unauthorized configuration; existing approved routes remain usable; alert and recover |
| Kong cold restart | Restart all gateway pods in controlled environment with Kubernetes/config source unavailable | No unconfigured instance marked ready; document exact restore dependency and time |
| Aurora writer failure | Fail over regional writer under concurrent idempotent requests | Reconnect to new writer; ledger invariants preserved and ambiguous outcomes resolved |
| Hybrid path failure | Lose a DX path, then all DX paths | Diverse/VPN route operates with required encryption, segmentation and priority capacity |
| Replication lag | Create safe controlled secondary lag | Measure exposure and effect of chosen RPO controls; alarm/write-protection behavior matches approved tolerance |
| Malaysia regional loss | Make primary application/data paths unavailable | Promote only with authority established; Singapore Kong, dependencies and journeys usable within 30 minutes from disruption |
| Partition with old submitter alive | Isolate control paths while Malaysia can still reach rail | No competing submission authorities; fail closed if fencing cannot be established |
| Queue recovery | Lose regional processing availability after outbox commit | Replay surviving outbox; duplicates harmless; lost database tail explicitly reported |
| External timeout | Rail commits but response is lost | Status query/idempotency resolves result, or payment quarantined; no blind duplicate resubmission |
| GitHub outage during DR | Remove CI access | Authorized recovery uses existing resources, independent identities and prepositioned artifacts |
| Backup/cyber-recovery | Simulate compromised account and restore clean point in recovery account | Keys usable, trusted stack restored, ledger reconciled; separate cyber objectives measured |
| Failback | Rebuild/resynchronise Malaysia | Planned switchover with controlled fencing, no dual writers and no unexpected data loss |

Before each exercise, approve scope, synthetic data, safety limits, stop conditions, observer roles and rollback. Avoid uncontrolled disruption of production payments.

Record disruption/detection/declaration/promotion/fencing/service-restoration timestamps, eligible journey results, replication lag, missing transaction count and identifiers, duplicates, reconciliation breaks and operator actions. RTO starts at disruption, not declaration. Compare actual RPO to the approved numeric threshold, not "looked close to zero".

Proposed cadence: component exercises regularly and after material releases, regional recovery quarterly and after topology changes, cyber-recovery on an approved risk-based schedule. Failed integrity or fencing exercises block relevant migration expansion until remediation is demonstrated.

See [data and DR](../architecture-paper/05-data-and-dr.md), [risk register](../architecture-paper/08-risk-register.md) and [DR diagram](../diagrams/dr-architecture.md).
