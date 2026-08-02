import type { LucideIcon } from "lucide-react";
import { CheckCircle2, FileText, Image, Layers, Sparkles, Type, Video } from "lucide-react";

export const WIZARD_STEP_COUNT = 8;

export type WizardStepId = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;

export type WizardStepConfig = {
  readonly id: WizardStepId;
  readonly key: string;
  readonly title: string;
  readonly description: string;
  readonly icon: LucideIcon;
  readonly estimatedMinutes: number;
};

export const WIZARD_STEPS: readonly WizardStepConfig[] = [
  {
    id: 1,
    key: "project",
    title: "Project information",
    description: "Name and schedule your publishing project.",
    icon: Type,
    estimatedMinutes: 2,
  },
  {
    id: 2,
    key: "poster",
    title: "Poster upload",
    description: "Add the hero visual for your campaign.",
    icon: Image,
    estimatedMinutes: 3,
  },
  {
    id: 3,
    key: "article",
    title: "Master article",
    description: "Upload or paste your source article.",
    icon: FileText,
    estimatedMinutes: 4,
  },
  {
    id: 4,
    key: "video",
    title: "Video upload",
    description: "Attach supporting video content.",
    icon: Video,
    estimatedMinutes: 5,
  },
  {
    id: 5,
    key: "thumbnail",
    title: "Thumbnail upload",
    description: "Add a cover image for video posts.",
    icon: Image,
    estimatedMinutes: 2,
  },
  {
    id: 6,
    key: "ai",
    title: "AI generation",
    description: "Configure platform variants and tone.",
    icon: Sparkles,
    estimatedMinutes: 3,
  },
  {
    id: 7,
    key: "review",
    title: "Review",
    description: "Confirm everything before creating.",
    icon: Layers,
    estimatedMinutes: 2,
  },
  {
    id: 8,
    key: "finish",
    title: "Finish",
    description: "Project created successfully.",
    icon: CheckCircle2,
    estimatedMinutes: 0,
  },
];

export const PROJECT_CATEGORIES = [
  { value: "cloud-architecture", label: "Cloud architecture" },
  { value: "devops", label: "DevOps & automation" },
  { value: "security", label: "Security & compliance" },
  { value: "data-ai", label: "Data & AI" },
  { value: "product-marketing", label: "Product marketing" },
] as const;

export const CONTENT_SERIES = [
  { value: "none", label: "No series" },
  { value: "azure-deep-dives", label: "Azure deep dives" },
  { value: "terraform-tips", label: "Terraform tips" },
  { value: "k8s-security", label: "Kubernetes security" },
  { value: "finops-weekly", label: "FinOps weekly" },
] as const;

export const AI_PLATFORMS = [
  { id: "linkedin", label: "LinkedIn" },
  { id: "facebook", label: "Facebook" },
  { id: "instagram", label: "Instagram" },
  { id: "x", label: "X (Twitter)" },
  { id: "medium", label: "Medium" },
  { id: "youtube", label: "YouTube" },
] as const;

export const AI_TONES = [
  { value: "professional", label: "Professional" },
  { value: "educational", label: "Educational" },
  { value: "friendly", label: "Friendly" },
  { value: "technical", label: "Technical" },
  { value: "executive", label: "Executive" },
] as const;

export const AI_LENGTHS = [
  { value: "short", label: "Short" },
  { value: "medium", label: "Medium" },
  { value: "long", label: "Long" },
] as const;

export const POSTER_ACCEPT = {
  "image/png": [".png"],
  "image/jpeg": [".jpg", ".jpeg"],
  "image/webp": [".webp"],
} as const;
export const ARTICLE_ACCEPT = {
  "text/markdown": [".md"],
  "text/plain": [".txt"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
} as const;
export const VIDEO_ACCEPT = { "video/mp4": [".mp4"], "video/quicktime": [".mov"] } as const;
export const THUMBNAIL_ACCEPT = { "image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"] } as const;

export const POSTER_MAX_BYTES = 10 * 1024 * 1024;
export const ARTICLE_MAX_BYTES = 10 * 1024 * 1024;
export const VIDEO_MAX_BYTES = 500 * 1024 * 1024;
export const THUMBNAIL_MAX_BYTES = 5 * 1024 * 1024;

export const DRAFT_STORAGE_KEY = "cch:upload-wizard-draft";
