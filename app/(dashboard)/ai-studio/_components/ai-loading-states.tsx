"use client";

import { motion } from "framer-motion";

import { Skeleton, SkeletonText, Spinner } from "@/components/feedback";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";

import type { LoadingPhase } from "./types";

export type AiLoadingOverlayProps = {
  phase: LoadingPhase;
};

const LABELS: Record<LoadingPhase, string> = {
  idle: "",
  thinking: "AI is thinking…",
  generating: "Generating content…",
  regenerating: "Regenerating…",
  saving: "Saving draft…",
};

export function AiLoadingOverlay({ phase }: AiLoadingOverlayProps): React.JSX.Element | null {
  if (phase === "idle") return null;

  return (
    <motion.div
      className="bg-background/80 absolute inset-0 z-10 grid place-items-center rounded-lg backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
      role="status"
      aria-live="polite"
    >
      <div className="grid gap-3 text-center">
        <Spinner label={LABELS[phase]} />
        <p className="text-sm font-medium">{LABELS[phase]}</p>
        {(phase === "generating" || phase === "regenerating") && (
          <div className="mx-auto w-48">
            <SkeletonText lines={2} />
          </div>
        )}
      </div>
    </motion.div>
  );
}

export function TypingCursor(): React.JSX.Element {
  return (
    <motion.span
      className="bg-primary inline-block h-4 w-0.5 align-middle"
      animate={{ opacity: [1, 0, 1] }}
      transition={{ duration: 0.9, repeat: Infinity, ease: "linear" }}
      aria-hidden="true"
    />
  );
}

export function ShimmerBlock({ className }: { className?: string }): React.JSX.Element {
  return <Skeleton className={className} />;
}
