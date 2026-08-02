import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";

import { SchedulerView } from "./_components/scheduler-view";

export const metadata = buildRouteMetadata(ROUTES.scheduler);

export default function SchedulerPage(): React.JSX.Element {
  return <SchedulerView />;
}
