import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";

import { AnalyticsView } from "./_components/analytics-view";

export const metadata = buildRouteMetadata(ROUTES.analytics);

export default function AnalyticsPage(): React.JSX.Element {
  return <AnalyticsView />;
}
