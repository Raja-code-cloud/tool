"use client";

import { motion } from "framer-motion";
import { CheckCircle2, RefreshCw } from "lucide-react";
import Image from "next/image";

import { PrimaryButton, SecondaryButton } from "@/components/buttons";
import { Card, CardHeader } from "@/components/cards";
import { Alert } from "@/components/feedback";
import { UploadProgress, UploadZone } from "@/components/upload";
import { POSTER_ACCEPT, POSTER_MAX_BYTES } from "@/constants/upload-wizard";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";

import type { WizardFormState } from "../wizard-types";

export type StepPosterUploadProps = {
  form: WizardFormState;
  errors: Readonly<Record<string, string>>;
  onUpload: (file: File) => void;
  onRemove: () => void;
};

export function StepPosterUpload({
  form,
  errors,
  onUpload,
  onRemove,
}: StepPosterUploadProps): React.JSX.Element {
  const poster = form.poster;

  return (
    <Card>
      <CardHeader
        title="Poster upload"
        description="Upload a hero image for your campaign. PNG, JPG, or WEBP up to 10 MB."
      />
      {!poster && (
        <UploadZone
          accept={POSTER_ACCEPT}
          maximumSize={POSTER_MAX_BYTES}
          supportedTypes="PNG, JPG, WEBP"
          prompt="Drag and drop your poster here"
          onFiles={(files) => {
            const file = files[0];
            if (file) onUpload(file);
          }}
          className="min-h-56"
        />
      )}
      {poster && (
        <div className="grid gap-4">
          <div className="bg-muted relative overflow-hidden rounded-lg border">
            <Image
              src={poster.previewUrl}
              alt="Poster preview"
              width={960}
              height={540}
              unoptimized
              className="mx-auto max-h-80 w-full object-contain"
            />
            {poster.status === "complete" && (
              <motion.div
                className="bg-success text-success-foreground absolute top-3 right-3 grid size-9 place-items-center rounded-full shadow-sm"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: MOTION_DURATION.dialog, ease: MOTION_EASING.enter }}
              >
                <CheckCircle2 className="size-5" aria-hidden="true" />
                <span className="sr-only">Upload complete</span>
              </motion.div>
            )}
          </div>
          <UploadProgress value={poster.progress} label={`Uploading ${poster.name}`} />
          <div className="flex flex-wrap gap-2">
            <SecondaryButton type="button" onClick={onRemove}>
              Remove image
            </SecondaryButton>
            <PrimaryButton type="button" onClick={onRemove}>
              <RefreshCw className="size-4" aria-hidden="true" />
              Replace image
            </PrimaryButton>
          </div>
        </div>
      )}
      {errors.poster && (
        <Alert variant="danger" title="Poster required" className="mt-4">
          {errors.poster}
        </Alert>
      )}
    </Card>
  );
}
