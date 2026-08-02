import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";

import { UploadWizardView } from "./_components/upload-wizard-view";

export const metadata = buildRouteMetadata(ROUTES.upload);

export default function UploadPage(): React.JSX.Element {
  return <UploadWizardView />;
}
