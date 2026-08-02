import { PageContainer, Stack } from "@/components/layout";
import { Skeleton, SkeletonCard, SkeletonTable } from "@/components/feedback";

const METRIC_PLACEHOLDERS = 4;

/** Route-level loading fallback shared by every workspace segment. */
export default function DashboardLoading(): React.JSX.Element {
  return (
    <PageContainer>
      <Stack gap="lg" aria-busy="true">
        <p role="status" className="sr-only">Loading page</p>

        <Stack gap="sm">
          <Skeleton className="h-8 w-56" />
          <Skeleton className="h-4 w-full max-w-md" />
        </Stack>

        <div className="grid gap-4 tablet:grid-cols-2 wide:grid-cols-4">
          {Array.from({ length: METRIC_PLACEHOLDERS }, (_, index) => <SkeletonCard key={index} />)}
        </div>

        <SkeletonTable />
      </Stack>
    </PageContainer>
  );
}
