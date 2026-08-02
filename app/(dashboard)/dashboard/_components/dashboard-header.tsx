import { CalendarPlus, RefreshCw, Share2, Sparkles, Upload } from "lucide-react";
import Link from "next/link";

import { IconButton, PrimaryButton } from "@/components/buttons";
import { PageHeader } from "@/components/layout";
import { ROUTES } from "@/constants/navigation";
import { workspaceService } from "@/lib/services";

const QUICK_ACTIONS = [
  { id: "upload", label: "Upload", icon: Upload, href: ROUTES.upload },
  { id: "ai", label: "Generate with AI", icon: Sparkles, href: ROUTES.aiStudio },
  { id: "schedule", label: "Schedule", icon: CalendarPlus, href: ROUTES.scheduler },
  { id: "connect", label: "Connect account", icon: Share2, href: ROUTES.socialAccounts },
] as const;

function greetingForHour(hour: number): string {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

type DashboardHeaderProps = {
  readonly healthSummary: string;
  readonly onRefresh?: () => void;
  readonly isRefreshing?: boolean;
};

export function DashboardHeader({
  healthSummary,
  onRefresh,
  isRefreshing = false,
}: DashboardHeaderProps): React.JSX.Element {
  const currentUser = workspaceService.getCurrentUser();
  const firstName = currentUser.name.split(" ")[0] ?? currentUser.name;
  const greeting = greetingForHour(new Date().getHours());

  return (
    <PageHeader
      title={`${greeting}, ${firstName}`}
      description={healthSummary}
      actions={
        <div className="flex items-center gap-2">
          {onRefresh ? (
            <IconButton
              label="Refresh dashboard"
              icon={<RefreshCw className={isRefreshing ? "animate-spin" : ""} aria-hidden="true" />}
              onClick={onRefresh}
            />
          ) : null}
          <PrimaryButton asChild>
            <Link href={ROUTES.upload}>Create content</Link>
          </PrimaryButton>
        </div>
      }
    >
      <div className="flex flex-wrap gap-2 pt-1">
        {QUICK_ACTIONS.map((action) => (
          <Link
            key={action.id}
            href={action.href}
            className="bg-card text-foreground hover:bg-accent hover:text-accent-foreground focus-visible:ring-ring inline-flex min-h-9 items-center gap-2 rounded-md border px-3 text-sm font-semibold transition-colors duration-(--duration-fast) focus-visible:ring-2 focus-visible:outline-none"
          >
            <action.icon className="size-4" aria-hidden="true" />
            {action.label}
          </Link>
        ))}
      </div>
    </PageHeader>
  );
}
