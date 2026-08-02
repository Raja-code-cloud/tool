"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { DRAFT_STORAGE_KEY } from "@/constants/upload-wizard";
import { useToast } from "@/hooks/use-toast";
import { getApiErrorMessage } from "@/lib/api/errors";
import type { ContentType } from "@/lib/domain/content";
import { readVersionedStorage, removeStorageKey, writeVersionedStorage } from "@/lib/security";
import { isBackendAuthEnabled, uploadService } from "@/lib/services";

import {
  INITIAL_WIZARD_STATE,
  validateStep,
  wizardProgressPercent,
  type FileAsset,
  type WizardFormState,
} from "./wizard-types";

type WizardMeta = {
  currentStep: number;
  isDirty: boolean;
  lastSavedAt: string | null;
  maxCompletedStep: number;
  projectId: string | null;
};

type PersistedDraft = {
  form: WizardFormState;
  meta: Omit<WizardMeta, "isDirty">;
};

const UPLOAD_KIND_MAP: Record<string, ContentType> = {
  poster: "poster",
  article: "article",
  video: "video",
  thumbnail: "thumbnail",
};

function isWizardFormState(value: unknown): value is WizardFormState {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<WizardFormState>;
  return (
    typeof candidate.projectName === "string" &&
    typeof candidate.description === "string" &&
    typeof candidate.category === "string" &&
    typeof candidate.tags === "string" &&
    typeof candidate.articleContent === "string" &&
    Array.isArray(candidate.platforms)
  );
}

function isPersistedDraft(value: unknown): value is PersistedDraft {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<PersistedDraft>;
  if (!candidate.form || !candidate.meta || typeof candidate.meta !== "object") return false;
  const meta = candidate.meta as Partial<PersistedDraft["meta"]>;
  return (
    isWizardFormState(candidate.form) &&
    typeof meta.currentStep === "number" &&
    typeof meta.maxCompletedStep === "number" &&
    (meta.lastSavedAt === null || typeof meta.lastSavedAt === "string") &&
    (meta.projectId === null || typeof meta.projectId === "string")
  );
}

function stripFileAssets(state: WizardFormState): WizardFormState {
  return {
    ...state,
    poster: state.poster ? { ...state.poster, previewUrl: "" } : null,
    articleFile: state.articleFile ? { ...state.articleFile, previewUrl: "" } : null,
    video: state.video ? { ...state.video, previewUrl: "" } : null,
    thumbnail: state.thumbnail ? { ...state.thumbnail, previewUrl: "" } : null,
  };
}

function createProjectId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `project-${Date.now()}`;
}

export function useWizardState() {
  const { toast } = useToast();
  const [form, setForm] = useState<WizardFormState>(INITIAL_WIZARD_STATE);
  const [currentStep, setCurrentStep] = useState(1);
  const [isDirty, setIsDirty] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null);
  const [maxCompletedStep, setMaxCompletedStep] = useState(0);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [stepErrors, setStepErrors] = useState<Readonly<Record<string, string>>>({});
  const [draftRestored, setDraftRestored] = useState(false);
  const timersRef = useRef<Map<string, ReturnType<typeof setInterval>>>(new Map());
  const filesRef = useRef<Map<string, File>>(new Map());
  const abortControllersRef = useRef<Map<string, AbortController>>(new Map());

  const progressPercent = useMemo(() => wizardProgressPercent(currentStep), [currentStep]);
  const validation = useMemo(() => validateStep(currentStep, form), [currentStep, form]);

  useEffect(() => {
    if (draftRestored) return;
    const result = readVersionedStorage(DRAFT_STORAGE_KEY, isPersistedDraft);
    if (result.ok) {
      setForm(result.data.form);
      setCurrentStep(result.data.meta.currentStep);
      setLastSavedAt(result.data.meta.lastSavedAt);
      setMaxCompletedStep(result.data.meta.maxCompletedStep);
      setProjectId(result.data.meta.projectId);
      setIsDirty(false);
    }
    setDraftRestored(true);
  }, [draftRestored]);

  const patchForm = useCallback((patch: Partial<WizardFormState>) => {
    setForm((prev) => ({ ...prev, ...patch }));
    setIsDirty(true);
    setStepErrors({});
  }, []);

  const clearUploadTimer = useCallback((key: string) => {
    const timer = timersRef.current.get(key);
    if (timer) {
      clearInterval(timer);
      timersRef.current.delete(key);
    }
  }, []);

  const simulateUpload = useCallback(
    (key: string, file: File, onUpdate: (asset: FileAsset) => void) => {
      clearUploadTimer(key);
      const previewUrl = URL.createObjectURL(file);
      let progress = 0;

      const initial: FileAsset = {
        name: file.name,
        size: file.size,
        type: file.type,
        previewUrl,
        progress: 0,
        status: "uploading",
      };
      onUpdate(initial);

      const timer = setInterval(() => {
        progress = Math.min(progress + 12 + Math.random() * 8, 100);
        if (progress >= 100) {
          clearUploadTimer(key);
          onUpdate({ ...initial, progress: 100, status: "complete" });
        } else {
          onUpdate({ ...initial, progress: Math.round(progress), status: "uploading" });
        }
      }, 180);
      timersRef.current.set(key, timer);
    },
    [clearUploadTimer],
  );

  const uploadFile = useCallback(
    (key: string, file: File, onUpdate: (asset: FileAsset) => void) => {
      filesRef.current.set(key, file);
      const assetType = UPLOAD_KIND_MAP[key];
      if (!uploadService || !assetType || !isBackendAuthEnabled) {
        simulateUpload(key, file, onUpdate);
        return;
      }

      clearUploadTimer(key);
      abortControllersRef.current.get(key)?.abort();
      const controller = new AbortController();
      abortControllersRef.current.set(key, controller);

      const previewUrl = URL.createObjectURL(file);
      const initial: FileAsset = {
        name: file.name,
        size: file.size,
        type: file.type,
        previewUrl,
        progress: 0,
        status: "uploading",
      };
      onUpdate(initial);

      const activeProjectId = projectId ?? createProjectId();
      if (!projectId) setProjectId(activeProjectId);

      void uploadService
        .uploadAsset({
          assetType,
          title: file.name,
          file,
          projectId: activeProjectId,
          signal: controller.signal,
          onProgress: (percent) => {
            onUpdate({ ...initial, progress: percent, status: "uploading" });
          },
        })
        .then((asset) => {
          onUpdate({
            ...initial,
            progress: 100,
            status: "complete",
            assetId: asset.id,
            version: asset.version,
          });
        })
        .catch((error) => {
          onUpdate({
            ...initial,
            progress: 0,
            status: "failed",
            errorMessage: getApiErrorMessage(error),
          });
        })
        .finally(() => {
          abortControllersRef.current.delete(key);
        });
    },
    [clearUploadTimer, projectId, simulateUpload],
  );

  const retryUpload = useCallback(
    (key: string, onUpdate: (asset: FileAsset) => void) => {
      const file = filesRef.current.get(key);
      if (!file) return;
      uploadFile(key, file, onUpdate);
    },
    [uploadFile],
  );

  const cancelUpload = useCallback(
    (key: string) => {
      abortControllersRef.current.get(key)?.abort();
      abortControllersRef.current.delete(key);
      clearUploadTimer(key);
    },
    [clearUploadTimer],
  );

  const revokeAsset = useCallback((asset: FileAsset | null) => {
    if (asset?.previewUrl) URL.revokeObjectURL(asset.previewUrl);
  }, []);

  useEffect(() => {
    const timers = timersRef.current;
    return () => {
      timers.forEach((timer) => clearInterval(timer));
      timers.clear();
      abortControllersRef.current.forEach((controller) => controller.abort());
      abortControllersRef.current.clear();
    };
  }, []);

  const uploadArticleFromPaste = useCallback(
    (content: string, projectName: string, onUpdate: (asset: FileAsset) => void) => {
      const blob = new Blob([content], { type: "text/plain" });
      const safeName = projectName.trim().replace(/\s+/g, "-").slice(0, 80) || "article";
      const file = new File([blob], `${safeName}.txt`, { type: "text/plain" });
      uploadFile("article", file, onUpdate);
    },
    [uploadFile],
  );

  const goToStep = useCallback(
    (step: number) => {
      if (step < 1 || step > 8) return false;
      if (step > currentStep) {
        const result = validateStep(currentStep, form);
        if (!result.valid) {
          setStepErrors(result.errors);
          return false;
        }
        if (
          currentStep === 3 &&
          form.articleMode === "paste" &&
          !form.articleFile &&
          form.articleContent.trim().length >= 50
        ) {
          uploadArticleFromPaste(form.articleContent, form.projectName, (asset) =>
            patchForm({ articleFile: asset }),
          );
        }
        setMaxCompletedStep((prev) => Math.max(prev, currentStep));
      }
      setCurrentStep(step);
      setStepErrors({});
      return true;
    },
    [currentStep, form, patchForm, uploadArticleFromPaste],
  );

  const goNext = useCallback(
    (): boolean => goToStep(currentStep + 1) ?? false,
    [currentStep, goToStep],
  );
  const goBack = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setStepErrors({});
    }
  }, [currentStep]);

  const saveDraft = useCallback(() => {
    const payload: PersistedDraft = {
      form: stripFileAssets(form),
      meta: {
        currentStep,
        lastSavedAt: new Date().toISOString(),
        maxCompletedStep,
        projectId,
      },
    };
    const saved = writeVersionedStorage(DRAFT_STORAGE_KEY, payload);
    if (saved) {
      setLastSavedAt(payload.meta.lastSavedAt);
      setIsDirty(false);
      toast({
        title: "Draft saved",
        description: isBackendAuthEnabled
          ? "Wizard metadata saved locally. Uploaded assets remain in your workspace."
          : "Your progress is saved locally on this device for up to 7 days.",
      });
    } else {
      toast({ title: "Could not save draft", description: "Local storage is unavailable." });
    }
  }, [currentStep, form, maxCompletedStep, projectId, toast]);

  const clearDraftStorage = useCallback(() => {
    removeStorageKey(DRAFT_STORAGE_KEY);
  }, []);

  const resetWizard = useCallback(() => {
    revokeAsset(form.poster);
    revokeAsset(form.articleFile);
    revokeAsset(form.video);
    revokeAsset(form.thumbnail);
    ["poster", "article", "video", "thumbnail"].forEach((key) => cancelUpload(key));
    filesRef.current.clear();
    setForm(INITIAL_WIZARD_STATE);
    setCurrentStep(1);
    setIsDirty(false);
    setLastSavedAt(null);
    setMaxCompletedStep(0);
    setProjectId(null);
    setStepErrors({});
    clearDraftStorage();
  }, [cancelUpload, clearDraftStorage, form, revokeAsset]);

  const createProject = useCallback(async (): Promise<boolean> => {
    if (!isBackendAuthEnabled) {
      return true;
    }

    const pendingAssets = [
      form.poster,
      form.articleFile,
      form.videoSkipped ? null : form.video,
      form.thumbnailSkipped ? null : form.thumbnail,
    ].filter((asset): asset is NonNullable<typeof asset> => asset !== null);

    const failed = pendingAssets.filter((asset) => asset.status === "failed");
    if (failed.length > 0) {
      toast({
        title: "Upload failed",
        description: "Retry failed uploads before creating the project.",
      });
      return false;
    }

    const uploading = pendingAssets.filter((asset) => asset.status === "uploading");
    if (uploading.length > 0) {
      toast({
        title: "Upload in progress",
        description: "Wait for uploads to finish before creating the project.",
      });
      return false;
    }

    if (form.articleMode === "paste" && form.articleContent.trim() && !form.articleFile) {
      toast({
        title: "Article not uploaded",
        description: "Upload or paste your article before finishing.",
      });
      return false;
    }

    return true;
  }, [form, toast]);

  return {
    form,
    patchForm,
    currentStep,
    setCurrentStep: goToStep,
    goNext,
    goBack,
    isDirty,
    lastSavedAt,
    maxCompletedStep,
    projectId,
    progressPercent,
    validation,
    stepErrors,
    setStepErrors,
    uploadFile,
    retryUpload,
    cancelUpload,
    revokeAsset,
    saveDraft,
    resetWizard,
    clearDraftStorage,
    createProject,
  };
}
