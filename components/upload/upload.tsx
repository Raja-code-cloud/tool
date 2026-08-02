"use client";

import { FileUp, RotateCcw, Trash2 } from "lucide-react";
import type { HTMLAttributes, ReactNode } from "react";
import { useDropzone, type Accept, type FileRejection } from "react-dropzone";

import { cn } from "../../lib/utils/cn";
import { formatBytes } from "../../lib/utils/formatting";
import { Button } from "../ui";

export type UploadZoneProps = Omit<HTMLAttributes<HTMLDivElement>, "onDrop" | "onError"> & {
  onFiles: (files: readonly File[]) => void;
  onReject?: (rejections: readonly FileRejection[]) => void;
  accept?: Accept;
  maximumSize?: number;
  maximumFiles?: number;
  supportedTypes?: string;
  prompt?: string;
};
export function UploadZone({
  onFiles,
  onReject,
  accept,
  maximumSize,
  maximumFiles = 1,
  supportedTypes,
  prompt = "Drop files here or browse",
  className,
  ...props
}: UploadZoneProps): React.JSX.Element {
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    ...(accept ? { accept } : {}),
    ...(maximumSize !== undefined ? { maxSize: maximumSize } : {}),
    maxFiles: maximumFiles,
    onDropAccepted: onFiles,
    ...(onReject ? { onDropRejected: onReject } : {}),
  });
  return (
    <div
      {...getRootProps({
        className: cn(
          "bg-card focus-visible:ring-ring grid min-h-44 cursor-pointer place-items-center rounded-lg border border-dashed p-6 text-center transition-colors focus-visible:ring-2 focus-visible:outline-none",
          isDragActive && "border-primary bg-accent",
          isDragReject && "border-destructive bg-destructive/10",
          className,
        ),
        ...props,
      })}
    >
      <input {...getInputProps()} />
      <div>
        <FileUp className="text-muted-foreground mx-auto size-8" aria-hidden="true" />
        <p className="mt-3 text-sm font-semibold">{prompt}</p>
        {supportedTypes && (
          <p className="text-muted-foreground mt-1 text-xs">
            {supportedTypes}
            {maximumSize ? ` · Maximum ${formatBytes(maximumSize)}` : ""}
          </p>
        )}
      </div>
    </div>
  );
}

export type UploadStatus = "queued" | "uploading" | "complete" | "failed";
export type UploadQueueItemProps = HTMLAttributes<HTMLLIElement> & {
  name: string;
  size?: number;
  status: UploadStatus;
  progress?: number;
  error?: string;
  onRetry?: () => void;
  onRemove?: () => void;
  preview?: ReactNode;
};
export function UploadQueueItem({
  name,
  size,
  status,
  progress = 0,
  error,
  onRetry,
  onRemove,
  preview,
  className,
  ...props
}: UploadQueueItemProps): React.JSX.Element {
  return (
    <li
      className={cn("bg-card flex items-center gap-3 rounded-lg border p-3", className)}
      {...props}
    >
      {preview}
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold">{name}</p>
        <p className="text-muted-foreground text-xs">
          {size !== undefined && `${formatBytes(size)} · `}
          {status}
        </p>
        {status === "uploading" && (
          <progress
            className="accent-primary mt-2 h-1.5 w-full"
            max={100}
            value={progress}
            aria-label={`Uploading ${name}: ${progress}%`}
          />
        )}
        {error && (
          <p role="alert" className="text-destructive mt-1 text-xs">
            {error}
          </p>
        )}
      </div>
      <div className="flex">
        {onRetry && status === "failed" && (
          <Button variant="icon" aria-label={`Retry ${name}`} onClick={onRetry}>
            <RotateCcw className="size-4" />
          </Button>
        )}
        {onRemove && (
          <Button variant="icon" aria-label={`Remove ${name}`} onClick={onRemove}>
            <Trash2 className="size-4" />
          </Button>
        )}
      </div>
    </li>
  );
}

export type UploadDropzoneProps = UploadZoneProps;
export const UploadDropzone = UploadZone;
export type FileCardProps = UploadQueueItemProps;
export const FileCard = UploadQueueItem;
export type UploadProgressProps = { value: number; label?: string; className?: string };
export function UploadProgress({
  value,
  label = "Upload progress",
  className,
}: UploadProgressProps): React.JSX.Element {
  const bounded = Math.min(100, Math.max(0, value));
  return (
    <div className={cn("grid gap-1", className)}>
      <div className="flex justify-between text-xs">
        <span>{label}</span>
        <span className="tabular-nums">{bounded}%</span>
      </div>
      <progress className="accent-primary h-2 w-full" max={100} value={bounded}>
        {bounded}%
      </progress>
    </div>
  );
}
