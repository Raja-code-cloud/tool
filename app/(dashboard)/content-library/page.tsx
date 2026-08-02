import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";

import { ContentLibraryView } from "./_components/content-library-view";

export const metadata = buildRouteMetadata(ROUTES.contentLibrary);

export default function ContentLibraryPage(): React.JSX.Element {
  return <ContentLibraryView />;
}
