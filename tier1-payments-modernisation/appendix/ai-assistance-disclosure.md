# AI assistance and provenance disclosure

**Selected cloud: AWS.** This architecture review pack was drafted with AI assistance. All design decisions, constraints and confirmations were supplied or approved by the human author; AI output was reviewed and edited before inclusion.

## Tools used

| Tool | Use in this pack |
|---|---|
| GitHub Copilot CLI (VS Code) | Initial structuring of the assessment response and first drafts of the paper sections and governance documents |
| Qwen Code CLI with an Anthropic Claude model | Review against the assessment brief; rewrite of the platform decision (Task 3) and ADR rationale; quality-attributes table and availability composition (Task 1); terminology consistency fixes; expansion of the evidence register (S17-S35); removal of duplicated text |
| draw.io MCP server and draw.io desktop (v32.6) | Generation of all diagrams as `.drawio` sources using the official AWS Architecture Icons (`mxgraph.aws4`) and Kubernetes icons, with scripted checks for blank icons, overlaps and edge crossings, and PNG export at 2x scale |

## What the AI did and did not do

AI assisted with structuring, comparing AWS services, drafting text and diagrams, and identifying limitations and gaps against the brief. Provider behavior statements are grounded in official AWS, Kong, GitHub and HashiCorp documentation recorded in the [evidence register](provider-native-evidence.md); source URLs were checked to resolve on 3-4 November 2026. Regional availability in `ap-southeast-5` was checked against AWS documentation on 4 November 2026 for two services only: the AWS Backup logically air-gapped vault and Aurora DSQL are documented as not available in Malaysia. Availability of the other S17-S35 services was **not** verified and remains an implementation gate.

The author selected AWS, EKS/Helm, Terraform, GitHub Actions, self-hosted platform-owned Kong and per-entity production isolation, and confirmed Malaysia primary, Singapore recovery and that cross-border approval has been granted (assumption C05). The approval document was not supplied to or verified by the AI.

DB-less Kong/KIC topology, Aurora/SQS data design, recovery time allocations, component scores, risk ratings and operational policies are review proposals unless explicitly marked confirmed. No deployment, performance, security exercise or recovery result is represented as completed. No executable Terraform, Helm charts, Kong configuration or GitHub Actions workflows were created or deployed.

Human architecture, platform, application, security/compliance, data and payments owners must approve the design and attach implementation evidence. The documents are not regulatory certification or a substitute for professional risk ownership.
