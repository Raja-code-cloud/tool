import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";

import { DashboardView } from "./_components/dashboard-view";

export const metadata = buildRouteMetadata(ROUTES.dashboard);

export default function DashboardPage(): React.JSX.Element {
  return <DashboardView />;
}
