"use client";

import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";

import { EmptyState } from "@/components/feedback";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";

import type { WizardFormState } from "../wizard-types";

export type StepFinishProps = {
  form: WizardFormState;
};

export function StepFinish({ form }: StepFinishProps): React.JSX.Element {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
    >
      <EmptyState
        title="Project created successfully"
        description={`“${form.projectName}” is ready. Open AI Studio to generate platform variants, or create another project.`}
        icon={
          <motion.span
            initial={{ scale: 0.85, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: MOTION_DURATION.dialog, ease: MOTION_EASING.enter, delay: 0.1 }}
          >
            <CheckCircle2 aria-hidden="true" />
          </motion.span>
        }
        className="bg-card min-h-72 border-solid"
      />
    </motion.div>
  );
}
