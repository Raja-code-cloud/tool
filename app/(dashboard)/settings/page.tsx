import { PageContainer, PageHeader, Stack } from "@/components/layout";
import { ROUTES } from "@/constants/navigation";
import { buildRouteMetadata } from "@/lib/utils/navigation";
import { AiProvidersSection } from "./_components/ai-providers-section";
import { ApiKeysSection } from "./_components/api-keys-section";
import { AppearanceSection } from "./_components/appearance-section";
import { DangerZoneSection } from "./_components/danger-zone-section";
import { NotificationsSection } from "./_components/notifications-section";
import { ProfileSection } from "./_components/profile-section";
import { PublishingSection } from "./_components/publishing-section";
import { SecuritySection } from "./_components/security-section";
import { SettingsNav } from "./_components/settings-nav";
import { StorageSection } from "./_components/storage-section";

export const metadata = buildRouteMetadata(ROUTES.settings);

export default function SettingsPage(): React.JSX.Element {
  return (
    <PageContainer>
      <Stack gap="lg">
        <PageHeader title="Settings" description="Manage your profile, workspace defaults, and integrations." />

        <div className="grid gap-6 desktop:grid-cols-[13rem_minmax(0,1fr)] desktop:items-start">
          <SettingsNav />

          <Stack gap="md">
            <ProfileSection />
            <AppearanceSection />
            <NotificationsSection />
            <AiProvidersSection />
            <StorageSection />
            <PublishingSection />
            <SecuritySection />
            <ApiKeysSection />
            <DangerZoneSection />
          </Stack>
        </div>
      </Stack>
    </PageContainer>
  );
}
