"use client";

import { Card, CardHeader } from "@/components/cards";
import { Tabs } from "@/components/navigation";
import { AI_STUDIO_PLATFORMS } from "@/constants/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";

import { AiSettingsPanel } from "./ai-settings-panel";
import { VersionHistoryPanel } from "./version-history-panel";
import { WorkspaceActionToolbars } from "./workspace-action-toolbars";
import type { WorkspaceActions, WorkspaceData, WorkspacePanelState } from "./workspace-contracts";
import { WorkspaceEditor } from "./workspace-editor";

export type WorkspacePanelProps = {
  data: WorkspaceData;
  panelState: WorkspacePanelState;
  actions: WorkspaceActions;
};

const TAB_ITEMS = AI_STUDIO_PLATFORMS.map((platform) => ({
  id: platform.id,
  label: platform.label,
}));

export function WorkspacePanel({
  data,
  panelState,
  actions,
}: WorkspacePanelProps): React.JSX.Element {
  const activeVersionId = data.current.versions[data.current.activeVersionIndex]?.id;
  return (
    <div className="grid gap-4">
      <Card className="relative overflow-hidden p-0">
        <div className="border-b p-4">
          <CardHeader
            title="AI workspace"
            description="Generate, refine, and approve platform variants."
            headingLevel={2}
            className="mb-0"
          />
          <Tabs
            items={TAB_ITEMS}
            value={data.activePlatform}
            onValueChange={(value) => actions.onPlatformChange(value as PlatformId)}
            label="Platform tabs"
            className="mt-4"
          />
        </div>
        <WorkspaceEditor data={data} actions={actions} />
        <WorkspaceActionToolbars data={data} panelState={panelState} actions={actions} />
      </Card>
      <AiSettingsPanel
        settings={data.settings}
        providers={data.providers}
        onChange={actions.onSettingsChange}
        isOpen={panelState.settingsOpen}
        onToggle={actions.onSettingsToggle}
      />
      <VersionHistoryPanel
        versions={data.current.versions}
        {...(activeVersionId ? { activeVersionId } : {})}
        compareVersionId={panelState.compareVersionId}
        onRestore={actions.onRestoreVersion}
        onCompare={actions.onCompareVersion}
        isOpen={panelState.versionsOpen}
        onToggle={actions.onVersionsToggle}
      />
    </div>
  );
}
