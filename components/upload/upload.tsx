"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { FileUp, RotateCcw, Trash2 } from "lucide-react";
import { useDropzone, type Accept, type FileRejection } from "react-dropzone";

import { cn } from "../../lib/utils/cn";
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
export function UploadZone({ onFiles, onReject, accept, maximumSize, maximumFiles = 1, supportedTypes, prompt = "Drop files here or browse", className, ...props }: UploadZoneProps): React.JSX.Element {
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    ...(accept ? { accept } : {}),
    ...(maximumSize !== undefined ? { maxSize: maximumSize } : {}),
    maxFiles: maximumFiles,
    onDropAccepted: onFiles,
    ...(onReject ? { onDropRejected: onReject } : {}),
  });
  return <div {...getRootProps({ className: cn("grid min-h-44 cursor-pointer place-items-center rounded-lg border border-dashed bg-card p-6 text-center transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring", isDragActive && "border-primary bg-accent", isDragReject && "border-destructive bg-destructive/10", className), ...props })}>
    <input {...getInputProps()} /><div><FileUp className="mx-auto size-8 text-muted-foreground" aria-hidden="true" /><p className="mt-3 text-sm font-semibold">{prompt}</p>{supportedTypes && <p className="mt-1 text-xs text-muted-foreground">{supportedTypes}{maximumSize ? ` · Maximum ${formatBytes(maximumSize)}` : ""}</p>}</div>
  </div>;
}

export type UploadStatus = "queued" | "uploading" | "complete" | "failed";
export type UploadQueueItemProps = HTMLAttributes<HTMLLIElement> & { name: string; size?: number; status: UploadStatus; progress?: number; error?: string; onRetry?: () => void; onRemove?: () => void; preview?: ReactNode };
export function UploadQueueItem({ name, size, status, progress = 0, error, onRetry, onRemove, preview, className, ...props }: UploadQueueItemProps): React.JSX.Element {
  return <li className={cn("flex items-center gap-3 rounded-lg border bg-card p-3", className)} {...props}>{preview}<div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{name}</p><p className="text-xs text-muted-foreground">{size !== undefined && `${formatBytes(size)} · `}{status}</p>{status === "uploading" && <progress className="mt-2 h-1.5 w-full accent-primary" max={100} value={progress} aria-label={`Uploading ${name}: ${progress}%`} />}{error && <p role="alert" className="mt-1 text-xs text-destructive">{error}</p>}</div><div className="flex">{onRetry && status === "failed" && <Button variant="icon" aria-label={`Retry ${name}`} onClick={onRetry}><RotateCcw className="size-4" /></Button>}{onRemove && <Button variant="icon" aria-label={`Remove ${name}`} onClick={onRemove}><Trash2 className="size-4" /></Button>}</div></li>;
}

export type UploadDropzoneProps = UploadZoneProps;
export const UploadDropzone = UploadZone;
export type FileCardProps = UploadQueueItemProps;
export const FileCard = UploadQueueItem;
export type UploadProgressProps = { value: number; label?: string; className?: string };
export function UploadProgress({ value, label = "Upload progress", className }: UploadProgressProps): React.JSX.Element {
  const bounded = Math.min(100, Math.max(0, value));
  return <div className={cn("grid gap-1", className)}><div className="flex justify-between text-xs"><span>{label}</span><span className="tabular-nums">{bounded}%</span></div><progress className="h-2 w-full accent-primary" max={100} value={bounded}>{bounded}%</progress></div>;
}

function formatBytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 ** 2) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 ** 2).toFixed(1)} MB`;
}
