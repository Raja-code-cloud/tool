"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

import { LiveRegion } from "@/components/feedback";
import { PageContainer } from "@/components/layout";
import { Button } from "@/components/ui";
import { AI_STUDIO_PLATFORMS } from "@/constants/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";
import { countCharacters } from "@/lib/utils/ai-studio";
import { cn } from "@/lib/utils/cn";

import { AiStudioHeader } from "./ai-studio-header";
import { AssetsPanel } from "./assets-panel";
import { PreviewPanel } from "./preview-panel";
import type { MobilePanel } from "./types";
import { useAiStudioState } from "./use-ai-studio-state";
import { WorkspacePanel } from "./workspace-panel";

const SuggestionsDrawer = dynamic(() =>
  import("./suggestions-drawer").then((module) => module.SuggestionsDrawer),
);

const MOBILE_TABS: readonly { id: MobilePanel; label: string }[] = [
  { id: "assets", label: "Assets" },
  { id: "workspace", label: "Workspace" },
  { id: "preview", label: "Preview" },
];

export function AiStudioView(): React.JSX.Element {
  const state = useAiStudioState();

  const platformCounts = useMemo(() => {
    const counts = {} as Record<PlatformId, number>;
    AI_STUDIO_PLATFORMS.forEach((platform) => {
      counts[platform.id] = countCharacters(state.platforms[platform.id].content);
    });
    return counts;
  }, [state.platforms]);

  return (
    <PageContainer className="pb-8">
      <div className="grid gap-5">
        <AiStudioHeader
          project={state.project}
          lastSavedAt={state.lastSavedAt}
          onSaveDraft={state.saveDraft}
          onOpenSuggestions={() => state.setSuggestionsOpen(true)}
          onToggleVersions={() => state.setVersionsOpen((open) => !open)}
          isSaving={state.loadingPhase === "saving"}
        />

        {/* Mobile panel switcher */}
        <div
          className="bg-card flex gap-1 rounded-lg border p-1 lg:hidden"
          role="tablist"
          aria-label="Studio panels"
        >
          {MOBILE_TABS.map((tab) => (
            <Button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={state.mobilePanel === tab.id}
              variant={state.mobilePanel === tab.id ? "secondary" : "ghost"}
              className="flex-1"
              onClick={() => state.setMobilePanel(tab.id)}
            >
              {tab.label}
            </Button>
          ))}
        </div>

        <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-[minmax(260px,300px)_minmax(0,1fr)_minmax(280px,320px)]">
          <div
            className={cn(
              "min-w-0 lg:col-span-2 xl:col-span-1",
              state.mobilePanel !== "assets" && "hidden lg:block",
            )}
          >
            <AssetsPanel project={state.project} />
          </div>

          <div className={cn("min-w-0", state.mobilePanel !== "workspace" && "hidden lg:block")}>
            <WorkspacePanel
              data={{
                activePlatform: state.activePlatform,
                current: state.current,
                displayContent: state.displayContent,
                settings: state.settings,
                providers: state.providers,
                loadingPhase: state.loadingPhase,
                isLoading: state.isLoading,
              }}
              panelState={{
                settingsOpen: state.settingsOpen,
                versionsOpen: state.versionsOpen,
                compareVersionId: state.compareVersionId,
                canUndo: state.canUndo,
                canRedo: state.canRedo,
              }}
              actions={{
                onPlatformChange: state.setActivePlatform,
                onSettingsChange: (patch) => state.setSettings((prev) => ({ ...prev, ...patch })),
                onSettingsToggle: () => state.setSettingsOpen((open) => !open),
                onVersionsToggle: () => state.setVersionsOpen((open) => !open),
                onCompareVersion: state.setCompareVersionId,
                onRestoreVersion: state.restoreVersion,
                onContentChange: state.updateContent,
                onGenerate: state.generate,
                onRegenerate: state.regenerate,
                onCancelGeneration: state.cancelGeneration,
                onTransform: state.transformContent,
                onApprove: state.approve,
                onReject: state.reject,
                onSaveDraft: state.saveDraft,
                onUndo: state.undo,
                onRedo: state.redo,
              }}
            />
          </div>

          <div className={cn("min-w-0", state.mobilePanel !== "preview" && "hidden lg:block")}>
            <PreviewPanel
              project={state.project}
              platform={state.activePlatform}
              current={state.current}
              displayContent={state.displayContent}
              platformCounts={platformCounts}
            />
          </div>
        </div>
      </div>

      <LiveRegion>
        {state.loadingPhase !== "idle"
          ? `AI ${state.loadingPhase}`
          : `Editing ${state.activePlatform}`}
      </LiveRegion>

      {state.suggestionsOpen && (
        <SuggestionsDrawer
          open
          onOpenChange={state.setSuggestionsOpen}
          suggestions={state.suggestions}
        />
      )}
    </PageContainer>
  );
}
