import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";
import { FeaturePlaceholder } from "../_components/feature-placeholder";

export const metadata = buildRouteMetadata(ROUTES.contentLibrary);

export default function ContentLibraryPage(): React.JSX.Element {
  return <FeaturePlaceholder href={ROUTES.contentLibrary} />;
}