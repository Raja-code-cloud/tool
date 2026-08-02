import { WIZARD_STEPS } from "@/constants/upload-wizard";
import { INPUT_LIMITS, isWithinLimit, limitExceededMessage } from "@/lib/security";

export type FileAsset = {
  readonly name: string;
  readonly size: number;
  readonly type: string;
  readonly previewUrl: string;
  readonly progress: number;
  readonly status: "uploading" | "complete" | "failed";
};

export type WizardFormState = {
  projectName: string;
  description: string;
  category: string;
  tags: string;
  contentSeries: string;
  publishDate: string;
  poster: FileAsset | null;
  articleMode: "upload" | "paste";
  articleContent: string;
  articleFile: FileAsset | null;
  videoSkipped: boolean;
  video: FileAsset | null;
  videoDuration: string;
  thumbnailSkipped: boolean;
  thumbnail: FileAsset | null;
  platforms: readonly string[];
  tone: string;
  length: string;
  generateHashtags: boolean;
  generateCta: boolean;
  generateSeo: boolean;
};

export type StepValidation = {
  readonly valid: boolean;
  readonly errors: Readonly<Record<string, string>>;
};

export const INITIAL_WIZARD_STATE: WizardFormState = {
  projectName: "",
  description: "",
  category: "",
  tags: "",
  contentSeries: "none",
  publishDate: "",
  poster: null,
  articleMode: "paste",
  articleContent: "",
  articleFile: null,
  videoSkipped: false,
  video: null,
  videoDuration: "",
  thumbnailSkipped: false,
  thumbnail: null,
  platforms: ["linkedin", "instagram"],
  tone: "professional",
  length: "medium",
  generateHashtags: true,
  generateCta: true,
  generateSeo: true,
};

export { INPUT_LIMITS };

export function countWords(text: string): number {
  const trimmed = text.trim();
  if (!trimmed) return 0;
  return trimmed.split(/\s+/).length;
}

export function estimateReadingMinutes(wordCount: number): number {
  return Math.max(1, Math.ceil(wordCount / 200));
}

export function validateStep(step: number, state: WizardFormState): StepValidation {
  const errors: Record<string, string> = {};

  switch (step) {
    case 1:
      if (!state.projectName.trim()) errors.projectName = "Enter a project name.";
      else if (!isWithinLimit(state.projectName, "projectName")) {
        errors.projectName = limitExceededMessage("projectName");
      }
      if (!state.category) errors.category = "Select a category.";
      if (!isWithinLimit(state.description, "description")) {
        errors.description = limitExceededMessage("description");
      }
      if (!isWithinLimit(state.tags, "tags")) {
        errors.tags = limitExceededMessage("tags");
      }
      break;
    case 2:
      if (!state.poster || state.poster.status !== "complete") {
        errors.poster = "Upload a poster image to continue.";
      }
      break;
    case 3:
      if (state.articleMode === "paste") {
        if (state.articleContent.trim().length < 50) {
          errors.articleContent = "Paste at least 50 characters of article content.";
        } else if (!isWithinLimit(state.articleContent, "articleContent")) {
          errors.articleContent = limitExceededMessage("articleContent");
        }
      } else if (!state.articleFile || state.articleFile.status !== "complete") {
        errors.articleFile = "Upload a master article file.";
      }
      break;
    case 4:
      if (!state.videoSkipped && (!state.video || state.video.status !== "complete")) {
        errors.video = "Upload a video or choose “Skip video for now”.";
      }
      break;
    case 5:
      if (!state.thumbnailSkipped && (!state.thumbnail || state.thumbnail.status !== "complete")) {
        errors.thumbnail = "Upload a thumbnail or choose “Skip thumbnail”.";
      }
      break;
    case 6:
      if (state.platforms.length === 0) errors.platforms = "Select at least one platform.";
      if (!state.tone) errors.tone = "Select a tone.";
      if (!state.length) errors.length = "Select a content length.";
      break;
    case 7:
    case 8:
      break;
    default:
      break;
  }

  return { valid: Object.keys(errors).length === 0, errors };
}

/** Maps validation error keys to focusable field ids for keyboard users. */
export function wizardErrorFieldId(errorKey: string): string {
  const fieldIds: Record<string, string> = {
    projectName: "project-name",
    category: "project-category",
    articleContent: "article-content",
    tone: "tone-professional",
    length: "length-medium",
  };
  return fieldIds[errorKey] ?? errorKey;
}

export function firstInvalidWizardFieldId(
  errors: Readonly<Record<string, string>>,
): string | undefined {
  for (const key of Object.keys(errors)) {
    return wizardErrorFieldId(key);
  }
  return undefined;
}

export function completedSteps(state: WizardFormState, currentStep: number): readonly number[] {
  const completed: number[] = [];
  for (let index = 1; index < currentStep; index += 1) {
    if (validateStep(index, state).valid) completed.push(index);
  }
  return completed;
}

export function wizardProgressPercent(step: number): number {
  return Math.round(((step - 1) / 7) * 100);
}

export function estimatedMinutesRemaining(step: number): number {
  return WIZARD_STEPS.filter((item) => item.id >= step && item.id < 8).reduce(
    (total, item) => total + item.estimatedMinutes,
    0,
  );
}
