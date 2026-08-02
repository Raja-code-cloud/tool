"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { DRAFT_STORAGE_KEY } from "@/constants/upload-wizard";
import { useToast } from "@/hooks/use-toast";
import { readVersionedStorage, removeStorageKey, writeVersionedStorage } from "@/lib/security";

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
};

type PersistedDraft = {
  form: WizardFormState;
  meta: Omit<WizardMeta, "isDirty">;
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
    (meta.lastSavedAt === null || typeof meta.lastSavedAt === "string")
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

export function useWizardState() {
  const { toast } = useToast();
  const [form, setForm] = useState<WizardFormState>(INITIAL_WIZARD_STATE);
  const [currentStep, setCurrentStep] = useState(1);
  const [isDirty, setIsDirty] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null);
  const [maxCompletedStep, setMaxCompletedStep] = useState(0);
  const [stepErrors, setStepErrors] = useState<Readonly<Record<string, string>>>({});
  const [draftRestored, setDraftRestored] = useState(false);
  const timersRef = useRef<Map<string, ReturnType<typeof setInterval>>>(new Map());

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

  const revokeAsset = useCallback((asset: FileAsset | null) => {
    if (asset?.previewUrl) URL.revokeObjectURL(asset.previewUrl);
  }, []);

  useEffect(() => {
    const timers = timersRef.current;
    return () => {
      timers.forEach((timer) => clearInterval(timer));
      timers.clear();
    };
  }, []);

  const goToStep = useCallback(
    (step: number) => {
      if (step < 1 || step > 8) return false;
      if (step > currentStep) {
        const result = validateStep(currentStep, form);
        if (!result.valid) {
          setStepErrors(result.errors);
          return false;
        }
        setMaxCompletedStep((prev) => Math.max(prev, currentStep));
      }
      setCurrentStep(step);
      setStepErrors({});
      return true;
    },
    [currentStep, form],
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
      meta: { currentStep, lastSavedAt: new Date().toISOString(), maxCompletedStep },
    };
    const saved = writeVersionedStorage(DRAFT_STORAGE_KEY, payload);
    if (saved) {
      setLastSavedAt(payload.meta.lastSavedAt);
      setIsDirty(false);
      toast({
        title: "Draft saved",
        description: "Your progress is saved locally on this device for up to 7 days.",
      });
    } else {
      toast({ title: "Could not save draft", description: "Local storage is unavailable." });
    }
  }, [currentStep, form, maxCompletedStep, toast]);

  const clearDraftStorage = useCallback(() => {
    removeStorageKey(DRAFT_STORAGE_KEY);
  }, []);

  const resetWizard = useCallback(() => {
    revokeAsset(form.poster);
    revokeAsset(form.articleFile);
    revokeAsset(form.video);
    revokeAsset(form.thumbnail);
    setForm(INITIAL_WIZARD_STATE);
    setCurrentStep(1);
    setIsDirty(false);
    setLastSavedAt(null);
    setMaxCompletedStep(0);
    setStepErrors({});
    clearDraftStorage();
  }, [clearDraftStorage, form, revokeAsset]);

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
    progressPercent,
    validation,
    stepErrors,
    setStepErrors,
    simulateUpload,
    revokeAsset,
    saveDraft,
    resetWizard,
    clearDraftStorage,
  };
}
