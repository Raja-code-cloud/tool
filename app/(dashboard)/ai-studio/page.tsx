import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";

import { AiStudioView } from "./_components/ai-studio-view";

export const metadata = buildRouteMetadata(ROUTES.aiStudio);

export default function AiStudioPage(): React.JSX.Element {
  return <AiStudioView />;
}
