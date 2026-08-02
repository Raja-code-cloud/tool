import { Skeleton, SkeletonText } from "@/components/feedback";
import { PageContainer, Stack } from "@/components/layout";
import { SETTINGS_SECTIONS } from "@/constants/settings";

const VISIBLE_SECTION_PLACEHOLDERS = 3;

export default function SettingsLoading(): React.JSX.Element {
  return (
    <PageContainer>
      <Stack gap="lg" aria-busy="true">
        <p role="status" className="sr-only">
          Loading settings
        </p>

        <Stack gap="sm">
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-4 w-full max-w-md" />
        </Stack>

        <div className="desktop:grid-cols-[13rem_minmax(0,1fr)] desktop:items-start grid gap-6">
          <div className="desktop:grid hidden gap-1">
            {SETTINGS_SECTIONS.map((section) => (
              <Skeleton key={section.id} className="h-9" />
            ))}
          </div>

          <Stack gap="md">
            {Array.from({ length: VISIBLE_SECTION_PLACEHOLDERS }, (_, index) => (
              <div key={index} className="bg-card rounded-xl border p-5">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="mt-2 h-4 w-64" />
                <SkeletonText className="mt-5" lines={4} />
              </div>
            ))}
          </Stack>
        </div>
      </Stack>
    </PageContainer>
  );
}
