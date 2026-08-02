import type { PlatformId } from "@/lib/domain/platform";

import type { AiStudioSettings, LoadingPhase, PlatformWorkspaceState } from "./types";

export type WorkspaceData = {
  activePlatform: PlatformId;
  current: PlatformWorkspaceState;
  displayContent: string;
  settings: AiStudioSettings;
  loadingPhase: LoadingPhase;
  isLoading: boolean;
};

export type WorkspacePanelState = {
  settingsOpen: boolean;
  versionsOpen: boolean;
  compareVersionId: string | null;
  canUndo: boolean;
  canRedo: boolean;
};

export type WorkspaceActions = {
  onPlatformChange: (platform: PlatformId) => void;
  onSettingsChange: (patch: Partial<AiStudioSettings>) => void;
  onSettingsToggle: () => void;
  onVersionsToggle: () => void;
  onCompareVersion: (id: string | null) => void;
  onRestoreVersion: (id: string) => void;
  onContentChange: (content: string) => void;
  onGenerate: () => void;
  onRegenerate: () => void;
  onTransform: (action: "improve" | "expand" | "shorten" | AiStudioSettings["tone"]) => void;
  onApprove: () => void;
  onReject: () => void;
  onSaveDraft: () => void;
  onUndo: () => void;
  onRedo: () => void;
};
