"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Crop, RefreshCw } from "lucide-react";
import Image from "next/image";

import { PrimaryButton, SecondaryButton } from "@/components/buttons";
import { Card, CardHeader } from "@/components/cards";
import { Alert } from "@/components/feedback";
import { Checkbox, Label } from "@/components/ui";
import { UploadProgress, UploadZone } from "@/components/upload";
import { THUMBNAIL_ACCEPT, THUMBNAIL_MAX_BYTES } from "@/constants/upload-wizard";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";

import type { WizardFormState } from "../wizard-types";

export type StepThumbnailUploadProps = {
  form: WizardFormState;
  errors: Readonly<Record<string, string>>;
  onChange: (patch: Partial<WizardFormState>) => void;
  onUpload: (file: File) => void;
  onRemove: () => void;
};

export function StepThumbnailUpload({
  form,
  errors,
  onChange,
  onUpload,
  onRemove,
}: StepThumbnailUploadProps): React.JSX.Element {
  const thumbnail = form.thumbnail;

  return (
    <Card>
      <CardHeader
        title="Thumbnail upload"
        description="Add a cover image for video posts. PNG or JPG up to 5 MB."
      />
      <div className="mb-4 flex items-center gap-2">
        <Checkbox
          id="skip-thumbnail"
          checked={form.thumbnailSkipped}
          onCheckedChange={(checked) =>
            onChange({
              thumbnailSkipped: checked === true,
              ...(checked ? { thumbnail: null } : {}),
            })
          }
        />
        <Label htmlFor="skip-thumbnail">Skip thumbnail</Label>
      </div>
      {!form.thumbnailSkipped && !thumbnail && (
        <UploadZone
          accept={THUMBNAIL_ACCEPT}
          maximumSize={THUMBNAIL_MAX_BYTES}
          supportedTypes="PNG, JPG"
          prompt="Drag and drop your thumbnail here"
          onFiles={(files) => {
            const file = files[0];
            if (file) onUpload(file);
          }}
        />
      )}
      {!form.thumbnailSkipped && thumbnail && (
        <div className="grid gap-4">
          <div className="bg-muted relative overflow-hidden rounded-lg border">
            <Image
              src={thumbnail.previewUrl}
              alt="Thumbnail preview"
              width={640}
              height={360}
              unoptimized
              className="mx-auto max-h-64 w-full object-contain"
            />
            <div className="bg-background/40 absolute inset-0 grid place-items-center opacity-0 transition-opacity hover:opacity-100">
              <div className="bg-card flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium shadow-sm">
                <Crop className="size-4" aria-hidden="true" />
                Crop (coming soon)
              </div>
            </div>
            {thumbnail.status === "complete" && (
              <motion.div
                className="bg-success text-success-foreground absolute top-3 right-3 grid size-9 place-items-center rounded-full"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: MOTION_DURATION.dialog, ease: MOTION_EASING.enter }}
              >
                <CheckCircle2 className="size-5" aria-hidden="true" />
              </motion.div>
            )}
          </div>
          <UploadProgress value={thumbnail.progress} label={`Uploading ${thumbnail.name}`} />
          <div className="flex flex-wrap gap-2">
            <SecondaryButton type="button" onClick={onRemove}>
              Remove
            </SecondaryButton>
            <PrimaryButton type="button" onClick={onRemove}>
              <RefreshCw className="size-4" aria-hidden="true" />
              Replace
            </PrimaryButton>
          </div>
        </div>
      )}
      {errors.thumbnail && (
        <Alert variant="danger" title="Thumbnail required" className="mt-4">
          {errors.thumbnail}
        </Alert>
      )}
    </Card>
  );
}
