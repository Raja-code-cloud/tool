import type { Accept } from "react-dropzone";

import {
  ARTICLE_ACCEPT,
  ARTICLE_MAX_BYTES,
  POSTER_ACCEPT,
  POSTER_MAX_BYTES,
  THUMBNAIL_ACCEPT,
  THUMBNAIL_MAX_BYTES,
  VIDEO_ACCEPT,
  VIDEO_MAX_BYTES,
} from "@/constants/upload-wizard";
import { MAX_FILENAME_LENGTH, SAFE_FILENAME_PATTERN } from "@/lib/security/constants";
import { formatBytes } from "@/lib/utils/formatting";

export type UploadKind = "poster" | "article" | "video" | "thumbnail";

type UploadRule = {
  readonly accept: Accept;
  readonly maxBytes: number;
  readonly label: string;
};

const UPLOAD_RULES: Record<UploadKind, UploadRule> = {
  poster: { accept: POSTER_ACCEPT, maxBytes: POSTER_MAX_BYTES, label: "Poster" },
  article: { accept: ARTICLE_ACCEPT, maxBytes: ARTICLE_MAX_BYTES, label: "Article" },
  video: { accept: VIDEO_ACCEPT, maxBytes: VIDEO_MAX_BYTES, label: "Video" },
  thumbnail: { accept: THUMBNAIL_ACCEPT, maxBytes: THUMBNAIL_MAX_BYTES, label: "Thumbnail" },
};

function fileExtension(name: string): string {
  const index = name.lastIndexOf(".");
  return index >= 0 ? name.slice(index).toLowerCase() : "";
}

function allowedExtensions(accept: Accept): readonly string[] {
  return Object.values(accept).flat();
}

function allowedMimeTypes(accept: Accept): readonly string[] {
  return Object.keys(accept);
}

export function validateFilename(name: string): string | undefined {
  if (!name.trim()) return "File name is required.";
  if (name.length > MAX_FILENAME_LENGTH) {
    return `File name must be ${MAX_FILENAME_LENGTH} characters or fewer.`;
  }
  if (name.includes("..") || name.includes("/") || name.includes("\\")) {
    return "File name contains invalid path characters.";
  }
  if (!SAFE_FILENAME_PATTERN.test(name)) {
    return "File name contains unsupported characters.";
  }
  return undefined;
}

export function validateUploadFile(
  file: File,
  kind: UploadKind,
): { valid: true } | { valid: false; error: string } {
  const rule = UPLOAD_RULES[kind];

  const filenameError = validateFilename(file.name);
  if (filenameError) return { valid: false, error: filenameError };

  const extension = fileExtension(file.name);
  const extensions = allowedExtensions(rule.accept);
  if (!extensions.includes(extension)) {
    return {
      valid: false,
      error: `${rule.label} must be one of: ${extensions.join(", ")}.`,
    };
  }

  const mimeTypes = allowedMimeTypes(rule.accept);
  if (file.type && !mimeTypes.includes(file.type)) {
    return {
      valid: false,
      error: `${rule.label} file type is not allowed. Expected ${mimeTypes.join(" or ")}.`,
    };
  }

  if (file.size <= 0) {
    return { valid: false, error: `${rule.label} file is empty.` };
  }

  if (file.size > rule.maxBytes) {
    return {
      valid: false,
      error: `${rule.label} must be ${formatBytes(rule.maxBytes)} or smaller.`,
    };
  }

  return { valid: true };
}

export function uploadRuleForKind(kind: UploadKind): UploadRule {
  return UPLOAD_RULES[kind];
}

export function uploadValidationErrorMessage(kind: UploadKind, file: File): string | undefined {
  const result = validateUploadFile(file, kind);
  return result.valid ? undefined : result.error;
}
