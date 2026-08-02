"use client";

import { motion } from "framer-motion";

import { Progress } from "@/components/feedback";
import { WIZARD_STEP_COUNT, WIZARD_STEPS } from "@/constants/upload-wizard";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";

import { estimatedMinutesRemaining, wizardProgressPercent } from "./wizard-types";

export type WizardProgressHeaderProps = {
  currentStep: number;
};

export function WizardProgressHeader({
  currentStep,
}: WizardProgressHeaderProps): React.JSX.Element {
  const step = WIZARD_STEPS.find((item) => item.id === currentStep);
  const percent = wizardProgressPercent(currentStep);
  const minutesLeft = estimatedMinutesRemaining(currentStep);

  return (
    <header className="bg-card rounded-xl border p-4 sm:p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-eyebrow">Upload wizard</p>
          <h1 className="text-heading-2 mt-1">{step?.title ?? "Create project"}</h1>
          {step?.description && (
            <p className="text-muted-foreground mt-1 text-sm">{step.description}</p>
          )}
        </div>
        <div className="text-left sm:text-right">
          <p className="text-muted-foreground text-xs">
            Step {currentStep} of {WIZARD_STEP_COUNT}
          </p>
          <p className="text-sm font-semibold tabular-nums">{percent}% complete</p>
          {currentStep < 8 && (
            <p className="text-muted-foreground text-xs">~{minutesLeft} min remaining</p>
          )}
        </div>
      </div>
      <motion.div
        className="mt-4"
        initial={false}
        animate={{ opacity: 1 }}
        transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
      >
        <Progress value={percent} label="Overall progress" />
      </motion.div>
    </header>
  );
}
