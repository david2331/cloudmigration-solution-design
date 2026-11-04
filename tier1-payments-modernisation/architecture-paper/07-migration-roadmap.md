# Migration roadmap

**Selected cloud: AWS. Task 6 (10%). Malaysia primary; Singapore recovery. Migrate by legal entity and bounded payment cohort, not a single global cutover.**

| Wave | Delivery and coexistence | Exit criteria | Rollback point |
|---|---|---|---|
| 0. Discover and define | Inventory journeys, rails, contracts, data, residency approval scope and legacy authority | Named owners; numerical objectives, approved scope and dependency map | No production change |
| 1. Establish foundation | Terraform accounts/network/EKS, platform Kong/KIC, identity, audit and GitHub Actions; provision both countries | Isolation, gateway policy, hybrid paths, artifacts and operational readiness evidenced | No new payment authority; revert safe configuration changes |
| 2. Read-only capabilities | Status/reporting or integration adapters with explicit freshness and authorization limits | Results reconciled; no sensitive-data leakage; latency/freshness accepted | Route reads back to legacy |
| 3. Shadow processing | Protected traffic replay; compare decisions without ledger authority or external submission | Explained discrepancies; capacity and fault behavior acceptable | Disable shadow path; no financial reversal |
| 4. Pilot cohort | Kong exposes approved routes; business routing assigns one authoritative payment owner | Balanced/reconciled ledger, stable SLOs, working exceptions and recovery exercises | Stop intake; drain/reconcile; reverse only with state-aware data handover |
| 5. Expand entities/rails | Repeat cohort gates; scale support, capacity and Singapore recovery | Sustained SLOs and unit cost, bounded exception backlog, support sign-off | Stop expansion; cohort-specific reversal where safe |
| 6. Retire legacy | Remove obsolete routes/adapters, archive records and satisfy retention | No hidden consumers or unresolved settlements; legal and operations approval | Recovery/archive procedures, not simple traffic rollback |

## Coexistence and safe authority transfer

Use a strangler interface and stable API contracts. Kong routes traffic but must not become the only record of payment ownership. Durable application routing/ownership records ensure retries reach the authoritative system.

CDC may support comparison or migration, not uncontrolled writes to two ledgers. Assign each cohort one authoritative writer. At cutover, pause/queue eligible intake, drain or record in-flight work, reconcile checkpoints, transfer authority and then reopen. Preserve the original payment reference across systems.

After the new ledger commits, redirecting traffic back can lose or duplicate payments. Rollback needs proven reverse data synchronization and rail reconciliation, otherwise use forward repair. Expand-and-contract schemas keep the preceding application release compatible; destructive schema contraction follows a separately approved rollback-window closure.

## Organisational dependencies

Platform delivers reusable Terraform/Kong/EKS contracts and support. Application teams deliver business behavior, idempotency and service SLOs. Data engineering owns conversion and reconciliation; network teams deliver paths to Malaysia and Singapore. Security/compliance attach the already-granted cross-border approval, verify its scope and gate controls. Payments operations and external partners certify rail behavior, status queries and recovery sessions.

Provide named on-call staff, training, runbooks and incident delegation before pilot. Existing teams' Kubernetes experience is an assumption to validate, not an automatic capability.

## Debt and change controls

Every temporary adapter, manual reconciliation process, overprivileged exception and legacy host has an owner, risk, target removal wave and expiry. Expired exceptions stop expansion unless the authorized owner renews them with controls.

Tie each wave to the [risk register](08-risk-register.md), [deployment governance](../governance/deployment-governance.md), [acceptance criteria](09-validation-and-limitations.md) and [DR exercises](../appendix/dr-testing-scenarios.md). Calendar dates require a funded delivery plan and are intentionally not invented.
