import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";

import { SocialAccountsView } from "./_components/social-accounts-view";

export const metadata = buildRouteMetadata(ROUTES.socialAccounts);

export default function SocialAccountsPage(): React.JSX.Element {
  return <SocialAccountsView />;
}
