import { PageContainer, Stack } from "@/components/layout";
import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";

import { AiSuggestionsPanel } from "./_components/ai-suggestions-panel";
import { DashboardBottomModules } from "./_components/dashboard-bottom-modules";
import { DashboardHeader } from "./_components/dashboard-header";
import { DashboardStats } from "./_components/dashboard-stats";
import { PublishingCalendarPanel } from "./_components/publishing-calendar-panel";
import { RecentContentTable } from "./_components/recent-content-table";

export const metadata = buildRouteMetadata(ROUTES.dashboard);

export default function DashboardPage(): React.JSX.Element {
  return (
    <PageContainer>
      <Stack gap="lg">
        <DashboardHeader />
        <DashboardStats />

        <div className="desktop:grid-cols-12 desktop:items-start grid gap-4">
          <div className="desktop:col-span-8">
            <AiSuggestionsPanel />
          </div>
          <div className="desktop:col-span-4">
            <PublishingCalendarPanel />
          </div>
        </div>

        <RecentContentTable />
        <DashboardBottomModules />
      </Stack>
    </PageContainer>
  );
}
