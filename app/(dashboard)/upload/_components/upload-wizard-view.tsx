"use client";

import { AnimatePresence, motion } from "framer-motion";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { LiveRegion, Skeleton } from "@/components/feedback";
import { FormErrorSummary } from "@/components/forms";
import { PageContainer, Stack } from "@/components/layout";
import { ROUTES } from "@/constants/navigation";
import { useToast } from "@/hooks/use-toast";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { validateUploadFile, type UploadKind } from "@/lib/security";
import { readTextFile, readVideoDuration } from "@/lib/utils/upload-wizard";

import { StepProjectInfo } from "./steps/step-project-info";
import { useWizardState } from "./use-wizard-state";
import { WizardExitDialog } from "./wizard-exit-dialog";
import { WizardNavigation } from "./wizard-navigation";
import { WizardProgressHeader } from "./wizard-progress-header";
import { WizardMobileStepper, WizardSidebar } from "./wizard-sidebar";
import { firstInvalidWizardFieldId, validateStep, wizardErrorFieldId } from "./wizard-types";

const stepLoading = (): React.JSX.Element => <Skeleton className="h-[32rem] w-full rounded-xl" />;
const StepPosterUpload = dynamic(
  () => import("./steps/step-poster-upload").then((module) => module.StepPosterUpload),
  { loading: stepLoading },
);
const StepMasterArticle = dynamic(
  () => import("./steps/step-master-article").then((module) => module.StepMasterArticle),
  { loading: stepLoading },
);
const StepVideoUpload = dynamic(
  () => import("./steps/step-video-upload").then((module) => module.StepVideoUpload),
  { loading: stepLoading },
);
const StepThumbnailUpload = dynamic(
  () => import("./steps/step-thumbnail-upload").then((module) => module.StepThumbnailUpload),
  { loading: stepLoading },
);
const StepAiSettings = dynamic(
  () => import("./steps/step-ai-settings").then((module) => module.StepAiSettings),
  { loading: stepLoading },
);
const StepReview = dynamic(
  () => import("./steps/step-review").then((module) => module.StepReview),
  { loading: stepLoading },
);
const StepFinish = dynamic(
  () => import("./steps/step-finish").then((module) => module.StepFinish),
  { loading: stepLoading },
);

export function UploadWizardView(): React.JSX.Element {
  const router = useRouter();
  const { toast } = useToast();
  const {
    form,
    patchForm,
    currentStep,
    setCurrentStep,
    goNext,
    goBack,
    isDirty,
    stepErrors,
    simulateUpload,
    revokeAsset,
    saveDraft,
    resetWizard,
    clearDraftStorage,
  } = useWizardState();

  const [exitOpen, setExitOpen] = useState(false);
  const [pendingExitHref, setPendingExitHref] = useState<string | null>(null);
  const errorSummaryRef = useRef<HTMLDivElement>(null);

  const focusFirstWizardError = useCallback((errors: Readonly<Record<string, string>>) => {
    const fieldId = firstInvalidWizardFieldId(errors);
    if (fieldId) {
      document.getElementById(fieldId)?.focus();
      return;
    }
    errorSummaryRef.current?.focus();
  }, []);

  useEffect(() => {
    if (Object.keys(stepErrors).length > 0) {
      focusFirstWizardError(stepErrors);
    }
  }, [focusFirstWizardError, stepErrors]);

  const rejectUpload = useCallback(
    (kind: UploadKind, file: File) => {
      const result = validateUploadFile(file, kind);
      if (!result.valid) {
        toast({ title: "File rejected", description: result.error });
        return false;
      }
      return true;
    },
    [toast],
  );

  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (isDirty && currentStep < 8) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [currentStep, isDirty]);

  const handlePosterUpload = useCallback(
    (file: File) => {
      if (!rejectUpload("poster", file)) return;
      simulateUpload("poster", file, (asset) => patchForm({ poster: asset }));
    },
    [patchForm, rejectUpload, simulateUpload],
  );

  const handlePosterRemove = useCallback(() => {
    revokeAsset(form.poster);
    patchForm({ poster: null });
  }, [form.poster, patchForm, revokeAsset]);

  const handleArticleUpload = useCallback(
    (file: File) => {
      if (!rejectUpload("article", file)) return;
      simulateUpload("article", file, (asset) => {
        patchForm({ articleFile: asset });
        if (
          asset.status === "complete" &&
          (file.type === "text/plain" || file.name.endsWith(".md"))
        ) {
          readTextFile(file).then((content) => patchForm({ articleContent: content }));
        }
      });
    },
    [patchForm, rejectUpload, simulateUpload],
  );

  const handleArticleRemove = useCallback(() => {
    revokeAsset(form.articleFile);
    patchForm({ articleFile: null });
  }, [form.articleFile, patchForm, revokeAsset]);

  const handleVideoUpload = useCallback(
    (file: File) => {
      if (!rejectUpload("video", file)) return;
      readVideoDuration(file).then((duration) => patchForm({ videoDuration: duration }));
      simulateUpload("video", file, (asset) => patchForm({ video: asset, videoSkipped: false }));
    },
    [patchForm, rejectUpload, simulateUpload],
  );

  const handleVideoRemove = useCallback(() => {
    revokeAsset(form.video);
    patchForm({ video: null, videoDuration: "" });
  }, [form.video, patchForm, revokeAsset]);

  const handleThumbnailUpload = useCallback(
    (file: File) => {
      if (!rejectUpload("thumbnail", file)) return;
      simulateUpload("thumbnail", file, (asset) =>
        patchForm({ thumbnail: asset, thumbnailSkipped: false }),
      );
    },
    [patchForm, rejectUpload, simulateUpload],
  );

  const handleThumbnailRemove = useCallback(() => {
    revokeAsset(form.thumbnail);
    patchForm({ thumbnail: null });
  }, [form.thumbnail, patchForm, revokeAsset]);

  const requestExit = useCallback(
    (href?: string) => {
      if (isDirty && currentStep < 8) {
        setPendingExitHref(href ?? ROUTES.dashboard);
        setExitOpen(true);
        return;
      }
      if (href) router.push(href);
      else resetWizard();
    },
    [currentStep, isDirty, resetWizard, router],
  );

  const confirmExit = useCallback(() => {
    resetWizard();
    if (pendingExitHref) router.push(pendingExitHref);
    setPendingExitHref(null);
  }, [pendingExitHref, resetWizard, router]);

  const allStepsValid = useMemo(() => {
    for (let step = 1; step <= 6; step += 1) {
      if (!validateStep(step, form).valid) return false;
    }
    return true;
  }, [form]);

  const handleNext = useCallback(() => {
    if (currentStep === 7) {
      if (!allStepsValid) {
        toast({
          title: "Complete all steps",
          description: "Review validation status before creating your project.",
        });
        return;
      }
      setCurrentStep(8);
      clearDraftStorage();
      toast({
        title: "Project created",
        description: `"${form.projectName}" was created successfully.`,
      });
      return;
    }
    goNext();
  }, [
    allStepsValid,
    clearDraftStorage,
    currentStep,
    form.projectName,
    goNext,
    setCurrentStep,
    toast,
  ]);

  const handleStepSelect = useCallback(
    (step: number) => {
      if (step > currentStep) {
        const moved = setCurrentStep(step);
        if (!moved) return;
      } else {
        setCurrentStep(step);
      }
    },
    [currentStep, setCurrentStep],
  );

  const renderStep = (): React.JSX.Element => {
    switch (currentStep) {
      case 1:
        return <StepProjectInfo form={form} errors={stepErrors} onChange={patchForm} />;
      case 2:
        return (
          <StepPosterUpload
            form={form}
            errors={stepErrors}
            onUpload={handlePosterUpload}
            onRemove={handlePosterRemove}
          />
        );
      case 3:
        return (
          <StepMasterArticle
            form={form}
            errors={stepErrors}
            onChange={patchForm}
            onUpload={handleArticleUpload}
            onRemoveFile={handleArticleRemove}
          />
        );
      case 4:
        return (
          <StepVideoUpload
            form={form}
            errors={stepErrors}
            onChange={patchForm}
            onUpload={handleVideoUpload}
            onRemove={handleVideoRemove}
          />
        );
      case 5:
        return (
          <StepThumbnailUpload
            form={form}
            errors={stepErrors}
            onChange={patchForm}
            onUpload={handleThumbnailUpload}
            onRemove={handleThumbnailRemove}
          />
        );
      case 6:
        return <StepAiSettings form={form} errors={stepErrors} onChange={patchForm} />;
      case 7:
        return <StepReview form={form} />;
      case 8:
        return <StepFinish form={form} />;
      default:
        return <StepProjectInfo form={form} errors={stepErrors} onChange={patchForm} />;
    }
  };

  return (
    <PageContainer className="pb-8">
      <Stack gap="lg">
        <WizardProgressHeader currentStep={currentStep} />
        <WizardMobileStepper
          currentStep={currentStep}
          form={form}
          onStepSelect={handleStepSelect}
        />

        <div className="desktop:grid-cols-[minmax(240px,280px)_1fr] desktop:items-start grid gap-6">
          <aside className="desktop:block hidden">
            <WizardSidebar currentStep={currentStep} form={form} onStepSelect={handleStepSelect} />
          </aside>

          <div className="min-w-0">
            {Object.keys(stepErrors).length > 0 && (
              <FormErrorSummary
                ref={errorSummaryRef}
                className="mb-4"
                errors={Object.entries(stepErrors).map(([key, message]) => ({
                  id: wizardErrorFieldId(key),
                  message,
                }))}
              />
            )}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -16 }}
                transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
              >
                {renderStep()}
              </motion.div>
            </AnimatePresence>

            <div className="mt-6">
              <WizardNavigation
                currentStep={currentStep}
                onBack={goBack}
                onNext={handleNext}
                onSaveDraft={saveDraft}
                onCancel={() => {
                  if (currentStep === 8) {
                    resetWizard();
                    setCurrentStep(1);
                    return;
                  }
                  requestExit(ROUTES.dashboard);
                }}
                isNextDisabled={currentStep === 7 && !allStepsValid}
              />
            </div>
          </div>
        </div>
      </Stack>

      <LiveRegion>{`Step ${currentStep} of 8`}</LiveRegion>
      <WizardExitDialog open={exitOpen} onOpenChange={setExitOpen} onConfirmExit={confirmExit} />
    </PageContainer>
  );
}
