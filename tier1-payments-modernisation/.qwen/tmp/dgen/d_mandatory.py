import sys
sys.path.insert(0, "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/.qwen/tmp/dgen")
from lib import Diagram, build

OUT = "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/diagrams"
WORK = "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/.qwen/tmp/dgen"


def mandatory():
    d = Diagram("mandatory-architecture", "Mandatory AWS architecture — one entity, Malaysia primary (P) with Singapore recovery (R)", 1980, 1560)

    d.group("ext", "external", "External trust boundary (outside AWS)", 20, 60, 1940, 140)
    d.res("users", "users", "Customers / channels", 80, 100, parent="ext")
    d.res("dc", "dc", "On-premises core banking,<br>screening, operations", 330, 100, parent="ext")
    d.res("rails", "bank", "Payment rails /<br>settlement partners", 640, 100, parent="ext")
    d.github("gh", "GitHub Actions<br>(OIDC, no runtime role)", 910, 100, parent="ext")
    d.svc("shield", "shield", "AWS Shield", 1180, 100, parent="ext")
    d.svc("r53", "route53", "Route 53 + ARC<br>routing controls", 1400, 100, parent="ext")
    d.add_text("ext_note", "Every hop is TLS/mTLS. Direct Connect is not encrypted by default: IPsec or mTLS is required.", 1600, 100, 340, 60, parent="ext", size=11)

    d.group("cloud", "cloud", "AWS Organization — Control Tower, SCP guardrails, region allow-list ap-southeast-5 / ap-southeast-1", 20, 220, 1940, 1320)

    d.group("net", "account", "Network account", 40, 260, 320, 560, parent="cloud")
    d.svc("dx", "dx", "Direct Connect<br>2 diverse locations", 90, 310, parent="net")
    d.svc("vpn", "vpn", "Site-to-Site VPN<br>fallback", 240, 310, parent="net")
    d.svc("tgw", "tgw", "Transit Gateway<br>entity route tables", 90, 450, parent="net")
    d.svc("nfw", "nfw", "Network Firewall<br>per-AZ, symmetric", 240, 450, parent="net")
    d.badge("b_net", "4", 320, 300, parent="net", color="#8C4FFF")
    d.add_text("net_note", "Regional TGW and inspection VPC in both P and R. No default cross-entity routes.", 60, 600, 280, 60, parent="net", size=11)

    d.group("shared", "account", "Security tooling, log archive, platform tooling", 40, 840, 320, 680, parent="cloud")
    d.svc("guard", "guardduty", "GuardDuty", 90, 890, parent="shared")
    d.svc("sechub", "sechub", "Security Hub", 240, 890, parent="shared")
    d.svc("trail", "cloudtrail", "CloudTrail<br>org trail", 90, 1010, parent="shared")
    d.svc("config", "config", "AWS Config", 240, 1010, parent="shared")
    d.svc("ecr", "ecr", "ECR signed<br>digests (to R)", 90, 1140, parent="shared")
    d.svc("idc", "idc", "IAM Identity Center<br>+ break-glass", 240, 1140, parent="shared")
    d.res("logs", "bucket", "Log archive S3<br>(Object Lock)", 90, 1270, parent="shared")
    d.res("sts", "sts", "STS scoped<br>deploy roles", 240, 1270, parent="shared")
    d.add_text("shared_note", "Residency-scoped: P and R logs stay in their region.", 60, 1410, 280, 40, parent="shared", size=11)

    d.group("prod", "account", "entity-a-prod workload account — isolated per legal entity (entity-b identical; no shared data, keys or routes)", 380, 260, 1300, 1260, parent="cloud")

    d.group("rp", "region", "P: Malaysia ap-southeast-5 (active writer region)", 400, 300, 1260, 620, parent="prod")
    d.group("vpcp", "vpc", "Workload VPC — security group and NetworkPolicy boundaries", 420, 340, 1220, 560, parent="rp")
    d.group("pub", "public_subnet", "Ingress subnets spanning AZ-a / AZ-b / AZ-c", 440, 380, 1180, 124, parent="vpcp")
    d.svc("waf", "waf", "AWS WAF", 490, 420, parent="pub")
    d.res("alb", "alb", "Internet ALB", 640, 420, parent="pub")
    d.badge("b1", "1", 700, 412, parent="pub")
    d.res("ialb", "alb", "Internal ALB (hybrid)", 900, 420, parent="pub")
    d.res("ep", "endpoints", "VPC endpoints:<br>S3, ECR, SQS, STS, KMS", 1220, 420, parent="pub")

    for i, az in enumerate("abc"):
        x = 440 + i * 400
        d.group(f"az{az}", "az", f"AZ-{az} — failure domain", x, 520, 380, 360, parent="vpcp")
        d.group(f"eks{az}", "eks", "EKS managed node group", x + 15, 555, 350, 170, parent=f"az{az}")
        d.k8s(f"kong{az}", "pod", "Kong DB-less + KIC", x + 55, 600, parent=f"eks{az}")
        d.k8s(f"app{az}", "pod", "Payment services", x + 245, 600, parent=f"eks{az}")
        d.res(f"db{az}", "aurora_inst" if az == "a" else "replica", "Aurora writer" if az == "a" else "Aurora reader / failover", x + 165, 775, parent=f"az{az}")
    d.badge("b2", "2", 470, 590, parent="eksa")
    d.badge("b3", "3", 580, 770, parent="aza")

    d.group("rr", "region", "R: Singapore ap-southeast-1 — pre-provisioned warm standby, payment submitters fenced", 400, 940, 1260, 280, parent="prod")
    d.group("vpcr", "vpc", "Workload VPC — identical layout across 3 AZs", 420, 980, 880, 220, parent="rr")
    d.svc("waf_r", "waf", "WAF + ALBs", 470, 1040, parent="vpcr")
    d.svc("eks_r", "eks", "EKS + Kong<br>(3 AZs)", 660, 1040, parent="vpcr")
    d.svc("aur_r", "aurora", "Aurora Global<br>secondary (read-only)", 860, 1040, parent="vpcr")
    d.svc("sqs_r", "sqs", "Region-local SQS<br>(rebuilt from outbox)", 1100, 1040, parent="vpcr")
    d.svc("kms_r", "kms", "Regional KMS /<br>Secrets Manager", 1360, 1040, parent="rr")
    d.svc("arc_r", "arc", "ARC readiness<br>checks", 1540, 1040, parent="rr")

    d.group("svcs", "plain", "Regional AWS services (P)", 400, 1240, 840, 260, parent="prod")
    d.svc("sqs", "sqs", "SQS + DLQ<br>(outbox relay)", 440, 1290, parent="svcs")
    d.svc("s3", "s3", "S3 (SSE-KMS)", 600, 1290, parent="svcs")
    d.svc("kms", "kms", "KMS entity keys", 760, 1290, parent="svcs")
    d.svc("secrets", "secrets", "Secrets Manager", 920, 1290, parent="svcs")
    d.svc("cw", "cloudwatch", "CloudWatch + OTel", 1090, 1290, parent="svcs")
    d.add_text("svcs_note", "EKS Pod Identity gives each service account its own least-privilege IAM role; IMDS is blocked for pods.", 420, 1420, 800, 40, parent="svcs", size=11)

    d.group("rec", "account", "entity-a-recovery account (cyber custody)", 1260, 1240, 400, 260, parent="prod")
    d.svc("bkp", "backup", "AWS Backup<br>Vault Lock", 1310, 1290, parent="rec")
    d.res("vault", "vault", "Clean-room VPC,<br>independent keys", 1500, 1290, parent="rec")

    d.legend(1700, 260, [
        ("flow", "Synchronous payment flow"),
        ("hybrid", "Hybrid private path"),
        ("async", "Async replication"),
        ("deploy", "Deployment via OIDC role"),
        ("backup", "Backup copy (isolated)"),
        ("fenced", "Fenced until authorised"),
        ("security", "Findings / audit logs"),
    ], parent="cloud", width=240)

    d.group("keys", "plain", "Controls at numbered points", 1700, 460, 240, 420, parent="cloud")
    d.add_text("k1", "<b>1</b> WAF + Shield at the public ALB; only platform ingress may expose workloads.", 1710, 490, 220, 65, parent="keys", size=11)
    d.add_text("k2", "<b>2</b> Kong authentication and limits; application authorisation and idempotency; NetworkPolicy, admission and signed images.", 1710, 560, 220, 95, parent="keys", size=11)
    d.add_text("k3", "<b>3</b> Single Aurora writer; storage replicated across three AZs; asynchronous global replica to R.", 1710, 660, 220, 80, parent="keys", size=11)
    d.add_text("k4", "<b>4</b> Diverse DX + VPN; TGW segmentation; symmetric Network Firewall inspection.", 1710, 745, 220, 65, parent="keys", size=11)
    d.add_text("k5", "Failure domains: pod, node, AZ, region, account.", 1710, 815, 220, 45, parent="keys", size=11, bold=True)

    d.group("fd", "plain", "Recovery objectives", 1700, 900, 240, 330, parent="cloud")
    d.add_text("fd1", "AZ loss: zero committed loss; serve from two AZs within the error budget.", 1710, 930, 220, 65, parent="fd", size=11)
    d.add_text("fd2", "Region loss: 30-minute RTO target; near-zero RPO (async tail is not guaranteed zero).", 1710, 1000, 220, 80, parent="fd", size=11)
    d.add_text("fd3", "Cyber: clean-room restore with separate RTO/RPO.", 1710, 1085, 220, 50, parent="fd", size=11)
    d.add_text("fd4", "A DNS or ARC switch is not fencing.", 1710, 1140, 220, 45, parent="fd", size=11, bold=True)

    d.edge("users", "r53", "flow", "HTTPS", points=[(104, 180), (1424, 180)], exit=(0.5, 1), entry=(0.5, 1))
    d.edge("r53", "waf", "flow", "", points=[(1440, 240), (514, 240)], exit=(0.85, 1), entry=(0.5, 0))
    d.edge("waf", "alb", "flow", "")
    d.edge("alb", "konga", "flow", "TLS", points=[(664, 510), (519, 510)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("alb", "kongb", "flow", "", points=[(664, 510), (919, 510)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("alb", "kongc", "flow", "", points=[(664, 510), (1319, 510)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("konga", "appa", "flow", "mTLS")
    d.edge("kongb", "appb", "flow", "mTLS")
    d.edge("kongc", "appc", "flow", "mTLS")
    d.edge("appa", "dba", "flow", "writer", exit=(0.5, 1), entry=(1, 0.5), points=[(709, 799)])
    d.edge("appb", "dba", "flow", "", exit=(0.5, 1), entry=(1, 0.3), points=[(1109, 745), (760, 745), (760, 789)])
    d.edge("dba", "dbb", "async", "storage x3 AZs", exit=(1, 0.8), entry=(0, 0.8))
    d.edge("dbb", "dbc", "async", "", exit=(1, 0.8), entry=(0, 0.8))
    d.edge("dc", "dx", "hybrid", "DX + IPsec/mTLS", points=[(354, 250), (114, 250)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("dc", "vpn", "hybrid", "", points=[(370, 280), (264, 280)], exit=(0.85, 1), entry=(0.5, 0))
    d.edge("dx", "tgw", "hybrid", "")
    d.edge("tgw", "nfw", "hybrid", "")
    d.edge("nfw", "ialb", "hybrid", "inspected", points=[(264, 540), (372, 540), (372, 404), (924, 404)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("ialb", "kongb", "hybrid", "", exit=(0.3, 1), entry=(0.3, 0), points=[(914, 540), (899, 540)])
    d.edge("appc", "rails", "flow", "submitter (single active)", points=[(1630, 624), (1630, 210), (664, 210)], exit=(1, 0.5), entry=(0.5, 1))
    d.edge("dbc", "aur_r", "async", "Aurora Global Database (async)", points=[(1429, 930), (884, 930)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("waf_r", "eks_r", "fenced", "")
    d.edge("eks_r", "aur_r", "fenced", "")
    d.edge("aur_r", "sqs_r", "fenced", "replay outbox")
    d.edge("dba", "bkp", "backup", "copy to Vault Lock", points=[(1320, 900), (1320, 1230), (1334, 1230)], exit=(0, 1), entry=(0.5, 0), style_extra="")
    d.edge("gh", "sts", "deploy", "OIDC", points=[(934, 230), (370, 230), (370, 1294)], exit=(0.5, 1), entry=(1, 0.5))
    d.edge("appa", "sqs", "async", "outbox", points=[(730, 755), (410, 755), (410, 1314)], exit=(0.9, 1), entry=(0, 0.5))
    d.edge("cw", "sechub", "security", "findings / logs", points=[(1114, 1528), (372, 1528), (372, 914)], exit=(0.5, 1), entry=(1, 0.5))
    return d


if __name__ == "__main__":
    ok = build(mandatory(), OUT, WORK)
    sys.exit(0 if ok else 1)
