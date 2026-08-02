"use client";

import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";

import { SecondaryButton } from "@/components/buttons";
import { Card, CardHeader } from "@/components/cards";
import { Alert } from "@/components/feedback";
import { Checkbox, Label } from "@/components/ui";
import { UploadProgress, UploadQueueItem, UploadZone } from "@/components/upload";
import { VIDEO_ACCEPT, VIDEO_MAX_BYTES } from "@/constants/upload-wizard";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { formatBytes } from "@/lib/utils/upload-wizard";

import type { WizardFormState } from "../wizard-types";

export type StepVideoUploadProps = {
  form: WizardFormState;
  errors: Readonly<Record<string, string>>;
  onChange: (patch: Partial<WizardFormState>) => void;
  onUpload: (file: File) => void;
  onRemove: () => void;
};

export function StepVideoUpload({
  form,
  errors,
  onChange,
  onUpload,
  onRemove,
}: StepVideoUploadProps): React.JSX.Element {
  const video = form.video;

  return (
    <Card>
      <CardHeader
        title="Video upload"
        description="Attach supporting video content. MP4 or MOV up to 500 MB."
      />
      <div className="mb-4 flex items-center gap-2">
        <Checkbox
          id="skip-video"
          checked={form.videoSkipped}
          onCheckedChange={(checked) =>
            onChange({ videoSkipped: checked === true, ...(checked ? { video: null } : {}) })
          }
        />
        <Label htmlFor="skip-video">Skip video for now</Label>
      </div>
      {!form.videoSkipped && !video && (
        <UploadZone
          accept={VIDEO_ACCEPT}
          maximumSize={VIDEO_MAX_BYTES}
          supportedTypes="MP4, MOV"
          prompt="Drag and drop your video here"
          onFiles={(files) => {
            const file = files[0];
            if (file) onUpload(file);
          }}
          className="min-h-52"
        />
      )}
      {!form.videoSkipped && video && (
        <div className="grid gap-4">
          <div className="bg-muted relative overflow-hidden rounded-lg border">
            <video src={video.previewUrl} controls className="max-h-72 w-full" />
            {video.status === "complete" && (
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
          <UploadProgress value={video.progress} label={`Uploading ${video.name}`} />
          <UploadQueueItem
            name={video.name}
            size={video.size}
            status={
              video.status === "complete"
                ? "complete"
                : video.status === "failed"
                  ? "failed"
                  : "uploading"
            }
            progress={video.progress}
            onRemove={onRemove}
          />
          <dl className="bg-muted/30 grid gap-2 rounded-lg border p-4 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-muted-foreground">Duration</dt>
              <dd className="font-medium">{form.videoDuration || "Calculating…"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">File size</dt>
              <dd className="font-medium">{formatBytes(video.size)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Format</dt>
              <dd className="font-medium">{video.type.split("/")[1]?.toUpperCase() ?? "Video"}</dd>
            </div>
          </dl>
          <SecondaryButton type="button" onClick={onRemove}>
            Remove video
          </SecondaryButton>
        </div>
      )}
      {errors.video && (
        <Alert variant="danger" title="Video required" className="mt-4">
          {errors.video}
        </Alert>
      )}
    </Card>
  );
}
