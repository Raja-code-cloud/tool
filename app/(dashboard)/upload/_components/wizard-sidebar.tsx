"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

import { WIZARD_STEPS } from "@/constants/upload-wizard";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { cn } from "@/lib/utils/cn";

import { validateStep, type WizardFormState } from "./wizard-types";

export type WizardSidebarProps = {
  currentStep: number;
  form: WizardFormState;
  onStepSelect: (step: number) => void;
  className?: string;
};

function canNavigateToStep(step: number, form: WizardFormState): boolean {
  if (step === 1) return true;
  for (let index = 1; index < step; index += 1) {
    if (!validateStep(index, form).valid) return false;
  }
  return true;
}

export function WizardSidebar({
  currentStep,
  form,
  onStepSelect,
  className,
}: WizardSidebarProps): React.JSX.Element {
  return (
    <nav aria-label="Upload wizard steps" className={cn("flex flex-col gap-1", className)}>
      <ol className="grid gap-1">
        {WIZARD_STEPS.map((step) => {
          const isCurrent = step.id === currentStep;
          const isComplete = step.id < currentStep && validateStep(step.id, form).valid;
          const isEnabled = canNavigateToStep(step.id, form);
          const Icon = step.icon;

          return (
            <li key={step.key}>
              <button
                type="button"
                disabled={!isEnabled}
                aria-current={isCurrent ? "step" : undefined}
                onClick={() => isEnabled && onStepSelect(step.id)}
                className={cn(
                  "flex w-full items-start gap-3 rounded-lg border px-3 py-2.5 text-left transition-colors",
                  isCurrent && "border-primary bg-accent",
                  !isCurrent && isEnabled && "hover:bg-muted/60 border-transparent",
                  !isEnabled && "cursor-not-allowed opacity-50",
                )}
              >
                <span
                  className={cn(
                    "mt-0.5 grid size-8 shrink-0 place-items-center rounded-full border text-xs font-semibold",
                    isComplete && "border-success bg-success/15 text-success",
                    isCurrent && !isComplete && "border-primary bg-primary text-primary-foreground",
                    !isCurrent && !isComplete && "border-border bg-muted text-muted-foreground",
                  )}
                  aria-hidden="true"
                >
                  {isComplete ? <Check className="size-4" /> : <Icon className="size-4" />}
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-semibold">{step.title}</span>
                  <span className="text-muted-foreground mt-0.5 block text-xs">
                    {step.description}
                  </span>
                </span>
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export type WizardMobileStepperProps = WizardSidebarProps;

export function WizardMobileStepper({ currentStep }: WizardMobileStepperProps): React.JSX.Element {
  const step = WIZARD_STEPS.find((item) => item.id === currentStep);
  return (
    <div className="bg-card desktop:hidden rounded-lg border p-3">
      <p className="text-muted-foreground text-xs font-medium">
        Step {currentStep} of {WIZARD_STEPS.length}
      </p>
      <p className="mt-1 text-sm font-semibold">{step?.title}</p>
      <motion.div
        className="bg-muted mt-3 h-1.5 overflow-hidden rounded-full"
        initial={false}
        animate={{ opacity: 1 }}
        transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
      >
        <motion.div
          className="bg-primary h-full rounded-full"
          initial={false}
          animate={{
            width: `${Math.round(((currentStep - 1) / (WIZARD_STEPS.length - 1)) * 100)}%`,
          }}
          transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
        />
      </motion.div>
    </div>
  );
}
