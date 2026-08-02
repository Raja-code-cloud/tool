export type DashboardSuggestion = {
  readonly id: string;
  readonly title: string;
  readonly reason: string;
  readonly priority: "high" | "medium" | "low";
  readonly actionLabel: string;
  readonly href: string;
};

export type AgendaEntry = {
  readonly id: string;
  readonly time: string;
  readonly title: string;
  readonly platform: string;
  readonly status: "queued" | "published" | "failed";
};

export type RecentContentRow = {
  readonly id: string;
  readonly title: string;
  readonly type: string;
  readonly variants: number;
  readonly platforms: readonly string[];
  readonly status: "draft" | "review" | "scheduled" | "published" | "failed";
  readonly owner: string;
  readonly updatedAt: string;
};

export type ActivityItem = {
  readonly id: string;
  readonly actor: string;
  readonly action: string;
  readonly target: string;
  readonly occurredAt: string;
};

export type PlatformHealth = {
  readonly id: string;
  readonly name: string;
  readonly status: "healthy" | "warning" | "error";
  readonly detail: string;
};

export type DashboardStorage = {
  readonly usedBytes: number;
  readonly totalBytes: number;
  readonly label: string;
};
