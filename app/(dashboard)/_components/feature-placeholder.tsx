import { Construction } from "lucide-react";

import { PageContainer, PageHeader, Stack } from "@/components/layout";
import { EmptyState } from "@/components/feedback";
import { Badge } from "@/components/ui";
import { findRouteByHref } from "@/constants/navigation";

export type FeaturePlaceholderProps = { href: string };

/**
 * Route scaffold for pages whose interface has not been built yet. Copy is read
 * from the navigation constants so it never drifts from the sidebar. Route-group
 * local on purpose: it is temporary and must not enter the shared library.
 */
export function FeaturePlaceholder({ href }: FeaturePlaceholderProps): React.JSX.Element {
  const route = findRouteByHref(href);
  if (!route) return <></>;

  return (
    <PageContainer>
      <Stack gap="lg">
        <PageHeader title={route.label} description={route.description} actions={<Badge variant="neutral">Planned</Badge>} />
        <EmptyState
          icon={<Construction aria-hidden="true" />}
          title={`${route.label} is not built yet`}
          description="This route is wired into the application shell. Its interface ships in a later milestone."
        />
      </Stack>
    </PageContainer>
  );
}
