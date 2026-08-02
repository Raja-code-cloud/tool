"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useToast } from "@/hooks/use-toast";
import { mapAiStudioError } from "@/lib/adapters/ai-studio-errors";
import type { AiStudioProject } from "@/lib/domain/ai-studio";
import type { GenerationScope } from "@/lib/domain/ai-studio-generation";
import type { PlatformId } from "@/lib/domain/platform";
import { aiStudioService } from "@/lib/services";
import { delay } from "@/lib/utils/ai-studio";

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

function transformToScope(
  transform: "improve" | "expand" | "shorten" | AiStudioSettings["tone"],
): { scope: GenerationScope; userPrompt?: string } {
  if (transform === "improve") {
    return { scope: "whole", userPrompt: "Improve clarity, engagement, and readability." };
  }
  if (transform === "expand") {
    return { scope: "whole", userPrompt: "Expand with more detail while staying on topic." };
  }
  if (transform === "shorten") {
    return { scope: "whole", userPrompt: "Shorten while preserving the core message." };
  }
  return { scope: "tone" };
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
  const [project, setProject] = useState<AiStudioProject | null>(null);
  const [suggestions, setSuggestions] = useState<readonly import("@/lib/domain/ai-studio").AiSuggestion[]>(
    [],
  );
  const [providers, setProviders] = useState<
    readonly import("@/lib/domain/ai-studio-generation").AiStudioProviderOption[]
  >([]);
  const [contentVersion, setContentVersion] = useState(1);
  const generationAbortRef = useRef<AbortController | null>(null);

  const current = platforms[activePlatform];

  const displayContent =
    loadingPhase === "generating" || loadingPhase === "regenerating"
      ? typingContent
      : current.content;

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      try {
        const [loadedProject, loadedSuggestions, loadedProviders] = await Promise.all([
          aiStudioService.getProject(),
          aiStudioService.listSuggestions(),
          aiStudioService.listProviders(),
        ]);
        if (cancelled) return;
        setProject(loadedProject);
        setSuggestions(loadedSuggestions);
        setProviders(loadedProviders);
        if (!settings.modelId && loadedProviders[0]?.modelId) {
          setSettings((prev) => ({ ...prev, modelId: loadedProviders[0]?.modelId ?? null }));
        }
      } catch (error) {
        if (cancelled) return;
        const mapped = mapAiStudioError(error);
        toast({ title: mapped.title, description: mapped.description, variant: "destructive" });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [toast]);

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

  const simulateTyping = useCallback(async (fullText: string, signal?: AbortSignal) => {
    setTypingContent("");
    const chunkSize = Math.max(8, Math.floor(fullText.length / 24));
    for (let index = 0; index < fullText.length; index += chunkSize) {
      if (signal?.aborted) return;
      setTypingContent(fullText.slice(0, index + chunkSize));
      await delay(40);
    }
    if (!signal?.aborted) {
      setTypingContent(fullText);
    }
  }, []);

  const runGeneration = useCallback(
    async (
      platform: PlatformId,
      mode: "generate" | "regenerate",
      options?: { scope?: GenerationScope; userPrompt?: string },
    ) => {
      generationAbortRef.current?.abort();
      const controller = new AbortController();
      generationAbortRef.current = controller;

      setLoadingPhase("thinking");
      await delay(400);

      if (controller.signal.aborted) return;

      setLoadingPhase(mode === "generate" ? "generating" : "regenerating");

      try {
        const request = {
          platform,
          tone: settings.tone,
          length: settings.length,
          audience: settings.audience,
          generateHashtags: settings.generateHashtags,
          generateCta: settings.generateCta,
          modelId: settings.modelId,
          scope: options?.scope,
          userPrompt: options?.userPrompt,
          signal: controller.signal,
        };

        const result =
          mode === "regenerate"
            ? await aiStudioService.regenerate(request)
            : await aiStudioService.generate(request);

        pushUndo(platform, platforms[platform].content);
        await simulateTyping(result.content, controller.signal);

        if (controller.signal.aborted) return;

        addVersion(platform, result.content, result.hashtags, result.cta, "ai");
        setContentVersion(result.contentVersion);
        setLoadingPhase("idle");
        setTypingContent("");
        toast({
          title: mode === "generate" ? "Content generated" : "Content regenerated",
          description: `${platform} variant is ready to review.`,
        });
      } catch (error) {
        setLoadingPhase("idle");
        setTypingContent("");
        const mapped = mapAiStudioError(error);
        if (mapped.title !== "Generation cancelled") {
          toast({ title: mapped.title, description: mapped.description, variant: "destructive" });
        }
      } finally {
        if (generationAbortRef.current === controller) {
          generationAbortRef.current = null;
        }
      }
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

      const mapped = transformToScope(transform);
      const nextTone =
        mapped.scope === "tone" ? (transform as AiStudioSettings["tone"]) : settings.tone;

      if (mapped.scope === "tone") {
        setSettings((prev) => ({ ...prev, tone: nextTone }));
      }

      generationAbortRef.current?.abort();
      const controller = new AbortController();
      generationAbortRef.current = controller;

      setLoadingPhase("regenerating");
      try {
        const result = await aiStudioService.regenerate({
          platform: activePlatform,
          tone: nextTone,
          length: settings.length,
          audience: settings.audience,
          generateHashtags: settings.generateHashtags,
          generateCta: settings.generateCta,
          modelId: settings.modelId,
          scope: mapped.scope,
          userPrompt: mapped.userPrompt,
          signal: controller.signal,
        });

        pushUndo(activePlatform, state.content);
        await simulateTyping(result.content, controller.signal);
        if (controller.signal.aborted) return;

        addVersion(activePlatform, result.content, result.hashtags, result.cta, "transform");
        setContentVersion(result.contentVersion);
        toast({ title: "Content updated", description: "A new version was saved to history." });
      } catch (error) {
        const mapped = mapAiStudioError(error);
        if (mapped.title !== "Generation cancelled") {
          toast({ title: mapped.title, description: mapped.description, variant: "destructive" });
        }
      } finally {
        setLoadingPhase("idle");
        setTypingContent("");
        if (generationAbortRef.current === controller) {
          generationAbortRef.current = null;
        }
      }
    },
    [
      activePlatform,
      addVersion,
      platforms,
      pushUndo,
      settings,
      simulateTyping,
      toast,
    ],
  );

  const cancelGeneration = useCallback(() => {
    generationAbortRef.current?.abort();
    aiStudioService.cancelGeneration();
    setLoadingPhase("idle");
    setTypingContent("");
    toast({ title: "Generation cancelled", description: "You can adjust settings and try again." });
  }, [toast]);

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
    if (!project) {
      toast({ title: "Nothing to save", description: "Project metadata is still loading." });
      return;
    }

    setLoadingPhase("saving");
    try {
      const result = await aiStudioService.saveDraft({
        contentId: project.id,
        contentVersion,
        title: project.name,
        bodyText: current.content,
        metadata: {
          platform: activePlatform,
          hashtags: current.hashtags,
          callToAction: current.cta,
        },
      });
      setContentVersion(result.contentVersion);
      setLastSavedAt(result.savedAt);
      toast({ title: "Draft saved", description: "Your AI Studio progress is saved to the backend." });
    } catch (error) {
      const mapped = mapAiStudioError(error);
      toast({ title: mapped.title, description: mapped.description, variant: "destructive" });
    } finally {
      setLoadingPhase("idle");
    }
  }, [activePlatform, contentVersion, current.content, current.cta, current.hashtags, project, toast]);

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
    project,
    suggestions,
    providers,
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
    cancelGeneration,
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
