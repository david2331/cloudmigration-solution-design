# Risk register

**Selected cloud: AWS. Ratings are provisional; all residual-risk decisions require named owners.**

| ID | Risk / impact | Initial level | Treatment and evidence | Accountable owner | Gate or review trigger |
|---|---|---|---|---|---|
| R01 | Async regional replication loses acknowledged payment tail | Critical | Quantify RPO and transaction exposure; redesign commitment if zero-loss is mandatory | Payments business/risk | Before data architecture approval; replication incidents |
| R02 | Fencing fails while old region still submits externally | Critical | Enforce exclusive writer/rail authority; partition exercise; stop rather than split brain | Payments service owner | Before regional DR approval; rail protocol changes |
| R03 | Claimed recovery exceeds 30 minutes | High | Preprovision Singapore dependencies; measure disruption-to-safe-journey recovery | Operations | Each DR exercise and topology change |
| R04 | Cross-border approval evidence/scope does not cover every copy | High | Bank-confirmed approval (C05); attach reference and classify ledger, telemetry, backup, state and secrets | Security/compliance | Before provisioning/copy policies; approval amendments |
| R05 | Kong plugin/edition/topology cannot implement required auth or limits | High | Evaluate DB-less compatibility, licensing, fail-closed behavior and distributed counter needs | Platform | Before Kong topology sign-off; plugin/version changes |
| R06 | Platform-wide Kong policy change affects multiple applications | High | Per-entity isolation, staged policy releases, route contract tests and rollback | Platform | Every baseline policy change |
| R07 | Kubernetes complexity exceeds operational skills | High | Supported platform baseline, training, staffed on-call, upgrade exercises | Platform | Upgrade backlog, incidents, staffing changes |
| R08 | Shared network or control failure spans entities | High | Diverse links, symmetric inspection, isolated routes and independent rollout | Network | Routing changes and network incidents |
| R09 | CI/runner compromise grants production control | Critical | Scoped OIDC, isolated runners, protected environments and trusted artifacts | Security | Workflow/trust changes and security incidents |
| R10 | Migration produces missing/duplicate payments | Critical | Single authority, reconciled cutover, idempotency and explicit rollback constraints | Payments migration owner | Every cohort promotion |
| R11 | Immutable backups cannot be decrypted or restored | Critical | Independent keys/roles, supported copy workflow and clean-room exercises | Data owner | Key/backup policy changes; restore exercises |
| R12 | Per-entity clusters/Kong and DR capacity exceed funding | High | Cost per payment, baseline/peak model, shared allocation and capacity approval | Platform/FinOps lead | Forecast deviations or entity expansion |
| R13 | Region/engine/instance capacity blocks target deployment | High | Confirm shared supported versions, quotas, endpoint/plugin capabilities and capacity in P/R | Platform | Before capacity commitment; upgrades |
| R14 | Regional queues or gateway configuration assumed replicated | High | Preposition configuration; replay surviving outbox; test empty gateway readiness and local dependencies | Application/platform lead | Restore exercises and release changes |
| R15 | External dependency prevents SLO or safe recovery | High | Contractual objectives, status query/idempotency, redundant connectivity and joint exercises | Payments service owner | Partner changes and dependency incidents |

All treatments are proposed until evidence is attached. Do not mark risk accepted merely because a service is selected. R01/R02 can invalidate the recovery claim and remain production approval blockers.

See [data and DR](05-data-and-dr.md), [threat controls](06-threat-control-model.md), [migration](07-migration-roadmap.md), and [validation](09-validation-and-limitations.md).
