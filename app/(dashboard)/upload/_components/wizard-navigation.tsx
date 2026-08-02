"use client";

import Link from "next/link";

import { PrimaryButton, SecondaryButton } from "@/components/buttons";
import { Button } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";

export type WizardNavigationProps = {
  currentStep: number;
  onBack: () => void;
  onNext: () => void;
  onSaveDraft: () => void;
  onCancel: () => void;
  nextLabel?: string;
  isNextDisabled?: boolean;
  showBack?: boolean;
};

export function WizardNavigation({
  currentStep,
  onBack,
  onNext,
  onSaveDraft,
  onCancel,
  nextLabel = "Next",
  isNextDisabled = false,
  showBack = true,
}: WizardNavigationProps): React.JSX.Element {
  const isFinishStep = currentStep === 8;

  if (isFinishStep) {
    return (
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-center">
        <SecondaryButton asChild>
          <Link href={ROUTES.dashboard}>Return to dashboard</Link>
        </SecondaryButton>
        <SecondaryButton onClick={onCancel}>Create another project</SecondaryButton>
        <PrimaryButton asChild>
          <Link href={ROUTES.aiStudio}>Open AI Studio</Link>
        </PrimaryButton>
      </div>
    );
  }

  return (
    <div className="bg-card/80 flex flex-col gap-3 border-t pt-4 backdrop-blur-sm sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-wrap gap-2">
        {showBack && currentStep > 1 && (
          <SecondaryButton type="button" onClick={onBack}>
            Back
          </SecondaryButton>
        )}
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
      <div className="flex flex-wrap gap-2 sm:justify-end">
        <SecondaryButton type="button" onClick={onSaveDraft}>
          Save draft
        </SecondaryButton>
        <PrimaryButton type="button" onClick={onNext} disabled={isNextDisabled}>
          {currentStep === 7 ? "Create project" : nextLabel}
        </PrimaryButton>
      </div>
    </div>
  );
}
