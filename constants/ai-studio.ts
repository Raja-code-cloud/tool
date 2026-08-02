import type { AiStudioProject, AiSuggestion } from "@/lib/domain/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";

export type { PlatformId } from "@/lib/domain/platform";
export type {
  AiAudience,
  AiLength,
  AiStudioProject,
  AiSuggestion,
  AiTone,
  ApprovalStatus,
  PlatformConfig,
} from "@/lib/domain/ai-studio";

export {
  AI_STUDIO_AUDIENCES,
  AI_STUDIO_DRAFT_STORAGE_KEY as DRAFT_STORAGE_KEY,
  AI_STUDIO_LENGTHS,
  AI_STUDIO_PLATFORMS,
  AI_STUDIO_TONES,
  PLATFORM_TIPS,
} from "@/lib/config/ai-studio";

export const AI_STUDIO_PROJECT: AiStudioProject = {
  id: "proj-azure-lz",
  name: "Azure landing zone deep dive",
  description:
    "Production-ready Azure landing zones with Terraform, policy guardrails, and identity baselines.",
  category: "Cloud architecture",
  tags: ["azure", "terraform", "iam", "kubernetes", "devops"],
  status: "in_review",
  wordCount: 1842,
  readingMinutes: 10,
  thumbnailHue: 210,
  videoDuration: "4:32",
  hasVideo: true,
  masterArticle: `# Production-Ready Azure Landing Zones

Landing zones are the foundation every mature cloud program builds on. Without a consistent baseline, teams reinvent networking, identity, and policy enforcement in every subscription—and audit findings compound.

## Why landing zones matter

An Azure landing zone is not a template download. It is an operational model: management group hierarchy, subscription vending, network topology, identity baseline, and guardrails that scale with your organization.

## Core design pillars

**Management groups and policy**
Organize subscriptions by environment and business unit. Azure Policy enforces tagging, region restrictions, and approved SKUs at scale. Pair policy definitions with Terraform modules so drift is visible in CI.

**Identity and access**
Entra ID groups map to Azure RBAC roles. Privileged Identity Management (PIM) time-boxes admin access. Service principals for automation get scoped roles—not Owner on the root management group.

**Network topology**
Hub-spoke or virtual WAN patterns centralize egress, firewall inspection, and hybrid connectivity. Private endpoints for PaaS services reduce public attack surface.

**Platform automation**
Terraform or Bicep modules version your baseline. Pipeline gates run \`terraform plan\` on every pull request. State files live in secure storage with OIDC federation—no long-lived secrets.

## Kubernetes on Azure

AKS inherits the landing zone network and identity model. Workload identity replaces pod-managed secrets. Azure Policy for Kubernetes blocks privileged containers and enforces label standards.

## Cloud SQL and data services

Data services land in dedicated subscriptions with stricter policies. Cloud SQL uses private link, automated backups, and Entra ID authentication. FinOps tags flow from policy into cost reports.

## Getting started

1. Define your management group hierarchy on paper first.
2. Implement identity baseline before any workload subscriptions.
3. Automate subscription creation with policy inheritance.
4. Measure adoption with Azure Advisor and policy compliance dashboards.

The teams that ship fastest treat landing zones as a product—not a one-off migration project.`,
};

export type MockPlatformContent = {
  readonly content: string;
  readonly hashtags: readonly string[];
  readonly cta: string;
};

export const MOCK_PLATFORM_CONTENT: Record<PlatformId, MockPlatformContent> = {
  linkedin: {
    content: `Production-ready Azure landing zones are not a six-month science project—they are an operating model.

In our latest deep dive we cover:

→ Management group hierarchy that scales with your org
→ Policy-driven guardrails with Azure Policy + Terraform
→ Identity baseline with Entra ID and PIM
→ Hub-spoke networking for hybrid connectivity
→ AKS workload identity and Cloud SQL private endpoints

The teams that ship fastest treat landing zones as a product—not a one-off migration.

What's your biggest blocker today: networking, identity, or policy enforcement?`,
    hashtags: [
      "#Azure",
      "#CloudArchitecture",
      "#Terraform",
      "#DevOps",
      "#LandingZone",
      "#Kubernetes",
    ],
    cta: "Read the full deep dive →",
  },
  facebook: {
    content: `Azure landing zones done right ☁️

We published a practical guide covering management groups, Azure Policy, Entra ID + PIM, hub-spoke networking, and running AKS + Cloud SQL on a secure baseline.

If you're building cloud foundations in 2026, start with identity and policy before workloads.`,
    hashtags: ["#Azure", "#Cloud", "#DevOps"],
    cta: "See the full article on our blog",
  },
  instagram: {
    content: `Your Azure estate shouldn't feel like 50 mini datacenters 🏗️

Landing zones give you:
✅ Consistent identity (Entra ID + PIM)
✅ Policy guardrails at scale
✅ Hub-spoke networking
✅ Terraform automation with CI gates
✅ AKS + Cloud SQL on private endpoints

Save this for your next architecture review.`,
    hashtags: [
      "#Azure",
      "#CloudArchitecture",
      "#Terraform",
      "#Kubernetes",
      "#DevOps",
      "#CloudSecurity",
      "#PlatformEngineering",
    ],
    cta: "Link in bio for the full guide",
  },
  x: {
    content: `Azure landing zones in one thread 🧵

1/ Treat landing zones as a product—not a migration side quest.

2/ Start with management groups + Azure Policy before workloads.

3/ Entra ID groups → RBAC. PIM for admin. No standing Owner.

4/ Hub-spoke or vWAN for centralized egress + hybrid.

5/ Terraform in CI. OIDC federation. No long-lived secrets.

6/ AKS: workload identity + Azure Policy for Kubernetes.

What's blocking your team? 👇`,
    hashtags: ["#Azure", "#Terraform", "#DevOps"],
    cta: "Full article linked below",
  },
  medium: {
    content: `# Production-Ready Azure Landing Zones: A Practitioner's Guide

*How to build cloud foundations that scale with your organization—not against it.*

## The problem with ad-hoc Azure adoption

Every team provisioning their own subscriptions creates inconsistent networking, orphaned identities, and audit debt. Landing zones solve this by defining a repeatable baseline.

## Management groups and policy

Structure subscriptions by environment and business unit. Azure Policy enforces tagging, allowed regions, and approved SKUs. Pair policies with Terraform modules so infrastructure changes are reviewable in pull requests.

## Identity baseline

Map Entra ID groups to Azure RBAC roles. Enable PIM for privileged roles. Automation service principals receive least-privilege scopes—never Owner at the root management group.

## Network design

Hub-spoke or Azure Virtual WAN centralizes firewall inspection, egress control, and hybrid connectivity. Private endpoints for PaaS services minimize public exposure.

## Platform automation

Version your baseline in Terraform or Bicep. Run \`terraform plan\` on every PR. Store state securely with OIDC pipeline authentication.

## Kubernetes and data services

AKS inherits landing zone networking and identity. Cloud SQL uses private link and Entra ID auth. FinOps tags from policy feed cost dashboards.

## Conclusion

Ship identity and policy first. Automate subscription vending. Measure compliance continuously. Landing zones are the product your platform team owns.`,
    hashtags: ["Azure", "Cloud Architecture", "Terraform", "DevOps"],
    cta: "Follow for more platform engineering content",
  },
  youtube: {
    content: `Production-Ready Azure Landing Zones — Full Breakdown

In this video we walk through building Azure landing zones with Terraform, Azure Policy, Entra ID, hub-spoke networking, AKS, and Cloud SQL.

TIMESTAMPS
0:00 Introduction
0:42 Why landing zones matter
2:15 Management groups & policy
4:08 Identity baseline (Entra ID + PIM)
6:20 Network topology (hub-spoke)
8:05 Terraform automation & CI
10:30 AKS on a landing zone
12:45 Cloud SQL private endpoints
14:10 FinOps tagging & compliance

TOPICS: Azure, landing zones, Terraform, Kubernetes, Cloud SQL, IAM, DevOps, cloud architecture

Subscribe for weekly cloud architecture content.`,
    hashtags: ["#Azure", "#LandingZone", "#Terraform", "#Kubernetes", "#CloudSQL", "#DevOps"],
    cta: "Subscribe and turn on notifications",
  },
};

export const AI_SUGGESTIONS: readonly AiSuggestion[] = [
  {
    id: "gram-1",
    category: "grammar",
    title: "Passive voice detected",
    description:
      "Consider changing “is enforced” to “enforces” for a stronger opening on LinkedIn.",
    action: "Apply fix",
  },
  {
    id: "seo-1",
    category: "seo",
    title: "Add primary keyword early",
    description: "Include “Azure landing zone” in the first 140 characters for YouTube SEO.",
    action: "Insert keyword",
  },
  {
    id: "eng-1",
    category: "engagement",
    title: "Add a question CTA",
    description: "Posts with a closing question see 20–30% higher comment rates on LinkedIn.",
    action: "Add question",
  },
  {
    id: "read-1",
    category: "readability",
    title: "Shorten paragraphs",
    description: "Instagram caption has 4 lines over 120 characters—split for mobile readability.",
    action: "Split lines",
  },
  {
    id: "time-1",
    category: "timing",
    title: "Best posting time",
    description:
      "LinkedIn: Tuesday 9:00 AM EST. X: Wednesday 12:00 PM EST. YouTube: Thursday 2:00 PM EST.",
    action: "Schedule suggestion",
  },
  {
    id: "warn-1",
    category: "warning",
    title: "X character limit",
    description: "Thread tweet 3 exceeds 280 characters when hashtags are included.",
    action: "Trim tweet",
  },
  {
    id: "warn-2",
    category: "warning",
    title: "Facebook length",
    description: "Post exceeds 500 characters—engagement typically drops beyond this threshold.",
    action: "Shorten post",
  },
];
