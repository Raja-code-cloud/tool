"use client";

import { useCallback, useMemo, useState } from "react";

import { useToast } from "@/hooks/use-toast";
import type { PlatformId } from "@/lib/domain/platform";
import { aiStudioService } from "@/lib/services";
import {
  applyExpand,
  applyImprove,
  applyShorten,
  applyToneTransform,
  delay,
} from "@/lib/utils/ai-studio";

import {
  createInitialPlatformStates,
  DEFAULT_AI_SETTINGS,
  type AiStudioSettings,
  type ContentVersion,
  type LoadingPhase,
  type MobilePanel,
  type PlatformWorkspaceState,
} from "./types";

function versionLabel(index: number): string {
  return `Version ${index + 1}`;
}

function createVersion(
  content: string,
  hashtags: readonly string[],
  cta: string,
  source: ContentVersion["source"],
  index: number,
): ContentVersion {
  return {
    id: `v-${Date.now()}-${index}`,
    label: versionLabel(index),
    content,
    hashtags,
    cta,
    createdAt: new Date().toISOString(),
    source,
  };
}

export function useAiStudioState() {
  const { toast } = useToast();
  const [activePlatform, setActivePlatform] = useState<PlatformId>("linkedin");
  const [platforms, setPlatforms] = useState(createInitialPlatformStates);
  const [settings, setSettings] = useState<AiStudioSettings>(DEFAULT_AI_SETTINGS);
  const [loadingPhase, setLoadingPhase] = useState<LoadingPhase>("idle");
  const [settingsOpen, setSettingsOpen] = useState(true);
  const [versionsOpen, setVersionsOpen] = useState(false);
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const [compareVersionId, setCompareVersionId] = useState<string | null>(null);
  const [mobilePanel, setMobilePanel] = useState<MobilePanel>("workspace");
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null);
  const [typingContent, setTypingContent] = useState("");

  const current = platforms[activePlatform];

  const displayContent =
    loadingPhase === "generating" || loadingPhase === "regenerating"
      ? typingContent
      : current.content;

  const patchPlatform = useCallback(
    (platform: PlatformId, patch: Partial<PlatformWorkspaceState>) => {
      setPlatforms((prev) => ({
        ...prev,
        [platform]: { ...prev[platform], ...patch },
      }));
    },
    [],
  );

  const pushUndo = useCallback((platform: PlatformId, previousContent: string) => {
    setPlatforms((prev) => ({
      ...prev,
      [platform]: {
        ...prev[platform],
        undoStack: [...prev[platform].undoStack, previousContent],
        redoStack: [],
      },
    }));
  }, []);

  const addVersion = useCallback(
    (
      platform: PlatformId,
      content: string,
      hashtags: readonly string[],
      cta: string,
      source: ContentVersion["source"],
    ) => {
      setPlatforms((prev) => {
        const state = prev[platform];
        const versions = [
          ...state.versions,
          createVersion(content, hashtags, cta, source, state.versions.length),
        ];
        return {
          ...prev,
          [platform]: {
            ...state,
            content,
            hashtags,
            cta,
            versions,
            activeVersionIndex: versions.length - 1,
            isGenerated: true,
            approvalStatus: state.approvalStatus === "approved" ? "changes" : state.approvalStatus,
          },
        };
      });
    },
    [],
  );

  const simulateTyping = useCallback(async (fullText: string) => {
    setTypingContent("");
    const chunkSize = Math.max(8, Math.floor(fullText.length / 24));
    for (let index = 0; index < fullText.length; index += chunkSize) {
      setTypingContent(fullText.slice(0, index + chunkSize));
      await delay(40);
    }
    setTypingContent(fullText);
  }, []);

  const runGeneration = useCallback(
    async (platform: PlatformId, mode: "generate" | "regenerate") => {
      const mock = aiStudioService.getPlatformContent(platform);
      setLoadingPhase("thinking");
      await delay(900);
      setLoadingPhase(mode === "generate" ? "generating" : "regenerating");

      let content = applyToneTransform(mock.content, settings.tone);
      if (settings.length === "short") content = applyShorten(content, 0.55);
      if (settings.length === "long") content = applyExpand(content);

      pushUndo(platform, platforms[platform].content);
      await simulateTyping(content);

      const hashtags = settings.generateHashtags ? mock.hashtags : [];
      const cta = settings.generateCta ? mock.cta : "";
      addVersion(platform, content, hashtags, cta, "ai");
      setLoadingPhase("idle");
      setTypingContent("");
      toast({
        title: mode === "generate" ? "Content generated" : "Content regenerated",
        description: `${platform} variant is ready to review.`,
      });
    },
    [addVersion, platforms, pushUndo, settings, simulateTyping, toast],
  );

  const generate = useCallback(
    () => runGeneration(activePlatform, "generate"),
    [activePlatform, runGeneration],
  );
  const regenerate = useCallback(
    () => runGeneration(activePlatform, "regenerate"),
    [activePlatform, runGeneration],
  );

  const transformContent = useCallback(
    async (transform: "improve" | "expand" | "shorten" | AiStudioSettings["tone"]) => {
      const state = platforms[activePlatform];
      if (!state.content && !state.isGenerated) {
        toast({ title: "Nothing to transform", description: "Generate content first." });
        return;
      }
      setLoadingPhase("regenerating");
      await delay(600);
      let next = state.content;
      if (transform === "improve") next = applyImprove(next);
      else if (transform === "expand") next = applyExpand(next);
      else if (transform === "shorten") next = applyShorten(next);
      else next = applyToneTransform(next, transform);
      pushUndo(activePlatform, state.content);
      addVersion(activePlatform, next, state.hashtags, state.cta, "transform");
      setLoadingPhase("idle");
      toast({ title: "Content updated", description: "A new version was saved to history." });
    },
    [activePlatform, addVersion, platforms, pushUndo, toast],
  );

  const updateContent = useCallback(
    (content: string) => {
      const previous = platforms[activePlatform].content;
      if (previous !== content) pushUndo(activePlatform, previous);
      patchPlatform(activePlatform, {
        content,
        approvalStatus:
          platforms[activePlatform].approvalStatus === "approved"
            ? "changes"
            : platforms[activePlatform].approvalStatus,
      });
    },
    [activePlatform, patchPlatform, platforms, pushUndo],
  );

  const undo = useCallback(() => {
    setPlatforms((prev) => {
      const state = prev[activePlatform];
      if (state.undoStack.length === 0) return prev;
      const previous = state.undoStack[state.undoStack.length - 1];
      return {
        ...prev,
        [activePlatform]: {
          ...state,
          content: previous,
          redoStack: [...state.redoStack, state.content],
          undoStack: state.undoStack.slice(0, -1),
        },
      };
    });
  }, [activePlatform]);

  const redo = useCallback(() => {
    setPlatforms((prev) => {
      const state = prev[activePlatform];
      if (state.redoStack.length === 0) return prev;
      const next = state.redoStack[state.redoStack.length - 1];
      return {
        ...prev,
        [activePlatform]: {
          ...state,
          content: next,
          undoStack: [...state.undoStack, state.content],
          redoStack: state.redoStack.slice(0, -1),
        },
      };
    });
  }, [activePlatform]);

  const approve = useCallback(() => {
    patchPlatform(activePlatform, { approvalStatus: "approved" });
    toast({
      title: "Content approved",
      description: `${activePlatform} variant is ready for scheduling.`,
    });
  }, [activePlatform, patchPlatform, toast]);

  const reject = useCallback(() => {
    patchPlatform(activePlatform, { approvalStatus: "rejected" });
    toast({ title: "Content rejected", description: "Regenerate or edit to address feedback." });
  }, [activePlatform, patchPlatform, toast]);

  const saveDraft = useCallback(async () => {
    setLoadingPhase("saving");
    await delay(500);
    setLastSavedAt(new Date().toISOString());
    setLoadingPhase("idle");
    toast({ title: "Draft saved", description: "Your AI Studio progress is saved locally." });
  }, [toast]);

  const restoreVersion = useCallback(
    (versionId: string) => {
      const state = platforms[activePlatform];
      const index = state.versions.findIndex((version) => version.id === versionId);
      if (index < 0) return;
      const version = state.versions[index];
      if (!version) return;
      pushUndo(activePlatform, state.content);
      patchPlatform(activePlatform, {
        content: version.content,
        hashtags: version.hashtags,
        cta: version.cta,
        activeVersionIndex: index,
      });
      toast({ title: "Version restored", description: version.label });
    },
    [activePlatform, patchPlatform, platforms, pushUndo, toast],
  );

  const canUndo = current.undoStack.length > 0;
  const canRedo = current.redoStack.length > 0;
  const isLoading = loadingPhase !== "idle";

  const allContent = useMemo(
    () => Object.values(platforms).some((state) => state.isGenerated),
    [platforms],
  );

  return {
    activePlatform,
    setActivePlatform,
    platforms,
    current,
    displayContent,
    settings,
    setSettings,
    loadingPhase,
    settingsOpen,
    setSettingsOpen,
    versionsOpen,
    setVersionsOpen,
    suggestionsOpen,
    setSuggestionsOpen,
    compareVersionId,
    setCompareVersionId,
    mobilePanel,
    setMobilePanel,
    lastSavedAt,
    generate,
    regenerate,
    transformContent,
    updateContent,
    undo,
    redo,
    approve,
    reject,
    saveDraft,
    restoreVersion,
    canUndo,
    canRedo,
    isLoading,
    allContent,
  };
}
