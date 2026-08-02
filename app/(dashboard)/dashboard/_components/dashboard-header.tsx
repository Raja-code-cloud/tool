import { CalendarPlus, Share2, Sparkles, Upload } from "lucide-react";
import Link from "next/link";

import { PrimaryButton } from "@/components/buttons";
import { PageHeader } from "@/components/layout";
import { ROUTES } from "@/constants/navigation";
import { dashboardService, workspaceService } from "@/lib/services";

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

export function DashboardHeader(): React.JSX.Element {
  const currentUser = workspaceService.getCurrentUser();
  const firstName = currentUser.name.split(" ")[0] ?? currentUser.name;
  const greeting = greetingForHour(new Date().getHours());

  return (
    <PageHeader
      title={`${greeting}, ${firstName}`}
      description={dashboardService.getHealthSummary()}
      actions={
        <PrimaryButton asChild>
          <Link href={ROUTES.upload}>Create content</Link>
        </PrimaryButton>
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
